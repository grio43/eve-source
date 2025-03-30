#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\json_format.py
__author__ = 'jieluo@google.com (Jie Luo)'
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

import base64
import json
import math
from operator import methodcaller
import re
import sys
import six
from google.protobuf.internal import type_checkers
from google.protobuf import descriptor
from google.protobuf import symbol_database
_TIMESTAMPFOMAT = '%Y-%m-%dT%H:%M:%S'
_INT_TYPES = frozenset([descriptor.FieldDescriptor.CPPTYPE_INT32,
 descriptor.FieldDescriptor.CPPTYPE_UINT32,
 descriptor.FieldDescriptor.CPPTYPE_INT64,
 descriptor.FieldDescriptor.CPPTYPE_UINT64])
_INT64_TYPES = frozenset([descriptor.FieldDescriptor.CPPTYPE_INT64, descriptor.FieldDescriptor.CPPTYPE_UINT64])
_FLOAT_TYPES = frozenset([descriptor.FieldDescriptor.CPPTYPE_FLOAT, descriptor.FieldDescriptor.CPPTYPE_DOUBLE])
_INFINITY = 'Infinity'
_NEG_INFINITY = '-Infinity'
_NAN = 'NaN'
_UNPAIRED_SURROGATE_PATTERN = re.compile(six.u('[\\ud800-\\udbff](?![\\udc00-\\udfff])|(?<![\\ud800-\\udbff])[\\udc00-\\udfff]'))
_VALID_EXTENSION_NAME = re.compile('\\[[a-zA-Z0-9\\._]*\\]$')

class Error(Exception):
    pass


class SerializeToJsonError(Error):
    pass


class ParseError(Error):
    pass


def MessageToJson(message, including_default_value_fields = False, preserving_proto_field_name = False, indent = 2, sort_keys = False, use_integers_for_enums = False, descriptor_pool = None, float_precision = None):
    printer = _Printer(including_default_value_fields, preserving_proto_field_name, use_integers_for_enums, descriptor_pool, float_precision=float_precision)
    return printer.ToJsonString(message, indent, sort_keys)


def MessageToDict(message, including_default_value_fields = False, preserving_proto_field_name = False, use_integers_for_enums = False, descriptor_pool = None, float_precision = None):
    printer = _Printer(including_default_value_fields, preserving_proto_field_name, use_integers_for_enums, descriptor_pool, float_precision=float_precision)
    return printer._MessageToJsonObject(message)


def _IsMapEntry(field):
    return field.type == descriptor.FieldDescriptor.TYPE_MESSAGE and field.message_type.has_options and field.message_type.GetOptions().map_entry


