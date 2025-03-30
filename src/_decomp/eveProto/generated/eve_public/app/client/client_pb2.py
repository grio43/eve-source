#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\client\client_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.app.client.audio import audio_pb2 as eve__public_dot_app_dot_client_dot_audio_dot_audio__pb2
from eveProto.generated.eve_public.app.client.graphics import graphics_pb2 as eve__public_dot_app_dot_client_dot_graphics_dot_graphics__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/client/client.proto', package='eve_public.app.client', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve_public/app/client', create_key=_descriptor._internal_create_key, serialized_pb='\n"eve_public/app/client/client.proto\x12\x15eve_public.app.client\x1a\'eve_public/app/client/audio/audio.proto\x1a-eve_public/app/client/graphics/graphics.proto"\x8e\x01\n\x08Settings\x12C\n\x11graphics_settings\x18\x02 \x01(\x0b2(.eve_public.app.client.graphics.Settings\x12=\n\x0eaudio_settings\x18\x03 \x01(\x0b2%.eve_public.app.client.audio.SettingsBBZ@github.com/ccpgames/eve-proto-go/generated/eve_public/app/clientb\x06proto3', dependencies=[eve__public_dot_app_dot_client_dot_audio_dot_audio__pb2.DESCRIPTOR, eve__public_dot_app_dot_client_dot_graphics_dot_graphics__pb2.DESCRIPTOR])
_SETTINGS = _descriptor.Descriptor(name='Settings', full_name='eve_public.app.client.Settings', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='graphics_settings', full_name='eve_public.app.client.Settings.graphics_settings', index=0, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='audio_settings', full_name='eve_public.app.client.Settings.audio_settings', index=1, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=150, serialized_end=292)
_SETTINGS.fields_by_name['graphics_settings'].message_type = eve__public_dot_app_dot_client_dot_graphics_dot_graphics__pb2._SETTINGS
_SETTINGS.fields_by_name['audio_settings'].message_type = eve__public_dot_app_dot_client_dot_audio_dot_audio__pb2._SETTINGS
DESCRIPTOR.message_types_by_name['Settings'] = _SETTINGS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Settings = _reflection.GeneratedProtocolMessageType('Settings', (_message.Message,), {'DESCRIPTOR': _SETTINGS,
 '__module__': 'eve_public.app.client.client_pb2'})
_sym_db.RegisterMessage(Settings)
DESCRIPTOR._options = None
