#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\standingsPanel\standingsHeaderButtons.py
import evetypes
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.shared.shipTree.infoBubble import SkillEntry
from eve.client.script.ui.shared.standings import standingUIConst
from localization import GetByLabel

class BaseStandingButton(Container):
    default_name = 'StandingActionButton'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.func = attributes.func
        self.standingData = attributes.standingData
        SpriteThemeColored(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=attributes.texturePath, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.7)
        Sprite(name='bgHoverFrame', bgParent=self, texturePath='res:/UI/texture/shared/frame.png', opacity=0.2, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        self.bgFrame = SpriteThemeColored(name='bgHoverFrame', bgParent=self, texturePath='res:/UI/texture/shared/frameHover.png', opacity=0.0, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelLarge(text=self.GetHintLabel(), colSpan=2, bold=True)
        tooltipPanel.AddSpacer(1, 8, 2)
        tooltipPanel.AddLabelMedium(text=self.GetHintText(), colSpan=2, wrapWidth=230)

    def GetHintLabel(self):
        pass

    def GetHintText(self):
        pass

    def OnClick(self, *args):
        self.func()

    def OnMouseEnter(self, *args):
        animations.FadeTo(self.bgFrame, 0.3, 0.0, duration=0.5)

    def OnMouseExit(self, *args):
        animations.FadeOut(self.bgFrame, duration=0.3)


class StandingActionButton(BaseStandingButton):

    def ApplyAttributes(self, attributes):
        self.actionID = attributes.actionID
        BaseStandingButton.ApplyAttributes(self, attributes)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.actionID == standingUIConst.ACTION_TRAINSKILL:
            tooltipPanel.LoadGeneric2ColumnTemplate()
            tooltipPanel.state = uiconst.UI_NORMAL
            self.CreateTooltipSkill(tooltipPanel)
        else:
            BaseStandingButton.LoadTooltipPanel(self, tooltipPanel, *args)

    def CreateTooltipSkill(self, tooltipPanel):
        skillTypeID = self.standingData.GetSkillTypeID2To1()
        skillLevel = sm.GetService('skills').MySkillLevel(skillTypeID)
        tooltipPanel.AddLabelLarge(text=GetByLabel('UI/Standings/Actions/SocialSkills'), colSpan=2, bold=True)
        tooltipPanel.AddSpacer(1, 8, 2)
        tooltipPanel.AddLabelMedium(text=GetByLabel('Tooltips/CharacterSheet/StandingSkillTooltip', skillName=evetypes.GetName(skillTypeID), ownerID=self.standingData.GetOwnerID2()), colSpan=2, wrapWidth=230)
        tooltipPanel.AddSpacer(1, 8, 2)
        tooltipPanel.AddRow(rowClass=SkillEntry, typeID=skillTypeID, level=skillLevel, showLevel=False, skillBarPadding=(24, 0, 0, 0), cellPadding=(0, 0, 0, 0), textPadding=(0, 0, 0, 0))
        tooltipPanel.AddSpacer(1, 8, 2)

    def GetHintLabel(self):
        return GetByLabel(standingUIConst.LABELS_BY_ACTIONID[self.actionID])

    def GetHintText(self):
        ownerName = cfg.eveowners.Get(self.standingData.GetOwnerID2()).ownerName
        hintText = GetByLabel(standingUIConst.HINTS_BY_ACTIONID[self.actionID], ownerName=ownerName)
        return hintText


class StandingBenefitButton(BaseStandingButton):

    def ApplyAttributes(self, attributes):
        self.benefitID = attributes.benefitID
        BaseStandingButton.ApplyAttributes(self, attributes)

    def GetHintLabel(self):
        return GetByLabel(standingUIConst.LABELS_BY_BENEFITID[self.benefitID])

    def GetHintText(self):
        ownerName = cfg.eveowners.Get(self.standingData.GetOwnerID2()).ownerName
        hintText = GetByLabel(standingUIConst.HINTS_BY_BENEFITID[self.benefitID], ownerName=ownerName)
        return hintText
