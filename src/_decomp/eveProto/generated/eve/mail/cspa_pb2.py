#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\mail\cspa_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.isk import isk_pb2 as eve_dot_isk_dot_isk__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/mail/cspa.proto', package='eve.mail.cspa', syntax='proto3', serialized_options='Z8github.com/ccpgames/eve-proto-go/generated/eve/mail/cspa', create_key=_descriptor._internal_create_key, serialized_pb='\n\x13eve/mail/cspa.proto\x12\reve.mail.cspa\x1a\x1deve/character/character.proto\x1a\x11eve/isk/isk.proto"+\n\x06Charge\x12!\n\x06amount\x18\x01 \x01(\x0b2\x11.eve.isk.Currency"\x80\x01\n\nGetRequest\x126\n\x13sender_character_id\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12:\n\x17recipient_character_ids\x18\x02 \x03(\x0b2\x19.eve.character.Identifier"9\n\x0bGetResponse\x12*\n\x0bcspa_charge\x18\x01 \x01(\x0b2\x15.eve.mail.cspa.ChargeB:Z8github.com/ccpgames/eve-proto-go/generated/eve/mail/cspab\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_isk_dot_isk__pb2.DESCRIPTOR])
_CHARGE = _descriptor.Descriptor(name='Charge', full_name='eve.mail.cspa.Charge', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='amount', full_name='eve.mail.cspa.Charge.amount', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=88, serialized_end=131)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.mail.cspa.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sender_character_id', full_name='eve.mail.cspa.GetRequest.sender_character_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='recipient_character_ids', full_name='eve.mail.cspa.GetRequest.recipient_character_ids', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=134, serialized_end=262)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.mail.cspa.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='cspa_charge', full_name='eve.mail.cspa.GetResponse.cspa_charge', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=264, serialized_end=321)
_CHARGE.fields_by_name['amount'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_GETREQUEST.fields_by_name['sender_character_id'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETREQUEST.fields_by_name['recipient_character_ids'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['cspa_charge'].message_type = _CHARGE
DESCRIPTOR.message_types_by_name['Charge'] = _CHARGE
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Charge = _reflection.GeneratedProtocolMessageType('Charge', (_message.Message,), {'DESCRIPTOR': _CHARGE,
 '__module__': 'eve.mail.cspa_pb2'})
_sym_db.RegisterMessage(Charge)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.mail.cspa_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.mail.cspa_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
