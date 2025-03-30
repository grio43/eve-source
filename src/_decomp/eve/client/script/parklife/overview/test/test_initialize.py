#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\test\test_initialize.py
from eve.client.script.parklife.overview.test.basetestpresetservice import UninitializedOverviewPresetsBaseTest
import eve.client.script.parklife.overview.test.presets as pConst
from eve.client.script.parklife.states import flagSamePlayerCorp, flagSameNpcCorp
import eve.client.script.parklife.stateSetting as sConst
import overviewPresets.overviewSettingsConst as oConst
from unittest import main

class LoadPresetsFromSettingsTest(UninitializedOverviewPresetsBaseTest):

    def _initialize(self):
        self._should_add_defaults = False
        self.overview_service.LoadPresetsFromUserSettings()

    def _add_defaults(self, presets):
        default_presets = self.overview_service.defaultOverviews.get_all_presets_data()
        presets_with_defaults = {}
        presets_with_defaults.update(presets)
        presets_with_defaults.update(default_presets)
        return presets_with_defaults

    def _check_results(self, expected_all = None, expected_unsaved = None):
        all = self._get_result_all()
        unsaved = self._get_result_unsaved()
        if expected_all is None:
            if self._should_add_defaults:
                self.assertEqual(all, self._add_defaults({}))
            else:
                self.assertEqual(all, {})
        elif self._should_add_defaults:
            self.assertEqual(all, self._add_defaults(expected_all))
        else:
            self.assertEqual(all, expected_all)
        if expected_unsaved is None:
            self.assertEqual(unsaved, {})
        else:
            self.assertEqual(unsaved, expected_unsaved)

    def _get_backup(self):
        return self.settings.Get(oConst.SETTING_OLD_PRESET_BACKUP)

    def _get_old(self):
        return self.settings.Get(oConst.SETTING_PRESETS)

    def _set_old(self, presets):
        self.settings.Set(oConst.SETTING_PRESETS, presets)

    def _set_new(self, presets):
        self.settings.Set(oConst.SETTING_PROFILE_PRESETS, presets)

    def _set_unsaved(self, presets):
        self.settings.Set(oConst.SETTING_PROFILE_PRESETS_NOT_SAVED, presets)

    def _get_result_all(self):
        return self.overview_service.allPresets

    def _get_result_unsaved(self):
        return self.overview_service.unsavedPresets

    def test_old_preset_setting_is_moved_to_backup(self):
        self._set_old(pConst.PRESETS)
        self._initialize()
        self.assertEqual(self._get_backup(), pConst.PRESETS)
        self.assertIsNone(self._get_old())

    def test_old_preset_setting_is_loaded_if_there_is_no_new(self):
        self._set_old(pConst.PRESETS)
        self._initialize()
        self._check_results(expected_all=pConst.PRESETS)

    def test_old_preset_setting_is_ignored_if_there_is_new(self):
        self._set_old(pConst.PRESETS)
        self._set_new(pConst.PRESETS_2)
        self._initialize()
        self._check_results(expected_all=pConst.PRESETS_2)

    def test_ewar_filters_are_ignored_from_old(self):
        self._set_old(pConst.PRESETS_WITH_EWAR_FILTERS)
        self._initialize()
        self._check_results(expected_all=pConst.PRESETS)

    def test_ewar_filters_are_not_ignored_from_new_or_unsaved(self):
        self._set_new(pConst.PRESETS_WITH_EWAR_FILTERS)
        self._set_unsaved(pConst.PRESETS_WITH_EWAR_FILTERS)
        self._initialize()
        self._check_results(expected_all=pConst.PRESETS_WITH_EWAR_FILTERS, expected_unsaved=pConst.PRESETS_WITH_EWAR_FILTERS)

    def test_items_in_lists_are_ordered_for_new(self):
        self._set_new(pConst.PRESETS_2_DISORDERED)
        self._initialize()
        self._check_results(expected_all=pConst.PRESETS_2)

    def test_items_in_lists_are_ordered_for_old(self):
        self._set_old(pConst.PRESETS_2_DISORDERED)
        self._initialize()
        self._check_results(expected_all=pConst.PRESETS_2)

    def test_unsaved_are_loaded(self):
        self._set_unsaved(pConst.PRESETS)
        self._initialize()
        self._check_results(expected_unsaved=pConst.PRESETS)

    def test_all_together(self):
        self._set_old(pConst.PRESETS)
        self._set_new(pConst.PRESETS_2_DISORDERED)
        self._set_unsaved(pConst.PRESETS_3)
        self._initialize()
        self._check_results(expected_all=pConst.PRESETS_2, expected_unsaved=pConst.PRESETS_3)


