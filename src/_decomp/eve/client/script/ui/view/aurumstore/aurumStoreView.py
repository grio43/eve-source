#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\aurumStoreView.py
import logging
import blue
import carbonui.const as uiconst
import localization
import locks
import uthread
from carbonui.primitives.fill import Fill
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.services.viewStateSvc import View
from eve.client.script.ui.view.aurumstore.aurumStoreContainer import AurumStoreContainer
from eve.client.script.ui.view.aurumstore.loadingPanel import LoadingPanel
from eve.client.script.ui.view.viewStateConst import ViewOverlay
from eveexceptions import ExceptionEater
logger = logging.getLogger(__name__)
_SearchLock = locks.RLock()
STORE_REQUEST_TIMEOUT = 60

class AurumStoreView(View):
    __notifyevents__ = ['OnShowUI']
    __suppressedOverlays__ = {ViewOverlay.SidePanels, ViewOverlay.Target, ViewOverlay.ShipUI}
    __subLayers__ = [('l_vgsabovesuppress', None, None), ('l_vgssuppress', None, None)]
    _debug = False

    def __init__(self, *args, **kwargs):
        super(AurumStoreView, self).__init__(*args, **kwargs)
        self.loadingPanel = None
        self.isLoaded = False
        self._immersiveAudioOverlay = None

    def IsLoaded(self):
        return self.isLoaded

    def LoadView(self, **kwargs):
        self.isLoaded = False
        View.LoadView(self, **kwargs)
        if not self._debug:
            uicore.layer.main.display = False
        uicore.layer.abovemain.display = False
        self._SearchTasklet = None
        categoryId = kwargs.get('categoryId', None)
        typeIds = kwargs.get('typeIds', None)
        categoryTag = kwargs.get('categoryTag', None)
        uthread.new(self.SetupStoreData, categoryId, typeIds, categoryTag)
        sm.GetService('audio').SendUIEvent('store_view_start')
        self._immersiveAudioOverlay = sm.GetService('audio').CreateImmersiveOverlay('aurum_store_view')
        self._immersiveAudioOverlay.set_full_screen()

    def SetupStoreData(self, categoryId = None, typeIds = None, categoryTag = None):
        logger.debug('SetupStoreData')
        if self.loadingPanel and not self.loadingPanel.destroyed:
            self.loadingPanel.Close()
        self.loadingPanel = LoadingPanel(parent=uicore.layer.vgsabovesuppress)
        if session.userid is None:
            logger.warn('SetupStoreData - Session has no userid. Store will be unavailable')
            self.loadingPanel.ShowStoreUnavailable()
            return
        try:
            vgsSvc = sm.GetService('vgsService')
            vgsSvc.ClearCache()
            self.store = vgsSvc.GetStore()
            logger.debug('SetupStoreData - Spawning Get* threads')
            getRootCategoryListTasklet = uthread.newJoinable(self.store.GetRootCategoryList)
            getAccountTasklet = uthread.newJoinable(self.store.GetAccount)
            getOffersTasklet = uthread.newJoinable(self.store.GetOffers)
            logger.debug('SetupStoreData - Creating AurumStoreContainer')
            self.storeContainer = AurumStoreContainer(parent=self.layer, store=self.store)
            logger.debug('SetupStoreData - Joining on Get* threads')
            rootCategoryList = uthread.waitForJoinable(getRootCategoryListTasklet, timeout=STORE_REQUEST_TIMEOUT)
            account = uthread.waitForJoinable(getAccountTasklet, timeout=STORE_REQUEST_TIMEOUT)
            aurumAmount = account.GetAurumBalance()
            gemAmount = account.GetGemBalance()
            uthread.waitForJoinable(getOffersTasklet, timeout=STORE_REQUEST_TIMEOUT)
            logger.debug('SetupStoreData - Populating UI')
            self.storeContainer.SetCategories(rootCategoryList)
            if typeIds:
                self.storeContainer.LoadTypeIdPage(typeIds)
            if categoryId:
                self.ShowCategory(categoryId)
            elif categoryTag:
                self.SelectCategoryByCategoryTag(categoryTag)
            else:
                self.storeContainer.LoadLandingPage()
            self.viewOpenedTimer = sm.GetService('viewState').lastViewOpenTime
            self.SubscribeToStoreEvents()
        except uthread.TaskletWaitTimeout:
            logger.warn('SetupStoreData timed out, store will be unavailable')
            self.loadingPanel.ShowStoreUnavailable(localization.GetByLabel('UI/VirtualGoodsStore/StoreUnavailableTimeout'))
            raise
        except Exception as e:
            message = None
            logger.warn('SetupStoreData - Store loading failed')
            self.loadingPanel.ShowStoreUnavailable(message)
            raise

        logger.debug('SetupStoreData - Loading completed successfully, showing store')
        uicore.animations.FadeOut(self.loadingPanel, duration=0.5, timeOffset=0.5, sleep=True)
        self.loadingPanel.Close()
        self.storeContainer.SetAUR(aurumAmount)
        self.storeContainer.SetGEM(gemAmount)
        self.isLoaded = True

    def ShowCategory(self, categoryId):
        if categoryId is None or categoryId not in self.store.GetCategories():
            return
        self.storeContainer.SelectCategory(categoryId)

    def SelectCategoryByCategoryTag(self, categoryTag):
        categoryId = self.store.GetCategoryIdByCategoryTag(categoryTag)
        self.ShowCategory(categoryId)

    def SubscribeToStoreEvents(self):
        self.store.GetAccount().SubscribeToAurumBalanceChanged(self.storeContainer.SetAUR)
        self.store.GetAccount().SubscribeToGemBalanceChanged(self.storeContainer.SetGEM)

    def UnsubscribeFromStoreEvents(self):
        try:
            self.store.GetAccount().UnsubscribeFromAurumBalanceChanged(self.storeContainer.SetAUR)
            self.store.GetAccount().UnsubscribeFromGemBalanceChanged(self.storeContainer.SetGEM)
        except Exception:
            self.LogError('Error while unsubscribing from store events')

    def UnloadView(self):
        self.isLoaded = False
        View.UnloadView(self)
        sm.GetService('audio').SendUIEvent('store_view_end')
        if self._immersiveAudioOverlay:
            self._immersiveAudioOverlay.close()
        self.UnsubscribeFromStoreEvents()
        sm.GetService('vgsService').GetUiController().CheckCloseOffer()
        if getattr(self, 'storeContainer', None) is not None:
            self.storeContainer.Close()
        uicore.layer.main.display = True
        uicore.layer.abovemain.display = True

    def OnShowUI(self):
        if not self._debug:
            uicore.layer.main.display = False

    def SetupSuppressLayer(self):
        if len(uicore.layer.vgssuppress.children) == 0:
            Fill(parent=uicore.layer.vgssuppress, color=Color.BLACK)
        uicore.layer.vgssuppress.opacity = 0.0
        uicore.layer.vgssuppress.state = uiconst.UI_DISABLED

    def ActivateSuppressLayer(self, duration = 0.25, clickCallback = None, callback = None):
        self.SetupSuppressLayer()
        uicore.layer.vgssuppress.state = uiconst.UI_NORMAL
        if clickCallback is not None:
            uicore.layer.vgssuppress.OnClick = clickCallback
        uicore.animations.FadeTo(obj=uicore.layer.vgssuppress, startVal=uicore.layer.vgssuppress.opacity, endVal=0.7, duration=duration, callback=callback)

    def DeactivateSuppressLayer(self, duration = 0.25, callback = None):
        uicore.layer.vgssuppress.state = uiconst.UI_DISABLED
        uicore.animations.FadeOut(uicore.layer.vgssuppress, duration=duration, sleep=True, callback=callback)

    def Search(self, searchString):
        if self._SearchTasklet is not None:
            with _SearchLock:
                if self._SearchTasklet is not None:
                    self._SearchTasklet.kill()
        self._SearchTasklet = uthread.new(self._Search, searchString)

    def _GetViewTime(self):
        return blue.os.GetWallclockTime() - self.viewOpenedTimer

    def FormatTimeInterval(self, time):
        return localization.formatters.FormatTimeIntervalShortWritten(time, showFrom='day')

    def _Search(self, searchString):
        blue.pyos.synchro.SleepWallclock(280)
        with _SearchLock:
            offers = self.store.SearchOffers(searchString)
            self._LogSearch(searchString)
            self.storeContainer.SetOffers(offers)

    def _LogStoreEvent(self, columnNames, eventName, *args):
        with ExceptionEater('eventLog'):
            uthread.new(sm.ProxySvc('eventLog').LogClientEvent, 'store', columnNames, eventName, *args)

    def _LogPurchase(self, offerID, quantity, success):
        self._LogStoreEvent(['offerID',
         'quantity',
         'success',
         'viewTime'], 'Purchase', offerID, quantity, success, self._GetViewTime())

    def _LogPurchaseGift(self, offerID, quantity, success, toCharacterID, isGametime = False):
        self._LogStoreEvent(['offerID',
         'quantity',
         'success',
         'toCharacterID',
         'isGametime',
         'viewTime'], 'PurchaseGift', offerID, quantity, success, toCharacterID, isGametime, self.FormatTimeInterval(self._GetViewTime()))

    def _LogOpenOffer(self, offerID):
        self._LogStoreEvent(['offerID', 'viewTime'], 'OpenOffer', offerID, self._GetViewTime())

    def _LogBannerClick(self, imageUrl, actionKey, actionValue):
        self._LogStoreEvent(['imageUrl',
         'actionKey',
         'actionValue',
         'viewTime'], 'BannerClick', imageUrl, actionKey, actionValue, self._GetViewTime())

    def _LogBuyAurum(self, location):
        self._LogStoreEvent(['aurumBalance', 'location', 'viewTime'], 'BuyAurum', self.store.GetAccount().GetAurumBalance(), location, self._GetViewTime())

    def _LogFilterChange(self, filterName):
        self._LogStoreEvent(['filterName', 'viewTime'], 'FilterChange', filterName, self._GetViewTime())

    def _LogSearch(self, searchString):
        self._LogStoreEvent(['searchString', 'viewTime'], 'search', searchString, self._GetViewTime())
