#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\internal\type_checkers.py
__author__ = 'robinson@google.com (Will Robinson)'
try:
    import ctypes
except Exception:
    ctypes = None
    import struct

import numbers
import six
if six.PY3:
    long = int
from google.protobuf.internal import api_implementation
from google.protobuf.internal import decoder
from google.protobuf.internal import encoder
from google.protobuf.internal import wire_format
from google.protobuf import descriptor
_FieldDescriptor = descriptor.FieldDescriptor

def TruncateToFourByteFloat(original):
    if ctypes:
        return ctypes.c_float(original).value
    else:
        return struct.unpack('<f', struct.pack('<f', original))[0]


def ToShortestFloat(original):
    precision = 6
    rounded = float('{0:.{1}g}'.format(original, precision))
    while TruncateToFourByteFloat(rounded) != original:
        precision += 1
        rounded = float('{0:.{1}g}'.format(original, precision))

    return rounded


def SupportsOpenEnums(field_descriptor):
    return field_descriptor.containing_type.syntax == 'proto3'


def GetTypeChecker(field):
    if field.cpp_type == _FieldDescriptor.CPPTYPE_STRING and field.type == _FieldDescriptor.TYPE_STRING:
        return UnicodeValueChecker()
    if field.cpp_type == _FieldDescriptor.CPPTYPE_ENUM:
        if SupportsOpenEnums(field):
            return _VALUE_CHECKERS[_FieldDescriptor.CPPTYPE_INT32]
        else:
            return EnumValueChecker(field.enum_type)
    return _VALUE_CHECKERS[field.cpp_type]


class TypeChecker(object):

    def __init__(self, *acceptable_types):
        self._acceptable_types = acceptable_types

    def CheckValue(self, proposed_value):
        if not isinstance(proposed_value, self._acceptable_types):
            message = '%.1024r has type %s, but expected one of: %s' % (proposed_value, type(proposed_value), self._acceptable_types)
            raise TypeError(message)
        if self._acceptable_types:
            if self._acceptable_types[0] in (bool, float):
                return self._acceptable_types[0](proposed_value)
        return proposed_value


class TypeCheckerWithDefault(TypeChecker):

    def __init__(self, default_value, *acceptable_types):
        TypeChecker.__init__(self, *acceptable_types)
        self._default_value = default_value

    def DefaultValue(self):
        return self._default_value


class IntValueChecker(object):

    def CheckValue(self, proposed_value):
        if not isinstance(proposed_value, numbers.Integral):
            message = '%.1024r has type %s, but expected one of: %s' % (proposed_value, type(proposed_value), six.integer_types)
            raise TypeError(message)
        if not self._MIN <= int(proposed_value) <= self._MAX:
            raise ValueError('Value out of range: %d' % proposed_value)
        proposed_value = self._TYPE(proposed_value)
        return proposed_value

    def DefaultValue(self):
        return 0


class EnumValueChecker(object):

    def __init__(self, enum_type):
        self._enum_type = enum_type

    def CheckValue(self, proposed_value):
        if not isinstance(proposed_value, numbers.Integral):
            message = '%.1024r has type %s, but expected one of: %s' % (proposed_value, type(proposed_value), six.integer_types)
            raise TypeError(message)
        if int(proposed_value) not in self._enum_type.values_by_number:
            raise ValueError('Unknown enum value: %d' % proposed_value)
        return proposed_value

    def DefaultValue(self):
        return self._enum_type.values[0].number


class UnicodeValueChecker(object):

    def CheckValue(self, proposed_value):
        if not isinstance(proposed_value, (bytes, six.text_type)):
            message = '%.1024r has type %s, but expected one of: %s' % (proposed_value, type(proposed_value), (bytes, six.text_type))
            raise TypeError(message)
        if isinstance(proposed_value, bytes):
            try:
                proposed_value = proposed_value.decode('utf-8')
            except UnicodeDecodeError:
                raise ValueError("%.1024r has type bytes, but isn't valid UTF-8 encoding. Non-UTF-8 strings must be converted to unicode objects before being added." % proposed_value)

        else:
            try:
                proposed_value.encode('utf8')
            except UnicodeEncodeError:
                raise ValueError("%.1024r isn't a valid unicode string and can't be encoded in UTF-8." % proposed_value)

        return proposed_value

    def DefaultValue(self):
        return u''


class Int32ValueChecker(IntValueChecker):
    _MIN = -2147483648
    _MAX = 2147483647
    _TYPE = int


class Uint32ValueChecker(IntValueChecker):
    _MIN = 0
    _MAX = 4294967295L
    _TYPE = int


class Int64ValueChecker(IntValueChecker):
    _MIN = -9223372036854775808L
    _MAX = 9223372036854775807L
    _TYPE = long


class Uint64ValueChecker(IntValueChecker):
    _MIN = 0
    _MAX = 18446744073709551615L
    _TYPE = long


_FLOAT_MAX = float.fromhex('0x1.fffffep+127')
_FLOAT_MIN = -_FLOAT_MAX
_INF = float('inf')
_NEG_INF = float('-inf')

