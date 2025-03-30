#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\module_state.py


class ChannelState(object):
    NONE = -1
    IDLE = 0
    CONNECTING = 1
    READY = 2
    TRANSIENT_FAILURE = 3
    SHUTDOWN = 4


class PublisherState(object):
    NONE = -1
    UNKNOWN = 0
    CONNECTING = 1
    ACTIVE = 2
    SHUTDOWN = 3


class ConsumerState(object):
    NONE = -1
    UNKNOWN = 0
    CONNECTING = 1
    ACTIVE = 2
    SHUTDOWN = 3


class BrokerState(object):
    NONE = -1
    UNKNOWN = 0
    CONNECTING = 1
    ACTIVE = 2
    SHUTDOWN = 3
