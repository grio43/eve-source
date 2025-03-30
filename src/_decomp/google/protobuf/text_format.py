#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\text_format.py
__author__ = 'kenton@google.com (Kenton Varda)'
import encodings.raw_unicode_escape
import encodings.unicode_escape
import io
import math
import re
import six
from google.protobuf.internal import decoder
from google.protobuf.internal import type_checkers
from google.protobuf import descriptor
from google.protobuf import text_encoding
if six.PY3:
    long = int
__all__ = ['MessageToString',
 'Parse',
 'PrintMessage',
 'PrintField',
 'PrintFieldValue',
 'Merge',
 'MessageToBytes']
_INTEGER_CHECKERS = (type_checkers.Uint32ValueChecker(),
 type_checkers.Int32ValueChecker(),
 type_checkers.Uint64ValueChecker(),
 type_checkers.Int64ValueChecker())
_FLOAT_INFINITY = re.compile('-?inf(?:inity)?f?$', re.IGNORECASE)
_FLOAT_NAN = re.compile('nanf?$', re.IGNORECASE)
_QUOTES = frozenset(("'", '"'))
_ANY_FULL_TYPE_NAME = 'google.protobuf.Any'

class Error(Exception):
    pass


class ParseError(Error):

    def __init__(self, message = None, line = None, column = None):
        if message is not None and line is not None:
            loc = str(line)
            if column is not None:
                loc += ':{0}'.format(column)
            message = '{0} : {1}'.format(loc, message)
        if message is not None:
            super(ParseError, self).__init__(message)
        else:
            super(ParseError, self).__init__()
        self._line = line
        self._column = column

    def GetLine(self):
        return self._line

    def GetColumn(self):
        return self._column


class TextWriter(object):

    def __init__(self, as_utf8):
        if six.PY2:
            self._writer = io.BytesIO()
        else:
            self._writer = io.StringIO()

    def write(self, val):
        if six.PY2:
            if isinstance(val, six.text_type):
                val = val.encode('utf-8')
        return self._writer.write(val)

    def close(self):
        return self._writer.close()

    def getvalue(self):
        return self._writer.getvalue()


def MessageToString(message, as_utf8 = False, as_one_line = False, use_short_repeated_primitives = False, pointy_brackets = False, use_index_order = False, float_format = None, double_format = None, use_field_number = False, descriptor_pool = None, indent = 0, message_formatter = None, print_unknown_fields = False, force_colon = False):
    out = TextWriter(as_utf8)
    printer = _Printer(out, indent, as_utf8, as_one_line, use_short_repeated_primitives, pointy_brackets, use_index_order, float_format, double_format, use_field_number, descriptor_pool, message_formatter, print_unknown_fields=print_unknown_fields, force_colon=force_colon)
    printer.PrintMessage(message)
    result = out.getvalue()
    out.close()
    if as_one_line:
        return result.rstrip()
    return result


def MessageToBytes(message, **kwargs):
    text = MessageToString(message, **kwargs)
    if isinstance(text, bytes):
        return text
    codec = 'utf-8' if kwargs.get('as_utf8') else 'ascii'
    return text.encode(codec)


def _IsMapEntry(field):
    return field.type == descriptor.FieldDescriptor.TYPE_MESSAGE and field.message_type.has_options and field.message_type.GetOptions().map_entry


def PrintMessage(message, out, indent = 0, as_utf8 = False, as_one_line = False, use_short_repeated_primitives = False, pointy_brackets = False, use_index_order = False, float_format = None, double_format = None, use_field_number = False, descriptor_pool = None, message_formatter = None, print_unknown_fields = False, force_colon = False):
    printer = _Printer(out=out, indent=indent, as_utf8=as_utf8, as_one_line=as_one_line, use_short_repeated_primitives=use_short_repeated_primitives, pointy_brackets=pointy_brackets, use_index_order=use_index_order, float_format=float_format, double_format=double_format, use_field_number=use_field_number, descriptor_pool=descriptor_pool, message_formatter=message_formatter, print_unknown_fields=print_unknown_fields, force_colon=force_colon)
    printer.PrintMessage(message)


def PrintField(field, value, out, indent = 0, as_utf8 = False, as_one_line = False, use_short_repeated_primitives = False, pointy_brackets = False, use_index_order = False, float_format = None, double_format = None, message_formatter = None, print_unknown_fields = False, force_colon = False):
    printer = _Printer(out, indent, as_utf8, as_one_line, use_short_repeated_primitives, pointy_brackets, use_index_order, float_format, double_format, message_formatter=message_formatter, print_unknown_fields=print_unknown_fields, force_colon=force_colon)
    printer.PrintField(field, value)


