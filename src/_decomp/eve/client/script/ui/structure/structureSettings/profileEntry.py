#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureSettings\profileEntry.py
import carbonui.control.contextMenu.contextMenu
from carbonui import const as uiconst
import carbonui
from carbonui.primitives.fill import Fill
from carbonui.control.buttonIcon import ButtonIcon
from sovDashboard.sovStatusEntries import MouseInsideScrollEntry
from carbonui.uicore import uicore

class ProfileEntryBase(MouseInsideScrollEntry):
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    rightBtnTexturePath = 'res:/UI/Texture/Icons/73_16_50.png'

    def ApplyAttributes(self, attributes):
        MouseInsideScrollEntry.ApplyAttributes(self, attributes)
        self.blinkBG = None
        if self.rightBtnTexturePath:
            self.rightBtn = ButtonIcon(name='optionIcon', parent=self, align=uiconst.CENTERRIGHT, pos=(2, 0, 16, 16), iconSize=16, texturePath=self.rightBtnTexturePath, func=self.OnRightBtnClicked, opacity=0.0)
            self.rightBtn.OnMouseEnter = self.OnRightBtnMouseEnter
        else:
            self.rightBtn = None

    def OnRightBtnClicked(self, *args):
        carbonui.control.contextMenu.contextMenu.ShowMenu(self)

    def OnRightBtnMouseEnter(self, *args):
        ButtonIcon.OnMouseEnter(self.rightBtn, *args)
        self.OnMouseEnter(*args)

    def OnMouseEnter(self, *args):
        MouseInsideScrollEntry.OnMouseEnter(self, *args)
        self.FadeSprites(1.0)
        self.ChangeRightContDisplay(True)

    def OnMouseNoLongerInEntry(self):
        MouseInsideScrollEntry.OnMouseNoLongerInEntry(self)
        self.FadeSprites(0.0)
        self.ChangeRightContDisplay(False)

    def FadeSprites(self, toValue):
        if self.rightBtn:
            uicore.animations.FadeTo(self.rightBtn, startVal=self.rightBtn.opacity, endVal=toValue, duration=0.1, loops=1)

    def ChangeRightContDisplay(self, show = False):
        pass

    def GetMenu(self, *args):
        pass

    def CheckConstructBlinkBG(self):
        if self.blinkBG is None:
            self.blinkBG = Fill(bgParent=self, color=(1.0, 1.0, 1.0, 0.0))
