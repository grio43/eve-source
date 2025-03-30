#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\vgs\client\account.py
import logging
import signals
log = logging.getLogger(__name__)

class Account:

    def __init__(self, vgs_client):
        self.vgs_client = vgs_client
        self.plex_balance = None
        self.gem_balance = None
        self.accountAurumBalanceChanged = signals.Signal(signalName='accountAurumBalanceChanged')
        self.accountGemBalanceChanged = signals.Signal(signalName='accountGemBalanceChanged')
        self.redeemingTokensUpdated = signals.Signal(signalName='redeemingTokensUpdated')

    def ClearCache(self):
        self.plex_balance = None
        self.gem_balance = None

    def SubscribeToAurumBalanceChanged(self, callBackFunction):
        self.accountAurumBalanceChanged.connect(callBackFunction)

    def SubscribeToGemBalanceChanged(self, callBackFunction):
        self.accountGemBalanceChanged.connect(callBackFunction)

    def SubscribeToRedeemingTokensUpdatedEvent(self, callBackFunction):
        self.redeemingTokensUpdated.connect(callBackFunction)

    def UnsubscribeFromAurumBalanceChanged(self, callBackFunction):
        self.accountAurumBalanceChanged.disconnect(callBackFunction)

    def UnsubscribeFromGemBalanceChanged(self, callBackFunction):
        self.accountGemBalanceChanged.disconnect(callBackFunction)

    def UnsubscribeFromRedeemingTokensUpdatedEvent(self, callBackFunction):
        self.redeemingTokensUpdated.disconnect(callBackFunction)

    def OnAurumChangeFromVgs(self, new_balance):
        log.debug('OnAurumChangeFromVgs %s' % new_balance)
        old_balance = self.plex_balance
        self.plex_balance = new_balance
        self.accountAurumBalanceChanged(self.plex_balance, old_balance)

    def OnGemChangeFromVgs(self, new_balance):
        log.debug('OnGemChangeFromVgs %s' % new_balance)
        self.gem_balance = new_balance
        self.accountGemBalanceChanged(self.gem_balance)

    def OnRedeemingTokensUpdated(self):
        self.redeemingTokensUpdated()

    def GetAurumBalance(self):
        if self.plex_balance is None:
            self.plex_balance = self.vgs_client.get_plex_account_balance()
        return self.plex_balance

    def GetGemBalance(self):
        if self.gem_balance is None:
            self.gem_balance = self.vgs_client.get_gem_account_balance()
        return self.gem_balance
