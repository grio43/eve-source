#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\internal\message_listener.py
__author__ = 'robinson@google.com (Will Robinson)'

class MessageListener(object):

    def Modified(self):
        raise NotImplementedError


class NullMessageListener(object):

    def Modified(self):
        pass
