#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\reflection.py
__author__ = 'robinson@google.com (Will Robinson)'
from google.protobuf import message_factory
from google.protobuf import symbol_database
GeneratedProtocolMessageType = message_factory._GENERATED_PROTOCOL_MESSAGE_TYPE
MESSAGE_CLASS_CACHE = {}

def ParseMessage(descriptor, byte_str):
    result_class = MakeClass(descriptor)
    new_msg = result_class()
    new_msg.ParseFromString(byte_str)
    return new_msg


def MakeClass(descriptor):
    return symbol_database.Default().GetPrototype(descriptor)
