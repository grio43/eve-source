#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\eveonline\agency\ui\help\video\link_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/eveonline/agency/ui/help/video/link.proto', package='eve_public.app.eveonline.agency.ui.help.video.link', syntax='proto3', serialized_options='Z]github.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/agency/ui/help/video/link', create_key=_descriptor._internal_create_key, serialized_pb='\n8eve_public/app/eveonline/agency/ui/help/video/link.proto\x122eve_public.app.eveonline.agency.ui.help.video.link"\x1d\n\x07Created\x12\x12\n\nvideo_path\x18\x01 \x01(\t"\x1d\n\x07Clicked\x12\x12\n\nvideo_path\x18\x01 \x01(\tB_Z]github.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/agency/ui/help/video/linkb\x06proto3')
_CREATED = _descriptor.Descriptor(name='Created', full_name='eve_public.app.eveonline.agency.ui.help.video.link.Created', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='video_path', full_name='eve_public.app.eveonline.agency.ui.help.video.link.Created.video_path', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=112, serialized_end=141)
_CLICKED = _descriptor.Descriptor(name='Clicked', full_name='eve_public.app.eveonline.agency.ui.help.video.link.Clicked', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='video_path', full_name='eve_public.app.eveonline.agency.ui.help.video.link.Clicked.video_path', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=143, serialized_end=172)
DESCRIPTOR.message_types_by_name['Created'] = _CREATED
DESCRIPTOR.message_types_by_name['Clicked'] = _CLICKED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Created = _reflection.GeneratedProtocolMessageType('Created', (_message.Message,), {'DESCRIPTOR': _CREATED,
 '__module__': 'eve_public.app.eveonline.agency.ui.help.video.link_pb2'})
_sym_db.RegisterMessage(Created)
Clicked = _reflection.GeneratedProtocolMessageType('Clicked', (_message.Message,), {'DESCRIPTOR': _CLICKED,
 '__module__': 'eve_public.app.eveonline.agency.ui.help.video.link_pb2'})
_sym_db.RegisterMessage(Clicked)
DESCRIPTOR._options = None
