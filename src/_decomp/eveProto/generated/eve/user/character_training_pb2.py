#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\user\character_training_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/user/character_training.proto', package='eve.user.character_training', syntax='proto3', serialized_options='ZFgithub.com/ccpgames/eve-proto-go/generated/eve/user/character_training', create_key=_descriptor._internal_create_key, serialized_pb='\n!eve/user/character_training.proto\x12\x1beve.user.character_training\x1a\x13eve/user/user.proto\x1a\x1fgoogle/protobuf/timestamp.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x11"m\n\x04Slot\x125\n\x04slot\x18\x01 \x01(\x0b2\'.eve.user.character_training.Identifier\x12.\n\nexpires_at\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp"5\n\x0fGetSlotsRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"D\n\x10GetSlotsResponse\x120\n\x05slots\x18\x01 \x03(\x0b2!.eve.user.character_training.SlotBHZFgithub.com/ccpgames/eve-proto-go/generated/eve/user/character_trainingb\x06proto3', dependencies=[eve_dot_user_dot_user__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.user.character_training.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.user.character_training.Identifier.sequential', index=0, number=1, type=17, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=120, serialized_end=152)
_SLOT = _descriptor.Descriptor(name='Slot', full_name='eve.user.character_training.Slot', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='slot', full_name='eve.user.character_training.Slot.slot', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='expires_at', full_name='eve.user.character_training.Slot.expires_at', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=154, serialized_end=263)
_GETSLOTSREQUEST = _descriptor.Descriptor(name='GetSlotsRequest', full_name='eve.user.character_training.GetSlotsRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.character_training.GetSlotsRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=265, serialized_end=318)
_GETSLOTSRESPONSE = _descriptor.Descriptor(name='GetSlotsResponse', full_name='eve.user.character_training.GetSlotsResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='slots', full_name='eve.user.character_training.GetSlotsResponse.slots', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=320, serialized_end=388)
_SLOT.fields_by_name['slot'].message_type = _IDENTIFIER
_SLOT.fields_by_name['expires_at'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_GETSLOTSREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_GETSLOTSRESPONSE.fields_by_name['slots'].message_type = _SLOT
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Slot'] = _SLOT
DESCRIPTOR.message_types_by_name['GetSlotsRequest'] = _GETSLOTSREQUEST
DESCRIPTOR.message_types_by_name['GetSlotsResponse'] = _GETSLOTSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.user.character_training_pb2'})
_sym_db.RegisterMessage(Identifier)
Slot = _reflection.GeneratedProtocolMessageType('Slot', (_message.Message,), {'DESCRIPTOR': _SLOT,
 '__module__': 'eve.user.character_training_pb2'})
_sym_db.RegisterMessage(Slot)
GetSlotsRequest = _reflection.GeneratedProtocolMessageType('GetSlotsRequest', (_message.Message,), {'DESCRIPTOR': _GETSLOTSREQUEST,
 '__module__': 'eve.user.character_training_pb2'})
_sym_db.RegisterMessage(GetSlotsRequest)
GetSlotsResponse = _reflection.GeneratedProtocolMessageType('GetSlotsResponse', (_message.Message,), {'DESCRIPTOR': _GETSLOTSRESPONSE,
 '__module__': 'eve.user.character_training_pb2'})
_sym_db.RegisterMessage(GetSlotsResponse)
DESCRIPTOR._options = None
