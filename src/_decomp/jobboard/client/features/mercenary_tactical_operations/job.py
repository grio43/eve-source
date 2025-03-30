#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\mercenary_tactical_operations\job.py
import caching
import datetime
import evelink
import localization
from datetimeutils import datetime_to_filetime
from evedungeons.common.instance_identifier import DungeonInstanceIdentifier
from carbonui.control.contextMenu.menuData import MenuData
from evelink.client import owner_link
from metadata import ContentTags
from .card import MTOCard, MTOListEntry
from .page import MTOPage
from eve.common.lib.appConst import factionUnknown
from evearchetypes import GetArchetype
from evedungeons.client.data import GetDungeon
from evedungeons.client.util import GetDungeonShipRestrictions, GetDungeonContentTags
from jobboard.client.job import BaseJob
from jobboard.client.link import format_url
from objectives.common.objective_context import ObjectivesContext
from objectives.client.objective_chain import ObjectiveChain
from sovereignty.mercenaryden.client.repository import get_mercenary_den_repository
import logging
logger = logging.getLogger('mercenary_den')

class MTOJob(BaseJob):
    PAGE_CLASS = MTOPage
    CARD_CLASS = MTOCard
    LIST_ENTRY_CLASS = MTOListEntry
    MTO_OBJECTIVE_CHAIN_ID = 84

    def __init__(self, job_id, provider, mto):
        self._repository = get_mercenary_den_repository()
        self._activity_id = mto.id
        self._travel_to_objective_chain = None
        self._is_completed = False
        self._title = localization.GetByMessageID(mto.template_name_id)
        self._description = localization.GetByMessageID(mto.template_description_id)
        self._development_impact = mto.development_impact
        self._anarchy_impact = mto.anarchy_impact
        self._infomorph_bonus = mto.infomorph_bonus
        self._solar_system_id = mto.solar_system_id
        self._den_id = mto.den_id
        self._data = GetDungeon(self.dungeon_id)
        content_id = mto.id
        super(MTOJob, self).__init__(job_id, content_id, provider)

    @property
    def title(self):
        return self._title

    @property
    def subtitle(self):
        if self.is_completed:
            return
        activity = self._repository.get_mercenary_den_activity_for_character(self._activity_id)
        if activity is None:
            return
        if activity.is_started:
            return localization.GetByLabel('UI/Agency/MercDen/InProgress')
        return localization.GetByLabel('UI/Agency/MercDen/ReadyToStart')

    @property
    def description(self):
        return self._description

    @property
    def data(self):
        if self._data is None:
            self._data = GetDungeon(self.dungeon_id)
        return self._data

    @property
    def development_impact(self):
        return self._development_impact

    @property
    def anarchy_impact(self):
        return self._anarchy_impact

    @property
    def infomorph_bonus(self):
        return self._infomorph_bonus

    @property
    def archetype_data(self):
        return GetArchetype(self.archetype_id)

    @property
    def dungeon_id(self):
        activity = self._repository.get_mercenary_den_activity_for_character(self._activity_id)
        return activity.dungeon_id

    @property
    def archetype_id(self):
        return self.data.archetypeID

    @property
    def faction_id(self):
        return self.data.factionID

    @property
    def is_activity_started(self):
        activity = self._repository.get_mercenary_den_activity_for_character(self._activity_id)
        return activity.is_started

    @property
    def is_completed(self):
        return self._is_completed

    @property
    def solar_system_id(self):
        return self._solar_system_id

    @property
    def den_id(self):
        return self._den_id

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
    def gameplay_description(self):
        return localization.GetByMessageID(self.data.gameplayDescriptionID)

    @property
    def enemy(self):
        if self.faction_id is not None and self.faction_id != factionUnknown:
            return self.faction_id

    @property
    def enemy_name(self):
        if self.faction_id:
            return owner_link(self.faction_id)
        return localization.GetByLabel('UI/Common/Unknown')

    @caching.lazy_property
    def ship_restrictions(self):
        return GetDungeonShipRestrictions(self.dungeon_id)

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

    @property
    def is_linkable(self):
        return True

    @property
    def link_title(self):
        return self.title

    def get_notification_link(self):
        return evelink.Link(url=format_url(self.job_id), text=self.link_title)

    @property
    def is_expired(self):
        activity = self._repository.get_mercenary_den_activity_for_character(self._activity_id)
        if activity is None:
            return False
        return datetime.datetime.utcnow() > activity.expiry

    @property
    def expiration_time(self):
        activity = self._repository.get_mercenary_den_activity_for_character(self._activity_id)
        if activity is None:
            return
        return datetime_to_filetime(activity.expiry)

    @property
    def is_trackable(self):
        return not self.is_expired or not self.is_completed

    @property
    def active_dungeon(self):
        current_dungeon = sm.GetService('dungeonTracking').current_dungeon
        if current_dungeon is None:
            return
        instance_id = current_dungeon.instance_id
        if not isinstance(instance_id, DungeonInstanceIdentifier):
            return
        if not instance_id.is_external_activity:
            return
        if current_dungeon and instance_id.external_activity_id == self._activity_id:
            return current_dungeon

    @property
    def active_dungeon_objective_chain(self):
        active_dungeon = self.active_dungeon
        if active_dungeon and active_dungeon.objective_chain:
            return active_dungeon.objective_chain

    @property
    def objective_chain(self):
        objective_chain = self.active_dungeon_objective_chain
        if objective_chain:
            return objective_chain
        if self.is_completed:
            return
        if not self._travel_to_objective_chain:
            activity = self._repository.get_mercenary_den_activity_for_character(self._activity_id)
            if activity is None:
                return
            context = ObjectivesContext()
            context.set_values(dungeon_id=self.dungeon_id, solar_system_id=self.solar_system_id, activity_id=activity.id.hex, den_id=self.den_id)
            objective_chain = ObjectiveChain(content_id=self.MTO_OBJECTIVE_CHAIN_ID, context=context)
            objective_chain.start()
            self._travel_to_objective_chain = objective_chain
        return self._travel_to_objective_chain

    def _get_content_tag_ids(self):
        tags = [ContentTags.feature_mercenary_tactical_ops]
        dungeon_tags = GetDungeonContentTags(self.dungeon_id)
        tags.extend(dungeon_tags)
        return tags

    def mark_started(self):
        self.update()

    def mark_completed(self):
        self._is_completed = True
        self.update()

    def update_expiry(self, expiry_datetime):
        self.update()

    def on_remove(self):
        self.clear()
        if self.is_removed:
            return
        self.is_removed = True
        self.update()

    def get_cta_buttons(self):
        if self.active_dungeon:
            return []
        if self.objective_chain is None:
            return []
        objective = self.objective_chain.objectives.get('enter_mto')
        if not objective:
            return []
        buttons = []
        for task in objective.get_all_tasks():
            button = task.construct_button_widget()
            if button:
                buttons.append(button)

        return buttons

    def get_menu(self):
        active_dungeon = self.active_dungeon
        if active_dungeon:
            data = active_dungeon.get_context_menu()
            data.entrylist.extend(super(MTOJob, self).get_menu().entrylist)
            return data
        elif self.objective_chain:
            data = MenuData()
            data.AddEntry('QA', subMenuData=self.objective_chain.get_context_menu(include_blackboard=True))
            data.entrylist.extend(super(MTOJob, self).get_menu().entrylist)
            return data
        else:
            return super(MTOJob, self).get_menu()
