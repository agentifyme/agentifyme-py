# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: api/v1/common.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'api/v1/common.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13\x61pi/v1/common.proto\x12\x06\x61pi.v1\x1a\x19google/protobuf/any.proto\x1a\x1egoogle/protobuf/duration.proto\x1a\x1cgoogle/protobuf/struct.proto\"\x94\x04\n\x05Param\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\x12)\n\tdata_type\x18\x03 \x01(\x0e\x32\x16.api.v1.Param.DataType\x12+\n\rdefault_value\x18\x04 \x01(\x0b\x32\x14.google.protobuf.Any\x12\x10\n\x08required\x18\x05 \x01(\x08\x12\x17\n\nclass_name\x18\x06 \x01(\tH\x00\x88\x01\x01\x12\x36\n\rnested_fields\x18\x07 \x03(\x0b\x32\x1f.api.v1.Param.NestedFieldsEntry\x1a\x42\n\x11NestedFieldsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x1c\n\x05value\x18\x02 \x01(\x0b\x32\r.api.v1.Param:\x02\x38\x01\"\xd9\x01\n\x08\x44\x61taType\x12\x19\n\x15\x44\x41TA_TYPE_UNSPECIFIED\x10\x00\x12\x14\n\x10\x44\x41TA_TYPE_STRING\x10\x01\x12\x15\n\x11\x44\x41TA_TYPE_INTEGER\x10\x02\x12\x13\n\x0f\x44\x41TA_TYPE_FLOAT\x10\x03\x12\x15\n\x11\x44\x41TA_TYPE_BOOLEAN\x10\x04\x12\x13\n\x0f\x44\x41TA_TYPE_ARRAY\x10\x05\x12\x14\n\x10\x44\x41TA_TYPE_OBJECT\x10\x06\x12\x16\n\x12\x44\x41TA_TYPE_DATETIME\x10\x07\x12\x16\n\x12\x44\x41TA_TYPE_DURATION\x10\x08\x42\r\n\x0b_class_name\"g\n\x08Schedule\x12\x19\n\x0f\x63ron_expression\x18\x01 \x01(\tH\x00\x12-\n\x08interval\x18\x02 \x01(\x0b\x32\x19.google.protobuf.DurationH\x00\x42\x11\n\x0fschedule_config\"\xf9\x02\n\x0eWorkflowConfig\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04slug\x18\x03 \x01(\t\x12\x18\n\x0b\x64\x65scription\x18\x04 \x01(\tH\x00\x88\x01\x01\x12\x31\n\x10input_parameters\x18\x05 \x01(\x0b\x32\x17.google.protobuf.Struct\x12\x32\n\x11output_parameters\x18\x06 \x01(\x0b\x32\x17.google.protobuf.Struct\x12\'\n\x08schedule\x18\x07 \x01(\x0b\x32\x10.api.v1.ScheduleH\x01\x88\x01\x01\x12\x0f\n\x07version\x18\x08 \x01(\t\x12\x36\n\x08metadata\x18\t \x03(\x0b\x32$.api.v1.WorkflowConfig.MetadataEntry\x1a/\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x42\x0e\n\x0c_descriptionB\x0b\n\t_schedule\"-\n\x14ListWorkflowsRequest\x12\x15\n\rdeployment_id\x18\x01 \x01(\t\"B\n\x15ListWorkflowsResponse\x12)\n\tworkflows\x18\x01 \x03(\x0b\x32\x16.api.v1.WorkflowConfig\"\x16\n\x14InboundClientMessage\"\x17\n\x15OutboundClientMessage\"\xd1\x01\n\x0eWorkflowResult\x12\x12\n\nrequest_id\x18\x01 \x01(\t\x12\'\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x17.google.protobuf.StructH\x00\x12\x0f\n\x05\x65rror\x18\x03 \x01(\tH\x00\x12\x36\n\x08metadata\x18\x04 \x03(\x0b\x32$.api.v1.WorkflowResult.MetadataEntry\x1a/\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x42\x08\n\x06result\"\xef\x01\n\x0bWorkflowJob\x12\x0e\n\x06job_id\x18\x01 \x01(\t\x12\'\n\x06status\x18\x02 \x01(\x0e\x32\x17.api.v1.WorkerJobStatus\x12&\n\x04\x64\x61ta\x18\x03 \x01(\x0b\x32\x16.api.v1.WorkflowResultH\x00\x12\x0f\n\x05\x65rror\x18\x04 \x01(\tH\x00\x12\x33\n\x08metadata\x18\x05 \x03(\x0b\x32!.api.v1.WorkflowJob.MetadataEntry\x1a/\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x42\x08\n\x06result*\xb1\x02\n\x0fWorkerJobStatus\x12!\n\x1dWORKER_JOB_STATUS_UNSPECIFIED\x10\x00\x12\x1c\n\x18WORKER_JOB_STATUS_QUEUED\x10\x01\x12 \n\x1cWORKER_JOB_STATUS_PROCESSING\x10\x02\x12\x1f\n\x1bWORKER_JOB_STATUS_COMPLETED\x10\x03\x12\x1c\n\x18WORKER_JOB_STATUS_FAILED\x10\x04\x12\x1e\n\x1aWORKER_JOB_STATUS_RETRYING\x10\x05\x12\x1f\n\x1bWORKER_JOB_STATUS_CANCELLED\x10\x06\x12\x1d\n\x19WORKER_JOB_STATUS_TIMEOUT\x10\x07\x12\x1c\n\x18WORKER_JOB_STATUS_PAUSED\x10\x08\x42\x06Z\x04.;v1b\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.v1.common_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z\004.;v1'
  _globals['_PARAM_NESTEDFIELDSENTRY']._loaded_options = None
  _globals['_PARAM_NESTEDFIELDSENTRY']._serialized_options = b'8\001'
  _globals['_WORKFLOWCONFIG_METADATAENTRY']._loaded_options = None
  _globals['_WORKFLOWCONFIG_METADATAENTRY']._serialized_options = b'8\001'
  _globals['_WORKFLOWRESULT_METADATAENTRY']._loaded_options = None
  _globals['_WORKFLOWRESULT_METADATAENTRY']._serialized_options = b'8\001'
  _globals['_WORKFLOWJOB_METADATAENTRY']._loaded_options = None
  _globals['_WORKFLOWJOB_METADATAENTRY']._serialized_options = b'8\001'
  _globals['_WORKERJOBSTATUS']._serialized_start=1759
  _globals['_WORKERJOBSTATUS']._serialized_end=2064
  _globals['_PARAM']._serialized_start=121
  _globals['_PARAM']._serialized_end=653
  _globals['_PARAM_NESTEDFIELDSENTRY']._serialized_start=352
  _globals['_PARAM_NESTEDFIELDSENTRY']._serialized_end=418
  _globals['_PARAM_DATATYPE']._serialized_start=421
  _globals['_PARAM_DATATYPE']._serialized_end=638
  _globals['_SCHEDULE']._serialized_start=655
  _globals['_SCHEDULE']._serialized_end=758
  _globals['_WORKFLOWCONFIG']._serialized_start=761
  _globals['_WORKFLOWCONFIG']._serialized_end=1138
  _globals['_WORKFLOWCONFIG_METADATAENTRY']._serialized_start=1062
  _globals['_WORKFLOWCONFIG_METADATAENTRY']._serialized_end=1109
  _globals['_LISTWORKFLOWSREQUEST']._serialized_start=1140
  _globals['_LISTWORKFLOWSREQUEST']._serialized_end=1185
  _globals['_LISTWORKFLOWSRESPONSE']._serialized_start=1187
  _globals['_LISTWORKFLOWSRESPONSE']._serialized_end=1253
  _globals['_INBOUNDCLIENTMESSAGE']._serialized_start=1255
  _globals['_INBOUNDCLIENTMESSAGE']._serialized_end=1277
  _globals['_OUTBOUNDCLIENTMESSAGE']._serialized_start=1279
  _globals['_OUTBOUNDCLIENTMESSAGE']._serialized_end=1302
  _globals['_WORKFLOWRESULT']._serialized_start=1305
  _globals['_WORKFLOWRESULT']._serialized_end=1514
  _globals['_WORKFLOWRESULT_METADATAENTRY']._serialized_start=1062
  _globals['_WORKFLOWRESULT_METADATAENTRY']._serialized_end=1109
  _globals['_WORKFLOWJOB']._serialized_start=1517
  _globals['_WORKFLOWJOB']._serialized_end=1756
  _globals['_WORKFLOWJOB_METADATAENTRY']._serialized_start=1062
  _globals['_WORKFLOWJOB_METADATAENTRY']._serialized_end=1109
# @@protoc_insertion_point(module_scope)
