#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\sovereignty\mercenaryden\activity\activity_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.sovereignty.mercenaryden.activity.activitytemplate import activitytemplate_pb2 as eve_dot_sovereignty_dot_mercenaryden_dot_activity_dot_activitytemplate_dot_activitytemplate__pb2
from eveProto.generated.eve.sovereignty.mercenaryden import mercenaryden_pb2 as eve_dot_sovereignty_dot_mercenaryden_dot_mercenaryden__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/sovereignty/mercenaryden/activity/activity.proto', package='eve.sovereignty.mercenaryden.activity', syntax='proto3', serialized_options='ZPgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/mercenaryden/activity', create_key=_descriptor._internal_create_key, serialized_pb='\n4eve/sovereignty/mercenaryden/activity/activity.proto\x12%eve.sovereignty.mercenaryden.activity\x1a\x1deve/character/character.proto\x1aMeve/sovereignty/mercenaryden/activity/activitytemplate/activitytemplate.proto\x1a/eve/sovereignty/mercenaryden/mercenaryden.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\x1a\n\nIdentifier\x12\x0c\n\x04uuid\x18\x01 \x01(\x0c"\x96\x02\n\nAttributes\x12\\\n\x10activitytemplate\x18\x01 \x01(\x0b2B.eve.sovereignty.mercenaryden.activity.activitytemplate.Definition\x12?\n\rmercenary_den\x18\x02 \x01(\x0b2(.eve.sovereignty.mercenaryden.Identifier\x12,\n\tcharacter\x18\x03 \x01(\x0b2\x19.eve.character.Identifier\x12\x0f\n\x07started\x18\x04 \x01(\x08\x12*\n\x06expiry\x18\x05 \x01(\x0b2\x1a.google.protobuf.TimestampBRZPgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/mercenaryden/activityb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_sovereignty_dot_mercenaryden_dot_activity_dot_activitytemplate_dot_activitytemplate__pb2.DESCRIPTOR,
 eve_dot_sovereignty_dot_mercenaryden_dot_mercenaryden__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.sovereignty.mercenaryden.activity.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='uuid', full_name='eve.sovereignty.mercenaryden.activity.Identifier.uuid', index=0, number=1, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=287, serialized_end=313)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.sovereignty.mercenaryden.activity.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='activitytemplate', full_name='eve.sovereignty.mercenaryden.activity.Attributes.activitytemplate', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='mercenary_den', full_name='eve.sovereignty.mercenaryden.activity.Attributes.mercenary_den', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='character', full_name='eve.sovereignty.mercenaryden.activity.Attributes.character', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='started', full_name='eve.sovereignty.mercenaryden.activity.Attributes.started', index=3, number=4, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='expiry', full_name='eve.sovereignty.mercenaryden.activity.Attributes.expiry', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=316, serialized_end=594)
_ATTRIBUTES.fields_by_name['activitytemplate'].message_type = eve_dot_sovereignty_dot_mercenaryden_dot_activity_dot_activitytemplate_dot_activitytemplate__pb2._DEFINITION
_ATTRIBUTES.fields_by_name['mercenary_den'].message_type = eve_dot_sovereignty_dot_mercenaryden_dot_mercenaryden__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['expiry'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.sovereignty.mercenaryden.activity.activity_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.sovereignty.mercenaryden.activity.activity_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
