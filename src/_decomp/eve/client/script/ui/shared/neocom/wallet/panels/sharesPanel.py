#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\sharesPanel.py
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.neocom.wallet.panels.sharesUtil import GetSharesMenu
from eve.client.script.ui.shared.neocom.wallet.walletConst import WALLET_SHARES_SCROLLID
from eve.common.lib import appConst
from localization import GetByLabel
headers = (GetByLabel('UI/Wallet/WalletWindow/ColHeaderOwner'), GetByLabel('UI/Wallet/WalletWindow/ColHeaderCorporation'), GetByLabel('UI/Wallet/WalletWindow/ColHeaderShares'))

class SharesPanel(Container):
    default_name = 'SharesPanel'
    __notifyevents__ = ['OnShareChange']

    def ApplyAttributes(self, attributes):
        super(SharesPanel, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.scroll = Scroll(parent=self)
        self.scroll.sr.id = WALLET_SHARES_SCROLLID

    def OnTabSelect(self):
        self.ShowMyShares()

    def ShowMyShares(self):
        if self.IsAccessDenied():
            self.SetHint(GetByLabel('UI/Wallet/WalletWindow/HintNeedAccountant'))
        elif self.IsCorpWallet() and not (appConst.corpRoleAccountant | appConst.corpRoleJuniorAccountant) & session.corprole != 0:
            self.scroll.Clear()
            self.SetHint(GetByLabel('UI/Wallet/WalletWindow/HintNeedAccountantRoles'))
        else:
            self.PopulateScroll()

    def PopulateScroll(self):
        scrolllist = self.GetScrollList()
        if scrolllist:
            self.scroll.Load(fixedEntryHeight=24, contentList=scrolllist, headers=headers)
        else:
            self.scroll.Clear()
            if self.IsCorpWallet():
                self.scroll.ShowHint(GetByLabel('UI/Wallet/WalletWindow/HintNoCorpShares'))
            else:
                self.scroll.ShowHint(GetByLabel('UI/Wallet/WalletWindow/HintNoShares'))

    def GetScrollList(self):
        scrolllist = []
        shares = sm.GetService('corp').GetSharesByShareholder(self.IsCorpWallet())
        for share in shares.itervalues():
            entry = self.GetEntry(share)
            scrolllist.append(entry)

        return scrolllist

    def GetEntry(self, shareCertificate):
        ownerID = self.GetOwnerID()
        corporationID = shareCertificate.corporationID
        shares = shareCertificate.shares
        return GetFromClass(Generic, {'ownerID': ownerID,
         'corporationID': corporationID,
         'shares': shares,
         'GetMenu': GetSharesMenu,
         'label': [cfg.eveowners.Get(ownerID).name,
                   '<t>',
                   cfg.eveowners.Get(corporationID).name,
                   '<t>',
                   FmtAmt(shares)]})

    def IsAccessDenied(self):
        return False

    def OnShareChange(self, shareholderID, corporationID, change):
        if self.GetOwnerID() in (shareholderID, corporationID) and self.display:
            self.ShowMyShares()

    def GetOwnerID(self):
        raise NotImplementedError

    def IsCorpWallet(self):
        raise NotImplementedError
