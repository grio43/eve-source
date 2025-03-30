#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\taleclient\active_tale.py
from collections import defaultdict
import localization
from objectives.client.objective_chain import ObjectiveChain
from objectives.common.objective_context import ObjectivesContext
from taleclient.qa_tools import get_qa_context_menu

class ActiveTale(object):

    def __init__(self, tale):
        self._tale = tale
        self._context = ObjectivesContext()
        self._context.set_default_values(is_expanded=True, current_progress=0, target_progress=0)
        self._objective_chain = ObjectiveChain(content_id=tale.objectiveChainID, context=self._context)
        self._objective_chain.start()
        self.update(tale)

    def close(self):
        self._objective_chain.stop()

    @property
    def tale_id(self):
        return self._tale.taleID

    @property
    def template_id(self):
        return self._tale.templateID

    @property
    def template_class_id(self):
        return self._tale.templateClassID

    @property
    def solar_system_id(self):
        return self._tale.locationID

    @property
    def manager_solar_system_id(self):
        return getattr(self._tale, 'managerSolarSystemID', None)

    @property
    def title(self):
        if not self.title_id:
            return ''
        return localization.GetByMessageID(self.title_id)

    @property
    def title_id(self):
        return getattr(self._tale, 'templateNameID', None)

    @property
    def description(self):
        if not self.description_id:
            return ''
        return localization.GetByMessageID(self.description_id)

    @property
    def description_id(self):
        return getattr(self._tale, 'templateDescriptionID', None)

    @property
    def influence(self):
        return getattr(self._tale, 'influence', None)

    @influence.setter
    def influence(self, value):
        current_value = self.influence
        if current_value is None or current_value == value:
            return
        self._tale.influence = value
        self._context.update_value('influence', value)

    @property
    def end_time(self):
        return getattr(self._tale, 'endTime', None)

    @property
    def aggressor_faction_id(self):
        return getattr(self._tale, 'aggressorFactionID', None)

    @property
    def objective_chain(self):
        return self._objective_chain

    @property
    def context(self):
        return self._context

    def update(self, tale):
        self._tale = tale
        locations_by_scene_type = defaultdict(set)
        for solar_system_id, scene_types in getattr(tale, 'sceneTypesByLocationID', {}).iteritems():
            for scene_type in scene_types:
                locations_by_scene_type[scene_type].add(solar_system_id)

        self._context.set_values(tale_id=tale.taleID, template_id=tale.templateID, manager_solar_system_id=tale.managerSolarSystemID, scene_types_by_location=tale.sceneTypesByLocationID, locations_by_scene_type=locations_by_scene_type, current_scene_types=tale.sceneTypesByLocationID.get(session.solarsystemid2, []), influence=self.influence, end_time=self.end_time, aggressor_faction_id=self.aggressor_faction_id)

    def get_menu(self):
        return get_qa_context_menu(self)
