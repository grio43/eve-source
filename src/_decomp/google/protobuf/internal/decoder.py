#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\internal\decoder.py
__author__ = 'kenton@google.com (Kenton Varda)'
import struct
import sys
import six
_UCS2_MAXUNICODE = 65535
if six.PY3:
    long = int
else:
    import re
    _SURROGATE_PATTERN = re.compile(six.u('[\\ud800-\\udfff]'))
from google.protobuf.internal import containers
from google.protobuf.internal import encoder
from google.protobuf.internal import wire_format
from google.protobuf import message
_POS_INF = float('inf')
_NEG_INF = -_POS_INF
_NAN = _POS_INF * 0
_DecodeError = message.DecodeError

def _VarintDecoder(mask, result_type):

    def DecodeVarint(buffer, pos):
        result = 0
        shift = 0
        while 1:
            b = six.indexbytes(buffer, pos)
            result |= (b & 127) << shift
            pos += 1
            if not b & 128:
                result &= mask
                result = result_type(result)
                return (result, pos)
            shift += 7
            if shift >= 64:
                raise _DecodeError('Too many bytes when decoding varint.')

    return DecodeVarint


def _SignedVarintDecoder(bits, result_type):
    signbit = 1 << bits - 1
    mask = (1 << bits) - 1

    def DecodeVarint(buffer, pos):
        result = 0
        shift = 0
        while 1:
            b = six.indexbytes(buffer, pos)
            result |= (b & 127) << shift
            pos += 1
            if not b & 128:
                result &= mask
                result = (result ^ signbit) - signbit
                result = result_type(result)
                return (result, pos)
            shift += 7
            if shift >= 64:
                raise _DecodeError('Too many bytes when decoding varint.')

    return DecodeVarint


_DecodeVarint = _VarintDecoder(18446744073709551615L, long)
_DecodeSignedVarint = _SignedVarintDecoder(64, long)
_DecodeVarint32 = _VarintDecoder(4294967295L, int)
_DecodeSignedVarint32 = _SignedVarintDecoder(32, int)

def ReadTag(buffer, pos):
    start = pos
    while six.indexbytes(buffer, pos) & 128:
        pos += 1

    pos += 1
    tag_bytes = buffer[start:pos].tobytes()
    return (tag_bytes, pos)


def _SimpleDecoder(wire_type, decode_value):

    def SpecificDecoder(field_number, is_repeated, is_packed, key, new_default, clear_if_default = False):
        if is_packed:
            local_DecodeVarint = _DecodeVarint

            def DecodePackedField(buffer, pos, end, message, field_dict):
                value = field_dict.get(key)
                if value is None:
                    value = field_dict.setdefault(key, new_default(message))
                endpoint, pos = local_DecodeVarint(buffer, pos)
                endpoint += pos
                if endpoint > end:
                    raise _DecodeError('Truncated message.')
                while pos < endpoint:
                    element, pos = decode_value(buffer, pos)
                    value.append(element)

                if pos > endpoint:
                    del value[-1]
                    raise _DecodeError('Packed element was truncated.')
                return pos

            return DecodePackedField
        elif is_repeated:
            tag_bytes = encoder.TagBytes(field_number, wire_type)
            tag_len = len(tag_bytes)

            def DecodeRepeatedField(buffer, pos, end, message, field_dict):
                value = field_dict.get(key)
                if value is None:
                    value = field_dict.setdefault(key, new_default(message))
                while 1:
                    element, new_pos = decode_value(buffer, pos)
                    value.append(element)
                    pos = new_pos + tag_len
                    if buffer[new_pos:pos] != tag_bytes or new_pos >= end:
                        if new_pos > end:
                            raise _DecodeError('Truncated message.')
                        return new_pos

            return DecodeRepeatedField
        else:

            def DecodeField(buffer, pos, end, message, field_dict):
                new_value, pos = decode_value(buffer, pos)
                if pos > end:
                    raise _DecodeError('Truncated message.')
                if clear_if_default and not new_value:
                    field_dict.pop(key, None)
                else:
                    field_dict[key] = new_value
                return pos

            return DecodeField

    return SpecificDecoder