def PrintFieldValue(field, value, out, indent = 0, as_utf8 = False, as_one_line = False, use_short_repeated_primitives = False, pointy_brackets = False, use_index_order = False, float_format = None, double_format = None, message_formatter = None, print_unknown_fields = False, force_colon = False):
    printer = _Printer(out, indent, as_utf8, as_one_line, use_short_repeated_primitives, pointy_brackets, use_index_order, float_format, double_format, message_formatter=message_formatter, print_unknown_fields=print_unknown_fields, force_colon=force_colon)
    printer.PrintFieldValue(field, value)


def _BuildMessageFromTypeName(type_name, descriptor_pool):
    if descriptor_pool is None:
        from google.protobuf import descriptor_pool as pool_mod
        descriptor_pool = pool_mod.Default()
    from google.protobuf import symbol_database
    database = symbol_database.Default()
    try:
        message_descriptor = descriptor_pool.FindMessageTypeByName(type_name)
    except KeyError:
        return

    message_type = database.GetPrototype(message_descriptor)
    return message_type()


WIRETYPE_LENGTH_DELIMITED = 2
WIRETYPE_START_GROUP = 3

class _Printer(object):

    def __init__(self, out, indent = 0, as_utf8 = False, as_one_line = False, use_short_repeated_primitives = False, pointy_brackets = False, use_index_order = False, float_format = None, double_format = None, use_field_number = False, descriptor_pool = None, message_formatter = None, print_unknown_fields = False, force_colon = False):
        self.out = out
        self.indent = indent
        self.as_utf8 = as_utf8
        self.as_one_line = as_one_line
        self.use_short_repeated_primitives = use_short_repeated_primitives
        self.pointy_brackets = pointy_brackets
        self.use_index_order = use_index_order
        self.float_format = float_format
        if double_format is not None:
            self.double_format = double_format
        else:
            self.double_format = float_format
        self.use_field_number = use_field_number
        self.descriptor_pool = descriptor_pool
        self.message_formatter = message_formatter
        self.print_unknown_fields = print_unknown_fields
        self.force_colon = force_colon

    def _TryPrintAsAnyMessage(self, message):
        if '/' not in message.type_url:
            return False
        else:
            packed_message = _BuildMessageFromTypeName(message.TypeName(), self.descriptor_pool)
            if packed_message:
                packed_message.MergeFromString(message.value)
                colon = ':' if self.force_colon else ''
                self.out.write('%s[%s]%s ' % (self.indent * ' ', message.type_url, colon))
                self._PrintMessageFieldValue(packed_message)
                self.out.write(' ' if self.as_one_line else '\n')
                return True
            return False

    def _TryCustomFormatMessage(self, message):
        formatted = self.message_formatter(message, self.indent, self.as_one_line)
        if formatted is None:
            return False
        out = self.out
        out.write(' ' * self.indent)
        out.write(formatted)
        out.write(' ' if self.as_one_line else '\n')
        return True

    def PrintMessage(self, message):
        if self.message_formatter and self._TryCustomFormatMessage(message):
            return
        if message.DESCRIPTOR.full_name == _ANY_FULL_TYPE_NAME and self._TryPrintAsAnyMessage(message):
            return
        fields = message.ListFields()
        if self.use_index_order:
            fields.sort(key=lambda x: (x[0].number if x[0].is_extension else x[0].index))
        for field, value in fields:
            if _IsMapEntry(field):
                for key in sorted(value):
                    entry_submsg = value.GetEntryClass()(key=key, value=value[key])
                    self.PrintField(field, entry_submsg)

            elif field.label == descriptor.FieldDescriptor.LABEL_REPEATED:
                if self.use_short_repeated_primitives and field.cpp_type != descriptor.FieldDescriptor.CPPTYPE_MESSAGE and field.cpp_type != descriptor.FieldDescriptor.CPPTYPE_STRING:
                    self._PrintShortRepeatedPrimitivesValue(field, value)
                else:
                    for element in value:
                        self.PrintField(field, element)

            else:
                self.PrintField(field, value)

        if self.print_unknown_fields:
            self._PrintUnknownFields(message.UnknownFields())

    def _PrintUnknownFields(self, unknown_fields):
        out = self.out
        for field in unknown_fields:
            out.write(' ' * self.indent)
            out.write(str(field.field_number))
            if field.wire_type == WIRETYPE_START_GROUP:
                if self.as_one_line:
                    out.write(' { ')
                else:
                    out.write(' {\n')
                    self.indent += 2
                self._PrintUnknownFields(field.data)
                if self.as_one_line:
                    out.write('} ')
                else:
                    self.indent -= 2
                    out.write(' ' * self.indent + '}\n')
            elif field.wire_type == WIRETYPE_LENGTH_DELIMITED:
                try:
                    embedded_unknown_message, pos = decoder._DecodeUnknownFieldSet(memoryview(field.data), 0, len(field.data))
                except Exception:
                    pos = 0

                if pos == len(field.data):
                    if self.as_one_line:
                        out.write(' { ')
                    else:
                        out.write(' {\n')
                        self.indent += 2
                    self._PrintUnknownFields(embedded_unknown_message)
                    if self.as_one_line:
                        out.write('} ')
                    else:
                        self.indent -= 2
                        out.write(' ' * self.indent + '}\n')
                else:
                    out.write(': "')
                    out.write(text_encoding.CEscape(field.data, False))
                    out.write('" ' if self.as_one_line else '"\n')
            else:
                out.write(': ')
                out.write(str(field.data))
                out.write(' ' if self.as_one_line else '\n')

    def _PrintFieldName(self, field):
        out = self.out
        out.write(' ' * self.indent)
        if self.use_field_number:
            out.write(str(field.number))
        elif field.is_extension:
            out.write('[')
            if field.containing_type.GetOptions().message_set_wire_format and field.type == descriptor.FieldDescriptor.TYPE_MESSAGE and field.label == descriptor.FieldDescriptor.LABEL_OPTIONAL:
                out.write(field.message_type.full_name)
            else:
                out.write(field.full_name)
            out.write(']')
        elif field.type == descriptor.FieldDescriptor.TYPE_GROUP:
            out.write(field.message_type.name)
        else:
            out.write(field.name)
        if self.force_colon or field.cpp_type != descriptor.FieldDescriptor.CPPTYPE_MESSAGE:
            out.write(':')

    def PrintField(self, field, value):
        self._PrintFieldName(field)
        self.out.write(' ')
        self.PrintFieldValue(field, value)
        self.out.write(' ' if self.as_one_line else '\n')

    def _PrintShortRepeatedPrimitivesValue(self, field, value):
        self._PrintFieldName(field)
        self.out.write(' [')
        for i in six.moves.range(len(value) - 1):
            self.PrintFieldValue(field, value[i])
            self.out.write(', ')

        self.PrintFieldValue(field, value[-1])
        self.out.write(']')
        self.out.write(' ' if self.as_one_line else '\n')

    def _PrintMessageFieldValue(self, value):
        if self.pointy_brackets:
            openb = '<'
            closeb = '>'
        else:
            openb = '{'
            closeb = '}'
        if self.as_one_line:
            self.out.write('%s ' % openb)
            self.PrintMessage(value)
            self.out.write(closeb)
        else:
            self.out.write('%s\n' % openb)
            self.indent += 2
            self.PrintMessage(value)
            self.indent -= 2
            self.out.write(' ' * self.indent + closeb)

    def PrintFieldValue(self, field, value):
        out = self.out
        if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_MESSAGE:
            self._PrintMessageFieldValue(value)
        elif field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_ENUM:
            enum_value = field.enum_type.values_by_number.get(value, None)
            if enum_value is not None:
                out.write(enum_value.name)
            else:
                out.write(str(value))
        elif field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_STRING:
            out.write('"')
            if isinstance(value, six.text_type) and (six.PY2 or not self.as_utf8):
                out_value = value.encode('utf-8')
            else:
                out_value = value
            if field.type == descriptor.FieldDescriptor.TYPE_BYTES:
                out_as_utf8 = False
            else:
                out_as_utf8 = self.as_utf8
            out.write(text_encoding.CEscape(out_value, out_as_utf8))
            out.write('"')
        elif field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_BOOL:
            if value:
                out.write('true')
            else:
                out.write('false')
        elif field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_FLOAT:
            if self.float_format is not None:
                out.write('{1:{0}}'.format(self.float_format, value))
            elif math.isnan(value):
                out.write(str(value))
            else:
                out.write(str(type_checkers.ToShortestFloat(value)))
        elif field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_DOUBLE and self.double_format is not None:
            out.write('{1:{0}}'.format(self.double_format, value))
        else:
            out.write(str(value))


