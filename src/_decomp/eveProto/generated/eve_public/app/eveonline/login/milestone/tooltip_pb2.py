#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\eveonline\login\milestone\tooltip_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.login import milestone_pb2 as eve__public_dot_login_dot_milestone__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/eveonline/login/milestone/tooltip.proto', package='eve_public.app.eveonline.login.milestone.tooltip', syntax='proto3', serialized_options='Z[github.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/login/milestone/tooltip', create_key=_descriptor._internal_create_key, serialized_pb='\n6eve_public/app/eveonline/login/milestone/tooltip.proto\x120eve_public.app.eveonline.login.milestone.tooltip\x1a eve_public/login/milestone.proto"F\n\tDisplayed\x129\n\tmilestone\x18\x01 \x01(\x0b2&.eve_public.login.milestone.IdentifierB]Z[github.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/login/milestone/tooltipb\x06proto3', dependencies=[eve__public_dot_login_dot_milestone__pb2.DESCRIPTOR])
_DISPLAYED = _descriptor.Descriptor(name='Displayed', full_name='eve_public.app.eveonline.login.milestone.tooltip.Displayed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='milestone', full_name='eve_public.app.eveonline.login.milestone.tooltip.Displayed.milestone', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=142, serialized_end=212)
_DISPLAYED.fields_by_name['milestone'].message_type = eve__public_dot_login_dot_milestone__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Displayed'] = _DISPLAYED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Displayed = _reflection.GeneratedProtocolMessageType('Displayed', (_message.Message,), {'DESCRIPTOR': _DISPLAYED,
 '__module__': 'eve_public.app.eveonline.login.milestone.tooltip_pb2'})
_sym_db.RegisterMessage(Displayed)
DESCRIPTOR._options = None
