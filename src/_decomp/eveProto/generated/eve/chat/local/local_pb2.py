#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\chat\local\local_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/chat/local/local.proto', package='eve.chat.local', syntax='proto3', serialized_options='Z9github.com/ccpgames/eve-proto-go/generated/eve/chat/local', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1aeve/chat/local/local.proto\x12\x0eeve.chat.local*B\n\x04Mode\x12\x14\n\x10MODE_UNSPECIFIED\x10\x00\x12\x12\n\x0eMODE_IMMEDIATE\x10\x01\x12\x10\n\x0cMODE_DELAYED\x10\x02*\xe3\x01\n\x0eClassification\x12\x1e\n\x1aCLASSIFICATION_UNSPECIFIED\x10\x00\x12\x1c\n\x18CLASSIFICATION_INVISIBLE\x10\x01\x12\x1c\n\x18CLASSIFICATION_DEVELOPER\x10\x02\x12 \n\x1cCLASSIFICATION_ADMINISTRATOR\x10\x03\x12\x1d\n\x19CLASSIFICATION_GAMEMASTER\x10\x04\x12\x1c\n\x18CLASSIFICATION_VOLUNTEER\x10\x05\x12\x16\n\x12CLASSIFICATION_NPC\x10\x06B;Z9github.com/ccpgames/eve-proto-go/generated/eve/chat/localb\x06proto3')
_MODE = _descriptor.EnumDescriptor(name='Mode', full_name='eve.chat.local.Mode', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='MODE_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='MODE_IMMEDIATE', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='MODE_DELAYED', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=46, serialized_end=112)
_sym_db.RegisterEnumDescriptor(_MODE)
Mode = enum_type_wrapper.EnumTypeWrapper(_MODE)
_CLASSIFICATION = _descriptor.EnumDescriptor(name='Classification', full_name='eve.chat.local.Classification', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='CLASSIFICATION_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CLASSIFICATION_INVISIBLE', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CLASSIFICATION_DEVELOPER', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CLASSIFICATION_ADMINISTRATOR', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CLASSIFICATION_GAMEMASTER', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CLASSIFICATION_VOLUNTEER', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CLASSIFICATION_NPC', index=6, number=6, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=115, serialized_end=342)
_sym_db.RegisterEnumDescriptor(_CLASSIFICATION)
Classification = enum_type_wrapper.EnumTypeWrapper(_CLASSIFICATION)
MODE_UNSPECIFIED = 0
MODE_IMMEDIATE = 1
MODE_DELAYED = 2
CLASSIFICATION_UNSPECIFIED = 0
CLASSIFICATION_INVISIBLE = 1
CLASSIFICATION_DEVELOPER = 2
CLASSIFICATION_ADMINISTRATOR = 3
CLASSIFICATION_GAMEMASTER = 4
CLASSIFICATION_VOLUNTEER = 5
CLASSIFICATION_NPC = 6
DESCRIPTOR.enum_types_by_name['Mode'] = _MODE
DESCRIPTOR.enum_types_by_name['Classification'] = _CLASSIFICATION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
DESCRIPTOR._options = None
