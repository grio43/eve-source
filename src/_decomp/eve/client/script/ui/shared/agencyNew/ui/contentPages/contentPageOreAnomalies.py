#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageOreAnomalies.py
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageResourceHarvesting import ContentPageResourceHarvesting
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.oreAnomalyInfoContainer import OreAnomalyInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.tooltips.scanningTooltip import ScanningTooltip
from localization import GetByLabel

class ContentPageOreAnomalies(ContentPageResourceHarvesting):
    default_name = 'ContentPageOreAnomalies'

    def ConstructInfoContainer(self):
        self.infoContainer = OreAnomalyInfoContainer(parent=self)

    def ConstructTooltips(self):
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/ProbeScanning'), tooltipPanelClassInfo=ScanningTooltip())
