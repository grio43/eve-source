#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\mail\status_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/mail/status.proto', package='eve.mail', syntax='proto3', serialized_options='Z3github.com/ccpgames/eve-proto-go/generated/eve/mail', create_key=_descriptor._internal_create_key, serialized_pb='\n\x15eve/mail/status.proto\x12\x08eve.mail*a\n\x06Status\x12\n\n\x06UNREAD\x10\x00\x12\x08\n\x04READ\x10\x01\x12\x0b\n\x07REPLIED\x10\x02\x12\r\n\tFORWARDED\x10\x04\x12\x0b\n\x07TRASHED\x10\x08\x12\t\n\x05DRAFT\x10\x10\x12\r\n\tAUTOMATED\x10 B5Z3github.com/ccpgames/eve-proto-go/generated/eve/mailb\x06proto3')
_STATUS = _descriptor.EnumDescriptor(name='Status', full_name='eve.mail.Status', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='UNREAD', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='READ', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='REPLIED', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='FORWARDED', index=3, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TRASHED', index=4, number=8, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DRAFT', index=5, number=16, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='AUTOMATED', index=6, number=32, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=35, serialized_end=132)
_sym_db.RegisterEnumDescriptor(_STATUS)
Status = enum_type_wrapper.EnumTypeWrapper(_STATUS)
UNREAD = 0
READ = 1
REPLIED = 2
FORWARDED = 4
TRASHED = 8
DRAFT = 16
AUTOMATED = 32
DESCRIPTOR.enum_types_by_name['Status'] = _STATUS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
DESCRIPTOR._options = None
