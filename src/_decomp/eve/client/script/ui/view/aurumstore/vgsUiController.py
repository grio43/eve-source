#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\vgsUiController.py
import logging
import blue
import carbonui.const as uiconst
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.uicore import uicore
from eve.client.script.ui.util.uiComponents import RunThreadOnce
from eve.client.script.ui.view.aurumstore.nesFastCheckoutContainer import NesFastCheckoutContainer
from eve.client.script.ui.view.aurumstore.vgsDetailContainer import VgsDetailContainer
from eve.client.script.ui.view.viewStateConst import ViewState
from fastcheckout.const import FROM_NES_HEADER
logger = logging.getLogger(__name__)
OPEN_OFFER_THREAD_KEY = 'OPEN_OFFER'
CLOSE_OFFER_THREAD_KEY = 'CLOSE_OFFER'
OPEN_AURUM_STORE_THREAD_KEY = 'OPEN_AURUM_STORE'
MINIMUM_PROGRESS_DISPLAY_TIME = 1.2 * const.SEC
OFFER_ADDED_TO_REDEEMING_QUEUE_TIME = 0.75
REDEEMING_BUTTON_SHOW_TIME = 2

class VgsUiController(object):

    def __init__(self, vgsService, viewStateService):
        self.viewState = viewStateService
        self.vgsService = vgsService
        self.fastCheckoutClientService = sm.GetService('fastCheckoutClientService')
        self.view = self.viewState.GetView(ViewState.VirtualGoodsStore)
        self.detailContainer = None
        self.buyIsInProgress = False
        self.nesFastCheckoutStoreView = None
        self.isInFastCheckoutWindow = False
        self.featuredOffers = []

    @RunThreadOnce(OPEN_OFFER_THREAD_KEY)
    def ShowOffer(self, offerId, categoryId = None):
        if self.buyIsInProgress:
            return
        self._ShowOffer(offerId, uicore.layer.vgsabovesuppress)
        if self.viewState.IsViewActive(ViewState.VirtualGoodsStore):
            self.view.ShowCategory(categoryId)
        else:
            self.viewState.ActivateView(ViewState.VirtualGoodsStore, categoryId=categoryId)

    def ShowOfferInWindow(self, offerId):
        self._ShowOffer(offerId, uicore.layer.abovemain)
        self.view.ActivateSuppressLayer(duration=0.3, clickCallback=self.CloseOffer)

    def _ShowOffer(self, offerId, parent):
        self.CheckCloseOffer()
        offer = self.vgsService.GetStore().GetOffer(offerId)
        PlaySound('store_click')
        self.detailContainer = VgsDetailContainer(parent=parent, align=uiconst.TOALL, opacity=0.0, vgsUiController=self, offer=offer, aurumBalance=self.vgsService.GetStore().GetAccount().GetAurumBalance(), gemBalance=self.vgsService.GetStore().GetAccount().GetGemBalance())
        self.view._LogOpenOffer(offerId)
        uicore.animations.FadeTo(self.detailContainer, 0.0, 1.0, duration=0.3, sleep=True)
        return offer

    @RunThreadOnce(OPEN_AURUM_STORE_THREAD_KEY)
    def OpenFastCheckoutWindow(self):
        self.Close()
        self.nesFastCheckoutStoreView = NesFastCheckoutContainer(parent=uicore.layer.vgsabovesuppress, logContext=FROM_NES_HEADER)
        self.view.ActivateSuppressLayer(duration=0.5, clickCallback=self.fastCheckoutClientService.close_fast_checkout_nes, callback=self.SetFastCheckoutWindowActive())

    def CloseFastCheckoutWindow(self):
        self.SetFastCheckoutWindowInactive()
        if self.nesFastCheckoutStoreView is not None:
            self.nesFastCheckoutStoreView.Close()
            self.nesFastCheckoutStoreView = None
            self.view.DeactivateSuppressLayer(duration=0.25)
        self.fastCheckoutClientService.close_fast_checkout_popup()

    def Close(self):
        self.CheckCloseOffer()
        self.CloseFastCheckoutWindow()

    def CanClose(self):
        return self.detailContainer is not None and not self.detailContainer.destroyed and not self.buyIsInProgress

    def CheckCloseOffer(self):
        if not self.CanClose():
            return
        logger.debug('Force closing offer')
        self.view.storeContainer.redeemingPanel.SetListenToRedeemQueueUpdatedEvents(True)
        self.view.storeContainer.redeemingPanel.UpdateDisplay(animate=False)
        self.detailContainer.fakeRedeemingPanel.CollapsePanel(animate=False)
        self.detailContainer.Close()
        self.view.DeactivateSuppressLayer(duration=0.0)

    @RunThreadOnce(CLOSE_OFFER_THREAD_KEY)
    def CloseOffer(self):
        if not self.CanClose():
            return
        closeDuration = 0.25
        self.view.storeContainer.redeemingPanel.SetListenToRedeemQueueUpdatedEvents(True)
        self.view.storeContainer.redeemingPanel.UpdateDisplay(animate=False)
        self.detailContainer.fakeRedeemingPanel.CollapsePanel(duration=closeDuration)
        self.detailContainer.PrepareClose()
        uicore.animations.FadeOut(self.detailContainer.offerContainer, duration=closeDuration)
        self.view.DeactivateSuppressLayer(duration=closeDuration, callback=self.detailContainer.Close)

    def SetFastCheckoutWindowActive(self):
        self.isInFastCheckoutWindow = True

    def SetFastCheckoutWindowInactive(self):
        self.isInFastCheckoutWindow = False

    def IsFastCheckoutWindowActive(self):
        return self.isInFastCheckoutWindow

    def _LogPurchase(self, offer, quantity, success, toCharacterID):
        isGametime = self.vgsService.store.IsGametimeOffer(offer)
        if toCharacterID:
            self.view._LogPurchaseGift(offer.id, quantity, success, toCharacterID, isGametime=isGametime)
        else:
            self.view._LogPurchase(offer.id, quantity, success)

    def BuyOffer(self, offer, currency, quantity = 1, toCharacterID = None, message = None):
        self.vgsService.LogInfo('VgsUiController.BuyOffer', offer, quantity)
        self.buyIsInProgress = True
        try:
            self.detailContainer.SwitchToProgressPanel()
            startTime = blue.os.GetWallclockTime()
            result = None
            try:
                result = self.vgsService.GetStore().BuyOffer(offer, currency=currency, qty=quantity, toCharacterID=toCharacterID, message=message)
                blue.pyos.synchro.SleepUntilWallclock(startTime + MINIMUM_PROGRESS_DISPLAY_TIME)
            finally:
                success = bool(result)
                self._LogPurchase(offer, quantity, success, toCharacterID)
                if success:
                    self.detailContainer.SwitchToSuccessPanel(quantity, toCharacterID)
                else:
                    self.detailContainer.SwitchToFailurePanel()

        finally:
            self.buyIsInProgress = False
            self.view.storeContainer.OnOfferPurchase(offer.id)

    def SetFeaturedOffers(self, offerIDs = None):
        if self.featuredOffers == offerIDs:
            return
        self.featuredOffers = offerIDs or []
        try:
            self.view.storeContainer.SetFeaturedOffers(offerIDs)
        except AttributeError:
            pass

    def GetFeaturedOffers(self):
        return self.featuredOffers
