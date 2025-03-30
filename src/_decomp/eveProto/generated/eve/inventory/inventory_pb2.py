#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\inventory\inventory_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/inventory/inventory.proto', package='eve.inventory', syntax='proto3', serialized_options='Z8github.com/ccpgames/eve-proto-go/generated/eve/inventory', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1deve/inventory/inventory.proto\x12\reve.inventory"$\n\x04Mass\x12\r\n\x05units\x18\x01 \x01(\x04\x12\r\n\x05nanos\x18\x02 \x01(\r"&\n\x06Volume\x12\r\n\x05units\x18\x01 \x01(\x04\x12\r\n\x05nanos\x18\x02 \x01(\r"\x1d\n\x0cLocationFlag\x12\r\n\x05value\x18\x01 \x01(\x04B:Z8github.com/ccpgames/eve-proto-go/generated/eve/inventoryb\x06proto3')
_MASS = _descriptor.Descriptor(name='Mass', full_name='eve.inventory.Mass', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='units', full_name='eve.inventory.Mass.units', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='nanos', full_name='eve.inventory.Mass.nanos', index=1, number=2, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=48, serialized_end=84)
_VOLUME = _descriptor.Descriptor(name='Volume', full_name='eve.inventory.Volume', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='units', full_name='eve.inventory.Volume.units', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='nanos', full_name='eve.inventory.Volume.nanos', index=1, number=2, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=86, serialized_end=124)
_LOCATIONFLAG = _descriptor.Descriptor(name='LocationFlag', full_name='eve.inventory.LocationFlag', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='value', full_name='eve.inventory.LocationFlag.value', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=126, serialized_end=155)
DESCRIPTOR.message_types_by_name['Mass'] = _MASS
DESCRIPTOR.message_types_by_name['Volume'] = _VOLUME
DESCRIPTOR.message_types_by_name['LocationFlag'] = _LOCATIONFLAG
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Mass = _reflection.GeneratedProtocolMessageType('Mass', (_message.Message,), {'DESCRIPTOR': _MASS,
 '__module__': 'eve.inventory.inventory_pb2'})
_sym_db.RegisterMessage(Mass)
Volume = _reflection.GeneratedProtocolMessageType('Volume', (_message.Message,), {'DESCRIPTOR': _VOLUME,
 '__module__': 'eve.inventory.inventory_pb2'})
_sym_db.RegisterMessage(Volume)
LocationFlag = _reflection.GeneratedProtocolMessageType('LocationFlag', (_message.Message,), {'DESCRIPTOR': _LOCATIONFLAG,
 '__module__': 'eve.inventory.inventory_pb2'})
_sym_db.RegisterMessage(LocationFlag)
DESCRIPTOR._options = None
