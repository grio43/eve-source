#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\default\yamldefaultoverview.py
from eve.client.script.parklife.overview.default import categories
from eve.client.script.parklife.overview.default.const import YAML_OVERVIEWS
from eve.client.script.parklife.overview.default.defaultoverview import BaseDefaultOverview, PresetData, TabData
from eve.client.script.parklife.overview.default.errors import FailedToLoadDefaultOverview, LoadedDefaultOverviewIsEmpty
from localization import GetByMessageID
from logging import getLogger
from overviewPresets.overviewPresetUtil import GetDictFromList, ReplaceInnerListsWithDicts
from overviewPresets.overviewSettingsConst import PRESET_SETTINGS_GROUPS, PRESET_SETTINGS_ALWAYS_SHOWN_STATES, PRESET_SETTINGS_FILTERED_STATES
from overviewPresets.overviewSharingConst import OVERVIEW_SHARING_PRESETS, OVERVIEW_SHARING_TAB_SETUP
import yaml
logger = getLogger(__name__)

class YamlDefaultOverview(BaseDefaultOverview):

    def __init__(self, overview_id, should_inform_of_update, general_settings_loader = None):
        super(YamlDefaultOverview, self).__init__(should_inform_of_update)
        self.overview = YAML_OVERVIEWS[overview_id]
        self.general_settings_loader = general_settings_loader
        self.data = None

    def _get_localized_name(self, name_id):
        if name_id:
            return GetByMessageID(name_id)
        return ''

    def _get_preset_name(self, preset_name):
        name_id = self._get_preset_name_id(preset_name)
        if name_id:
            return self._get_localized_name(name_id)
        return preset_name

    def _get_preset_name_id(self, preset_name):
        name_id = self.overview['preset_name_ids'].get(preset_name, None)
        return name_id

    def _get_preset_description(self, preset_name):
        name_id = self._get_preset_description_id(preset_name)
        if name_id:
            return self._get_localized_name(name_id)
        return preset_name

    def _get_preset_description_id(self, preset_name):
        name_id = self.overview['preset_name_ids'].get(preset_name, None)
        return name_id

    def _get_tab_name(self, tab_id):
        name_id = self._get_tab_name_id(tab_id)
        if name_id:
            return self._get_localized_name(name_id)
        return str(tab_id)

    def _get_tab_name_id(self, tab_id):
        name_id = self.overview['tab_name_ids'].get(tab_id, None)
        return name_id

    def activate(self):
        if callable(self.general_settings_loader):
            self.general_settings_loader(self.data)

    def _load_yaml(self):
        try:
            source = self.overview['yaml']
            data = yaml.load(source, Loader=yaml.CLoader)
        except Exception as exc:
            raise FailedToLoadDefaultOverview('Failed to read YAML: {exc}'.format(exc=exc))

        if data is None:
            raise LoadedDefaultOverviewIsEmpty('Loaded YAML data is empty: {source}'.format(source=source))
        return data

    def _do_load(self):
        self._all_presets = {}
        self._sorted_preset_names = []
        self._default_tabs = {}
        self.data = {}
        try:
            self.data = self._load_yaml()
        except (FailedToLoadDefaultOverview, LoadedDefaultOverviewIsEmpty) as exc:
            logger.exception(exc)
            return

        if callable(self.general_settings_loader):
            self.general_settings_loader(self.data)
        presets_dict = GetDictFromList(self.data[OVERVIEW_SHARING_PRESETS])
        presets = ReplaceInnerListsWithDicts(presets_dict)
        for short_name, preset_data in presets.iteritems():
            if 'DefaultPreset' in short_name:
                name_id = int(short_name.replace('DefaultPreset_', ''))
                name = self._get_localized_name(name_id)
            else:
                name_id = self._get_preset_name_id(short_name)
                name = self._get_preset_name(short_name)
            preset = PresetData(name=name, short_name=short_name, name_id=name_id, description_id=preset_data.get('description_id', None), category_id=preset_data.get('category_id', categories.CATEGORY_NONE), groups=preset_data.get(PRESET_SETTINGS_GROUPS, []), always_shown_states=preset_data.get(PRESET_SETTINGS_ALWAYS_SHOWN_STATES, []), filtered_states=preset_data.get(PRESET_SETTINGS_FILTERED_STATES, []))
            self._all_presets[short_name] = preset

        self._sorted_preset_names = [ preset.short_name for preset in sorted(self._all_presets.values(), key=lambda k: k.name) ]
        self._default_preset = self.overview['default_preset']
        tabs_dict = GetDictFromList(self.data.get(OVERVIEW_SHARING_TAB_SETUP, []))
        tabs = ReplaceInnerListsWithDicts(tabs_dict)
        for tab_id, tab_data in tabs.iteritems():
            self._default_tabs[tab_id] = TabData(name=self._get_tab_name(tab_id), color=tab_data.get('color', None), overview_preset=tab_data.get('overview', None), bracket_preset=tab_data.get('bracket', None))