class FloatValueChecker(object):

    def CheckValue(self, proposed_value):
        if not isinstance(proposed_value, numbers.Real):
            message = '%.1024r has type %s, but expected one of: numbers.Real' % (proposed_value, type(proposed_value))
            raise TypeError(message)
        converted_value = float(proposed_value)
        if converted_value > _FLOAT_MAX:
            return _INF
        if converted_value < _FLOAT_MIN:
            return _NEG_INF
        return TruncateToFourByteFloat(converted_value)

    def DefaultValue(self):
        return 0.0


_VALUE_CHECKERS = {_FieldDescriptor.CPPTYPE_INT32: Int32ValueChecker(),
 _FieldDescriptor.CPPTYPE_INT64: Int64ValueChecker(),
 _FieldDescriptor.CPPTYPE_UINT32: Uint32ValueChecker(),
 _FieldDescriptor.CPPTYPE_UINT64: Uint64ValueChecker(),
 _FieldDescriptor.CPPTYPE_DOUBLE: TypeCheckerWithDefault(0.0, float, numbers.Real),
 _FieldDescriptor.CPPTYPE_FLOAT: FloatValueChecker(),
 _FieldDescriptor.CPPTYPE_BOOL: TypeCheckerWithDefault(False, bool, numbers.Integral),
 _FieldDescriptor.CPPTYPE_STRING: TypeCheckerWithDefault('', bytes)}
TYPE_TO_BYTE_SIZE_FN = {_FieldDescriptor.TYPE_DOUBLE: wire_format.DoubleByteSize,
 _FieldDescriptor.TYPE_FLOAT: wire_format.FloatByteSize,
 _FieldDescriptor.TYPE_INT64: wire_format.Int64ByteSize,
 _FieldDescriptor.TYPE_UINT64: wire_format.UInt64ByteSize,
 _FieldDescriptor.TYPE_INT32: wire_format.Int32ByteSize,
 _FieldDescriptor.TYPE_FIXED64: wire_format.Fixed64ByteSize,
 _FieldDescriptor.TYPE_FIXED32: wire_format.Fixed32ByteSize,
 _FieldDescriptor.TYPE_BOOL: wire_format.BoolByteSize,
 _FieldDescriptor.TYPE_STRING: wire_format.StringByteSize,
 _FieldDescriptor.TYPE_GROUP: wire_format.GroupByteSize,
 _FieldDescriptor.TYPE_MESSAGE: wire_format.MessageByteSize,
 _FieldDescriptor.TYPE_BYTES: wire_format.BytesByteSize,
 _FieldDescriptor.TYPE_UINT32: wire_format.UInt32ByteSize,
 _FieldDescriptor.TYPE_ENUM: wire_format.EnumByteSize,
 _FieldDescriptor.TYPE_SFIXED32: wire_format.SFixed32ByteSize,
 _FieldDescriptor.TYPE_SFIXED64: wire_format.SFixed64ByteSize,
 _FieldDescriptor.TYPE_SINT32: wire_format.SInt32ByteSize,
 _FieldDescriptor.TYPE_SINT64: wire_format.SInt64ByteSize}
TYPE_TO_ENCODER = {_FieldDescriptor.TYPE_DOUBLE: encoder.DoubleEncoder,
 _FieldDescriptor.TYPE_FLOAT: encoder.FloatEncoder,
 _FieldDescriptor.TYPE_INT64: encoder.Int64Encoder,
 _FieldDescriptor.TYPE_UINT64: encoder.UInt64Encoder,
 _FieldDescriptor.TYPE_INT32: encoder.Int32Encoder,
 _FieldDescriptor.TYPE_FIXED64: encoder.Fixed64Encoder,
 _FieldDescriptor.TYPE_FIXED32: encoder.Fixed32Encoder,
 _FieldDescriptor.TYPE_BOOL: encoder.BoolEncoder,
 _FieldDescriptor.TYPE_STRING: encoder.StringEncoder,
 _FieldDescriptor.TYPE_GROUP: encoder.GroupEncoder,
 _FieldDescriptor.TYPE_MESSAGE: encoder.MessageEncoder,
 _FieldDescriptor.TYPE_BYTES: encoder.BytesEncoder,
 _FieldDescriptor.TYPE_UINT32: encoder.UInt32Encoder,
 _FieldDescriptor.TYPE_ENUM: encoder.EnumEncoder,
 _FieldDescriptor.TYPE_SFIXED32: encoder.SFixed32Encoder,
 _FieldDescriptor.TYPE_SFIXED64: encoder.SFixed64Encoder,
 _FieldDescriptor.TYPE_SINT32: encoder.SInt32Encoder,
 _FieldDescriptor.TYPE_SINT64: encoder.SInt64Encoder}
