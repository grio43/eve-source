#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\sovereignty\versionmanifest_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve import semanticversion_pb2 as eve_dot_semanticversion__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/sovereignty/versionmanifest.proto', package='eve.sovereignty', syntax='proto3', serialized_options='ZJgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/versionmanifest', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve/sovereignty/versionmanifest.proto\x12\x0feve.sovereignty\x1a\x19eve/semanticversion.proto"\xbb\x02\n\x0fVersionManifest\x12<\n\x10planet_resources\x18\x01 \x01(\x0b2".eve.semanticversion.Specification\x12D\n\x18mercenary_den_activities\x18\x02 \x01(\x0b2".eve.semanticversion.Specification\x122\n\x06skills\x18\x03 \x01(\x0b2".eve.semanticversion.Specification\x12:\n\x0estar_resources\x18\x04 \x01(\x0b2".eve.semanticversion.Specification\x124\n\x08upgrades\x18\x05 \x01(\x0b2".eve.semanticversion.SpecificationBLZJgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/versionmanifestb\x06proto3', dependencies=[eve_dot_semanticversion__pb2.DESCRIPTOR])
_VERSIONMANIFEST = _descriptor.Descriptor(name='VersionManifest', full_name='eve.sovereignty.VersionManifest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='planet_resources', full_name='eve.sovereignty.VersionManifest.planet_resources', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='mercenary_den_activities', full_name='eve.sovereignty.VersionManifest.mercenary_den_activities', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='skills', full_name='eve.sovereignty.VersionManifest.skills', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='star_resources', full_name='eve.sovereignty.VersionManifest.star_resources', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='upgrades', full_name='eve.sovereignty.VersionManifest.upgrades', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=86, serialized_end=401)
_VERSIONMANIFEST.fields_by_name['planet_resources'].message_type = eve_dot_semanticversion__pb2._SPECIFICATION
_VERSIONMANIFEST.fields_by_name['mercenary_den_activities'].message_type = eve_dot_semanticversion__pb2._SPECIFICATION
_VERSIONMANIFEST.fields_by_name['skills'].message_type = eve_dot_semanticversion__pb2._SPECIFICATION
_VERSIONMANIFEST.fields_by_name['star_resources'].message_type = eve_dot_semanticversion__pb2._SPECIFICATION
_VERSIONMANIFEST.fields_by_name['upgrades'].message_type = eve_dot_semanticversion__pb2._SPECIFICATION
DESCRIPTOR.message_types_by_name['VersionManifest'] = _VERSIONMANIFEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
VersionManifest = _reflection.GeneratedProtocolMessageType('VersionManifest', (_message.Message,), {'DESCRIPTOR': _VERSIONMANIFEST,
 '__module__': 'eve.sovereignty.versionmanifest_pb2'})
_sym_db.RegisterMessage(VersionManifest)
DESCRIPTOR._options = None
