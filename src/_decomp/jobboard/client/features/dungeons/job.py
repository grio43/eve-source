#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\job.py
import caching
import eveicon
from eve.common.lib.appConst import factionUnknown
from eve.common.script.sys import eveCfg
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
from evearchetypes import GetArchetype
from evedungeons.client.data import GetDungeon
from evedungeons.client.util import GetDungeonShipRestrictions, GetDungeonContentTags
from evelink.client import owner_link
import localization
from objectives.client.objective_chain import ObjectiveChain
from objectives.common.objective_context import ObjectivesContext
from jobboard.client import job_board_signals
from jobboard.client.job import BaseJob
from .card import DungeonCard, DungeonListEntry, DungeonInfoPanelEntry
from .page import DungeonPage

class DungeonJob(BaseJob):
    PAGE_CLASS = DungeonPage
    CARD_CLASS = DungeonCard
    LIST_ENTRY_CLASS = DungeonListEntry
    INFO_PANEL_ENTRY_CLASS = DungeonInfoPanelEntry
    CONTENT_GROUP_ID = None
    OBJECTIVE_CHAIN_ID = 48

    def __init__(self, job_id, provider, dungeon):
        self._dungeon = dungeon
        self._data = None
        self._travel_to_objective_chain = None
        self._is_completed = False
        content_id = self.dungeon_id
        super(DungeonJob, self).__init__(job_id, content_id, provider)

    def clear(self):
        super(DungeonJob, self).clear()
        if self._travel_to_objective_chain:
            self._travel_to_objective_chain.stop()
            self._travel_to_objective_chain = None

    def update(self, dungeon_info = None):
        if dungeon_info:
            self._dungeon = dungeon_info
            if self._travel_to_objective_chain:
                self._travel_to_objective_chain.context.update_value('scan_result', self.scan_result)
        super(DungeonJob, self).update()

    @property
    def data(self):
        if not self._data:
            self._data = GetDungeon(self.dungeon_id)
        return self._data

    @property
    def archetype_data(self):
        return GetArchetype(self.archetype_id)

    @property
    def active_dungeon(self):
        current_dungeon = sm.GetService('dungeonTracking').current_dungeon
        if current_dungeon and current_dungeon.instance_id == self.instance_id:
            return current_dungeon

    @property
    def dungeon_id(self):
        return self._dungeon['dungeon_id']

    @property
    def instance_id(self):
        return self._dungeon['instance_id']

    @property
    def scan_result(self):
        return self._dungeon.get('scan_result')

    @property
    def scan_result_id(self):
        scan_result = self.scan_result
        if scan_result:
            return scan_result.targetID

    @property
    def solar_system_id(self):
        return self._dungeon['solar_system_id']

    @property
    def archetype_id(self):
        return self.data.archetypeID

    @property
    def faction_id(self):
        return self.data.factionID

    @property
    def faction_name(self):
        if not self.faction_id:
            return ''
        faction = cfg.eveowners.Get(self.faction_id)
        if faction:
            return faction.name
        return ''

    @property
    def difficulty(self):
        return self.data.difficulty

    @property
    def title(self):
        return localization.GetByMessageID(self.data.dungeonNameID)

    @property
    def link_title(self):
        scan_result_id = self.scan_result_id
        if scan_result_id and self.in_same_system:
            return u'{} [{}]'.format(self.title, scan_result_id)
        return self.title

    @property
    def description(self):
        return localization.GetByMessageID(self.data.descriptionID)

    @property
    def gameplay_description(self):
        return localization.GetByMessageID(self.data.gameplayDescriptionID)

    @property
    def resources(self):
        return set()

    @property
    def enemy(self):
        if self.faction_id and self.faction_id != factionUnknown:
            return self.faction_id

    @property
    def enemy_name(self):
        if self.faction_id:
            return owner_link(self.faction_id)
        return localization.GetByLabel('UI/Common/Unknown')

    @property
    def archetype_title(self):
        return localization.GetByMessageID(self.archetype_data.titleID)

    @property
    def archetype_description(self):
        return localization.GetByMessageID(self.archetype_data.descriptionID)

    @property
    def in_valid_ship(self):
        restrictions = self.ship_restrictions
        if not restrictions:
            return True
        if not session.shipid:
            return False
        ship_type_id = sm.GetService('invCache').GetInventoryFromId(session.shipid).typeID
        if ship_type_id in restrictions.restrictedShipTypes:
            return False
        if ship_type_id in restrictions.allowedShipTypes:
            return True
        return True

    @caching.lazy_property
    def ship_restrictions(self):
        return GetDungeonShipRestrictions(self.dungeon_id)

    @property
    def is_completed(self):
        return self._is_completed

    @is_completed.setter
    def is_completed(self, value):
        if self._is_completed == value:
            return
        self._is_completed = value
        self.update()
        job_board_signals.on_job_state_changed(self)
        job_board_signals.on_job_completed(self)

    @property
    def is_trackable(self):
        return not self.is_removed

    @property
    def is_available_in_active(self):
        return bool(self.active_dungeon) or self.is_tracked

    @property
    def objective_chain(self):
        objective_chain = self.active_dungeon_objective_chain
        if objective_chain:
            return objective_chain
        if not self._travel_to_objective_chain:
            context = ObjectivesContext()
            context.set_values(dungeon_id=self.dungeon_id, scan_result=self.scan_result, solar_system_id=self.solar_system_id, instance_id=self.instance_id)
            objective_chain = ObjectiveChain(content_id=self.OBJECTIVE_CHAIN_ID, context=context)
            objective_chain.start()
            self._travel_to_objective_chain = objective_chain
        return self._travel_to_objective_chain

    @property
    def active_dungeon_objective_chain(self):
        active_dungeon = self.active_dungeon
        if active_dungeon and active_dungeon.objective_chain:
            return active_dungeon.objective_chain

    def get_cta_buttons(self):
        if self.active_dungeon:
            return []
        objective = self.objective_chain.objectives.get('enter_dungeon')
        if not objective:
            return []
        buttons = []
        for task in objective.get_all_tasks():
            button = task.construct_button_widget()
            if button:
                buttons.append(button)

        return buttons

    def get_buttons(self):
        buttons = super(DungeonJob, self).get_buttons()
        if self.CONTENT_GROUP_ID:
            buttons.append({'icon': eveicon.open_window,
             'on_click': self._open_dungeon_agency_page,
             'hint': localization.GetByLabel('UI/Opportunities/OpenAgency')})
        return buttons

    def get_menu(self):
        active_dungeon = self.active_dungeon
        if active_dungeon:
            data = active_dungeon.get_context_menu()
            data.entrylist.extend(super(DungeonJob, self).get_menu().entrylist)
            return data
        else:
            warp_to_menu = self._get_warp_to_menu()
            if warp_to_menu:
                warp_to_menu.extend(super(DungeonJob, self).get_menu().entrylist)
                return warp_to_menu
            return super(DungeonJob, self).get_menu()

    def get_state_info(self):
        state_info = super(DungeonJob, self).get_state_info()
        if state_info:
            return state_info
        if bool(self.active_dungeon):
            return {'text': localization.GetByLabel('UI/Generic/CurrentLocation'),
             'color': eveColor.CRYO_BLUE,
             'icon': eveicon.location}

    def _get_warp_to_menu(self):
        if not self.scan_result or not self.in_same_system or not eveCfg.InSpace():
            return None
        return sm.GetService('scanSvc').GetScanResultMenuWithoutIgnore(self.scan_result)

    def _get_content_tag_ids(self):
        return GetDungeonContentTags(self.dungeon_id)

    def _open_dungeon_agency_page(self, *args, **kwargs):
        if self.CONTENT_GROUP_ID:
            AgencyWndNew.OpenAndShowContentGroup(contentGroupID=self.CONTENT_GROUP_ID)
