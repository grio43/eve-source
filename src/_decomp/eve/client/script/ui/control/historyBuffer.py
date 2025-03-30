#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\historyBuffer.py
import collections
import blue

class HistoryBuffer:

    def __init__(self, maxLen = None):
        self.maxLen = maxLen
        self.Reset()

    def Reset(self):
        self.deque = collections.deque(maxlen=self.maxLen)
        self.idx = None

    def Append(self, data):
        if len(self.deque) and self.idx is not None:
            self.deque = collections.deque(list(self.deque)[:self.idx + 1], maxlen=self.maxLen)
        if self.ShouldAppend(data):
            self.deque.append(data)
        self.idx = len(self.deque) - 1

    def ShouldAppend(self, data):
        if not len(self.deque):
            return True
        try:
            if data != self.deque[-1]:
                return True
        except TypeError:
            return True

    def GoBack(self):
        if self.IsBackEnabled():
            self.idx -= 1
            return self.GetCurrent()

    def GetPrevious(self):
        if self.IsBackEnabled():
            return self.deque[self.idx - 1]

    def GetNext(self):
        if self.IsForwardEnabled():
            return self.deque[self.idx + 1]

    def GoForward(self):
        if self.IsForwardEnabled():
            self.idx += 1
            return self.GetCurrent()

    def GetCurrent(self):
        return self.deque[self.idx]

    def IsBackEnabled(self):
        return len(self.deque) > 1 and self.idx > 0

    def IsForwardEnabled(self):
        return len(self.deque) > 1 and self.idx < len(self.deque) - 1

    def UpdateCurrent(self, value):
        self.deque[self.idx] = value

    def IsEmpty(self):
        return len(self.deque) == 0
