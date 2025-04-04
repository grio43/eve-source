#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\controls\stackFader.py
from carbonui.uicore import uicore
__author__ = 'aevar'
from eve.common.script.util.notificationconst import MIN_FADE_DELAY_SECONDS
from notifications.client.controls.autoCloser import AutoCloser

class StackFader(object):

    def __init__(self, container, startPosition, audioCallback, down = False, maxStackSize = 3, stackTimeSeconds = 3):
        self.maxStacked = maxStackSize
        self.slotHeight = 55
        self.slotSpacing = 5
        self.showingStack = []
        self.overFlowStack = []
        self.stackTimeSeconds = stackTimeSeconds
        self.baseContainer = container
        self.audioCallback = audioCallback
        self.SetAnchorPosition(startPosition)
        self.autoClosers = []
        self._directionModifier = 1 if down else -1

    def SetStackTimeSeconds(self, second):
        self.stackTimeSeconds = second

    def SetStackSize(self, size):
        self.maxStacked = size

    def SetAnchorPosition(self, position):
        self.startItemPosition = position

    def PushDisplayedItems(self):
        yOffset = self.startItemPosition[1]
        for item in self.showingStack:
            if self._directionModifier == -1:
                yOffset -= self.slotSpacing + item.height
            else:
                yOffset += self.slotSpacing
            self.AnimateMoveItem(item, yOffset)
            if self._directionModifier == 1:
                yOffset += item.height

    def AnimateMoveItem(self, item, endYPosition):
        uicore.animations.MoveTo(item, startPos=(item.left, item.top), endPos=(item.left, endYPosition), duration=0.5, loops=1, curveType=2, callback=self.MoveAnimationFinished, sleep=False, timeOffset=0.0, curveSet=None)

    def MoveAnimationFinished(self, *args):
        pass

    def ShowThisItem(self, item):
        self.audioCallback('notify_beep3_play')
        item.left = self.startItemPosition[0]
        item.top = self.startItemPosition[1]
        if self._directionModifier == -1:
            item.top -= item.height + self.slotSpacing
        else:
            item.top += self.slotSpacing
        item.Blink()
        self.showingStack.insert(0, item)
        self.baseContainer.children.append(item)
        self.PushDisplayedItems()
        closer = AutoCloser(area=None, closeCallback=self.OnItemAutoClosed, monitorObject=item, thresholdInSeconds=self.GetFadeDelaySeconds(item))
        closer.monitor()
        self.autoClosers.insert(0, closer)

    def GetFadeDelaySeconds(self, item):
        notificationTypeID = item.notification.typeID
        if notificationTypeID in MIN_FADE_DELAY_SECONDS:
            return max(self.stackTimeSeconds, MIN_FADE_DELAY_SECONDS[notificationTypeID])
        return self.stackTimeSeconds

    def OnItemAutoClosed(self, closer):
        idx = self.autoClosers.index(closer)
        item = self.showingStack[idx]
        uicore.animations.FadeOut(item, duration=0.5, callback=lambda : self._CloseItem(closer))

    def CloseItem(self, item):
        closer = self._GetCloser(item)
        if not closer:
            return
        self._CloseItem(closer)

    def _CloseItem(self, closer):
        idx = self.autoClosers.index(closer)
        item = self.showingStack[idx]
        self.showingStack.remove(item)
        self.autoClosers.remove(closer)
        closer.Abort()
        item.Close()
        self.CheckOverFlow()
        self.PushDisplayedItems()

    def _GetCloser(self, item):
        for closer in self.autoClosers:
            if closer.monitorObject == item:
                return closer

    def CheckOverFlow(self):
        if len(self.overFlowStack) > 0:
            self.ShowThisItem(self.overFlowStack.pop())

    def QueueItem(self, item):
        self.overFlowStack.append(item)

    def AddItem(self, item):
        if hasattr(item, 'on_closed_by_user_signal'):
            item.on_closed_by_user_signal.connect(self.CloseByUser)
        if len(self.showingStack) < self.maxStacked:
            self.ShowThisItem(item)
        else:
            self.QueueItem(item)

    def CloseByUser(self, item):
        return self.CloseItem(item)

    def Cleanup(self):
        self.baseContainer.Flush()
        self.showingStack = []
        self.overFlowStack = []
        for closer in self.autoClosers:
            closer.Abort()

        self.autoClosers = []

    def Update(self):
        pass
