#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentGroupPages\contentScroller.py
import math
import carbonui.const as uiconst
import uthread
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from mathext import clamp
from signals import Signal
import uthread2
SETTING_CONFIG = 'contentScroller_%s'

class ContentScroller(object):

    def __init__(self, contentID, contentCont, numAvailableCards, numVisibleCards, slotSize, extraSlotWidth, scrollIndicator):
        self.onUpdate = Signal(signalName='onUpdate8')
        self._initMouseDownX = 0
        self._initPosX = 0
        self.contentID = contentID
        self.contentCont = contentCont
        self.scrollIndicator = scrollIndicator
        self.numAvailableCards = numAvailableCards
        self.numVisibleCards = numVisibleCards
        self.slotSize = slotSize
        self.extraSlotWidth = extraSlotWidth
        self.visibleWidth = numVisibleCards * slotSize + self.extraSlotWidth
        self.totalWidth = numAvailableCards * slotSize
        self.minLeft = self.visibleWidth - self.totalWidth
        self.clickedOn = None
        self.hasMoved = False
        self.scrollTimer = None
        self.scrollIndicator.width = int(abs(float(self.visibleWidth) / self.totalWidth) * self.visibleWidth)
        self.isDead = False
        lastLeft = settings.char.ui.Get(SETTING_CONFIG % self.contentID, 0)
        uthread2.call_after_wallclocktime_delay(self.UpdateLeft, 0.1, lastLeft)

    def OnMouseWheel(self, *args):
        if not self._IsContentAvailable():
            return
        uthread2.start_tasklet(self._OnMouseWheel)

    def _OnMouseWheel(self):
        newLeft = self.contentCont.left - uicore.uilib.dz / 3
        self.UpdateLeft(newLeft)
        if not self.scrollIndicator.display:
            endValue = getattr(self.scrollIndicator, 'baseOpacity', 1)
            self.scrollIndicator.display = True
            animations.FadeTo(self.scrollIndicator, 0, endValue, duration=0.3, sleep=True)
            if self.scrollIndicator.display:
                animations.FadeTo(self.scrollIndicator, self.scrollIndicator.opacity, 0, duration=0.3, sleep=True, callback=self.scrollIndicator.Hide)
        settings.char.ui.Set(SETTING_CONFIG % self.contentID, newLeft)

    def OnMouseDown(self, clickedOn, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return
        self.scrollIndicator.display = True
        self.scrollIndicator.opacity = getattr(self.scrollIndicator, 'baseOpacity', 1)
        self._initMouseDownX = uicore.uilib.x
        self._initPosX = self.contentCont.left
        self.clickedOn = clickedOn
        self.scrollTimer = AutoTimer(10, self.UpdateScroll)
        uicore.uilib.tooltipHandler.CloseTooltip()
        self.hasMoved = False

    def OnMouseUp(self, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return
        if self.hasMoved:
            self.clickedOn.backupOnClick = getattr(self.clickedOn, 'OnClick', None)
            self.clickedOn.OnClick = lambda *args: None
            uthread.new(self.ResetOnClick_thread, self.clickedOn)
            self.hasMoved = False
        self.scrollTimer = None
        self.clickedOn = None
        self.scrollIndicator.display = False
        settings.char.ui.Set(SETTING_CONFIG % self.contentID, self.contentCont.left)

    def ResetOnClick_thread(self, clickedOn):
        onClickedFunc = getattr(clickedOn, 'backupOnClick', None)
        if onClickedFunc:
            clickedOn.OnClick = onClickedFunc

    def _IsContentAvailable(self):
        return self.contentCont is not None and not self.contentCont.destroyed and not self.isDead

    def UpdateScroll(self, *args):
        if not self._IsContentAvailable():
            self.scrollTimer = None
            return
        self.hasMoved = self.hasMoved or abs(self._initMouseDownX - uicore.uilib.x) > 2
        newLeft = self._initPosX + (uicore.uilib.x - self._initMouseDownX)
        self.UpdateLeft(newLeft)

    def UpdateLeft(self, newLeft):
        if not self._IsContentAvailable():
            return
        newLeft = clamp(newLeft, self.minLeft, 0)
        self.UpdateScrollIndicator(newLeft)
        self.SendSignal(newLeft)

    def UpdateScrollIndicator(self, newLeft):
        self.scrollIndicator.left = float(newLeft) / self.minLeft * (self.visibleWidth - self.scrollIndicator.width)

    def SendSignal(self, newLeft):
        firstIdx, lastIdx = self.GetFirstAndLastIdx(newLeft)
        self.onUpdate(newLeft, firstIdx, lastIdx, self.slotSize)

    def GetFirstAndLastIdx(self, newLeft):
        firstIdx = -1 if newLeft == 0 else int(-newLeft / self.slotSize)
        lastIdx = math.ceil(float(-newLeft + self.extraSlotWidth) / self.slotSize) + self.numVisibleCards - 1
        if newLeft == self.minLeft:
            lastIdx += 1
        return (firstIdx, lastIdx)

    def Cleanup(self):
        self.contentCont = None
        self.leftFade = None
        self.rightFade = None
        self.clickedOn = None
        self.scrollIndicator = None
        self.onUpdate.clear()
        self.isDead = True
