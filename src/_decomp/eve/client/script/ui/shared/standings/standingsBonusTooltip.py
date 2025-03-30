#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\standings\standingsBonusTooltip.py
import localization
from carbonui import uiconst
from carbonui.util.color import Color
from eve.client.script.ui.control import tooltips
from eve.client.script.ui.shared.shipTree.infoBubble import SkillEntry
from eve.client.script.ui.shared.standings.standingsUtil import GetStandingChangeFormatted
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper

class StandingBonusTooltip(TooltipBaseWrapper):

    def __init__(self, standingData):
        super(StandingBonusTooltip, self).__init__()
        self.standingData = standingData
        self.skillSvc = sm.GetService('skills')

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.state = uiconst.UI_NORMAL
        self.tooltipPanel.LoadGeneric2ColumnTemplate()
        self.tooltipPanel.AddLabelValue(localization.GetByLabel('UI/Standings/StandingsTooltipBase'), round(self.standingData.standing2to1, 2), valueColor=Color.GRAY5)
        self.tooltipPanel.AddSpacer(1, 10, 2)
        skillTypeID = self.standingData.GetSkillTypeID2To1()
        if skillTypeID:
            skillLevel = self.skillSvc.MySkillLevel(skillTypeID)
            self.tooltipPanel.AddLabelValue(localization.GetByLabel('UI/Standings/StandingTooltipSkillBonus'), GetStandingChangeFormatted(self.standingData.GetStandingBonus2To1()))
            self.tooltipPanel.AddRow(rowClass=SkillEntry, typeID=skillTypeID, level=skillLevel, showLevel=False, skillBarPadding=(24, 0, 0, 0), cellPadding=(0, 0, 0, 0), textPadding=(0, 0, 0, 0))
            self.tooltipPanel.AddSpacer(1, 8, 2)
        self.tooltipPanel.AddLabelMedium(text=localization.GetByLabel('Tooltips/CharacterSheet/Standings') + ':', align=uiconst.CENTERLEFT, bold=True, cellPadding=(0, 0, 7, 0))
        self.tooltipPanel.AddLabelMedium(text=round(self.standingData.GetStanding2To1(), 2), align=uiconst.CENTERRIGHT, colSpan=1, cellPadding=(7, 0, 0, 0), bold=True)
        return self.tooltipPanel
