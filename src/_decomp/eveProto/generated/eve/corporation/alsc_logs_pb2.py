#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\corporation\alsc_logs_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.inventory.container.secure import auditlog_pb2 as eve_dot_inventory_dot_container_dot_secure_dot_auditlog__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/corporation/alsc_logs.proto', package='eve.corporation.alsclogs', syntax='proto3', serialized_options='ZCgithub.com/ccpgames/eve-proto-go/generated/eve/corporation/alsclogs', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1feve/corporation/alsc_logs.proto\x12\x18eve.corporation.alsclogs\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a-eve/inventory/container/secure/auditlog.proto"\x95\x01\n\nGetRequest\x120\n\x0bcorporation\x18\x01 \x01(\x0b2\x1b.eve.corporation.Identifier\x124\n\x11requesting_member\x18\x02 \x01(\x0b2\x19.eve.character.Identifier\x12\x0c\n\x04page\x18\x03 \x01(\r\x12\x11\n\tpage_size\x18\x04 \x01(\r"N\n\x0bGetResponse\x12?\n\x07entries\x18\x01 \x03(\x0b2..eve.inventory.container.secure.auditlog.EntryBEZCgithub.com/ccpgames/eve-proto-go/generated/eve/corporation/alsclogsb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR, eve_dot_inventory_dot_container_dot_secure_dot_auditlog__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.corporation.alsclogs.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='corporation', full_name='eve.corporation.alsclogs.GetRequest.corporation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='requesting_member', full_name='eve.corporation.alsclogs.GetRequest.requesting_member', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='page', full_name='eve.corporation.alsclogs.GetRequest.page', index=2, number=3, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='page_size', full_name='eve.corporation.alsclogs.GetRequest.page_size', index=3, number=4, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=175, serialized_end=324)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.corporation.alsclogs.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='entries', full_name='eve.corporation.alsclogs.GetResponse.entries', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=326, serialized_end=404)
_GETREQUEST.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_GETREQUEST.fields_by_name['requesting_member'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['entries'].message_type = eve_dot_inventory_dot_container_dot_secure_dot_auditlog__pb2._ENTRY
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.corporation.alsc_logs_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.corporation.alsc_logs_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
