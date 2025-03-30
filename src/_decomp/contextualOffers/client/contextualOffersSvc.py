#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contextualOffers\client\contextualOffersSvc.py
import carbonui.const as uiconst
from carbon.common.script.sys.service import Service
from contextualOffers.client.UI.omegaOffer.omegaOfferWindow import OmegaOfferWindow
from contextualOffers.client.contextualOfferInnerService import ContextualOfferInnerService
from contextualOffers.client.offerMocks import MockOmegaOfferAvailable, MockDestroyerBundleOfferAvailable, MockDestroyerBundleAndOmegaOfferAvailable
from contextualOffers.client.UI.neocom import UnseenOffersExtension, UnseenOffersBtnData
from contextualOffers.common.contextualOfferDataHelpers import flatten_omega_prepared_message
from carbonui.uicore import uicore
from eve.client.script.ui.shared.neocom.neocom.fixedButtonExtension import SeenItemStorage
OFFER_RECEIVED = 0
OFFER_PURCHASED = 1
SOUND_OFFER_RECEIVED = 'contextual_offer_window_open_play'
SOUND_OFFER_BUY_CLICKED = 'contextual_offer_complete_open_play'
SOUND_OFFER_PURCHASED = 'purchase_success_play'
OFFER_IDS_WITHOUT_BADGING = [1007,
 1008,
 1009,
 1010]

