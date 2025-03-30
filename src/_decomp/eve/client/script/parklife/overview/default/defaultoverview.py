#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\default\defaultoverview.py
import abc
import localization
from eve.client.script.parklife.overview.default import categories
from overviewPresets.overviewSettingsConst import PRESET_SETTINGS_GROUPS, PRESET_SETTINGS_ALWAYS_SHOWN_STATES, PRESET_SETTINGS_FILTERED_STATES

class BaseDefaultOverview(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, should_inform_of_update):
        self._is_loaded = False
        self._default_preset = None
        self._default_tabs = None
        self._all_presets = None
        self._sorted_preset_names = None
        self.should_inform_of_update = should_inform_of_update

    @property
    def all_presets(self):
        if self._all_presets is None:
            self._load_data()
        return self._all_presets

    @property
    def sorted_preset_names(self):
        if self._sorted_preset_names is None:
            self._load_data()
        return self._sorted_preset_names

    @property
    def default_preset(self):
        if self._default_preset is None:
            self._load_data()
        return self._default_preset

    @property
    def default_tabs(self):
        if self._default_tabs is None:
            self._load_data()
        return self._default_tabs

    def activate(self):
        pass

    def _load_data(self):
        if self._is_loaded:
            return
        self._do_load()
        self._is_loaded = True

    def get_name(self, name):
        try:
            return self.all_presets[name].name
        except KeyError:
            return None

    def get_name_with_category(self, preset_name):
        name = self.get_name(preset_name)
        if not name:
            return None
        category_name = categories.get_name(self.get_category_id(preset_name))
        return '%s: %s' % (category_name, name)

    def get_description(self, name):
        try:
            description_id = self.all_presets[name].description_id
            if description_id:
                return localization.GetByMessageID(description_id)
        except KeyError:
            return None

    def get_category_id(self, preset_name):
        try:
            return self.all_presets[preset_name].category_id
        except KeyError:
            return categories.CATEGORY_NONE

    def get_default_preset_data(self):
        return {self.default_preset: self.get_data(self.default_preset)}

    def get_all_presets_data(self):
        return {preset_name:self.get_data(preset_name) for preset_name in self.all_presets.keys()}

    def get_data(self, name):
        try:
            preset = self.all_presets[name]
            return {PRESET_SETTINGS_GROUPS: preset.groups,
             PRESET_SETTINGS_FILTERED_STATES: preset.filtered_states,
             PRESET_SETTINGS_ALWAYS_SHOWN_STATES: preset.always_shown_states}
        except (AttributeError, KeyError):
            return {PRESET_SETTINGS_GROUPS: [],
             PRESET_SETTINGS_FILTERED_STATES: [],
             PRESET_SETTINGS_ALWAYS_SHOWN_STATES: []}

    @abc.abstractmethod
    def _do_load(self):
        raise NotImplementedError


class PresetData(object):

    def __init__(self, name, short_name, name_id, groups, description_id = None, category_id = categories.CATEGORY_NONE, always_shown_states = None, filtered_states = None):
        self.name = name
        self.short_name = short_name
        self.name_id = name_id
        self.description_id = description_id
        self.category_id = category_id
        self.groups = sorted(groups)
        self.always_shown_states = always_shown_states or []
        self.filtered_states = filtered_states or []

    def __eq__(self, other):
        a = (self.name,
         self.short_name,
         self.name_id,
         self.groups,
         self.always_shown_states,
         self.filtered_states)
        b = (other.name,
         other.short_name,
         other.name_id,
         other.groups,
         other.always_shown_states,
         other.filtered_states)
        return a == b

    def __repr__(self):
        return 'name: {name}, name ID: {nameID}, short name: {shortName}, groups: {groups}'.format(name=self.name, nameID=self.name_id, shortName=self.short_name, groups=self.groups)


class TabData(object):

    def __init__(self, name, color, overview_preset, bracket_preset):
        self.name = name
        self.color = color
        self.overview_preset = overview_preset
        self.bracket_preset = bracket_preset

    def __eq__(self, other):
        a = (self.name,
         self.color,
         self.overview_preset,
         self.bracket_preset)
        b = (other.name,
         other.color,
         other.overview_preset,
         other.bracket_preset)
        return a == b

    def __repr__(self):
        return 'name: {name}, color: {color}, overview: {overview}, bracket: {bracket}'.format(name=self.name, color=self.color, overview=self.overview_preset, bracket=self.bracket_preset)
