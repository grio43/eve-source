#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\controls\agencyScrollContEntry.py
from carbonui import uiconst
from carbonui.control.baseScrollContEntry import BaseScrollContEntry
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveLabelMedium

class AgencyScrollContEntry(BaseScrollContEntry):
    default_height = 20
    default_top = 5
    default_opacity = 0.0

    def ApplyAttributes(self, attributes):
        super(AgencyScrollContEntry, self).ApplyAttributes(attributes)
        self.contentPiece = attributes.contentPiece
        self.ConstructLayout()
        self.Update()

    def ConstructLayout(self):
        self.ConstructIcon()
        self.ConstructLabel()

    def ConstructIcon(self):
        iconContainer = Container(name='iconContainer', parent=self, align=uiconst.TOLEFT, width=16, left=5)
        self.icon = Sprite(name='asteroidBeltBracketIcon', parent=iconContainer, pos=(0, 0, 16, 16), align=uiconst.CENTERLEFT)

    def ConstructLabel(self):
        self.label = EveLabelMedium(name='label', parent=self, align=uiconst.CENTERLEFT, pos=(24, 0, 0, 0))

    def Update(self):
        self.UpdateIcon()
        self.UpdateLabel()

    def UpdateIcon(self):
        self.icon.SetTexturePath(self.contentPiece.GetBracketIconTexturePath())

    def UpdateLabel(self):
        self.label.SetText(self.contentPiece.GetName())
        self.label.SetRightAlphaFade(fadeEnd=350, maxFadeWidth=15)

    def AnimEnter(self, offsetIdx):
        timeOffset = 0.05 * offsetIdx
        duration = 0.15
        animations.Tr2DScaleTo(self, (0.9, 0.9), (1.0, 1.0), duration=duration, timeOffset=timeOffset)
        animations.FadeIn(self, duration=2 * duration, timeOffset=timeOffset)

    def GetMenu(self):
        return self.contentPiece.GetMenu()
