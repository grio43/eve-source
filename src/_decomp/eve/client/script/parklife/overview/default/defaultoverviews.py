#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\default\defaultoverviews.py
from eve.client.script.parklife.overview.default import categories
from eve.client.script.parklife.overview.default.const import DEFAULT, OVERVIEWS, OverviewType
from eve.client.script.parklife.overview.default.fsddefaultoverview import FsdDefaultOverview
from eve.client.script.parklife.overview.default.yamldefaultoverview import YamlDefaultOverview

class DefaultOverviews(object):

    def __init__(self, general_settings_loader):
        self._initialize(DEFAULT, general_settings_loader)

    def _create_overview(self, overview_id, overview_type, should_inform_of_update, general_settings_loader):
        if overview_type == OverviewType.FSD:
            return FsdDefaultOverview(should_inform_of_update)
        if overview_type == OverviewType.YAML:
            return YamlDefaultOverview(overview_id, should_inform_of_update, general_settings_loader)

    def _initialize(self, default_overview_id, general_settings_loader):
        self.default_overview_id = default_overview_id
        self.overviews = {}
        for overview_id, overview_type, should_inform_of_update in OVERVIEWS:
            overview = self._create_overview(overview_id, overview_type, should_inform_of_update, general_settings_loader)
            if overview:
                self.overviews[overview_id] = overview

        self.default_overview = self.overviews[self.default_overview_id]
        self._initialize_other_presets()

    def _initialize_other_presets(self):
        self.presets_from_others = {}
        current_preset_names = self.default_overview.all_presets.keys()
        for overview_id, overview in self.overviews.iteritems():
            if overview_id != self.default_overview_id:
                other_presets = overview.get_all_presets_data()
                for preset_name, preset_data in other_presets.iteritems():
                    if preset_name not in current_preset_names:
                        localized_name = overview.get_name(preset_name)
                        self.presets_from_others[preset_name] = (localized_name, preset_data)

    def should_inform_of_update(self):
        return self.default_overview.should_inform_of_update

    def switch(self, default_overview_id, general_settings_loader):
        self._initialize(default_overview_id, general_settings_loader)

    def activate_default_overview(self, general_settings_loader):
        if isinstance(self.default_overview, YamlDefaultOverview):
            self.default_overview.general_settings_loader = general_settings_loader
        self.default_overview.activate()

    def get_old_preset(self, preset_name):
        try:
            return self.presets_from_others[preset_name]
        except KeyError:
            return (None, None)

    def get_default_preset(self):
        return self.default_overview.default_preset

    def get_all_presets(self):
        return self.default_overview.all_presets

    def get_all_presets_data(self):
        return {preset_name:self.get_preset_data(preset_name) for preset_name in self.get_all_presets()}

    def get_default_preset_data(self):
        return self.default_overview.get_default_preset_data()

    def get_preset_name(self, name):
        return self.default_overview.get_name(name)

    def get_preset_name_with_category(self, name):
        return self.default_overview.get_name_with_category(name)

    def get_preset_description(self, name):
        return self.default_overview.get_description(name)

    def get_preset_category_id(self, name):
        return self.default_overview.get_category_id(name)

    def get_preset_data(self, name):
        return self.default_overview.get_data(name)

    def get_preset_names(self):
        return self.default_overview.sorted_preset_names

    def get_tabs(self):
        return self.default_overview.default_tabs
