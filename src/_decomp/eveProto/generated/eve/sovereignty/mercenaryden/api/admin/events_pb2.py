#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\sovereignty\mercenaryden\api\admin\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.sovereignty.mercenaryden import mercenaryden_pb2 as eve_dot_sovereignty_dot_mercenaryden_dot_mercenaryden__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/sovereignty/mercenaryden/api/admin/events.proto', package='eve.sovereignty.mercenaryden.api.admin', syntax='proto3', serialized_options='ZQgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/mercenaryden/api/admin', create_key=_descriptor._internal_create_key, serialized_pb='\n3eve/sovereignty/mercenaryden/api/admin/events.proto\x12&eve.sovereignty.mercenaryden.api.admin\x1a/eve/sovereignty/mercenaryden/mercenaryden.proto"i\n\x12InfomorphsModified\x12?\n\rmercenary_den\x18\x01 \x01(\x0b2(.eve.sovereignty.mercenaryden.Identifier\x12\x12\n\ninfomorphs\x18\x02 \x01(\rBSZQgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/mercenaryden/api/adminb\x06proto3', dependencies=[eve_dot_sovereignty_dot_mercenaryden_dot_mercenaryden__pb2.DESCRIPTOR])
_INFOMORPHSMODIFIED = _descriptor.Descriptor(name='InfomorphsModified', full_name='eve.sovereignty.mercenaryden.api.admin.InfomorphsModified', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='mercenary_den', full_name='eve.sovereignty.mercenaryden.api.admin.InfomorphsModified.mercenary_den', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='infomorphs', full_name='eve.sovereignty.mercenaryden.api.admin.InfomorphsModified.infomorphs', index=1, number=2, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=144, serialized_end=249)
_INFOMORPHSMODIFIED.fields_by_name['mercenary_den'].message_type = eve_dot_sovereignty_dot_mercenaryden_dot_mercenaryden__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['InfomorphsModified'] = _INFOMORPHSMODIFIED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
InfomorphsModified = _reflection.GeneratedProtocolMessageType('InfomorphsModified', (_message.Message,), {'DESCRIPTOR': _INFOMORPHSMODIFIED,
 '__module__': 'eve.sovereignty.mercenaryden.api.admin.events_pb2'})
_sym_db.RegisterMessage(InfomorphsModified)
DESCRIPTOR._options = None
