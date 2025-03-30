#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\corp\corpMarketTransactionsPanel.py
from carbonui import uiconst
from carbonui.control.combo import Combo
from eve.client.script.ui.shared.neocom.wallet.panels.marketTransactionsPanel import MarketTransactionsPanel
from eve.client.script.ui.shared.neocom.wallet.walletUtil import AmAccountantOrJuniorAccountant, HaveAccessToCorpWalletDivision
from localization import GetByLabel

class CorpMarketTransactionsPanel(MarketTransactionsPanel):

    def _GetTransactions(self, fromDate):
        accountKey = self.divisionCombo.GetValue()
        accountKey = None if accountKey == -1 else accountKey
        return sm.GetService('market').GetCorpMarketTransactions(fromDate, accountKey)

    def GetScrollHeaders(self):
        headers = super(CorpMarketTransactionsPanel, self).GetScrollHeaders()
        headers.extend([GetByLabel('UI/Wallet/WalletWindow/ColHeaderWho', 'characterString'), GetByLabel('UI/Wallet/WalletWindow/ColHeaderWalletDivision', 'keyString')])
        return headers

    def ConstructFilters(self):
        super(CorpMarketTransactionsPanel, self).ConstructFilters()
        if AmAccountantOrJuniorAccountant():
            accountOptions = [(GetByLabel('UI/Common/Any'), None)]
        else:
            accountOptions = []
        names = sm.GetService('corp').GetDivisionNames()
        for i, n in names.iteritems():
            if i >= 8:
                accountKey = 1000 + i - 8
                if AmAccountantOrJuniorAccountant() or HaveAccessToCorpWalletDivision(accountKey):
                    accountOptions.append((n, accountKey))

        self.divisionCombo = Combo(label=GetByLabel('UI/Wallet/WalletWindow/Division'), parent=self.transactionsOptionsCont, options=accountOptions, select=settings.user.ui.Get('corpMarketTransDivision', 1000), name='accountkey', width=90, align=uiconst.TOLEFT, padRight=6, idx=0, callback=self.OnDivisionCombo)
        self.memberCombo = Combo(name='type', parent=self.transactionsOptionsCont, label=GetByLabel('UI/Wallet/WalletWindow/Member'), top=0, width=120, align=uiconst.TOLEFT, padRight=6, callback=self.OnMemberCombo)

    def OnDivisionCombo(self, entry, header, value, *args):
        self.UpdateTransactions()
        self.PopulateScroll()
        settings.user.ui.Set('corpMarketTransDivision', value)

    def OnMemberCombo(self, *args):
        self.UpdateTransactionsByPage()
        self.PopulateScroll()

    def _GetTransactionEntryLines(self, tr):
        lines = super(CorpMarketTransactionsPanel, self)._GetTransactionEntryLines(tr)
        lines.append(tr.characterString)
        lines.append(tr.keyString)
        return lines

    def GetScrollEntryData(self, text, tr):
        data = super(CorpMarketTransactionsPanel, self).GetScrollEntryData(text, tr)
        data.Set('sort_%s' % GetByLabel('UI/Wallet/WalletWindow/ColHeaderWho'), tr.characterString)
        data.Set('sort_%s' % GetByLabel('UI/Wallet/WalletWindow/ColHeaderWalletDivision'), tr.keyString)
        return data

    def UpdateTransactions(self):
        super(CorpMarketTransactionsPanel, self).UpdateTransactions()
        self.UpdateMemberCombo()

    def UpdateMemberCombo(self):
        options = self._transactionsList.GetCharacterIDs()
        options = sorted(list(options))
        options.insert(0, (GetByLabel('UI/Common/Any'), 0))
        self.memberCombo.LoadOptions(options)

    def IsTransactionVisible(self, transaction):
        isVisible = super(CorpMarketTransactionsPanel, self).IsTransactionVisible(transaction)
        memberID = self.memberCombo.GetValue()
        if memberID:
            return memberID == transaction.data.characterID
        return isVisible

    def ShowMarketTransactions(self, accountKey = None):
        if accountKey:
            self.divisionCombo.SelectItemByValue(accountKey)
        self.UpdateTransactions()
        self.PopulateScroll()