def Parse(text, message, allow_unknown_extension = False, allow_field_number = False, descriptor_pool = None, allow_unknown_field = False):
    return ParseLines(text.split('\n' if isinstance(text, bytes) else u'\n'), message, allow_unknown_extension, allow_field_number, descriptor_pool=descriptor_pool, allow_unknown_field=allow_unknown_field)


def Merge(text, message, allow_unknown_extension = False, allow_field_number = False, descriptor_pool = None, allow_unknown_field = False):
    return MergeLines(text.split('\n' if isinstance(text, bytes) else u'\n'), message, allow_unknown_extension, allow_field_number, descriptor_pool=descriptor_pool, allow_unknown_field=allow_unknown_field)


def ParseLines(lines, message, allow_unknown_extension = False, allow_field_number = False, descriptor_pool = None, allow_unknown_field = False):
    parser = _Parser(allow_unknown_extension, allow_field_number, descriptor_pool=descriptor_pool, allow_unknown_field=allow_unknown_field)
    return parser.ParseLines(lines, message)


def MergeLines(lines, message, allow_unknown_extension = False, allow_field_number = False, descriptor_pool = None, allow_unknown_field = False):
    parser = _Parser(allow_unknown_extension, allow_field_number, descriptor_pool=descriptor_pool, allow_unknown_field=allow_unknown_field)
    return parser.MergeLines(lines, message)


