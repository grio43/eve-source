#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\assets\ship_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.asset import asset_pb2 as eve_dot_asset_dot_asset__pb2
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.ship import ship_pb2 as eve_dot_ship_dot_ship__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/assets/ship.proto', package='eve.character.assets.ship', syntax='proto3', serialized_options='ZDgithub.com/ccpgames/eve-proto-go/generated/eve/character/assets/ship', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1feve/character/assets/ship.proto\x12\x19eve.character.assets.ship\x1a\x15eve/asset/asset.proto\x1a\x1deve/character/character.proto\x1a\x13eve/ship/ship.proto"u\n GetAssetsForMultipleShipsRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12#\n\x05ships\x18\x02 \x03(\x0b2\x14.eve.ship.Identifier"P\n!GetAssetsForMultipleShipsResponse\x12+\n\x06assets\x18\x01 \x03(\x0b2\x1b.eve.asset.ShipAssetDetailsBFZDgithub.com/ccpgames/eve-proto-go/generated/eve/character/assets/shipb\x06proto3', dependencies=[eve_dot_asset_dot_asset__pb2.DESCRIPTOR, eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_ship_dot_ship__pb2.DESCRIPTOR])
_GETASSETSFORMULTIPLESHIPSREQUEST = _descriptor.Descriptor(name='GetAssetsForMultipleShipsRequest', full_name='eve.character.assets.ship.GetAssetsForMultipleShipsRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.assets.ship.GetAssetsForMultipleShipsRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='ships', full_name='eve.character.assets.ship.GetAssetsForMultipleShipsRequest.ships', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=137, serialized_end=254)
_GETASSETSFORMULTIPLESHIPSRESPONSE = _descriptor.Descriptor(name='GetAssetsForMultipleShipsResponse', full_name='eve.character.assets.ship.GetAssetsForMultipleShipsResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='assets', full_name='eve.character.assets.ship.GetAssetsForMultipleShipsResponse.assets', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=256, serialized_end=336)
_GETASSETSFORMULTIPLESHIPSREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETASSETSFORMULTIPLESHIPSREQUEST.fields_by_name['ships'].message_type = eve_dot_ship_dot_ship__pb2._IDENTIFIER
_GETASSETSFORMULTIPLESHIPSRESPONSE.fields_by_name['assets'].message_type = eve_dot_asset_dot_asset__pb2._SHIPASSETDETAILS
DESCRIPTOR.message_types_by_name['GetAssetsForMultipleShipsRequest'] = _GETASSETSFORMULTIPLESHIPSREQUEST
DESCRIPTOR.message_types_by_name['GetAssetsForMultipleShipsResponse'] = _GETASSETSFORMULTIPLESHIPSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetAssetsForMultipleShipsRequest = _reflection.GeneratedProtocolMessageType('GetAssetsForMultipleShipsRequest', (_message.Message,), {'DESCRIPTOR': _GETASSETSFORMULTIPLESHIPSREQUEST,
 '__module__': 'eve.character.assets.ship_pb2'})
_sym_db.RegisterMessage(GetAssetsForMultipleShipsRequest)
GetAssetsForMultipleShipsResponse = _reflection.GeneratedProtocolMessageType('GetAssetsForMultipleShipsResponse', (_message.Message,), {'DESCRIPTOR': _GETASSETSFORMULTIPLESHIPSRESPONSE,
 '__module__': 'eve.character.assets.ship_pb2'})
_sym_db.RegisterMessage(GetAssetsForMultipleShipsResponse)
DESCRIPTOR._options = None
