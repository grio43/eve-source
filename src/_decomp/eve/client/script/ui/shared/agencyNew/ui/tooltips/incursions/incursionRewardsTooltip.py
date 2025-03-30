#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\incursions\incursionRewardsTooltip.py
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.shared.agencyNew.ui.controls.warningContainer import WarningContainer
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eveuniverse.security import securityClassZeroSec
from grouprewards import REWARD_TYPE_ISK, REWARD_TYPE_LP
from grouprewards.data import get_max_reward_value_by_reward_type, get_group_reward, get_optimal_player_count_for_table, get_tables_for_security_class, get_group_reward_min_max_player_count_by_security_class
from localization import GetByLabel
from talecommon.const import REWARD_SCOUT, REWARD_VANGUARD, REWARD_ASSAULT, REWARD_HQ
SITE_ICON_BY_REWARD_TYPE = {REWARD_SCOUT: 'res:/UI/Texture/classes/Incursions/incursionStaging.png',
 REWARD_VANGUARD: 'res:/UI/Texture/classes/Incursions/incursionLight.png',
 REWARD_ASSAULT: 'res:/UI/Texture/classes/Incursions/IncursionMedium.png',
 REWARD_HQ: 'res:/UI/Texture/classes/Incursions/incursionHeavy.png'}
SITE_NAME_BY_REWARD_TYPE = {REWARD_SCOUT: 'UI/Agency/Tooltips/Encounters/Incursions/StagingSite',
 REWARD_VANGUARD: 'UI/Agency/Tooltips/Encounters/Incursions/VanguardSite',
 REWARD_ASSAULT: 'UI/Agency/Tooltips/Encounters/Incursions/AssaultSite',
 REWARD_HQ: 'UI/Agency/Tooltips/Encounters/Incursions/HeadquartersSite'}

class IncursionRewardsTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.columns = 7
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/SiteRewards'), colSpan=self.tooltipPanel.columns)
        self.CreateWarningContainer(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/SiteRewardWarning'))
        self.tooltipPanel.AddSpacer(height=5, colSpan=self.tooltipPanel.columns)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/SiteType'))
        self.tooltipPanel.AddCell(Line(align=uiconst.TOLEFT), cellPadding=(5, 0, 5, 0))
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/MaximumISK'))
        self.tooltipPanel.AddCell(Line(align=uiconst.TOLEFT), cellPadding=(5, 0, 5, 0))
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/MaximumLP'))
        self.tooltipPanel.AddCell(Line(align=uiconst.TOLEFT), cellPadding=(5, 0, 5, 0))
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/OptimalPilots'), width=60)
        self.tooltipPanel.AddDivider()
        self.CreateRewardRow(REWARD_SCOUT)
        self.CreateRewardRow(REWARD_VANGUARD)
        self.CreateRewardRow(REWARD_ASSAULT)
        self.CreateRewardRow(REWARD_HQ)
        self.tooltipPanel.AddSpacer(height=5, colSpan=self.tooltipPanel.columns)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/FleetSizeRestrictions'), colSpan=self.tooltipPanel.columns)
        self.CreateWarningContainer(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/FleetSizeWarning'))
        self.tooltipPanel.AddSpacer(height=5, colSpan=self.tooltipPanel.columns)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/SiteType'))
        self.tooltipPanel.AddCell(Line(align=uiconst.TOLEFT), cellPadding=(5, 0, 5, 0))
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/MinimumFleetSize'))
        self.tooltipPanel.AddCell(Line(align=uiconst.TOLEFT), cellPadding=(5, 0, 5, 0))
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/MaximumFleetSize'), colSpan=3)
        self.tooltipPanel.AddDivider()
        self.CreateFleetSizeRow(REWARD_SCOUT)
        self.CreateFleetSizeRow(REWARD_VANGUARD)
        self.CreateFleetSizeRow(REWARD_ASSAULT)
        self.CreateFleetSizeRow(REWARD_HQ)
        return self.tooltipPanel

    def CreateWarningContainer(self, text):
        warningContainer = WarningContainer(align=uiconst.CENTERTOP, color=eveColor.WARNING_ORANGE, text=text)
        self.tooltipPanel.AddCell(warningContainer, colSpan=self.tooltipPanel.columns)

    def CreateFleetSizeRow(self, reward_id):
        minSize, maxSize = get_group_reward_min_max_player_count_by_security_class(reward_id, securityClassZeroSec)
        self.CreateSeverityIconLabel(reward_id)
        self.tooltipPanel.AddCell(Line(align=uiconst.TOLEFT), cellPadding=5)
        self.tooltipPanel.AddLabelMedium(text=minSize, align=uiconst.CENTERLEFT)
        self.tooltipPanel.AddCell(Line(align=uiconst.TOLEFT), cellPadding=5)
        self.tooltipPanel.AddLabelMedium(text=maxSize, align=uiconst.CENTERLEFT, colSpan=3)

    def CreateSeverityIconLabel(self, reward_id):
        severityIconLabelContainer = ContainerAutoSize(align=uiconst.CENTERLEFT, height=32)
        Sprite(parent=Container(parent=severityIconLabelContainer, align=uiconst.TOLEFT, width=32), align=uiconst.CENTER, width=32, height=32, texturePath=SITE_ICON_BY_REWARD_TYPE[reward_id])
        EveLabelMedium(parent=ContainerAutoSize(parent=severityIconLabelContainer, align=uiconst.TOLEFT, left=5), align=uiconst.CENTERLEFT, text=GetByLabel(SITE_NAME_BY_REWARD_TYPE[reward_id]))
        self.tooltipPanel.AddCell(severityIconLabelContainer)

    def CreateRewardRow(self, reward_id):
        self.CreateSeverityIconLabel(reward_id)
        line = Line(align=uiconst.TOLEFT)
        self.tooltipPanel.AddCell(line, cellPadding=5)
        self.tooltipPanel.AddLabelMedium(text=FmtAmt(get_max_reward_value_by_reward_type(group_reward_id=reward_id, reward_type_id=REWARD_TYPE_ISK)), align=uiconst.CENTERLEFT)
        line = Line(align=uiconst.TOLEFT)
        self.tooltipPanel.AddCell(line, cellPadding=5)
        self.tooltipPanel.AddLabelMedium(text=FmtAmt(get_max_reward_value_by_reward_type(group_reward_id=reward_id, reward_type_id=REWARD_TYPE_LP)), align=uiconst.CENTERLEFT)
        line = Line(align=uiconst.TOLEFT)
        self.tooltipPanel.AddCell(line, cellPadding=5)
        minOptimalPlayers, maxOptimalPlayers = self.GetOptimalPlayerRange(reward_id)
        self.tooltipPanel.AddLabelMedium(text='%s-%s' % (minOptimalPlayers, maxOptimalPlayers), align=uiconst.CENTERLEFT)

    def GetOptimalPlayerRange(self, groupRewardID):
        allRewardTables = get_group_reward(groupRewardID).tables
        nullSecTables = get_tables_for_security_class(allRewardTables, securityClassZeroSec) if groupRewardID != REWARD_SCOUT else allRewardTables
        return get_optimal_player_count_for_table(nullSecTables[0])
