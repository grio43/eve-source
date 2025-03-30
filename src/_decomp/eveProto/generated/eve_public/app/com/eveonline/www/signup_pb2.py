#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\com\eveonline\www\signup_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.app.com import com_pb2 as eve__public_dot_app_dot_com_dot_com__pb2
from eveProto.generated.eve_public.user import user_pb2 as eve__public_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/com/eveonline/www/signup.proto', package='eve_public.app.com.eveonline.www.signup', syntax='proto3', serialized_options='ZRgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/com/eveonline/www/signup', create_key=_descriptor._internal_create_key, serialized_pb='\n-eve_public/app/com/eveonline/www/signup.proto\x12\'eve_public.app.com.eveonline.www.signup\x1a\x1ceve_public/app/com/com.proto\x1a\x1aeve_public/user/user.proto"i\n\x0eAccountCreated\x12,\n\x07context\x18\x01 \x01(\x0b2\x1b.eve_public.app.com.Context\x12)\n\x04user\x18\x02 \x01(\x0b2\x1b.eve_public.user.IdentifierBTZRgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/com/eveonline/www/signupb\x06proto3', dependencies=[eve__public_dot_app_dot_com_dot_com__pb2.DESCRIPTOR, eve__public_dot_user_dot_user__pb2.DESCRIPTOR])
_ACCOUNTCREATED = _descriptor.Descriptor(name='AccountCreated', full_name='eve_public.app.com.eveonline.www.signup.AccountCreated', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='context', full_name='eve_public.app.com.eveonline.www.signup.AccountCreated.context', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='user', full_name='eve_public.app.com.eveonline.www.signup.AccountCreated.user', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=148, serialized_end=253)
_ACCOUNTCREATED.fields_by_name['context'].message_type = eve__public_dot_app_dot_com_dot_com__pb2._CONTEXT
_ACCOUNTCREATED.fields_by_name['user'].message_type = eve__public_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['AccountCreated'] = _ACCOUNTCREATED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
AccountCreated = _reflection.GeneratedProtocolMessageType('AccountCreated', (_message.Message,), {'DESCRIPTOR': _ACCOUNTCREATED,
 '__module__': 'eve_public.app.com.eveonline.www.signup_pb2'})
_sym_db.RegisterMessage(AccountCreated)
DESCRIPTOR._options = None
