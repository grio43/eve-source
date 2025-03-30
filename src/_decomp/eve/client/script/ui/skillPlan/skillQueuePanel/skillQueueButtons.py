#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillQueuePanel\skillQueueButtons.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import ButtonStyle, uiconst
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.control import tooltips
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.cloneGrade import cloneStateUtil, ORIGIN_TRAININGSPEEDICON, ORIGIN_SKILLPLANBUTTON
from eve.client.script.ui.skilltrading.banner import SkillInjectorBanner, AlphaInjectorBanner
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from inventorycommon import const as invconst
from localization import GetByLabel
ICON_SIZE = 26
BUTTON_SIZE = 32

class ExpertSystemIconButton(Button):

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.margin = (12, 8, 12, 8)
        tooltipPanel.AddSpriteLabel(texturePath='res:/UI/Texture/classes/ExpertSystems/logo_simple_32.png', label=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/ExpertSystems/ExpertSystems'), iconOffset=0)
        tooltipPanel.AddSpacer(0, 5)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/ExpertSystems/ExpertSystemDescription'), wrapWidth=200)


class ApplySkillPointsButtonTooltip(TooltipBaseWrapper):

    def __init__(self, queueLength, freeSkillPoints):
        super(ApplySkillPointsButtonTooltip, self).__init__()
        self.queueLength = queueLength
        self.freeSkillPoints = freeSkillPoints

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        if self.queueLength <= 0:
            text = GetByLabel('UI/SkillQueue/ApllySkillPointsDisabledHint')
        elif self.freeSkillPoints <= 0:
            text = GetByLabel('UI/SkillQueue/FreeSkillPointsNeededLabel', injectorTypeID=invconst.typeSkillInjector)
        else:
            text = GetByLabel('UI/SkillQueue/ApplySkillPoints')
        self.tooltipPanel.AddLabelMedium(text=text, wrapWidth=250, state=uiconst.UI_NORMAL)
        return self.tooltipPanel


class SkillInjectorTooltip(TooltipBaseWrapper):

    def __init__(self):
        super(SkillInjectorTooltip, self).__init__()

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.AddCell(SkillInjectorBanner(align=uiconst.TOPLEFT, width=280))
        return self.tooltipPanel


class AlphaInjectorTooltip(TooltipBaseWrapper):

    def __init__(self):
        super(AlphaInjectorTooltip, self).__init__()

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.AddCell(AlphaInjectorBanner(align=uiconst.TOPLEFT, width=280))
        return self.tooltipPanel


class TrainingSpeedIcon(ContainerAutoSize):
    default_name = 'TrainingSpeedIcon'
    default_height = 18
    default_state = uiconst.UI_NORMAL
    default_opacity = 0.7
    __notifyevents__ = ['OnSubscriptionChanged']

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        cont = ContainerAutoSize(parent=self, align=uiconst.TOLEFT)
        self.label = Label(parent=cont, align=uiconst.CENTER, bold=True, padRight=3, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=1.0)
        self.icon = Sprite(parent=self, align=uiconst.TOLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/CloneGrade/trainingSpeed.png', width=16, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.9)
        self.UpdateText()

    def UpdateText(self):
        if self.IsOmega():
            self.label.text = '2x'
        else:
            self.label.text = '1x'

    def LoadTooltipPanel(self, tooltipPanel, *args):
        return cloneStateUtil.LoadTooltipPanel(tooltipPanel, self.GetTooltipText(), origin=ORIGIN_TRAININGSPEEDICON)

    def IsOmega(self):
        return sm.GetService('cloneGradeSvc').IsOmega()

    def GetTooltipText(self):
        if self.IsOmega():
            return GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/TrainingSpeedOmega')
        else:
            return GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/TrainingSpeedAlpha')

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def OnSubscriptionChanged(self):
        self.UpdateText()


class OmegaButton(Button):
    default_iconSize = 24
    default_style = ButtonStyle.MONETIZATION
    default_texturePath = 'res:/UI/Texture/classes/Seasons/omega_32x32.png'
    origin = ORIGIN_SKILLPLANBUTTON

    def ApplyAttributes(self, attributes):
        attributes.func = lambda button: uicore.cmd.OpenCloneUpgradeWindow(origin=button.origin)
        super(OmegaButton, self).ApplyAttributes(attributes)


class OmegaTrainingSpeedButton(OmegaButton):
    origin = ORIGIN_TRAININGSPEEDICON

    def LoadTooltipPanel(self, tooltipPanel, *args):
        text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/TrainingSpeedAlpha')
        return cloneStateUtil.LoadTooltipPanel(tooltipPanel, text, origin=self.origin)
