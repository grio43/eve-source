#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\factionWarfare\systemRewardsTooltip.py
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.util.color import Color
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from evedungeons.common.constants import facWarNoviceDungeonLPGranted, facWarSmallDungeonLPGranted, facWarMediumDungeonLPGranted, facWarLargeDungeonLPGranted
from localization import GetByLabel

class SystemRewardsTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric2ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/RewardPerComplexType'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH, colSpan=2)
        self.tooltipPanel.AddSpacer(height=10, colSpan=2)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/BiggerComplexBiggerReward'), wrapWidth=280, colSpan=2)
        self.tooltipPanel.AddSpacer(height=10, colSpan=2)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/DefendersGetLessLP'), wrapWidth=280, colSpan=2)
        return self.tooltipPanel
