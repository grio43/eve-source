#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\cloneGrade\omegaCloneIcon.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
import carbonui.const as uiconst
from clonegrade.const import TEXTUREPATH_OMEGA_64, TEXTUREPATH_OMEGA_32, TEXTUREPATH_OMEGA_24
from eve.client.script.ui.shared.cloneGrade import cloneStateUtil
import expertSystems.client
from localization import GetByLabel
from carbonui.uicore import uicore

class OmegaCloneIcon(Container):
    default_name = 'OmegaCloneIcon'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.cloneGradeSvc = sm.GetService('cloneGradeSvc')
        self.baseOpacity = attributes.get('opacity', self.default_opacity)
        self.tooltipText = attributes.get('tooltipText', None)
        self.unlockedWithExpertSystems = attributes.get('unlockedWithExpertSystems')
        self.origin = attributes.origin
        self.reason = attributes.reason
        self.construct_layout()
        self.UpdateIcon()

    def construct_layout(self):
        self.icon = Sprite(name='icon', bgParent=self)

    def UpdateIcon(self):
        if self.width <= 24:
            self.icon.texturePath = TEXTUREPATH_OMEGA_24
        elif self.width <= 32:
            self.icon.texturePath = TEXTUREPATH_OMEGA_32
        else:
            self.icon.texturePath = TEXTUREPATH_OMEGA_64

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        uicore.cmd.OpenCloneUpgradeWindow(self.origin, self.reason)

    def OnMouseEnter(self, *args):
        self.FadeIn()
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        sm.ScatterEvent('OnOmegaIconMouseEnter')

    def OnMouseExit(self, *args):
        self.FadeOut()
        sm.ScatterEvent('OnOmegaIconMouseExit')

    def FadeIn(self):
        uicore.animations.FadeTo(self, self.opacity, 1.5 * self.baseOpacity, duration=0.3)

    def FadeOut(self):
        uicore.animations.FadeTo(self, self.opacity, self.baseOpacity, duration=0.3)

    def GetTooltipText(self):
        if self.tooltipText:
            return self.tooltipText
        elif self.cloneGradeSvc.IsOmega():
            return GetByLabel('UI/CloneState/RequiresOmegaCloneIsOmega')
        else:
            return GetByLabel('UI/CloneState/RequiresOmegaClone')

    def LoadTooltipPanel(self, tooltipPanel, *args):
        text = self.GetTooltipText()
        if self.unlockedWithExpertSystems:
            tooltipPanel.LoadGeneric1ColumnTemplate()
            expertSystems.add_generic_unlocked_by_expert_systems(tooltipPanel)
        else:
            cloneStateUtil.LoadTooltipPanel(tooltipPanel, text, origin=self.origin, reason=self.reason)
