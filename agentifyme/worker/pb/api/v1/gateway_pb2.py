# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: api/v1/gateway.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'api/v1/gateway.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from agentifyme.worker.pb.api.v1 import common_pb2 as api_dot_v1_dot_common__pb2
from google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14\x61pi/v1/gateway.proto\x12\x06\x61pi.v1\x1a\x13\x61pi/v1/common.proto\x1a\x1cgoogle/api/annotations.proto\x1a\x1cgoogle/protobuf/struct.proto\"\x97\x03\n\x14InboundWorkerMessage\x12\x0e\n\x06msg_id\x18\x01 \x01(\t\x12\x11\n\tworker_id\x18\x02 \x01(\t\x12\x15\n\rdeployment_id\x18\x03 \x01(\t\x12\x11\n\ttimestamp\x18\x04 \x01(\x03\x12<\n\x08metadata\x18\x05 \x03(\x0b\x32*.api.v1.InboundWorkerMessage.MetadataEntry\x12.\n\x04type\x18\x06 \x01(\x0e\x32 .api.v1.InboundWorkerMessageType\x12\x32\n\x0cregistration\x18\x07 \x01(\x0b\x32\x1a.api.v1.WorkerRegistrationH\x00\x12%\n\x05\x65vent\x18\x08 \x01(\x0b\x32\x14.api.v1.RuntimeEventH\x00\x12-\n\rworker_status\x18\t \x01(\x0b\x32\x14.api.v1.WorkerStatusH\x00\x1a/\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x42\t\n\x07message\"\x9e\x01\n\x12WorkerRegistration\x12\x0f\n\x07version\x18\x01 \x01(\t\x12\x42\n\x0c\x63\x61pabilities\x18\x02 \x03(\x0b\x32,.api.v1.WorkerRegistration.CapabilitiesEntry\x1a\x33\n\x11\x43\x61pabilitiesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\x98\x02\n\x0cLLMEventData\x12\r\n\x05model\x18\x01 \x01(\t\x12\x0e\n\x06vendor\x18\x02 \x01(\t\x12\x14\n\x0ctotal_tokens\x18\x03 \x01(\x03\x12\x15\n\rprompt_tokens\x18\x04 \x01(\x03\x12\x19\n\x11\x63ompletion_tokens\x18\x05 \x01(\x03\x12\x12\n\ntotal_cost\x18\x06 \x01(\t\x12\x13\n\x0bprompt_cost\x18\x07 \x01(\t\x12\x17\n\x0f\x63ompletion_cost\x18\x08 \x01(\t\x12\x12\n\nlatency_ms\x18\t \x01(\x03\x12\x13\n\x0btemperature\x18\n \x01(\x01\x12\x12\n\nmax_tokens\x18\x0b \x01(\x03\x12\x10\n\x08messages\x18\x0c \x03(\t\x12\x10\n\x08response\x18\r \x01(\t\"\x87\x07\n\x0cRuntimeEvent\x12,\n\nevent_type\x18\x01 \x01(\x0e\x32\x18.api.v1.RuntimeEventType\x12.\n\x0b\x65vent_stage\x18\x02 \x01(\x0e\x32\x19.api.v1.RuntimeEventStage\x12\x12\n\nevent_name\x18\x03 \x01(\t\x12\x11\n\ttimestamp\x18\x04 \x01(\x03\x12\x10\n\x08\x65vent_id\x18\x05 \x01(\t\x12\x17\n\x0fparent_event_id\x18\x06 \x01(\t\x12\x0e\n\x06run_id\x18\x07 \x01(\t\x12\x12\n\nrequest_id\x18\x08 \x01(\t\x12\x17\n\x0fidempotency_key\x18\t \x01(\t\x12*\n\x06status\x18\n \x01(\x0e\x32\x1a.api.v1.RuntimeEventStatus\x12\x15\n\rretry_attempt\x18\x0b \x01(\x05\x12&\n\x05\x65rror\x18\x0c \x01(\x0b\x32\x17.api.v1.AgentifyMeError\x12\x13\n\x0bmax_retries\x18\r \x01(\x05\x12\x13\n\x0bretry_delay\x18\x0e \x01(\x05\x12\x34\n\x08metadata\x18\x0f \x03(\x0b\x32\".api.v1.RuntimeEvent.MetadataEntry\x12-\n\x11input_data_format\x18\x10 \x01(\x0e\x32\x12.api.v1.DataFormat\x12\x14\n\njson_input\x18\x11 \x01(\tH\x00\x12\x16\n\x0c\x62inary_input\x18\x12 \x01(\x0cH\x00\x12/\n\x0cstruct_input\x18\x13 \x01(\x0b\x32\x17.google.protobuf.StructH\x00\x12\x16\n\x0cstring_input\x18\x14 \x01(\tH\x00\x12.\n\x12output_data_format\x18\x15 \x01(\x0e\x32\x12.api.v1.DataFormat\x12\x15\n\x0bjson_output\x18\x16 \x01(\tH\x01\x12\x17\n\rbinary_output\x18\x17 \x01(\x0cH\x01\x12\x30\n\rstruct_output\x18\x18 \x01(\x0b\x32\x17.google.protobuf.StructH\x01\x12\x17\n\rstring_output\x18\x19 \x01(\tH\x01\x12*\n\nllm_output\x18\x1a \x01(\x0b\x32\x14.api.v1.LLMEventDataH\x01\x1a/\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x42\x07\n\x05inputB\x08\n\x06output\"\x85\x01\n\x0cWorkerStatus\x12\x11\n\tcpu_usage\x18\x01 \x01(\x01\x12\x14\n\x0cmemory_usage\x18\x02 \x01(\x01\x12\x12\n\ndisk_usage\x18\x03 \x01(\x01\x12\x14\n\x0c\x61\x63tive_tasks\x18\x04 \x01(\x05\x12\"\n\x05state\x18\x05 \x01(\x0e\x32\x13.api.v1.WorkerState\"\x9e\x03\n\x15OutboundWorkerMessage\x12\x0e\n\x06msg_id\x18\x01 \x01(\t\x12\x11\n\ttimestamp\x18\x02 \x01(\x03\x12=\n\x08metadata\x18\x03 \x03(\x0b\x32+.api.v1.OutboundWorkerMessage.MetadataEntry\x12/\n\x04type\x18\x04 \x01(\x0e\x32!.api.v1.OutboundWorkerMessageType\x12\x33\n\x10workflow_request\x18\x05 \x01(\x0b\x32\x17.api.v1.WorkflowRequestH\x00\x12\x31\n\x0f\x63ontrol_command\x18\x06 \x01(\x0b\x32\x16.api.v1.ControlCommandH\x00\x12+\n\x0chealth_check\x18\x07 \x01(\x0b\x32\x13.api.v1.HealthCheckH\x00\x12!\n\x03\x61\x63k\x18\x08 \x01(\x0b\x32\x12.api.v1.MessageAckH\x00\x1a/\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x42\t\n\x07message\"\xd2\x02\n\x0fWorkflowRequest\x12\x0e\n\x06run_id\x18\x01 \x01(\t\x12\x15\n\rworkflow_name\x18\x02 \x01(\t\x12\x17\n\x0fidempotency_key\x18\x03 \x01(\t\x12\x37\n\x08metadata\x18\x04 \x03(\x0b\x32%.api.v1.WorkflowRequest.MetadataEntry\x12-\n\x11input_data_format\x18\x05 \x01(\x0e\x32\x12.api.v1.DataFormat\x12\x14\n\njson_input\x18\x06 \x01(\tH\x00\x12\x16\n\x0c\x62inary_input\x18\x07 \x01(\x0cH\x00\x12/\n\x0cstruct_input\x18\x08 \x01(\x0b\x32\x17.google.protobuf.StructH\x00\x1a/\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x42\x07\n\x05input\"\xb9\x01\n\x0e\x43ontrolCommand\x12(\n\x04type\x18\x01 \x01(\x0e\x32\x1a.api.v1.ControlCommandType\x12\x0e\n\x06run_id\x18\x02 \x01(\t\x12:\n\nparameters\x18\x03 \x03(\x0b\x32&.api.v1.ControlCommand.ParametersEntry\x1a\x31\n\x0fParametersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\"\n\x0bHealthCheck\x12\x13\n\x0bserver_time\x18\x01 \x01(\x03\"k\n\x14SyncWorkflowsRequest\x12\x11\n\tworker_id\x18\x01 \x01(\t\x12\x15\n\rdeployment_id\x18\x02 \x01(\t\x12)\n\tworkflows\x18\x03 \x03(\x0b\x32\x16.api.v1.WorkflowConfig\"\'\n\x15SyncWorkflowsResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\"\xb1\x02\n\x16WorkerHeartbeatRequest\x12\x11\n\tworker_id\x18\x01 \x01(\t\x12\x15\n\rdeployment_id\x18\x02 \x01(\t\x12\x0e\n\x06status\x18\x03 \x01(\t\x12>\n\x08metadata\x18\x04 \x03(\x0b\x32,.api.v1.WorkerHeartbeatRequest.MetadataEntry\x12<\n\x07metrics\x18\x05 \x03(\x0b\x32+.api.v1.WorkerHeartbeatRequest.MetricsEntry\x1a/\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x1a.\n\x0cMetricsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x03:\x02\x38\x01\")\n\x17WorkerHeartbeatResponse\x12\x0e\n\x06status\x18\x01 \x01(\t*\xd3\x01\n\x18InboundWorkerMessageType\x12+\n\'INBOUND_WORKER_MESSAGE_TYPE_UNSPECIFIED\x10\x00\x12,\n(INBOUND_WORKER_MESSAGE_TYPE_REGISTRATION\x10\x01\x12-\n)INBOUND_WORKER_MESSAGE_TYPE_RUNTIME_EVENT\x10\x02\x12-\n)INBOUND_WORKER_MESSAGE_TYPE_WORKER_STATUS\x10\x03*\xb2\x01\n\x10RuntimeEventType\x12\"\n\x1eRUNTIME_EVENT_TYPE_UNSPECIFIED\x10\x00\x12 \n\x1cRUNTIME_EVENT_TYPE_EXECUTION\x10\x01\x12\x1f\n\x1bRUNTIME_EVENT_TYPE_WORKFLOW\x10\x02\x12\x1b\n\x17RUNTIME_EVENT_TYPE_TASK\x10\x03\x12\x1a\n\x16RUNTIME_EVENT_TYPE_LLM\x10\x04*\xc4\x02\n\x11RuntimeEventStage\x12#\n\x1fRUNTIME_EVENT_STAGE_UNSPECIFIED\x10\x00\x12!\n\x1dRUNTIME_EVENT_STAGE_INITIATED\x10\x01\x12\x1e\n\x1aRUNTIME_EVENT_STAGE_QUEUED\x10\x02\x12\x1f\n\x1bRUNTIME_EVENT_STAGE_STARTED\x10\x03\x12!\n\x1dRUNTIME_EVENT_STAGE_COMPLETED\x10\x04\x12!\n\x1dRUNTIME_EVENT_STAGE_CANCELLED\x10\x05\x12\x1f\n\x1bRUNTIME_EVENT_STAGE_TIMEOUT\x10\x06\x12\x1d\n\x19RUNTIME_EVENT_STAGE_RETRY\x10\x07\x12 \n\x1cRUNTIME_EVENT_STAGE_FINISHED\x10\x08*}\n\x12RuntimeEventStatus\x12$\n RUNTIME_EVENT_STATUS_UNSPECIFIED\x10\x00\x12 \n\x1cRUNTIME_EVENT_STATUS_SUCCESS\x10\x01\x12\x1f\n\x1bRUNTIME_EVENT_STATUS_FAILED\x10\x02*\x87\x01\n\nDataFormat\x12\x1b\n\x17\x44\x41TA_FORMAT_UNSPECIFIED\x10\x00\x12\x14\n\x10\x44\x41TA_FORMAT_JSON\x10\x01\x12\x16\n\x12\x44\x41TA_FORMAT_BINARY\x10\x02\x12\x16\n\x12\x44\x41TA_FORMAT_STRUCT\x10\x03\x12\x16\n\x12\x44\x41TA_FORMAT_STRING\x10\x04*u\n\x0bWorkerState\x12\x1c\n\x18WORKER_STATE_UNSPECIFIED\x10\x00\x12\x16\n\x12WORKER_STATE_READY\x10\x01\x12\x15\n\x11WORKER_STATE_BUSY\x10\x02\x12\x19\n\x15WORKER_STATE_DRAINING\x10\x03*\x84\x02\n\x19OutboundWorkerMessageType\x12,\n(OUTBOUND_WORKER_MESSAGE_TYPE_UNSPECIFIED\x10\x00\x12$\n OUTBOUND_WORKER_MESSAGE_TYPE_ACK\x10\x01\x12\x31\n-OUTBOUND_WORKER_MESSAGE_TYPE_WORKFLOW_REQUEST\x10\x02\x12\x31\n-OUTBOUND_WORKER_MESSAGE_TYPE_WORKFLOW_COMMAND\x10\x03\x12-\n)OUTBOUND_WORKER_MESSAGE_TYPE_HEALTH_CHECK\x10\x04*\x9c\x01\n\x12\x43ontrolCommandType\x12$\n CONTROL_COMMAND_TYPE_UNSPECIFIED\x10\x00\x12\x1e\n\x1a\x43ONTROL_COMMAND_TYPE_PAUSE\x10\x01\x12\x1f\n\x1b\x43ONTROL_COMMAND_TYPE_RESUME\x10\x02\x12\x1f\n\x1b\x43ONTROL_COMMAND_TYPE_CANCEL\x10\x03*\x95\x01\n\x10WorkflowExecMode\x12\"\n\x1eWORKFLOW_EXEC_MODE_UNSPECIFIED\x10\x00\x12\x1b\n\x17WORKFLOW_EXEC_MODE_SYNC\x10\x01\x12\x1c\n\x18WORKFLOW_EXEC_MODE_ASYNC\x10\x02\x12\"\n\x1eWORKFLOW_EXEC_MODE_INTERACTIVE\x10\x03\x32\xd4\x02\n\x0eGatewayService\x12O\n\x0c\x43lientStream\x12\x1c.api.v1.InboundClientMessage\x1a\x1d.api.v1.OutboundClientMessage(\x01\x30\x01\x12O\n\x0cWorkerStream\x12\x1c.api.v1.InboundWorkerMessage\x1a\x1d.api.v1.OutboundWorkerMessage(\x01\x30\x01\x12L\n\rSyncWorkflows\x12\x1c.api.v1.SyncWorkflowsRequest\x1a\x1d.api.v1.SyncWorkflowsResponse\x12R\n\x0fWorkerHeartbeat\x12\x1e.api.v1.WorkerHeartbeatRequest\x1a\x1f.api.v1.WorkerHeartbeatResponse2\xf7\x01\n\x13WorkerHealthService\x12m\n\rLivenessCheck\x12\x1c.api.v1.LivenessCheckRequest\x1a\x1d.api.v1.LivenessCheckResponse\"\x1f\x82\xd3\xe4\x93\x02\x19\x12\x17/api/workers/{id}/livez\x12q\n\x0eReadinessCheck\x12\x1d.api.v1.ReadinessCheckRequest\x1a\x1e.api.v1.ReadinessCheckResponse\" \x82\xd3\xe4\x93\x02\x1a\x12\x18/api/workers/{id}/readyzB\x06Z\x04.;v1b\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.v1.gateway_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z\004.;v1'
  _globals['_INBOUNDWORKERMESSAGE_METADATAENTRY']._loaded_options = None
  _globals['_INBOUNDWORKERMESSAGE_METADATAENTRY']._serialized_options = b'8\001'
  _globals['_WORKERREGISTRATION_CAPABILITIESENTRY']._loaded_options = None
  _globals['_WORKERREGISTRATION_CAPABILITIESENTRY']._serialized_options = b'8\001'
  _globals['_RUNTIMEEVENT_METADATAENTRY']._loaded_options = None
  _globals['_RUNTIMEEVENT_METADATAENTRY']._serialized_options = b'8\001'
  _globals['_OUTBOUNDWORKERMESSAGE_METADATAENTRY']._loaded_options = None
  _globals['_OUTBOUNDWORKERMESSAGE_METADATAENTRY']._serialized_options = b'8\001'
  _globals['_WORKFLOWREQUEST_METADATAENTRY']._loaded_options = None
  _globals['_WORKFLOWREQUEST_METADATAENTRY']._serialized_options = b'8\001'
  _globals['_CONTROLCOMMAND_PARAMETERSENTRY']._loaded_options = None
  _globals['_CONTROLCOMMAND_PARAMETERSENTRY']._serialized_options = b'8\001'
  _globals['_WORKERHEARTBEATREQUEST_METADATAENTRY']._loaded_options = None
  _globals['_WORKERHEARTBEATREQUEST_METADATAENTRY']._serialized_options = b'8\001'
  _globals['_WORKERHEARTBEATREQUEST_METRICSENTRY']._loaded_options = None
  _globals['_WORKERHEARTBEATREQUEST_METRICSENTRY']._serialized_options = b'8\001'
  _globals['_WORKERHEALTHSERVICE'].methods_by_name['LivenessCheck']._loaded_options = None
  _globals['_WORKERHEALTHSERVICE'].methods_by_name['LivenessCheck']._serialized_options = b'\202\323\344\223\002\031\022\027/api/workers/{id}/livez'
  _globals['_WORKERHEALTHSERVICE'].methods_by_name['ReadinessCheck']._loaded_options = None
  _globals['_WORKERHEALTHSERVICE'].methods_by_name['ReadinessCheck']._serialized_options = b'\202\323\344\223\002\032\022\030/api/workers/{id}/readyz'
  _globals['_INBOUNDWORKERMESSAGETYPE']._serialized_start=3493
  _globals['_INBOUNDWORKERMESSAGETYPE']._serialized_end=3704
  _globals['_RUNTIMEEVENTTYPE']._serialized_start=3707
  _globals['_RUNTIMEEVENTTYPE']._serialized_end=3885
  _globals['_RUNTIMEEVENTSTAGE']._serialized_start=3888
  _globals['_RUNTIMEEVENTSTAGE']._serialized_end=4212
  _globals['_RUNTIMEEVENTSTATUS']._serialized_start=4214
  _globals['_RUNTIMEEVENTSTATUS']._serialized_end=4339
  _globals['_DATAFORMAT']._serialized_start=4342
  _globals['_DATAFORMAT']._serialized_end=4477
  _globals['_WORKERSTATE']._serialized_start=4479
  _globals['_WORKERSTATE']._serialized_end=4596
  _globals['_OUTBOUNDWORKERMESSAGETYPE']._serialized_start=4599
  _globals['_OUTBOUNDWORKERMESSAGETYPE']._serialized_end=4859
  _globals['_CONTROLCOMMANDTYPE']._serialized_start=4862
  _globals['_CONTROLCOMMANDTYPE']._serialized_end=5018
  _globals['_WORKFLOWEXECMODE']._serialized_start=5021
  _globals['_WORKFLOWEXECMODE']._serialized_end=5170
  _globals['_INBOUNDWORKERMESSAGE']._serialized_start=114
  _globals['_INBOUNDWORKERMESSAGE']._serialized_end=521
  _globals['_INBOUNDWORKERMESSAGE_METADATAENTRY']._serialized_start=463
  _globals['_INBOUNDWORKERMESSAGE_METADATAENTRY']._serialized_end=510
  _globals['_WORKERREGISTRATION']._serialized_start=524
  _globals['_WORKERREGISTRATION']._serialized_end=682
  _globals['_WORKERREGISTRATION_CAPABILITIESENTRY']._serialized_start=631
  _globals['_WORKERREGISTRATION_CAPABILITIESENTRY']._serialized_end=682
  _globals['_LLMEVENTDATA']._serialized_start=685
  _globals['_LLMEVENTDATA']._serialized_end=965
  _globals['_RUNTIMEEVENT']._serialized_start=968
  _globals['_RUNTIMEEVENT']._serialized_end=1871
  _globals['_RUNTIMEEVENT_METADATAENTRY']._serialized_start=463
  _globals['_RUNTIMEEVENT_METADATAENTRY']._serialized_end=510
  _globals['_WORKERSTATUS']._serialized_start=1874
  _globals['_WORKERSTATUS']._serialized_end=2007
  _globals['_OUTBOUNDWORKERMESSAGE']._serialized_start=2010
  _globals['_OUTBOUNDWORKERMESSAGE']._serialized_end=2424
  _globals['_OUTBOUNDWORKERMESSAGE_METADATAENTRY']._serialized_start=463
  _globals['_OUTBOUNDWORKERMESSAGE_METADATAENTRY']._serialized_end=510
  _globals['_WORKFLOWREQUEST']._serialized_start=2427
  _globals['_WORKFLOWREQUEST']._serialized_end=2765
  _globals['_WORKFLOWREQUEST_METADATAENTRY']._serialized_start=463
  _globals['_WORKFLOWREQUEST_METADATAENTRY']._serialized_end=510
  _globals['_CONTROLCOMMAND']._serialized_start=2768
  _globals['_CONTROLCOMMAND']._serialized_end=2953
  _globals['_CONTROLCOMMAND_PARAMETERSENTRY']._serialized_start=2904
  _globals['_CONTROLCOMMAND_PARAMETERSENTRY']._serialized_end=2953
  _globals['_HEALTHCHECK']._serialized_start=2955
  _globals['_HEALTHCHECK']._serialized_end=2989
  _globals['_SYNCWORKFLOWSREQUEST']._serialized_start=2991
  _globals['_SYNCWORKFLOWSREQUEST']._serialized_end=3098
  _globals['_SYNCWORKFLOWSRESPONSE']._serialized_start=3100
  _globals['_SYNCWORKFLOWSRESPONSE']._serialized_end=3139
  _globals['_WORKERHEARTBEATREQUEST']._serialized_start=3142
  _globals['_WORKERHEARTBEATREQUEST']._serialized_end=3447
  _globals['_WORKERHEARTBEATREQUEST_METADATAENTRY']._serialized_start=463
  _globals['_WORKERHEARTBEATREQUEST_METADATAENTRY']._serialized_end=510
  _globals['_WORKERHEARTBEATREQUEST_METRICSENTRY']._serialized_start=3401
  _globals['_WORKERHEARTBEATREQUEST_METRICSENTRY']._serialized_end=3447
  _globals['_WORKERHEARTBEATRESPONSE']._serialized_start=3449
  _globals['_WORKERHEARTBEATRESPONSE']._serialized_end=3490
  _globals['_GATEWAYSERVICE']._serialized_start=5173
  _globals['_GATEWAYSERVICE']._serialized_end=5513
  _globals['_WORKERHEALTHSERVICE']._serialized_start=5516
  _globals['_WORKERHEALTHSERVICE']._serialized_end=5763
# @@protoc_insertion_point(module_scope)
