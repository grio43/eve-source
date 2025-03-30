#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\personal\personalTransactionsPanel.py
from eve.client.script.ui.shared.neocom.wallet.panels.transactionsPanel import TransactionsPanel

class PersonalTransactionsPanel(TransactionsPanel):

    def _GetTransactions(self):
        year, month = self._GetDateTimeSelection()
        return sm.GetService('account').GetPersonalTransactions(year, month)
