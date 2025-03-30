#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\loyaltyPointsWalletSvc.py
import logging
from appConst import corpHeraldry
from carbon.common.script.sys.service import Service
from inventorycommon.const import ownerCONCORD
logger = logging.getLogger(__name__)

class LoyaltyPointsWalletSvc(Service):
    __guid__ = 'svc.loyaltyPointsWallet'
    __servicename__ = 'loyaltyPointsWallet'
    __displayname__ = 'Loyalty Points Wallet'
    __dependencies__ = []
    __notifyevents__ = ['OnSessionChanged',
     'ProcessSessionReset',
     'OnLPChange',
     'OnCorpLPChange']
    _characterLPBalanceByIssuerCorpID = None
    _corpLPBalanceByIssuerCorpID = None

    @staticmethod
    def _GetRemoteLPService():
        return sm.RemoteSvc('LPSvc')

    def _LoadCharacterLPData(self):
        if self._characterLPBalanceByIssuerCorpID is None:
            loyaltyPoints = self._GetRemoteLPService().GetAllMyCharacterWalletLPBalances()
            self._characterLPBalanceByIssuerCorpID = {row[0]:row[1] for row in loyaltyPoints}
        return self._characterLPBalanceByIssuerCorpID

    def _LoadCorporationLPData(self):
        if self._corpLPBalanceByIssuerCorpID is None:
            loyaltyPoints = self._GetRemoteLPService().GetAllMyCorporationWalletLPBalances()
            self._corpLPBalanceByIssuerCorpID = {row[0]:row[1] for row in loyaltyPoints}
        return self._corpLPBalanceByIssuerCorpID

    def _FlushAllCharacterLPData(self):
        self._characterLPBalanceByIssuerCorpID = None

    def _FlushAllCorporationLPData(self):
        self._corpLPBalanceByIssuerCorpID = None

    def ProcessSessionReset(self):
        self._FlushAllCharacterLPData()
        self._FlushAllCorporationLPData()

    def OnSessionChanged(self, isremote, sess, change):
        if 'corpid' in change or 'corprole' in change:
            self._FlushAllCorporationLPData()

    def OnLPChange(self, _changeType, issuerCorpID, lpBefore, lpAfter):
        self._FlushAllCharacterLPData()
        sm.ScatterEvent('OnCharacterLPBalanceChange_Local', issuerCorpID, lpBefore, lpAfter)

    def OnCorpLPChange(self, reason, issuerCorpID):
        self._FlushAllCorporationLPData()
        sm.ScatterEvent('OnCorporationLPBalanceChange_Local', issuerCorpID)

    def GetCharacterWalletLPBalance(self, issuerCorpID):
        characterLPByCorpID = self._LoadCharacterLPData()
        return characterLPByCorpID.get(issuerCorpID, 0)

    def GetCharacterEvermarkBalance(self):
        return self.GetCharacterWalletLPBalance(corpHeraldry)

    def GetCharacterConcordLPBalance(self):
        return self.GetCharacterWalletLPBalance(ownerCONCORD)

    def GetAllCharacterLPBalancesExcludingEvermarks(self):
        characterLPByCorpID = self._LoadCharacterLPData()
        return [ (issuerCorpID, amount) for issuerCorpID, amount in characterLPByCorpID.iteritems() if issuerCorpID != corpHeraldry ]

    def GetCorporationWalletLPBalance(self, issuerCorpID):
        corpLPByCorpID = self._LoadCorporationLPData()
        return corpLPByCorpID.get(issuerCorpID, 0)

    def GetCorporationEvermarkBalance(self):
        return self.GetCorporationWalletLPBalance(corpHeraldry)

    def GetAllCorporationLPBalancesExcludingEvermarks(self):
        corpLPByIssuerCorpID = self._LoadCorporationLPData()
        return [ (issuerCorpID, amount) for issuerCorpID, amount in corpLPByIssuerCorpID.iteritems() if issuerCorpID != corpHeraldry ]

    def TransferLPFromCorpToCorp(self, receiverCorpID, issuerCorpID, lpAmount):
        self._GetRemoteLPService().TransferLPFromMyCorpWalletToOtherCorp(receiverCorpID, issuerCorpID, lpAmount)

    def TransferLPFromPlayerToCorp(self, receiverCorpID, issuerCorpID, lpAmount):
        self._GetRemoteLPService().TransferLPFromMyWalletToOtherCorp(receiverCorpID, issuerCorpID, lpAmount)