class _Printer(object):

    def __init__(self, including_default_value_fields = False, preserving_proto_field_name = False, use_integers_for_enums = False, descriptor_pool = None, float_precision = None):
        self.including_default_value_fields = including_default_value_fields
        self.preserving_proto_field_name = preserving_proto_field_name
        self.use_integers_for_enums = use_integers_for_enums
        self.descriptor_pool = descriptor_pool
        if float_precision:
            self.float_format = '.{}g'.format(float_precision)
        else:
            self.float_format = None

    def ToJsonString(self, message, indent, sort_keys):
        js = self._MessageToJsonObject(message)
        return json.dumps(js, indent=indent, sort_keys=sort_keys)

    def _MessageToJsonObject(self, message):
        message_descriptor = message.DESCRIPTOR
        full_name = message_descriptor.full_name
        if _IsWrapperMessage(message_descriptor):
            return self._WrapperMessageToJsonObject(message)
        if full_name in _WKTJSONMETHODS:
            return methodcaller(_WKTJSONMETHODS[full_name][0], message)(self)
        js = {}
        return self._RegularMessageToJsonObject(message, js)

    def _RegularMessageToJsonObject(self, message, js):
        fields = message.ListFields()
        try:
            for field, value in fields:
                if self.preserving_proto_field_name:
                    name = field.name
                else:
                    name = field.json_name
                if _IsMapEntry(field):
                    v_field = field.message_type.fields_by_name['value']
                    js_map = {}
                    for key in value:
                        if isinstance(key, bool):
                            if key:
                                recorded_key = 'true'
                            else:
                                recorded_key = 'false'
                        else:
                            recorded_key = key
                        js_map[recorded_key] = self._FieldToJsonObject(v_field, value[key])

                    js[name] = js_map
                elif field.label == descriptor.FieldDescriptor.LABEL_REPEATED:
                    js[name] = [ self._FieldToJsonObject(field, k) for k in value ]
                elif field.is_extension:
                    name = '[%s]' % field.full_name
                    js[name] = self._FieldToJsonObject(field, value)
                else:
                    js[name] = self._FieldToJsonObject(field, value)

            if self.including_default_value_fields:
                message_descriptor = message.DESCRIPTOR
                for field in message_descriptor.fields:
                    if field.label != descriptor.FieldDescriptor.LABEL_REPEATED and field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_MESSAGE or field.containing_oneof:
                        continue
                    if self.preserving_proto_field_name:
                        name = field.name
                    else:
                        name = field.json_name
                    if name in js:
                        continue
                    if _IsMapEntry(field):
                        js[name] = {}
                    elif field.label == descriptor.FieldDescriptor.LABEL_REPEATED:
                        js[name] = []
                    else:
                        js[name] = self._FieldToJsonObject(field, field.default_value)

        except ValueError as e:
            raise SerializeToJsonError('Failed to serialize {0} field: {1}.'.format(field.name, e))

        return js

    def _FieldToJsonObject(self, field, value):
        if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_MESSAGE:
            return self._MessageToJsonObject(value)
        if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_ENUM:
            if self.use_integers_for_enums:
                return value
            if field.enum_type.full_name == 'google.protobuf.NullValue':
                return
            enum_value = field.enum_type.values_by_number.get(value, None)
            if enum_value is not None:
                return enum_value.name
            if field.file.syntax == 'proto3':
                return value
            raise SerializeToJsonError('Enum field contains an integer value which can not mapped to an enum value.')
        elif field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_STRING:
            if field.type == descriptor.FieldDescriptor.TYPE_BYTES:
                return base64.b64encode(value).decode('utf-8')
            else:
                return value
        else:
            if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_BOOL:
                return bool(value)
            if field.cpp_type in _INT64_TYPES:
                return str(value)
            if field.cpp_type in _FLOAT_TYPES:
                if math.isinf(value):
                    if value < 0.0:
                        return _NEG_INFINITY
                    else:
                        return _INFINITY
                if math.isnan(value):
                    return _NAN
                if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_FLOAT:
                    if self.float_format:
                        return float(format(value, self.float_format))
                    else:
                        return type_checkers.ToShortestFloat(value)
        return value

    def _AnyMessageToJsonObject(self, message):
        if not message.ListFields():
            return {}
        js = OrderedDict()
        type_url = message.type_url
        js['@type'] = type_url
        sub_message = _CreateMessageFromTypeUrl(type_url, self.descriptor_pool)
        sub_message.ParseFromString(message.value)
        message_descriptor = sub_message.DESCRIPTOR
        full_name = message_descriptor.full_name
        if _IsWrapperMessage(message_descriptor):
            js['value'] = self._WrapperMessageToJsonObject(sub_message)
            return js
        if full_name in _WKTJSONMETHODS:
            js['value'] = methodcaller(_WKTJSONMETHODS[full_name][0], sub_message)(self)
            return js
        return self._RegularMessageToJsonObject(sub_message, js)

    def _GenericMessageToJsonObject(self, message):
        return message.ToJsonString()

    def _ValueMessageToJsonObject(self, message):
        which = message.WhichOneof('kind')
        if which is None or which == 'null_value':
            return
        if which == 'list_value':
            return self._ListValueMessageToJsonObject(message.list_value)
        if which == 'struct_value':
            value = message.struct_value
        else:
            value = getattr(message, which)
        oneof_descriptor = message.DESCRIPTOR.fields_by_name[which]
        return self._FieldToJsonObject(oneof_descriptor, value)

    def _ListValueMessageToJsonObject(self, message):
        return [ self._ValueMessageToJsonObject(value) for value in message.values ]

    def _StructMessageToJsonObject(self, message):
        fields = message.fields
        ret = {}
        for key in fields:
            ret[key] = self._ValueMessageToJsonObject(fields[key])

        return ret

    def _WrapperMessageToJsonObject(self, message):
        return self._FieldToJsonObject(message.DESCRIPTOR.fields_by_name['value'], message.value)


