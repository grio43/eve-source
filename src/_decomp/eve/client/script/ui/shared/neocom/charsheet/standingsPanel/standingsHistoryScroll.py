#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\standingsPanel\standingsHistoryScroll.py
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.neocom.charsheet.standingsPanel.standingsHistoryEntry import StandingsHistoryEntry
from localization import GetByLabel

class StandingsHistoryScroll(Scroll):
    default_name = 'StandingsHistoryScroll'
    default_id = 'StandingsHistoryScroll2'
    default_columnWidth = StandingsHistoryEntry.GetDefaultColumnWidth()
    __notifyevents__ = ['OnStandingsGraphHoverStateChange']

    def ApplyAttributes(self, attributes):
        Scroll.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.transactions = []

    def Update(self, transactions, ownerID):
        nodes = []
        self.transactions = transactions
        for transaction in self.transactions:
            node = Bunch(decoClass=StandingsHistoryEntry, sortValues=StandingsHistoryEntry.GetColumnSortValues(transaction), transaction=transaction)
            nodes.append(node)

        ownerName = cfg.eveowners.Get(ownerID).ownerName
        self.LoadContent(contentList=nodes, headers=StandingsHistoryEntry.GetHeaders(), noContentHint=GetByLabel('UI/Standings/NoStandingsTransactions', ownerName=ownerName))

    def OnStandingsGraphHoverStateChange(self, index):
        transaction = self.transactions[index - 1] if index else None
        for node in self.GetNodes():
            if not node.panel:
                continue
            if node.transaction == transaction:
                node.panel.ShowHilite()
            else:
                node.panel.HideHilite()
