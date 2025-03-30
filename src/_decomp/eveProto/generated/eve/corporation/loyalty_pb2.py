#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\corporation\loyalty_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/corporation/loyalty.proto', package='eve.corporation.loyalty', syntax='proto3', serialized_options='ZBgithub.com/ccpgames/eve-proto-go/generated/eve/corporation/loyalty', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1deve/corporation/loyalty.proto\x12\x17eve.corporation.loyalty\x1a!eve/corporation/corporation.proto"U\n\x06Points\x12\x0e\n\x06amount\x18\x01 \x01(\x04\x12;\n\x16associated_corporation\x18\x02 \x01(\x0b2\x1b.eve.corporation.IdentifierBDZBgithub.com/ccpgames/eve-proto-go/generated/eve/corporation/loyaltyb\x06proto3', dependencies=[eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR])
_POINTS = _descriptor.Descriptor(name='Points', full_name='eve.corporation.loyalty.Points', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='amount', full_name='eve.corporation.loyalty.Points.amount', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='associated_corporation', full_name='eve.corporation.loyalty.Points.associated_corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=93, serialized_end=178)
_POINTS.fields_by_name['associated_corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Points'] = _POINTS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Points = _reflection.GeneratedProtocolMessageType('Points', (_message.Message,), {'DESCRIPTOR': _POINTS,
 '__module__': 'eve.corporation.loyalty_pb2'})
_sym_db.RegisterMessage(Points)
DESCRIPTOR._options = None
