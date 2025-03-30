#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\symbol_database.py
from google.protobuf.internal import api_implementation
from google.protobuf import descriptor_pool
from google.protobuf import message_factory

class SymbolDatabase(message_factory.MessageFactory):

    def RegisterMessage(self, message):
        desc = message.DESCRIPTOR
        self._classes[desc] = message
        self.RegisterMessageDescriptor(desc)
        return message

    def RegisterMessageDescriptor(self, message_descriptor):
        if api_implementation.Type() == 'python':
            self.pool._AddDescriptor(message_descriptor)

    def RegisterEnumDescriptor(self, enum_descriptor):
        if api_implementation.Type() == 'python':
            self.pool._AddEnumDescriptor(enum_descriptor)
        return enum_descriptor

    def RegisterServiceDescriptor(self, service_descriptor):
        if api_implementation.Type() == 'python':
            self.pool._AddServiceDescriptor(service_descriptor)

    def RegisterFileDescriptor(self, file_descriptor):
        if api_implementation.Type() == 'python':
            self.pool._InternalAddFileDescriptor(file_descriptor)

    def GetSymbol(self, symbol):
        return self._classes[self.pool.FindMessageTypeByName(symbol)]

    def GetMessages(self, files):

        def _GetAllMessages(desc):
            yield desc
            for msg_desc in desc.nested_types:
                for nested_desc in _GetAllMessages(msg_desc):
                    yield nested_desc

        result = {}
        for file_name in files:
            file_desc = self.pool.FindFileByName(file_name)
            for msg_desc in file_desc.message_types_by_name.values():
                for desc in _GetAllMessages(msg_desc):
                    try:
                        result[desc.full_name] = self._classes[desc]
                    except KeyError:
                        pass

        return result


_DEFAULT = SymbolDatabase(pool=descriptor_pool.Default())

def Default():
    return _DEFAULT
