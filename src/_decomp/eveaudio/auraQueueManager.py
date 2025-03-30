#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\auraQueueManager.py
from collections import deque

class AuraQueueManager(object):

    def __init__(self, sendEventWithCallbackFunc):
        self.messageQueue = deque()
        self.isPlaying = False
        self.sendEventWithCallbackFunc = sendEventWithCallbackFunc

    def GetNumWaitingEvents(self):
        return len(self.messageQueue)

    def IsPlaying(self):
        return self.isPlaying

    def QueueIsEmpty(self):
        return self.GetNumWaitingEvents() == 0

    def AddMessage(self, message):
        if len(self.messageQueue) == 0:
            self.sendEventWithCallbackFunc(message)
        self.isPlaying = True
        if self.messageQueue.count(message) == 0:
            self.messageQueue.append(message)

    def QueueCallbackHandler(self, message):
        if self.QueueIsEmpty() or message != self.messageQueue[0]:
            return
        playing = self.messageQueue.popleft()
        if playing == message and self.GetNumWaitingEvents() > 0:
            nextMessage = self.messageQueue[0]
            self.sendEventWithCallbackFunc(nextMessage)
        else:
            self.isPlaying = False