class _Parser(object):

    def __init__(self, allow_unknown_extension = False, allow_field_number = False, descriptor_pool = None, allow_unknown_field = False):
        self.allow_unknown_extension = allow_unknown_extension
        self.allow_field_number = allow_field_number
        self.descriptor_pool = descriptor_pool
        self.allow_unknown_field = allow_unknown_field

    def ParseLines(self, lines, message):
        self._allow_multiple_scalars = False
        self._ParseOrMerge(lines, message)
        return message

    def MergeLines(self, lines, message):
        self._allow_multiple_scalars = True
        self._ParseOrMerge(lines, message)
        return message

    def _ParseOrMerge(self, lines, message):
        if six.PY2:
            str_lines = ((line if isinstance(line, str) else line.encode('utf-8')) for line in lines)
        else:
            str_lines = ((line if isinstance(line, str) else line.decode('utf-8')) for line in lines)
        tokenizer = Tokenizer(str_lines)
        while not tokenizer.AtEnd():
            self._MergeField(tokenizer, message)

    def _MergeField(self, tokenizer, message):
        message_descriptor = message.DESCRIPTOR
        if message_descriptor.full_name == _ANY_FULL_TYPE_NAME and tokenizer.TryConsume('['):
            type_url_prefix, packed_type_name = self._ConsumeAnyTypeUrl(tokenizer)
            tokenizer.Consume(']')
            tokenizer.TryConsume(':')
            if tokenizer.TryConsume('<'):
                expanded_any_end_token = '>'
            else:
                tokenizer.Consume('{')
                expanded_any_end_token = '}'
            expanded_any_sub_message = _BuildMessageFromTypeName(packed_type_name, self.descriptor_pool)
            if not expanded_any_sub_message:
                raise ParseError('Type %s not found in descriptor pool' % packed_type_name)
            while not tokenizer.TryConsume(expanded_any_end_token):
                if tokenizer.AtEnd():
                    raise tokenizer.ParseErrorPreviousToken('Expected "%s".' % (expanded_any_end_token,))
                self._MergeField(tokenizer, expanded_any_sub_message)

            deterministic = False
            message.Pack(expanded_any_sub_message, type_url_prefix=type_url_prefix, deterministic=deterministic)
            return
        if tokenizer.TryConsume('['):
            name = [tokenizer.ConsumeIdentifier()]
            while tokenizer.TryConsume('.'):
                name.append(tokenizer.ConsumeIdentifier())

            name = '.'.join(name)
            if not message_descriptor.is_extendable:
                raise tokenizer.ParseErrorPreviousToken('Message type "%s" does not have extensions.' % message_descriptor.full_name)
            field = message.Extensions._FindExtensionByName(name)
            if not field:
                if self.allow_unknown_extension:
                    field = None
                else:
                    raise tokenizer.ParseErrorPreviousToken('Extension "%s" not registered. Did you import the _pb2 module which defines it? If you are trying to place the extension in the MessageSet field of another message that is in an Any or MessageSet field, that message\'s _pb2 module must be imported as well' % name)
            elif message_descriptor != field.containing_type:
                raise tokenizer.ParseErrorPreviousToken('Extension "%s" does not extend message type "%s".' % (name, message_descriptor.full_name))
            tokenizer.Consume(']')
        else:
            name = tokenizer.ConsumeIdentifierOrNumber()
            if self.allow_field_number and name.isdigit():
                number = ParseInteger(name, True, True)
                field = message_descriptor.fields_by_number.get(number, None)
                if not field and message_descriptor.is_extendable:
                    field = message.Extensions._FindExtensionByNumber(number)
            else:
                field = message_descriptor.fields_by_name.get(name, None)
                if not field:
                    field = message_descriptor.fields_by_name.get(name.lower(), None)
                    if field and field.type != descriptor.FieldDescriptor.TYPE_GROUP:
                        field = None
                if field and field.type == descriptor.FieldDescriptor.TYPE_GROUP and field.message_type.name != name:
                    field = None
            if not field and not self.allow_unknown_field:
                raise tokenizer.ParseErrorPreviousToken('Message type "%s" has no field named "%s".' % (message_descriptor.full_name, name))
        if field:
            if not self._allow_multiple_scalars and field.containing_oneof:
                which_oneof = message.WhichOneof(field.containing_oneof.name)
                if which_oneof is not None and which_oneof != field.name:
                    raise tokenizer.ParseErrorPreviousToken('Field "%s" is specified along with field "%s", another member of oneof "%s" for message type "%s".' % (field.name,
                     which_oneof,
                     field.containing_oneof.name,
                     message_descriptor.full_name))
            if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_MESSAGE:
                tokenizer.TryConsume(':')
                merger = self._MergeMessageField
            else:
                tokenizer.Consume(':')
                merger = self._MergeScalarField
            if field.label == descriptor.FieldDescriptor.LABEL_REPEATED and tokenizer.TryConsume('['):
                if not tokenizer.TryConsume(']'):
                    while True:
                        merger(tokenizer, message, field)
                        if tokenizer.TryConsume(']'):
                            break
                        tokenizer.Consume(',')

            else:
                merger(tokenizer, message, field)
        else:
            _SkipFieldContents(tokenizer)
        if not tokenizer.TryConsume(','):
            tokenizer.TryConsume(';')

    def _ConsumeAnyTypeUrl(self, tokenizer):
        prefix = [tokenizer.ConsumeIdentifier()]
        tokenizer.Consume('.')
        prefix.append(tokenizer.ConsumeIdentifier())
        tokenizer.Consume('.')
        prefix.append(tokenizer.ConsumeIdentifier())
        tokenizer.Consume('/')
        name = [tokenizer.ConsumeIdentifier()]
        while tokenizer.TryConsume('.'):
            name.append(tokenizer.ConsumeIdentifier())

        return ('.'.join(prefix), '.'.join(name))

    def _MergeMessageField(self, tokenizer, message, field):
        is_map_entry = _IsMapEntry(field)
        if tokenizer.TryConsume('<'):
            end_token = '>'
        else:
            tokenizer.Consume('{')
            end_token = '}'
        if field.label == descriptor.FieldDescriptor.LABEL_REPEATED:
            if field.is_extension:
                sub_message = message.Extensions[field].add()
            elif is_map_entry:
                sub_message = getattr(message, field.name).GetEntryClass()()
            else:
                sub_message = getattr(message, field.name).add()
        else:
            if field.is_extension:
                if not self._allow_multiple_scalars and message.HasExtension(field):
                    raise tokenizer.ParseErrorPreviousToken('Message type "%s" should not have multiple "%s" extensions.' % (message.DESCRIPTOR.full_name, field.full_name))
                sub_message = message.Extensions[field]
            else:
                if not self._allow_multiple_scalars and message.HasField(field.name):
                    raise tokenizer.ParseErrorPreviousToken('Message type "%s" should not have multiple "%s" fields.' % (message.DESCRIPTOR.full_name, field.name))
                sub_message = getattr(message, field.name)
            sub_message.SetInParent()
        while not tokenizer.TryConsume(end_token):
            if tokenizer.AtEnd():
                raise tokenizer.ParseErrorPreviousToken('Expected "%s".' % (end_token,))
            self._MergeField(tokenizer, sub_message)

        if is_map_entry:
            value_cpptype = field.message_type.fields_by_name['value'].cpp_type
            if value_cpptype == descriptor.FieldDescriptor.CPPTYPE_MESSAGE:
                value = getattr(message, field.name)[sub_message.key]
                value.CopyFrom(sub_message.value)
            else:
                getattr(message, field.name)[sub_message.key] = sub_message.value

    @staticmethod
    def _IsProto3Syntax(message):
        message_descriptor = message.DESCRIPTOR
        return hasattr(message_descriptor, 'syntax') and message_descriptor.syntax == 'proto3'

    def _MergeScalarField(self, tokenizer, message, field):
        _ = self.allow_unknown_extension
        value = None
        if field.type in (descriptor.FieldDescriptor.TYPE_INT32, descriptor.FieldDescriptor.TYPE_SINT32, descriptor.FieldDescriptor.TYPE_SFIXED32):
            value = _ConsumeInt32(tokenizer)
        elif field.type in (descriptor.FieldDescriptor.TYPE_INT64, descriptor.FieldDescriptor.TYPE_SINT64, descriptor.FieldDescriptor.TYPE_SFIXED64):
            value = _ConsumeInt64(tokenizer)
        elif field.type in (descriptor.FieldDescriptor.TYPE_UINT32, descriptor.FieldDescriptor.TYPE_FIXED32):
            value = _ConsumeUint32(tokenizer)
        elif field.type in (descriptor.FieldDescriptor.TYPE_UINT64, descriptor.FieldDescriptor.TYPE_FIXED64):
            value = _ConsumeUint64(tokenizer)
        elif field.type in (descriptor.FieldDescriptor.TYPE_FLOAT, descriptor.FieldDescriptor.TYPE_DOUBLE):
            value = tokenizer.ConsumeFloat()
        elif field.type == descriptor.FieldDescriptor.TYPE_BOOL:
            value = tokenizer.ConsumeBool()
        elif field.type == descriptor.FieldDescriptor.TYPE_STRING:
            value = tokenizer.ConsumeString()
        elif field.type == descriptor.FieldDescriptor.TYPE_BYTES:
            value = tokenizer.ConsumeByteString()
        elif field.type == descriptor.FieldDescriptor.TYPE_ENUM:
            value = tokenizer.ConsumeEnum(field)
        else:
            raise RuntimeError('Unknown field type %d' % field.type)
        if field.label == descriptor.FieldDescriptor.LABEL_REPEATED:
            if field.is_extension:
                message.Extensions[field].append(value)
            else:
                getattr(message, field.name).append(value)
        elif field.is_extension:
            if not self._allow_multiple_scalars and not self._IsProto3Syntax(message) and message.HasExtension(field):
                raise tokenizer.ParseErrorPreviousToken('Message type "%s" should not have multiple "%s" extensions.' % (message.DESCRIPTOR.full_name, field.full_name))
            else:
                message.Extensions[field] = value
        else:
            duplicate_error = False
            if not self._allow_multiple_scalars:
                if self._IsProto3Syntax(message):
                    duplicate_error = bool(getattr(message, field.name))
                else:
                    duplicate_error = message.HasField(field.name)
            if duplicate_error:
                raise tokenizer.ParseErrorPreviousToken('Message type "%s" should not have multiple "%s" fields.' % (message.DESCRIPTOR.full_name, field.name))
            else:
                setattr(message, field.name, value)


