#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPagePirateIncursions.py
from carbonui import TextBody, uiconst
from localization import GetByLabel
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.pirateInsurgencyInfoContainer import PirateInsurgencyInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.contentPages.singleColumnContentPage import SingleColumnContentPage
from pirateinsurgency.const import CAMPAIGN_STATE_ACTIVE

class ContentPagePirateIncursions(SingleColumnContentPage):
    default_name = 'ContentPagePirateIncursions'

    def ConstructInfoContainer(self):
        self.infoContainer = PirateInsurgencyInfoContainer(parent=self)
        self.insurgencyCampaignSvc = sm.GetService('insurgencyCampaignSvc')

    def ConstructInformationContainer(self):
        self.informationContainer = None

    def UpdateNumResultsLabel(self):
        if len(self.cards) > 0:
            text = GetByLabel('UI/Agency/ShowingXResults', numResults=len(self.cards))
        else:
            text = GetByLabel('UI/Inflight/Scanner/FilteredResults')
            snapshots = self.insurgencyCampaignSvc.GetCurrentCampaignSnapshots_Memoized()
            self.CheckIfNoActiveInsurgency(snapshots)
        self.scrollSection.SetText(text)

    def CheckIfNoActiveInsurgency(self, snapshots):
        if snapshots is None:
            self.ShowNoActiveInsurgency()
        else:
            numberOfActiveInsurgencies = 0
            for snapshot in snapshots:
                if snapshot.fsmState == CAMPAIGN_STATE_ACTIVE:
                    numberOfActiveInsurgencies += 1

            if numberOfActiveInsurgencies == 0:
                self.ShowNoActiveInsurgency()

    def ShowNoActiveInsurgency(self):
        self.label = TextBody(name='label', parent=self.contentScroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/PirateIncursions/NoActiveInsurgency'), padding=5)
