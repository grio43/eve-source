#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\presetservice.py
import logging
from copy import deepcopy
import blue
import yaml
from carbonui import uiconst
import eve.client.script.parklife.stateSetting as stateSetting
import eve.client.script.parklife.states as stateConst
import localization
import overviewPresets.overviewSettingsConst as oConst
import overviewPresets.overviewSharingConst as sharingConst
import utillib
from bannedwords.client import bannedwords
from carbon.common.script.sys.service import Service
from eve.client.script.parklife.bracketConst import SHOW_ALL, SHOW_NONE, SHOW_DEFAULT
from eve.client.script.parklife.overview import overviewSignals
from eve.client.script.parklife.overview.blocker import OverviewBlocker
from eve.client.script.parklife.overview.default.defaultoverviews import DefaultOverviews
from eve.client.script.parklife.overview.default.settings import DefaultOverviewSettings
from eve.client.script.parklife.overview.default.informer import DefaultOverviewUpdateInformer
from eve.client.script.parklife.overview.override import OverviewOverride
from eve.client.script.parklife.state import GetStateColors, FindColorName, GetNPCGroups
from eve.client.script.parklife.tacticalConst import get_group_ids
from eve.client.script.ui.inflight.bracketsAndTargets.bracketNameFormatting import GetAllowedLabelTypes, GetAllowedVariables
from eve.client.script.ui.inflight.overview import overviewConst, overviewColumns
from eve.client.script.ui.inflight.overview.overviewConst import LABEL_TYPE, LABEL_TYPE_LINEBREAK
from eve.client.script.ui.util import utilWindows
from eve.client.script.ui.view.viewStateConst import is_entering_space
from eve.client.script.util.settings import EncodeSetting
from eveexceptions import ExceptionEater, UserError
from localization import GetByLabel
from overviewPresets.overviewPresetUtil import EncodeKeyInDict, DecodeKeyInDict, GetDeterministicListFromDict, IsPresetTheSame, GetDictFromList, ReplaceInnerListsWithDicts, ReorderList, GetOrderedListFromDict
from overviewPresets.overviewSettingsConst import SETTING_BRACKET_PRESET_NAME, SETTING_OVERVIEW_PRESET_NAME, SETTING_TAB_COLOR, SETTING_TAB_NAME, SETTING_BRACKETS_SHOWNONE, SETTING_BRACKETS_SHOWSPECIALS, SETTING_BRACKETS_SHOWALL, PRESET_SETTINGS_ALWAYS_SHOWN_STATES, PRESET_SETTINGS_GROUPS, PRESET_SETTINGS_FILTERED_STATES, MAX_TAB_NUM
from storylines.client.airnpe import is_air_npe_active
DEFAULT_BROADCAST_TO_TOP = True
log = logging.getLogger(__name__)

