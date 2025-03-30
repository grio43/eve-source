#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\standingsPanelOld.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.shared.standings.standingsUIUtilOld import GetStandingsEntriesNPCsToMyCharacter
from localization import GetByLabel

class StandingsPanelOld(Container):
    default_name = 'StandingsPanelOld'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.scroll = Scroll(parent=self, padding=(0, 4, 0, 4))
        self.scroll.sr.id = 'charsheet_standings'
        self.tabs = TabGroup(name='tabparent', parent=self, idx=0, padding=0, tabs=((GetByLabel('UI/CharacterSheet/CharacterSheetWindow/StandingTabs/LikedBy'),
          self.scroll,
          self,
          'mystandings_to_positive'), (GetByLabel('UI/CharacterSheet/CharacterSheetWindow/StandingTabs/DislikeBy'),
          self.scroll,
          self,
          'mystandings_to_negative')), groupID='cs_standings')

    def LoadPanel(self, *args):
        self.tabs.AutoSelect()

    def Load(self, key):
        positive = key == 'mystandings_to_positive'
        scrolllist = GetStandingsEntriesNPCsToMyCharacter(positive=positive)
        self.scroll.Load(contentList=scrolllist)
