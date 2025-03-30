#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\message_factory.py
__author__ = 'matthewtoia@google.com (Matt Toia)'
from google.protobuf.internal import api_implementation
from google.protobuf import descriptor_pool
from google.protobuf import message
if api_implementation.Type() == 'cpp':
    from google.protobuf.pyext import cpp_message as message_impl
else:
    from google.protobuf.internal import python_message as message_impl
_GENERATED_PROTOCOL_MESSAGE_TYPE = message_impl.GeneratedProtocolMessageType

class MessageFactory(object):

    def __init__(self, pool = None):
        self.pool = pool or descriptor_pool.DescriptorPool()
        self._classes = {}

    def GetPrototype(self, descriptor):
        if descriptor not in self._classes:
            result_class = self.CreatePrototype(descriptor)
            self._classes[descriptor] = result_class
            return result_class
        return self._classes[descriptor]

    def CreatePrototype(self, descriptor):
        descriptor_name = descriptor.name
        if str is bytes:
            descriptor_name = descriptor.name.encode('ascii', 'ignore')
        result_class = _GENERATED_PROTOCOL_MESSAGE_TYPE(descriptor_name, (message.Message,), {'DESCRIPTOR': descriptor,
         '__module__': None})
        result_class._FACTORY = self
        self._classes[descriptor] = result_class
        for field in descriptor.fields:
            if field.message_type:
                self.GetPrototype(field.message_type)

        for extension in result_class.DESCRIPTOR.extensions:
            if extension.containing_type not in self._classes:
                self.GetPrototype(extension.containing_type)
            extended_class = self._classes[extension.containing_type]
            extended_class.RegisterExtension(extension)

        return result_class

    def GetMessages(self, files):
        result = {}
        for file_name in files:
            file_desc = self.pool.FindFileByName(file_name)
            for desc in file_desc.message_types_by_name.values():
                result[desc.full_name] = self.GetPrototype(desc)

            for extension in file_desc.extensions_by_name.values():
                if extension.containing_type not in self._classes:
                    self.GetPrototype(extension.containing_type)
                extended_class = self._classes[extension.containing_type]
                extended_class.RegisterExtension(extension)

        return result


_FACTORY = MessageFactory()

def GetMessages(file_protos):
    file_by_name = {file_proto.name:file_proto for file_proto in file_protos}

    def _AddFile(file_proto):
        for dependency in file_proto.dependency:
            if dependency in file_by_name:
                _AddFile(file_by_name.pop(dependency))

        _FACTORY.pool.Add(file_proto)

    while file_by_name:
        _AddFile(file_by_name.popitem()[1])

    return _FACTORY.GetMessages([ file_proto.name for file_proto in file_protos ])