def _IsWrapperMessage(message_descriptor):
    return message_descriptor.file.name == 'google/protobuf/wrappers.proto'


def _DuplicateChecker(js):
    result = {}
    for name, value in js:
        if name in result:
            raise ParseError('Failed to load JSON: duplicate key {0}.'.format(name))
        result[name] = value

    return result


def _CreateMessageFromTypeUrl(type_url, descriptor_pool):
    db = symbol_database.Default()
    pool = db.pool if descriptor_pool is None else descriptor_pool
    type_name = type_url.split('/')[-1]
    try:
        message_descriptor = pool.FindMessageTypeByName(type_name)
    except KeyError:
        raise TypeError('Can not find message descriptor by type_url: {0}.'.format(type_url))

    message_class = db.GetPrototype(message_descriptor)
    return message_class()


def Parse(text, message, ignore_unknown_fields = False, descriptor_pool = None):
    if not isinstance(text, six.text_type):
        text = text.decode('utf-8')
    try:
        js = json.loads(text, object_pairs_hook=_DuplicateChecker)
    except ValueError as e:
        raise ParseError('Failed to load JSON: {0}.'.format(str(e)))

    return ParseDict(js, message, ignore_unknown_fields, descriptor_pool)


def ParseDict(js_dict, message, ignore_unknown_fields = False, descriptor_pool = None):
    parser = _Parser(ignore_unknown_fields, descriptor_pool)
    parser.ConvertMessage(js_dict, message)
    return message


_INT_OR_FLOAT = six.integer_types + (float,)