def _ModifiedDecoder(wire_type, decode_value, modify_value):

    def InnerDecode(buffer, pos):
        result, new_pos = decode_value(buffer, pos)
        return (modify_value(result), new_pos)

    return _SimpleDecoder(wire_type, InnerDecode)


def _StructPackDecoder(wire_type, format):
    value_size = struct.calcsize(format)
    local_unpack = struct.unpack

    def InnerDecode(buffer, pos):
        new_pos = pos + value_size
        result = local_unpack(format, buffer[pos:new_pos])[0]
        return (result, new_pos)

    return _SimpleDecoder(wire_type, InnerDecode)


def _FloatDecoder():
    local_unpack = struct.unpack

    def InnerDecode(buffer, pos):
        new_pos = pos + 4
        float_bytes = buffer[pos:new_pos].tobytes()
        if float_bytes[3:4] in '\x7f\xff' and float_bytes[2:3] >= '\x80':
            if float_bytes[0:3] != '\x00\x00\x80':
                return (_NAN, new_pos)
            if float_bytes[3:4] == '\xff':
                return (_NEG_INF, new_pos)
            return (_POS_INF, new_pos)
        result = local_unpack('<f', float_bytes)[0]
        return (result, new_pos)

    return _SimpleDecoder(wire_format.WIRETYPE_FIXED32, InnerDecode)


def _DoubleDecoder():
    local_unpack = struct.unpack

    def InnerDecode(buffer, pos):
        new_pos = pos + 8
        double_bytes = buffer[pos:new_pos].tobytes()
        if double_bytes[7:8] in '\x7f\xff' and double_bytes[6:7] >= '\xf0' and double_bytes[0:7] != '\x00\x00\x00\x00\x00\x00\xf0':
            return (_NAN, new_pos)
        result = local_unpack('<d', double_bytes)[0]
        return (result, new_pos)

    return _SimpleDecoder(wire_format.WIRETYPE_FIXED64, InnerDecode)


def EnumDecoder(field_number, is_repeated, is_packed, key, new_default, clear_if_default = False):
    enum_type = key.enum_type
    if is_packed:
        local_DecodeVarint = _DecodeVarint

        def DecodePackedField(buffer, pos, end, message, field_dict):
            value = field_dict.get(key)
            if value is None:
                value = field_dict.setdefault(key, new_default(message))
            endpoint, pos = local_DecodeVarint(buffer, pos)
            endpoint += pos
            if endpoint > end:
                raise _DecodeError('Truncated message.')
            while pos < endpoint:
                value_start_pos = pos
                element, pos = _DecodeSignedVarint32(buffer, pos)
                if element in enum_type.values_by_number:
                    value.append(element)
                else:
                    if not message._unknown_fields:
                        message._unknown_fields = []
                    tag_bytes = encoder.TagBytes(field_number, wire_format.WIRETYPE_VARINT)
                    message._unknown_fields.append((tag_bytes, buffer[value_start_pos:pos].tobytes()))
                    if message._unknown_field_set is None:
                        message._unknown_field_set = containers.UnknownFieldSet()
                    message._unknown_field_set._add(field_number, wire_format.WIRETYPE_VARINT, element)

            if pos > endpoint:
                if element in enum_type.values_by_number:
                    del value[-1]
                else:
                    del message._unknown_fields[-1]
                    del message._unknown_field_set._values[-1]
                raise _DecodeError('Packed element was truncated.')
            return pos

        return DecodePackedField
    elif is_repeated:
        tag_bytes = encoder.TagBytes(field_number, wire_format.WIRETYPE_VARINT)
        tag_len = len(tag_bytes)

        def DecodeRepeatedField(buffer, pos, end, message, field_dict):
            value = field_dict.get(key)
            if value is None:
                value = field_dict.setdefault(key, new_default(message))
            while 1:
                element, new_pos = _DecodeSignedVarint32(buffer, pos)
                if element in enum_type.values_by_number:
                    value.append(element)
                else:
                    if not message._unknown_fields:
                        message._unknown_fields = []
                    message._unknown_fields.append((tag_bytes, buffer[pos:new_pos].tobytes()))
                    if message._unknown_field_set is None:
                        message._unknown_field_set = containers.UnknownFieldSet()
                    message._unknown_field_set._add(field_number, wire_format.WIRETYPE_VARINT, element)
                pos = new_pos + tag_len
                if buffer[new_pos:pos] != tag_bytes or new_pos >= end:
                    if new_pos > end:
                        raise _DecodeError('Truncated message.')
                    return new_pos

        return DecodeRepeatedField
    else:

        def DecodeField(buffer, pos, end, message, field_dict):
            value_start_pos = pos
            enum_value, pos = _DecodeSignedVarint32(buffer, pos)
            if pos > end:
                raise _DecodeError('Truncated message.')
            if clear_if_default and not enum_value:
                field_dict.pop(key, None)
                return pos
            if enum_value in enum_type.values_by_number:
                field_dict[key] = enum_value
            else:
                if not message._unknown_fields:
                    message._unknown_fields = []
                tag_bytes = encoder.TagBytes(field_number, wire_format.WIRETYPE_VARINT)
                message._unknown_fields.append((tag_bytes, buffer[value_start_pos:pos].tobytes()))
                if message._unknown_field_set is None:
                    message._unknown_field_set = containers.UnknownFieldSet()
                message._unknown_field_set._add(field_number, wire_format.WIRETYPE_VARINT, enum_value)
            return pos

        return DecodeField


