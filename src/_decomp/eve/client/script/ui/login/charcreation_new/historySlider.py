#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\historySlider.py
import carbonui.const as uiconst
import uthread
import charactercreator.const as ccConst
import localization
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util import timerstuff
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import FlushList
from eve.client.script.ui.control import eveIcon
from eve.client.script.ui.login.charcreation_new.charCreationUtils import CCLabel
from eve.client.script.ui.login.charcreation_new.dollManager import GetCharacterCreationDollManager

class CharacterCreationHistorySlider(Container):
    __notifyevents__ = ['OnDollUpdated', 'OnHistoryUpdated']
    SIZE = 15
    BITWIDTH = 4
    BITGAP = 3
    default_name = 'CharacterCreationHistorySlider'
    default_left = 0
    default_top = 0
    default_width = 400
    default_height = SIZE
    default_align = uiconst.CENTER

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        for each in uicore.layer.main.children:
            if each.name == self.default_name:
                each.Close()

        if not attributes.parent:
            uicore.layer.main.children.insert(0, self)
        self.bitChangeCheck = attributes.bitChangeCheck
        self._lastLit = None
        self._currentIndex = None
        self._scrolling = False
        self._mouseOffset = 0
        self._lastLoadIndex = attributes.lastLitHistoryBit
        for name, icon, align in (('left', ccConst.ICON_BACK, uiconst.TOLEFT), ('right', ccConst.ICON_NEXT, uiconst.TORIGHT)):
            btn = Container(name='%sBtn' % name, parent=self, align=align, width=self.SIZE, state=uiconst.UI_NORMAL)
            btn.icon = eveIcon.Icon(name='%sIcon' % name, icon=icon, parent=btn, state=uiconst.UI_DISABLED, align=uiconst.CENTER, color=ccConst.COLOR50)
            Frame(parent=btn, frameConst=ccConst.MAINFRAME_INV, color=(1.0, 1.0, 1.0, 0.5))
            Fill(parent=btn, color=(0.0, 0.0, 0.0, 0.25))
            btn.OnClick = (self.OnButtonClicked, btn)
            btn.OnMouseEnter = (self.OnButtonEnter, btn)
            btn.OnMouseExit = (self.OnButtonExit, btn)
            btn.cursor = uiconst.UICURSOR_SELECT

        CCLabel(parent=self, idx=0, text=localization.GetByLabel('UI/Login/CharacterCreation/UndoHistory'), top=-20, uppercase=True, letterspace=1, shadowOffset=(0, 0), color=ccConst.COLOR50)
        self.mainPar = Container(parent=self, clipChildren=True, padding=(3, 0, 3, 0))
        self.bitParent = Container(parent=self.mainPar, align=uiconst.TOPLEFT, height=self.SIZE)
        self.scrollHandle = Container(parent=self.bitParent, align=uiconst.TOPLEFT, pos=(0,
         0,
         10,
         self.SIZE), color=(1.0, 1.0, 1.0, 1.0), state=uiconst.UI_NORMAL)
        Fill(parent=self.scrollHandle, color=(1.0, 1.0, 1.0, 1.0), padding=(2, 0, 2, 0))
        self.scrollHandle.OnMouseDown = self.SH_MouseDown
        self.scrollHandle.OnMouseUp = self.SH_MouseUp
        Frame(parent=self.mainPar, frameConst=ccConst.MAINFRAME_INV, color=(1.0, 1.0, 1.0, 0.5))
        Fill(parent=self.mainPar, color=(0.0, 0.0, 0.0, 0.25))
        frame = Frame(parent=self, frameConst=ccConst.FRAME_SOFTSHADE, color=(0.0, 0.0, 0.0, 0.25))
        frame.padding = (-32, -5, -32, -15)
        self.UpdateHistory()
        sm.RegisterNotify(self)

    def OnDollUpdated(self, charID, redundantUpdate, *args):
        if not self.destroyed and not redundantUpdate and self.state != uiconst.UI_HIDDEN:
            self.UpdateHistory()

    def OnHistoryUpdated(self, *args):
        if not self.destroyed:
            self.UpdateHistory()

    def UpdateHistory(self):
        dnaLog = GetCharacterCreationDollManager().GetDollDNAHistory()
        if dnaLog is not None:
            self.LoadHistory(len(dnaLog))

    def GetCurrentIndexAndMaxIndex(self):
        if self._lastLit and self._lastLit in self.bitParent.children:
            currentIndex = self.bitParent.children.index(self._lastLit) - 1
        else:
            currentIndex = 0
        return (currentIndex, len(self.bitParent.children) - 2)

    def OnButtonClicked(self, button, *args):
        PlaySound('ui_icc_button_mouse_down_play')
        if self.bitChangeCheck and not self.bitChangeCheck():
            return
        if button.name == 'leftBtn':
            direction = -1
        else:
            direction = 1
        self.ButtonScroll(direction)

    def ButtonScroll(self, direction):
        currentIndex, maxIndex = self.GetCurrentIndexAndMaxIndex()
        if currentIndex + direction > maxIndex:
            return
        currentIndex += 1
        newIndex = max(0, min(len(self.bitParent.children) - 1, direction + currentIndex))
        if newIndex == 0:
            self._lastLit = None
        else:
            self._lastLit = self.bitParent.children[newIndex]
        self.SettleScrollHandle()
        self.UpdateBitsState()
        self.UpdatePosition()

    def OnButtonEnter(self, button, *args):
        PlaySound('ui_icc_button_mouse_over_play')
        button.icon.SetAlpha(1.0)

    def OnButtonExit(self, button, *args):
        button.icon.SetAlpha(0.5)

    def LoadHistory(self, historyLength):
        FlushList(self.bitParent.children[1:])
        litBit = None
        for i in xrange(historyLength):
            bit = Container(parent=self.bitParent, name='bit_%s' % i, align=uiconst.TOPLEFT, pos=(i * (self.BITWIDTH + self.BITGAP),
             0,
             self.BITWIDTH + self.BITGAP,
             self.SIZE), state=uiconst.UI_NORMAL)
            Fill(parent=bit, color=(1.0, 1.0, 1.0, 0.75), padding=(self.BITGAP,
             4,
             0,
             4))
            bit.OnClick = (self.OnClickBit, bit)
            bit.OnMouseEnter = self.OnBitMouseEnter
            bit.idx = i
            if i == self._lastLoadIndex:
                litBit = bit

        self._lastLoadIndex = None
        self.UpdateContentWidth()
        if litBit is None:
            self.ScrollTo(1.0, initing=True)
        else:
            self._lastLit = litBit
            self.SettleScrollHandle(initing=True)
            self.UpdateBitsState()

    def OnBitMouseEnter(self):
        PlaySound('ui_icc_button_mouse_over_play')

    def OnClickBit(self, bit, *args):
        PlaySound('ui_icc_button_mouse_down_play')
        if self.bitChangeCheck and not self.bitChangeCheck():
            return
        self._lastLit = bit
        self.SettleScrollHandle()
        self.UpdateBitsState()

    def UpdateContentWidth(self):
        self.bitParent.width = (len(self.bitParent.children) - 1) * (self.BITWIDTH + self.BITGAP) + self.BITGAP

    def ScrollTo(self, portion, initing = False):
        l, t, w, h = self.mainPar.GetAbsolute()
        scrollRange = min(0, w - self.bitParent.width)
        self.scrollHandle.left = int((self.bitParent.width - self.scrollHandle.width) * portion)
        self.UpdatePosition()
        self.SettleScrollHandle(initing)

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
        self.SettleScrollHandle()

    def SettleScrollHandle(self, initing = False):
        if self._lastLit is not None:
            self.scrollHandle.left = self._lastLit.left
            if not initing:
                self._currentIndex = self._lastLit.idx
                uthread.new(GetCharacterCreationDollManager().LoadDnaFromHistory, self._lastLit.idx)
                self._lastLoadIndex = self._lastLit.idx
        else:
            self.scrollHandle.left = -2

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
        self.UpdateBitsState()

    def UpdateBitsState(self):
        self._lastLit = None
        l, t, w, h = self.bitParent.GetAbsolute()
        for bit in self.bitParent.children[1:]:
            if bit.left + self.BITGAP + self.BITWIDTH / 2 > self.scrollHandle.left + self.scrollHandle.width / 2:
                bit.children[0].opacity = 0.25
            else:
                bit.children[0].opacity = 1.0
                self._lastLit = bit
