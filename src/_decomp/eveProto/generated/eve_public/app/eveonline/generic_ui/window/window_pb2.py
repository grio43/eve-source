#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\eveonline\generic_ui\window\window_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/eveonline/generic_ui/window/window.proto', package='eve_public.app.eveonline.generic_ui.window', syntax='proto3', serialized_options='ZUgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/generic_ui/window', create_key=_descriptor._internal_create_key, serialized_pb='\n7eve_public/app/eveonline/generic_ui/window/window.proto\x12*eve_public.app.eveonline.generic_ui.window"!\n\nIdentifier\x12\x13\n\x0bunique_name\x18\x01 \x01(\t*\x8d\x01\n\x0bDockingMode\x12\x1b\n\x17DOCKINGMODE_UNSPECIFIED\x10\x00\x12\x18\n\x14DOCKINGMODE_FLOATING\x10\x01\x12\x1a\n\x16DOCKINGMODE_FULLSCREEN\x10\x02\x12\x14\n\x10DOCKINGMODE_LEFT\x10\x03\x12\x15\n\x11DOCKINGMODE_RIGHT\x10\x04BWZUgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/generic_ui/windowb\x06proto3')
_DOCKINGMODE = _descriptor.EnumDescriptor(name='DockingMode', full_name='eve_public.app.eveonline.generic_ui.window.DockingMode', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='DOCKINGMODE_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DOCKINGMODE_FLOATING', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DOCKINGMODE_FULLSCREEN', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DOCKINGMODE_LEFT', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DOCKINGMODE_RIGHT', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=139, serialized_end=280)
_sym_db.RegisterEnumDescriptor(_DOCKINGMODE)
DockingMode = enum_type_wrapper.EnumTypeWrapper(_DOCKINGMODE)
DOCKINGMODE_UNSPECIFIED = 0
DOCKINGMODE_FLOATING = 1
DOCKINGMODE_FULLSCREEN = 2
DOCKINGMODE_LEFT = 3
DOCKINGMODE_RIGHT = 4
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve_public.app.eveonline.generic_ui.window.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='unique_name', full_name='eve_public.app.eveonline.generic_ui.window.Identifier.unique_name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=103, serialized_end=136)
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.enum_types_by_name['DockingMode'] = _DOCKINGMODE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve_public.app.eveonline.generic_ui.window.window_pb2'})
_sym_db.RegisterMessage(Identifier)
DESCRIPTOR._options = None
