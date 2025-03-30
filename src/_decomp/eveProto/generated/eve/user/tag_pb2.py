#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\user\tag_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/user/tag.proto', package='eve.user.tag', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/user/tag\xaa\x02\rEve.User.Tags', create_key=_descriptor._internal_create_key, serialized_pb='\n\x12eve/user/tag.proto\x12\x0ceve.user.tag\x1a\x13eve/user/user.proto"r\n\nAddRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier\x12\x1a\n\x03tag\x18\x02 \x03(\x0b2\r.eve.user.Tag\x12$\n\x06tagger\x18\x03 \x01(\x0b2\x14.eve.user.IdentifierBIZ7github.com/ccpgames/eve-proto-go/generated/eve/user/tag\xaa\x02\rEve.User.Tagsb\x06proto3', dependencies=[eve_dot_user_dot_user__pb2.DESCRIPTOR])
_ADDREQUEST = _descriptor.Descriptor(name='AddRequest', full_name='eve.user.tag.AddRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.tag.AddRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='tag', full_name='eve.user.tag.AddRequest.tag', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='tagger', full_name='eve.user.tag.AddRequest.tagger', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=57, serialized_end=171)
_ADDREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_ADDREQUEST.fields_by_name['tag'].message_type = eve_dot_user_dot_user__pb2._TAG
_ADDREQUEST.fields_by_name['tagger'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['AddRequest'] = _ADDREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
AddRequest = _reflection.GeneratedProtocolMessageType('AddRequest', (_message.Message,), {'DESCRIPTOR': _ADDREQUEST,
 '__module__': 'eve.user.tag_pb2'})
_sym_db.RegisterMessage(AddRequest)
DESCRIPTOR._options = None
