#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\killmail\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.constellation import constellation_pb2 as eve_dot_constellation_dot_constellation__pb2
from eveProto.generated.eve.isk import isk_pb2 as eve_dot_isk_dot_isk__pb2
from eveProto.generated.eve.killmail import killmail_pb2 as eve_dot_killmail_dot_killmail__pb2
from eveProto.generated.eve.pvp import pvp_pb2 as eve_dot_pvp_dot_pvp__pb2
from eveProto.generated.eve.region import region_pb2 as eve_dot_region_dot_region__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/killmail/api/events.proto', package='eve.killmail.api', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve/killmail/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1deve/killmail/api/events.proto\x12\x10eve.killmail.api\x1a%eve/constellation/constellation.proto\x1a\x11eve/isk/isk.proto\x1a\x1beve/killmail/killmail.proto\x1a\x11eve/pvp/pvp.proto\x1a\x17eve/region/region.proto\x1a!eve/solarsystem/solarsystem.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\xb4\x03\n\x0eShipLossReport\x12$\n\x02id\x18\x01 \x01(\x0b2\x18.eve.killmail.Identifier\x12-\n\ttimestamp\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x121\n\x0csolar_system\x18\x03 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x124\n\rconstellation\x18\x04 \x01(\x0b2\x1d.eve.constellation.Identifier\x12&\n\x06region\x18\x05 \x01(\x0b2\x16.eve.region.Identifier\x12\x1e\n\x14non_player_character\x18\x06 \x01(\x08H\x00\x12(\n\x08attacker\x18\x07 \x01(\x0b2\x14.eve.pvp.ParticipantH\x00\x12$\n\x06victim\x18\x08 \x01(\x0b2\x14.eve.pvp.Participant\x12*\n\x0ftotal_isk_value\x18\t \x01(\x0b2\x11.eve.isk.Currency\x12\x12\n\nis_capsule\x18\n \x01(\x08B\x0c\n\nfinal_blowB=Z;github.com/ccpgames/eve-proto-go/generated/eve/killmail/apib\x06proto3', dependencies=[eve_dot_constellation_dot_constellation__pb2.DESCRIPTOR,
 eve_dot_isk_dot_isk__pb2.DESCRIPTOR,
 eve_dot_killmail_dot_killmail__pb2.DESCRIPTOR,
 eve_dot_pvp_dot_pvp__pb2.DESCRIPTOR,
 eve_dot_region_dot_region__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_SHIPLOSSREPORT = _descriptor.Descriptor(name='ShipLossReport', full_name='eve.killmail.api.ShipLossReport', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.killmail.api.ShipLossReport.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='timestamp', full_name='eve.killmail.api.ShipLossReport.timestamp', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.killmail.api.ShipLossReport.solar_system', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='constellation', full_name='eve.killmail.api.ShipLossReport.constellation', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='region', full_name='eve.killmail.api.ShipLossReport.region', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='non_player_character', full_name='eve.killmail.api.ShipLossReport.non_player_character', index=5, number=6, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='attacker', full_name='eve.killmail.api.ShipLossReport.attacker', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='victim', full_name='eve.killmail.api.ShipLossReport.victim', index=7, number=8, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='total_isk_value', full_name='eve.killmail.api.ShipLossReport.total_isk_value', index=8, number=9, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='is_capsule', full_name='eve.killmail.api.ShipLossReport.is_capsule', index=9, number=10, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='final_blow', full_name='eve.killmail.api.ShipLossReport.final_blow', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=251, serialized_end=687)
_SHIPLOSSREPORT.fields_by_name['id'].message_type = eve_dot_killmail_dot_killmail__pb2._IDENTIFIER
_SHIPLOSSREPORT.fields_by_name['timestamp'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_SHIPLOSSREPORT.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_SHIPLOSSREPORT.fields_by_name['constellation'].message_type = eve_dot_constellation_dot_constellation__pb2._IDENTIFIER
_SHIPLOSSREPORT.fields_by_name['region'].message_type = eve_dot_region_dot_region__pb2._IDENTIFIER
_SHIPLOSSREPORT.fields_by_name['attacker'].message_type = eve_dot_pvp_dot_pvp__pb2._PARTICIPANT
_SHIPLOSSREPORT.fields_by_name['victim'].message_type = eve_dot_pvp_dot_pvp__pb2._PARTICIPANT
_SHIPLOSSREPORT.fields_by_name['total_isk_value'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_SHIPLOSSREPORT.oneofs_by_name['final_blow'].fields.append(_SHIPLOSSREPORT.fields_by_name['non_player_character'])
_SHIPLOSSREPORT.fields_by_name['non_player_character'].containing_oneof = _SHIPLOSSREPORT.oneofs_by_name['final_blow']
_SHIPLOSSREPORT.oneofs_by_name['final_blow'].fields.append(_SHIPLOSSREPORT.fields_by_name['attacker'])
_SHIPLOSSREPORT.fields_by_name['attacker'].containing_oneof = _SHIPLOSSREPORT.oneofs_by_name['final_blow']
DESCRIPTOR.message_types_by_name['ShipLossReport'] = _SHIPLOSSREPORT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
ShipLossReport = _reflection.GeneratedProtocolMessageType('ShipLossReport', (_message.Message,), {'DESCRIPTOR': _SHIPLOSSREPORT,
 '__module__': 'eve.killmail.api.events_pb2'})
_sym_db.RegisterMessage(ShipLossReport)
DESCRIPTOR._options = None