class _Parser(object):

    def __init__(self, ignore_unknown_fields, descriptor_pool):
        self.ignore_unknown_fields = ignore_unknown_fields
        self.descriptor_pool = descriptor_pool

    def ConvertMessage(self, value, message):
        message_descriptor = message.DESCRIPTOR
        full_name = message_descriptor.full_name
        if _IsWrapperMessage(message_descriptor):
            self._ConvertWrapperMessage(value, message)
        elif full_name in _WKTJSONMETHODS:
            methodcaller(_WKTJSONMETHODS[full_name][1], value, message)(self)
        else:
            self._ConvertFieldValuePair(value, message)

    def _ConvertFieldValuePair(self, js, message):
        names = []
        message_descriptor = message.DESCRIPTOR
        fields_by_json_name = dict(((f.json_name, f) for f in message_descriptor.fields))
        for name in js:
            try:
                field = fields_by_json_name.get(name, None)
                if not field:
                    field = message_descriptor.fields_by_name.get(name, None)
                if not field and _VALID_EXTENSION_NAME.match(name):
                    if not message_descriptor.is_extendable:
                        raise ParseError('Message type {0} does not have extensions'.format(message_descriptor.full_name))
                    identifier = name[1:-1]
                    field = message.Extensions._FindExtensionByName(identifier)
                    if not field:
                        identifier = '.'.join(identifier.split('.')[:-1])
                        field = message.Extensions._FindExtensionByName(identifier)
                if not field:
                    if self.ignore_unknown_fields:
                        continue
                    raise ParseError('Message type "{0}" has no field named "{1}".\n Available Fields(except extensions): {2}'.format(message_descriptor.full_name, name, [ f.json_name for f in message_descriptor.fields ]))
                if name in names:
                    raise ParseError('Message type "{0}" should not have multiple "{1}" fields.'.format(message.DESCRIPTOR.full_name, name))
                names.append(name)
                value = js[name]
                if field.containing_oneof is not None and value is not None:
                    oneof_name = field.containing_oneof.name
                    if oneof_name in names:
                        raise ParseError('Message type "{0}" should not have multiple "{1}" oneof fields.'.format(message.DESCRIPTOR.full_name, oneof_name))
                    names.append(oneof_name)
                if value is None:
                    if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_MESSAGE and field.message_type.full_name == 'google.protobuf.Value':
                        sub_message = getattr(message, field.name)
                        sub_message.null_value = 0
                    elif field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_ENUM and field.enum_type.full_name == 'google.protobuf.NullValue':
                        setattr(message, field.name, 0)
                    else:
                        message.ClearField(field.name)
                    continue
                if _IsMapEntry(field):
                    message.ClearField(field.name)
                    self._ConvertMapFieldValue(value, message, field)
                elif field.label == descriptor.FieldDescriptor.LABEL_REPEATED:
                    message.ClearField(field.name)
                    if not isinstance(value, list):
                        raise ParseError('repeated field {0} must be in [] which is {1}.'.format(name, value))
                    if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_MESSAGE:
                        for item in value:
                            sub_message = getattr(message, field.name).add()
                            if item is None and sub_message.DESCRIPTOR.full_name != 'google.protobuf.Value':
                                raise ParseError('null is not allowed to be used as an element in a repeated field.')
                            self.ConvertMessage(item, sub_message)

                    else:
                        for item in value:
                            if item is None:
                                raise ParseError('null is not allowed to be used as an element in a repeated field.')
                            getattr(message, field.name).append(_ConvertScalarFieldValue(item, field))

                elif field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_MESSAGE:
                    if field.is_extension:
                        sub_message = message.Extensions[field]
                    else:
                        sub_message = getattr(message, field.name)
                    sub_message.SetInParent()
                    self.ConvertMessage(value, sub_message)
                elif field.is_extension:
                    message.Extensions[field] = _ConvertScalarFieldValue(value, field)
                else:
                    setattr(message, field.name, _ConvertScalarFieldValue(value, field))
            except ParseError as e:
                if field and field.containing_oneof is None:
                    raise ParseError('Failed to parse {0} field: {1}.'.format(name, e))
                else:
                    raise ParseError(str(e))
            except ValueError as e:
                raise ParseError('Failed to parse {0} field: {1}.'.format(name, e))
            except TypeError as e:
                raise ParseError('Failed to parse {0} field: {1}.'.format(name, e))

    def _ConvertAnyMessage(self, value, message):
        if isinstance(value, dict) and not value:
            return
        try:
            type_url = value['@type']
        except KeyError:
            raise ParseError('@type is missing when parsing any message.')

        sub_message = _CreateMessageFromTypeUrl(type_url, self.descriptor_pool)
        message_descriptor = sub_message.DESCRIPTOR
        full_name = message_descriptor.full_name
        if _IsWrapperMessage(message_descriptor):
            self._ConvertWrapperMessage(value['value'], sub_message)
        elif full_name in _WKTJSONMETHODS:
            methodcaller(_WKTJSONMETHODS[full_name][1], value['value'], sub_message)(self)
        else:
            del value['@type']
            self._ConvertFieldValuePair(value, sub_message)
            value['@type'] = type_url
        message.value = sub_message.SerializeToString()
        message.type_url = type_url

    def _ConvertGenericMessage(self, value, message):
        try:
            message.FromJsonString(value)
        except ValueError as e:
            raise ParseError(e)

    def _ConvertValueMessage(self, value, message):
        if isinstance(value, dict):
            self._ConvertStructMessage(value, message.struct_value)
        elif isinstance(value, list):
            self._ConvertListValueMessage(value, message.list_value)
        elif value is None:
            message.null_value = 0
        elif isinstance(value, bool):
            message.bool_value = value
        elif isinstance(value, six.string_types):
            message.string_value = value
        elif isinstance(value, _INT_OR_FLOAT):
            message.number_value = value
        else:
            raise ParseError('Value {0} has unexpected type {1}.'.format(value, type(value)))

    def _ConvertListValueMessage(self, value, message):
        if not isinstance(value, list):
            raise ParseError('ListValue must be in [] which is {0}.'.format(value))
        message.ClearField('values')
        for item in value:
            self._ConvertValueMessage(item, message.values.add())

    def _ConvertStructMessage(self, value, message):
        if not isinstance(value, dict):
            raise ParseError('Struct must be in a dict which is {0}.'.format(value))
        message.Clear()
        for key in value:
            self._ConvertValueMessage(value[key], message.fields[key])

    def _ConvertWrapperMessage(self, value, message):
        field = message.DESCRIPTOR.fields_by_name['value']
        setattr(message, 'value', _ConvertScalarFieldValue(value, field))

    def _ConvertMapFieldValue(self, value, message, field):
        if not isinstance(value, dict):
            raise ParseError('Map field {0} must be in a dict which is {1}.'.format(field.name, value))
        key_field = field.message_type.fields_by_name['key']
        value_field = field.message_type.fields_by_name['value']
        for key in value:
            key_value = _ConvertScalarFieldValue(key, key_field, True)
            if value_field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_MESSAGE:
                self.ConvertMessage(value[key], getattr(message, field.name)[key_value])
            else:
                getattr(message, field.name)[key_value] = _ConvertScalarFieldValue(value[key], value_field)