def _SkipFieldContents(tokenizer):
    if tokenizer.TryConsume(':') and not tokenizer.LookingAt('{') and not tokenizer.LookingAt('<'):
        _SkipFieldValue(tokenizer)
    else:
        _SkipFieldMessage(tokenizer)


def _SkipField(tokenizer):
    if tokenizer.TryConsume('['):
        tokenizer.ConsumeIdentifier()
        while tokenizer.TryConsume('.'):
            tokenizer.ConsumeIdentifier()

        tokenizer.Consume(']')
    else:
        tokenizer.ConsumeIdentifierOrNumber()
    _SkipFieldContents(tokenizer)
    if not tokenizer.TryConsume(','):
        tokenizer.TryConsume(';')


def _SkipFieldMessage(tokenizer):
    if tokenizer.TryConsume('<'):
        delimiter = '>'
    else:
        tokenizer.Consume('{')
        delimiter = '}'
    while not tokenizer.LookingAt('>') and not tokenizer.LookingAt('}'):
        _SkipField(tokenizer)

    tokenizer.Consume(delimiter)


def _SkipFieldValue(tokenizer):
    if tokenizer.TryConsumeByteString():
        while tokenizer.TryConsumeByteString():
            pass

        return
    if not tokenizer.TryConsumeIdentifier() and not _TryConsumeInt64(tokenizer) and not _TryConsumeUint64(tokenizer) and not tokenizer.TryConsumeFloat():
        raise ParseError('Invalid field value: ' + tokenizer.token)


