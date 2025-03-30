#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\eveonline\helperpointer\ui\link_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/eveonline/helperpointer/ui/link.proto', package='eve_public.app.eveonline.helperpointer.ui.link', syntax='proto3', serialized_options='ZYgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/helperpointer/ui/link', create_key=_descriptor._internal_create_key, serialized_pb='\n4eve_public/app/eveonline/helperpointer/ui/link.proto\x12.eve_public.app.eveonline.helperpointer.ui.link"C\n\x07Clicked\x12\x1b\n\x13pointer_unique_name\x18\x01 \x01(\t\x12\x17\n\x0fsource_location\x18\x02 \x01(\r:\x02\x18\x01"&\n\x07Created\x12\x1b\n\x13pointer_unique_name\x18\x01 \x01(\tB[ZYgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/helperpointer/ui/linkb\x06proto3')
_CLICKED = _descriptor.Descriptor(name='Clicked', full_name='eve_public.app.eveonline.helperpointer.ui.link.Clicked', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='pointer_unique_name', full_name='eve_public.app.eveonline.helperpointer.ui.link.Clicked.pointer_unique_name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='source_location', full_name='eve_public.app.eveonline.helperpointer.ui.link.Clicked.source_location', index=1, number=2, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=104, serialized_end=171)
_CREATED = _descriptor.Descriptor(name='Created', full_name='eve_public.app.eveonline.helperpointer.ui.link.Created', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='pointer_unique_name', full_name='eve_public.app.eveonline.helperpointer.ui.link.Created.pointer_unique_name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=173, serialized_end=211)
DESCRIPTOR.message_types_by_name['Clicked'] = _CLICKED
DESCRIPTOR.message_types_by_name['Created'] = _CREATED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Clicked = _reflection.GeneratedProtocolMessageType('Clicked', (_message.Message,), {'DESCRIPTOR': _CLICKED,
 '__module__': 'eve_public.app.eveonline.helperpointer.ui.link_pb2'})
_sym_db.RegisterMessage(Clicked)
Created = _reflection.GeneratedProtocolMessageType('Created', (_message.Message,), {'DESCRIPTOR': _CREATED,
 '__module__': 'eve_public.app.eveonline.helperpointer.ui.link_pb2'})
_sym_db.RegisterMessage(Created)
DESCRIPTOR._options = None
_CLICKED._options = None
