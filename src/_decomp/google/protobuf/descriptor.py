#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\descriptor.py
__author__ = 'robinson@google.com (Will Robinson)'
import threading
import warnings
import six
from google.protobuf.internal import api_implementation
_USE_C_DESCRIPTORS = False
if api_implementation.Type() == 'cpp':
    import binascii
    import os
    from google.protobuf.pyext import _message
    _USE_C_DESCRIPTORS = True

class Error(Exception):
    pass


class TypeTransformationError(Error):
    pass


if _USE_C_DESCRIPTORS:

    class DescriptorMetaclass(type):

        def __instancecheck__(cls, obj):
            if super(DescriptorMetaclass, cls).__instancecheck__(obj):
                return True
            if isinstance(obj, cls._C_DESCRIPTOR_CLASS):
                return True
            return False


else:
    DescriptorMetaclass = type

class _Lock(object):

    def __new__(cls):
        self = object.__new__(cls)
        self._lock = threading.Lock()
        return self

    def __enter__(self):
        self._lock.acquire()

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._lock.release()


_lock = threading.Lock()

def _Deprecated(name):
    if _Deprecated.count > 0:
        _Deprecated.count -= 1
        warnings.warn('Call to deprecated create function %s(). Note: Create unlinked descriptors is going to go away. Please use get/find descriptors from generated code or query the descriptor_pool.' % name, category=DeprecationWarning, stacklevel=3)


_Deprecated.count = 100
_internal_create_key = object()

class DescriptorBase(six.with_metaclass(DescriptorMetaclass)):
    if _USE_C_DESCRIPTORS:
        _C_DESCRIPTOR_CLASS = ()

    def __init__(self, options, serialized_options, options_class_name):
        self._options = options
        self._options_class_name = options_class_name
        self._serialized_options = serialized_options
        self.has_options = options is not None or serialized_options is not None

    def _SetOptions(self, options, options_class_name):
        self._options = options
        self._options_class_name = options_class_name
        self.has_options = options is not None

    def GetOptions(self):
        if self._options:
            return self._options
        from google.protobuf import descriptor_pb2
        try:
            options_class = getattr(descriptor_pb2, self._options_class_name)
        except AttributeError:
            raise RuntimeError('Unknown options class name %s!' % self._options_class_name)

        with _lock:
            if self._serialized_options is None:
                self._options = options_class()
            else:
                self._options = _ParseOptions(options_class(), self._serialized_options)
            return self._options


class _NestedDescriptorBase(DescriptorBase):

    def __init__(self, options, options_class_name, name, full_name, file, containing_type, serialized_start = None, serialized_end = None, serialized_options = None):
        super(_NestedDescriptorBase, self).__init__(options, serialized_options, options_class_name)
        self.name = name
        self.full_name = full_name
        self.file = file
        self.containing_type = containing_type
        self._serialized_start = serialized_start
        self._serialized_end = serialized_end

    def CopyToProto(self, proto):
        if self.file is not None and self._serialized_start is not None and self._serialized_end is not None:
            proto.ParseFromString(self.file.serialized_pb[self._serialized_start:self._serialized_end])
        else:
            raise Error('Descriptor does not contain serialization.')


