import asyncio
import queue
import random
import time
import traceback
import uuid
from contextlib import asynccontextmanager

import grpc
from grpc.aio import StreamStreamCall
from loguru import logger
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

import agentifyme.worker.pb.api.v1.common_pb2 as common_pb

# Import generated protobuf code (assuming pb directory structure matches Go)
import agentifyme.worker.pb.api.v1.gateway_pb2 as pb
import agentifyme.worker.pb.api.v1.gateway_pb2_grpc as pb_grpc
from agentifyme.config import TaskConfig, WorkflowConfig
from agentifyme.worker.helpers import convert_workflow_to_pb, struct_to_dict
from agentifyme.worker.workflows import (
    WorkflowCommandHandler,
    WorkflowHandler,
    WorkflowJob,
)


async def exponential_backoff(attempt: int, max_delay: int = 32) -> None:
    """Exponential backoff with jitter"""
    delay = min(2**attempt, max_delay)
    jitter = random.uniform(0, 0.1) * delay
    total_delay = delay + jitter
    logger.info(f"Reconnection attempt {attempt+1}, waiting {total_delay:.1f} seconds")
    await asyncio.sleep(total_delay)


tracer = trace.get_tracer(__name__)


class WorkerService:
    """
    Worker service for processing jobs.
    """

    MAX_RECONNECT_ATTEMPTS = 5  # Maximum number of reconnection attempts
    MAX_BACKOFF_DELAY = 32  # Maximum delay between attempts in seconds

    def __init__(
        self,
        stub: pb_grpc.GatewayServiceStub,
        api_gateway_url: str,
        project_id: str,
        deployment_id: str,
        worker_id: str,
        max_workers: int = 50,
        heartbeat_interval: int = 30,
    ):
        # configuration
        self.api_gateway_url = api_gateway_url
        self.project_id = project_id
        self.deployment_id = deployment_id
        self.worker_id = worker_id

        self.jobs_queue = asyncio.Queue()
        self.events_queue = asyncio.Queue()
        self.shutdown_event = asyncio.Event()
        self.active_jobs: dict[str, asyncio.Task] = {}
        self.job_semaphore = asyncio.Semaphore(max_workers)

        # workflow handlers.
        self._workflow_handlers: dict[str, WorkflowHandler] = {}
        self.workflow_semaphore = asyncio.Semaphore(max_workers)

        # Tasks
        self.process_jobs_task: asyncio.Task | None = None

        # state
        self._stub: pb_grpc.GatewayServiceStub | None = None
        self.worker_type = "python-worker"
        self.connected = False
        self.connection_event = asyncio.Event()

        self.running = True
        self._stream: StreamStreamCall | None = None
        self._workflow_command_handler = WorkflowCommandHandler(self._stream, max_workers)
        self._active_tasks: dict[str, asyncio.Task] = {}
        self._heartbeat_task: asyncio.Task | None = None
        self._heartbeat_interval = heartbeat_interval
        self._stub = stub
        self.retry_attempt = 0

        # trace
        self._propagator = TraceContextTextMapPropagator()

    async def start_service(self) -> bool:
        """Start the worker service."""

        # initialize workflow handlers
        workflow_handlers = self.initialize_workflow_handlers()
        workflow_names = list(workflow_handlers.keys())
        self._workflow_names = workflow_names
        self._workflow_handlers = workflow_handlers
        tasks = []

        try:
            self.process_jobs_task = asyncio.create_task(self.process_jobs())
            self.subscribe_to_event_stream_task = asyncio.create_task(self.subscribe_to_event_stream())
            self.send_events_task = asyncio.create_task(self._send_events())
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())

            tasks = [self.process_jobs_task, self.subscribe_to_event_stream_task, self.send_events_task, self.heartbeat_task]
            await asyncio.gather(*tasks)

            logger.info("Worker service started successfully")
            return True

        except Exception as e:
            # Handle any other unexpected errors
            for task in tasks:
                if task:
                    task.cancel()
            traceback.print_exc()
            logger.error(f"Unexpected error during worker registration: {str(e)}")
            return False

    async def subscribe_to_event_stream(self):
        while not self.shutdown_event.is_set():
            try:
                if self.retry_attempt >= self.MAX_RECONNECT_ATTEMPTS:
                    logger.error(f"Failed to reconnect after {self.retry_attempt} attempts")
                    self.shutdown_event.set()
                    break

                # async for msg in self._stream:
                #     logger.info(f"Received worker message: {msg.request_id}")

                logger.info(f"Subscribing to event stream with worker:{self.worker_id}")
                self._stream = self._stub.WorkerStream()

                msg = pb.InboundWorkerMessage(
                    worker_id=self.worker_id,
                    deployment_id=self.deployment_id,
                    type=pb.INBOUND_WORKER_MESSAGE_TYPE_REGISTER,
                    registration=pb.WorkerRegistration(workflows=self._workflow_names),
                )
                await self._stream.write(msg)

                async for msg in self._stream:
                    logger.info(f"🚀 Received worker message: {msg.request_id}")
                    if self.shutdown_event.is_set():
                        break

                    if msg.HasField("ack") and msg.ack.status == "registered":
                        self.connected = True
                        self.connection_event.set()
                        await self.sync_workflows()
                        logger.info("Worker connected to API gateway. Listening for jobs...")

                    if msg.HasField("workflow_command"):
                        await self._handle_workflow_command(msg, msg.workflow_command)

            except grpc.RpcError as e:
                logger.error(f"Stream error on attempt {self.retry_attempt+1}/{self.MAX_RECONNECT_ATTEMPTS}: {e}")

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
            finally:
                if not self.connected or self._stream is None:
                    await exponential_backoff(self.retry_attempt, self.MAX_BACKOFF_DELAY)
                    self.retry_attempt += 1
                    continue

    async def stop_service(self):
        self.shutdown_event.set()

        logger.info("Stopping worker service")

        # Cancel all running workflows
        for task in self.active_jobs.values():
            task.cancel()

        if self.active_jobs:
            await asyncio.gather(*self.active_jobs.values(), return_exceptions=True)

        await self._stop_heartbeat()

    async def sync_workflows(self) -> None:
        # Prepare workflow configs
        _workflows = [convert_workflow_to_pb(WorkflowConfig.get(name).config) for name in WorkflowConfig.get_all()]

        # Sync workflows
        sync_msg = pb.SyncWorkflowsRequest(
            worker_id=self.worker_id,
            deployment_id=self.deployment_id,
            workflows=_workflows,
        )
        response = await self._stub.SyncWorkflows(sync_msg)
        logger.info(f"Synchronized workflows: {response}")

    async def _receive_commands(self) -> None:
        """Receive and process commands from gRPC stream"""
        try:
            logger.info("Starting receive_commands")
            if self._stream is None:
                logger.error("Stream is not initialized")
                return

            async for msg in self._stream:
                if self.shutdown_event.is_set():
                    break

                logger.info(f"Received worker message: {msg.request_id}")
                # if isinstance(msg, pb.OutboundWorkerMessage):
                #     await self._handle_worker_message(msg)

        except grpc.aio.AioRpcError as e:
            logger.error(f"gRPC stream error in receive_commands: {e}")
            await self._handle_stream_error(e)
        except Exception as e:
            logger.exception(f"Unexpected error in receive_commands: {e}")
            raise

    async def _handle_worker_message(self, msg: pb.OutboundWorkerMessage) -> None:
        """Handle incoming worker messages"""
        if msg.HasField("workflow_command"):
            await self._handle_workflow_command(msg, msg.workflow_command)

    async def _handle_workflow_command(self, msg: pb.OutboundWorkerMessage, command: pb.WorkflowCommand) -> None:
        """Handle workflow commands"""
        try:
            if command.type == pb.WORKFLOW_COMMAND_TYPE_RUN:
                await self._handle_run_command(msg, command)
            elif command.type == pb.WORKFLOW_COMMAND_TYPE_LIST:
                await self._handle_list_command(msg)
        except Exception as e:
            logger.error(f"Error handling workflow command: {e}")

    async def _handle_run_command(self, msg: pb.OutboundWorkerMessage, command: pb.WorkflowCommand) -> None:
        """Handle run workflow commands"""
        carrier: dict[str, str] = getattr(msg, "metadata", {})
        context = self._propagator.extract(carrier)

        with tracer.start_as_current_span(name="workflow.execute", context=context) as span:
            workflow_job = WorkflowJob(
                run_id=msg.request_id,
                workflow_name=command.run_workflow.workflow_name,
                input_parameters=struct_to_dict(command.run_workflow.parameters),
                metadata=carrier,
            )

            span.add_event("job_queued", attributes={"request_id": msg.request_id, "input_parameters": workflow_job.input_parameters})

            await self.jobs_queue.put(workflow_job)
            logger.debug(f"Queued workflow job: {msg.request_id}")

    async def _handle_list_command(self, msg: pb.OutboundWorkerMessage) -> None:
        """Handle list workflows command"""
        response = await self._workflow_command_handler.list_workflows()
        reply = pb.InboundWorkerMessage(
            request_id=msg.request_id,
            worker_id=self.worker_id,
            deployment_id=self.deployment_id,
            type=pb.INBOUND_WORKER_MESSAGE_TYPE_LIST_WORKFLOWS,
            list_workflows=response,
        )
        await self._stream.write(reply)

    async def _handle_stream_error(self, e: grpc.aio.AioRpcError) -> None:
        """Handle stream errors"""
        if e.code() == grpc.StatusCode.INTERNAL and "RST_STREAM" in str(e.details()):
            logger.warning("Received RST_STREAM error, initiating graceful reconnect", extra={"error_details": e.details()})
            self.connected = False
            return

        logger.error(f"gRPC stream error in receive_commands: {e}")
        raise

    async def _send_events(self) -> None:
        while not self.shutdown_event.is_set():
            try:
                if self._stream is None or self.events_queue.empty():
                    await asyncio.sleep(1)
                    continue

                job = await self.events_queue.get()
                logger.debug(f"Sending event: {job.run_id}, job.success: {job.success}, Job: {job}")
                if isinstance(job, WorkflowJob):
                    msg = pb.InboundWorkerMessage(
                        request_id=job.run_id,
                        worker_id=self.worker_id,
                        deployment_id=self.deployment_id,
                        type=pb.INBOUND_WORKER_MESSAGE_TYPE_WORKFLOW_RESULT,
                        workflow_result=common_pb.WorkflowResult(request_id=job.run_id, data=job.output, error=job.error),
                    )

                    await self._stream.write(msg)
                else:
                    logger.error(f"Received unexpected job type: {type(job)}")
            except queue.Empty:
                pass

    async def process_jobs(self) -> None:
        """Process jobs from the queue"""
        while not self.shutdown_event.is_set():
            logger.info("Processing jobs from queue")
            try:
                job = await self.jobs_queue.get()
                asyncio.create_task(self._handle_job(job))
            except Exception as e:
                self.logger.error(f"Error processing task: {e}")
                await asyncio.sleep(1)

    async def _handle_job(self, job: WorkflowJob):
        """Handle a single job"""
        async with self._workflow_context(job.run_id):
            try:
                context = self._propagator.extract(job.metadata)
                with tracer.start_as_current_span(name="handle.job", context=context) as span:
                    workflow_task = asyncio.current_task()
                    self.active_jobs[job.run_id] = workflow_task

                    while not self.shutdown_event.is_set():
                        # Execute workflow step
                        _workflow_handler = self._workflow_handlers.get(job.workflow_name)
                        job = await _workflow_handler(job)

                        logger.info(f"Workflow {job.run_id} result: {job.output}, job.success: {job.success}")

                        # Send event
                        await self.events_queue.put(job)

                        # If the job is completed, break out of the loop.
                        # TODO: Handle errors and retry scenario.
                        if job.completed:
                            break

            except asyncio.CancelledError:
                self.logger.info(f"Workflow {job.run_id} cancelled")
                raise
            except Exception as e:
                self.logger.error(f"Workflow execution error: {e}")
                await self.event_queue.put({"workflow_id": job.run_id, "status": "error", "error": str(e)})

    @asynccontextmanager
    async def _workflow_context(self, run_id: str):
        """Context manager for workflow execution"""
        async with self.workflow_semaphore:
            try:
                yield
            finally:
                self.active_jobs.pop(run_id, None)

    async def _heartbeat_loop(self) -> None:
        """Continuously send heartbeats at the specified interval."""
        try:
            while not self.shutdown_event.is_set():
                await asyncio.sleep(self._heartbeat_interval)

                if not self.connected:
                    await asyncio.sleep(10.0)
                    continue

                try:
                    metrics = {
                        "num_active_jobs": len(self.active_jobs),
                        "num_jobs_in_queue": self.jobs_queue.qsize(),
                        "num_events_in_queue": self.events_queue.qsize(),
                    }
                    heartbeat_msg = pb.WorkerHeartbeatRequest(
                        worker_id=self.worker_id,
                        deployment_id=self.deployment_id,
                        status="active",
                        metrics=metrics,
                    )
                    _ = await self._stub.WorkerHeartbeat(heartbeat_msg)
                except grpc.RpcError as e:
                    logger.error(f"Failed to send heartbeat: {e}")
                    # Instead of continuing in a loop, raise the error to trigger reconnection
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error in heartbeat: {e}")
                    raise

        except asyncio.CancelledError:
            logger.debug("Heartbeat loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Heartbeat loop error: {e}")
            raise

    def _start_heartbeat(self, stream: StreamStreamCall) -> None:
        """Start the heartbeat task."""
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def _stop_heartbeat(self) -> None:
        """Stop the heartbeat task."""
        if self._heartbeat_task is not None:
            await self._heartbeat_task.cancel()
            self._heartbeat_task = None

    async def cleanup_on_disconnect(self):
        """Cleanup resources on disconnect"""
        self._stop_heartbeat()
        self.connected = False
        self.connection_event.clear()

        # Clear queues
        while not self.jobs_queue.empty():
            try:
                self.jobs_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        while not self.events_queue.empty():
            try:
                self.events_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        # Cancel active jobs
        for job_id, task in list(self.active_jobs.items()):
            logger.info(f"Cancelling job {job_id} due to disconnect")
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Error cancelling job {job_id}: {e}")

        self._active_tasks.clear()
        await asyncio.sleep(1)
        logger.info("Cleaned up disconnected resources")

    def initialize_workflow_handlers(self) -> dict[str, WorkflowHandler]:
        """Initialize workflow handlers"""
        _workflow_handlers = {}
        for workflow_name in WorkflowConfig.get_all():
            _workflow = WorkflowConfig.get(workflow_name)
            _workflow_handler = WorkflowHandler(_workflow)
            _workflow_handlers[workflow_name] = _workflow_handler

        return _workflow_handlers
