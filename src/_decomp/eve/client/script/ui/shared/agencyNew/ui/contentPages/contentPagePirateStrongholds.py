#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPagePirateStrongholds.py
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.pirateStrongholdInfoContainer import PirateStrongholdInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.contentPages.singleColumnContentPage import SingleColumnContentPage
from eve.client.script.ui.shared.agencyNew.ui.tooltips.pirateStrongholdMechanicsTooltip import PirateStrongholdMechanicsTooltip
from localization import GetByLabel

class ContentPagePirateStrongholds(SingleColumnContentPage):

    def ConstructInfoContainer(self):
        self.infoContainer = PirateStrongholdInfoContainer(parent=self, padding=(10, 0, 10, 0))

    def ConstructTooltips(self):
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/PirateStrongholdMechanics'), tooltipPanelClassInfo=PirateStrongholdMechanicsTooltip())