class Descriptor(_NestedDescriptorBase):
    if _USE_C_DESCRIPTORS:
        _C_DESCRIPTOR_CLASS = _message.Descriptor

        def __new__(cls, name = None, full_name = None, filename = None, containing_type = None, fields = None, nested_types = None, enum_types = None, extensions = None, options = None, serialized_options = None, is_extendable = True, extension_ranges = None, oneofs = None, file = None, serialized_start = None, serialized_end = None, syntax = None, create_key = None):
            _message.Message._CheckCalledFromGeneratedFile()
            return _message.default_pool.FindMessageTypeByName(full_name)

    def __init__(self, name, full_name, filename, containing_type, fields, nested_types, enum_types, extensions, options = None, serialized_options = None, is_extendable = True, extension_ranges = None, oneofs = None, file = None, serialized_start = None, serialized_end = None, syntax = None, create_key = None):
        if create_key is not _internal_create_key:
            _Deprecated('Descriptor')
        super(Descriptor, self).__init__(options, 'MessageOptions', name, full_name, file, containing_type, serialized_start=serialized_start, serialized_end=serialized_end, serialized_options=serialized_options)
        self.fields = fields
        for field in self.fields:
            field.containing_type = self

        self.fields_by_number = dict(((f.number, f) for f in fields))
        self.fields_by_name = dict(((f.name, f) for f in fields))
        self._fields_by_camelcase_name = None
        self.nested_types = nested_types
        for nested_type in nested_types:
            nested_type.containing_type = self

        self.nested_types_by_name = dict(((t.name, t) for t in nested_types))
        self.enum_types = enum_types
        for enum_type in self.enum_types:
            enum_type.containing_type = self

        self.enum_types_by_name = dict(((t.name, t) for t in enum_types))
        self.enum_values_by_name = dict(((v.name, v) for t in enum_types for v in t.values))
        self.extensions = extensions
        for extension in self.extensions:
            extension.extension_scope = self

        self.extensions_by_name = dict(((f.name, f) for f in extensions))
        self.is_extendable = is_extendable
        self.extension_ranges = extension_ranges
        self.oneofs = oneofs if oneofs is not None else []
        self.oneofs_by_name = dict(((o.name, o) for o in self.oneofs))
        for oneof in self.oneofs:
            oneof.containing_type = self

        self.syntax = syntax or 'proto2'

    @property
    def fields_by_camelcase_name(self):
        if self._fields_by_camelcase_name is None:
            self._fields_by_camelcase_name = dict(((f.camelcase_name, f) for f in self.fields))
        return self._fields_by_camelcase_name

    def EnumValueName(self, enum, value):
        return self.enum_types_by_name[enum].values_by_number[value].name

    def CopyToProto(self, proto):
        super(Descriptor, self).CopyToProto(proto)


class FieldDescriptor(DescriptorBase):
    TYPE_DOUBLE = 1
    TYPE_FLOAT = 2
    TYPE_INT64 = 3
    TYPE_UINT64 = 4
    TYPE_INT32 = 5
    TYPE_FIXED64 = 6
    TYPE_FIXED32 = 7
    TYPE_BOOL = 8
    TYPE_STRING = 9
    TYPE_GROUP = 10
    TYPE_MESSAGE = 11
    TYPE_BYTES = 12
    TYPE_UINT32 = 13
    TYPE_ENUM = 14
    TYPE_SFIXED32 = 15
    TYPE_SFIXED64 = 16
    TYPE_SINT32 = 17
    TYPE_SINT64 = 18
    MAX_TYPE = 18
    CPPTYPE_INT32 = 1
    CPPTYPE_INT64 = 2
    CPPTYPE_UINT32 = 3
    CPPTYPE_UINT64 = 4
    CPPTYPE_DOUBLE = 5
    CPPTYPE_FLOAT = 6
    CPPTYPE_BOOL = 7
    CPPTYPE_ENUM = 8
    CPPTYPE_STRING = 9
    CPPTYPE_MESSAGE = 10
    MAX_CPPTYPE = 10
    _PYTHON_TO_CPP_PROTO_TYPE_MAP = {TYPE_DOUBLE: CPPTYPE_DOUBLE,
     TYPE_FLOAT: CPPTYPE_FLOAT,
     TYPE_ENUM: CPPTYPE_ENUM,
     TYPE_INT64: CPPTYPE_INT64,
     TYPE_SINT64: CPPTYPE_INT64,
     TYPE_SFIXED64: CPPTYPE_INT64,
     TYPE_UINT64: CPPTYPE_UINT64,
     TYPE_FIXED64: CPPTYPE_UINT64,
     TYPE_INT32: CPPTYPE_INT32,
     TYPE_SFIXED32: CPPTYPE_INT32,
     TYPE_SINT32: CPPTYPE_INT32,
     TYPE_UINT32: CPPTYPE_UINT32,
     TYPE_FIXED32: CPPTYPE_UINT32,
     TYPE_BYTES: CPPTYPE_STRING,
     TYPE_STRING: CPPTYPE_STRING,
     TYPE_BOOL: CPPTYPE_BOOL,
     TYPE_MESSAGE: CPPTYPE_MESSAGE,
     TYPE_GROUP: CPPTYPE_MESSAGE}
    LABEL_OPTIONAL = 1
    LABEL_REQUIRED = 2
    LABEL_REPEATED = 3
    MAX_LABEL = 3
    MAX_FIELD_NUMBER = 536870911
    FIRST_RESERVED_FIELD_NUMBER = 19000
    LAST_RESERVED_FIELD_NUMBER = 19999
    if _USE_C_DESCRIPTORS:
        _C_DESCRIPTOR_CLASS = _message.FieldDescriptor

        def __new__(cls, name, full_name, index, number, type, cpp_type, label, default_value, message_type, enum_type, containing_type, is_extension, extension_scope, options = None, serialized_options = None, has_default_value = True, containing_oneof = None, json_name = None, file = None, create_key = None):
            _message.Message._CheckCalledFromGeneratedFile()
            if is_extension:
                return _message.default_pool.FindExtensionByName(full_name)
            else:
                return _message.default_pool.FindFieldByName(full_name)

    def __init__(self, name, full_name, index, number, type, cpp_type, label, default_value, message_type, enum_type, containing_type, is_extension, extension_scope, options = None, serialized_options = None, has_default_value = True, containing_oneof = None, json_name = None, file = None, create_key = None):
        if create_key is not _internal_create_key:
            _Deprecated('FieldDescriptor')
        super(FieldDescriptor, self).__init__(options, serialized_options, 'FieldOptions')
        self.name = name
        self.full_name = full_name
        self.file = file
        self._camelcase_name = None
        if json_name is None:
            self.json_name = _ToJsonName(name)
        else:
            self.json_name = json_name
        self.index = index
        self.number = number
        self.type = type
        self.cpp_type = cpp_type
        self.label = label
        self.has_default_value = has_default_value
        self.default_value = default_value
        self.containing_type = containing_type
        self.message_type = message_type
        self.enum_type = enum_type
        self.is_extension = is_extension
        self.extension_scope = extension_scope
        self.containing_oneof = containing_oneof
        if api_implementation.Type() == 'cpp':
            if is_extension:
                self._cdescriptor = _message.default_pool.FindExtensionByName(full_name)
            else:
                self._cdescriptor = _message.default_pool.FindFieldByName(full_name)
        else:
            self._cdescriptor = None

    @property
    def camelcase_name(self):
        if self._camelcase_name is None:
            self._camelcase_name = _ToCamelCase(self.name)
        return self._camelcase_name

    @staticmethod
    def ProtoTypeToCppProtoType(proto_type):
        try:
            return FieldDescriptor._PYTHON_TO_CPP_PROTO_TYPE_MAP[proto_type]
        except KeyError:
            raise TypeTransformationError('Unknown proto_type: %s' % proto_type)


