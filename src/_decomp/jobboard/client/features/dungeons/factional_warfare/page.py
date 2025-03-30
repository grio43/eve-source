#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\factional_warfare\page.py
import carbonui
import eveui
import localization
from evelink.client import owner_link
from carbonui.primitives.cardsContainer import CardsContainer
from eve.client.script.ui.control.infoIcon import InfoGlyphIcon
import threadutils
from fwwarzone.client.dashboard.const import ADJACENCY_TO_LABEL_SYSTEM_TEXT
from fwwarzone.client.dashboard.gauges.advantageWidget import AdvantageWidget
from fwwarzone.client.dashboard.gauges.contestedGauge import ContestedFWSystemGauge
from fwwarzone.client.util import GetAttackerDefenderColors
from factionwarfare.client.text import GetSystemCaptureStatusText
from jobboard.client.ui.pages.details_page import DetailsSection
from jobboard.client.features.dungeons.page import DungeonPage

class FactionalWarfareSitePage(DungeonPage):

    def _construct_body(self, parent_container):
        super(FactionalWarfareSitePage, self)._construct_body(parent_container)
        self._construct_system_details(parent_container)

    def _construct_system_details(self, parent_container):
        system_section = DetailsSection(parent=parent_container, title=localization.GetByLabel('UI/Opportunities/FWSystemStatusHeader', solar_system_id=self.job.solar_system_id))
        container = system_section.content_container
        system_info_container = CardsContainer(parent=container, align=eveui.Align.to_top, cardHeight=80, cardMaxWidth=500, contentSpacing=(16, 16))
        contested_container = eveui.Container(parent=system_info_container, align=eveui.Align.to_all)
        self._construct_contested(contested_container)
        advantage_container = eveui.Container(parent=system_info_container, align=eveui.Align.to_all)
        self._construct_advantage(advantage_container)

    @threadutils.threaded
    def _construct_contested(self, parent_container):
        attackerColor, defenderColor = GetAttackerDefenderColors(self.job.solar_system_id)
        self.gauge = ContestedFWSystemGauge(parent=parent_container, align=eveui.Align.center_left, systemId=self.job.solar_system_id, radius=25, attackerColor=attackerColor, defenderColor=defenderColor, adjacencyState=self.job.adjacency_state, displayAdjacencyIcon=True, animateIn=False, lineWidth=2)
        text_container = eveui.ContainerAutoSize(parent=parent_container, align=carbonui.Align.VERTICALLY_CENTERED, padLeft=66, clipChildren=True)
        carbonui.TextBody(parent=text_container, pickState=carbonui.PickState.ON, align=eveui.Align.to_top, text=owner_link(self.job.occupier_id), autoFadeSides=16)
        carbonui.TextBody(parent=text_container, align=eveui.Align.to_top, text=GetSystemCaptureStatusText(self.job.victory_point_state), autoFadeSides=16)
        carbonui.TextBody(parent=text_container, align=eveui.Align.to_top, text=ADJACENCY_TO_LABEL_SYSTEM_TEXT.get(self.job.adjacency_state, ''), autoFadeSides=16)

    @threadutils.threaded
    def _construct_advantage(self, parent_container):
        title_container = eveui.ContainerAutoSize(parent=parent_container, align=eveui.Align.to_top, height=20)
        carbonui.TextBody(name='advantageLabel', parent=title_container, align=eveui.Align.to_left, text=localization.GetByLabel('UI/FactionWarfare/frontlinesDashboard/advantageTitleLabel'))
        icon_container = eveui.Container(parent=title_container, align=eveui.Align.to_left, width=20, left=4)
        InfoGlyphIcon(parent=icon_container, align=eveui.Align.center, hint=localization.GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/advantageTrackerDescription'))
        AdvantageWidget(name='AdvantageWidget', parent=parent_container, align=eveui.Align.to_top, systemId=self.job.solar_system_id)

    def _construct_archetype_info(self, parent_container):
        pass