Int32Decoder = _SimpleDecoder(wire_format.WIRETYPE_VARINT, _DecodeSignedVarint32)
Int64Decoder = _SimpleDecoder(wire_format.WIRETYPE_VARINT, _DecodeSignedVarint)
UInt32Decoder = _SimpleDecoder(wire_format.WIRETYPE_VARINT, _DecodeVarint32)
UInt64Decoder = _SimpleDecoder(wire_format.WIRETYPE_VARINT, _DecodeVarint)
SInt32Decoder = _ModifiedDecoder(wire_format.WIRETYPE_VARINT, _DecodeVarint32, wire_format.ZigZagDecode)
SInt64Decoder = _ModifiedDecoder(wire_format.WIRETYPE_VARINT, _DecodeVarint, wire_format.ZigZagDecode)
Fixed32Decoder = _StructPackDecoder(wire_format.WIRETYPE_FIXED32, '<I')
Fixed64Decoder = _StructPackDecoder(wire_format.WIRETYPE_FIXED64, '<Q')
SFixed32Decoder = _StructPackDecoder(wire_format.WIRETYPE_FIXED32, '<i')
SFixed64Decoder = _StructPackDecoder(wire_format.WIRETYPE_FIXED64, '<q')
FloatDecoder = _FloatDecoder()
DoubleDecoder = _DoubleDecoder()
BoolDecoder = _ModifiedDecoder(wire_format.WIRETYPE_VARINT, _DecodeVarint, bool)

def StringDecoder(field_number, is_repeated, is_packed, key, new_default, is_strict_utf8 = False, clear_if_default = False):
    local_DecodeVarint = _DecodeVarint
    local_unicode = six.text_type

    def _ConvertToUnicode(memview):
        byte_str = memview.tobytes()
        try:
            value = local_unicode(byte_str, 'utf-8')
        except UnicodeDecodeError as e:
            e.reason = '%s in field: %s' % (e, key.full_name)
            raise

        if is_strict_utf8 and six.PY2 and sys.maxunicode > _UCS2_MAXUNICODE:
            if _SURROGATE_PATTERN.search(value):
                reason = 'String field %s contains invalid UTF-8 data when parsinga protocol buffer: surrogates not allowed. Usethe bytes type if you intend to send raw bytes.' % key.full_name
                raise message.DecodeError(reason)
        return value

    if is_repeated:
        tag_bytes = encoder.TagBytes(field_number, wire_format.WIRETYPE_LENGTH_DELIMITED)
        tag_len = len(tag_bytes)

        def DecodeRepeatedField(buffer, pos, end, message, field_dict):
            value = field_dict.get(key)
            if value is None:
                value = field_dict.setdefault(key, new_default(message))
            while 1:
                size, pos = local_DecodeVarint(buffer, pos)
                new_pos = pos + size
                if new_pos > end:
                    raise _DecodeError('Truncated string.')
                value.append(_ConvertToUnicode(buffer[pos:new_pos]))
                pos = new_pos + tag_len
                if buffer[new_pos:pos] != tag_bytes or new_pos == end:
                    return new_pos

        return DecodeRepeatedField
    else:

        def DecodeField(buffer, pos, end, message, field_dict):
            size, pos = local_DecodeVarint(buffer, pos)
            new_pos = pos + size
            if new_pos > end:
                raise _DecodeError('Truncated string.')
            if clear_if_default and not size:
                field_dict.pop(key, None)
            else:
                field_dict[key] = _ConvertToUnicode(buffer[pos:new_pos])
            return new_pos

        return DecodeField


