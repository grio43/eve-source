#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\world_events\job.py
import eveicon
import localization
from characterdata.factions import get_faction_logo_flat
from eve.client.script.ui import eveColor
from metadata import ContentTags
from objectives.client.objective_chain import ObjectiveChain
from objectives.common.objective_context import ObjectivesContext
from jobboard.client.job import BaseJob
from .card import WorldEventCard, WorldEventListEntry
from .page import WorldEventPage

class WorldEventJob(BaseJob):
    PAGE_CLASS = WorldEventPage
    CARD_CLASS = WorldEventCard
    LIST_ENTRY_CLASS = WorldEventListEntry

    def __init__(self, job_id, provider, tale_info):
        self._objective_chain = None
        self._tale_info = tale_info
        content_id = tale_info['taleID']
        super(WorldEventJob, self).__init__(job_id, content_id, provider)

    def update(self, content = None, *args, **kwargs):
        if content:
            self._tale_info = content
            if self.is_tracked and self.is_active:
                self.remove_tracked()
        super(WorldEventJob, self).update()

    @property
    def tale_id(self):
        return self._tale_info['taleID']

    @property
    def templateID(self):
        return self._tale_info['templateID']

    @property
    def influence(self):
        return self._tale_info.get('influence', None)

    @property
    def has_influence(self):
        return self.influence is not None

    @property
    def solar_system_id(self):
        return self._tale_info['managerSolarSystemID']

    @property
    def faction_id(self):
        return self._tale_info['aggressorFactionID']

    @property
    def expiration_time(self):
        return self._tale_info.get('endTime', None)

    @property
    def title(self):
        return localization.GetByMessageID(self._tale_info['templateNameID'])

    @property
    def description(self):
        description_id = self._tale_info.get('templateDescriptionID', None)
        if description_id:
            return localization.GetByMessageID(description_id)
        return ''

    @property
    def subtitle(self):
        faction_id = self.faction_id
        if faction_id:
            return cfg.eveowners.Get(faction_id).name
        return ''

    @property
    def faction_logo(self):
        if not self.faction_id:
            return None
        return get_faction_logo_flat(self.faction_id)

    @property
    def current_progress(self):
        return self.influence or 0.0

    @property
    def target_progress(self):
        return 1.0

    @property
    def progress_percentage(self):
        return float(self.current_progress) / self.target_progress

    @property
    def is_active(self):
        return bool(sm.GetService('tale').get_active_tale(self.tale_id))

    @property
    def is_available_in_browse(self):
        return super(WorldEventJob, self).is_available_in_browse

    @property
    def is_available_in_active(self):
        return self.is_tracked or self.is_active

    @property
    def is_trackable(self):
        return not self.is_active

    @property
    def is_linkable(self):
        return True

    @property
    def objective_chain(self):
        if not self._objective_chain:
            context = ObjectivesContext()
            context.set_values(location_id=self.solar_system_id)
            objective_chain = ObjectiveChain(content_id=94, context=context)
            objective_chain.start()
            self._objective_chain = objective_chain
        return self._objective_chain

    def _get_content_tag_ids(self):
        return [ContentTags.feature_world_events]
