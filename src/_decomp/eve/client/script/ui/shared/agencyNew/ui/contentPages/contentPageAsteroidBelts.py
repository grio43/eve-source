#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageAsteroidBelts.py
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageResourceHarvesting import ContentPageResourceHarvesting
from eve.client.script.ui.shared.agencyNew.ui.tooltips.mineralAvailabilityTooltip import MineralAvailabilityTooltip
from eve.client.script.ui.shared.agencyNew.ui.tooltips.oreAvailabilityTooltip import OreAvailabilityTooltip
from localization import GetByLabel

class ContentPageAsteroidBelts(ContentPageResourceHarvesting):
    default_name = 'ContentPageAsteroidBelts'

    def ConstructTooltips(self):
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/OreAvailability'), tooltipPanelClassInfo=OreAvailabilityTooltip(), top=5)
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Common/ItemTypes/Minerals'), tooltipPanelClassInfo=MineralAvailabilityTooltip(), top=5)
