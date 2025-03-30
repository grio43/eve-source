#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\descriptor_pool.py
__author__ = 'matthewtoia@google.com (Matt Toia)'
import collections
import warnings
from google.protobuf import descriptor
from google.protobuf import descriptor_database
from google.protobuf import text_encoding
_USE_C_DESCRIPTORS = descriptor._USE_C_DESCRIPTORS

def _Deprecated(func):

    def NewFunc(*args, **kwargs):
        warnings.warn('Call to deprecated function %s(). Note: Do add unlinked descriptors to descriptor_pool is wrong. Use Add() or AddSerializedFile() instead.' % func.__name__, category=DeprecationWarning)
        return func(*args, **kwargs)

    NewFunc.__name__ = func.__name__
    NewFunc.__doc__ = func.__doc__
    NewFunc.__dict__.update(func.__dict__)
    return NewFunc


def _NormalizeFullyQualifiedName(name):
    return name.lstrip('.')


def _OptionsOrNone(descriptor_proto):
    if descriptor_proto.HasField('options'):
        return descriptor_proto.options
    else:
        return None


def _IsMessageSetExtension(field):
    return field.is_extension and field.containing_type.has_options and field.containing_type.GetOptions().message_set_wire_format and field.type == descriptor.FieldDescriptor.TYPE_MESSAGE and field.label == descriptor.FieldDescriptor.LABEL_OPTIONAL


