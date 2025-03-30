#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\inventory\container\secure\auditlog_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.inventory.container import container_pb2 as eve_dot_inventory_dot_container_dot_container__pb2
from eveProto.generated.eve.inventory.container.secure import secure_pb2 as eve_dot_inventory_dot_container_dot_secure_dot_secure__pb2
from eveProto.generated.eve.inventory.container import type_pb2 as eve_dot_inventory_dot_container_dot_type__pb2
from eveProto.generated.eve.inventory import generic_item_pb2 as eve_dot_inventory_dot_generic__item__pb2
from eveProto.generated.eve.inventory import generic_item_type_pb2 as eve_dot_inventory_dot_generic__item__type__pb2
from eveProto.generated.eve.owner import generic_pb2 as eve_dot_owner_dot_generic__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/inventory/container/secure/auditlog.proto', package='eve.inventory.container.secure.auditlog', syntax='proto3', serialized_options='ZRgithub.com/ccpgames/eve-proto-go/generated/eve/inventory/container/secure/auditlog', create_key=_descriptor._internal_create_key, serialized_pb='\n-eve/inventory/container/secure/auditlog.proto\x12\'eve.inventory.container.secure.auditlog\x1a\x1deve/character/character.proto\x1a\'eve/inventory/container/container.proto\x1a+eve/inventory/container/secure/secure.proto\x1a"eve/inventory/container/type.proto\x1a eve/inventory/generic_item.proto\x1a%eve/inventory/generic_item_type.proto\x1a\x17eve/owner/generic.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\x91\x0b\n\x06Action\x12L\n\x08assemble\x18\x01 \x01(\x0b28.eve.inventory.container.secure.auditlog.Action.AssembleH\x00\x12N\n\trepackage\x18\x02 \x01(\x0b29.eve.inventory.container.secure.auditlog.Action.RepackageH\x00\x12K\n\x08set_name\x18\x03 \x01(\x0b27.eve.inventory.container.secure.auditlog.Action.SetNameH\x00\x12D\n\x04move\x18\x04 \x01(\x0b24.eve.inventory.container.secure.auditlog.Action.MoveH\x00\x12S\n\x0cset_password\x18\x05 \x01(\x0b2;.eve.inventory.container.secure.auditlog.Action.SetPasswordH\x00\x12B\n\x03add\x18\x06 \x01(\x0b23.eve.inventory.container.secure.auditlog.Action.AddH\x00\x12D\n\x04lock\x18\x07 \x01(\x0b24.eve.inventory.container.secure.auditlog.Action.LockH\x00\x12H\n\x06unlock\x18\x08 \x01(\x0b26.eve.inventory.container.secure.auditlog.Action.UnlockH\x00\x12W\n\x0eenter_password\x18\t \x01(\x0b2=.eve.inventory.container.secure.auditlog.Action.EnterPasswordH\x00\x12N\n\tconfigure\x18\n \x01(\x0b29.eve.inventory.container.secure.auditlog.Action.ConfigureH\x00\x1aq\n\x08Assemble\x12,\n\x05owner\x18\x01 \x01(\x0b2\x1d.eve.owner.generic.Identifier\x127\n\x04type\x18\x02 \x01(\x0b2).eve.inventory.genericitemtype.Identifier\x1a\x0b\n\tRepackage\x1a\t\n\x07SetName\x1a\x06\n\x04Move\x1aR\n\x0bSetPassword\x12C\n\rpassword_type\x18\x01 \x01(\x0e2,.eve.inventory.container.secure.PasswordType\x1aP\n\x03Add\x127\n\x04type\x18\x01 \x01(\x0b2).eve.inventory.genericitemtype.Identifier\x12\x10\n\x08quantity\x18\x02 \x01(\x04\x1aQ\n\x04Lock\x127\n\x04type\x18\x01 \x01(\x0b2).eve.inventory.genericitemtype.Identifier\x12\x10\n\x08quantity\x18\x02 \x01(\x04\x1aS\n\x06Unlock\x127\n\x04type\x18\x01 \x01(\x0b2).eve.inventory.genericitemtype.Identifier\x12\x10\n\x08quantity\x18\x02 \x01(\x04\x1aT\n\rEnterPassword\x12C\n\rpassword_type\x18\x01 \x01(\x0e2,.eve.inventory.container.secure.PasswordType\x1aC\n\tConfigure\x12\x1a\n\x12old_config_bitmask\x18\x01 \x01(\x04\x12\x1a\n\x12new_config_bitmask\x18\x02 \x01(\x04B\x08\n\x06action"\x83\x03\n\x05Entry\x12-\n\ttimestamp\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x126\n\tcontainer\x18\x02 \x01(\x0b2#.eve.inventory.container.Identifier\x12@\n\x0econtainer_type\x18\x03 \x01(\x0b2(.eve.inventory.container.type.Identifier\x12A\n\x12container_location\x18\x04 \x01(\x0b2%.eve.inventory.genericitem.Identifier\x12\x1f\n\x17container_location_flag\x18\x05 \x01(\r\x12?\n\x06action\x18\x06 \x01(\x0b2/.eve.inventory.container.secure.auditlog.Action\x12,\n\tcharacter\x18\x07 \x01(\x0b2\x19.eve.character.IdentifierBTZRgithub.com/ccpgames/eve-proto-go/generated/eve/inventory/container/secure/auditlogb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_inventory_dot_container_dot_container__pb2.DESCRIPTOR,
 eve_dot_inventory_dot_container_dot_secure_dot_secure__pb2.DESCRIPTOR,
 eve_dot_inventory_dot_container_dot_type__pb2.DESCRIPTOR,
 eve_dot_inventory_dot_generic__item__pb2.DESCRIPTOR,
 eve_dot_inventory_dot_generic__item__type__pb2.DESCRIPTOR,
 eve_dot_owner_dot_generic__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_ACTION_ASSEMBLE = _descriptor.Descriptor(name='Assemble', full_name='eve.inventory.container.secure.auditlog.Action.Assemble', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='owner', full_name='eve.inventory.container.secure.auditlog.Action.Assemble.owner', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='type', full_name='eve.inventory.container.secure.auditlog.Action.Assemble.type', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1156, serialized_end=1269)
