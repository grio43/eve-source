#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\contract\contract_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
from eveProto.generated.eve.station import station_pb2 as eve_dot_station_dot_station__pb2
from eveProto.generated.eve.structure import structure_pb2 as eve_dot_structure_dot_structure__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/contract/contract.proto', package='eve.contract', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/contract', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1beve/contract/contract.proto\x12\x0ceve.contract\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a!eve/solarsystem/solarsystem.proto\x1a\x19eve/station/station.proto\x1a\x1deve/structure/structure.proto\x1a\x1fgoogle/protobuf/timestamp.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"E\n\nAttributes\x12(\n\x04type\x18\x01 \x01(\x0e2\x1a.eve.contract.ContractType\x12\r\n\x05title\x18\x02 \x01(\t"8\n\x08Searched\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"7\n\x07Created\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"8\n\x08Accepted\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"7\n\x07Deleted\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"9\n\tBidPlaced\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"@\n\x10CourierCompleted\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"8\n\x08Rejected\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"\xe9\x01\n\x06Issuer\x12.\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.IdentifierH\x00\x127\n\x0bcorporation\x18\x02 \x01(\x0b2 .eve.contract.Issuer.CorporationH\x00\x1al\n\x0bCorporation\x12/\n\nissued_for\x18\x01 \x01(\x0b2\x1b.eve.corporation.Identifier\x12,\n\tissued_by\x18\x02 \x01(\x0b2\x19.eve.character.IdentifierB\x08\n\x06issuer"\xad\x01\n\x08Acceptor\x121\n\raccepted_time\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12.\n\tcharacter\x18\x02 \x01(\x0b2\x19.eve.character.IdentifierH\x00\x122\n\x0bcorporation\x18\x03 \x01(\x0b2\x1b.eve.corporation.IdentifierH\x00B\n\n\x08acceptor"\xa4\x01\n\x08Location\x12*\n\x07station\x18\x01 \x01(\x0b2\x17.eve.station.IdentifierH\x00\x12.\n\tstructure\x18\x02 \x01(\x0b2\x19.eve.structure.IdentifierH\x00\x120\n\x0bsolarsystem\x18\x03 \x01(\x0b2\x1b.eve.solarsystem.IdentifierB\n\n\x08dockable*Q\n\x0cContractType\x12\x0b\n\x07NOTHING\x10\x00\x12\x10\n\x0cITEMEXCHANGE\x10\x01\x12\x0b\n\x07AUCTION\x10\x02\x12\x0b\n\x07COURIER\x10\x03\x12\x08\n\x04LOAN\x10\x04B9Z7github.com/ccpgames/eve-proto-go/generated/eve/contractb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR,
 eve_dot_station_dot_station__pb2.DESCRIPTOR,
 eve_dot_structure_dot_structure__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_CONTRACTTYPE = _descriptor.EnumDescriptor(name='ContractType', full_name='eve.contract.ContractType', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='NOTHING', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='ITEMEXCHANGE', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='AUCTION', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='COURIER', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='LOAN', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=1334, serialized_end=1415)
_sym_db.RegisterEnumDescriptor(_CONTRACTTYPE)
ContractType = enum_type_wrapper.EnumTypeWrapper(_CONTRACTTYPE)
NOTHING = 0
ITEMEXCHANGE = 1
AUCTION = 2
COURIER = 3
LOAN = 4
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.contract.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.contract.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=237, serialized_end=269)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.contract.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='type', full_name='eve.contract.Attributes.type', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='title', full_name='eve.contract.Attributes.title', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=271, serialized_end=340)
_SEARCHED = _descriptor.Descriptor(name='Searched', full_name='eve.contract.Searched', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.contract.Searched.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=342, serialized_end=398)
_CREATED = _descriptor.Descriptor(name='Created', full_name='eve.contract.Created', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.contract.Created.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=400, serialized_end=455)
_ACCEPTED = _descriptor.Descriptor(name='Accepted', full_name='eve.contract.Accepted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.contract.Accepted.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=457, serialized_end=513)
_DELETED = _descriptor.Descriptor(name='Deleted', full_name='eve.contract.Deleted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.contract.Deleted.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=515, serialized_end=570)
_BIDPLACED = _descriptor.Descriptor(name='BidPlaced', full_name='eve.contract.BidPlaced', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.contract.BidPlaced.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=572, serialized_end=629)
_COURIERCOMPLETED = _descriptor.Descriptor(name='CourierCompleted', full_name='eve.contract.CourierCompleted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.contract.CourierCompleted.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=631, serialized_end=695)
_REJECTED = _descriptor.Descriptor(name='Rejected', full_name='eve.contract.Rejected', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.contract.Rejected.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=697, serialized_end=753)
_ISSUER_CORPORATION = _descriptor.Descriptor(name='Corporation', full_name='eve.contract.Issuer.Corporation', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='issued_for', full_name='eve.contract.Issuer.Corporation.issued_for', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='issued_by', full_name='eve.contract.Issuer.Corporation.issued_by', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=871, serialized_end=979)
_ISSUER = _descriptor.Descriptor(name='Issuer', full_name='eve.contract.Issuer', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.contract.Issuer.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='corporation', full_name='eve.contract.Issuer.corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_ISSUER_CORPORATION], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='issuer', full_name='eve.contract.Issuer.issuer', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=756, serialized_end=989)
_ACCEPTOR = _descriptor.Descriptor(name='Acceptor', full_name='eve.contract.Acceptor', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='accepted_time', full_name='eve.contract.Acceptor.accepted_time', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='character', full_name='eve.contract.Acceptor.character', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='corporation', full_name='eve.contract.Acceptor.corporation', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='acceptor', full_name='eve.contract.Acceptor.acceptor', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=992, serialized_end=1165)
_LOCATION = _descriptor.Descriptor(name='Location', full_name='eve.contract.Location', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='station', full_name='eve.contract.Location.station', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='structure', full_name='eve.contract.Location.structure', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='solarsystem', full_name='eve.contract.Location.solarsystem', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='dockable', full_name='eve.contract.Location.dockable', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=1168, serialized_end=1332)
_ATTRIBUTES.fields_by_name['type'].enum_type = _CONTRACTTYPE
_SEARCHED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_CREATED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ACCEPTED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_DELETED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_BIDPLACED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_COURIERCOMPLETED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_REJECTED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ISSUER_CORPORATION.fields_by_name['issued_for'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_ISSUER_CORPORATION.fields_by_name['issued_by'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ISSUER_CORPORATION.containing_type = _ISSUER
_ISSUER.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ISSUER.fields_by_name['corporation'].message_type = _ISSUER_CORPORATION
_ISSUER.oneofs_by_name['issuer'].fields.append(_ISSUER.fields_by_name['character'])
_ISSUER.fields_by_name['character'].containing_oneof = _ISSUER.oneofs_by_name['issuer']
_ISSUER.oneofs_by_name['issuer'].fields.append(_ISSUER.fields_by_name['corporation'])
_ISSUER.fields_by_name['corporation'].containing_oneof = _ISSUER.oneofs_by_name['issuer']
_ACCEPTOR.fields_by_name['accepted_time'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ACCEPTOR.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ACCEPTOR.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_ACCEPTOR.oneofs_by_name['acceptor'].fields.append(_ACCEPTOR.fields_by_name['character'])
_ACCEPTOR.fields_by_name['character'].containing_oneof = _ACCEPTOR.oneofs_by_name['acceptor']
_ACCEPTOR.oneofs_by_name['acceptor'].fields.append(_ACCEPTOR.fields_by_name['corporation'])
_ACCEPTOR.fields_by_name['corporation'].containing_oneof = _ACCEPTOR.oneofs_by_name['acceptor']
_LOCATION.fields_by_name['station'].message_type = eve_dot_station_dot_station__pb2._IDENTIFIER
_LOCATION.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_LOCATION.fields_by_name['solarsystem'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_LOCATION.oneofs_by_name['dockable'].fields.append(_LOCATION.fields_by_name['station'])
_LOCATION.fields_by_name['station'].containing_oneof = _LOCATION.oneofs_by_name['dockable']
_LOCATION.oneofs_by_name['dockable'].fields.append(_LOCATION.fields_by_name['structure'])
_LOCATION.fields_by_name['structure'].containing_oneof = _LOCATION.oneofs_by_name['dockable']
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Searched'] = _SEARCHED
DESCRIPTOR.message_types_by_name['Created'] = _CREATED
DESCRIPTOR.message_types_by_name['Accepted'] = _ACCEPTED
DESCRIPTOR.message_types_by_name['Deleted'] = _DELETED
DESCRIPTOR.message_types_by_name['BidPlaced'] = _BIDPLACED
DESCRIPTOR.message_types_by_name['CourierCompleted'] = _COURIERCOMPLETED
DESCRIPTOR.message_types_by_name['Rejected'] = _REJECTED
DESCRIPTOR.message_types_by_name['Issuer'] = _ISSUER
DESCRIPTOR.message_types_by_name['Acceptor'] = _ACCEPTOR
DESCRIPTOR.message_types_by_name['Location'] = _LOCATION
DESCRIPTOR.enum_types_by_name['ContractType'] = _CONTRACTTYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.contract.contract_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.contract.contract_pb2'})
_sym_db.RegisterMessage(Attributes)
Searched = _reflection.GeneratedProtocolMessageType('Searched', (_message.Message,), {'DESCRIPTOR': _SEARCHED,
 '__module__': 'eve.contract.contract_pb2'})
_sym_db.RegisterMessage(Searched)
Created = _reflection.GeneratedProtocolMessageType('Created', (_message.Message,), {'DESCRIPTOR': _CREATED,
 '__module__': 'eve.contract.contract_pb2'})
_sym_db.RegisterMessage(Created)
Accepted = _reflection.GeneratedProtocolMessageType('Accepted', (_message.Message,), {'DESCRIPTOR': _ACCEPTED,
 '__module__': 'eve.contract.contract_pb2'})
_sym_db.RegisterMessage(Accepted)
Deleted = _reflection.GeneratedProtocolMessageType('Deleted', (_message.Message,), {'DESCRIPTOR': _DELETED,
 '__module__': 'eve.contract.contract_pb2'})
_sym_db.RegisterMessage(Deleted)
BidPlaced = _reflection.GeneratedProtocolMessageType('BidPlaced', (_message.Message,), {'DESCRIPTOR': _BIDPLACED,
 '__module__': 'eve.contract.contract_pb2'})
_sym_db.RegisterMessage(BidPlaced)
CourierCompleted = _reflection.GeneratedProtocolMessageType('CourierCompleted', (_message.Message,), {'DESCRIPTOR': _COURIERCOMPLETED,
 '__module__': 'eve.contract.contract_pb2'})
_sym_db.RegisterMessage(CourierCompleted)
Rejected = _reflection.GeneratedProtocolMessageType('Rejected', (_message.Message,), {'DESCRIPTOR': _REJECTED,
 '__module__': 'eve.contract.contract_pb2'})
_sym_db.RegisterMessage(Rejected)
Issuer = _reflection.GeneratedProtocolMessageType('Issuer', (_message.Message,), {'Corporation': _reflection.GeneratedProtocolMessageType('Corporation', (_message.Message,), {'DESCRIPTOR': _ISSUER_CORPORATION,
                 '__module__': 'eve.contract.contract_pb2'}),
 'DESCRIPTOR': _ISSUER,
 '__module__': 'eve.contract.contract_pb2'})
_sym_db.RegisterMessage(Issuer)
_sym_db.RegisterMessage(Issuer.Corporation)
Acceptor = _reflection.GeneratedProtocolMessageType('Acceptor', (_message.Message,), {'DESCRIPTOR': _ACCEPTOR,
 '__module__': 'eve.contract.contract_pb2'})
_sym_db.RegisterMessage(Acceptor)
Location = _reflection.GeneratedProtocolMessageType('Location', (_message.Message,), {'DESCRIPTOR': _LOCATION,
 '__module__': 'eve.contract.contract_pb2'})
_sym_db.RegisterMessage(Location)
DESCRIPTOR._options = None