TYPE_TO_SIZER = {_FieldDescriptor.TYPE_DOUBLE: encoder.DoubleSizer,
 _FieldDescriptor.TYPE_FLOAT: encoder.FloatSizer,
 _FieldDescriptor.TYPE_INT64: encoder.Int64Sizer,
 _FieldDescriptor.TYPE_UINT64: encoder.UInt64Sizer,
 _FieldDescriptor.TYPE_INT32: encoder.Int32Sizer,
 _FieldDescriptor.TYPE_FIXED64: encoder.Fixed64Sizer,
 _FieldDescriptor.TYPE_FIXED32: encoder.Fixed32Sizer,
 _FieldDescriptor.TYPE_BOOL: encoder.BoolSizer,
 _FieldDescriptor.TYPE_STRING: encoder.StringSizer,
 _FieldDescriptor.TYPE_GROUP: encoder.GroupSizer,
 _FieldDescriptor.TYPE_MESSAGE: encoder.MessageSizer,
 _FieldDescriptor.TYPE_BYTES: encoder.BytesSizer,
 _FieldDescriptor.TYPE_UINT32: encoder.UInt32Sizer,
 _FieldDescriptor.TYPE_ENUM: encoder.EnumSizer,
 _FieldDescriptor.TYPE_SFIXED32: encoder.SFixed32Sizer,
 _FieldDescriptor.TYPE_SFIXED64: encoder.SFixed64Sizer,
 _FieldDescriptor.TYPE_SINT32: encoder.SInt32Sizer,
 _FieldDescriptor.TYPE_SINT64: encoder.SInt64Sizer}
TYPE_TO_DECODER = {_FieldDescriptor.TYPE_DOUBLE: decoder.DoubleDecoder,
 _FieldDescriptor.TYPE_FLOAT: decoder.FloatDecoder,
 _FieldDescriptor.TYPE_INT64: decoder.Int64Decoder,
 _FieldDescriptor.TYPE_UINT64: decoder.UInt64Decoder,
 _FieldDescriptor.TYPE_INT32: decoder.Int32Decoder,
 _FieldDescriptor.TYPE_FIXED64: decoder.Fixed64Decoder,
 _FieldDescriptor.TYPE_FIXED32: decoder.Fixed32Decoder,
 _FieldDescriptor.TYPE_BOOL: decoder.BoolDecoder,
 _FieldDescriptor.TYPE_STRING: decoder.StringDecoder,
 _FieldDescriptor.TYPE_GROUP: decoder.GroupDecoder,
 _FieldDescriptor.TYPE_MESSAGE: decoder.MessageDecoder,
 _FieldDescriptor.TYPE_BYTES: decoder.BytesDecoder,
 _FieldDescriptor.TYPE_UINT32: decoder.UInt32Decoder,
 _FieldDescriptor.TYPE_ENUM: decoder.EnumDecoder,
 _FieldDescriptor.TYPE_SFIXED32: decoder.SFixed32Decoder,
 _FieldDescriptor.TYPE_SFIXED64: decoder.SFixed64Decoder,
 _FieldDescriptor.TYPE_SINT32: decoder.SInt32Decoder,
 _FieldDescriptor.TYPE_SINT64: decoder.SInt64Decoder}
FIELD_TYPE_TO_WIRE_TYPE = {_FieldDescriptor.TYPE_DOUBLE: wire_format.WIRETYPE_FIXED64,
 _FieldDescriptor.TYPE_FLOAT: wire_format.WIRETYPE_FIXED32,
 _FieldDescriptor.TYPE_INT64: wire_format.WIRETYPE_VARINT,
 _FieldDescriptor.TYPE_UINT64: wire_format.WIRETYPE_VARINT,
 _FieldDescriptor.TYPE_INT32: wire_format.WIRETYPE_VARINT,
 _FieldDescriptor.TYPE_FIXED64: wire_format.WIRETYPE_FIXED64,
 _FieldDescriptor.TYPE_FIXED32: wire_format.WIRETYPE_FIXED32,
 _FieldDescriptor.TYPE_BOOL: wire_format.WIRETYPE_VARINT,
 _FieldDescriptor.TYPE_STRING: wire_format.WIRETYPE_LENGTH_DELIMITED,
 _FieldDescriptor.TYPE_GROUP: wire_format.WIRETYPE_START_GROUP,
 _FieldDescriptor.TYPE_MESSAGE: wire_format.WIRETYPE_LENGTH_DELIMITED,
 _FieldDescriptor.TYPE_BYTES: wire_format.WIRETYPE_LENGTH_DELIMITED,
 _FieldDescriptor.TYPE_UINT32: wire_format.WIRETYPE_VARINT,
 _FieldDescriptor.TYPE_ENUM: wire_format.WIRETYPE_VARINT,
 _FieldDescriptor.TYPE_SFIXED32: wire_format.WIRETYPE_FIXED32,
 _FieldDescriptor.TYPE_SFIXED64: wire_format.WIRETYPE_FIXED64,
 _FieldDescriptor.TYPE_SINT32: wire_format.WIRETYPE_VARINT,
 _FieldDescriptor.TYPE_SINT64: wire_format.WIRETYPE_VARINT}