_ACTION_REPACKAGE = _descriptor.Descriptor(name='Repackage', full_name='eve.inventory.container.secure.auditlog.Action.Repackage', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1271, serialized_end=1282)
_ACTION_SETNAME = _descriptor.Descriptor(name='SetName', full_name='eve.inventory.container.secure.auditlog.Action.SetName', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1284, serialized_end=1293)
_ACTION_MOVE = _descriptor.Descriptor(name='Move', full_name='eve.inventory.container.secure.auditlog.Action.Move', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1295, serialized_end=1301)
_ACTION_SETPASSWORD = _descriptor.Descriptor(name='SetPassword', full_name='eve.inventory.container.secure.auditlog.Action.SetPassword', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='password_type', full_name='eve.inventory.container.secure.auditlog.Action.SetPassword.password_type', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1303, serialized_end=1385)
_ACTION_ADD = _descriptor.Descriptor(name='Add', full_name='eve.inventory.container.secure.auditlog.Action.Add', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='type', full_name='eve.inventory.container.secure.auditlog.Action.Add.type', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='quantity', full_name='eve.inventory.container.secure.auditlog.Action.Add.quantity', index=1, number=2, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1387, serialized_end=1467)
_ACTION_LOCK = _descriptor.Descriptor(name='Lock', full_name='eve.inventory.container.secure.auditlog.Action.Lock', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='type', full_name='eve.inventory.container.secure.auditlog.Action.Lock.type', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='quantity', full_name='eve.inventory.container.secure.auditlog.Action.Lock.quantity', index=1, number=2, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1469, serialized_end=1550)
_ACTION_UNLOCK = _descriptor.Descriptor(name='Unlock', full_name='eve.inventory.container.secure.auditlog.Action.Unlock', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='type', full_name='eve.inventory.container.secure.auditlog.Action.Unlock.type', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='quantity', full_name='eve.inventory.container.secure.auditlog.Action.Unlock.quantity', index=1, number=2, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1552, serialized_end=1635)
_ACTION_ENTERPASSWORD = _descriptor.Descriptor(name='EnterPassword', full_name='eve.inventory.container.secure.auditlog.Action.EnterPassword', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='password_type', full_name='eve.inventory.container.secure.auditlog.Action.EnterPassword.password_type', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1637, serialized_end=1721)
_ACTION_CONFIGURE = _descriptor.Descriptor(name='Configure', full_name='eve.inventory.container.secure.auditlog.Action.Configure', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='old_config_bitmask', full_name='eve.inventory.container.secure.auditlog.Action.Configure.old_config_bitmask', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='new_config_bitmask', full_name='eve.inventory.container.secure.auditlog.Action.Configure.new_config_bitmask', index=1, number=2, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1723, serialized_end=1790)
_ACTION = _descriptor.Descriptor(name='Action', full_name='eve.inventory.container.secure.auditlog.Action', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='assemble', full_name='eve.inventory.container.secure.auditlog.Action.assemble', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='repackage', full_name='eve.inventory.container.secure.auditlog.Action.repackage', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='set_name', full_name='eve.inventory.container.secure.auditlog.Action.set_name', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='move', full_name='eve.inventory.container.secure.auditlog.Action.move', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='set_password', full_name='eve.inventory.container.secure.auditlog.Action.set_password', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='add', full_name='eve.inventory.container.secure.auditlog.Action.add', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='lock', full_name='eve.inventory.container.secure.auditlog.Action.lock', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unlock', full_name='eve.inventory.container.secure.auditlog.Action.unlock', index=7, number=8, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='enter_password', full_name='eve.inventory.container.secure.auditlog.Action.enter_password', index=8, number=9, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='configure', full_name='eve.inventory.container.secure.auditlog.Action.configure', index=9, number=10, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_ACTION_ASSEMBLE,
 _ACTION_REPACKAGE,
 _ACTION_SETNAME,
 _ACTION_MOVE,
 _ACTION_SETPASSWORD,
 _ACTION_ADD,
 _ACTION_LOCK,
 _ACTION_UNLOCK,
 _ACTION_ENTERPASSWORD,
 _ACTION_CONFIGURE], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='action', full_name='eve.inventory.container.secure.auditlog.Action.action', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=375, serialized_end=1800)
