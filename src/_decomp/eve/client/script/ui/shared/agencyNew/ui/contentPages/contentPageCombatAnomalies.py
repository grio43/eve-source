#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageCombatAnomalies.py
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.combatAnomalyInfoContainer import CombatAnomalyInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.contentPages.singleColumnContentPage import SingleColumnContentPage
from eve.client.script.ui.shared.agencyNew.ui.tooltips.combatSiteTypesTooltip import CombatSiteTypesTooltip
from localization import GetByLabel

class ContentPageCombatAnomalies(SingleColumnContentPage):
    default_name = 'ContentPageCombatAnomalies'

    def ConstructInfoContainer(self):
        self.infoContainer = CombatAnomalyInfoContainer(parent=self)

    def ConstructTooltips(self):
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/CombatSiteTypes'), tooltipPanelClassInfo=CombatSiteTypesTooltip())
