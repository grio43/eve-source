#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\internal\well_known_types.py
__author__ = 'jieluo@google.com (Jie Luo)'
import calendar
from datetime import datetime
from datetime import timedelta
import six
try:
    import collections.abc as collections_abc
except ImportError:
    import collections as collections_abc

from google.protobuf.descriptor import FieldDescriptor
_TIMESTAMPFOMAT = '%Y-%m-%dT%H:%M:%S'
_NANOS_PER_SECOND = 1000000000
_NANOS_PER_MILLISECOND = 1000000
_NANOS_PER_MICROSECOND = 1000
_MILLIS_PER_SECOND = 1000
_MICROS_PER_SECOND = 1000000
_SECONDS_PER_DAY = 86400
_DURATION_SECONDS_MAX = 315576000000L

class Any(object):
    __slots__ = ()

    def Pack(self, msg, type_url_prefix = 'type.googleapis.com/', deterministic = None):
        if len(type_url_prefix) < 1 or type_url_prefix[-1] != '/':
            self.type_url = '%s/%s' % (type_url_prefix, msg.DESCRIPTOR.full_name)
        else:
            self.type_url = '%s%s' % (type_url_prefix, msg.DESCRIPTOR.full_name)
        self.value = msg.SerializeToString(deterministic=deterministic)

    def Unpack(self, msg):
        descriptor = msg.DESCRIPTOR
        if not self.Is(descriptor):
            return False
        msg.ParseFromString(self.value)
        return True

    def TypeName(self):
        return self.type_url.split('/')[-1]

    def Is(self, descriptor):
        return '/' in self.type_url and self.TypeName() == descriptor.full_name


_EPOCH_DATETIME = datetime.utcfromtimestamp(0)

class Timestamp(object):
    __slots__ = ()

    def ToJsonString(self):
        nanos = self.nanos % _NANOS_PER_SECOND
        total_sec = self.seconds + (self.nanos - nanos) // _NANOS_PER_SECOND
        seconds = total_sec % _SECONDS_PER_DAY
        days = (total_sec - seconds) // _SECONDS_PER_DAY
        dt = datetime(1970, 1, 1) + timedelta(days, seconds)
        result = dt.isoformat()
        if nanos % 1000000000.0 == 0:
            return result + 'Z'
        if nanos % 1000000.0 == 0:
            return result + '.%03dZ' % (nanos / 1000000.0)
        if nanos % 1000.0 == 0:
            return result + '.%06dZ' % (nanos / 1000.0)
        return result + '.%09dZ' % nanos

    def FromJsonString(self, value):
        timezone_offset = value.find('Z')
        if timezone_offset == -1:
            timezone_offset = value.find('+')
        if timezone_offset == -1:
            timezone_offset = value.rfind('-')
        if timezone_offset == -1:
            raise ValueError('Failed to parse timestamp: missing valid timezone offset.')
        time_value = value[0:timezone_offset]
        point_position = time_value.find('.')
        if point_position == -1:
            second_value = time_value
            nano_value = ''
        else:
            second_value = time_value[:point_position]
            nano_value = time_value[point_position + 1:]
        if 't' in second_value:
            raise ValueError("time data '{0}' does not match format '%Y-%m-%dT%H:%M:%S', lowercase 't' is not accepted".format(second_value))
        date_object = datetime.strptime(second_value, _TIMESTAMPFOMAT)
        td = date_object - datetime(1970, 1, 1)
        seconds = td.seconds + td.days * _SECONDS_PER_DAY
        if len(nano_value) > 9:
            raise ValueError('Failed to parse Timestamp: nanos {0} more than 9 fractional digits.'.format(nano_value))
        if nano_value:
            nanos = round(float('0.' + nano_value) * 1000000000.0)
        else:
            nanos = 0
        if value[timezone_offset] == 'Z':
            if len(value) != timezone_offset + 1:
                raise ValueError('Failed to parse timestamp: invalid trailing data {0}.'.format(value))
        else:
            timezone = value[timezone_offset:]
            pos = timezone.find(':')
            if pos == -1:
                raise ValueError('Invalid timezone offset value: {0}.'.format(timezone))
            if timezone[0] == '+':
                seconds -= (int(timezone[1:pos]) * 60 + int(timezone[pos + 1:])) * 60
            else:
                seconds += (int(timezone[1:pos]) * 60 + int(timezone[pos + 1:])) * 60
        self.seconds = int(seconds)
        self.nanos = int(nanos)

    def GetCurrentTime(self):
        self.FromDatetime(datetime.utcnow())

    def ToNanoseconds(self):
        return self.seconds * _NANOS_PER_SECOND + self.nanos

    def ToMicroseconds(self):
        return self.seconds * _MICROS_PER_SECOND + self.nanos // _NANOS_PER_MICROSECOND

    def ToMilliseconds(self):
        return self.seconds * _MILLIS_PER_SECOND + self.nanos // _NANOS_PER_MILLISECOND

    def ToSeconds(self):
        return self.seconds

    def FromNanoseconds(self, nanos):
        self.seconds = nanos // _NANOS_PER_SECOND
        self.nanos = nanos % _NANOS_PER_SECOND

    def FromMicroseconds(self, micros):
        self.seconds = micros // _MICROS_PER_SECOND
        self.nanos = micros % _MICROS_PER_SECOND * _NANOS_PER_MICROSECOND

    def FromMilliseconds(self, millis):
        self.seconds = millis // _MILLIS_PER_SECOND
        self.nanos = millis % _MILLIS_PER_SECOND * _NANOS_PER_MILLISECOND

    def FromSeconds(self, seconds):
        self.seconds = seconds
        self.nanos = 0

    def ToDatetime(self):
        return _EPOCH_DATETIME + timedelta(seconds=self.seconds, microseconds=_RoundTowardZero(self.nanos, _NANOS_PER_MICROSECOND))

    def FromDatetime(self, dt):
        self.seconds = calendar.timegm(dt.utctimetuple())
        self.nanos = dt.microsecond * _NANOS_PER_MICROSECOND


