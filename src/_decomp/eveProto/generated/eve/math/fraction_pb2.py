#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\math\fraction_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/math/fraction.proto', package='eve.math', syntax='proto3', serialized_options='Z3github.com/ccpgames/eve-proto-go/generated/eve/math', create_key=_descriptor._internal_create_key, serialized_pb='\n\x17eve/math/fraction.proto\x12\x08eve.math"2\n\x08Fraction\x12\x11\n\tnumerator\x18\x01 \x01(\x04\x12\x13\n\x0bdenominator\x18\x02 \x01(\x04B5Z3github.com/ccpgames/eve-proto-go/generated/eve/mathb\x06proto3')
_FRACTION = _descriptor.Descriptor(name='Fraction', full_name='eve.math.Fraction', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='numerator', full_name='eve.math.Fraction.numerator', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='denominator', full_name='eve.math.Fraction.denominator', index=1, number=2, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=37, serialized_end=87)
DESCRIPTOR.message_types_by_name['Fraction'] = _FRACTION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Fraction = _reflection.GeneratedProtocolMessageType('Fraction', (_message.Message,), {'DESCRIPTOR': _FRACTION,
 '__module__': 'eve.math.fraction_pb2'})
_sym_db.RegisterMessage(Fraction)
DESCRIPTOR._options = None
