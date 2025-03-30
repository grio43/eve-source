#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\factional_warfare\job.py
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupFactionalWarfareSystems
import localization
import eveicon
from factionwarfare.client.text import GetSystemCaptureStatusText
from fwwarzone.client.dashboard.const import ADJACENCY_TO_LABEL_TEXT
from fwwarzone.client.facwarUtil import IsMyCombatEnemyFaction, IsMyFwFaction
from jobboard.client.features.dungeons.job import DungeonJob
from .page import FactionalWarfareSitePage

class FactionalWarfareJob(DungeonJob):
    CONTENT_GROUP_ID = contentGroupFactionalWarfareSystems
    PAGE_CLASS = FactionalWarfareSitePage

    @property
    def is_available_in_browse(self):
        if not super(FactionalWarfareJob, self).is_available_in_browse:
            return False
        faction_id = self.faction_id
        return IsMyFwFaction(faction_id) or IsMyCombatEnemyFaction(faction_id)

    @property
    def occupation_state(self):
        return sm.GetService('fwWarzoneSvc').GetOccupationState(self.solar_system_id)

    @property
    def occupier_id(self):
        return self.occupation_state.occupierID

    @property
    def adjacency_state(self):
        occupation_state = self.occupation_state
        if occupation_state:
            return occupation_state.adjacencyState

    @property
    def victory_point_state(self):
        return sm.GetService('fwVictoryPointSvc').GetVictoryPointState(self.solar_system_id)

    @property
    def contested_fraction(self):
        victory_point_state = self.victory_point_state
        if victory_point_state:
            return victory_point_state.contestedFraction
        else:
            return 0.0

    @property
    def subtitle(self):
        return u'{} - {}'.format(GetSystemCaptureStatusText(self.victory_point_state), ADJACENCY_TO_LABEL_TEXT.get(self.adjacency_state, ''))

    def get_buttons(self):
        buttons = super(FactionalWarfareJob, self).get_buttons()
        buttons.append({'icon': eveicon.flag,
         'on_click': self._open_factional_warfare_window,
         'hint': localization.GetByLabel('UI/Agency/FactionWarfare/openFactionWarfareWindow')})
        return buttons

    def _open_factional_warfare_window(self, *args, **kwargs):
        sm.GetService('cmd').OpenMilitia()
