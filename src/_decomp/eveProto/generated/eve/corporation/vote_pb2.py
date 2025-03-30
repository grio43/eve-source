#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\corporation\vote_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/corporation/vote.proto', package='eve.corporation.vote', syntax='proto3', serialized_options='Z?github.com/ccpgames/eve-proto-go/generated/eve/corporation/vote', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1aeve/corporation/vote.proto\x12\x14eve.corporation.vote\x1a!eve/corporation/corporation.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"A\n\nAttributes\x123\n\x0ecorporation_id\x18\x01 \x01(\x0b2\x1b.eve.corporation.Identifier"<\n\nGetRequest\x12.\n\x04vote\x18\x01 \x01(\x0b2 .eve.corporation.vote.Identifier"=\n\x0bGetResponse\x12.\n\x04vote\x18\x01 \x01(\x0b2 .eve.corporation.vote.Attributes"?\n\nVoteCalled\x121\n\x07vote_id\x18\x01 \x01(\x0b2 .eve.corporation.vote.IdentifierBAZ?github.com/ccpgames/eve-proto-go/generated/eve/corporation/voteb\x06proto3', dependencies=[eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.corporation.vote.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.corporation.vote.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=87, serialized_end=119)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.corporation.vote.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='corporation_id', full_name='eve.corporation.vote.Attributes.corporation_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=121, serialized_end=186)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.corporation.vote.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='vote', full_name='eve.corporation.vote.GetRequest.vote', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=188, serialized_end=248)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.corporation.vote.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='vote', full_name='eve.corporation.vote.GetResponse.vote', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=250, serialized_end=311)
_VOTECALLED = _descriptor.Descriptor(name='VoteCalled', full_name='eve.corporation.vote.VoteCalled', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='vote_id', full_name='eve.corporation.vote.VoteCalled.vote_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=313, serialized_end=376)
_ATTRIBUTES.fields_by_name['corporation_id'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_GETREQUEST.fields_by_name['vote'].message_type = _IDENTIFIER
_GETRESPONSE.fields_by_name['vote'].message_type = _ATTRIBUTES
_VOTECALLED.fields_by_name['vote_id'].message_type = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['VoteCalled'] = _VOTECALLED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.corporation.vote_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.corporation.vote_pb2'})
_sym_db.RegisterMessage(Attributes)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.corporation.vote_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.corporation.vote_pb2'})
_sym_db.RegisterMessage(GetResponse)
VoteCalled = _reflection.GeneratedProtocolMessageType('VoteCalled', (_message.Message,), {'DESCRIPTOR': _VOTECALLED,
 '__module__': 'eve.corporation.vote_pb2'})
_sym_db.RegisterMessage(VoteCalled)
DESCRIPTOR._options = None
