#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageFactionWarfareSystems.py
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.factionWarfareSystemInfoContainer import FactionWarfareSystemInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.contentPages.singleColumnContentPage import SingleColumnContentPage
from eve.client.script.ui.shared.agencyNew.ui.tooltips.factionWarfare.complexTypeTooltip import ComplexTypesTooltip
from eve.client.script.ui.shared.agencyNew.ui.tooltips.factionWarfare.systemRewardsTooltip import SystemRewardsTooltip
from eve.client.script.ui.shared.agencyNew.ui.tooltips.factionWarfare.systemUpgradesTooltip import SystemUpgradesTooltip
from localization import GetByLabel

class ContentPageFactionWarfareSystems(SingleColumnContentPage):
    default_name = 'ContentPageFactionWarfareSystems'

    def ConstructInfoContainer(self):
        self.infoContainer = FactionWarfareSystemInfoContainer(parent=self)

    def ConstructTooltips(self):
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/FactionWarfare/systemUpgrades'), tooltipPanelClassInfo=SystemUpgradesTooltip())
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/FactionWarfare/complexTypes'), tooltipPanelClassInfo=ComplexTypesTooltip())
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/FactionWarfare/systemRewards'), tooltipPanelClassInfo=SystemRewardsTooltip())
