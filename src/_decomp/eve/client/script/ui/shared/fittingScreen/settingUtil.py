#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\settingUtil.py
from eve.client.script.ui.shared.fittingScreen import FITTING_FILTER_SHIP_PREFIX, BTN_TYPE_PERSONAL_FITTINGS, BTN_TYPE_CORP_FITTINGS, BTN_TYPE_CURRENT_SHIP, FITTING_FILTER_HW_PREFIX, BTN_TYPE_LOSLOT, BTN_TYPE_MEDSLOT, BTN_TYPE_HISLOT, BTN_TYPE_RIGSLOT, BTN_TYPE_DRONES, BTN_TYPE_SHIP, BTN_TYPE_RESOURCES, BTN_TYPE_SKILLS, HW_BTN_ID_CONFIG, BROWSE_MODULES, BROWSE_CHARGES, BROWSER_BTN_ID_CONFIG, BROWSE_FITTINGS, BROWSE_HARDWARE, AMMO_FAVORITE_CONFIG, BTN_TYPE_COMMUNITY_FITTINGS, RESOURCE_FITTING_MODE_CONFIG, BTN_TYPE_FITTING_SKILLS, FILTER_DEFAULT_COMMUNITY_FITTING, FTTING_PANEL_SETTING_LEFT_DEFAULT, FTTING_PANEL_SETTING_LEFT, FTTING_PANEL_SETTING_RIGHT, TAB_CONFIGNAME_STATS, BROWSER_SEARCH_MODULES, CHARGE_FILTER_SETTING, TAB_CONFIGNAME_INVENTORY, TAB_CONFIGNAME_BROWSER, BTN_TYPE_ALLIANCE_FITTINGS
FILTER_TYPE_DEFAULT = 'browser'

class HardwareFiltersSettingObject(object):

    def __init__(self, filterType = FILTER_TYPE_DEFAULT):
        if filterType != FILTER_TYPE_DEFAULT:
            self.extraPrefix = filterType
        else:
            self.extraPrefix = ''
        self.filterType = filterType
        self.hwPrefix = self.GetHwPrefix()

    def GetHwLoSlotsSetting(self):
        return _GetHwSetting(BTN_TYPE_LOSLOT, prefix=self.hwPrefix)

    def GetHwMedSlotSetting(self):
        return _GetHwSetting(BTN_TYPE_MEDSLOT, prefix=self.hwPrefix)

    def GetHwHiSlotSetting(self):
        return _GetHwSetting(BTN_TYPE_HISLOT, prefix=self.hwPrefix)

    def GetHwRigSlotsSetting(self):
        return _GetHwSetting(BTN_TYPE_RIGSLOT, prefix=self.hwPrefix)

    def GetHwDronesSetting(self):
        return _GetHwSetting(BTN_TYPE_DRONES, prefix=self.hwPrefix)

    def GetHwShipCanUseSetting(self):
        return _GetHwSetting(BTN_TYPE_SHIP, defaultValue=True, prefix=self.hwPrefix)

    def GetHwResourcesSetting(self):
        return _GetHwSetting(BTN_TYPE_RESOURCES, prefix=self.hwPrefix)

    def GetHwSkillsSetting(self):
        return _GetHwSetting(BTN_TYPE_SKILLS, prefix=self.hwPrefix)

    def GetHwResourcesSettingResourcesLeftActive(self):
        return self.GetHwResourcesSetting() and not self.GetFilterModeForResource()

    def GetFilterModeForResource(self):
        resourceConfig = self.GetSettingNameWithExtraPerfix(RESOURCE_FITTING_MODE_CONFIG)
        return settings.user.ui.Get(resourceConfig, True)

    def SetFilterModeForResource(self, value):
        resourceConfig = self.GetSettingNameWithExtraPerfix(RESOURCE_FITTING_MODE_CONFIG)
        return settings.user.ui.Set(resourceConfig, value)

    def GetTextFilter(self):
        settingName = self.GetSettingNameWithExtraPerfix(BROWSER_SEARCH_MODULES)
        return settings.user.ui.Get(settingName, '').lower()

    def SetTextFiltering(self, text):
        settingName = self.GetSettingNameWithExtraPerfix(BROWSER_SEARCH_MODULES)
        return settings.user.ui.Set(settingName, text)

    def GetHwPrefix(self):
        prefix = FITTING_FILTER_HW_PREFIX
        if self.extraPrefix:
            prefix = prefix % self.extraPrefix
            prefix += '_%s'
        return prefix

    def GetSettingNameWithExtraPerfix(self, settingName):
        if self.extraPrefix:
            settingName += '_%s' % self.extraPrefix
        return settingName

    def GetChargeSettingName(self):
        return self.GetSettingNameWithExtraPerfix(CHARGE_FILTER_SETTING)

    def GetFilterType(self):
        return self.filterType


