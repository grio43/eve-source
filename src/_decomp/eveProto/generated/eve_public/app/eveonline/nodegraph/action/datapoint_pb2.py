#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\eveonline\nodegraph\action\datapoint_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.nodegraph import nodegraph_pb2 as eve__public_dot_nodegraph_dot_nodegraph__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/eveonline/nodegraph/action/datapoint.proto', package='eve_public.app.eveonline.nodegraph.action.datapoint', syntax='proto3', serialized_options='ZTgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/nodegraph/action', create_key=_descriptor._internal_create_key, serialized_pb='\n9eve_public/app/eveonline/nodegraph/action/datapoint.proto\x123eve_public.app.eveonline.nodegraph.action.datapoint\x1a$eve_public/nodegraph/nodegraph.proto"X\n\tTriggered\x123\n\tnodegraph\x18\x01 \x01(\x0b2 .eve_public.nodegraph.Identifier\x12\x16\n\x0edatapoint_name\x18\x02 \x01(\tBVZTgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/nodegraph/actionb\x06proto3', dependencies=[eve__public_dot_nodegraph_dot_nodegraph__pb2.DESCRIPTOR])
_TRIGGERED = _descriptor.Descriptor(name='Triggered', full_name='eve_public.app.eveonline.nodegraph.action.datapoint.Triggered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='nodegraph', full_name='eve_public.app.eveonline.nodegraph.action.datapoint.Triggered.nodegraph', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='datapoint_name', full_name='eve_public.app.eveonline.nodegraph.action.datapoint.Triggered.datapoint_name', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=152, serialized_end=240)
_TRIGGERED.fields_by_name['nodegraph'].message_type = eve__public_dot_nodegraph_dot_nodegraph__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Triggered'] = _TRIGGERED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Triggered = _reflection.GeneratedProtocolMessageType('Triggered', (_message.Message,), {'DESCRIPTOR': _TRIGGERED,
 '__module__': 'eve_public.app.eveonline.nodegraph.action.datapoint_pb2'})
_sym_db.RegisterMessage(Triggered)
DESCRIPTOR._options = None
