#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\controllers\filterContController.py
from carbonui.services.setting import CharSettingNumeric, CharSettingEnum
from eve.client.script.ui.control.filter import FilterController
from eve.client.script.ui.station.stationServiceConst import serviceIDAlwaysPresent
from eve.client.script.ui.structure.structureBrowser.filterContUtil import GetLocationOptions, GetStructureOptions, GetServiceOptions
from localization import GetByLabel, GetByMessageID
from signals import Signal
import eve.client.script.ui.structure.structureBrowser.browserUIConst as browserUIConst
from eve.client.script.ui.station import stationServiceConst
import structures
from inventorycommon.const import minRegion, maxRegion
from sovereignty.client import get_sov_region_ids
from caching import Memoize
from marketutil.const import rangeSolarSystem
from orbitalSkyhook.const import STATE_LABELS

class FilterContController(object):

    def __init__(self, configName = None):
        configName = configName or 'structurebrowser_filterContController'
        self.currentTextFilter = ''
        self.on_text_filter_changed = Signal(signalName='on_text_filter_changed')
        self.on_structure_type_changed = Signal(signalName='on_structure_type_changed')
        self.structureTypeFilterController = FilterController('%s_structureTypes' % configName, [], doSortChildren=False)
        self.serviceFilterController = FilterController('%s_services' % configName, [], doSortChildren=True)

    def GetTextFilter(self):
        return self.currentTextFilter

    def TextFilterChanged(self, filterText):
        self.currentTextFilter = filterText
        self.on_text_filter_changed()

    def GetServicesChecked(self):
        optionsChecked = self.serviceFilterController.GetSelectedOptions()
        return {y for x, y in optionsChecked}

    def AreServiceFiltersDisbled(self):
        return not self.serviceFilterController.IsActive()

    def GetStructureTypesChecked(self):
        checkedOptions = self.structureTypeFilterController.GetSelectedOptions()
        checkedOptions = {z for x, y in checkedOptions for z in y}
        return checkedOptions

    def _GetSortedServiceOption(self):
        return []

    def GetStructureOptions(self):
        return []

    def GetServiceOptions(self):
        sortedOptions = self._GetSortedServiceOption()
        return GetServiceOptions(sortedOptions)


class FilterContControllerAllStructures(FilterContController):

    def __init__(self):
        configName = 'structurebrowser_allStructures_filterContController'
        FilterContController.__init__(self, configName)
        self.rangeSelected = settings.char.ui.Get(browserUIConst.UI_SETTING_STRUCTUREBROWSER_FILTERS % 'location', rangeSolarSystem)
        self.structureOwnerValue = 0
        self.on_change_location_range = Signal(signalName='on_change_location_range')
        self.on_change_owner_value = Signal(signalName='on_change_owner_value')

    def GetRange(self):
        locationOptions = GetLocationOptions()
        if self.rangeSelected not in locationOptions:
            self.rangeSelected = locationOptions[0]
        return self.rangeSelected

    def ChangeLocationRange(self, value):
        settingName = browserUIConst.UI_SETTING_STRUCTUREBROWSER_FILTERS % 'location'
        settings.char.ui.Set(settingName, value)
        self.rangeSelected = value
        self.on_change_location_range(value)

    def GetStructureOwnerValue(self):
        return self.structureOwnerValue

    def ChangeStructureOwnerFilter(self, value):
        self.structureOwnerValue = value
        self.on_change_owner_value(value)

    def _GetSortedServiceOption(self):
        servicesToSkip = [structures.SERVICE_CYNO_JAMMER]
        serviceDataList = [ x for x in stationServiceConst.serviceData if x.serviceID not in servicesToSkip ]
        serviceData = sorted(serviceDataList, key=lambda x: x.label)
        return serviceData

    def GetStructureOptions(self):
        return GetStructureOptions()


class FilterContControllerMyStructures(FilterContController):

    def __init__(self):
        configName = 'structurebrowser_myStructures_filterContController'
        self.filterLowerPower = settings.char.ui.Get(browserUIConst.UI_SETTING_STRUCTUREBROWSER_FILTERS % 'lowPower', False)
        self.on_lower_power_filter_changed = Signal(signalName='on_lower_power_filter_changed')
        FilterContController.__init__(self, configName)

    def OnlyShowLowPower(self):
        return bool(self.filterLowerPower)

    def ChangeLowPower(self, value):
        settings.char.ui.Set(browserUIConst.UI_SETTING_STRUCTUREBROWSER_FILTERS % 'lowPower', value)
        self.filterLowerPower = value
        self.on_lower_power_filter_changed()

    def _GetSortedServiceOption(self):
        npcServices = (serviceIDAlwaysPresent,
         structures.SERVICE_SECURITY_OFFICE,
         structures.SERVICE_LOYALTY_STORE,
         structures.SERVICE_FACTION_WARFARE,
         structures.SERVICE_FITTING,
         structures.SERVICE_INSURANCE,
         structures.SERVICE_REPAIR)
        serviceData = stationServiceConst.serviceData
        serviceData = (x for x in serviceData if x.serviceID not in npcServices)
        serviceData = sorted(serviceData, key=lambda x: x.label)
        return serviceData

    def GetStructureOptions(self):
        return GetStructureOptions(False)


