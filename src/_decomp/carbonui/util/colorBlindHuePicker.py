#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\util\colorBlindHuePicker.py
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbonui.util import colorblind
from carbonui.util.color import Color
import carbonui.const as uiconst
from eve.client.script.ui.control.eveWindowUnderlay import RaisedUnderlay
from localization import GetByLabel
OPACITY_DISABLED = 0.05
SIZE = 16

class ColorBlindHuePicker(Container):
    default_name = 'ColorBlindHuePicker'
    default_height = SIZE

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.onHueClicked = attributes.onHueClicked
        self.hueContainers = []
        for hue in colorblind.HUES:
            hueCont = HueContainer(parent=self, align=uiconst.TOLEFT, width=41, hue=hue, onClick=self.OnHueClicked, padLeft=1)
            self.hueContainers.append(hueCont)

    def GetActiveHues(self):
        return [ hueCont.GetHUE() for hueCont in self.hueContainers if hueCont.IsActive() ]

    def OnHueClicked(self, hue):
        self.onHueClicked(hue)

    def UpdateHues(self):
        for hue in self.hueContainers:
            hue.UpdateIsActive()


class HueContainer(Container):
    default_name = 'HueContainer'
    default_state = uiconst.UI_NORMAL
    default_hint = GetByLabel('UI/SystemMenu/GeneralSettings/ColorBlindToggleHint')

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.hue = attributes.hue
        self.onClick = attributes.onClick
        self.isActive = None
        color = Color().SetHSB(self.hue, 1.0, 1.0).GetRGBA()
        Fill(parent=self, color=color, ignoreColorBlindMode=True, padding=2)
        self.underlay = RaisedUnderlay(bgParent=self)
        self.UpdateIsActive()

    def UpdateIsActive(self):
        self.StopAnimations()
        self.isActive = self.hue in colorblind.GetCurrentHues()
        self.opacity = 1.0 if self.isActive else OPACITY_DISABLED
        self.underlay.opacity = 1.0 if self.isActive else 0.0

    def IsActive(self):
        return self.isActive

    def OnClick(self, *args):
        self.onClick(self.hue)

    def GetHUE(self):
        return self.hue

    def OnMouseEnter(self, *args):
        opacity = 0.5
        animations.FadeTo(self, self.opacity, opacity, duration=0.3)

    def OnMouseExit(self, *args):
        opacity = 1.0 if self.isActive else OPACITY_DISABLED
        animations.FadeTo(self, self.opacity, opacity, duration=0.3)
