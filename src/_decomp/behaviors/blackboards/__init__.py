#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\blackboards\__init__.py
import collections
from behaviors.blackboards.scopes import IsReusableScope
import signals
from ccpProfile import TimedFunction
from eveexceptions.exceptionEater import ExceptionEater
MessageData = collections.namedtuple('MessageData', ['time', 'value'])

class MessageChannel(object):

    def __init__(self, name, getTimeFunc, maxLength = 10):
        self.name = name
        self.messages = collections.deque(maxlen=maxLength)
        self.observerSignal = signals.Signal(signalName='observerSignal')
        self.GetTime = getTimeFunc
        self.resetOnRespawn = True

    def GetHistoryLength(self):
        return self.messages.maxlen

    def ClearAllMessages(self):
        self.messages.clear()
        self.NotifyObservers(None)

    @TimedFunction('behaviors::blackboards::MessageChannel::SendMessage')
    def SendMessage(self, messageValue):
        message = MessageData(self.GetTime(), messageValue)
        self.messages.appendleft(message)
        self.NotifyObservers(message)

    def _GetMaxTime(self, maxAge):
        return self.GetTime() - maxAge

    def _IterMessagesUnderAge(self, maxAge):
        maxTime = self._GetMaxTime(maxAge)
        for m in self.messages:
            if m.time >= maxTime:
                yield m
            else:
                return

    @TimedFunction('behaviors::blackboards::MessageChannel::GetLastMessage')
    def GetLastMessage(self):
        if self.messages:
            return self.messages[0]

    def GetLastMessageWithMaxAge(self, maxAge):
        if self.messages:
            m = self.messages[0]
            if m.time >= self._GetMaxTime(maxAge):
                return m

    def GetLastMessageValue(self):
        message = self.GetLastMessage()
        if message:
            return message.value
        else:
            return None

    def GetLastMessageValueWithMaxAge(self, maxAge):
        message = self.GetLastMessageWithMaxAge(maxAge)
        if message:
            return message.value
        else:
            return None

    @TimedFunction('behaviors::blackboards::MessageChannel::GetMessages')
    def GetMessages(self):
        return list(self.messages)

    def GetMessagesWithMaxAge(self, maxAge):
        return [ m for m in self._IterMessagesUnderAge(maxAge) ]

    @TimedFunction('behaviors::blackboards::MessageChannel::NotifyObservers')
    def NotifyObservers(self, message):
        self.observerSignal(self.name, message)

    def AddObserver(self, observer):
        self.observerSignal.connect(observer)

    def RemoveObserver(self, observer):
        try:
            self.observerSignal.disconnect(observer)
        except ValueError:
            pass

    def RemoveAllObservers(self):
        self.observerSignal.clear()

    def SetChannelResetOnGroupRespawn(self, reset):
        self.resetOnRespawn = reset

    def ShouldResetOnRespawn(self):
        return self.resetOnRespawn