class EnumDescriptor(_NestedDescriptorBase):
    if _USE_C_DESCRIPTORS:
        _C_DESCRIPTOR_CLASS = _message.EnumDescriptor

        def __new__(cls, name, full_name, filename, values, containing_type = None, options = None, serialized_options = None, file = None, serialized_start = None, serialized_end = None, create_key = None):
            _message.Message._CheckCalledFromGeneratedFile()
            return _message.default_pool.FindEnumTypeByName(full_name)

    def __init__(self, name, full_name, filename, values, containing_type = None, options = None, serialized_options = None, file = None, serialized_start = None, serialized_end = None, create_key = None):
        if create_key is not _internal_create_key:
            _Deprecated('EnumDescriptor')
        super(EnumDescriptor, self).__init__(options, 'EnumOptions', name, full_name, file, containing_type, serialized_start=serialized_start, serialized_end=serialized_end, serialized_options=serialized_options)
        self.values = values
        for value in self.values:
            value.type = self

        self.values_by_name = dict(((v.name, v) for v in values))
        self.values_by_number = dict(((v.number, v) for v in reversed(values)))

    def CopyToProto(self, proto):
        super(EnumDescriptor, self).CopyToProto(proto)


class EnumValueDescriptor(DescriptorBase):
    if _USE_C_DESCRIPTORS:
        _C_DESCRIPTOR_CLASS = _message.EnumValueDescriptor

        def __new__(cls, name, index, number, type = None, options = None, serialized_options = None, create_key = None):
            _message.Message._CheckCalledFromGeneratedFile()

    def __init__(self, name, index, number, type = None, options = None, serialized_options = None, create_key = None):
        if create_key is not _internal_create_key:
            _Deprecated('EnumValueDescriptor')
        super(EnumValueDescriptor, self).__init__(options, serialized_options, 'EnumValueOptions')
        self.name = name
        self.index = index
        self.number = number
        self.type = type


