#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\standingsPanel\standingCompositionScroll.py
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.neocom.charsheet.standingsPanel.standingCompositionEntry import StandingCompositionEntry
from eve.common.script.sys import idCheckers
from localization import GetByLabel

class StandingCompositionScroll(Scroll):
    default_name = 'StandingCompositionScroll'
    default_id = 'StandingCompositionScroll'
    default_columnWidth = StandingCompositionEntry.GetDefaultColumnWidth()

    def ApplyAttributes(self, attributes):
        super(StandingCompositionScroll, self).ApplyAttributes(attributes)

    def Update(self, compositions, ownerID):
        scrollList = []
        for composition in compositions:
            if idCheckers.IsNPC(composition.ownerID):
                continue
            scrollEntry = Bunch(decoClass=StandingCompositionEntry, sortValues=StandingCompositionEntry.GetColumnSortValues(composition), composition=composition)
            scrollList.append(scrollEntry)

        ownerName = cfg.eveowners.Get(ownerID).ownerName
        self.LoadContent(contentList=scrollList, headers=StandingCompositionEntry.GetHeaders(), noContentHint=GetByLabel('UI/Standings/NoStandingsTransactions', ownerName=ownerName))
