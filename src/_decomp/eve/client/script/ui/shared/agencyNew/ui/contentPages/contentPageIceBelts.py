#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageIceBelts.py
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageResourceHarvesting import ContentPageResourceHarvesting
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.iceBeltInfoContainer import IceBeltInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.tooltips.iceAvailabilityTooltip import IceAvailabilityTooltip
from eve.client.script.ui.shared.agencyNew.ui.tooltips.iceReprocessingTooltip import IceReprocessingTooltip
from localization import GetByLabel

class ContentPageIceBelts(ContentPageResourceHarvesting):
    default_name = 'ContentPageIceBelts'

    def ConstructInfoContainer(self):
        self.infoContainer = IceBeltInfoContainer(parent=self)

    def ConstructTooltips(self):
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/IceAvailability'), tooltipPanelClassInfo=IceAvailabilityTooltip())
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/IceReprocessing'), tooltipPanelClassInfo=IceReprocessingTooltip())