class OneofDescriptor(DescriptorBase):
    if _USE_C_DESCRIPTORS:
        _C_DESCRIPTOR_CLASS = _message.OneofDescriptor

        def __new__(cls, name, full_name, index, containing_type, fields, options = None, serialized_options = None, create_key = None):
            _message.Message._CheckCalledFromGeneratedFile()
            return _message.default_pool.FindOneofByName(full_name)

    def __init__(self, name, full_name, index, containing_type, fields, options = None, serialized_options = None, create_key = None):
        if create_key is not _internal_create_key:
            _Deprecated('OneofDescriptor')
        super(OneofDescriptor, self).__init__(options, serialized_options, 'OneofOptions')
        self.name = name
        self.full_name = full_name
        self.index = index
        self.containing_type = containing_type
        self.fields = fields


class ServiceDescriptor(_NestedDescriptorBase):
    if _USE_C_DESCRIPTORS:
        _C_DESCRIPTOR_CLASS = _message.ServiceDescriptor

        def __new__(cls, name = None, full_name = None, index = None, methods = None, options = None, serialized_options = None, file = None, serialized_start = None, serialized_end = None, create_key = None):
            _message.Message._CheckCalledFromGeneratedFile()
            return _message.default_pool.FindServiceByName(full_name)

    def __init__(self, name, full_name, index, methods, options = None, serialized_options = None, file = None, serialized_start = None, serialized_end = None, create_key = None):
        if create_key is not _internal_create_key:
            _Deprecated('ServiceDescriptor')
        super(ServiceDescriptor, self).__init__(options, 'ServiceOptions', name, full_name, file, None, serialized_start=serialized_start, serialized_end=serialized_end, serialized_options=serialized_options)
        self.index = index
        self.methods = methods
        self.methods_by_name = dict(((m.name, m) for m in methods))
        for method in self.methods:
            method.containing_service = self

    def FindMethodByName(self, name):
        return self.methods_by_name.get(name, None)

    def CopyToProto(self, proto):
        super(ServiceDescriptor, self).CopyToProto(proto)


class MethodDescriptor(DescriptorBase):
    if _USE_C_DESCRIPTORS:
        _C_DESCRIPTOR_CLASS = _message.MethodDescriptor

        def __new__(cls, name, full_name, index, containing_service, input_type, output_type, options = None, serialized_options = None, create_key = None):
            _message.Message._CheckCalledFromGeneratedFile()
            return _message.default_pool.FindMethodByName(full_name)

    def __init__(self, name, full_name, index, containing_service, input_type, output_type, options = None, serialized_options = None, create_key = None):
        if create_key is not _internal_create_key:
            _Deprecated('MethodDescriptor')
        super(MethodDescriptor, self).__init__(options, serialized_options, 'MethodOptions')
        self.name = name
        self.full_name = full_name
        self.index = index
        self.containing_service = containing_service
        self.input_type = input_type
        self.output_type = output_type

    def CopyToProto(self, proto):
        if self.containing_service is not None:
            from google.protobuf import descriptor_pb2
            service_proto = descriptor_pb2.ServiceDescriptorProto()
            self.containing_service.CopyToProto(service_proto)
            proto.CopyFrom(service_proto.method[self.index])
        else:
            raise Error('Descriptor does not contain a service.')


class FileDescriptor(DescriptorBase):
    if _USE_C_DESCRIPTORS:
        _C_DESCRIPTOR_CLASS = _message.FileDescriptor

        def __new__(cls, name, package, options = None, serialized_options = None, serialized_pb = None, dependencies = None, public_dependencies = None, syntax = None, pool = None, create_key = None):
            if serialized_pb == '':
                try:
                    return _message.default_pool.FindFileByName(name)
                except KeyError:
                    raise RuntimeError('Please link in cpp generated lib for %s' % name)

            else:
                if serialized_pb:
                    return _message.default_pool.AddSerializedFile(serialized_pb)
                return super(FileDescriptor, cls).__new__(cls)

    def __init__(self, name, package, options = None, serialized_options = None, serialized_pb = None, dependencies = None, public_dependencies = None, syntax = None, pool = None, create_key = None):
        if create_key is not _internal_create_key:
            _Deprecated('FileDescriptor')
        super(FileDescriptor, self).__init__(options, serialized_options, 'FileOptions')
        if pool is None:
            from google.protobuf import descriptor_pool
            pool = descriptor_pool.Default()
        self.pool = pool
        self.message_types_by_name = {}
        self.name = name
        self.package = package
        self.syntax = syntax or 'proto2'
        self.serialized_pb = serialized_pb
        self.enum_types_by_name = {}
        self.extensions_by_name = {}
        self.services_by_name = {}
        self.dependencies = dependencies or []
        self.public_dependencies = public_dependencies or []

    def CopyToProto(self, proto):
        proto.ParseFromString(self.serialized_pb)