def BytesDecoder(field_number, is_repeated, is_packed, key, new_default, clear_if_default = False):
    local_DecodeVarint = _DecodeVarint
    if is_repeated:
        tag_bytes = encoder.TagBytes(field_number, wire_format.WIRETYPE_LENGTH_DELIMITED)
        tag_len = len(tag_bytes)

        def DecodeRepeatedField(buffer, pos, end, message, field_dict):
            value = field_dict.get(key)
            if value is None:
                value = field_dict.setdefault(key, new_default(message))
            while 1:
                size, pos = local_DecodeVarint(buffer, pos)
                new_pos = pos + size
                if new_pos > end:
                    raise _DecodeError('Truncated string.')
                value.append(buffer[pos:new_pos].tobytes())
                pos = new_pos + tag_len
                if buffer[new_pos:pos] != tag_bytes or new_pos == end:
                    return new_pos

        return DecodeRepeatedField
    else:

        def DecodeField(buffer, pos, end, message, field_dict):
            size, pos = local_DecodeVarint(buffer, pos)
            new_pos = pos + size
            if new_pos > end:
                raise _DecodeError('Truncated string.')
            if clear_if_default and not size:
                field_dict.pop(key, None)
            else:
                field_dict[key] = buffer[pos:new_pos].tobytes()
            return new_pos

        return DecodeField


def GroupDecoder(field_number, is_repeated, is_packed, key, new_default):
    end_tag_bytes = encoder.TagBytes(field_number, wire_format.WIRETYPE_END_GROUP)
    end_tag_len = len(end_tag_bytes)
    if is_repeated:
        tag_bytes = encoder.TagBytes(field_number, wire_format.WIRETYPE_START_GROUP)
        tag_len = len(tag_bytes)

        def DecodeRepeatedField(buffer, pos, end, message, field_dict):
            value = field_dict.get(key)
            if value is None:
                value = field_dict.setdefault(key, new_default(message))
            while 1:
                value = field_dict.get(key)
                if value is None:
                    value = field_dict.setdefault(key, new_default(message))
                pos = value.add()._InternalParse(buffer, pos, end)
                new_pos = pos + end_tag_len
                if buffer[pos:new_pos] != end_tag_bytes or new_pos > end:
                    raise _DecodeError('Missing group end tag.')
                pos = new_pos + tag_len
                if buffer[new_pos:pos] != tag_bytes or new_pos == end:
                    return new_pos

        return DecodeRepeatedField
    else:

        def DecodeField(buffer, pos, end, message, field_dict):
            value = field_dict.get(key)
            if value is None:
                value = field_dict.setdefault(key, new_default(message))
            pos = value._InternalParse(buffer, pos, end)
            new_pos = pos + end_tag_len
            if buffer[pos:new_pos] != end_tag_bytes or new_pos > end:
                raise _DecodeError('Missing group end tag.')
            return new_pos

        return DecodeField


