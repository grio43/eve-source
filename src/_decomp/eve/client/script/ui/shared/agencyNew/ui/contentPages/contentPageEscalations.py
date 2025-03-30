#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageEscalations.py
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.escalationInfoContainer import EscalationInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.contentPages.singleColumnContentPage import SingleColumnContentPage

class ContentPageEscalations(SingleColumnContentPage):

    def ConstructInfoContainer(self):
        self.infoContainer = EscalationInfoContainer(parent=self, width=450)