class ConvertOldSettingsToNewSettingsTest(UninitializedOverviewPresetsBaseTest):

    def _get_setting_names(self):
        return [(sConst.SETTING_OLD_BACKGROUND_STATES_CONFIG_NAME, sConst.SETTING_BACKGROUND_STATES_CONFIG_NAME),
         (sConst.SETTING_OLD_FLAG_STATES_CONFIG_NAME, sConst.SETTING_FLAG_STATES_CONFIG_NAME),
         (sConst.SETTING_OLD_FLAG_ORDER_CONFIG_NAME, sConst.SETTING_FLAG_ORDER_CONFIG_NAME),
         (sConst.SETTING_OLD_BACKGROUND_ORDER_CONFIG_NAME, sConst.SETTING_BACKGROUND_ORDER_CONFIG_NAME)]

    def test_old_settings_are_backed_up_if_they_are_a_list(self):
        value = [1,
         2,
         3,
         4,
         5]
        setting_names = self._get_setting_names()
        for old_name, new_name in setting_names:
            self.settings.Set(old_name, value)

        self.overview_service.LoadPresetsFromUserSettings()
        for old_name, new_name in setting_names:
            self.assertEqual(self.settings.Get(old_name), None)
            self.assertEqual(self.settings.Get(old_name + '_backup'), value)

    def test_old_settings_are_not_backed_up_if_they_are_not_a_list(self):
        value = 'old_name'
        setting_names = self._get_setting_names()
        for old_name, new_name in setting_names:
            self.settings.Set(old_name, value)

        self.overview_service.LoadPresetsFromUserSettings()
        for old_name, new_name in setting_names:
            self.assertEqual(self.settings.Get(old_name), 'old_name')
            self.assertEqual(self.settings.Get(old_name + '_backup'), None)

    def test_if_same_player_corp_flag_is_present_in_old_then_insert_same_npc_corp_flag(self):
        value = [1,
         2,
         flagSamePlayerCorp,
         3]
        expected_result = [1,
         2,
         flagSameNpcCorp,
         flagSamePlayerCorp,
         3]
        setting_names = self._get_setting_names()
        for old_name, new_name in setting_names:
            self.settings.Set(old_name, value)

        self.overview_service.LoadPresetsFromUserSettings()
        for old_name, new_name in setting_names:
            self.assertEqual(self.settings.Get(old_name), None)
            self.assertEqual(self.settings.Get(old_name + '_backup'), value)
            self.assertEqual(self.settings.Get(new_name), expected_result)

    def test_old_settings_are_not_backed_up_if_new_is_present(self):
        value_old = [1,
         2,
         3,
         4,
         5]
        value_new = [6,
         7,
         8,
         9,
         10]
        setting_names = self._get_setting_names()
        for old_name, new_name in setting_names:
            self.settings.Set(old_name, value_old)
            self.settings.Set(new_name, value_new)

        self.overview_service.LoadPresetsFromUserSettings()
        for old_name, new_name in setting_names:
            self.assertEqual(self.settings.Get(old_name), value_old)
            self.assertEqual(self.settings.Get(old_name + '_backup'), None)
            self.assertEqual(self.settings.Get(new_name), value_new)


class RecoverActivePresetSettingTest(UninitializedOverviewPresetsBaseTest):

    def _get_setting(self):
        return self.settings.Get(oConst.SETTING_ACTIVE_PRESET, None)

    def _set_setting(self, value):
        self.settings.Set(oConst.SETTING_ACTIVE_PRESET, value)

    def _get_active_overview_preset(self):
        return self.overview_service.activeOverviewPresetName

    def _get_active_bracket_preset(self):
        return self.overview_service.activeBracketPresetName

    def test_active_preset_is_the_default_if_not_in_settings(self):
        self.overview_service.Initialize()
        self.assertEqual(self._get_active_overview_preset(), self.overview_service.defaultPreset)

    def test_active_overview_preset_is_recovered_from_settings(self):
        value = 'myfavoritepreset'
        self.settings.Set(oConst.SETTING_ACTIVE_PRESET, value)
        self.overview_service.Initialize()
        self.assertEqual(self._get_active_overview_preset(), value)

    def test_active_bracket_preset_is_none(self):
        value = 'myfavoritepreset'
        self.settings.Set(oConst.SETTING_ACTIVE_PRESET, value)
        self.overview_service.Initialize()
        self.assertEqual(self._get_active_bracket_preset(), None)


class InitializeDefaultsTest(UninitializedOverviewPresetsBaseTest):

    def _set_new(self, presets):
        self.settings.Set(oConst.SETTING_PROFILE_PRESETS, presets)

    def _set_unsaved(self, presets):
        self.settings.Set(oConst.SETTING_PROFILE_PRESETS_NOT_SAVED, presets)

    def _get_result_all(self):
        return self.overview_service.allPresets

    def _get_result_unsaved(self):
        return self.overview_service.unsavedPresets

    def test_defaults_are_added_to_all(self):
        self._set_new(pConst.PRESETS_2_DISORDERED)
        self._set_unsaved(pConst.PRESETS_3)
        self.overview_service.Initialize()
        default_presets = self.overview_service.defaultOverviews.get_all_presets_data()
        expected_result = {}
        expected_result.update(pConst.PRESETS_2)
        expected_result.update(default_presets)
        self.assertEqual(self._get_result_all(), expected_result)
        self.assertEqual(self._get_result_unsaved(), pConst.PRESETS_3)


class AddDefaultsTest(LoadPresetsFromSettingsTest):

    def _initialize(self):
        self._should_add_defaults = True
        self.overview_service.Initialize()


if __name__ == '__main__':
    main()
