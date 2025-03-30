#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contextualOffers\client\UI\neocom.py
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from eve.client.script.ui.shared.neocom.neocom.fixedButtonExtension import OnlyShowWhenAvailableExtension
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNodeNotification import BtnDataNodeNotification
from localization import GetByLabel
UNSEEN_OFFERS_NOTIFICATION_ID = 'NewContextualOfferNotification'

class UnseenOffersBtnData(BtnDataNodeNotification):
    default_btnType = neocomConst.BTNTYPE_OFFERS
    default_cmdName = 'OpenContextualOffersWindow'
    default_iconPath = 'res:/UI/Texture/Shared/bracketBorderWindow/offer_neocom_icon.png'
    default_btnID = UNSEEN_OFFERS_NOTIFICATION_ID
    __notifyevents__ = ['OnContextualOffersChanged']

    def OnContextualOffersChanged(self, *args, **kwargs):
        self.OnBadgeCountChanged()

    @property
    def default_label(self):
        return GetByLabel('UI/ContextualOffers/OfferTitle')

    def GetItemCount(self):
        return sm.GetService('contextualOfferSvc').GetNumberOfUnseenOffers()


class UnseenOffersExtension(OnlyShowWhenAvailableExtension):

    def notify_of_offers_changed(self):
        self._update_visibility()
        sm.ScatterEvent('OnContextualOffersChanged', self.get_badge_count())