class Duration(object):
    __slots__ = ()

    def ToJsonString(self):
        _CheckDurationValid(self.seconds, self.nanos)
        if self.seconds < 0 or self.nanos < 0:
            result = '-'
            seconds = -self.seconds + int((0 - self.nanos) // 1000000000.0)
            nanos = (0 - self.nanos) % 1000000000.0
        else:
            result = ''
            seconds = self.seconds + int(self.nanos // 1000000000.0)
            nanos = self.nanos % 1000000000.0
        result += '%d' % seconds
        if nanos % 1000000000.0 == 0:
            return result + 's'
        if nanos % 1000000.0 == 0:
            return result + '.%03ds' % (nanos / 1000000.0)
        if nanos % 1000.0 == 0:
            return result + '.%06ds' % (nanos / 1000.0)
        return result + '.%09ds' % nanos

    def FromJsonString(self, value):
        if len(value) < 1 or value[-1] != 's':
            raise ValueError('Duration must end with letter "s": {0}.'.format(value))
        try:
            pos = value.find('.')
            if pos == -1:
                seconds = int(value[:-1])
                nanos = 0
            else:
                seconds = int(value[:pos])
                if value[0] == '-':
                    nanos = int(round(float('-0{0}'.format(value[pos:-1])) * 1000000000.0))
                else:
                    nanos = int(round(float('0{0}'.format(value[pos:-1])) * 1000000000.0))
            _CheckDurationValid(seconds, nanos)
            self.seconds = seconds
            self.nanos = nanos
        except ValueError as e:
            raise ValueError("Couldn't parse duration: {0} : {1}.".format(value, e))

    def ToNanoseconds(self):
        return self.seconds * _NANOS_PER_SECOND + self.nanos

    def ToMicroseconds(self):
        micros = _RoundTowardZero(self.nanos, _NANOS_PER_MICROSECOND)
        return self.seconds * _MICROS_PER_SECOND + micros

    def ToMilliseconds(self):
        millis = _RoundTowardZero(self.nanos, _NANOS_PER_MILLISECOND)
        return self.seconds * _MILLIS_PER_SECOND + millis

    def ToSeconds(self):
        return self.seconds

    def FromNanoseconds(self, nanos):
        self._NormalizeDuration(nanos // _NANOS_PER_SECOND, nanos % _NANOS_PER_SECOND)

    def FromMicroseconds(self, micros):
        self._NormalizeDuration(micros // _MICROS_PER_SECOND, micros % _MICROS_PER_SECOND * _NANOS_PER_MICROSECOND)

    def FromMilliseconds(self, millis):
        self._NormalizeDuration(millis // _MILLIS_PER_SECOND, millis % _MILLIS_PER_SECOND * _NANOS_PER_MILLISECOND)

    def FromSeconds(self, seconds):
        self.seconds = seconds
        self.nanos = 0

    def ToTimedelta(self):
        return timedelta(seconds=self.seconds, microseconds=_RoundTowardZero(self.nanos, _NANOS_PER_MICROSECOND))

    def FromTimedelta(self, td):
        self._NormalizeDuration(td.seconds + td.days * _SECONDS_PER_DAY, td.microseconds * _NANOS_PER_MICROSECOND)

    def _NormalizeDuration(self, seconds, nanos):
        if seconds < 0 and nanos > 0:
            seconds += 1
            nanos -= _NANOS_PER_SECOND
        self.seconds = seconds
        self.nanos = nanos


def _CheckDurationValid(seconds, nanos):
    if seconds < -_DURATION_SECONDS_MAX or seconds > _DURATION_SECONDS_MAX:
        raise ValueError('Duration is not valid: Seconds {0} must be in range [-315576000000, 315576000000].'.format(seconds))
    if nanos <= -_NANOS_PER_SECOND or nanos >= _NANOS_PER_SECOND:
        raise ValueError('Duration is not valid: Nanos {0} must be in range [-999999999, 999999999].'.format(nanos))
    if nanos < 0 and seconds > 0 or nanos > 0 and seconds < 0:
        raise ValueError('Duration is not valid: Sign mismatch.')


def _RoundTowardZero(value, divider):
    result = value // divider
    remainder = value % divider
    if result < 0 and remainder > 0:
        return result + 1
    else:
        return result


class FieldMask(object):
    __slots__ = ()

    def ToJsonString(self):
        camelcase_paths = []
        for path in self.paths:
            camelcase_paths.append(_SnakeCaseToCamelCase(path))

        return ','.join(camelcase_paths)

    def FromJsonString(self, value):
        self.Clear()
        if value:
            for path in value.split(','):
                self.paths.append(_CamelCaseToSnakeCase(path))

    def IsValidForDescriptor(self, message_descriptor):
        for path in self.paths:
            if not _IsValidPath(message_descriptor, path):
                return False

        return True

    def AllFieldsFromDescriptor(self, message_descriptor):
        self.Clear()
        for field in message_descriptor.fields:
            self.paths.append(field.name)

    def CanonicalFormFromMask(self, mask):
        tree = _FieldMaskTree(mask)
        tree.ToFieldMask(self)

    def Union(self, mask1, mask2):
        _CheckFieldMaskMessage(mask1)
        _CheckFieldMaskMessage(mask2)
        tree = _FieldMaskTree(mask1)
        tree.MergeFromFieldMask(mask2)
        tree.ToFieldMask(self)

    def Intersect(self, mask1, mask2):
        _CheckFieldMaskMessage(mask1)
        _CheckFieldMaskMessage(mask2)
        tree = _FieldMaskTree(mask1)
        intersection = _FieldMaskTree()
        for path in mask2.paths:
            tree.IntersectPath(path, intersection)

        intersection.ToFieldMask(self)

    def MergeMessage(self, source, destination, replace_message_field = False, replace_repeated_field = False):
        tree = _FieldMaskTree(self)
        tree.MergeMessage(source, destination, replace_message_field, replace_repeated_field)


def _IsValidPath(message_descriptor, path):
    parts = path.split('.')
    last = parts.pop()
    for name in parts:
        field = message_descriptor.fields_by_name.get(name)
        if field is None or field.label == FieldDescriptor.LABEL_REPEATED or field.type != FieldDescriptor.TYPE_MESSAGE:
            return False
        message_descriptor = field.message_type

    return last in message_descriptor.fields_by_name


def _CheckFieldMaskMessage(message):
    message_descriptor = message.DESCRIPTOR
    if message_descriptor.name != 'FieldMask' or message_descriptor.file.name != 'google/protobuf/field_mask.proto':
        raise ValueError('Message {0} is not a FieldMask.'.format(message_descriptor.full_name))


def _SnakeCaseToCamelCase(path_name):
    result = []
    after_underscore = False
    for c in path_name:
        if c.isupper():
            raise ValueError('Fail to print FieldMask to Json string: Path name {0} must not contain uppercase letters.'.format(path_name))
        if after_underscore:
            if c.islower():
                result.append(c.upper())
                after_underscore = False
            else:
                raise ValueError('Fail to print FieldMask to Json string: The character after a "_" must be a lowercase letter in path name {0}.'.format(path_name))
        elif c == '_':
            after_underscore = True
        else:
            result += c

    if after_underscore:
        raise ValueError('Fail to print FieldMask to Json string: Trailing "_" in path name {0}.'.format(path_name))
    return ''.join(result)


def _CamelCaseToSnakeCase(path_name):
    result = []
    for c in path_name:
        if c == '_':
            raise ValueError('Fail to parse FieldMask: Path name {0} must not contain "_"s.'.format(path_name))
        if c.isupper():
            result += '_'
            result += c.lower()
        else:
            result += c

    return ''.join(result)


class _FieldMaskTree(object):
    __slots__ = ('_root',)

    def __init__(self, field_mask = None):
        self._root = {}
        if field_mask:
            self.MergeFromFieldMask(field_mask)

    def MergeFromFieldMask(self, field_mask):
        for path in field_mask.paths:
            self.AddPath(path)

    def AddPath(self, path):
        node = self._root
        for name in path.split('.'):
            if name not in node:
                node[name] = {}
            elif not node[name]:
                return
            node = node[name]

        node.clear()

    def ToFieldMask(self, field_mask):
        field_mask.Clear()
        _AddFieldPaths(self._root, '', field_mask)

    def IntersectPath(self, path, intersection):
        node = self._root
        for name in path.split('.'):
            if name not in node:
                return
            if not node[name]:
                intersection.AddPath(path)
                return
            node = node[name]

        intersection.AddLeafNodes(path, node)

    def AddLeafNodes(self, prefix, node):
        if not node:
            self.AddPath(prefix)
        for name in node:
            child_path = prefix + '.' + name
            self.AddLeafNodes(child_path, node[name])

    def MergeMessage(self, source, destination, replace_message, replace_repeated):
        _MergeMessage(self._root, source, destination, replace_message, replace_repeated)


def _StrConvert(value):
    if not isinstance(value, str):
        return value.encode('utf-8')
    return value


def _MergeMessage(node, source, destination, replace_message, replace_repeated):
    source_descriptor = source.DESCRIPTOR
    for name in node:
        child = node[name]
        field = source_descriptor.fields_by_name[name]
        if field is None:
            raise ValueError("Error: Can't find field {0} in message {1}.".format(name, source_descriptor.full_name))
        if child:
            if field.label == FieldDescriptor.LABEL_REPEATED or field.cpp_type != FieldDescriptor.CPPTYPE_MESSAGE:
                raise ValueError('Error: Field {0} in message {1} is not a singular message field and cannot have sub-fields.'.format(name, source_descriptor.full_name))
            if source.HasField(name):
                _MergeMessage(child, getattr(source, name), getattr(destination, name), replace_message, replace_repeated)
            continue
        if field.label == FieldDescriptor.LABEL_REPEATED:
            if replace_repeated:
                destination.ClearField(_StrConvert(name))
            repeated_source = getattr(source, name)
            repeated_destination = getattr(destination, name)
            repeated_destination.MergeFrom(repeated_source)
        elif field.cpp_type == FieldDescriptor.CPPTYPE_MESSAGE:
            if replace_message:
                destination.ClearField(_StrConvert(name))
            if source.HasField(name):
                getattr(destination, name).MergeFrom(getattr(source, name))
        else:
            setattr(destination, name, getattr(source, name))


def _AddFieldPaths(node, prefix, field_mask):
    if not node and prefix:
        field_mask.paths.append(prefix)
        return
    for name in sorted(node):
        if prefix:
            child_path = prefix + '.' + name
        else:
            child_path = name
        _AddFieldPaths(node[name], child_path, field_mask)


_INT_OR_FLOAT = six.integer_types + (float,)

def _SetStructValue(struct_value, value):
    if value is None:
        struct_value.null_value = 0
    elif isinstance(value, bool):
        struct_value.bool_value = value
    elif isinstance(value, six.string_types):
        struct_value.string_value = value
    elif isinstance(value, _INT_OR_FLOAT):
        struct_value.number_value = value
    elif isinstance(value, (dict, Struct)):
        struct_value.struct_value.Clear()
        struct_value.struct_value.update(value)
    elif isinstance(value, (list, ListValue)):
        struct_value.list_value.Clear()
        struct_value.list_value.extend(value)
    else:
        raise ValueError('Unexpected type')


def _GetStructValue(struct_value):
    which = struct_value.WhichOneof('kind')
    if which == 'struct_value':
        return struct_value.struct_value
    if which == 'null_value':
        return
    if which == 'number_value':
        return struct_value.number_value
    if which == 'string_value':
        return struct_value.string_value
    if which == 'bool_value':
        return struct_value.bool_value
    if which == 'list_value':
        return struct_value.list_value
    if which is None:
        raise ValueError('Value not set')


class Struct(object):
    __slots__ = ()

    def __getitem__(self, key):
        return _GetStructValue(self.fields[key])

    def __contains__(self, item):
        return item in self.fields

    def __setitem__(self, key, value):
        _SetStructValue(self.fields[key], value)

    def __delitem__(self, key):
        del self.fields[key]

    def __len__(self):
        return len(self.fields)

    def __iter__(self):
        return iter(self.fields)

    def keys(self):
        return self.fields.keys()

    def values(self):
        return [ self[key] for key in self ]

    def items(self):
        return [ (key, self[key]) for key in self ]

    def get_or_create_list(self, key):
        if not self.fields[key].HasField('list_value'):
            self.fields[key].list_value.Clear()
        return self.fields[key].list_value

    def get_or_create_struct(self, key):
        if not self.fields[key].HasField('struct_value'):
            self.fields[key].struct_value.Clear()
        return self.fields[key].struct_value

    def update(self, dictionary):
        for key, value in dictionary.items():
            _SetStructValue(self.fields[key], value)


collections_abc.MutableMapping.register(Struct)

class ListValue(object):
    __slots__ = ()

    def __len__(self):
        return len(self.values)

    def append(self, value):
        _SetStructValue(self.values.add(), value)

    def extend(self, elem_seq):
        for value in elem_seq:
            self.append(value)

    def __getitem__(self, index):
        return _GetStructValue(self.values.__getitem__(index))

    def __setitem__(self, index, value):
        _SetStructValue(self.values.__getitem__(index), value)

    def __delitem__(self, key):
        del self.values[key]

    def items(self):
        for i in range(len(self)):
            yield self[i]

    def add_struct(self):
        struct_value = self.values.add().struct_value
        struct_value.Clear()
        return struct_value

    def add_list(self):
        list_value = self.values.add().list_value
        list_value.Clear()
        return list_value


collections_abc.MutableSequence.register(ListValue)
WKTBASES = {'google.protobuf.Any': Any,
 'google.protobuf.Duration': Duration,
 'google.protobuf.FieldMask': FieldMask,
 'google.protobuf.ListValue': ListValue,
 'google.protobuf.Struct': Struct,
 'google.protobuf.Timestamp': Timestamp}
