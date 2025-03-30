#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\historyBar.py
import carbonui.const as uiconst
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util import timerstuff
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.control.buttonIcon import ButtonIcon
from eveexceptions import ExceptionEater
from menu import MenuLabel
from signals import Signal
from signals.signalUtil import ChangeSignalConnect
UPDATE_CODE_INIT = 1
UPDATE_CODE_ADD = 2
UPDATE_CODE_REMOVE = 3
UPDATE_CODE_CLEAR = 4
UPDATE_CODE_SELECTED = 5
UPDATE_CODE_CORRECTION = 6

class HistoryBar(Container):
    default_name = 'historyBar'
    default_left = 0
    default_top = 0
    default_width = 400
    default_height = 17
    default_align = uiconst.CENTER
    default_btnSize = 9
    default_bitWidth = 7
    default_bitGap = 3

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.bitChangeCheck = attributes.bitChangeCheck
        self.btnSize = attributes.get('btnSize', self.default_btnSize)
        self.callback = attributes.callback
        self.bitHintFunc = attributes.bitHintFunc
        self.isAllowedToLoadFunc = attributes.isAllowedToLoadFunc
        self.historyController = attributes.get('historyController', HistoryController())
        self.bitHeight = attributes.get('bitHeight', self.height - 6)
        self.bitWidth = attributes.get('bitWidth', self.default_bitWidth)
        self.bitGap = attributes.get('bitGap', self.default_bitGap)
        self._scrolling = False
        self._mouseOffset = 0
        self.ConstructButtons()
        self.ConstructBar()
        self.UpdateHistory(updateCode=UPDATE_CODE_INIT)
        self.ChangeSignalConnection()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.historyController.on_history_updated, self.OnHistoryUpdated), (self.historyController.on_history_correction_triggered, self.OnCorrectPosition)]
        ChangeSignalConnect(signalAndCallback, connect)

    def OnHistoryUpdated(self, updateCode = None):
        self.UpdateHistory(updateCode=updateCode)

    def ConstructButtons(self):
        fullSize = self.btnSize + 10
        leftBtnCont = Container(name='leftBtnCont', parent=self, align=uiconst.TOLEFT, width=fullSize, opacity=0.75)
        self.leftBtn = ButtonIcon(name='leftBtn', parent=leftBtnCont, align=uiconst.CENTERRIGHT, width=fullSize, height=fullSize, iconSize=self.btnSize, texturePath='res:/ui/texture/shared/arrows/arrowLeft.png', func=self.OnButtonClicked, args=(-1,), iconClass=Sprite)
        rightBtnCont = Container(name='leftBtnCont', parent=self, align=uiconst.TORIGHT, width=fullSize, opacity=0.75)
        self.rightBtn = ButtonIcon(name='rightBtn', parent=rightBtnCont, align=uiconst.CENTERLEFT, width=fullSize, height=fullSize, iconSize=self.btnSize, texturePath='res:/ui/texture/shared/arrows/arrowRight.png', func=self.OnButtonClicked, args=(1,), iconClass=Sprite)

    def ConstructBar(self):
        self.mainPar = Container(name='mainPar', parent=self, clipChildren=True, state=uiconst.UI_NORMAL)
        Frame(parent=self.mainPar, color=(0.5, 0.5, 0.5, 0.2))
        Fill(parent=self.mainPar, color=(0.0, 0.0, 0.0, 0.25))
        self.mainPar.GetMenu = self.GetHistoryBarMenu
        self.scrollHandleCont = Container(name='scrollHandleCont', parent=self.mainPar, align=uiconst.CENTERLEFT, height=self.height)
        self.bitParent = Container(name='bitParent', parent=self.mainPar, align=uiconst.CENTERLEFT, height=self.height - 6)
        self.bits = []
        self.scrollHandle = Container(parent=self.scrollHandleCont, align=uiconst.TOPLEFT, pos=(0,
         1,
         self.bitWidth,
         self.height - 2), color=(1.0, 1.0, 1.0, 1.0), state=uiconst.UI_NORMAL)
        self.scrollHandle.cursor = uiconst.UICURSOR_POINTER_MENU
        Fill(parent=self.scrollHandle, color=(1.0, 1.0, 1.0, 1.0))
        self.scrollHandle.OnMouseDown = self.SH_MouseDown
        self.scrollHandle.OnMouseUp = self.SH_MouseUp
        self.scrollHandle.GetMenu = self.GetScrollHandleMenu

    def UpdateHistory(self, updateCode = None):
        history = self.historyController.GetHistory()
        if history is not None:
            self.LoadHistory(len(history), updateCode)

    def GetCurrentIndexAndMaxIndex(self):
        lastLitIdx = self.historyController.lastLitIdx
        if lastLitIdx and self.bits:
            currentIndex = min(lastLitIdx, len(self.bits) - 1)
        else:
            currentIndex = 0
        return (currentIndex, len(self.bits) - 1)

    def OnButtonClicked(self, direction, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        if self.bitChangeCheck and not self.bitChangeCheck():
            return
        self.ButtonScroll(direction)

    def ButtonScroll(self, direction):
        currentIndex, maxIndex = self.GetCurrentIndexAndMaxIndex()
        if currentIndex + direction > maxIndex:
            return
        newIndex = max(0, min(len(self.bits), direction + currentIndex))
        self.historyController.lastLitIdx = newIndex
        self.SettleScrollHandle(UPDATE_CODE_SELECTED)
        self.UpdateBitsState()
        self.UpdatePosition()

    def LoadHistory(self, historyLength, updateCode = None):
        self.bitParent.Flush()
        self.bits = []
        litBit = None
        widthForBit = self.bitWidth + self.bitGap
        for i in xrange(historyLength):
            bit = HistoryBit(bitIdx=i, parent=self.bitParent, name='bit_%s' % i, pos=(i * widthForBit,
             0,
             widthForBit,
             self.bitHeight), callback=self.OnClickBit, bitGap=self.bitGap)
            bit.GetMenu = (self.GetBitMenu, i)
            bit.GetHint = lambda bitIdx = i: self.GetBitHint(bitIdx)
            if i == self.historyController.lastLoadIdx:
                litBit = bit
            self.bits.append(bit)

        self.historyController.lastLoadIdx = None
        self.UpdateContentWidth()
        if litBit is None:
            initing = updateCode == UPDATE_CODE_INIT
            self.ScrollTo(1.0, initing=initing)
        else:
            self.historyController.lastLitIdx = litBit.bitIdx
            self.SettleScrollHandle(updateCode=updateCode)
            self.UpdateBitsState()
        self.UpdatePosition()

    def OnClickBit(self, bit, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        if self.bitChangeCheck and not self.bitChangeCheck():
            return
        self.historyController.lastLitIdx = bit.bitIdx
        self.SettleScrollHandle(UPDATE_CODE_SELECTED)
        self.UpdateBitsState()

    def GetBitHint(self, bitIdx):
        if self.bitHintFunc:
            bitData = self.historyController.GetHistoryFromIdx(bitIdx)
            return self.bitHintFunc(bitData)

    def UpdateContentWidth(self):
        widthForBit = self.bitWidth + self.bitGap
        self.bitParent.width = len(self.bits) * widthForBit + self.bitGap
        self.scrollHandleCont.width = self.bitParent.width

    def ScrollTo(self, portion, initing = False):
        l, t, w, h = self.mainPar.GetAbsolute()
        self.scrollHandle.left = int((self.bitParent.width - self.scrollHandle.width) * portion) + self.bitGap
        self.UpdatePosition()
        updateCode = UPDATE_CODE_INIT if initing else None
        self.SettleScrollHandle(updateCode)

    def SH_MouseDown(self, *args):
        if self.bitChangeCheck and not self.bitChangeCheck():
            return
        l, t, w, h = self.scrollHandle.GetAbsolute()
        self._mouseOffset = uicore.uilib.x - l
        self._scrolling = True
        self.scrollTimer = timerstuff.AutoTimer(5, self.DragScroll)

    def SH_MouseUp(self, *args):
        if self.bitChangeCheck and not self.bitChangeCheck():
            return
        self._scrolling = False
        self._mouseOffset = 0
        self.scrollTimer = None
        self.SettleScrollHandle(UPDATE_CODE_SELECTED)

    def SettleScrollHandle(self, updateCode = None):
        initing = updateCode == UPDATE_CODE_INIT
        lastLitIdx = self.historyController.lastLitIdx
        if lastLitIdx is not None:
            lastLit = self.bits[lastLitIdx]
            if not initing:
                if updateCode == UPDATE_CODE_SELECTED and self.callback and self.isAllowedToLoadFunc:
                    currentBitData = self.historyController.GetHistoryFromIdx(self.historyController.currentIndex)
                    toBeLoaded = self.historyController.GetHistoryFromIdx(lastLitIdx)
                    if not self.isAllowedToLoadFunc(currentBitData, toBeLoaded):
                        return
                self.historyController.currentIndex = lastLitIdx
                self.historyController.lastLoadIdx = lastLitIdx
                if self.callback:
                    historyBitData = self.historyController.GetHistoryFromLastLit()
                    uthread.new(self.callback, historyBitData, updateCode)
            self.scrollHandle.left = lastLit.left + self.bitGap
        else:
            self.scrollHandle.left = -2
        self.leftBtn.Enable()
        self.rightBtn.Enable()
        self.scrollHandle.Show()
        if self.historyController.IsOnFirstBit():
            self.leftBtn.Disable()
            self.leftBtn.UpdateIconState()
        if self.historyController.IsOnLastBit():
            self.rightBtn.Disable()
            self.rightBtn.UpdateIconState()
        if self.historyController.lastLitIdx is None:
            self.leftBtn.Disable()
            self.rightBtn.Disable()
            self.scrollHandle.Hide()

    def DragScroll(self, *args):
        l, t, w, h = self.mainPar.GetAbsolute()
        bl, bt, bw, bh = self.bitParent.GetAbsolute()
        self.scrollHandle.left = min(bw - self.scrollHandle.width, max(0, uicore.uilib.x - self._mouseOffset - bl))
        self.UpdatePosition()

    def UpdatePosition(self):
        l, t, w, h = self.mainPar.GetAbsolute()
        sl, st, sw, sh = self.scrollHandle.GetAbsolute()
        if self.bitParent.width <= w:
            self.bitParent.left = 0
        elif sl < l:
            self.bitParent.left += l - sl
        elif sl + sw > l + w:
            self.bitParent.left -= sl + sw - (l + w)
        self.scrollHandleCont.left = self.bitParent.left
        self.UpdateBitsState()

    def UpdateBitsState(self):
        self.historyController.lastLitIdx = None
        l, t, w, h = self.bitParent.GetAbsolute()
        for bit in self.bits:
            bitVale = bit.left + self.bitGap + self.bitWidth / 2
            handleValue = self.scrollHandle.left + self.scrollHandle.width / 2
            if bitVale > handleValue:
                bit.SetFaded()
            else:
                bit.SetNormal()
                self.historyController.lastLitIdx = bit.bitIdx

    def OnCorrectPosition(self, currentHistoryData):
        lastLoaded = self.historyController.GetHistoryFromLastLit()
        if currentHistoryData != lastLoaded:
            self.historyController.lastLitIdx = None
            self.SettleScrollHandle(UPDATE_CODE_CORRECTION)

    def GetScrollHandleMenu(self):
        if self.historyController.lastLitIdx is None:
            return []
        m = self.GetBitMenu(self.historyController.lastLitIdx)
        return m

    def GetBitMenu(self, bitIdx, *args):
        m = [(MenuLabel('UI/Commands/Remove'), self.historyController.RemoveFromHistory, (bitIdx,))]
        m += self.GetHistoryBarMenu()
        return m

    def GetHistoryBarMenu(self):
        return [(MenuLabel('/Carbon/UI/Controls/Common/ClearHistory'), self.ClearHistory)]

    def ClearHistory(self):
        self.historyController.ClearHistory()

    def Close(self):
        with ExceptionEater('closingHistoryBar'):
            self.ChangeSignalConnection(connect=False)
        Container.Close(self)


class HistoryBit(Container):
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_bitGap = 0

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.bitIdx = attributes.get('bitIdx')
        self.idx = self.bitIdx
        bitGap = attributes.get('bitGap', self.default_bitGap)
        self.callback = attributes.get('callback', None)
        fillColor = (1.0, 1.0, 1.0, 1.0)
        self.bitFill = Fill(name='bitFill', parent=self, color=fillColor, padding=(bitGap,
         0,
         0,
         0))

    def GetNomalOpacity(self):
        if self.bitIdx % 2:
            return 0.7
        return 0.5

    def SetFaded(self):
        self.bitFill.opacity = 0.25

    def SetNormal(self):
        self.bitFill.opacity = self.GetNomalOpacity()

    def OnClick(self, *args):
        if self.callback:
            self.callback(self)

    def OnMouseEnter(self):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self.bitFill.padTop = -2
        self.bitFill.padBottom = -2

    def OnMouseExit(self, *args):
        self.bitFill.padTop = 0
        self.bitFill.padBottom = 0


class HistoryController(object):

    def __init__(self, history = None, overwriteHistory = True):
        self.overwriteHistory = overwriteHistory
        self.ResetVariables()
        if history:
            self.history = history[:]
        self.on_history_updated = Signal(signalName='on_history_updated')
        self.on_history_correction_triggered = Signal(signalName='on_history_correction_triggered')

    def ResetVariables(self):
        self._currentIndex = None
        self._lastLoadIndex = None
        self._lastLitIdx = None
        self.history = []

    @property
    def currentIndex(self):
        return self._currentIndex

    @currentIndex.setter
    def currentIndex(self, value):
        self._currentIndex = value

    @property
    def lastLoadIdx(self):
        return self._lastLoadIndex

    @lastLoadIdx.setter
    def lastLoadIdx(self, value):
        self._lastLoadIndex = value

    @property
    def lastLitIdx(self):
        return self._lastLitIdx

    @lastLitIdx.setter
    def lastLitIdx(self, value):
        self._lastLitIdx = value

    def LoadHistory(self, history):
        self.history = history

    def AddToHistory(self, value, sendSignal = True):
        if self.overwriteHistory:
            if self.lastLitIdx:
                self.history = self.history[:self.lastLitIdx + 1]
        self.history.append(value)
        self.lastLoadIdx = len(self.history) - 1
        if sendSignal:
            self.on_history_updated(UPDATE_CODE_ADD)

    def RemoveFromHistory(self, idx):
        if idx <= len(self.history) - 1:
            self.history.pop(idx)
            if self.lastLitIdx > idx:
                self.lastLitIdx = max(0, self.lastLitIdx - 1)
            if self.lastLoadIdx > idx:
                self.lastLoadIdx = max(0, self.lastLoadIdx - 1)
            if self.currentIndex > idx:
                self.currentIndex = max(0, self.currentIndex - 1)
            self.on_history_updated(UPDATE_CODE_REMOVE)

    def ClearHistory(self, sendSignal = True):
        self.ResetVariables()
        if sendSignal:
            self.on_history_updated(UPDATE_CODE_CLEAR)

    def GetHistory(self):
        return self.history

    def GetHistoryFromLastLit(self):
        return self.GetHistoryFromIdx(self.lastLitIdx)

    def GetHistoryFromIdx(self, idx):
        historyIdx = max(0, min(len(self.history) - 1, idx))
        if historyIdx <= len(self.history) - 1:
            return self.history[historyIdx]

    def IsOnFirstBit(self):
        return self.lastLitIdx == 0

    def IsOnLastBit(self):
        return self.lastLitIdx == len(self.history) - 1

    def TriggerHistoryCorrection(self, historyData):
        self.on_history_correction_triggered(historyData)
