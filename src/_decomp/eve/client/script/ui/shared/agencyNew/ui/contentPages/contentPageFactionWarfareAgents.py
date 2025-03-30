#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageFactionWarfareAgents.py
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageAgents import ContentPageAgents
from eve.client.script.ui.shared.agencyNew.ui.tooltips.factionWarfare.agentRewardsTooltip import FactionWarfareAgentRewardsTooltip
from localization import GetByLabel

class ContentPageFactionWarfareAgents(ContentPageAgents):
    default_name = 'ContentPageFactionWarfareAgents'

    def ConstructTooltips(self):
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/FactionWarfare/MissionRewards'), tooltipPanelClassInfo=FactionWarfareAgentRewardsTooltip())