_ENTRY = _descriptor.Descriptor(name='Entry', full_name='eve.inventory.container.secure.auditlog.Entry', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='timestamp', full_name='eve.inventory.container.secure.auditlog.Entry.timestamp', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='container', full_name='eve.inventory.container.secure.auditlog.Entry.container', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='container_type', full_name='eve.inventory.container.secure.auditlog.Entry.container_type', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='container_location', full_name='eve.inventory.container.secure.auditlog.Entry.container_location', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='container_location_flag', full_name='eve.inventory.container.secure.auditlog.Entry.container_location_flag', index=4, number=5, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='action', full_name='eve.inventory.container.secure.auditlog.Entry.action', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='character', full_name='eve.inventory.container.secure.auditlog.Entry.character', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1803, serialized_end=2190)
_ACTION_ASSEMBLE.fields_by_name['owner'].message_type = eve_dot_owner_dot_generic__pb2._IDENTIFIER
_ACTION_ASSEMBLE.fields_by_name['type'].message_type = eve_dot_inventory_dot_generic__item__type__pb2._IDENTIFIER
_ACTION_ASSEMBLE.containing_type = _ACTION
_ACTION_REPACKAGE.containing_type = _ACTION
_ACTION_SETNAME.containing_type = _ACTION
_ACTION_MOVE.containing_type = _ACTION
_ACTION_SETPASSWORD.fields_by_name['password_type'].enum_type = eve_dot_inventory_dot_container_dot_secure_dot_secure__pb2._PASSWORDTYPE
_ACTION_SETPASSWORD.containing_type = _ACTION
_ACTION_ADD.fields_by_name['type'].message_type = eve_dot_inventory_dot_generic__item__type__pb2._IDENTIFIER
_ACTION_ADD.containing_type = _ACTION
_ACTION_LOCK.fields_by_name['type'].message_type = eve_dot_inventory_dot_generic__item__type__pb2._IDENTIFIER
_ACTION_LOCK.containing_type = _ACTION
_ACTION_UNLOCK.fields_by_name['type'].message_type = eve_dot_inventory_dot_generic__item__type__pb2._IDENTIFIER
_ACTION_UNLOCK.containing_type = _ACTION
_ACTION_ENTERPASSWORD.fields_by_name['password_type'].enum_type = eve_dot_inventory_dot_container_dot_secure_dot_secure__pb2._PASSWORDTYPE
_ACTION_ENTERPASSWORD.containing_type = _ACTION
_ACTION_CONFIGURE.containing_type = _ACTION
_ACTION.fields_by_name['assemble'].message_type = _ACTION_ASSEMBLE
_ACTION.fields_by_name['repackage'].message_type = _ACTION_REPACKAGE
_ACTION.fields_by_name['set_name'].message_type = _ACTION_SETNAME
_ACTION.fields_by_name['move'].message_type = _ACTION_MOVE
_ACTION.fields_by_name['set_password'].message_type = _ACTION_SETPASSWORD
_ACTION.fields_by_name['add'].message_type = _ACTION_ADD
_ACTION.fields_by_name['lock'].message_type = _ACTION_LOCK
_ACTION.fields_by_name['unlock'].message_type = _ACTION_UNLOCK
_ACTION.fields_by_name['enter_password'].message_type = _ACTION_ENTERPASSWORD
_ACTION.fields_by_name['configure'].message_type = _ACTION_CONFIGURE
_ACTION.oneofs_by_name['action'].fields.append(_ACTION.fields_by_name['assemble'])
_ACTION.fields_by_name['assemble'].containing_oneof = _ACTION.oneofs_by_name['action']
_ACTION.oneofs_by_name['action'].fields.append(_ACTION.fields_by_name['repackage'])
_ACTION.fields_by_name['repackage'].containing_oneof = _ACTION.oneofs_by_name['action']
_ACTION.oneofs_by_name['action'].fields.append(_ACTION.fields_by_name['set_name'])
_ACTION.fields_by_name['set_name'].containing_oneof = _ACTION.oneofs_by_name['action']
_ACTION.oneofs_by_name['action'].fields.append(_ACTION.fields_by_name['move'])
_ACTION.fields_by_name['move'].containing_oneof = _ACTION.oneofs_by_name['action']
_ACTION.oneofs_by_name['action'].fields.append(_ACTION.fields_by_name['set_password'])
_ACTION.fields_by_name['set_password'].containing_oneof = _ACTION.oneofs_by_name['action']
_ACTION.oneofs_by_name['action'].fields.append(_ACTION.fields_by_name['add'])
_ACTION.fields_by_name['add'].containing_oneof = _ACTION.oneofs_by_name['action']
_ACTION.oneofs_by_name['action'].fields.append(_ACTION.fields_by_name['lock'])
_ACTION.fields_by_name['lock'].containing_oneof = _ACTION.oneofs_by_name['action']
_ACTION.oneofs_by_name['action'].fields.append(_ACTION.fields_by_name['unlock'])
_ACTION.fields_by_name['unlock'].containing_oneof = _ACTION.oneofs_by_name['action']
_ACTION.oneofs_by_name['action'].fields.append(_ACTION.fields_by_name['enter_password'])
_ACTION.fields_by_name['enter_password'].containing_oneof = _ACTION.oneofs_by_name['action']
_ACTION.oneofs_by_name['action'].fields.append(_ACTION.fields_by_name['configure'])
_ACTION.fields_by_name['configure'].containing_oneof = _ACTION.oneofs_by_name['action']
_ENTRY.fields_by_name['timestamp'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ENTRY.fields_by_name['container'].message_type = eve_dot_inventory_dot_container_dot_container__pb2._IDENTIFIER
_ENTRY.fields_by_name['container_type'].message_type = eve_dot_inventory_dot_container_dot_type__pb2._IDENTIFIER
_ENTRY.fields_by_name['container_location'].message_type = eve_dot_inventory_dot_generic__item__pb2._IDENTIFIER
_ENTRY.fields_by_name['action'].message_type = _ACTION
_ENTRY.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Action'] = _ACTION
DESCRIPTOR.message_types_by_name['Entry'] = _ENTRY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Action = _reflection.GeneratedProtocolMessageType('Action', (_message.Message,), {'Assemble': _reflection.GeneratedProtocolMessageType('Assemble', (_message.Message,), {'DESCRIPTOR': _ACTION_ASSEMBLE,
              '__module__': 'eve.inventory.container.secure.auditlog_pb2'}),
 'Repackage': _reflection.GeneratedProtocolMessageType('Repackage', (_message.Message,), {'DESCRIPTOR': _ACTION_REPACKAGE,
               '__module__': 'eve.inventory.container.secure.auditlog_pb2'}),
 'SetName': _reflection.GeneratedProtocolMessageType('SetName', (_message.Message,), {'DESCRIPTOR': _ACTION_SETNAME,
             '__module__': 'eve.inventory.container.secure.auditlog_pb2'}),
 'Move': _reflection.GeneratedProtocolMessageType('Move', (_message.Message,), {'DESCRIPTOR': _ACTION_MOVE,
          '__module__': 'eve.inventory.container.secure.auditlog_pb2'}),
 'SetPassword': _reflection.GeneratedProtocolMessageType('SetPassword', (_message.Message,), {'DESCRIPTOR': _ACTION_SETPASSWORD,
                 '__module__': 'eve.inventory.container.secure.auditlog_pb2'}),
 'Add': _reflection.GeneratedProtocolMessageType('Add', (_message.Message,), {'DESCRIPTOR': _ACTION_ADD,
         '__module__': 'eve.inventory.container.secure.auditlog_pb2'}),
 'Lock': _reflection.GeneratedProtocolMessageType('Lock', (_message.Message,), {'DESCRIPTOR': _ACTION_LOCK,
          '__module__': 'eve.inventory.container.secure.auditlog_pb2'}),
 'Unlock': _reflection.GeneratedProtocolMessageType('Unlock', (_message.Message,), {'DESCRIPTOR': _ACTION_UNLOCK,
            '__module__': 'eve.inventory.container.secure.auditlog_pb2'}),
 'EnterPassword': _reflection.GeneratedProtocolMessageType('EnterPassword', (_message.Message,), {'DESCRIPTOR': _ACTION_ENTERPASSWORD,
                   '__module__': 'eve.inventory.container.secure.auditlog_pb2'}),
 'Configure': _reflection.GeneratedProtocolMessageType('Configure', (_message.Message,), {'DESCRIPTOR': _ACTION_CONFIGURE,
               '__module__': 'eve.inventory.container.secure.auditlog_pb2'}),
 'DESCRIPTOR': _ACTION,
 '__module__': 'eve.inventory.container.secure.auditlog_pb2'})
_sym_db.RegisterMessage(Action)
_sym_db.RegisterMessage(Action.Assemble)
_sym_db.RegisterMessage(Action.Repackage)
_sym_db.RegisterMessage(Action.SetName)
_sym_db.RegisterMessage(Action.Move)
_sym_db.RegisterMessage(Action.SetPassword)
_sym_db.RegisterMessage(Action.Add)
_sym_db.RegisterMessage(Action.Lock)
_sym_db.RegisterMessage(Action.Unlock)
_sym_db.RegisterMessage(Action.EnterPassword)
_sym_db.RegisterMessage(Action.Configure)
Entry = _reflection.GeneratedProtocolMessageType('Entry', (_message.Message,), {'DESCRIPTOR': _ENTRY,
 '__module__': 'eve.inventory.container.secure.auditlog_pb2'})
_sym_db.RegisterMessage(Entry)
DESCRIPTOR._options = None