def GetPersonalFittingSetting():
    return settings.user.ui.Get(FITTING_FILTER_SHIP_PREFIX % BTN_TYPE_PERSONAL_FITTINGS, False)


def GetCorpFittingSetting():
    return settings.user.ui.Get(FITTING_FILTER_SHIP_PREFIX % BTN_TYPE_CORP_FITTINGS, False)


def GetAllianceFittingSetting():
    if not session.allianceid:
        return False
    return settings.user.ui.Get(FITTING_FILTER_SHIP_PREFIX % BTN_TYPE_ALLIANCE_FITTINGS, False)


def GetCommunityFittingSetting():
    return settings.user.ui.Get(FITTING_FILTER_SHIP_PREFIX % BTN_TYPE_COMMUNITY_FITTINGS, FILTER_DEFAULT_COMMUNITY_FITTING)


def GetOnlyCurrentShipSetting():
    return settings.user.ui.Get(FITTING_FILTER_SHIP_PREFIX % BTN_TYPE_CURRENT_SHIP, False)


def GetOnlyFittingsWithSkillsSetting():
    return settings.user.ui.Get(FITTING_FILTER_SHIP_PREFIX % BTN_TYPE_FITTING_SKILLS, False)


def _GetHwSetting(settingType, defaultValue = False, prefix = FITTING_FILTER_HW_PREFIX):
    return settings.user.ui.Get(prefix % settingType, defaultValue)


def IsChargeTabSelected():
    return GetHwTabSelected() == BROWSE_CHARGES


def IsModuleTabSelected():
    return GetHwTabSelected() == BROWSE_MODULES


def GetHwTabSelected():
    return settings.user.ui.Get(HW_BTN_ID_CONFIG, BROWSE_MODULES)


def IsFittingAndHullsSelected():
    return GetBrowserBtnSelected() == BROWSE_FITTINGS


def IsHardwareTabSelected():
    return GetBrowserBtnSelected() == BROWSE_HARDWARE


def GetBrowserBtnSelected():
    return settings.user.ui.Get(BROWSER_BTN_ID_CONFIG, BROWSE_FITTINGS)


def GetAllAmmoFavorites():
    return settings.user.ui.Get(AMMO_FAVORITE_CONFIG, set())


def GetCurrentLeftPanelKey():
    return settings.user.ui.Get(FTTING_PANEL_SETTING_LEFT, FTTING_PANEL_SETTING_LEFT_DEFAULT)


def SetCurrentLeftPanelKey(value):
    return settings.user.ui.Set(FTTING_PANEL_SETTING_LEFT, value)


def GetCurrentRightPanelKey():
    return settings.user.ui.Get(FTTING_PANEL_SETTING_RIGHT, TAB_CONFIGNAME_STATS)


def SetCurrentRightPanelKey(value):
    return settings.user.ui.Set(FTTING_PANEL_SETTING_RIGHT, value)


def IsInventorySelected():
    currentlySelected = GetCurrentLeftPanelKey()
    return currentlySelected == TAB_CONFIGNAME_INVENTORY


def IsBrowserSelected():
    currentlySelected = GetCurrentLeftPanelKey()
    return currentlySelected == TAB_CONFIGNAME_BROWSER
