#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\vgsService.py
import logging
import threadutils
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.service import Service
from carbonui.uicore import uicore
from eve.client.script.ui.view.aurumstore.specialNeocomButton import AurumStoreNeocomButtonExtension
from eve.client.script.ui.view.aurumstore.vgsUiController import VgsUiController
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.common.lib.vgsConst import CATEGORYTAG_GAMETIME
from eveexceptions import UserError
from globalConfig import GetFakeVgsEnabled
import locks
from localization import GetByLabel
from vgs.client.store import Store
from vgs.client.vgsClient import VgsClient
log = logging.getLogger(__name__)

class VgsService(Service):
    __guid__ = 'svc.vgsService'
    __servicename__ = 'vgsSvc'
    __displayName__ = 'Vgs Service'
    __startupdependencies__ = ['neocom',
     'redeem',
     'viewState',
     'machoNet']
    __notifyevents__ = ['OnAurumChangeFromVgs',
     'OnGemChangeFromVgs',
     'OnRedeemingTokensUpdated',
     'OnSessionChanged',
     'OnSessionReset',
     'OnUIScalingChange',
     'OnGlobalConfigChanged']

    def __init__(self):
        super(VgsService, self).__init__()
        self.vgsClient = None
        self.store = None
        self.uiController = None
        self.isTestingEnabled = None
        self._neoComButtonExtension = None

    def Run(self, memStream = None):
        self.LogInfo('Starting Vgs Service')
        self.Initialize()
        self.isTestingEnabled = GetFakeVgsEnabled(self.machoNet)

    @threadutils.threaded
    def RegisterNeoComButtonExtension(self):
        if self._neoComButtonExtension is not None:
            return
        self._neoComButtonExtension = AurumStoreNeocomButtonExtension()
        self.neocom.RegisterFixedButtonExtension(self._neoComButtonExtension)

    def UnregisterNeoComButtonExtension(self):
        if self._neoComButtonExtension is not None:
            try:
                self.neocom.UnregisterFixedButtonExtension(self._neoComButtonExtension)
            except ValueError:
                pass

            self._neoComButtonExtension = None

    def Initialize(self):
        self.vgsClient = VgsClient()
        self.store = Store(self.vgsClient, lockImpl=locks.Lock)
        self.uiController = VgsUiController(self, self.viewState)
        self.RegisterNeoComButtonExtension()

    def ClearCache(self):
        self.store.ClearCache()

    def Reset(self):
        self.ClearCache()
        self.vgsClient = None
        self.store = None
        self.uiController.Close()
        self.uiController = None
        self.UnregisterNeoComButtonExtension()

    def UpdateMockingSettings(self):
        oldIsTestingEnabled = self.isTestingEnabled
        self.isTestingEnabled = GetFakeVgsEnabled(self.machoNet)
        if oldIsTestingEnabled != self.isTestingEnabled:
            self.Reset()
            self.Initialize()
            self.CloseView(reason='Connection settings change detected - closing store to avoid UI errors')

    def OnUIScalingChange(self, *args):
        self.CloseView(reason='VgsService.OnUIScalingChange - closing store to avoid UI errors')

    def OnGlobalConfigChanged(self, *args, **kwargs):
        self.UpdateMockingSettings()

    def OnAurumChangeFromVgs(self, notification):
        if session.userid != notification['userid']:
            return
        newBalance = notification['balance']
        currentBalance = self.store.GetAccount().GetAurumBalance()
        if currentBalance < newBalance:
            PlaySound('ui_plex_in001_play')
        elif currentBalance > newBalance:
            PlaySound('ui_plex_out001_play')
        self.store.GetAccount().OnAurumChangeFromVgs(notification['balance'])
        self.neocom.Blink('aurumStore', GetByLabel('UI/Neocom/Blink/PLEXBalanceChanged'))

    def OnGemChangeFromVgs(self, notification):
        if session.userid != notification['userid']:
            return
        newBalance = notification['balance']
        currentBalance = self.store.GetAccount().GetGemBalance()
        if currentBalance < newBalance:
            PlaySound('ui_plex_in001_play')
        elif currentBalance > newBalance:
            PlaySound('ui_plex_out001_play')
        self.store.GetAccount().OnGemChangeFromVgs(notification['balance'])
        self.neocom.Blink('aurumStore', GetByLabel('UI/Neocom/Blink/GemBalanceChanged'))

    def OnRedeemingTokensUpdated(self):
        self.store.GetAccount().OnRedeemingTokensUpdated()

    def GetStore(self):
        return self.store

    def GetUiController(self):
        return self.uiController

    def CloseView(self, reason = None):
        if self.viewState.IsViewActive(ViewState.VirtualGoodsStore):
            if reason:
                self.LogInfo(reason)
            self.viewState.CloseSecondaryView(ViewState.VirtualGoodsStore)

    def OnSessionChanged(self, isRemote, session, change):
        if 'charid' in change and change['charid'][1] is not None and self.vgsClient is None:
            self.Initialize()
        isLocationChange = 'locationid' in change
        isUserChange = 'userid' in change
        if isLocationChange or isUserChange:
            reason = ''
            if isLocationChange and isUserChange:
                reason = 'VgsService.OnSessionChanged - locationid and userid change detected, closing store'
            elif isLocationChange:
                reason = 'VgsService.OnSessionChanged - locationid change detected, closing store'
            elif isUserChange:
                reason = 'VgsService.OnSessionChanged - userid change detected, closing store'
            self.LogInfo(reason)
            self.CloseView(reason)

    def OnSessionReset(self):
        self.Reset()
        self.Initialize()

    def ShowRedeemUI(self):
        if session.charid:
            self.redeem.OpenRedeemWindow()
        if self.viewState.IsViewActive(ViewState.VirtualGoodsStore):
            self.uiController.CloseOffer()
            self.viewState.CloseSecondaryView(ViewState.VirtualGoodsStore)
        if session.charid is None:
            uicore.layer.charsel.EnterRedeemMode(animate=True)

    def ShowOffer(self, offerId, categoryId = None):
        self.GetUiController().ShowOffer(offerId, categoryId)

    def SetFeaturedOffers(self, offerIDs = None):
        self.GetUiController().SetFeaturedOffers(offerIDs)

    def GetFeaturedOffers(self):
        return self.GetUiController().GetFeaturedOffers()

    def ToggleStore(self, categoryId = None):
        self._CheckIsUndocking()
        self.viewState.ToggleSecondaryView(ViewState.VirtualGoodsStore, categoryId=categoryId)

    def OpenStore(self, categoryTag = None, typeIds = None):
        self._CheckIsUndocking()
        if not self.viewState.IsViewActive(ViewState.VirtualGoodsStore):
            self.viewState.ActivateView(ViewState.VirtualGoodsStore, categoryTag=categoryTag, typeIds=typeIds)
        elif categoryTag:
            view = self.viewState.GetView(ViewState.VirtualGoodsStore)
            view.SelectCategoryByCategoryTag(categoryTag)

    def IsFastCheckoutWindowActive(self):
        return self.GetUiController().IsFastCheckoutWindowActive()

    def ShowBuyOmegaInStore(self):
        self.OpenStore(categoryTag=CATEGORYTAG_GAMETIME)

    def _CheckIsUndocking(self):
        if sm.GetService('undocking').IsExiting():
            raise UserError('StoreNotAvailableWhileUndocking')

    def GetPLEXBalance(self):
        try:
            return self.GetStore().GetAccount().GetAurumBalance()
        except Exception as e:
            log.exception(e)
            return 0
