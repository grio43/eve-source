#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\client\audio\audio_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/client/audio/audio.proto', package='eve_public.app.client.audio', syntax='proto3', serialized_options='ZFgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/client/audio', create_key=_descriptor._internal_create_key, serialized_pb='\n\'eve_public/app/client/audio/audio.proto\x12\x1beve_public.app.client.audio"$\n\x08Settings\x12\x18\n\x10is_audio_enabled\x18\x01 \x01(\x08BHZFgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/client/audiob\x06proto3')
_SETTINGS = _descriptor.Descriptor(name='Settings', full_name='eve_public.app.client.audio.Settings', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='is_audio_enabled', full_name='eve_public.app.client.audio.Settings.is_audio_enabled', index=0, number=1, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=72, serialized_end=108)
DESCRIPTOR.message_types_by_name['Settings'] = _SETTINGS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Settings = _reflection.GeneratedProtocolMessageType('Settings', (_message.Message,), {'DESCRIPTOR': _SETTINGS,
 '__module__': 'eve_public.app.client.audio.audio_pb2'})
_sym_db.RegisterMessage(Settings)
DESCRIPTOR._options = None