class Tokenizer(object):
    _WHITESPACE = re.compile('\\s+')
    _COMMENT = re.compile('(\\s*#.*$)', re.MULTILINE)
    _WHITESPACE_OR_COMMENT = re.compile('(\\s|(#.*$))+', re.MULTILINE)
    _TOKEN = re.compile('|'.join(['[a-zA-Z_][0-9a-zA-Z_+-]*', '([0-9+-]|(\\.[0-9]))[0-9a-zA-Z_.+-]*'] + [ '{qt}[^{qt}\\n\\\\]*((\\\\.)+[^{qt}\\n\\\\]*)*({qt}|\\\\?$)'.format(qt=mark) for mark in _QUOTES ]))
    _IDENTIFIER = re.compile('[^\\d\\W]\\w*')
    _IDENTIFIER_OR_NUMBER = re.compile('\\w+')

    def __init__(self, lines, skip_comments = True):
        self._position = 0
        self._line = -1
        self._column = 0
        self._token_start = None
        self.token = ''
        self._lines = iter(lines)
        self._current_line = ''
        self._previous_line = 0
        self._previous_column = 0
        self._more_lines = True
        self._skip_comments = skip_comments
        self._whitespace_pattern = skip_comments and self._WHITESPACE_OR_COMMENT or self._WHITESPACE
        self._SkipWhitespace()
        self.NextToken()

    def LookingAt(self, token):
        return self.token == token

    def AtEnd(self):
        return not self.token

    def _PopLine(self):
        while len(self._current_line) <= self._column:
            try:
                self._current_line = next(self._lines)
            except StopIteration:
                self._current_line = ''
                self._more_lines = False
                return

            self._line += 1
            self._column = 0

    def _SkipWhitespace(self):
        while True:
            self._PopLine()
            match = self._whitespace_pattern.match(self._current_line, self._column)
            if not match:
                break
            length = len(match.group(0))
            self._column += length

    def TryConsume(self, token):
        if self.token == token:
            self.NextToken()
            return True
        return False

    def Consume(self, token):
        if not self.TryConsume(token):
            raise self.ParseError('Expected "%s".' % token)

    def ConsumeComment(self):
        result = self.token
        if not self._COMMENT.match(result):
            raise self.ParseError('Expected comment.')
        self.NextToken()
        return result

    def ConsumeCommentOrTrailingComment(self):
        just_started = self._line == 0 and self._column == 0
        before_parsing = self._previous_line
        comment = self.ConsumeComment()
        trailing = self._previous_line == before_parsing and not just_started
        return (trailing, comment)

    def TryConsumeIdentifier(self):
        try:
            self.ConsumeIdentifier()
            return True
        except ParseError:
            return False

    def ConsumeIdentifier(self):
        result = self.token
        if not self._IDENTIFIER.match(result):
            raise self.ParseError('Expected identifier.')
        self.NextToken()
        return result

    def TryConsumeIdentifierOrNumber(self):
        try:
            self.ConsumeIdentifierOrNumber()
            return True
        except ParseError:
            return False

    def ConsumeIdentifierOrNumber(self):
        result = self.token
        if not self._IDENTIFIER_OR_NUMBER.match(result):
            raise self.ParseError('Expected identifier or number, got %s.' % result)
        self.NextToken()
        return result

    def TryConsumeInteger(self):
        try:
            self.ConsumeInteger()
            return True
        except ParseError:
            return False

    def ConsumeInteger(self, is_long = False):
        try:
            result = _ParseAbstractInteger(self.token, is_long=is_long)
        except ValueError as e:
            raise self.ParseError(str(e))

        self.NextToken()
        return result

    def TryConsumeFloat(self):
        try:
            self.ConsumeFloat()
            return True
        except ParseError:
            return False

    def ConsumeFloat(self):
        try:
            result = ParseFloat(self.token)
        except ValueError as e:
            raise self.ParseError(str(e))

        self.NextToken()
        return result

    def ConsumeBool(self):
        try:
            result = ParseBool(self.token)
        except ValueError as e:
            raise self.ParseError(str(e))

        self.NextToken()
        return result

    def TryConsumeByteString(self):
        try:
            self.ConsumeByteString()
            return True
        except ParseError:
            return False

    def ConsumeString(self):
        the_bytes = self.ConsumeByteString()
        try:
            return six.text_type(the_bytes, 'utf-8')
        except UnicodeDecodeError as e:
            raise self._StringParseError(e)

    def ConsumeByteString(self):
        the_list = [self._ConsumeSingleByteString()]
        while self.token and self.token[0] in _QUOTES:
            the_list.append(self._ConsumeSingleByteString())

        return ''.join(the_list)

    def _ConsumeSingleByteString(self):
        text = self.token
        if len(text) < 1 or text[0] not in _QUOTES:
            raise self.ParseError('Expected string but found: %r' % (text,))
        if len(text) < 2 or text[-1] != text[0]:
            raise self.ParseError('String missing ending quote: %r' % (text,))
        try:
            result = text_encoding.CUnescape(text[1:-1])
        except ValueError as e:
            raise self.ParseError(str(e))

        self.NextToken()
        return result

    def ConsumeEnum(self, field):
        try:
            result = ParseEnum(field, self.token)
        except ValueError as e:
            raise self.ParseError(str(e))

        self.NextToken()
        return result

    def ParseErrorPreviousToken(self, message):
        return ParseError(message, self._previous_line + 1, self._previous_column + 1)

    def ParseError(self, message):
        return ParseError("'" + self._current_line + "': " + message, self._line + 1, self._column + 1)

    def _StringParseError(self, e):
        return self.ParseError("Couldn't parse string: " + str(e))

    def NextToken(self):
        self._previous_line = self._line
        self._previous_column = self._column
        self._column += len(self.token)
        self._SkipWhitespace()
        if not self._more_lines:
            self.token = ''
            return
        match = self._TOKEN.match(self._current_line, self._column)
        if not match and not self._skip_comments:
            match = self._COMMENT.match(self._current_line, self._column)
        if match:
            token = match.group(0)
            self.token = token
        else:
            self.token = self._current_line[self._column]


