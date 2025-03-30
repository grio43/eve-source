#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\standingsPanel\standingsHistoryEntry.py
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.shared.standings.standingsUIUtil import GetStandingEventIcon
from eve.client.script.ui.shared.standings.standingsUtil import GetStandingChangeFormatted
from eve.common.script.util.eveFormat import FmtStandingTransaction
from eve.common.script.util.standingUtil import RoundStandingChange
from localization import GetByLabel

class StandingsHistoryEntry(BaseListEntryCustomColumns):

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.transaction = self.node.transaction
        iconCont = self.AddColumnContainer()
        texturePath = GetStandingEventIcon(self.transaction.eventTypeID)
        iconSize = 26
        SpriteThemeColored(name='icon', parent=iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=texturePath, pos=(0,
         0,
         iconSize,
         iconSize), colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.85)
        dateTime = FmtDate(self.transaction.eventDateTime, 'sn')
        self.AddColumnText(dateTime)
        change = RoundStandingChange(self.transaction.modification)
        self.AddColumnText(GetStandingChangeFormatted(change))
        subject, self.node.hint = FmtStandingTransaction(self.transaction)
        self.AddColumnText(subject)

    def OnMouseEnter(self, *args):
        BaseListEntryCustomColumns.OnMouseEnter(self, *args)
        sm.ScatterEvent('OnStandingHistoryEntryMouseEnter', self.transaction)

    def OnMouseExit(self, *args):
        BaseListEntryCustomColumns.OnMouseExit(self, *args)
        sm.ScatterEvent('OnStandingHistoryEntryMouseExit', self.transaction)

    @classmethod
    def GetDynamicHeight(cls, node, width = None):
        return 30

    @staticmethod
    def GetDefaultColumnWidth():
        return {'': 40,
         GetByLabel('UI/Common/Date'): 70,
         GetByLabel('UI/Common/Change'): 55,
         GetByLabel('UI/Common/Reason'): 300}

    @staticmethod
    def GetColumnSortValues(transaction):
        reason, _ = FmtStandingTransaction(transaction)
        return (transaction.eventTypeID,
         transaction.eventDateTime,
         transaction.modification,
         reason)

    @staticmethod
    def GetHeaders():
        return ('',
         GetByLabel('UI/Common/Date'),
         GetByLabel('UI/Common/Change'),
         GetByLabel('UI/Common/Reason'))
