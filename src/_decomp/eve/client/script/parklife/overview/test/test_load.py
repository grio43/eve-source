#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\test\test_load.py
from eve.client.script.parklife.overview.test.basetestpresetservice import OverviewPresetsBaseTest
import eve.client.script.parklife.overview.test.defaultoverview as dConst
import overviewPresets.overviewSettingsConst as oConst
from unittest import main
from overviewPresets import overviewSettingsConst

class LoadTabTest(OverviewPresetsBaseTest):

    def _get_active_overview_preset_setting(self):
        return self.settings.Get(oConst.SETTING_ACTIVE_PRESET, None)

    def _get_active_overview_preset(self):
        return self.overview_service.activeOverviewPresetName

    def _get_active_bracket_preset(self):
        return self.overview_service.activeBracketPresetName

    def _add_preset(self, preset_name, groups = None, filtered_states = None, always_shown_states = None):
        preset = {overviewSettingsConst.PRESET_SETTINGS_GROUPS: groups or [],
         overviewSettingsConst.PRESET_SETTINGS_FILTERED_STATES: filtered_states or [],
         overviewSettingsConst.PRESET_SETTINGS_ALWAYS_SHOWN_STATES: always_shown_states or []}
        self.overview_service.allPresets[preset_name] = preset

    def _set_tab_settings(self, tab_id, overview_preset, bracket_preset, tab_name, tab_color):
        settings_by_tab = {tab_id: {oConst.SETTING_OVERVIEW_PRESET_NAME: overview_preset,
                  oConst.SETTING_BRACKET_PRESET_NAME: bracket_preset,
                  oConst.SETTING_TAB_NAME: tab_name,
                  oConst.SETTING_TAB_COLOR: tab_color}}
        self.settings.Set(oConst.SETTING_TAB_SETTINGS_OLD, settings_by_tab)

    def test_default_tabs_get_default_presets_when_there_are_no_settings(self):
        self.overview_service.LoadTab(dConst.MINING_TAB_ID)
        self.assertEqual(self._get_active_overview_preset(), dConst.MINING_PRESET_NAME)
        self.assertEqual(self._get_active_overview_preset_setting(), dConst.MINING_PRESET_NAME)
        self.assertEqual(self._get_active_bracket_preset(), dConst.MINING_BRACKET_PRESET_NAME)
        self.overview_service.LoadTab(dConst.LOOT_TAB_ID)
        self.assertEqual(self._get_active_overview_preset(), dConst.LOOT_NAME)
        self.assertEqual(self._get_active_overview_preset_setting(), dConst.LOOT_NAME)
        self.assertEqual(self._get_active_bracket_preset(), dConst.LOOT_BRACKET_PRESET_NAME)

    def test_default_tabs_get_default_presets_when_settings_have_unknown_presets(self):
        (self._set_tab_settings(dConst.MINING_TAB_ID, 'overview_preset', 'bracket_preset', 'tab_name', 'tab_color'),)
        self.overview_service.LoadTab(dConst.MINING_TAB_ID)
        self.assertEqual(self._get_active_overview_preset(), dConst.MINING_PRESET_NAME)
        self.assertEqual(self._get_active_overview_preset_setting(), dConst.MINING_PRESET_NAME)
        self.assertEqual(self._get_active_bracket_preset(), dConst.MINING_BRACKET_PRESET_NAME)


if __name__ == '__main__':
    main()