_Tokenizer = Tokenizer

def _ConsumeInt32(tokenizer):
    return _ConsumeInteger(tokenizer, is_signed=True, is_long=False)


def _ConsumeUint32(tokenizer):
    return _ConsumeInteger(tokenizer, is_signed=False, is_long=False)


def _TryConsumeInt64(tokenizer):
    try:
        _ConsumeInt64(tokenizer)
        return True
    except ParseError:
        return False


def _ConsumeInt64(tokenizer):
    return _ConsumeInteger(tokenizer, is_signed=True, is_long=True)


def _TryConsumeUint64(tokenizer):
    try:
        _ConsumeUint64(tokenizer)
        return True
    except ParseError:
        return False


def _ConsumeUint64(tokenizer):
    return _ConsumeInteger(tokenizer, is_signed=False, is_long=True)


def _TryConsumeInteger(tokenizer, is_signed = False, is_long = False):
    try:
        _ConsumeInteger(tokenizer, is_signed=is_signed, is_long=is_long)
        return True
    except ParseError:
        return False


def _ConsumeInteger(tokenizer, is_signed = False, is_long = False):
    try:
        result = ParseInteger(tokenizer.token, is_signed=is_signed, is_long=is_long)
    except ValueError as e:
        raise tokenizer.ParseError(str(e))

    tokenizer.NextToken()
    return result


