#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\eveonline\newscarousel\ui\ui_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/eveonline/newscarousel/ui/ui.proto', package='eve_public.app.eveonline.newscarousel.ui', syntax='proto3', serialized_options='ZSgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/newscarousel/ui', create_key=_descriptor._internal_create_key, serialized_pb='\n1eve_public/app/eveonline/newscarousel/ui/ui.proto\x12(eve_public.app.eveonline.newscarousel.ui"\x1c\n\x0cAcknowledged\x12\x0c\n\x04news\x18\x01 \x01(\r"\x19\n\tDisplayed\x12\x0c\n\x04news\x18\x01 \x01(\r"#\n\x10AutoPopupToggled\x12\x0f\n\x07checked\x18\x01 \x01(\x08BUZSgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/newscarousel/uib\x06proto3')
_ACKNOWLEDGED = _descriptor.Descriptor(name='Acknowledged', full_name='eve_public.app.eveonline.newscarousel.ui.Acknowledged', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='news', full_name='eve_public.app.eveonline.newscarousel.ui.Acknowledged.news', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=95, serialized_end=123)
_DISPLAYED = _descriptor.Descriptor(name='Displayed', full_name='eve_public.app.eveonline.newscarousel.ui.Displayed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='news', full_name='eve_public.app.eveonline.newscarousel.ui.Displayed.news', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=125, serialized_end=150)
_AUTOPOPUPTOGGLED = _descriptor.Descriptor(name='AutoPopupToggled', full_name='eve_public.app.eveonline.newscarousel.ui.AutoPopupToggled', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='checked', full_name='eve_public.app.eveonline.newscarousel.ui.AutoPopupToggled.checked', index=0, number=1, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=152, serialized_end=187)
DESCRIPTOR.message_types_by_name['Acknowledged'] = _ACKNOWLEDGED
DESCRIPTOR.message_types_by_name['Displayed'] = _DISPLAYED
DESCRIPTOR.message_types_by_name['AutoPopupToggled'] = _AUTOPOPUPTOGGLED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Acknowledged = _reflection.GeneratedProtocolMessageType('Acknowledged', (_message.Message,), {'DESCRIPTOR': _ACKNOWLEDGED,
 '__module__': 'eve_public.app.eveonline.newscarousel.ui.ui_pb2'})
_sym_db.RegisterMessage(Acknowledged)
Displayed = _reflection.GeneratedProtocolMessageType('Displayed', (_message.Message,), {'DESCRIPTOR': _DISPLAYED,
 '__module__': 'eve_public.app.eveonline.newscarousel.ui.ui_pb2'})
_sym_db.RegisterMessage(Displayed)
AutoPopupToggled = _reflection.GeneratedProtocolMessageType('AutoPopupToggled', (_message.Message,), {'DESCRIPTOR': _AUTOPOPUPTOGGLED,
 '__module__': 'eve_public.app.eveonline.newscarousel.ui.ui_pb2'})
_sym_db.RegisterMessage(AutoPopupToggled)
DESCRIPTOR._options = None