class DescriptorPool(object):
    if _USE_C_DESCRIPTORS:

        def __new__(cls, descriptor_db = None):
            return descriptor._message.DescriptorPool(descriptor_db)

    def __init__(self, descriptor_db = None):
        self._internal_db = descriptor_database.DescriptorDatabase()
        self._descriptor_db = descriptor_db
        self._descriptors = {}
        self._enum_descriptors = {}
        self._service_descriptors = {}
        self._file_descriptors = {}
        self._toplevel_extensions = {}
        self._file_desc_by_toplevel_extension = {}
        self._top_enum_values = {}
        self._extensions_by_name = collections.defaultdict(dict)
        self._extensions_by_number = collections.defaultdict(dict)

    def _CheckConflictRegister(self, desc, desc_name, file_name):
        for register, descriptor_type in [(self._descriptors, descriptor.Descriptor),
         (self._enum_descriptors, descriptor.EnumDescriptor),
         (self._service_descriptors, descriptor.ServiceDescriptor),
         (self._toplevel_extensions, descriptor.FieldDescriptor),
         (self._top_enum_values, descriptor.EnumValueDescriptor)]:
            if desc_name in register:
                old_desc = register[desc_name]
                if isinstance(old_desc, descriptor.EnumValueDescriptor):
                    old_file = old_desc.type.file.name
                else:
                    old_file = old_desc.file.name
                if not isinstance(desc, descriptor_type) or old_file != file_name:
                    error_msg = 'Conflict register for file "' + file_name + '": ' + desc_name + ' is already defined in file "' + old_file + '". Please fix the conflict by adding package name on the proto file, or use different name for the duplication.'
                    if isinstance(desc, descriptor.EnumValueDescriptor):
                        error_msg += '\nNote: enum values appear as siblings of the enum type instead of children of it.'
                    raise TypeError(error_msg)
                return

    def Add(self, file_desc_proto):
        self._internal_db.Add(file_desc_proto)

    def AddSerializedFile(self, serialized_file_desc_proto):
        from google.protobuf import descriptor_pb2
        file_desc_proto = descriptor_pb2.FileDescriptorProto.FromString(serialized_file_desc_proto)
        self.Add(file_desc_proto)

    @_Deprecated
    def AddDescriptor(self, desc):
        self._AddDescriptor(desc)

    def _AddDescriptor(self, desc):
        if not isinstance(desc, descriptor.Descriptor):
            raise TypeError('Expected instance of descriptor.Descriptor.')
        self._CheckConflictRegister(desc, desc.full_name, desc.file.name)
        self._descriptors[desc.full_name] = desc
        self._AddFileDescriptor(desc.file)

    @_Deprecated
    def AddEnumDescriptor(self, enum_desc):
        self._AddEnumDescriptor(enum_desc)

    def _AddEnumDescriptor(self, enum_desc):
        if not isinstance(enum_desc, descriptor.EnumDescriptor):
            raise TypeError('Expected instance of descriptor.EnumDescriptor.')
        file_name = enum_desc.file.name
        self._CheckConflictRegister(enum_desc, enum_desc.full_name, file_name)
        self._enum_descriptors[enum_desc.full_name] = enum_desc
        if enum_desc.file.package:
            top_level = enum_desc.full_name.count('.') - enum_desc.file.package.count('.') == 1
        else:
            top_level = enum_desc.full_name.count('.') == 0
        if top_level:
            file_name = enum_desc.file.name
            package = enum_desc.file.package
            for enum_value in enum_desc.values:
                full_name = _NormalizeFullyQualifiedName('.'.join((package, enum_value.name)))
                self._CheckConflictRegister(enum_value, full_name, file_name)
                self._top_enum_values[full_name] = enum_value

        self._AddFileDescriptor(enum_desc.file)

    @_Deprecated
    def AddServiceDescriptor(self, service_desc):
        self._AddServiceDescriptor(service_desc)

    def _AddServiceDescriptor(self, service_desc):
        if not isinstance(service_desc, descriptor.ServiceDescriptor):
            raise TypeError('Expected instance of descriptor.ServiceDescriptor.')
        self._CheckConflictRegister(service_desc, service_desc.full_name, service_desc.file.name)
        self._service_descriptors[service_desc.full_name] = service_desc

    @_Deprecated
    def AddExtensionDescriptor(self, extension):
        self._AddExtensionDescriptor(extension)

    def _AddExtensionDescriptor(self, extension):
        if not (isinstance(extension, descriptor.FieldDescriptor) and extension.is_extension):
            raise TypeError('Expected an extension descriptor.')
        if extension.extension_scope is None:
            self._toplevel_extensions[extension.full_name] = extension
        try:
            existing_desc = self._extensions_by_number[extension.containing_type][extension.number]
        except KeyError:
            pass
        else:
            if extension is not existing_desc:
                raise AssertionError('Extensions "%s" and "%s" both try to extend message type "%s" with field number %d.' % (extension.full_name,
                 existing_desc.full_name,
                 extension.containing_type.full_name,
                 extension.number))

        self._extensions_by_number[extension.containing_type][extension.number] = extension
        self._extensions_by_name[extension.containing_type][extension.full_name] = extension
        if _IsMessageSetExtension(extension):
            self._extensions_by_name[extension.containing_type][extension.message_type.full_name] = extension

    @_Deprecated
    def AddFileDescriptor(self, file_desc):
        self._InternalAddFileDescriptor(file_desc)

    def _InternalAddFileDescriptor(self, file_desc):
        self._AddFileDescriptor(file_desc)
        for extension in file_desc.extensions_by_name.values():
            self._file_desc_by_toplevel_extension[extension.full_name] = file_desc

    def _AddFileDescriptor(self, file_desc):
        if not isinstance(file_desc, descriptor.FileDescriptor):
            raise TypeError('Expected instance of descriptor.FileDescriptor.')
        self._file_descriptors[file_desc.name] = file_desc

    def FindFileByName(self, file_name):
        try:
            return self._file_descriptors[file_name]
        except KeyError:
            pass

        try:
            file_proto = self._internal_db.FindFileByName(file_name)
        except KeyError as error:
            if self._descriptor_db:
                file_proto = self._descriptor_db.FindFileByName(file_name)
            else:
                raise error

        if not file_proto:
            raise KeyError('Cannot find a file named %s' % file_name)
        return self._ConvertFileProtoToFileDescriptor(file_proto)

    def FindFileContainingSymbol(self, symbol):
        symbol = _NormalizeFullyQualifiedName(symbol)
        try:
            return self._InternalFindFileContainingSymbol(symbol)
        except KeyError:
            pass

        try:
            self._FindFileContainingSymbolInDb(symbol)
            return self._InternalFindFileContainingSymbol(symbol)
        except KeyError:
            raise KeyError('Cannot find a file containing %s' % symbol)

    def _InternalFindFileContainingSymbol(self, symbol):
        try:
            return self._descriptors[symbol].file
        except KeyError:
            pass

        try:
            return self._enum_descriptors[symbol].file
        except KeyError:
            pass

        try:
            return self._service_descriptors[symbol].file
        except KeyError:
            pass

        try:
            return self._top_enum_values[symbol].type.file
        except KeyError:
            pass

        try:
            return self._file_desc_by_toplevel_extension[symbol]
        except KeyError:
            pass

        top_name, _, sub_name = symbol.rpartition('.')
        try:
            message = self.FindMessageTypeByName(top_name)
            return message.file
        except (KeyError, AssertionError):
            raise KeyError('Cannot find a file containing %s' % symbol)

    def FindMessageTypeByName(self, full_name):
        full_name = _NormalizeFullyQualifiedName(full_name)
        if full_name not in self._descriptors:
            self._FindFileContainingSymbolInDb(full_name)
        return self._descriptors[full_name]

    def FindEnumTypeByName(self, full_name):
        full_name = _NormalizeFullyQualifiedName(full_name)
        if full_name not in self._enum_descriptors:
            self._FindFileContainingSymbolInDb(full_name)
        return self._enum_descriptors[full_name]

    def FindFieldByName(self, full_name):
        full_name = _NormalizeFullyQualifiedName(full_name)
        message_name, _, field_name = full_name.rpartition('.')
        message_descriptor = self.FindMessageTypeByName(message_name)
        return message_descriptor.fields_by_name[field_name]

    def FindOneofByName(self, full_name):
        full_name = _NormalizeFullyQualifiedName(full_name)
        message_name, _, oneof_name = full_name.rpartition('.')
        message_descriptor = self.FindMessageTypeByName(message_name)
        return message_descriptor.oneofs_by_name[oneof_name]

    def FindExtensionByName(self, full_name):
        full_name = _NormalizeFullyQualifiedName(full_name)
        try:
            return self._toplevel_extensions[full_name]
        except KeyError:
            pass

        message_name, _, extension_name = full_name.rpartition('.')
        try:
            scope = self.FindMessageTypeByName(message_name)
        except KeyError:
            scope = self._FindFileContainingSymbolInDb(full_name)

        return scope.extensions_by_name[extension_name]

    def FindExtensionByNumber(self, message_descriptor, number):
        try:
            return self._extensions_by_number[message_descriptor][number]
        except KeyError:
            self._TryLoadExtensionFromDB(message_descriptor, number)
            return self._extensions_by_number[message_descriptor][number]

    def FindAllExtensions(self, message_descriptor):
        if self._descriptor_db and hasattr(self._descriptor_db, 'FindAllExtensionNumbers'):
            full_name = message_descriptor.full_name
            all_numbers = self._descriptor_db.FindAllExtensionNumbers(full_name)
            for number in all_numbers:
                if number in self._extensions_by_number[message_descriptor]:
                    continue
                self._TryLoadExtensionFromDB(message_descriptor, number)

        return list(self._extensions_by_number[message_descriptor].values())

    def _TryLoadExtensionFromDB(self, message_descriptor, number):
        if not self._descriptor_db:
            return
        if not hasattr(self._descriptor_db, 'FindFileContainingExtension'):
            return
        full_name = message_descriptor.full_name
        file_proto = self._descriptor_db.FindFileContainingExtension(full_name, number)
        if file_proto is None:
            return
        try:
            self._ConvertFileProtoToFileDescriptor(file_proto)
        except:
            warn_msg = 'Unable to load proto file %s for extension number %d.' % (file_proto.name, number)
            warnings.warn(warn_msg, RuntimeWarning)

    def FindServiceByName(self, full_name):
        full_name = _NormalizeFullyQualifiedName(full_name)
        if full_name not in self._service_descriptors:
            self._FindFileContainingSymbolInDb(full_name)
        return self._service_descriptors[full_name]

    def FindMethodByName(self, full_name):
        full_name = _NormalizeFullyQualifiedName(full_name)
        service_name, _, method_name = full_name.rpartition('.')
        service_descriptor = self.FindServiceByName(service_name)
        return service_descriptor.methods_by_name[method_name]

    def _FindFileContainingSymbolInDb(self, symbol):
        try:
            file_proto = self._internal_db.FindFileContainingSymbol(symbol)
        except KeyError as error:
            if self._descriptor_db:
                file_proto = self._descriptor_db.FindFileContainingSymbol(symbol)
            else:
                raise error

        if not file_proto:
            raise KeyError('Cannot find a file containing %s' % symbol)
        return self._ConvertFileProtoToFileDescriptor(file_proto)

    def _ConvertFileProtoToFileDescriptor(self, file_proto):
        if file_proto.name not in self._file_descriptors:
            built_deps = list(self._GetDeps(file_proto.dependency))
            direct_deps = [ self.FindFileByName(n) for n in file_proto.dependency ]
            public_deps = [ direct_deps[i] for i in file_proto.public_dependency ]
            file_descriptor = descriptor.FileDescriptor(pool=self, name=file_proto.name, package=file_proto.package, syntax=file_proto.syntax, options=_OptionsOrNone(file_proto), serialized_pb=file_proto.SerializeToString(), dependencies=direct_deps, public_dependencies=public_deps, create_key=descriptor._internal_create_key)
            scope = {}
            for dependency in built_deps:
                scope.update(self._ExtractSymbols(dependency.message_types_by_name.values()))
                scope.update(((_PrefixWithDot(enum.full_name), enum) for enum in dependency.enum_types_by_name.values()))

            for message_type in file_proto.message_type:
                message_desc = self._ConvertMessageDescriptor(message_type, file_proto.package, file_descriptor, scope, file_proto.syntax)
                file_descriptor.message_types_by_name[message_desc.name] = message_desc

            for enum_type in file_proto.enum_type:
                file_descriptor.enum_types_by_name[enum_type.name] = self._ConvertEnumDescriptor(enum_type, file_proto.package, file_descriptor, None, scope, True)

            for index, extension_proto in enumerate(file_proto.extension):
                extension_desc = self._MakeFieldDescriptor(extension_proto, file_proto.package, index, file_descriptor, is_extension=True)
                extension_desc.containing_type = self._GetTypeFromScope(file_descriptor.package, extension_proto.extendee, scope)
                self._SetFieldType(extension_proto, extension_desc, file_descriptor.package, scope)
                file_descriptor.extensions_by_name[extension_desc.name] = extension_desc
                self._file_desc_by_toplevel_extension[extension_desc.full_name] = file_descriptor

            for desc_proto in file_proto.message_type:
                self._SetAllFieldTypes(file_proto.package, desc_proto, scope)

            if file_proto.package:
                desc_proto_prefix = _PrefixWithDot(file_proto.package)
            else:
                desc_proto_prefix = ''
            for desc_proto in file_proto.message_type:
                desc = self._GetTypeFromScope(desc_proto_prefix, desc_proto.name, scope)
                file_descriptor.message_types_by_name[desc_proto.name] = desc

            for index, service_proto in enumerate(file_proto.service):
                file_descriptor.services_by_name[service_proto.name] = self._MakeServiceDescriptor(service_proto, index, scope, file_proto.package, file_descriptor)

            self.Add(file_proto)
            self._file_descriptors[file_proto.name] = file_descriptor
        file_desc = self._file_descriptors[file_proto.name]
        for extension in file_desc.extensions_by_name.values():
            self._AddExtensionDescriptor(extension)

        for message_type in file_desc.message_types_by_name.values():
            for extension in message_type.extensions:
                self._AddExtensionDescriptor(extension)

        return file_desc

    def _ConvertMessageDescriptor(self, desc_proto, package = None, file_desc = None, scope = None, syntax = None):
        if package:
            desc_name = '.'.join((package, desc_proto.name))
        else:
            desc_name = desc_proto.name
        if file_desc is None:
            file_name = None
        else:
            file_name = file_desc.name
        if scope is None:
            scope = {}
        nested = [ self._ConvertMessageDescriptor(nested, desc_name, file_desc, scope, syntax) for nested in desc_proto.nested_type ]
        enums = [ self._ConvertEnumDescriptor(enum, desc_name, file_desc, None, scope, False) for enum in desc_proto.enum_type ]
        fields = [ self._MakeFieldDescriptor(field, desc_name, index, file_desc) for index, field in enumerate(desc_proto.field) ]
        extensions = [ self._MakeFieldDescriptor(extension, desc_name, index, file_desc, is_extension=True) for index, extension in enumerate(desc_proto.extension) ]
        oneofs = [ descriptor.OneofDescriptor(desc.name, '.'.join((desc_name, desc.name)), index, None, [], desc.options, create_key=descriptor._internal_create_key) for index, desc in enumerate(desc_proto.oneof_decl) ]
        extension_ranges = [ (r.start, r.end) for r in desc_proto.extension_range ]
        if extension_ranges:
            is_extendable = True
        else:
            is_extendable = False
        desc = descriptor.Descriptor(name=desc_proto.name, full_name=desc_name, filename=file_name, containing_type=None, fields=fields, oneofs=oneofs, nested_types=nested, enum_types=enums, extensions=extensions, options=_OptionsOrNone(desc_proto), is_extendable=is_extendable, extension_ranges=extension_ranges, file=file_desc, serialized_start=None, serialized_end=None, syntax=syntax, create_key=descriptor._internal_create_key)
        for nested in desc.nested_types:
            nested.containing_type = desc

        for enum in desc.enum_types:
            enum.containing_type = desc

        for field_index, field_desc in enumerate(desc_proto.field):
            if field_desc.HasField('oneof_index'):
                oneof_index = field_desc.oneof_index
                oneofs[oneof_index].fields.append(fields[field_index])
                fields[field_index].containing_oneof = oneofs[oneof_index]

        scope[_PrefixWithDot(desc_name)] = desc
        self._CheckConflictRegister(desc, desc.full_name, desc.file.name)
        self._descriptors[desc_name] = desc
        return desc

    def _ConvertEnumDescriptor(self, enum_proto, package = None, file_desc = None, containing_type = None, scope = None, top_level = False):
        if package:
            enum_name = '.'.join((package, enum_proto.name))
        else:
            enum_name = enum_proto.name
        if file_desc is None:
            file_name = None
        else:
            file_name = file_desc.name
        values = [ self._MakeEnumValueDescriptor(value, index) for index, value in enumerate(enum_proto.value) ]
        desc = descriptor.EnumDescriptor(name=enum_proto.name, full_name=enum_name, filename=file_name, file=file_desc, values=values, containing_type=containing_type, options=_OptionsOrNone(enum_proto), create_key=descriptor._internal_create_key)
        scope['.%s' % enum_name] = desc
        self._CheckConflictRegister(desc, desc.full_name, desc.file.name)
        self._enum_descriptors[enum_name] = desc
        if top_level:
            for value in values:
                full_name = _NormalizeFullyQualifiedName('.'.join((package, value.name)))
                self._CheckConflictRegister(value, full_name, file_name)
                self._top_enum_values[full_name] = value

        return desc

    def _MakeFieldDescriptor(self, field_proto, message_name, index, file_desc, is_extension = False):
        if message_name:
            full_name = '.'.join((message_name, field_proto.name))
        else:
            full_name = field_proto.name
        return descriptor.FieldDescriptor(name=field_proto.name, full_name=full_name, index=index, number=field_proto.number, type=field_proto.type, cpp_type=None, message_type=None, enum_type=None, containing_type=None, label=field_proto.label, has_default_value=False, default_value=None, is_extension=is_extension, extension_scope=None, options=_OptionsOrNone(field_proto), file=file_desc, create_key=descriptor._internal_create_key)

    def _SetAllFieldTypes(self, package, desc_proto, scope):
        package = _PrefixWithDot(package)
        main_desc = self._GetTypeFromScope(package, desc_proto.name, scope)
        if package == '.':
            nested_package = _PrefixWithDot(desc_proto.name)
        else:
            nested_package = '.'.join([package, desc_proto.name])
        for field_proto, field_desc in zip(desc_proto.field, main_desc.fields):
            self._SetFieldType(field_proto, field_desc, nested_package, scope)

        for extension_proto, extension_desc in zip(desc_proto.extension, main_desc.extensions):
            extension_desc.containing_type = self._GetTypeFromScope(nested_package, extension_proto.extendee, scope)
            self._SetFieldType(extension_proto, extension_desc, nested_package, scope)

        for nested_type in desc_proto.nested_type:
            self._SetAllFieldTypes(nested_package, nested_type, scope)

    def _SetFieldType(self, field_proto, field_desc, package, scope):
        if field_proto.type_name:
            desc = self._GetTypeFromScope(package, field_proto.type_name, scope)
        else:
            desc = None
        if not field_proto.HasField('type'):
            if isinstance(desc, descriptor.Descriptor):
                field_proto.type = descriptor.FieldDescriptor.TYPE_MESSAGE
            else:
                field_proto.type = descriptor.FieldDescriptor.TYPE_ENUM
        field_desc.cpp_type = descriptor.FieldDescriptor.ProtoTypeToCppProtoType(field_proto.type)
        if field_proto.type == descriptor.FieldDescriptor.TYPE_MESSAGE or field_proto.type == descriptor.FieldDescriptor.TYPE_GROUP:
            field_desc.message_type = desc
        if field_proto.type == descriptor.FieldDescriptor.TYPE_ENUM:
            field_desc.enum_type = desc
        if field_proto.label == descriptor.FieldDescriptor.LABEL_REPEATED:
            field_desc.has_default_value = False
            field_desc.default_value = []
        elif field_proto.HasField('default_value'):
            field_desc.has_default_value = True
            if field_proto.type == descriptor.FieldDescriptor.TYPE_DOUBLE or field_proto.type == descriptor.FieldDescriptor.TYPE_FLOAT:
                field_desc.default_value = float(field_proto.default_value)
            elif field_proto.type == descriptor.FieldDescriptor.TYPE_STRING:
                field_desc.default_value = field_proto.default_value
            elif field_proto.type == descriptor.FieldDescriptor.TYPE_BOOL:
                field_desc.default_value = field_proto.default_value.lower() == 'true'
            elif field_proto.type == descriptor.FieldDescriptor.TYPE_ENUM:
                field_desc.default_value = field_desc.enum_type.values_by_name[field_proto.default_value].number
            elif field_proto.type == descriptor.FieldDescriptor.TYPE_BYTES:
                field_desc.default_value = text_encoding.CUnescape(field_proto.default_value)
            elif field_proto.type == descriptor.FieldDescriptor.TYPE_MESSAGE:
                field_desc.default_value = None
            else:
                field_desc.default_value = int(field_proto.default_value)
        else:
            field_desc.has_default_value = False
            if field_proto.type == descriptor.FieldDescriptor.TYPE_DOUBLE or field_proto.type == descriptor.FieldDescriptor.TYPE_FLOAT:
                field_desc.default_value = 0.0
            elif field_proto.type == descriptor.FieldDescriptor.TYPE_STRING:
                field_desc.default_value = u''
            elif field_proto.type == descriptor.FieldDescriptor.TYPE_BOOL:
                field_desc.default_value = False
            elif field_proto.type == descriptor.FieldDescriptor.TYPE_ENUM:
                field_desc.default_value = field_desc.enum_type.values[0].number
            elif field_proto.type == descriptor.FieldDescriptor.TYPE_BYTES:
                field_desc.default_value = ''
            elif field_proto.type == descriptor.FieldDescriptor.TYPE_MESSAGE:
                field_desc.default_value = None
            else:
                field_desc.default_value = 0
        field_desc.type = field_proto.type

    def _MakeEnumValueDescriptor(self, value_proto, index):
        return descriptor.EnumValueDescriptor(name=value_proto.name, index=index, number=value_proto.number, options=_OptionsOrNone(value_proto), type=None, create_key=descriptor._internal_create_key)

    def _MakeServiceDescriptor(self, service_proto, service_index, scope, package, file_desc):
        if package:
            service_name = '.'.join((package, service_proto.name))
        else:
            service_name = service_proto.name
        methods = [ self._MakeMethodDescriptor(method_proto, service_name, package, scope, index) for index, method_proto in enumerate(service_proto.method) ]
        desc = descriptor.ServiceDescriptor(name=service_proto.name, full_name=service_name, index=service_index, methods=methods, options=_OptionsOrNone(service_proto), file=file_desc, create_key=descriptor._internal_create_key)
        self._CheckConflictRegister(desc, desc.full_name, desc.file.name)
        self._service_descriptors[service_name] = desc
        return desc

    def _MakeMethodDescriptor(self, method_proto, service_name, package, scope, index):
        full_name = '.'.join((service_name, method_proto.name))
        input_type = self._GetTypeFromScope(package, method_proto.input_type, scope)
        output_type = self._GetTypeFromScope(package, method_proto.output_type, scope)
        return descriptor.MethodDescriptor(name=method_proto.name, full_name=full_name, index=index, containing_service=None, input_type=input_type, output_type=output_type, options=_OptionsOrNone(method_proto), create_key=descriptor._internal_create_key)

    def _ExtractSymbols(self, descriptors):
        for desc in descriptors:
            yield (_PrefixWithDot(desc.full_name), desc)
            for symbol in self._ExtractSymbols(desc.nested_types):
                yield symbol

            for enum in desc.enum_types:
                yield (_PrefixWithDot(enum.full_name), enum)

    def _GetDeps(self, dependencies):
        for dependency in dependencies:
            dep_desc = self.FindFileByName(dependency)
            yield dep_desc
            for parent_dep in dep_desc.dependencies:
                yield parent_dep

    def _GetTypeFromScope(self, package, type_name, scope):
        if type_name not in scope:
            components = _PrefixWithDot(package).split('.')
            while components:
                possible_match = '.'.join(components + [type_name])
                if possible_match in scope:
                    type_name = possible_match
                    break
                else:
                    components.pop(-1)

        return scope[type_name]


def _PrefixWithDot(name):
    if name.startswith('.'):
        return name
    return '.%s' % name


if _USE_C_DESCRIPTORS:
    _DEFAULT = descriptor._message.default_pool
else:
    _DEFAULT = DescriptorPool()

def Default():
    return _DEFAULT
