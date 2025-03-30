#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\stationServiceEntry.py
import carbonui.const as uiconst
from eve.client.script.ui.control.entries.icon import IconEntry
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from localization import GetByLabel

class StationServiceEntry(IconEntry):
    __guid__ = 'listentry.StationServiceEntry'

    def Startup(self, *args):
        super(StationServiceEntry, self).Startup(*args)
        self.sr.standingsRestriction = MoreInfoIcon(parent=self, align=uiconst.CENTERRIGHT, left=2, width=24, height=24, texturePath='res:/UI/Texture/Classes/Standings/Actions/derivedAgentInFaction.png')

    def Load(self, node):
        super(StationServiceEntry, self).Load(node)
        standingsRestriction = node.Get('standingsRestriction', None)
        if standingsRestriction:
            self.sr.standingsRestriction.hint = GetByLabel('UI/Standings/StationServiceStandingsRequired', **standingsRestriction)
            self.sr.standingsRestriction.Show()
        else:
            self.sr.standingsRestriction.Hide()
