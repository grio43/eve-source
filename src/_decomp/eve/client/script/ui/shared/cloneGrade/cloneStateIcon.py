#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\cloneGrade\cloneStateIcon.py
import clonegrade
from eve.client.script.ui.shared.cloneGrade.omegaCloneIcon import OmegaCloneIcon
from localization import GetByLabel

class CloneStateIcon(OmegaCloneIcon):
    default_name = 'CloneStateIcon'
    __notifyevents__ = ['OnSubscriptionChanged']

    def ApplyAttributes(self, attributes):
        OmegaCloneIcon.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)

    def UpdateIcon(self):
        if self.cloneGradeSvc.IsOmega():
            if self.width <= 24:
                texturePath = clonegrade.TEXTUREPATH_OMEGA_24
            elif self.width <= 32:
                texturePath = clonegrade.TEXTUREPATH_OMEGA_32
            else:
                texturePath = clonegrade.TEXTUREPATH_OMEGA_64
        elif self.width <= 32:
            texturePath = clonegrade.TEXTUREPATH_ALPHA_32
        else:
            texturePath = clonegrade.TEXTUREPATH_ALPHA_64
        self.icon.texturePath = texturePath

    def OnSubscriptionChanged(self):
        self.UpdateIcon()

    def GetTooltipText(self):
        if self.cloneGradeSvc.IsOmega():
            return GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/CurrentCloneStateOmegaDescription')
        else:
            return GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/CurrentCloneStateAlphaDescription')
