#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\message.py
__author__ = 'robinson@google.com (Will Robinson)'

class Error(Exception):
    pass


class DecodeError(Error):
    pass


class EncodeError(Error):
    pass


class Message(object):
    __slots__ = []
    DESCRIPTOR = None

    def __deepcopy__(self, memo = None):
        clone = type(self)()
        clone.MergeFrom(self)
        return clone

    def __eq__(self, other_msg):
        raise NotImplementedError

    def __ne__(self, other_msg):
        return not self == other_msg

    def __hash__(self):
        raise TypeError('unhashable object')

    def __str__(self):
        raise NotImplementedError

    def __unicode__(self):
        raise NotImplementedError

    def MergeFrom(self, other_msg):
        raise NotImplementedError

    def CopyFrom(self, other_msg):
        if self is other_msg:
            return
        self.Clear()
        self.MergeFrom(other_msg)

    def Clear(self):
        raise NotImplementedError

    def SetInParent(self):
        raise NotImplementedError

    def IsInitialized(self):
        raise NotImplementedError

    def MergeFromString(self, serialized):
        raise NotImplementedError

    def ParseFromString(self, serialized):
        self.Clear()
        return self.MergeFromString(serialized)

    def SerializeToString(self, **kwargs):
        raise NotImplementedError

    def SerializePartialToString(self, **kwargs):
        raise NotImplementedError

    def ListFields(self):
        raise NotImplementedError

    def HasField(self, field_name):
        raise NotImplementedError

    def ClearField(self, field_name):
        raise NotImplementedError

    def WhichOneof(self, oneof_group):
        raise NotImplementedError

    def HasExtension(self, extension_handle):
        raise NotImplementedError

    def ClearExtension(self, extension_handle):
        raise NotImplementedError

    def UnknownFields(self):
        raise NotImplementedError

    def DiscardUnknownFields(self):
        raise NotImplementedError

    def ByteSize(self):
        raise NotImplementedError

    def _SetListener(self, message_listener):
        raise NotImplementedError

    def __getstate__(self):
        return dict(serialized=self.SerializePartialToString())

    def __setstate__(self, state):
        self.__init__()
        serialized = state['serialized']
        if not isinstance(serialized, bytes):
            serialized = serialized.encode('latin1')
        self.ParseFromString(serialized)

    def __reduce__(self):
        message_descriptor = self.DESCRIPTOR
        if message_descriptor.containing_type is None:
            return (type(self), (), self.__getstate__())
        container = message_descriptor
        return (_InternalConstructMessage, (container.full_name,), self.__getstate__())


def _InternalConstructMessage(full_name):
    from google.protobuf import symbol_database
    return symbol_database.Default().GetSymbol(full_name)()
