#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\internal\wire_format.py
__author__ = 'robinson@google.com (Will Robinson)'
import struct
from google.protobuf import descriptor
from google.protobuf import message
TAG_TYPE_BITS = 3
TAG_TYPE_MASK = (1 << TAG_TYPE_BITS) - 1
WIRETYPE_VARINT = 0
WIRETYPE_FIXED64 = 1
WIRETYPE_LENGTH_DELIMITED = 2
WIRETYPE_START_GROUP = 3
WIRETYPE_END_GROUP = 4
WIRETYPE_FIXED32 = 5
_WIRETYPE_MAX = 5
INT32_MAX = int(2147483647L)
INT32_MIN = int(-2147483648L)
UINT32_MAX = 4294967295L
INT64_MAX = 9223372036854775807L
INT64_MIN = -9223372036854775808L
UINT64_MAX = 18446744073709551615L
FORMAT_UINT32_LITTLE_ENDIAN = '<I'
FORMAT_UINT64_LITTLE_ENDIAN = '<Q'
FORMAT_FLOAT_LITTLE_ENDIAN = '<f'
FORMAT_DOUBLE_LITTLE_ENDIAN = '<d'
if struct.calcsize(FORMAT_UINT32_LITTLE_ENDIAN) != 4:
    raise AssertionError('Format "I" is not a 32-bit number.')
if struct.calcsize(FORMAT_UINT64_LITTLE_ENDIAN) != 8:
    raise AssertionError('Format "Q" is not a 64-bit number.')

def PackTag(field_number, wire_type):
    if not 0 <= wire_type <= _WIRETYPE_MAX:
        raise message.EncodeError('Unknown wire type: %d' % wire_type)
    return field_number << TAG_TYPE_BITS | wire_type


def UnpackTag(tag):
    return (tag >> TAG_TYPE_BITS, tag & TAG_TYPE_MASK)


def ZigZagEncode(value):
    if value >= 0:
        return value << 1
    return value << 1 ^ -1


def ZigZagDecode(value):
    if not value & 1:
        return value >> 1
    return value >> 1 ^ -1


def Int32ByteSize(field_number, int32):
    return Int64ByteSize(field_number, int32)


def Int32ByteSizeNoTag(int32):
    return _VarUInt64ByteSizeNoTag(18446744073709551615L & int32)


def Int64ByteSize(field_number, int64):
    return UInt64ByteSize(field_number, 18446744073709551615L & int64)


def UInt32ByteSize(field_number, uint32):
    return UInt64ByteSize(field_number, uint32)


def UInt64ByteSize(field_number, uint64):
    return TagByteSize(field_number) + _VarUInt64ByteSizeNoTag(uint64)


def SInt32ByteSize(field_number, int32):
    return UInt32ByteSize(field_number, ZigZagEncode(int32))


def SInt64ByteSize(field_number, int64):
    return UInt64ByteSize(field_number, ZigZagEncode(int64))


def Fixed32ByteSize(field_number, fixed32):
    return TagByteSize(field_number) + 4


def Fixed64ByteSize(field_number, fixed64):
    return TagByteSize(field_number) + 8


def SFixed32ByteSize(field_number, sfixed32):
    return TagByteSize(field_number) + 4


def SFixed64ByteSize(field_number, sfixed64):
    return TagByteSize(field_number) + 8


def FloatByteSize(field_number, flt):
    return TagByteSize(field_number) + 4


def DoubleByteSize(field_number, double):
    return TagByteSize(field_number) + 8


def BoolByteSize(field_number, b):
    return TagByteSize(field_number) + 1


def EnumByteSize(field_number, enum):
    return UInt32ByteSize(field_number, enum)


def StringByteSize(field_number, string):
    return BytesByteSize(field_number, string.encode('utf-8'))


def BytesByteSize(field_number, b):
    return TagByteSize(field_number) + _VarUInt64ByteSizeNoTag(len(b)) + len(b)


def GroupByteSize(field_number, message):
    return 2 * TagByteSize(field_number) + message.ByteSize()


def MessageByteSize(field_number, message):
    return TagByteSize(field_number) + _VarUInt64ByteSizeNoTag(message.ByteSize()) + message.ByteSize()


def MessageSetItemByteSize(field_number, msg):
    total_size = 2 * TagByteSize(1) + TagByteSize(2) + TagByteSize(3)
    total_size += _VarUInt64ByteSizeNoTag(field_number)
    message_size = msg.ByteSize()
    total_size += _VarUInt64ByteSizeNoTag(message_size)
    total_size += message_size
    return total_size


def TagByteSize(field_number):
    return _VarUInt64ByteSizeNoTag(PackTag(field_number, 0))


def _VarUInt64ByteSizeNoTag(uint64):
    if uint64 <= 127:
        return 1
    if uint64 <= 16383:
        return 2
    if uint64 <= 2097151:
        return 3
    if uint64 <= 268435455:
        return 4
    if uint64 <= 34359738367L:
        return 5
    if uint64 <= 4398046511103L:
        return 6
    if uint64 <= 562949953421311L:
        return 7
    if uint64 <= 72057594037927935L:
        return 8
    if uint64 <= 9223372036854775807L:
        return 9
    if uint64 > UINT64_MAX:
        raise message.EncodeError('Value out of range: %d' % uint64)
    return 10


NON_PACKABLE_TYPES = (descriptor.FieldDescriptor.TYPE_STRING,
 descriptor.FieldDescriptor.TYPE_GROUP,
 descriptor.FieldDescriptor.TYPE_MESSAGE,
 descriptor.FieldDescriptor.TYPE_BYTES)

def IsTypePackable(field_type):
    return field_type not in NON_PACKABLE_TYPES
