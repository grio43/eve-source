#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\personal\personalMarketTransactionsPanel.py
from eve.client.script.ui.shared.neocom.wallet.panels.marketTransactionsPanel import MarketTransactionsPanel

class PersonalMarketTransactionsPanel(MarketTransactionsPanel):

    def IsCorpWallet(self):
        return False

    def _GetTransactions(self, fromDate):
        return sm.GetService('market').GetPersonalMarketTransactions(fromDate)