def MessageDecoder(field_number, is_repeated, is_packed, key, new_default):
    local_DecodeVarint = _DecodeVarint
    if is_repeated:
        tag_bytes = encoder.TagBytes(field_number, wire_format.WIRETYPE_LENGTH_DELIMITED)
        tag_len = len(tag_bytes)

        def DecodeRepeatedField(buffer, pos, end, message, field_dict):
            value = field_dict.get(key)
            if value is None:
                value = field_dict.setdefault(key, new_default(message))
            while 1:
                size, pos = local_DecodeVarint(buffer, pos)
                new_pos = pos + size
                if new_pos > end:
                    raise _DecodeError('Truncated message.')
                if value.add()._InternalParse(buffer, pos, new_pos) != new_pos:
                    raise _DecodeError('Unexpected end-group tag.')
                pos = new_pos + tag_len
                if buffer[new_pos:pos] != tag_bytes or new_pos == end:
                    return new_pos

        return DecodeRepeatedField
    else:

        def DecodeField(buffer, pos, end, message, field_dict):
            value = field_dict.get(key)
            if value is None:
                value = field_dict.setdefault(key, new_default(message))
            size, pos = local_DecodeVarint(buffer, pos)
            new_pos = pos + size
            if new_pos > end:
                raise _DecodeError('Truncated message.')
            if value._InternalParse(buffer, pos, new_pos) != new_pos:
                raise _DecodeError('Unexpected end-group tag.')
            return new_pos

        return DecodeField


MESSAGE_SET_ITEM_TAG = encoder.TagBytes(1, wire_format.WIRETYPE_START_GROUP)

def MessageSetItemDecoder(descriptor):
    type_id_tag_bytes = encoder.TagBytes(2, wire_format.WIRETYPE_VARINT)
    message_tag_bytes = encoder.TagBytes(3, wire_format.WIRETYPE_LENGTH_DELIMITED)
    item_end_tag_bytes = encoder.TagBytes(1, wire_format.WIRETYPE_END_GROUP)
    local_ReadTag = ReadTag
    local_DecodeVarint = _DecodeVarint
    local_SkipField = SkipField

    def DecodeItem(buffer, pos, end, message, field_dict):
        message_set_item_start = pos
        type_id = -1
        message_start = -1
        message_end = -1
        while 1:
            tag_bytes, pos = local_ReadTag(buffer, pos)
            if tag_bytes == type_id_tag_bytes:
                type_id, pos = local_DecodeVarint(buffer, pos)
            elif tag_bytes == message_tag_bytes:
                size, message_start = local_DecodeVarint(buffer, pos)
                pos = message_end = message_start + size
            elif tag_bytes == item_end_tag_bytes:
                break
            else:
                pos = SkipField(buffer, pos, end, tag_bytes)
                if pos == -1:
                    raise _DecodeError('Missing group end tag.')

        if pos > end:
            raise _DecodeError('Truncated message.')
        if type_id == -1:
            raise _DecodeError('MessageSet item missing type_id.')
        if message_start == -1:
            raise _DecodeError('MessageSet item missing message.')
        extension = message.Extensions._FindExtensionByNumber(type_id)
        if extension is not None:
            value = field_dict.get(extension)
            if value is None:
                message_type = extension.message_type
                if not hasattr(message_type, '_concrete_class'):
                    message._FACTORY.GetPrototype(message_type)
                value = field_dict.setdefault(extension, message_type._concrete_class())
            if value._InternalParse(buffer, message_start, message_end) != message_end:
                raise _DecodeError('Unexpected end-group tag.')
        else:
            if not message._unknown_fields:
                message._unknown_fields = []
            message._unknown_fields.append((MESSAGE_SET_ITEM_TAG, buffer[message_set_item_start:pos].tobytes()))
            if message._unknown_field_set is None:
                message._unknown_field_set = containers.UnknownFieldSet()
            message._unknown_field_set._add(type_id, wire_format.WIRETYPE_LENGTH_DELIMITED, buffer[message_start:message_end].tobytes())
        return pos

    return DecodeItem


def MapDecoder(field_descriptor, new_default, is_message_map):
    key = field_descriptor
    tag_bytes = encoder.TagBytes(field_descriptor.number, wire_format.WIRETYPE_LENGTH_DELIMITED)
    tag_len = len(tag_bytes)
    local_DecodeVarint = _DecodeVarint
    message_type = field_descriptor.message_type

    def DecodeMap(buffer, pos, end, message, field_dict):
        submsg = message_type._concrete_class()
        value = field_dict.get(key)
        if value is None:
            value = field_dict.setdefault(key, new_default(message))
        while 1:
            size, pos = local_DecodeVarint(buffer, pos)
            new_pos = pos + size
            if new_pos > end:
                raise _DecodeError('Truncated message.')
            submsg.Clear()
            if submsg._InternalParse(buffer, pos, new_pos) != new_pos:
                raise _DecodeError('Unexpected end-group tag.')
            if is_message_map:
                value[submsg.key].CopyFrom(submsg.value)
            else:
                value[submsg.key] = submsg.value
            pos = new_pos + tag_len
            if buffer[new_pos:pos] != tag_bytes or new_pos == end:
                return new_pos

    return DecodeMap


