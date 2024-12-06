import asyncio
import queue
import random
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
        heartbeat_interval: int = 60,
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
        """Start the worker service."""  # initialize workflow handlers
        workflow_handlers = self.initialize_workflow_handlers()
        workflow_names = list(workflow_handlers.keys())
        self._workflow_handlers = workflow_handlers

        try:
            self._stream = self._stub.WorkerStream()

            receive_task = asyncio.create_task(self._receive_commands())

            # register worker
            msg = pb.InboundWorkerMessage(
                worker_id=self.worker_id,
                deployment_id=self.deployment_id,
                type=pb.INBOUND_WORKER_MESSAGE_TYPE_REGISTER,
                registration=pb.WorkerRegistration(workflows=workflow_names),
            )

            await self._stream.write(msg)

            # Wait for connection event with timeout
            try:
                await asyncio.wait_for(self.connection_event.wait(), timeout=5.0)
                self.retry_attempt = 0
                return True
            except asyncio.TimeoutError:
                logger.error("Timeout waiting for connection")
                receive_task.cancel()
                try:
                    await receive_task
                except asyncio.CancelledError:
                    pass
                return False

        except grpc.RpcError as e:
            # Handle gRPC specific errors
            logger.error(f"Failed to register worker: {e.details()}")
            return False

        except Exception as e:
            # Handle any other unexpected errors
            traceback.print_exc()
            logger.error(f"Unexpected error during worker registration: {str(e)}")
            return False

    async def stop_service(self):
        self.shutdown_event.set()

        # Cancel all running workflows
        for task in self.active_jobs.values():
            task.cancel()

        if self.active_jobs:
            await asyncio.gather(*self.active_jobs.values(), return_exceptions=True)

    async def start_worker_stream(self) -> None:
        """Start the worker stream. This should be called after registering the worker. It handles the bidirectional stream with the API gateway.
        We listen to commands from the server, execute the commands and respond through events.
        """

        while not self.shutdown_event.is_set():
            try:
                if self.retry_attempt >= self.MAX_RECONNECT_ATTEMPTS:
                    logger.error(f"Failed to reconnect after {self.retry_attempt} attempts")
                    self.shutdown_event.set()
                    break

                if not self.connected or self._stream is None:
                    connected = await self.start_service()
                    if not connected:
                        logger.error(f"Failed to connect worker {self.worker_id}")
                        await exponential_backoff(self.retry_attempt, self.MAX_BACKOFF_DELAY)
                        self.retry_attempt += 1
                        continue

                # Create tasks for ongoing operations
                tasks = [
                    asyncio.create_task(self._heartbeat_loop(self._stream), name="heartbeat"),
                    asyncio.create_task(self._send_events(), name="send_events"),
                    asyncio.create_task(self._process_jobs(), name="process_jobs"),
                ]

                # Wait for any task to complete (which usually means an error occurred)
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

                # Cancel all pending tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                # Check if any task failed with an error
                for task in done:
                    try:
                        await task
                    except grpc.RpcError as e:
                        logger.error(f"gRPC error in {task.get_name()}: {e}")
                        raise  # Re-raise to trigger reconnection
                    except Exception as e:
                        logger.error(f"Unexpected error in {task.get_name()}: {e}")
                        raise

            except grpc.RpcError as e:
                logger.error(f"Stream error on attempt {self.retry_attempt+1}/{self.MAX_RECONNECT_ATTEMPTS}: {e}")
                if not self.shutdown_event.is_set():
                    self._stream = None
                    await self.cleanup_on_disconnect()
                    await exponential_backoff(self.retry_attempt, self.MAX_BACKOFF_DELAY)
                    self.retry_attempt += 1
                    continue

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                if not self.shutdown_event.is_set():
                    self._stream = None
                    await self.cleanup_on_disconnect()
                    await exponential_backoff(self.retry_attempt, self.MAX_BACKOFF_DELAY)
                    self.retry_attempt += 1
                    continue

    async def _receive_commands(self) -> None:
        """Receive commands from gRPC stream"""
        try:
            async for stream_msg in self._stream:
                if self.shutdown_event.is_set():
                    break

                if isinstance(stream_msg, pb.OutboundWorkerMessage):
                    if stream_msg.HasField("workflow_command"):
                        workflow_command = stream_msg.workflow_command
                        match workflow_command.type:
                            case pb.WORKFLOW_COMMAND_TYPE_RUN:
                                carrier: dict[str, str] = getattr(stream_msg, "metadata", {})
                                context = self._propagator.extract(carrier)
                                with tracer.start_as_current_span(name="workflow.execute", context=context) as span:
                                    _workflow_command = WorkflowJob(
                                        run_id=stream_msg.request_id,
                                        workflow_name=workflow_command.run_workflow.workflow_name,
                                        input_parameters=struct_to_dict(workflow_command.run_workflow.parameters),
                                        metadata=carrier,
                                    )
                                    span.add_event(
                                        "job_queued",
                                        attributes={"request_id": stream_msg.request_id, "input_parameters": _workflow_command.input_parameters},
                                    )

                                    result = await self.jobs_queue.put(_workflow_command)
                                    logger.debug(f"Workflow command result: {result}")

                            case pb.WORKFLOW_COMMAND_TYPE_LIST:
                                response = await self._workflow_command_handler.list_workflows()
                                msg = pb.InboundWorkerMessage(
                                    request_id=stream_msg.request_id,
                                    worker_id=self.worker_id,
                                    deployment_id=self.deployment_id,
                                    type=pb.INBOUND_WORKER_MESSAGE_TYPE_LIST_WORKFLOWS,
                                    list_workflows=response,
                                )
                                await self._stream.write(msg)

                    elif stream_msg.HasField("ack"):
                        if stream_msg.ack.status == "registered":
                            self.connected = True
                            self.connection_event.set()
                            logger.info("Worker connected to API gateway. Listening for jobs...")

                            _workflows: list[pb.WorkflowConfig] = []
                            for workflow_name in WorkflowConfig.get_all():
                                _workflow = WorkflowConfig.get(workflow_name)
                                _workflow_pb = convert_workflow_to_pb(_workflow.config)
                                _workflows.append(_workflow_pb)

                            # Send the latest workflows
                            msg = pb.SyncWorkflowsRequest(
                                worker_id=self.worker_id,
                                deployment_id=self.deployment_id,
                                workflows=_workflows,
                            )

                            response = await self._stub.SyncWorkflows(msg)
                            logger.info(f"Synchronized workflows: {response}")

                            continue
                        else:
                            logger.error("Failed to register worker")
                            self.connected = False
                    elif stream_msg.HasField("workflow_status"):
                        pass

        except grpc.aio.AioRpcError as e:
            if e.code() == grpc.StatusCode.INTERNAL and "RST_STREAM" in str(e.details()):
                logger.warning(
                    "Received RST_STREAM error, initiating graceful reconnect",
                    extra={"error_details": e.details()},
                )
                # Signal reconnection needed but don't raise
                self.connected = False
                self.connection_event.clear()
                return
            else:
                logger.error(f"gRPC stream error in receive_commands: {e}")
                raise  # Propagate other gRPC errors to trigger reconnection
        except Exception as e:
            traceback.print_exc()
            logger.exception(f"Unexpected error in receive_commands: {e}")
            raise

    async def _send_events(self) -> None:
        while not self.shutdown_event.is_set():
            try:
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

    async def _process_jobs(self) -> None:
        """Process jobs from the queue"""
        while not self.shutdown_event.is_set():
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

    async def _heartbeat_loop(self, stream: StreamStreamCall) -> None:
        """Continuously send heartbeats at the specified interval."""
        logger.info(f"Sending heartbeats for worker {self.worker_id} every {self._heartbeat_interval} seconds")

        try:
            while not self.shutdown_event.is_set() and self.connected:
                logger.debug(f"Sending heartbeat for worker {self.worker_id}")
                heartbeat_msg = pb.InboundWorkerMessage(
                    request_id=str(uuid.uuid4()),
                    worker_id=self.worker_id,
                    type=pb.INBOUND_WORKER_MESSAGE_TYPE_HEARTBEAT,
                    heartbeat=pb.WorkerHeartbeat(status="active"),
                )

                try:
                    await stream.write(heartbeat_msg)
                    logger.debug(f"Sent heartbeat for worker {self.worker_id}")
                except grpc.RpcError as e:
                    logger.error(f"Failed to send heartbeat: {e}")
                    # Instead of continuing in a loop, raise the error to trigger reconnection
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error in heartbeat: {e}")
                    raise

                await asyncio.sleep(self._heartbeat_interval)

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
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop(stream))

    def _stop_heartbeat(self) -> None:
        """Stop the heartbeat task."""
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
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

    async def process_workflow_command(self, command: pb.WorkflowCommand, stream: StreamStreamCall) -> None:
        try:
            async with self._job_semaphore:
                self._current_jobs += 1

                #             workflow_name = job.function.name
        #             if workflow_name not in self._workflow_handlers:
        #                 raise ValueError(
        #                     f"No handler registered for workflow: {workflow_name}"
        #                 )

        #             workflow_parameters = dict(job.function.parameters)

        #             logger.info(f"Processing job {job.job_id}")

        #             yield pb.WorkerStreamOutbound(
        #                 worker_id=self.worker_id,
        #                 type=pb.WORKER_SERVICE_OUTBOUND_TYPE_JOB_STATUS,
        #                 job=common_pb2.JobStatus(
        #                     job_id=job.job_id,
        #                     status=common_pb2.WORKER_JOB_STATUS_PROCESSING,
        #                     metadata=job.metadata,
        #                 ),
        #             )

        #             workflow_handler = self._workflow_handlers[workflow_name]
        #             result = await workflow_handler(workflow_parameters)

        except Exception as e:
            logger.error(f"Error processing workflow command: {e}")
        finally:
            self._current_jobs -= 1

    async def send_heartbeat(self, stream: StreamStreamCall) -> None:
        heartbeat = pb.WorkerHeartbeat(status="active")

        heartbeat_msg = pb.InboundWorkerMessage(
            worker_id=self.worker_id,
            type=pb.INBOUND_WORKER_MESSAGE_TYPE_HEARTBEAT,
            heartbeat=heartbeat,
        )

        await stream.write(heartbeat_msg)

    def initialize_workflow_handlers(self) -> dict[str, WorkflowHandler]:
        """Initialize workflow handlers"""
        _workflow_handlers = {}
        for workflow_name in WorkflowConfig.get_all():
            _workflow = WorkflowConfig.get(workflow_name)
            _workflow_handler = WorkflowHandler(_workflow)
            _workflow_handlers[workflow_name] = _workflow_handler

        return _workflow_handlers
