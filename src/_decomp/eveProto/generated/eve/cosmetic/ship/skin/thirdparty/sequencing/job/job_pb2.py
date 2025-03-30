#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\ship\skin\thirdparty\sequencing\job\job_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.cosmetic.ship.skin.thirdparty import thirdparty_pb2 as eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_thirdparty__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/ship/skin/thirdparty/sequencing/job/job.proto', package='eve.cosmetic.ship.skin.thirdparty.sequencing.job', syntax='proto3', serialized_options='Z[github.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/thirdparty/sequencing/job', create_key=_descriptor._internal_create_key, serialized_pb='\n:eve/cosmetic/ship/skin/thirdparty/sequencing/job/job.proto\x120eve.cosmetic.ship.skin.thirdparty.sequencing.job\x1a\x1deve/character/character.proto\x1a2eve/cosmetic/ship/skin/thirdparty/thirdparty.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\x1a\n\nIdentifier\x12\x0c\n\x04uuid\x18\x01 \x01(\x0c"\x8b\x03\n\nAttributes\x12;\n\x04skin\x18\x01 \x01(\x0b2-.eve.cosmetic.ship.skin.thirdparty.Identifier\x12,\n\tsequencer\x18\x02 \x01(\x0b2\x19.eve.character.Identifier\x12\x10\n\x08quantity\x18\x03 \x01(\x04\x12\x11\n\x07pending\x18\x04 \x01(\x08H\x00\x12-\n\x07started\x18\x05 \x01(\x0b2\x1a.google.protobuf.TimestampH\x00\x12K\n\x06failed\x18\x06 \x01(\x0e29.eve.cosmetic.ship.skin.thirdparty.sequencing.job.FailureH\x00\x12/\n\tcompleted\x18\x07 \x01(\x0b2\x1a.google.protobuf.TimestampH\x00\x126\n\x12planned_completion\x18\x08 \x01(\x0b2\x1a.google.protobuf.TimestampB\x08\n\x06status*\x7f\n\x07Failure\x12\x17\n\x13FAILURE_UNSPECIFIED\x10\x00\x12\x19\n\x15FAILURE_MISSING_FUNDS\x10\x01\x12\x1d\n\x19FAILURE_MISSING_RESOURCES\x10\x03\x12!\n\x1dFAILURE_INTERNAL_SERVER_ERROR\x10\x04B]Z[github.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/thirdparty/sequencing/jobb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_thirdparty__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_FAILURE = _descriptor.EnumDescriptor(name='Failure', full_name='eve.cosmetic.ship.skin.thirdparty.sequencing.job.Failure', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='FAILURE_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='FAILURE_MISSING_FUNDS', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='FAILURE_MISSING_RESOURCES', index=2, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='FAILURE_INTERNAL_SERVER_ERROR', index=3, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=654, serialized_end=781)
_sym_db.RegisterEnumDescriptor(_FAILURE)
Failure = enum_type_wrapper.EnumTypeWrapper(_FAILURE)
FAILURE_UNSPECIFIED = 0
FAILURE_MISSING_FUNDS = 1
FAILURE_MISSING_RESOURCES = 3
FAILURE_INTERNAL_SERVER_ERROR = 4
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.cosmetic.ship.skin.thirdparty.sequencing.job.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='uuid', full_name='eve.cosmetic.ship.skin.thirdparty.sequencing.job.Identifier.uuid', index=0, number=1, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=228, serialized_end=254)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.cosmetic.ship.skin.thirdparty.sequencing.job.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='skin', full_name='eve.cosmetic.ship.skin.thirdparty.sequencing.job.Attributes.skin', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='sequencer', full_name='eve.cosmetic.ship.skin.thirdparty.sequencing.job.Attributes.sequencer', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='quantity', full_name='eve.cosmetic.ship.skin.thirdparty.sequencing.job.Attributes.quantity', index=2, number=3, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='pending', full_name='eve.cosmetic.ship.skin.thirdparty.sequencing.job.Attributes.pending', index=3, number=4, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='started', full_name='eve.cosmetic.ship.skin.thirdparty.sequencing.job.Attributes.started', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='failed', full_name='eve.cosmetic.ship.skin.thirdparty.sequencing.job.Attributes.failed', index=5, number=6, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='completed', full_name='eve.cosmetic.ship.skin.thirdparty.sequencing.job.Attributes.completed', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='planned_completion', full_name='eve.cosmetic.ship.skin.thirdparty.sequencing.job.Attributes.planned_completion', index=7, number=8, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='status', full_name='eve.cosmetic.ship.skin.thirdparty.sequencing.job.Attributes.status', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=257, serialized_end=652)
_ATTRIBUTES.fields_by_name['skin'].message_type = eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_thirdparty__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['sequencer'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['started'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['failed'].enum_type = _FAILURE
_ATTRIBUTES.fields_by_name['completed'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['planned_completion'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.oneofs_by_name['status'].fields.append(_ATTRIBUTES.fields_by_name['pending'])
_ATTRIBUTES.fields_by_name['pending'].containing_oneof = _ATTRIBUTES.oneofs_by_name['status']
_ATTRIBUTES.oneofs_by_name['status'].fields.append(_ATTRIBUTES.fields_by_name['started'])
_ATTRIBUTES.fields_by_name['started'].containing_oneof = _ATTRIBUTES.oneofs_by_name['status']
_ATTRIBUTES.oneofs_by_name['status'].fields.append(_ATTRIBUTES.fields_by_name['failed'])
_ATTRIBUTES.fields_by_name['failed'].containing_oneof = _ATTRIBUTES.oneofs_by_name['status']
_ATTRIBUTES.oneofs_by_name['status'].fields.append(_ATTRIBUTES.fields_by_name['completed'])
_ATTRIBUTES.fields_by_name['completed'].containing_oneof = _ATTRIBUTES.oneofs_by_name['status']
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.enum_types_by_name['Failure'] = _FAILURE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.cosmetic.ship.skin.thirdparty.sequencing.job.job_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.cosmetic.ship.skin.thirdparty.sequencing.job.job_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
