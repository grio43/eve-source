#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\cloneGrade\button.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from clonegrade.const import COLOR_OMEGA_ORANGE
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold
from localization import GetByLabel

class CloneGradeButtonMedium(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL
    default_height = 21

    def ApplyAttributes(self, attributes):
        super(CloneGradeButtonMedium, self).ApplyAttributes(attributes)
        self.onClick = attributes.onClick
        self.onMouseEnter = attributes.onMouseEnter
        self.onMouseExit = attributes.onMouseExit
        text = attributes.text or GetByLabel('UI/CloneState/Upgrade')
        cont = ContainerAutoSize(parent=self, align=uiconst.TOLEFT)
        self.label = EveLabelMediumBold(parent=cont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, text=text, color=COLOR_OMEGA_ORANGE, padding=(16, 0, 16, 0))
        self.bg = StretchSpriteHorizontal(bgParent=self, texturePath='res:/UI/Texture/Classes/CloneGrade/omegaBG_21.png', rightEdgeSize=8, leftEdgeSize=8, opacity=0.85)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        duration = 0.2
        animations.FadeTo(self.label, self.label.opacity, 1.5, duration=duration)
        animations.FadeTo(self.bg, self.bg.opacity, 1.5, duration=duration)
        if callable(self.onMouseEnter):
            self.onMouseEnter()

    def OnMouseExit(self, *args):
        duration = 0.3
        animations.FadeTo(self.label, self.label.opacity, 1.0, duration=duration)
        animations.FadeTo(self.bg, self.bg.opacity, 1.0, duration=duration)
        if callable(self.onMouseExit):
            self.onMouseExit()

    def OnClick(self, *args):
        if callable(self.onClick):
            PlaySound(uiconst.SOUND_BUTTON_CLICK)
            self.onClick()