class Blackboard(object):

    def __init__(self, identity, getTimeFunc, maxHistoryLength):
        self.identity = identity
        self.getTimeFunc = getTimeFunc
        self.maxHistoryLength = maxHistoryLength
        self.messageChannelsByName = {}
        self.allObserverSignal = signals.Signal(signalName='allObserverSignal')

    def CreateMessageChannel(self, name, maxHistoryLength):
        if name in self.messageChannelsByName:
            raise MessageChannelAlreadyExistsError()
        channel = MessageChannel(name, self.getTimeFunc, maxHistoryLength)
        channel.AddObserver(self.allObserverSignal)
        self.messageChannelsByName[name] = channel

    def AddMessageObserver(self, messageType, observer):
        channel = self.GetMessageChannel(messageType)
        channel.AddObserver(observer)

    def RemoveMessageObserver(self, messageType, observer):
        channel = self.GetMessageChannel(messageType)
        channel.RemoveObserver(observer)

    def GetMessageChannel(self, name):
        if name not in self.messageChannelsByName:
            self.CreateMessageChannel(name, self.maxHistoryLength)
        return self.messageChannelsByName[name]

    def GetMessageChannelList(self):
        return self.messageChannelsByName.values()

    def SendMessage(self, messageType, messageValue):
        channel = self.GetMessageChannel(messageType)
        channel.SendMessage(messageValue)

    def GetLastMessage(self, messageType):
        channel = self.GetMessageChannel(messageType)
        return channel.GetLastMessage()

    def GetLastMessageWithMaxAge(self, messageType, maxAge):
        channel = self.GetMessageChannel(messageType)
        return channel.GetLastMessageWithMaxAge(maxAge)

    def GetMessages(self, messageType):
        channel = self.GetMessageChannel(messageType)
        return channel.GetMessages()

    def GetMessagesWithMaxAge(self, messageType, maxAge):
        channel = self.GetMessageChannel(messageType)
        return channel.GetMessagesWithMaxAge(maxAge)

    def GetLastMessageValue(self, messageType):
        channel = self.GetMessageChannel(messageType)
        return channel.GetLastMessageValue()

    def GetLastMessageValueWithMaxAge(self, messageType, maxAge):
        channel = self.GetMessageChannel(messageType)
        return channel.GetLastMessageValue(maxAge)

    def GetLastMessageValueForAll(self):
        return {messageType:channel.GetLastMessageValue() for messageType, channel in self.messageChannelsByName.iteritems()}

    def Reset(self):
        for channel in self.messageChannelsByName.values():
            channel.RemoveAllObservers()

        self.allObserverSignal.clear()
        self.messageChannelsByName.clear()

    def ResetOnGroupRespawn(self):
        channelNames = self.messageChannelsByName.keys()
        for channelName in channelNames:
            channel = self.messageChannelsByName[channelName]
            if channel.ShouldResetOnRespawn():
                channel.RemoveAllObservers()
                channel.ClearAllMessages()

        for channel in self.messageChannelsByName.itervalues():
            channel.AddObserver(self.allObserverSignal)


class BlackboardManager:

    def __init__(self, getTimeFunc, maxHistoryLength):
        self.blackboardsById = {}
        self.maxHistoryLength = maxHistoryLength
        self.getTimeFunc = getTimeFunc
        self.removedBlackboards = set()

    def CreateBlackboard(self, blackboardId, maxHistoryLength):
        if blackboardId in self.blackboardsById:
            raise BlackboardAlreadyExistsError()
        if not IsReusableScope(blackboardId) and blackboardId in self.removedBlackboards:
            raise BlackboardDeletedError()
        bb = Blackboard(blackboardId, self.getTimeFunc, maxHistoryLength)
        self.blackboardsById[blackboardId] = bb

    def GetBlackboard(self, blackboardId):
        if blackboardId not in self.blackboardsById:
            self.CreateBlackboard(blackboardId, self.maxHistoryLength)
        return self.blackboardsById[blackboardId]

    def RemoveBlackboard(self, blackboardId):
        if blackboardId in self.blackboardsById:
            blackboard = self.blackboardsById.pop(blackboardId)
            blackboard.Reset()
            if not IsReusableScope(blackboardId):
                self.removedBlackboards.add(blackboardId)

    def HasBlackboard(self, blackboardId):
        return blackboardId in self.blackboardsById

    def GetMessageChannel(self, blackboardId, messageType):
        return self.GetBlackboard(blackboardId).GetMessageChannel(messageType)

    def CleanUp(self):
        with ExceptionEater('cleaning up'):
            for blackboard in self.blackboardsById.values():
                blackboard.Reset()

            self.blackboardsById.clear()

    def GetBlackboardCount(self):
        return len(self.blackboardsById)


class MessageChannelAlreadyExistsError(Exception):
    pass


class BlackboardAlreadyExistsError(Exception):
    pass


class BlackboardDeletedError(Exception):
    pass
