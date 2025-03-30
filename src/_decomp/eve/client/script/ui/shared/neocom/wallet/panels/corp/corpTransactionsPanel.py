#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\corp\corpTransactionsPanel.py
from carbonui import uiconst
from carbonui.control.combo import Combo
from eve.client.script.ui.shared.neocom.wallet.panels.transactionsPanel import TransactionsPanel

class CorpTransactionsPanel(TransactionsPanel):

    def _GetTransactions(self):
        accountKey = self.corpTransactionsAccountKeyCombo.GetValue()
        year, month = self._GetDateTimeSelection()
        return sm.GetService('account').GetCorpTransactions(accountKey, year, month)

    def ConstructLayout(self):
        super(CorpTransactionsPanel, self).ConstructLayout()
        self.corpTransactionsAccountKeyCombo = Combo(parent=self.transactionsOptionsCont, options=self._GetAccountKeyList(), name='accountkey', select=settings.user.ui.Get('accountkey', 1000), callback=self.OnCorpTransactionsAccountKeyCombo, width=130, align=uiconst.TOLEFT, padRight=6, idx=0)

    def OnCorpTransactionsAccountKeyCombo(self, entry, header, value, *args):
        settings.user.ui.Set('accountkey', value)
        self.UpdateTransactionsAndPopulateScroll()

    def ShowTransactions(self, accountKey = None):
        if accountKey:
            self.corpTransactionsAccountKeyCombo.SelectItemByValue(accountKey)
        super(CorpTransactionsPanel, self).ShowTransactions(accountKey)