def ParseInteger(text, is_signed = False, is_long = False):
    result = _ParseAbstractInteger(text, is_long=is_long)
    checker = _INTEGER_CHECKERS[2 * int(is_long) + int(is_signed)]
    checker.CheckValue(result)
    return result


def _ParseAbstractInteger(text, is_long = False):
    orig_text = text
    c_octal_match = re.match('(-?)0(\\d+)$', text)
    if c_octal_match:
        text = c_octal_match.group(1) + '0o' + c_octal_match.group(2)
    try:
        if is_long:
            return long(text, 0)
        return int(text, 0)
    except ValueError:
        raise ValueError("Couldn't parse integer: %s" % orig_text)


def ParseFloat(text):
    try:
        return float(text)
    except ValueError:
        if _FLOAT_INFINITY.match(text):
            if text[0] == '-':
                return float('-inf')
            else:
                return float('inf')
        else:
            if _FLOAT_NAN.match(text):
                return float('nan')
            try:
                return float(text.rstrip('f'))
            except ValueError:
                raise ValueError("Couldn't parse float: %s" % text)


def ParseBool(text):
    if text in ('true', 't', '1', 'True'):
        return True
    if text in ('false', 'f', '0', 'False'):
        return False
    raise ValueError('Expected "true" or "false".')


def ParseEnum(field, value):
    enum_descriptor = field.enum_type
    try:
        number = int(value, 0)
    except ValueError:
        enum_value = enum_descriptor.values_by_name.get(value, None)
        if enum_value is None:
            raise ValueError('Enum type "%s" has no value named %s.' % (enum_descriptor.full_name, value))
    else:
        if hasattr(field.file, 'syntax'):
            if field.file.syntax == 'proto3':
                return number
        enum_value = enum_descriptor.values_by_number.get(number, None)
        if enum_value is None:
            raise ValueError('Enum type "%s" has no value with number %d.' % (enum_descriptor.full_name, number))

    return enum_value.number