def _SkipVarint(buffer, pos, end):
    while ord(buffer[pos:pos + 1].tobytes()) & 128:
        pos += 1

    pos += 1
    if pos > end:
        raise _DecodeError('Truncated message.')
    return pos


def _SkipFixed64(buffer, pos, end):
    pos += 8
    if pos > end:
        raise _DecodeError('Truncated message.')
    return pos


def _DecodeFixed64(buffer, pos):
    new_pos = pos + 8
    return (struct.unpack('<Q', buffer[pos:new_pos])[0], new_pos)


def _SkipLengthDelimited(buffer, pos, end):
    size, pos = _DecodeVarint(buffer, pos)
    pos += size
    if pos > end:
        raise _DecodeError('Truncated message.')
    return pos


def _SkipGroup(buffer, pos, end):
    while 1:
        tag_bytes, pos = ReadTag(buffer, pos)
        new_pos = SkipField(buffer, pos, end, tag_bytes)
        if new_pos == -1:
            return pos
        pos = new_pos


def _DecodeUnknownFieldSet(buffer, pos, end_pos = None):
    unknown_field_set = containers.UnknownFieldSet()
    while end_pos is None or pos < end_pos:
        tag_bytes, pos = ReadTag(buffer, pos)
        tag, _ = _DecodeVarint(tag_bytes, 0)
        field_number, wire_type = wire_format.UnpackTag(tag)
        if wire_type == wire_format.WIRETYPE_END_GROUP:
            break
        data, pos = _DecodeUnknownField(buffer, pos, wire_type)
        unknown_field_set._add(field_number, wire_type, data)

    return (unknown_field_set, pos)


def _DecodeUnknownField(buffer, pos, wire_type):
    if wire_type == wire_format.WIRETYPE_VARINT:
        data, pos = _DecodeVarint(buffer, pos)
    elif wire_type == wire_format.WIRETYPE_FIXED64:
        data, pos = _DecodeFixed64(buffer, pos)
    elif wire_type == wire_format.WIRETYPE_FIXED32:
        data, pos = _DecodeFixed32(buffer, pos)
    elif wire_type == wire_format.WIRETYPE_LENGTH_DELIMITED:
        size, pos = _DecodeVarint(buffer, pos)
        data = buffer[pos:pos + size].tobytes()
        pos += size
    elif wire_type == wire_format.WIRETYPE_START_GROUP:
        data, pos = _DecodeUnknownFieldSet(buffer, pos)
    else:
        if wire_type == wire_format.WIRETYPE_END_GROUP:
            return (0, -1)
        raise _DecodeError('Wrong wire type in tag.')
    return (data, pos)


def _EndGroup(buffer, pos, end):
    return -1


def _SkipFixed32(buffer, pos, end):
    pos += 4
    if pos > end:
        raise _DecodeError('Truncated message.')
    return pos


def _DecodeFixed32(buffer, pos):
    new_pos = pos + 4
    return (struct.unpack('<I', buffer[pos:new_pos])[0], new_pos)


def _RaiseInvalidWireType(buffer, pos, end):
    raise _DecodeError('Tag had invalid wire type.')


def _FieldSkipper():
    WIRETYPE_TO_SKIPPER = [_SkipVarint,
     _SkipFixed64,
     _SkipLengthDelimited,
     _SkipGroup,
     _EndGroup,
     _SkipFixed32,
     _RaiseInvalidWireType,
     _RaiseInvalidWireType]
    wiretype_mask = wire_format.TAG_TYPE_MASK

    def SkipField(buffer, pos, end, tag_bytes):
        wire_type = ord(tag_bytes[0:1]) & wiretype_mask
        return WIRETYPE_TO_SKIPPER[wire_type](buffer, pos, end)

    return SkipField


SkipField = _FieldSkipper()