class ContextualOfferService(Service):
    __guid__ = 'svc.contextualOfferSvc'
    __service__ = 'svc.contextualOfferSvc'
    __notifyevents__ = ['OnOfferReceived', 'OnContextualOfferPurchased', 'OnCharacterSessionChanged']

    def Run(self, *args, **kwargs):
        super(ContextualOfferService, self).Run(*args, **kwargs)
        self.innerService = ContextualOfferInnerService(scatterService=sm)
        self.wnd = None
        self.audioService = sm.GetService('audio')
        self.InitializeNeocomButton()

    def InitializeNeocomButton(self):
        self._seenOffersStorage = SeenItemStorage(get_items_function=self.GetOfferNotifications, settings_container=settings.user.ui, settings_key='ContextualOffers_SeenOffers')
        self._neocomOffersNotificationExtension = UnseenOffersExtension(button_data_class=UnseenOffersBtnData, get_badge_count=self.GetNumberOfUnseenOffers, get_item_count=self.GetNumberOfOffers)
        self._neocomOffersNotificationExtension.connect_item_changes(self._seenOffersStorage.on_items_changed)
        sm.GetService('neocom').RegisterFixedButtonExtension(self._neocomOffersNotificationExtension)

    def ClearNeocomButton(self):
        self._neocomOffersNotificationExtension.disconnect_item_changes(self._seenOffersStorage.on_items_changed)
        try:
            sm.GetService('neocom').UnregisterFixedButtonExtension(self._neocomOffersNotificationExtension)
        except ValueError:
            pass

    def OnCharacterSessionChanged(self, _oldCharacterID, newCharacterID):
        self.ClearNeocomButton()
        if newCharacterID:
            self.InitializeNeocomButton()

    def OnOfferReceived(self, offerID, offer):
        self.innerService.OnOfferReceived(offerID, offer)
        self.TrackOfferDelivered(offerID=offerID)
        self.AddOfferNotification(offerID, OFFER_RECEIVED)

    def OnContextualOfferPurchased(self, offerID, purchaseInfo):
        self.innerService.OnPurchaseSuccessReceived(offerID=offerID, purchaseObj=purchaseInfo)
        self.TrackOfferPurchased(offerID=offerID)
        self.RemoveOfferNotification(offerID, OFFER_RECEIVED)
        self._OpenPurchaseConfirmedWindow(purchaseInfo)

    def ShouldShowBadgingForOffer(self, offerID):
        return offerID not in OFFER_IDS_WITHOUT_BADGING

    def GetNumberOfOffers(self):
        return len(self.GetOfferNotifications() or [])

    def GetNumberOfUnseenOffers(self):
        unseenOffers = self._seenOffersStorage.get_unseen()
        availableUnseenOffers = [ offerID for offerID, _ in unseenOffers if self.innerService.IsOfferAvailable(offerID) ]
        return len(availableUnseenOffers)

    def GetOfferNotifications(self):
        return set(self.innerService.GetOfferNotifications())

    def AddOfferNotification(self, offerID, viewType):
        self.innerService.AddOfferNotification(offerID, viewType)
        self.CleanupUnavailableOffers()
        if (offerID, viewType) not in self._seenOffersStorage.seen_items:
            if self.ShouldShowBadgingForOffer(offerID):
                self._seenOffersStorage.mark_as_unseen((offerID, viewType))
            else:
                self._seenOffersStorage.mark_as_seen((offerID, viewType))
        self._neocomOffersNotificationExtension.notify_of_offers_changed()

    def MarkSeenOfferNotification(self, offerID, viewType):
        self._seenOffersStorage.mark_as_seen((offerID, viewType))
        self._neocomOffersNotificationExtension.notify_of_offers_changed()

    def RemoveOfferNotification(self, offerID, viewType):
        self.innerService.RemoveOfferNotification(offerID, viewType)
        self._seenOffersStorage.mark_as_seen((offerID, viewType))
        self._neocomOffersNotificationExtension.notify_of_offers_changed()

    def CleanupUnavailableOffers(self):
        seenOffers = self._seenOffersStorage.seen_items
        unavailableSeenOffers = set([ (offerID, offerType) for offerID, offerType in seenOffers if not self.innerService.IsOfferAvailable(offerID) ])
        self._seenOffersStorage.mark_many_as_unseen(unavailableSeenOffers)

    def GetOffers(self):
        return self.innerService.GetOffers()

    def GetOffer(self, offerID):
        return self.innerService.GetOfferById(offerID)

    def IsOfferAvailable(self, offerID):
        return self.innerService.IsOfferAvailable(offerID)

    def GetPurchasedOffers(self):
        return self.innerService.GetPurchasedOffers()

    def GetPurchasedOffer(self, offerID):
        return self.innerService.GetPurchasedOfferById(offerID)

    def IsPurchaseConfirmed(self, offerID):
        return self.innerService.IsPurchaseConfirmed(offerID)

    def GetLastOfferToken(self):
        unseenOffers = self._seenOffersStorage.get_unseen()
        for offerToken in reversed(self.innerService.GetOfferNotifications()):
            if not unseenOffers or offerToken in unseenOffers:
                return offerToken

    def OpenContextualOffersWindow(self):
        offerToken = self.GetLastOfferToken()
        if offerToken:
            offerID, viewType = offerToken
            if self.IsOfferAvailable(offerID):
                offerInfo = self.GetOffer(offerID)
                self._OpenPurchaseWindow(offerInfo)
                return
        self.LogWarn('Trying to open Contextual Offers window when there are no offers available')

    def DisplayOfferWindowIfActive(self, offerID):
        if self.IsPurchaseConfirmed(offerID):
            purchaseInfo = self.GetPurchasedOffer(offerID)
            self._OpenPurchaseConfirmedWindow(purchaseInfo)
        elif self.IsOfferAvailable(offerID):
            offerInfo = self.GetOffer(offerID)
            self._OpenPurchaseWindow(offerInfo)
        else:
            self.LogError('Trying to open Contextual Offer window when there are no offers')

    def _OpenPurchaseWindow(self, offerInfo):
        offerID = offerInfo['offerID']
        offerInfo = flatten_omega_prepared_message(offerInfo)
        self.TrackOfferIDSeen(offerID)
        self._OpenWindow(OFFER_RECEIVED, offerInfo)

    def _OpenPurchaseConfirmedWindow(self, purchaseInfo):
        offerID = purchaseInfo['offerID']
        self.TrackOfferPurchasedSeen(offerID)
        if self.wnd and not self.wnd.destroyed and self.wnd.state != uiconst.UI_HIDDEN:
            self.wnd.CloseButtonClicked()

    def _OpenWindow(self, viewType, viewInfo):
        offerID = viewInfo['offerID']
        isNewWindow = not self.wnd or self.wnd.destroyed
        if isNewWindow:
            self.wnd = OmegaOfferWindow.Open(onOpenCallback=lambda : self._OnWindowOpened(offerID, viewType), onCloseCallback=lambda : self._OnWindowClosed(offerID, viewType))
            self.wnd.sr.underlay.SetState(uiconst.UI_HIDDEN)
            self.innerService.SubscribeToOfferTimer(offerID, self.wnd, self.wnd.OnTimerUpdated)
        if viewType == OFFER_RECEIVED:
            self.audioService.SendUIEvent(SOUND_OFFER_RECEIVED)
            self.wnd.OpenPurchaseView(viewInfo)
        elif viewType == OFFER_PURCHASED:
            self.audioService.SendUIEvent(SOUND_OFFER_PURCHASED)
            self.wnd.OpenConfirmationView(viewInfo)
        else:
            self.LogWarn('Failed to open Contextual Offers window, requested viewType is not supported. Defaulting to confirmation view.')
            self.wnd.OpenConfirmationView(viewInfo)
        if isNewWindow:
            self.wnd.ShowDialog(modal=True, state=uiconst.UI_PICKCHILDREN)

    def _OnWindowOpened(self, offerID, viewType):
        self.MarkSeenOfferNotification(offerID, OFFER_RECEIVED)

    def _OnWindowClosed(self, offerID, viewType):
        if viewType == OFFER_RECEIVED:
            self.TrackOfferClosed(offerID)
        self.innerService.UnsubscribeFromOfferTimer(offerID, self.wnd)

    def OnBuyClicked(self, offerID):
        self.audioService.SendUIEvent(SOUND_OFFER_BUY_CLICKED)
        self.TrackOfferPurchaseClicked(offerID=offerID)
        self._RedirectToContextualOffersWeb(offerID)

    def _RedirectToContextualOffersWeb(self, offerID):
        try:
            offerinfo = self.innerService.GetOfferById(offerID)
            offerURL = offerinfo['purchaseStep']['PurchaseURL']
            uicore.cmd.BuyContextualOfferOnline(offerURL, offerID)
        except Exception:
            self.LogException('Failed to direct to purchase URL for the offer (offerID: %s)' % offerID)
            self._RedirectToSpecialOffersWeb()

    def _RedirectToSpecialOffersWeb(self):
        try:
            uicore.cmd.ViewSpecialOffersOnline(origin='contextualofferwindow')
        except Exception:
            self.LogException('Failed to direct to Special Offers URL')
            raise

    def TrackOfferDelivered(self, offerID):
        sm.RemoteSvc('contextualOfferMgr').TrackOfferDelivered(offerID)

    def TrackOfferIDSeen(self, offerID):
        sm.RemoteSvc('contextualOfferMgr').TrackOfferSeen(offerID)

    def TrackOfferPurchaseClicked(self, offerID):
        sm.RemoteSvc('contextualOfferMgr').TrackOfferBuyPress(offerID)

    def TrackOfferClosed(self, offerID):
        sm.RemoteSvc('contextualOfferMgr').TrackOfferClosed(offerID)

    def TrackOfferPurchased(self, offerID):
        sm.RemoteSvc('contextualOfferMgr').TrackOfferPurchased(offerID)

    def TrackOfferPurchasedSeen(self, offerID):
        sm.RemoteSvc('contextualOfferMgr').TrackOfferPurchasedSeen(offerID)

    def Debug_ClearOffers(self):
        self.innerService.Debug_ClearOffers()
        self._seenOffersStorage.clear_all()
        self._neocomOffersNotificationExtension.notify_of_offers_changed()

    def Debug_AddMockOffer1(self):
        self.OnOfferReceived(1, MockOmegaOfferAvailable())

    def Debug_AddMockOffer2(self):
        self.OnOfferReceived(3, MockDestroyerBundleOfferAvailable())

    def Debug_AddMockOffer3(self):
        self.OnOfferReceived(4, MockDestroyerBundleAndOmegaOfferAvailable())