class OverviewPresetSvc(Service):
    __guid__ = 'svc.overviewPresetSvc'
    __displayName__ = 'Overview Preset Service'
    __serviceName__ = 'This service handles overview presets'
    __notifyevents__ = ['OnViewStateChanged']
    __update_on_reload__ = 1

    def Run(self, *args):
        Service.Run(self, *args)
        self._Setup()
        self.Initialize()

    def _HadOverviewSettings(self):
        try:
            overviewID = self.defaultOverviewSettings.get_overview()
            defaultOverviewID = self.defaultOverviewSettings.get_default_overview()
            shipLabels = settings.user.overview.Get(oConst.SETTINGS_SHIP_LABELS, None)
            activePreset = settings.user.overview.Get(oConst.SETTING_ACTIVE_PRESET, None)
            presets = settings.user.overview.Get(oConst.SETTING_PRESETS, None)
            presetsOld = settings.user.overview.Get(oConst.SETTING_OLD_PRESET_BACKUP, None)
            tabs = settings.user.overview.Get(oConst.SETTING_TAB_SETTINGS_OLD, None)
            tabsNew = settings.user.overview.Get(oConst.SETTING_TAB_SETTINGS, None)
            result = any([overviewID,
             defaultOverviewID,
             shipLabels,
             activePreset,
             presets,
             presetsOld,
             tabs,
             tabsNew])
            with ExceptionEater('Failed to log checks in _HadOverviewSettings'):
                log.info('Default Overview: Checking if player had any settings:\n    Result: {result}, \n    Overview ID: {overviewID}, \n    Default Overview ID: {defaultOverviewID}, \n    Ship Labels: {shipLabels}, \n    Active Preset: {activePreset}, \n    Presets: {presets}, \n    Presets (Backup): {presetsOld}, \n    Tabs: {tabs}, \n    Tabs (New): {tabsNew}, \n'.format(result=result, overviewID=EncodeSetting(overviewID), defaultOverviewID=EncodeSetting(defaultOverviewID), shipLabels=EncodeSetting(shipLabels), activePreset=EncodeSetting(activePreset), presets=EncodeSetting(presets), presetsOld=EncodeSetting(presetsOld), tabs=EncodeSetting(tabs), tabsNew=EncodeSetting(tabsNew)))
            return result
        except Exception as exc:
            log.exception('Failed to check if player had Overview Settings: %s', exc)
            return False

    def _Setup(self):
        self.isReadOnly = False
        self.configNamesAndDefaults = None
        self.cachedPresetsFromServer = {}
        self.overviewOverride = OverviewOverride()
        self._SetupDefaultOverviews()
        self.overviewBlocker = OverviewBlocker(initialize_function=self.Initialize, reset_function=self.ResetOverviewSettingsToDefault, set_read_only_function=self.SetReadOnly, default_settings=self.defaultOverviewSettings)

    def _SetupDefaultOverviews(self):
        self.isDefaultInitialized = False
        self.defaultOverviewSettings = DefaultOverviewSettings()
        self.hadOverviewSettings = self._HadOverviewSettings()
        self.defaultOverviews = DefaultOverviews(general_settings_loader=self._LoadGeneralSettings if not self.hadOverviewSettings else None)
        self.defaultOverviewUpdater = DefaultOverviewUpdateInformer(settings=self.defaultOverviewSettings, defaults=self.defaultOverviews, should_delay=is_air_npe_active)
        previousDefaultOverview = self.defaultOverviewSettings.get_default_overview()
        newDefaultOverview = self.defaultOverviews.default_overview_id
        if previousDefaultOverview != newDefaultOverview:
            self.defaultOverviewSettings.set_default_overview(newDefaultOverview)
            self.defaultOverviewSettings.set_informed_of_update(False)
        if not self.hadOverviewSettings:
            self.isDefaultInitialized = True
            self.defaultOverviewSettings.set_overview(newDefaultOverview)
            self.defaultOverviewSettings.set_informed_of_update(True)
            log.info('Default Overview: Setting default as the player has no settings')

    def OnViewStateChanged(self, _fromView, toView):
        if self.isDefaultInitialized or not is_entering_space(toView):
            return
        self.isDefaultInitialized = self.defaultOverviewUpdater.update()

    def ResetDefaultOverviewData(self, defaultOverviewID):
        try:
            self.defaultOverviews.switch(defaultOverviewID, self.LoadGeneralSettings)
            self._ResetSettings(overviewID=defaultOverviewID)
            self.defaultPreset = self.defaultOverviews.get_default_preset()
        except Exception as exc:
            self.LogException('Failed to reset default overview data to {overviewID}: {exc}'.format(overviewID=defaultOverviewID, exc=exc))

        self.defaultOverviewSettings.set_default_overview(self.defaultOverviews.default_overview_id)
        self.defaultOverviewSettings.set_informed_of_update(True)

    def _AddMissingPresetsFromOtherDefaultOverviews(self):
        namesToLoad = []
        oldTabSettings = self.GetSettingsByTabID()
        newTabSettings = {}
        for tabIdx, tabSettings in oldTabSettings.iteritems():
            newTabSettings[tabIdx] = tabSettings
            for setupGroupName in (SETTING_OVERVIEW_PRESET_NAME, SETTING_BRACKET_PRESET_NAME):
                if setupGroupName not in tabSettings:
                    continue
                presetName = tabSettings[setupGroupName]
                if presetName in self.allPresets:
                    continue
                name, data = self.defaultOverviews.get_old_preset(presetName)
                if name and data:
                    self.allPresets[name] = data
                    newTabSettings[tabIdx][setupGroupName] = name
                    namesToLoad.append(name)

        if namesToLoad:
            self._PersistPresets()
            self.PersistSettingsByTabID(newTabSettings)
            sm.ScatterEvent('OnOverviewPresetSaved')

    def Initialize(self):
        self.defaultPreset = self.defaultOverviews.get_default_preset()
        self.LoadPresetsFromUserSettings()
        self._AddMissingPresetsFromOtherDefaultOverviews()
        self.activeOverviewPresetName = settings.user.overview.Get(oConst.SETTING_ACTIVE_PRESET, self.defaultPreset)
        self.activeBracketPresetName = None
        self.AddDefaultPresetsToAllPresets()
        self._PersistPresets()

    def IsReadOnly(self):
        return self.isReadOnly

    def SetReadOnly(self, isReadOnly):
        self.isReadOnly = isReadOnly

    def BlockOverview(self):
        self.overviewBlocker.block()

    def UnblockOverview(self):
        self.overviewBlocker.unblock()

    def AddDefaultPresetsToAllPresets(self):
        for presetName in self.GetDefaultOverviewPresetNames():
            self.allPresets[presetName] = self.defaultOverviews.get_preset_data(presetName)

    def LoadPresetsFromUserSettings(self):
        try:
            self.ConvertOldSettingsToNewSettings()
            if settings.user.overview.Get(oConst.SETTING_PRESETS, None) is not None:
                oldPresets = settings.user.overview.Get(oConst.SETTING_PRESETS, {}).copy()
                settings.user.overview.Set(oConst.SETTING_OLD_PRESET_BACKUP, oldPresets.copy())
                for presetKey, presetValue in oldPresets.iteritems():
                    presetValue.pop('ewarFilters', None)

                settings.user.overview.Delete(oConst.SETTING_PRESETS)
            else:
                oldPresets = {}
        except Exception as e:
            log.exception('Error when migrating overview presets, e = %s' % e)
            settings.user.overview.Delete(oConst.SETTING_PRESETS)
            oldPresets = {}

        self.allPresets = settings.user.overview.Get(oConst.SETTING_PROFILE_PRESETS, oldPresets)
        self.unsavedPresets = self._GetUnsavedPresets()
        self.ReorderPresets(self.allPresets)
        self.ReorderPresets(self.unsavedPresets)

    def _GetUnsavedPresets(self):
        default = settings.user.overview.Get(oConst.SETTING_PROFILE_PRESETS_NOT_SAVED, {})
        unsavedPresets = settings.user.overview.Get(oConst.SETTING_PROFILE_PRESETS_NOT_SAVED2, default)
        return unsavedPresets

    def ConvertOldSettingsToNewSettings(self):
        with ExceptionEater('Failed to convert old overview settings to new'):
            for oldSettingName, newSettingName in ((stateSetting.SETTING_OLD_BACKGROUND_STATES_CONFIG_NAME, stateSetting.SETTING_BACKGROUND_STATES_CONFIG_NAME),
             (stateSetting.SETTING_OLD_FLAG_STATES_CONFIG_NAME, stateSetting.SETTING_FLAG_STATES_CONFIG_NAME),
             (stateSetting.SETTING_OLD_FLAG_ORDER_CONFIG_NAME, stateSetting.SETTING_FLAG_ORDER_CONFIG_NAME),
             (stateSetting.SETTING_OLD_BACKGROUND_ORDER_CONFIG_NAME, stateSetting.SETTING_BACKGROUND_ORDER_CONFIG_NAME)):
                oldSettings = settings.user.overview.Get(oldSettingName, None)
                if oldSettings and settings.user.overview.Get(newSettingName, stateSetting.SETTING_NOT_PRESENT) == stateSetting.SETTING_NOT_PRESENT:
                    backupName = oldSettingName + '_backup'
                    oldSettingsCopy = oldSettings[:] if isinstance(oldSettings, list) else None
                    settings.user.overview.Set(backupName, oldSettingsCopy)
                    if oldSettings and stateConst.flagSamePlayerCorp in oldSettings:
                        indexOfCorpState = oldSettings.index(stateConst.flagSamePlayerCorp)
                        oldSettings.insert(indexOfCorpState, stateConst.flagSameNpcCorp)
                    settings.user.overview.Set(newSettingName, oldSettings)
                    settings.user.overview.Delete(oldSettingName)

    def ReorderPresets(self, presetDict):
        try:
            for presetKey, presetValue in presetDict.iteritems():
                ReorderList(presetValue, (PRESET_SETTINGS_GROUPS, PRESET_SETTINGS_FILTERED_STATES, PRESET_SETTINGS_ALWAYS_SHOWN_STATES))

        except Exception as e:
            oldPresets = settings.user.overview.Get(oConst.SETTING_OLD_PRESET_BACKUP, {})
            log.exception('Error when reordering presets, e=%s, oldPresets=%s' % (e, oldPresets))
            presetDict.clear()

    def GetDefaultOverviewPresetNames(self):
        return self.defaultOverviews.get_preset_names()

    def GetCustomPresetNames(self):
        defaultPresetNames = self.GetDefaultOverviewPresetNames()
        return [ presetName for presetName in self.allPresets if presetName not in defaultPresetNames ]

    def GetDefaultPreset(self):
        return self.defaultPreset

    def GetDefaultOverviewDisplayName(self, presetName):
        return self.defaultOverviews.get_preset_name(presetName)

    def GetDefaultOverviewDisplayNameWithCategory(self, presetName):
        return self.defaultOverviews.get_preset_name_with_category(presetName)

    def GetDefaultOverviewDescription(self, presetName):
        return self.defaultOverviews.get_preset_description(presetName)

    def GetDefaultOverviewCategoryID(self, presetName):
        return self.defaultOverviews.get_preset_category_id(presetName)

    def GetDefaultOverviewCategoryName(self, presetName):
        return self.defaultOverviews.get_preset_category_name(presetName)

    def GetAllPresets(self):
        if not self.allPresets:
            self.AddDefaultPresetsToAllPresets()
        return self.allPresets

    def GetPresetFromKey(self, presetName):
        if self.IsUnsavedPreset(presetName):
            preset = self.unsavedPresets.get(self._ExtractPresetNameFromTuple(presetName), None)
        else:
            self.GetAllPresets()
            preset = self.allPresets.get(presetName, None)
        if not preset:
            preset = self.allPresets.get(self.defaultPreset, {})
        return preset

    def GetPresetGroupsFromKey(self, presetName):
        preset = self.GetPresetFromKey(presetName)
        if not preset:
            return []
        return preset.get(PRESET_SETTINGS_GROUPS, [])

    def GetGroups(self, presetName = None):
        if not presetName:
            presetName = self.GetActiveOverviewPresetName()
        return self.GetPresetGroupsFromKey(presetName)

    def IsGroupIDShown(self, groupID, presetName = None):
        if groupID not in get_group_ids():
            return False
        return groupID in self.GetGroups(presetName)

    def GetBracketGroups(self, presetName = None):
        if not presetName:
            presetName = self.GetActiveBracketPresetName()
        return self.GetPresetGroupsFromKey(presetName)

    def FindPresetForStates(self, isBracket = False, presetName = None):
        if not presetName:
            if isBracket:
                presetName = self.GetActiveBracketPresetName()
            else:
                presetName = self.GetActiveOverviewPresetName()
        preset = self.GetPresetFromKey(presetName)
        if preset is None:
            preset = self.GetPresetFromKey(self.defaultPreset)
        return preset

    def GetFilteredStates(self, isBracket = False, presetName = None):
        preset = self.FindPresetForStates(isBracket, presetName)
        return preset.get(PRESET_SETTINGS_FILTERED_STATES, [])

    def GetAlwaysShownStates(self, isBracket = False, presetName = None):
        preset = self.FindPresetForStates(isBracket, presetName)
        return preset.get(PRESET_SETTINGS_ALWAYS_SHOWN_STATES, [])

    def GetValidGroups(self, isBracket = False, presetName = None):
        if isBracket:
            groups = set(self.GetBracketGroups(presetName=presetName))
        else:
            groups = set(self.GetGroups(presetName=presetName))
        availableGroups = get_group_ids()
        return groups.intersection(availableGroups)

    def GetFilteredStatesByPresetKey(self, presetName = ''):
        preset = self.GetPresetFromKey(presetName)
        if not preset:
            return []
        return preset.get(PRESET_SETTINGS_FILTERED_STATES, [])

    def GetAlwaysShownStatesByPresetKey(self, presetName = ''):
        preset = self.GetPresetFromKey(presetName)
        if not preset:
            return []
        return preset.get(PRESET_SETTINGS_ALWAYS_SHOWN_STATES, [])

    def GetOverrideState(self, slimItem):
        return self.overviewOverride.get_state_slim_item(slimItem)

    def GetPresetsMenuElevated(self):
        m = []
        m.append(('Switch to New Default Overview', lambda : self.ResetDefaultOverviewData('jotunn_default')))
        m.append(('Switch to Old Default Overview', lambda : self.ResetDefaultOverviewData('old_default')))
        m.append(('Reset informing of new Default for next login', self._ResetInformingOfNewDefault))
        return m

    def _ResetInformingOfNewDefault(self):
        self.defaultOverviewSettings.set_default_overview('')
        self.defaultOverviewSettings.set_informed_of_update(False)

    def PersistBracketSettings(self, tabID, showState, showingSpecials):
        tabsetting = self.GetTabSettings(tabID)
        if tabsetting:
            tabsetting[SETTING_BRACKETS_SHOWALL] = showState == SHOW_ALL
            tabsetting[SETTING_BRACKETS_SHOWNONE] = showState == SHOW_NONE
            tabsetting[SETTING_BRACKETS_SHOWSPECIALS] = showingSpecials

    def GetBracketShowState(self, tabID):
        tabSettings = self.GetTabSettings(tabID)
        if tabSettings.get(SETTING_BRACKETS_SHOWALL, False):
            return SHOW_ALL
        elif tabSettings.get(SETTING_BRACKETS_SHOWNONE, False):
            return SHOW_NONE
        else:
            return SHOW_DEFAULT

    def LoadTab(self, tabID):
        tabsettings = self.GetSettingsByTabID().get(tabID, {})
        presetName = tabsettings.get(SETTING_OVERVIEW_PRESET_NAME, None)
        self.LoadPreset(presetName, False, notSavedPreset=self.IsUnsavedPreset(presetName))
        bracketPresetName = tabsettings.get(SETTING_BRACKET_PRESET_NAME, None)
        showSpecials = tabsettings.get(SETTING_BRACKETS_SHOWSPECIALS, False)
        if not self.IsBracketFilterDictatingTab(tabID):
            return
        self.LoadBracketPreset(bracketPresetName, showSpecials=showSpecials, bracketShowState=self.GetBracketShowState(tabID))

    def IsBracketFilterDictatingTab(self, tabID):
        wndInstID = self.GetWindowInstanceID(tabID)
        return self.IsBracketFilterDictatingWindow(wndInstID)

    def IsBracketFilterDictatingWindow(self, wndInstID):
        return wndInstID == self.GetDefaultWindowInstanceID()

    def LoadPreset(self, presetName, updateTabSettings = True, notSavedPreset = False):
        if not notSavedPreset:
            presetName = self._GetPresetNameFromNotSaved(presetName)
        self.activeOverviewPresetName = presetName
        settings.user.overview.Set(oConst.SETTING_ACTIVE_PRESET, presetName)
        sm.ScatterEvent('OnOverviewPresetLoaded', presetName, None)

    def _ApplyPresetToCurrentlySelectedTab(self, presetName):
        overview = sm.GetService('tactical').GetPanelForUpdate(overviewConst.WINDOW_ID)
        if overview is not None and hasattr(overview, 'GetSelectedTabID'):
            tabID = overview.GetSelectedTabID()
            tabSettings = self.GetSettingsByTabID()
            if tabID in tabSettings.keys():
                tabSettings[tabID][oConst.SETTING_OVERVIEW_PRESET_NAME] = presetName
            self.UpdateSettingsByTabID(tabSettings)

    def _GetPresetNameFromNotSaved(self, presetName):
        presets = self.GetAllPresets()
        if self.IsUnsavedPreset(presetName):
            log.warning("Loading temp name when I shouldn't be, label = %s" % repr(presetName))
            presetName = self._ExtractPresetNameFromTuple(presetName)
        defaultPresetNames = self.GetDefaultOverviewPresetNames()
        if presetName not in presets and presetName not in defaultPresetNames:
            log.info("Trying to load a preset that doesn't exist, load default instead - presetName=%s" % repr(presetName))
            presetName = self.defaultPreset
        return presetName

    def LoadBracketPreset(self, presetName, showSpecials = None, bracketShowState = None):
        if presetName not in self.allPresets and presetName not in (None, oConst.BRACKET_FILTER_SHOWALL):
            return
        self.activeBracketPresetName = presetName
        sm.GetService('bracket').SoftReload(showSpecials, bracketShowState)

    def GetActiveBracketPresetName(self):
        isInvalid = not self.activeBracketPresetName or self.activeBracketPresetName not in self.allPresets or self.IsUnsavedPreset(self.activeBracketPresetName) and self._ExtractPresetNameFromTuple(self.activeBracketPresetName) not in self.unsavedPresets
        if isInvalid:
            self.activeBracketPresetName = oConst.BRACKET_FILTER_SHOWALL
        return self.activeBracketPresetName

    def GetActiveOverviewPresetName(self):
        presetName = self.activeOverviewPresetName
        isInvalid = not presetName or presetName not in self.allPresets and self.IsUnsavedPreset(presetName) and self._ExtractPresetNameFromTuple(presetName) not in self.unsavedPresets
        if isInvalid:
            self.activeOverviewPresetName = self.defaultPreset
        return presetName

    def _ResetActivePresets(self):
        self.activeOverviewPresetName = self.defaultPreset
        self.activeBracketPresetName = None

    def _ResetPresetsToDefault(self):
        self.allPresets = {}
        self.AddDefaultPresetsToAllPresets()

    def ResetOverviewSettingsToDefault(self):
        overviewID = self.defaultOverviews.default_overview_id
        self._ResetSettings(overviewID)

    def ResetOverviewSettingsToDefaultWithPrompt(self):
        if eve.Message('ResetAllOverviewSettings', {}, uiconst.YESNO) != uiconst.ID_YES:
            return
        self.StoreCurrentProfileDataInSettings()
        self.ResetOverviewSettingsToDefault()
        self.defaultOverviewSettings.set_informed_of_update(True)

    def _ResetSettings(self, overviewID = None):
        self._ResetPresetsToDefault()
        self._ResetActivePresets()
        self.unsavedPresets = {}
        self._DeleteAllOverviewSettingValues()
        stateSvc = sm.StartService('stateSvc')
        stateSvc.SetDefaultShipLabel('default')
        stateSvc.ResetColors()
        self.defaultOverviews.activate_default_overview(self.LoadGeneralSettings)
        self.UpdateSettingsByTabID(self._GetDefaultSettingsByTabID(), overviewID)
        sm.GetService('bracket').Reload()

    def _DeleteAllOverviewSettingValues(self):
        values = settings.user.overview.GetValues()
        keys = values.keys()
        for key in keys:
            if key in oConst.NEVER_DELETE_SETTINGS:
                continue
            settings.user.overview.Delete(key)

    def SavePresetAs(self, presetName = None):
        if not presetName:
            presetName = self.GetActiveOverviewPresetName()
        newPresetName = utilWindows.NamePopup(localization.GetByLabel('UI/Common/Buttons/SaveAs'), localization.GetByLabel('UI/Overview/FilterName'), setvalue=self._GetPresetNameForSaveWindow(presetName), maxLength=80)
        if newPresetName:
            if self.IsDefaultPresetName(newPresetName):
                eve.Message('InvalidPresetName')
                return self.SavePresetAs(presetName)
            if newPresetName in self.allPresets:
                if eve.Message('AlreadyHaveLabel', {}, uiconst.YESNO) != uiconst.ID_YES:
                    return self.SavePresetAs(presetName)
            self.SavePreset(presetName, newPresetName)

    def IsDefaultPresetName(self, presetName):
        presetName = presetName.lower()
        for p in self.GetDefaultOverviewPresetNames():
            if p.lower() == presetName:
                return True
            if self.GetDefaultOverviewDisplayName(p).lower() == presetName:
                return True

        return False

    def SavePreset(self, presetName, newPresetName = None):
        if newPresetName is None:
            newPresetName = presetName
        bannedwords.check_words_allowed(newPresetName)
        newPreset = {PRESET_SETTINGS_GROUPS: self.GetGroups(presetName=presetName)[:],
         PRESET_SETTINGS_FILTERED_STATES: self.GetFilteredStates(presetName=presetName)[:],
         PRESET_SETTINGS_ALWAYS_SHOWN_STATES: self.GetAlwaysShownStates(presetName=presetName)[:]}
        self.unsavedPresets.pop(newPresetName, None)
        self.unsavedPresets.pop(presetName, None)
        self.allPresets[newPresetName] = newPreset
        self._PersistPresets()
        self.LoadPreset(newPresetName)
        if presetName != newPresetName:
            overviewSignals.on_preset_saved_as(presetName, newPresetName)
        else:
            overviewSignals.on_preset_saved(newPresetName)
        sm.ScatterEvent('OnOverviewPresetSaved')

    def _GetPresetNameForSaveWindow(self, presetName):
        return self._GetPresetDisplayName(presetName)

    def RevertUnsaved(self, presetName):
        if not self.IsUnsavedPreset(presetName):
            return
        preset = self.unsavedPresets.pop(presetName, None)
        if preset:
            overviewSignals.on_preset_restored(presetName)

    def DeletePreset(self, presetName):
        if presetName in self.allPresets:
            self.allPresets.pop(presetName)
        if presetName in self.unsavedPresets:
            self.unsavedPresets.pop(presetName)
        if presetName == self.activeOverviewPresetName:
            self.LoadPreset(self.defaultPreset)
        sm.ScatterEvent('OnOverviewPresetSaved')
        overviewSignals.on_preset_deleted(presetName)

    def GetMotifiedSetting(self, value, add, current):
        if add:
            if type(value) == list:
                for each in value:
                    if each not in current:
                        current.append(each)

            elif value not in current:
                current.append(value)
        elif type(value) == list:
            for each in value:
                while each in current:
                    current.remove(each)

        else:
            while value in current:
                current.remove(value)

        current.sort()
        return current

    def SetNPCGroups(self):
        sendGroupIDs = []
        userSettings = self.GetGroups()
        for cat, groupdict in GetNPCGroups().iteritems():
            for groupname, groupids in groupdict.iteritems():
                for groupid in groupids:
                    if groupid in userSettings:
                        sendGroupIDs += groupids
                        break

        if sendGroupIDs:
            changeList = [('groups', sendGroupIDs, 1)]
            self.ChangeSettings(changeList=changeList)

    def AddGroupIDToPreset(self, groupID, presetName = None):
        self.ChangeSettings([(PRESET_SETTINGS_GROUPS, groupID, 1)], presetName)

    def RemoveGroupIDFromPreset(self, groupID, presetName = None):
        self.ChangeSettings([(PRESET_SETTINGS_GROUPS, groupID, 0)], presetName)

    def ChangeSettings(self, changeList, presetName = None):
        if not presetName:
            presetName = self.GetActiveOverviewPresetName()
        activePreset = self.GetPresetFromKey(presetName).copy()
        changeCounter = 0
        for eachChange in changeList:
            settingID, value, add = eachChange
            current = None
            if settingID == PRESET_SETTINGS_FILTERED_STATES:
                current = self.GetFilteredStatesByPresetKey(presetName)[:]
            elif settingID == PRESET_SETTINGS_ALWAYS_SHOWN_STATES:
                current = self.GetAlwaysShownStatesByPresetKey(presetName)[:]
            elif settingID == PRESET_SETTINGS_GROUPS:
                current = self.GetPresetGroupsFromKey(presetName)[:]
            if current is None:
                continue
            changeCounter += 1
            current = self.GetMotifiedSetting(value, add, current)
            activePreset[settingID] = current

        if changeCounter == 0:
            return
        if self.IsUnsavedPreset(presetName):
            basePresetName = self._ExtractPresetNameFromTuple(presetName)
            unsavedName = presetName
        else:
            basePresetName = presetName
            unsavedName = self.GetUnsavedPresetName(presetName)
        basePreset = self.allPresets.get(basePresetName, {})
        if IsPresetTheSame(basePreset, activePreset):
            self.RestoreSavedPreset(basePresetName, unsavedName)
        else:
            self.unsavedPresets[basePresetName] = activePreset
            self._PersistPresets()
            self.LoadPreset(unsavedName, notSavedPreset=True)
        overviewSignals.on_preset_saved(presetName)

    def RestoreSavedPreset(self, basePresetName, unsavedName):
        self.ChangeTabSettingsToUseBasePreset(unsavedName, basePresetName)
        self.unsavedPresets.pop(basePresetName, None)
        self._PersistPresets()
        self.LoadPreset(basePresetName, notSavedPreset=True)
        overviewSignals.on_preset_restored(basePresetName)

    def ChangeTabSettingsToUseBasePreset(self, tempPresetName, basePresetName):
        tabSettings = self.GetSettingsByTabID()
        for _, tSetting in tabSettings.iteritems():
            if tSetting.get(SETTING_OVERVIEW_PRESET_NAME) == tempPresetName:
                tSetting[SETTING_OVERVIEW_PRESET_NAME] = basePresetName
            if tSetting.get(SETTING_BRACKET_PRESET_NAME) == tempPresetName:
                tSetting[SETTING_BRACKET_PRESET_NAME] = basePresetName

        self.PersistSettingsByTabID(tabSettings)

    def GetSettingForGroups(self, presetName = None):
        if presetName is None:
            presetName = self.GetActiveOverviewPresetName()
        preset = self.GetPresetFromKey(presetName)
        try:
            return preset[PRESET_SETTINGS_GROUPS][:]
        except KeyError:
            return set()

    def SavePresetGroupFilters(self, groupList, presetName = None):
        if not presetName:
            presetName = self.GetActiveOverviewPresetName()
        preset = self.GetPresetFromKey(presetName).copy()
        preset[PRESET_SETTINGS_GROUPS] = groupList
        if self.IsUnsavedPreset(presetName):
            newTempPresetName = self._ExtractPresetNameFromTuple(presetName)
            unsavedName = presetName
        else:
            newTempPresetName = presetName
            unsavedName = self.GetUnsavedPresetName(presetName)
        self.unsavedPresets[newTempPresetName] = preset
        self.LoadPreset(unsavedName, notSavedPreset=True)
        self._PersistPresets()
        overviewSignals.on_preset_saved(presetName)

    def GetUnsavedPresetName(self, presetName):
        return presetName

    def IsUnsavedPreset(self, presetName):
        return presetName in self.unsavedPresets

    def IsTuplePresetName(self, presetName):
        return isinstance(presetName, (list, tuple))

    def GetPresetDisplayName(self, presetName, showCategory = True):
        if presetName == oConst.BRACKET_FILTER_SHOWALL:
            return GetByLabel('UI/Overview/ShowAllBrackets')
        else:
            display_name = self._GetPresetDisplayName(presetName, showCategory)
            if self.IsUnsavedPreset(presetName):
                return GetByLabel('UI/Overview/PresetNotSaved', presetName=display_name)
            return display_name

    def _GetPresetDisplayName(self, presetName, showCategory = True):
        if presetName in self.defaultOverviews.get_all_presets():
            if showCategory:
                return self.GetDefaultOverviewDisplayNameWithCategory(presetName)
            else:
                return self.GetDefaultOverviewDisplayName(presetName)
        else:
            return presetName

    def _ExtractPresetNameFromTuple(self, presetName):
        if self.IsTuplePresetName(presetName):
            return presetName[1]
        else:
            return presetName

    def _PersistPresets(self):
        settings.user.overview.Set(oConst.SETTING_PROFILE_PRESETS, self.allPresets)
        settings.user.overview.Set(oConst.SETTING_PROFILE_PRESETS_NOT_SAVED, self.unsavedPresets)

    def GetStringForOverviewPreset(self, data):
        dataString = yaml.safe_dump(data)
        return dataString

    def GetOverviewDataForSave(self, presetsToUse = None):
        data = self.GetGeneralSettings()
        presetsInUseDict = self.GetPresetsInUse(presetsToUse=presetsToUse)
        presetsInUseList = presetsInUseDict.values()
        presetsInUseList.sort()
        data[sharingConst.OVERVIEW_SHARING_PRESETS] = presetsInUseList
        data[sharingConst.OVERVIEW_SHARING_TAB_SETUP] = self.GetTabSettingsForSaving()
        return data

    def GetGeneralSettings(self):
        data = {}
        settingsAndDefaults = self.GetSettingsNamesAndDefaults()
        userSettingsTuples = []
        for configName, defaultSetting in settingsAndDefaults.iteritems():
            myValue = bool(settings.user.overview.Get(configName, defaultSetting))
            if myValue == defaultSetting:
                continue
            userSettingsTuples.append((configName, myValue))

        userSettingsTuples.sort()
        data[sharingConst.OVERVIEW_SHARING_USERSETTINGS] = userSettingsTuples
        stateSvc = sm.GetService('stateSvc')
        flagOrder = stateSvc.GetStateOrder('Flag')
        backgroundOrder = stateSvc.GetStateOrder('Background')
        data[sharingConst.OVERVIEW_SHARING_FLAG_ORDER] = flagOrder
        data[sharingConst.OVERVIEW_SHARING_BACKGROUND_ORDER] = backgroundOrder
        flagStates = stateSvc.GetStateStates('flag')[:]
        backgroundStates = stateSvc.GetStateStates('background')[:]
        flagStates.sort()
        backgroundStates.sort()
        data[sharingConst.OVERVIEW_SHARING_FLAG_STATES] = flagStates
        data[sharingConst.OVERVIEW_SHARING_BG_STATES] = backgroundStates
        columnOrder = overviewColumns.GetColumnOrder()
        columnsIDs = overviewColumns.GetColumns()[:]
        columnsIDs.sort()
        data[sharingConst.OVERVIEW_SHARING_COLUMN_ORDER] = columnOrder
        data[sharingConst.OVERVIEW_SHARING_OVERVIEW_COLUMNS] = columnsIDs
        colorDict = sm.GetService('stateSvc').GetFixedColorSettings()
        newColorDict = self.GetColorsToSave(colorDict)
        colorDictAsList = GetDeterministicListFromDict(newColorDict)
        data[sharingConst.OVERVIEW_SHARING_STATE_COLORS_LIST] = colorDictAsList
        stateBlinks = sm.GetService('stateSvc').defaultBlinkStates.copy()
        stateBlinks.update(settings.user.overview.Get(oConst.SETTING_STATE_BLINKS, {}))
        stateBlinks = EncodeKeyInDict(stateBlinks)
        stateBlinksList = GetDeterministicListFromDict(stateBlinks)
        data[sharingConst.OVERVIEW_SHARING_STATE_BLINKS] = stateBlinksList
        shipLabels = sm.GetService('stateSvc').GetShipLabels()
        shipLabelsList = []
        shipLabelOrder = []
        allowedLabelTypes = GetAllowedLabelTypes()
        allowedVariables = GetAllowedVariables()
        for eachConfig in shipLabels:
            configType = eachConfig[LABEL_TYPE]
            if configType not in allowedLabelTypes:
                continue
            eachConfigCopy = eachConfig.copy()
            for k in eachConfigCopy.keys():
                if k not in allowedVariables:
                    eachConfigCopy.pop(k, None)

            shipLabelOrder.append(configType)
            orderedConfig = GetDeterministicListFromDict(eachConfig)
            shipLabelsList.append((configType, orderedConfig))

        shipLabelsList.sort()
        data[sharingConst.OVERVIEW_SHARING_SHIP_LABELS] = shipLabelsList
        data[sharingConst.OVERVIEW_SHARING_SHIP_LABEL_ORDER] = shipLabelOrder
        return data

    def GetPresetsInUse(self, presetsToUse = None):
        allPresets = self.GetAllPresets()
        allTabSettings = self.GetSettingsByTabID()
        defaultPresetNames = self.GetDefaultOverviewPresetNames()
        return self.GetPresetsInUseFromTabSettings(allTabSettings, allPresets, defaultPresetNames, presetsToUse=presetsToUse)

    def GetPresetsInUseFromTabSettings(self, allTabSettings, allPresets, exludePresets = [], presetsToUse = None):
        presetsInUse = {}

        def ShouldAddPreset(presetName):
            if presetName not in allPresets:
                return False
            if presetName in presetsInUse:
                return False
            if presetName in exludePresets:
                return False
            return True

        def AddPreset(presetName):
            presetAsList = GetDeterministicListFromDict(allPresets[presetName])
            presetsInUse[presetName] = (presetName, presetAsList)

        if presetsToUse:
            for presetName in presetsToUse:
                if ShouldAddPreset(presetName):
                    AddPreset(presetName)

        else:
            for tabIdx, tabSettings in allTabSettings.iteritems():
                if tabIdx >= MAX_TAB_NUM:
                    break
                for setupGroupName in (SETTING_OVERVIEW_PRESET_NAME, SETTING_BRACKET_PRESET_NAME):
                    presetName = tabSettings[setupGroupName]
                    if self.IsUnsavedPreset(presetName):
                        presetName = self._ExtractPresetNameFromTuple(presetName)
                    if ShouldAddPreset(presetName):
                        AddPreset(presetName)

        return presetsInUse

    def GetSettingsNamesAndDefaults(self):
        if self.configNamesAndDefaults is None:
            self.configNamesAndDefaults = {oConst.SETTING_NAME_APPLY_STRUCTURE: True,
             oConst.SETTING_NAME_APPLY_OTHER_OBJ: False,
             oConst.SETTING_NAME_SMALL_TAGS: False,
             oConst.SETTING_NAME_SMALL_TEXT: False,
             oConst.SETTING_HIDE_CORP_TICKER: False,
             oConst.SETTING_BROADCAST_TO_TOP: DEFAULT_BROADCAST_TO_TOP,
             oConst.SETTING_BIGGEST_DMG_DEALER: True,
             oConst.SETTING_MODULE_HAIRLINES: True,
             oConst.SETTING_TARGET_CROSSHAIR: True,
             oConst.SETTING_TARGET_RANGE: True,
             'showCategoryInTargetRange_6': True,
             'showCategoryInTargetRange_11': True,
             'showCategoryInTargetRange_18': True}
        return self.configNamesAndDefaults

    def GetSettingValueOrDefaultFromName(self, settingName, fallbackDefaultValue):
        defaultValue = self.GetDefaultSettingValueFromName(settingName, fallbackDefaultValue)
        return settings.user.overview.Get(settingName, defaultValue)

    def GetDefaultSettingValueFromName(self, settingName, fallbackDefaultValue):
        defaultNameAndSettings = self.GetSettingsNamesAndDefaults()
        return defaultNameAndSettings.get(settingName, fallbackDefaultValue)

    def LoadSharedOverviewProfile(self, presetKey, overviewName):
        if eve.Message('LoadOverviewProfile', {}, uiconst.YESNO, default=uiconst.ID_NO) != uiconst.ID_YES:
            return
        yamlString = self.cachedPresetsFromServer.get(presetKey, None)
        if yamlString is None:
            yamlString = sm.RemoteSvc('overviewPresetMgr').GetStoredPreset(presetKey)
        if yamlString is None:
            raise UserError('OverviewProfileLoadingError')
        self.StoreCurrentProfileDataInSettings()
        dataList = yaml.safe_load(yamlString)
        data = GetDictFromList(dataList)
        self.LoadOverviewProfileFromDict(data, overviewName, presetKey, saveInHistory=True)

    def RestoreAutoSavedOverviewProfile(self):
        restoreData = settings.user.overview.Get(oConst.SETTING_RESTORE_DATA, {})
        if not restoreData:
            return
        data = restoreData['data']
        overviewName = restoreData['name']
        self.LoadOverviewProfileFromDict(data, overviewName)
        settings.user.overview.Set(oConst.SETTING_RESTORE_DATA, {})

    def LoadOverviewProfileFromDict(self, data, overviewName, presetKey = None, saveInHistory = False):
        self.LoadGeneralSettings(data)
        presetDict = GetDictFromList(data[sharingConst.OVERVIEW_SHARING_PRESETS])
        tabPresets = ReplaceInnerListsWithDicts(presetDict)
        self.UpdateAllPresets(tabPresets)
        tabSetup = self.GetTabSetupToLoad(data)
        self.PersistSettingsByTabID(tabSetup)
        settings.user.ui.Set('overviewProfileName', overviewName)
        if presetKey and saveInHistory:
            self.SaveOverviewLinkInSettings(overviewName, presetKey)
        self.UpdateSettingsByTabID(tabSetup)
        self._CheckResetTabIDsByWindowInstanceIDs()
        sm.ScatterEvent('OnReloadingOverviewProfile')

    def _CheckResetTabIDsByWindowInstanceIDs(self):
        if not self._IsTabsByWndInstIDDataValid(self.GetTabIDsByWindowInstanceID()):
            self.PersistTabIDsByWindowInstanceID(self._GetDefaultTabIDsByWindowInstanceID())
            sm.ScatterEvent('OnOverviewTabsChanged')

    def StoreCurrentProfileDataInSettings(self):
        oldProfileData = self.GetOverviewDataForSave()
        oldOverviewName = self.GetOverviewName()
        now = blue.os.GetWallclockTime()
        oldProfileInfo = {'data': oldProfileData,
         'name': oldOverviewName,
         'timestamp': now}
        settings.user.overview.Set(oConst.SETTING_RESTORE_DATA, oldProfileInfo)

    def SaveOverviewLinkInSettings(self, overviewName, presetKey):
        timestamp = blue.os.GetWallclockTime()
        presetHistoryKeys = settings.user.overview.Get(oConst.SETTING_HISTORY_KEYS, {})
        if presetKey in presetHistoryKeys:
            entry = presetHistoryKeys[presetKey]
            entry['overviewName'] = overviewName
            entry['timestamp'] = timestamp
        else:
            entry = {'overviewName': overviewName,
             'presetKey': presetKey,
             'timestamp': timestamp}
            presetHistoryKeys[presetKey] = entry
        settings.user.overview.Set(oConst.SETTING_HISTORY_KEYS, presetHistoryKeys)

    def _LoadGeneralSettings(self, data):
        configNamesAndDefaultsCopy = self.GetSettingsNamesAndDefaults().copy()
        userSettings = data.get('userSettings', [])
        for configName, settingValue in userSettings:
            if configName not in configNamesAndDefaultsCopy:
                continue
            settings.user.overview.Set(configName, settingValue)
            configNamesAndDefaultsCopy.pop(configName)

        for configName, defaultValue in configNamesAndDefaultsCopy.iteritems():
            settings.user.overview.Set(configName, defaultValue)

        flagOrder = data.get(sharingConst.OVERVIEW_SHARING_FLAG_ORDER, [])
        backgroundOrder = data.get(sharingConst.OVERVIEW_SHARING_BACKGROUND_ORDER, [])
        settings.user.overview.Set(stateSetting.SETTING_FLAG_ORDER_CONFIG_NAME, flagOrder)
        settings.user.overview.Set(stateSetting.SETTING_BACKGROUND_ORDER_CONFIG_NAME, backgroundOrder)
        flagStates = data.get(sharingConst.OVERVIEW_SHARING_FLAG_STATES, [])
        flagStates.sort()
        backgroundStates = data.get(sharingConst.OVERVIEW_SHARING_BG_STATES, [])
        backgroundStates.sort()
        settings.user.overview.Set(stateSetting.SETTING_FLAG_STATES_CONFIG_NAME, flagStates)
        settings.user.overview.Set(stateSetting.SETTING_BACKGROUND_STATES_CONFIG_NAME, backgroundStates)
        columnOrder = data.get(sharingConst.OVERVIEW_SHARING_COLUMN_ORDER, overviewConst.ALL_COLUMNS)
        overviewColumns = data.get(sharingConst.OVERVIEW_SHARING_OVERVIEW_COLUMNS, overviewConst.DEFAULT_COLUMNS[:])
        overviewColumns.sort()
        settings.user.overview.Set(oConst.SETTING_COLUMN_ORDER, columnOrder)
        settings.user.overview.Set(oConst.SETTING_COLUMNS, overviewColumns)
        colorNameDictAsList = data.get(sharingConst.OVERVIEW_SHARING_STATE_COLORS_LIST, [])
        try:
            colorNameDict = GetDictFromList(colorNameDictAsList)
            newColorDict = self.GetColorValuesFromName(colorNameDict)
            settings.user.overview.Set(oConst.SETTING_STATE_COLORS, newColorDict)
        except Exception as exc:
            log.warning('Omit loading Overview data for colors: %s. \nData: %s' % (exc, colorNameDictAsList))

        stateBlinksAsList = data.get(sharingConst.OVERVIEW_SHARING_STATE_BLINKS, [])
        try:
            stateBlinks = GetDictFromList(stateBlinksAsList)
            stateBlinks = DecodeKeyInDict(stateBlinks)
            settings.user.overview.Set(oConst.SETTING_STATE_BLINKS, stateBlinks)
        except Exception as exc:
            log.warning('Omit loading Overview data for state blinks: %s. \nData: %s' % (exc, stateBlinksAsList))

        shipLabelsAsList = data.get(sharingConst.OVERVIEW_SHARING_SHIP_LABELS, [])
        try:
            shipLabels = GetDictFromList(shipLabelsAsList)
            shipLabels = ReplaceInnerListsWithDicts(shipLabels)
            shipLabelOrder = data.get(sharingConst.OVERVIEW_SHARING_SHIP_LABEL_ORDER, [])
            orderedShipLabelsList = GetOrderedListFromDict(shipLabels, shipLabelOrder, allowedDuplicates=(LABEL_TYPE_LINEBREAK,))
            settings.user.overview.Set(oConst.SETTINGS_SHIP_LABELS, orderedShipLabelsList)
        except Exception as exc:
            log.warning('Omit loading Overview data for ship labels: %s. \nData: %s' % (exc, shipLabelsAsList))

    def LoadGeneralSettings(self, data):
        self._LoadGeneralSettings(data)
        sm.GetService('stateSvc').InitColors(reset=True)
        sm.GetService('stateSvc').shipLabels = None

    def GetTabSetupToLoad(self, data):
        tabSetup = GetDictFromList(data.get(sharingConst.OVERVIEW_SHARING_TAB_SETUP, []))
        tabSetup = ReplaceInnerListsWithDicts(tabSetup)
        return tabSetup

    def UpdateAllPresets(self, profileUpdateDict):
        self.allPresets.update(profileUpdateDict)
        self._PersistPresets()

    def GetColorsToSave(self, colorDict):
        newColorDict = {}
        for key, colorValue in colorDict.iteritems():
            colorName = FindColorName(colorValue)
            if colorName:
                newColorDict[key] = colorName

        newColorDict = EncodeKeyInDict(newColorDict)
        return newColorDict

    def GetColorValuesFromName(self, colorDict):
        newColorDict = {}
        for key, colorName in colorDict.iteritems():
            colorInfo = GetStateColors().get(colorName, None)
            if colorInfo:
                newColorDict[key] = colorInfo[0]

        newColorDict = DecodeKeyInDict(newColorDict)
        return newColorDict

    def GetTabSettingsForSaving(self):
        tabSettings = self.GetSettingsByTabID()
        tabSettingsAsList = []
        for idx, tSettingValue in tabSettings.items():
            for setupGroupName in (SETTING_OVERVIEW_PRESET_NAME, SETTING_BRACKET_PRESET_NAME):
                if self.IsUnsavedPreset(tSettingValue.get(setupGroupName, None)):
                    tSettingValue[setupGroupName] = self._ExtractPresetNameFromTuple(tSettingValue[setupGroupName])

            tSettingList = GetDeterministicListFromDict(tSettingValue)
            tabSettingsAsList.append((idx, tSettingList))

        tabSettingsAsList.sort()
        tabSettingsAsList = tabSettingsAsList[:MAX_TAB_NUM]
        return tabSettingsAsList

    def GetWindowInstanceIDs(self):
        return range(len(self.GetTabIDsByWindowInstanceID()))

    def GetDefaultWindowInstanceID(self):
        return self.GetWindowInstanceIDs()[0]

    def GetWindowIDs(self):
        return [ self.GetWindowID(wndInstID) for wndInstID in self.GetWindowInstanceIDs() ]

    def GetWindowID(self, windowInstanceID):
        windowID = overviewConst.WINDOW_ID
        if windowInstanceID > 0:
            windowID += '_%s' % windowInstanceID
        return windowID

    def GetTabIDsByWindowInstanceID(self):
        return settings.user.overview.Get(oConst.SETTING_TABS_BY_WINDOW_INSTANCE_ID, self._GetDefaultTabIDsByWindowInstanceID())

    def _IsTabsByWndInstIDDataValid(self, tabIDsByWndInstID):
        settingsByTabID = self.GetSettingsByTabID()
        if sum([ len(tabIDs) for tabIDs in tabIDsByWndInstID ]) != len(settingsByTabID):
            log.warning("Number of tabs don't match, so resetting to default. tabIdsByWndInstID=%s, settingsByTabID=%s" % (tabIDsByWndInstID, settingsByTabID))
            return False
        return True

    def GetWindowInstanceID(self, tabID):
        for wndInstID, tabIDs in enumerate(self.GetTabIDsByWindowInstanceID()):
            if tabID in tabIDs:
                return wndInstID

    def _GetDefaultTabIDsByWindowInstanceID(self):
        return [self.GetSettingsByTabID().keys()]

    def GetTabIDs(self, windowInstanceID):
        tabIDsByWndInstID = self.GetTabIDsByWindowInstanceID()
        if windowInstanceID >= len(tabIDsByWndInstID):
            return None
        tabIDs = tabIDsByWndInstID[windowInstanceID]
        return sorted(tabIDs)

    def PersistTabIDsByWindowInstanceID(self, tabIDsByWndInstID):
        if not self._IsTabsByWndInstIDDataValid(tabIDsByWndInstID):
            tabIDsByWndInstID = self._GetDefaultTabIDsByWindowInstanceID()
        return settings.user.overview.Set(oConst.SETTING_TABS_BY_WINDOW_INSTANCE_ID, tabIDsByWndInstID)

    def GetSettingsByTabID(self):
        settingsByTabID = settings.user.overview.Get(oConst.SETTING_TAB_SETTINGS, None)
        if settingsByTabID is None:
            settingsByTabID = settings.user.overview.Get(oConst.SETTING_TAB_SETTINGS_OLD, self._GetDefaultSettingsByTabID())
            self._ConvertOldFormatSettingsByTabID(settingsByTabID)
            self.PersistSettingsByTabID(settingsByTabID)
        return settingsByTabID

    def _ConvertOldFormatSettingsByTabID(self, settingsByTabID):
        for tabID, _settings in settingsByTabID.iteritems():
            if SETTING_OVERVIEW_PRESET_NAME in _settings:
                presetName = _settings[SETTING_OVERVIEW_PRESET_NAME]
                if self.IsTuplePresetName(presetName):
                    _settings[SETTING_OVERVIEW_PRESET_NAME] = self._ExtractPresetNameFromTuple(presetName)
            if SETTING_BRACKET_PRESET_NAME in _settings:
                bracketPresetName = _settings[SETTING_BRACKET_PRESET_NAME]
                if self.IsTuplePresetName(bracketPresetName):
                    _settings[SETTING_BRACKET_PRESET_NAME] = self._ExtractPresetNameFromTuple(bracketPresetName)

    def GetTabSettings(self, tabID):
        return self.GetSettingsByTabID().get(tabID, None)

    def GetTabName(self, tabID):
        return self.GetTabSettings(tabID)[oConst.SETTING_TAB_NAME]

    def PersistSettingsByTabID(self, settingsByTabID):
        if not settingsByTabID:
            log.exception('Attempting to persist empty settingsByTabID')
            return
        self._ConvertOldFormatSettingsByTabID(settingsByTabID)
        settings.user.overview.Set(oConst.SETTING_TAB_SETTINGS, settingsByTabID)

    def GetOverviewName(self):
        currentText = settings.user.ui.Get('overviewProfileName', None)
        if not currentText:
            currentText = localization.GetByLabel('UI/Overview/DefaultOverviewName', charID=session.charid)
        return currentText

    def GetShareData(self, text, presetsToUse = None):
        data = self.GetOverviewDataForSave(presetsToUse=presetsToUse)
        overviewPreset = utillib.KeyVal(__guid__='fakeentry.OverviewProfile', data=data, label=text)
        return [overviewPreset]

    def UpdateSettingsByTabID(self, settingsByTabID, overviewID = None):
        if settingsByTabID is None:
            settingsByTabID = self.GetSettingsByTabID() or self._GetDefaultSettingsByTabID()
        self.PersistSettingsByTabID(deepcopy(settingsByTabID))
        self.defaultOverviewSettings.set_overview(overviewID)
        sm.ScatterEvent('OnOverviewPresetsChanged')

    def ImportOverviewSettings(self, settingsByTabID):
        self.UpdateSettingsByTabID(settingsByTabID)
        self._AddMissingPresetsFromOtherDefaultOverviews()

    def _GetDefaultSettingsByTabID(self):
        settingsByTabID = {}
        defaultTabs = self.defaultOverviews.get_tabs()
        for tabID, tab in defaultTabs.iteritems():
            settingsByTabID[tabID] = {SETTING_OVERVIEW_PRESET_NAME: tab.overview_preset,
             SETTING_BRACKET_PRESET_NAME: tab.bracket_preset,
             SETTING_TAB_NAME: tab.name,
             SETTING_TAB_COLOR: tab.color}

        return settingsByTabID

    def GetSettingValueBroadcastToTop(self):
        return self.GetSettingValueOrDefaultFromName(oConst.SETTING_BROADCAST_TO_TOP, DEFAULT_BROADCAST_TO_TOP)

    def AddTab(self, name, overviewPreset = None, bracketPreset = None, windowInstanceID = None, color = None):
        bannedwords.check_words_allowed(name)
        settingsByTabID = self.GetSettingsByTabID()
        if len(settingsByTabID) >= MAX_TAB_NUM:
            eve.Message('TooManyTabs', {'numTabs': MAX_TAB_NUM})
            return
        tabID = self._AppendTab(name, settingsByTabID, overviewPreset, bracketPreset, color)
        self.UpdateSettingsByTabID(settingsByTabID)
        self._AssignTabToWindow(tabID, windowInstanceID)
        sm.ScatterEvent('OnOverviewTabsChanged')

    def UpdateTab(self, tabID, name, presetName, bracketPresetName, color):
        settingsByTabID = self.GetSettingsByTabID()
        if tabID not in settingsByTabID:
            log.exception('Trying to edit missing tab (tabID=%s' % tabID)
            return
        settings = settingsByTabID[tabID]
        if name is not None:
            settings[SETTING_TAB_NAME] = name
        if presetName is not None:
            settings[SETTING_OVERVIEW_PRESET_NAME] = presetName
        if bracketPresetName is not None:
            settings[SETTING_BRACKET_PRESET_NAME] = bracketPresetName
        settings[SETTING_TAB_COLOR] = color
        self.PersistSettingsByTabID(settingsByTabID)
        sm.ScatterEvent('OnOverviewTabsChanged')

    def GetTabPreset(self, tabID):
        tabSettings = self.GetTabSettings(tabID)
        if tabSettings:
            return tabSettings[SETTING_OVERVIEW_PRESET_NAME]

    def SetTabPreset(self, tabID, presetName):
        self._SetTabSetting(tabID, SETTING_OVERVIEW_PRESET_NAME, presetName)

    def GetTabBracketPreset(self, tabID):
        tabSettings = self.GetTabSettings(tabID)
        if tabSettings:
            return tabSettings[SETTING_BRACKET_PRESET_NAME] or oConst.BRACKET_FILTER_SHOWALL

    def SetTabBracketPreset(self, tabID, presetName):
        self._SetTabSetting(tabID, SETTING_BRACKET_PRESET_NAME, presetName)

    def GetTabVisibleColumnIDs(self, tabID):
        tabSettings = self.GetTabSettings(tabID)
        if tabSettings:
            defaultColumnIDs = settings.user.overview.Get(oConst.SETTING_COLUMNS, overviewConst.DEFAULT_COLUMNS)
            return tabSettings.get(oConst.SETTING_TAB_VISIBLE_COLUMN_IDS, defaultColumnIDs)[:]

    def SetTabVisibleColumnIDs(self, tabID, columnIDs):
        self._SetTabSetting(tabID, oConst.SETTING_TAB_VISIBLE_COLUMN_IDS, columnIDs)
        overviewSignals.on_tab_columns_changed(tabID)

    def ResetTabVisibleColumnIDs(self, tabID):
        self.SetTabVisibleColumnIDs(tabID, overviewConst.DEFAULT_COLUMNS[:])

    def GetTabColumnOrder(self, tabID):
        tabSettings = self.GetTabSettings(tabID)
        if tabSettings:
            return tabSettings.get(oConst.SETTING_TAB_COLUMN_ORDER, overviewConst.ALL_COLUMNS[:])

    def SetTabColumnOrder(self, tabID, columnIDs):
        self._SetTabSetting(tabID, oConst.SETTING_TAB_COLUMN_ORDER, columnIDs)
        overviewSignals.on_tab_columns_changed(tabID)

    def ResetTabColumnOrder(self, tabID):
        self.SetTabColumnOrder(tabID, overviewConst.ALL_COLUMNS[:])

    def ToggleTabColumnVisibility(self, tabID, columnID):
        columnIDs = self.GetTabVisibleColumnIDs(tabID)
        if columnID in columnIDs:
            columnIDs.remove(columnID)
        else:
            columnIDs.append(columnID)
        self.SetTabVisibleColumnIDs(tabID, columnIDs)

    def SetTabName(self, tabID, tabName):
        self._SetTabSetting(tabID, SETTING_TAB_NAME, tabName)

    def _SetTabSetting(self, tabID, settingID, value):
        settingsByTabID = self.GetSettingsByTabID()
        if tabID not in settingsByTabID:
            log.exception('Trying to edit missing tab (tabID=%s' % tabID)
            return
        settingsByTabID[tabID][settingID] = value
        self.PersistSettingsByTabID(settingsByTabID)
        sm.ScatterEvent('OnOverviewTabsChanged')

    def _AppendTab(self, name, settingsByTabID, overviewPreset = None, bracketPreset = None, color = None):
        if len(settingsByTabID) == 0:
            tabID = 0
        else:
            tabID = max(settingsByTabID.keys()) + 1
        settingsByTabID[tabID] = {SETTING_TAB_NAME: name,
         SETTING_OVERVIEW_PRESET_NAME: overviewPreset or self.defaultPreset,
         SETTING_BRACKET_PRESET_NAME: bracketPreset,
         SETTING_TAB_COLOR: color}
        return tabID

    def DeleteTab(self, tabID):
        oldSettings = self.GetSettingsByTabID()
        if tabID not in oldSettings:
            return
        settingsByTabID = {}
        _tabID = 0
        for key, dictItem in oldSettings.iteritems():
            if key == tabID:
                continue
            settingsByTabID[_tabID] = dictItem
            _tabID += 1

        self.UpdateSettingsByTabID(settingsByTabID)
        self._RemoveTabFromWindow(tabID)
        sm.ScatterEvent('OnOverviewTabsChanged')

    def _RemoveTabFromWindow(self, tabID):
        tabIDsByWndInstID = self.GetTabIDsByWindowInstanceID()
        self._RemoveTabID(tabID, tabIDsByWndInstID)
        self._RemoveEmptyTabIDs(tabIDsByWndInstID)
        self._UpdateTabIDsAfterTabRemoval(tabID, tabIDsByWndInstID)
        self.PersistTabIDsByWindowInstanceID(tabIDsByWndInstID)

    def _UpdateTabIDsAfterTabRemoval(self, tabID, tabIDsByWndInstID):
        for tabIDs in tabIDsByWndInstID:
            for i, _tabID in enumerate(tabIDs):
                if _tabID > tabID:
                    tabIDs[i] -= 1

    def _RemoveTabID(self, tabID, tabIDsByWndInstID):
        for tabIDs in tabIDsByWndInstID:
            if tabID in tabIDs:
                tabIDs.remove(tabID)

    def _RemoveEmptyTabIDs(self, tabIDsByWndInstID):
        if [] in tabIDsByWndInstID:
            tabIDsByWndInstID.remove([])

    def MoveTab(self, tabID, windowInstanceID = None):
        self._AssignTabToWindow(tabID, windowInstanceID)
        sm.ScatterEvent('OnOverviewTabsChanged')

    def _AssignTabToWindow(self, tabID, windowInstanceID = None):
        tabIDsByWndInstID = self.GetTabIDsByWindowInstanceID()
        self._RemoveTabID(tabID, tabIDsByWndInstID)
        if windowInstanceID is None:
            tabIDsByWndInstID.append([tabID])
        else:
            tabIDsByWndInstID[windowInstanceID].append(tabID)
        self._RemoveEmptyTabIDs(tabIDsByWndInstID)
        self.PersistTabIDsByWindowInstanceID(tabIDsByWndInstID)