class FilterContControllerSkyhook(object):

    def __init__(self):
        self.currentTextFilter = ''
        self.on_filters_changed = Signal(signalName='on_filters_changed')
        self._selectedLocationSetting = CharSettingEnum(browserUIConst.UI_SETTING_SKYHOOKBROWSER_FILTERS % 'location', None, [ x[1] for x in self.GetLocationOptions() ])
        self._selectedRegionSetting = CharSettingEnum(browserUIConst.UI_SETTING_SKYHOOKBROWSER_FILTERS % 'region', None, [ x[1] for x in self.GetRegionOptions() ])
        self._selectedStateSetting = CharSettingEnum(browserUIConst.UI_SETTING_SKYHOOKBROWSER_FILTERS % 'state', None, [ x[1] for x in self.GetStateOptions() ])
        self._selectedTheftVulnerabilitySetting = CharSettingEnum(browserUIConst.UI_SETTING_SKYHOOKBROWSER_FILTERS % 'theftvulnerability', None, [ x[1] for x in self.GetTheftVulnerabilityOptions() ])

    def GetTextFilter(self):
        return self.currentTextFilter

    def TextFilterChanged(self, filterText):
        if filterText == self.currentTextFilter:
            return
        self.currentTextFilter = filterText
        self.on_filters_changed()

    def GetSelectedLocationOption(self):
        locationOption = self._selectedLocationSetting.get()
        if locationOption not in self._selectedLocationSetting.options:
            locationOption = self._selectedLocationSetting.options[0]
        return locationOption

    def SetSelectedLocationOption(self, value):
        if value == self._selectedLocationSetting.get():
            return
        if value not in self._selectedLocationSetting.options:
            value = self._selectedLocationSetting.options[-1]
        self._selectedLocationSetting.set(value)
        self.on_filters_changed()

    @Memoize
    def GetLocationOptions(self):
        return [(GetByLabel('UI/Agency/ContentOfAnyDistance'), None),
         (GetByLabel('UI/Generic/CurrentSystem'), 1),
         (GetByLabel('UI/Common/WithinJumps', numJumps=2), 2),
         (GetByLabel('UI/Common/WithinJumps', numJumps=5), 5),
         (GetByLabel('UI/Common/WithinJumps', numJumps=10), 10),
         (GetByLabel('UI/Common/LocationTypes/Region'), -1)]

    def GetSelectedRegionOption(self):
        regionID = self._selectedRegionSetting.get()
        if regionID in get_sov_region_ids():
            return regionID
        return session.regionid

    def SetSelectedRegionOption(self, value):
        if value == self._selectedRegionSetting.get():
            return
        if value not in get_sov_region_ids():
            value = None
        self._selectedRegionSetting.set(value)
        self.on_filters_changed()

    @Memoize
    def GetRegionOptions(self):
        return [(GetByLabel('UI/Generic/CurrentRegion'), None)] + sorted([ (GetByMessageID(cfg.mapRegionCache.Get(regionID).nameID), regionID) for regionID in get_sov_region_ids() ])

    def GetSelectedStateOption(self):
        locationOption = self._selectedStateSetting.get()
        if locationOption not in self._selectedStateSetting.options:
            locationOption = self._selectedStateSetting.options[0]
        return locationOption

    def SetSelectedStateOption(self, value):
        if value == self._selectedStateSetting.get():
            return
        if value not in self._selectedStateSetting.options:
            value = None
        self._selectedStateSetting.set(value)
        self.on_filters_changed()

    @Memoize
    def GetStateOptions(self):
        return [(GetByLabel('UI/StructureBrowser/SkyhookState'), None), (GetByLabel('UI/Structures/States/Reinforced'), 'reinforced'), (GetByLabel('UI/Structures/States/Vulnerable'), 'vulnerable')]

    def GetSelectedTheftVulnerabilityOption(self):
        locationOption = self._selectedTheftVulnerabilitySetting.get()
        if locationOption not in self._selectedTheftVulnerabilitySetting.options:
            locationOption = self._selectedTheftVulnerabilitySetting.options[0]
        return locationOption

    def SetSelectedTheftVulnerabilityOption(self, value):
        if value == self._selectedTheftVulnerabilitySetting.get():
            return
        if value not in self._selectedTheftVulnerabilitySetting.options:
            value = None
        self._selectedTheftVulnerabilitySetting.set(value)
        self.on_filters_changed()

    @Memoize
    def GetTheftVulnerabilityOptions(self):
        return [(GetByLabel('UI/StructureBrowser/SkyhookTheftVulnerability'), None), (GetByLabel('UI/OrbitalSkyhook/TheftStates/Secure'), 'secure'), (GetByLabel('UI/OrbitalSkyhook/TheftStates/Vulnerable'), 'vulnerable')]
