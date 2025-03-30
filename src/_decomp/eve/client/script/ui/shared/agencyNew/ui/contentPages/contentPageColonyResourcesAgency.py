#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageColonyResourcesAgency.py
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew.ui.contentPages.singleColumnContentPage import SingleColumnContentPage
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.colonyResourcesAgencyInfoContainer import ColonyResourceAgencyInfoContainer
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew import agencyConst

class ContentPageColonyResourcesAgency(SingleColumnContentPage):
    default_name = 'ContentPageColonyResourcesAgency'
    contentGroupID = contentGroupConst.contentGroupColonyResourcesAgency

    def ConstructInfoContainer(self):
        self.infoContainer = ColonyResourceAgencyInfoContainer(parent=self)

    def ConstructInformationContainer(self):
        self.informationContainer = None

    def GetContentPiecesCapped(self):
        return self.GetContentPieces()[:agencyConst.COLONY_RESOURCE_AGENCY_PIECES_MAX]
