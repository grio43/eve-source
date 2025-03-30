#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\dungeon\instance_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.sovereignty.mercenaryden.activity import activity_pb2 as eve__public_dot_sovereignty_dot_mercenaryden_dot_activity_dot_activity__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/dungeon/instance.proto', package='eve_public.dungeon.instance', syntax='proto3', serialized_options='ZFgithub.com/ccpgames/eve-proto-go/generated/eve_public/dungeon/instance', create_key=_descriptor._internal_create_key, serialized_pb='\n!eve_public/dungeon/instance.proto\x12\x1beve_public.dungeon.instance\x1a;eve_public/sovereignty/mercenaryden/activity/activity.proto"\xc8\x01\n\nIdentifier\x12\x13\n\tpermanent\x18\x01 \x01(\x04H\x00\x12\x13\n\tephemeral\x18\x02 \x01(\x03H\x00\x12\x0f\n\x05admin\x18\x03 \x01(\x08H\x00\x12\x11\n\x07unknown\x18\x04 \x01(\x08H\x00\x12L\n\x08activity\x18\x05 \x01(\x0b28.eve_public.sovereignty.mercenaryden.activity.IdentifierH\x00\x12\x0e\n\x04uuid\x18\x06 \x01(\x0cH\x00B\x0e\n\x0cdistributionBHZFgithub.com/ccpgames/eve-proto-go/generated/eve_public/dungeon/instanceb\x06proto3', dependencies=[eve__public_dot_sovereignty_dot_mercenaryden_dot_activity_dot_activity__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve_public.dungeon.instance.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='permanent', full_name='eve_public.dungeon.instance.Identifier.permanent', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='ephemeral', full_name='eve_public.dungeon.instance.Identifier.ephemeral', index=1, number=2, type=3, cpp_type=2, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='admin', full_name='eve_public.dungeon.instance.Identifier.admin', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unknown', full_name='eve_public.dungeon.instance.Identifier.unknown', index=3, number=4, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='activity', full_name='eve_public.dungeon.instance.Identifier.activity', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='uuid', full_name='eve_public.dungeon.instance.Identifier.uuid', index=5, number=6, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='distribution', full_name='eve_public.dungeon.instance.Identifier.distribution', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=128, serialized_end=328)
_IDENTIFIER.fields_by_name['activity'].message_type = eve__public_dot_sovereignty_dot_mercenaryden_dot_activity_dot_activity__pb2._IDENTIFIER
_IDENTIFIER.oneofs_by_name['distribution'].fields.append(_IDENTIFIER.fields_by_name['permanent'])
_IDENTIFIER.fields_by_name['permanent'].containing_oneof = _IDENTIFIER.oneofs_by_name['distribution']
_IDENTIFIER.oneofs_by_name['distribution'].fields.append(_IDENTIFIER.fields_by_name['ephemeral'])
_IDENTIFIER.fields_by_name['ephemeral'].containing_oneof = _IDENTIFIER.oneofs_by_name['distribution']
_IDENTIFIER.oneofs_by_name['distribution'].fields.append(_IDENTIFIER.fields_by_name['admin'])
_IDENTIFIER.fields_by_name['admin'].containing_oneof = _IDENTIFIER.oneofs_by_name['distribution']
_IDENTIFIER.oneofs_by_name['distribution'].fields.append(_IDENTIFIER.fields_by_name['unknown'])
_IDENTIFIER.fields_by_name['unknown'].containing_oneof = _IDENTIFIER.oneofs_by_name['distribution']
_IDENTIFIER.oneofs_by_name['distribution'].fields.append(_IDENTIFIER.fields_by_name['activity'])
_IDENTIFIER.fields_by_name['activity'].containing_oneof = _IDENTIFIER.oneofs_by_name['distribution']
_IDENTIFIER.oneofs_by_name['distribution'].fields.append(_IDENTIFIER.fields_by_name['uuid'])
_IDENTIFIER.fields_by_name['uuid'].containing_oneof = _IDENTIFIER.oneofs_by_name['distribution']
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve_public.dungeon.instance_pb2'})
_sym_db.RegisterMessage(Identifier)
DESCRIPTOR._options = None