def _ParseOptions(message, string):
    message.ParseFromString(string)
    return message


def _ToCamelCase(name):
    capitalize_next = False
    result = []
    for c in name:
        if c == '_':
            if result:
                capitalize_next = True
        elif capitalize_next:
            result.append(c.upper())
            capitalize_next = False
        else:
            result += c

    if result and result[0].isupper():
        result[0] = result[0].lower()
    return ''.join(result)


def _OptionsOrNone(descriptor_proto):
    if descriptor_proto.HasField('options'):
        return descriptor_proto.options
    else:
        return None


def _ToJsonName(name):
    capitalize_next = False
    result = []
    for c in name:
        if c == '_':
            capitalize_next = True
        elif capitalize_next:
            result.append(c.upper())
            capitalize_next = False
        else:
            result += c

    return ''.join(result)


def MakeDescriptor(desc_proto, package = '', build_file_if_cpp = True, syntax = None):
    if api_implementation.Type() == 'cpp' and build_file_if_cpp:
        from google.protobuf import descriptor_pb2
        file_descriptor_proto = descriptor_pb2.FileDescriptorProto()
        file_descriptor_proto.message_type.add().MergeFrom(desc_proto)
        proto_name = binascii.hexlify(os.urandom(16)).decode('ascii')
        if package:
            file_descriptor_proto.name = os.path.join(package.replace('.', '/'), proto_name + '.proto')
            file_descriptor_proto.package = package
        else:
            file_descriptor_proto.name = proto_name + '.proto'
        _message.default_pool.Add(file_descriptor_proto)
        result = _message.default_pool.FindFileByName(file_descriptor_proto.name)
        if _USE_C_DESCRIPTORS:
            return result.message_types_by_name[desc_proto.name]
    full_message_name = [desc_proto.name]
    if package:
        full_message_name.insert(0, package)
    enum_types = {}
    for enum_proto in desc_proto.enum_type:
        full_name = '.'.join(full_message_name + [enum_proto.name])
        enum_desc = EnumDescriptor(enum_proto.name, full_name, None, [ EnumValueDescriptor(enum_val.name, ii, enum_val.number, create_key=_internal_create_key) for ii, enum_val in enumerate(enum_proto.value) ], create_key=_internal_create_key)
        enum_types[full_name] = enum_desc

    nested_types = {}
    for nested_proto in desc_proto.nested_type:
        full_name = '.'.join(full_message_name + [nested_proto.name])
        nested_desc = MakeDescriptor(nested_proto, package='.'.join(full_message_name), build_file_if_cpp=False, syntax=syntax)
        nested_types[full_name] = nested_desc

    fields = []
    for field_proto in desc_proto.field:
        full_name = '.'.join(full_message_name + [field_proto.name])
        enum_desc = None
        nested_desc = None
        if field_proto.json_name:
            json_name = field_proto.json_name
        else:
            json_name = None
        if field_proto.HasField('type_name'):
            type_name = field_proto.type_name
            full_type_name = '.'.join(full_message_name + [type_name[type_name.rfind('.') + 1:]])
            if full_type_name in nested_types:
                nested_desc = nested_types[full_type_name]
            elif full_type_name in enum_types:
                enum_desc = enum_types[full_type_name]
        field = FieldDescriptor(field_proto.name, full_name, field_proto.number - 1, field_proto.number, field_proto.type, FieldDescriptor.ProtoTypeToCppProtoType(field_proto.type), field_proto.label, None, nested_desc, enum_desc, None, False, None, options=_OptionsOrNone(field_proto), has_default_value=False, json_name=json_name, create_key=_internal_create_key)
        fields.append(field)

    desc_name = '.'.join(full_message_name)
    return Descriptor(desc_proto.name, desc_name, None, None, fields, list(nested_types.values()), list(enum_types.values()), [], options=_OptionsOrNone(desc_proto), create_key=_internal_create_key)
