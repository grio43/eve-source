#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\standings\transaction.py
import localization
from eve.client.script.ui.control.entries.text import Text
from eve.client.script.ui.util import uix
from menu import MenuLabel

class StandingTransaction(Text):
    __guid__ = 'listentry.StandingTransaction'
    __params__ = ['text', 'details']
    default_showHilite = True

    def Load(self, node):
        Text.Load(self, node)
        self.isNPC = node.isNPC
        self.sr.details = node.details

    def GetMenu(self):
        if self.isNPC:
            details = self.sr.details
            return [(MenuLabel('UI/Common/Details'), self.ShowTransactionDetails, (details,))]
        return []

    def OnDblClick(self, *args):
        if self.isNPC:
            self.ShowTransactionDetails()

    def ShowTransactionDetails(self, details = None, *args):
        details = details if details != None else self.sr.details
        uix.TextBox(localization.GetByLabel('UI/Standings/TransactionWindow/Details'), details)