def _ConvertScalarFieldValue(value, field, require_str = False):
    if field.cpp_type in _INT_TYPES:
        return _ConvertInteger(value)
    if field.cpp_type in _FLOAT_TYPES:
        return _ConvertFloat(value, field)
    if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_BOOL:
        return _ConvertBool(value, require_str)
    if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_STRING:
        if field.type == descriptor.FieldDescriptor.TYPE_BYTES:
            if isinstance(value, six.text_type):
                encoded = value.encode('utf-8')
            else:
                encoded = value
            padded_value = encoded + '=' * (4 - len(encoded) % 4)
            return base64.urlsafe_b64decode(padded_value)
        else:
            if _UNPAIRED_SURROGATE_PATTERN.search(value):
                raise ParseError('Unpaired surrogate')
            return value
    elif field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_ENUM:
        enum_value = field.enum_type.values_by_name.get(value, None)
        if enum_value is None:
            try:
                number = int(value)
                enum_value = field.enum_type.values_by_number.get(number, None)
            except ValueError:
                raise ParseError('Invalid enum value {0} for enum type {1}.'.format(value, field.enum_type.full_name))

            if enum_value is None:
                if field.file.syntax == 'proto3':
                    return number
                raise ParseError('Invalid enum value {0} for enum type {1}.'.format(value, field.enum_type.full_name))
        return enum_value.number


def _ConvertInteger(value):
    if isinstance(value, float) and not value.is_integer():
        raise ParseError("Couldn't parse integer: {0}.".format(value))
    if isinstance(value, six.text_type) and value.find(' ') != -1:
        raise ParseError('Couldn\'t parse integer: "{0}".'.format(value))
    if isinstance(value, bool):
        raise ParseError('Bool value {0} is not acceptable for integer field.'.format(value))
    return int(value)


def _ConvertFloat(value, field):
    if isinstance(value, float):
        if math.isnan(value):
            raise ParseError('Couldn\'t parse NaN, use quoted "NaN" instead.')
        if math.isinf(value):
            if value > 0:
                raise ParseError('Couldn\'t parse Infinity or value too large, use quoted "Infinity" instead.')
            else:
                raise ParseError('Couldn\'t parse -Infinity or value too small, use quoted "-Infinity" instead.')
        if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_FLOAT:
            if value > type_checkers._FLOAT_MAX:
                raise ParseError('Float value too large')
            if value < type_checkers._FLOAT_MIN:
                raise ParseError('Float value too small')
    if value == 'nan':
        raise ParseError('Couldn\'t parse float "nan", use "NaN" instead.')
    try:
        return float(value)
    except ValueError:
        if value == _NEG_INFINITY:
            return float('-inf')
        if value == _INFINITY:
            return float('inf')
        if value == _NAN:
            return float('nan')
        raise ParseError("Couldn't parse float: {0}.".format(value))


def _ConvertBool(value, require_str):
    if require_str:
        if value == 'true':
            return True
        if value == 'false':
            return False
        raise ParseError('Expected "true" or "false", not {0}.'.format(value))
    if not isinstance(value, bool):
        raise ParseError('Expected true or false without quotes.')
    return value


_WKTJSONMETHODS = {'google.protobuf.Any': ['_AnyMessageToJsonObject', '_ConvertAnyMessage'],
 'google.protobuf.Duration': ['_GenericMessageToJsonObject', '_ConvertGenericMessage'],
 'google.protobuf.FieldMask': ['_GenericMessageToJsonObject', '_ConvertGenericMessage'],
 'google.protobuf.ListValue': ['_ListValueMessageToJsonObject', '_ConvertListValueMessage'],
 'google.protobuf.Struct': ['_StructMessageToJsonObject', '_ConvertStructMessage'],
 'google.protobuf.Timestamp': ['_GenericMessageToJsonObject', '_ConvertGenericMessage'],
 'google.protobuf.Value': ['_ValueMessageToJsonObject', '_ConvertValueMessage']}
