#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\corp\corpShareholdersPanel.py
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.neocom.wallet.panels.sharesUtil import GetSharesMenu
from eve.client.script.ui.shared.neocom.wallet.walletUtil import HaveReadAccessToCorpWalletDivision
from eve.common.lib import appConst
from localization import GetByLabel
from utillib import KeyVal
headers = (GetByLabel('UI/Wallet/WalletWindow/ColHeaderOwner'), GetByLabel('UI/Wallet/WalletWindow/ColHeaderCorporation'), GetByLabel('UI/Wallet/WalletWindow/ColHeaderShares'))

class CorpShareholdersPanel(Container):
    default_name = 'ShareholdersPanel'

    def ApplyAttributes(self, attributes):
        super(CorpShareholdersPanel, self).ApplyAttributes(attributes)
        self.isInitialized = False
        self.scroll = Scroll(parent=self)

    def OnTabSelect(self):
        if HaveReadAccessToCorpWalletDivision(session.corpAccountKey):
            self.SetHint(GetByLabel('UI/Wallet/WalletWindow/HintNeedAccountant'))
        if not (appConst.corpRoleAccountant | appConst.corpRoleJuniorAccountant) & session.corprole != 0:
            self.scroll.Clear()
            self.SetHint(GetByLabel('UI/Wallet/WalletWindow/HintNeedAccountantRoles'))
        else:
            self.PopulateScroll()

    def PopulateScroll(self):
        self.scroll.ShowHint()
        scrollList = self.GetScrollList()
        if scrollList:
            if self.scroll is not None:
                self.scroll.Load(fixedEntryHeight=24, contentList=scrollList, headers=headers)
        else:
            if self.scroll is not None:
                self.scroll.Clear()
            self.scroll.ShowHint(GetByLabel('UI/Wallet/WalletWindow/HintNoCorpShares'))

    def GetScrollList(self):
        scrolllist = []
        shares = sm.GetService('corp').GetShareholders()
        for share in shares.itervalues():
            entry = self.GetScrollEntry(share)
            scrolllist.append(entry)

        return scrolllist

    def GetScrollEntry(self, shareCertificate):
        data = KeyVal()
        data.ownerID = shareCertificate.shareholderID
        if shareCertificate.shareholderCorporationID:
            data.corporationID = shareCertificate.shareholderCorporationID
        else:
            data.corporationID = shareCertificate.corporationID
        data.shares = shareCertificate.shares
        data.GetMenu = GetSharesMenu
        data.label = [cfg.eveowners.Get(data.ownerID).name,
         '<t>',
         cfg.eveowners.Get(data.corporationID).name,
         '<t>',
         FmtAmt(data.shares)]
        entry = GetFromClass(Generic, data)
        return entry
