#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\filters\colonyResourcesAgencyFiltersCont.py
import log
import gametime
import uthread2
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.primitives.container import Container
from carbonui.control.combo import Combo
from carbonui.control.radioButton import RadioButton
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.agencyNew.ui.filters.baseFiltersCont import BaseFiltersCont
from eve.client.script.ui.shared.agencyNew import agencyFilters, agencyConst
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.ui.controls.filterCombo import FilterCombo
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from localization import GetByLabel
from sovereignty.client import get_sov_region_ids
from orbitalSkyhook.resourceRichness import richnessLabelPaths, RICHNESS_MODEST, RICHNESS_AVG, RICHNESS_ABUNDANT

def trim_numeric_label(label, max_length):
    extra_tooltip = None
    new_label = None
    if len(label) > max_length:
        chunks = label.split(' ')
        if len(chunks) == 1:
            return (label, extra_tooltip)
        take_chunks = len(chunks) - 1
        extra_tooltip = label
        new_label = ' '.join(chunks[:take_chunks])
        return (new_label, extra_tooltip)
    return (label, extra_tooltip)


class ColonyResourceAgencyFiltersCont(BaseFiltersCont):
    default_name = 'ColonyResourceAgencyCont'
    contentGroupID = contentGroupConst.contentGroupColonyResourcesAgency
    constellationCombo = None

    def __init__(self, *args, **kwargs):
        super(ColonyResourceAgencyFiltersCont, self).__init__(*args, **kwargs)
        self.per_system_planet_value = agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_PER_SYSTEM_PLANET)
        self.last_filter_edit_time = None

    def ConstructPerSystemPlanetFilter(self):
        per_system_planet_label = GetByLabel('UI/Agency/ColonyResourcesAgency/FilterColonyResources')
        per_system_planet_container = Container(name='perSystemPlanetContainer', parent=self.filtersCont, align=uiconst.TOTOP, height=50)
        per_system_planet_label = Label(name='perSystemPlanetLabel', parent=per_system_planet_container, text=GetByLabel('UI/Agency/ColonyResourcesAgency/FilterColonyResources'), align=uiconst.TOTOP, padBottom=5)
        selected_per_system_planet_filter = agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_PER_SYSTEM_PLANET)
        radio_button_container = Container(name='perSystemPlanetRadioButtonContainer', parent=per_system_planet_container, align=uiconst.TOTOP, height=30)
        self.per_system_radio_button = RadioButton(parent=radio_button_container, align=uiconst.TOLEFT, text=agencyConst.OPTION_PER_SYSTEM, checked=selected_per_system_planet_filter == agencyConst.OPTION_PER_SYSTEM_VALUE, retval=agencyConst.OPTION_PER_SYSTEM_VALUE, callback=self.OnPerSystemPlanetChanged, padRight=10, width=40, hint=agencyConst.OPTION_PER_SYSTEM_HINT)
        self.per_planet_radio_button = RadioButton(parent=radio_button_container, align=uiconst.TOLEFT, text=agencyConst.OPTION_PER_PLANET, checked=selected_per_system_planet_filter == agencyConst.OPTION_PER_PLANET_VALUE, retval=agencyConst.OPTION_PER_PLANET_VALUE, callback=self.OnPerSystemPlanetChanged, width=40, hint=agencyConst.OPTION_PER_PLANET_HINT)

    def ConstructPowerOutput(self):
        label, extra_tooltip = trim_numeric_label(GetByLabel('UI/Agency/ColonyResourcesAgency/PowerOutput'), 26)
        power_output_container = Container(name='powerOutputContainer', parent=self.filtersCont, align=uiconst.TOTOP, height=40, padBottom=5)
        power_output_label = Label(name='powerOutputLabel', parent=power_output_container, align=uiconst.CENTERLEFT, text=label)
        if extra_tooltip:
            more_info = MoreInfoIcon(parent=power_output_container, pos=(power_output_label.width + 4,
             0,
             16,
             16), align=uiconst.CENTERLEFT)
            more_info.hint = extra_tooltip
        self.power_output_control = SingleLineEditInteger(name='powerOutputControl', parent=power_output_container, align=uiconst.CENTERRIGHT, width=80, setvalue=self._GetPowerOutput(), OnChange=self.OnPowerOutputChanged, datatype=int)

    def ConstructWorkforceOutput(self):
        label, extra_tooltip = trim_numeric_label(GetByLabel('UI/Agency/ColonyResourcesAgency/WorkforceOutput'), 26)
        workforce_output_container = Container(name='workforceOutputContainer', parent=self.filtersCont, align=uiconst.TOTOP, height=40, padBottom=5)
        workforce_output_label = Label(name='constructWorkforceOutputLabel', parent=workforce_output_container, align=uiconst.CENTERLEFT, text=label)
        self.workforce_output_control = SingleLineEditInteger(name='workforceOutputControl', parent=workforce_output_container, align=uiconst.CENTERRIGHT, width=80, setvalue=self._GetWorkforceOutput(), OnChange=self.OnWorkforceOutputChanged, datatype=int)
        if extra_tooltip:
            more_info = MoreInfoIcon(parent=workforce_output_container, pos=(workforce_output_label.width + 4,
             0,
             16,
             16), align=uiconst.CENTERLEFT)
            more_info.hint = extra_tooltip

    def ConstructReagents(self):
        reagents_magmatic_gas_container = Container(name='reagentsMagmaticGasContainer', parent=self.filtersCont, align=uiconst.TOTOP, height=40, padBottom=5)
        reagents_magmatic_gas_label = Label(name='reagentsMagmaticGasLabel', parent=reagents_magmatic_gas_container, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Agency/ColonyResourcesAgency/MagmaticGas'))
        reagents_magmatic_gas_richness_combo = Combo(name='reagentsTypeCombo', parent=reagents_magmatic_gas_container, align=uiconst.CENTERRIGHT, width=140, options=self.GetReagentRichnessOptions(), callback=self.OnMagmaticGasRichnessCombo, select=self._GetMagmaticGasRichness())
        reagents_superionic_ice_container = Container(parent=self.filtersCont, align=uiconst.TOTOP, height=40, padBottom=5)
        reagents_superionic_ice_label = Label(name='reagentsSuperionicIceLabel', parent=reagents_superionic_ice_container, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Agency/ColonyResourcesAgency/SuperionicIce'))
        reagents_richness_superionic_ice_combo = Combo(name='reagentsRichnessCombo', parent=reagents_superionic_ice_container, align=uiconst.CENTERRIGHT, width=140, options=self.GetReagentRichnessOptions(), callback=self.OnSuperionicIceRichnessCombo, select=self._GetSuperionicIceRichness())

    def ConstructOrbitalStructuresCheckbox(self):
        orbital_structures_checkbox = Checkbox(parent=self.filtersCont, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/ColonyResourcesAgency/ShowSystemsWithOrbitalStructures'), checked=self._GetOrbitalStructureCheck(), callback=self.OnOrbitalStructuresCheckbox, hint='')

    def ConstructSovereigntyCombo(self):
        sovereignty_combo = FilterCombo(name='sovereigntyCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/Sovereignty/Sovereignty'), options=self.GetSovereigntyComboOptions(), callback=self.OnSovereigntyCombo, select=self._GetSelectedSovereignty())

    def ConstructSkyhookCombo(self):
        FilterCombo(name='skyhookCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/Agency/OrbitalSkyhooks'), options=self.GetSkyhookComboOptions(), callback=self.OnSkyhookCombo, select=self._GetSelectedSkyhook())

    def ConstructDistanceCombo(self):
        FilterCombo(name='distanceCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/Common/Location'), options=self.GetDistanceComboOptions(), callback=self.OnDistanceCombo, select=self._GetSelectedDistance())
        self.regionCombo = FilterCombo(name='regionCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/Common/LocationTypes/Region'), options=self.GetRegionComboOptions(), callback=self.OnRegionCombo, select=self._GetSelectedRegion())
        value = self._GetSelectedDistance()
        self.CheckShowRegion(value)

    def ConstructFilters(self):
        self.ConstructDistanceCombo()
        self.ConstructSovereigntyCombo()
        self.ConstructSkyhookCombo()
        self.ConstructPerSystemPlanetFilter()
        self.ConstructPowerOutput()
        self.ConstructWorkforceOutput()
        self.ConstructReagents()

    def CheckShowRegion(self, value):
        if value == agencyConst.DISTANCE_REGION:
            agencyFilters.SetFilterValueWithoutEvent(self.contentGroupID, agencyConst.FILTERTYPE_REGION, session.regionid)
            self.regionCombo.Show()
            self.regionCombo.SelectItemByValue(self._GetSelectedRegionID())
        else:
            self.regionCombo.Hide()

    def GetRegionComboOptions(self):
        return sorted([ (self._GetRegionName(cfg.mapRegionCache.get(regionID, None)), regionID) for regionID in get_sov_region_ids() ])

    def GetSovereigntyComboOptions(self):
        return [(GetByLabel('UI/Agency/ColonyResourcesAgency/All'), agencyConst.SOVEREIGNTY_ALL), (GetByLabel('UI/Agency/ColonyResourcesAgency/Claimed'), agencyConst.SOVEREIGNTY_CLAIMED), (GetByLabel('UI/Agency/ColonyResourcesAgency/Unclaimed'), agencyConst.SOVEREIGNTY_UNCLAIMED)]

    def GetSkyhookComboOptions(self):
        return [(GetByLabel('UI/Agency/ColonyResourcesAgency/SkyhookTheftAny'), agencyConst.SKYHOOKS_THEFT_ANY_STATE), (GetByLabel('UI/Agency/ColonyResourcesAgency/SkyhookTheftVulnerable'), agencyConst.SKYHOOKS_THEFT_VULNERABLE)]

    def GetReagentsTypeOptions(self):
        return [(GetByLabel('UI/Agency/ColonyResourcesAgency/AnyType'), agencyConst.REAGENTS_ALL), (GetByLabel('UI/Agency/ColonyResourcesAgency/SuperionicIce'), agencyConst.REAGENTS_SUPERIONIC_ICE), (GetByLabel('UI/Agency/ColonyResourcesAgency/MagmaticGas'), agencyConst.REAGENTS_MAGMATIC_GAS)]

    def GetReagentRichnessOptions(self):
        return [(GetByLabel('UI/Agency/ColonyResourcesAgency/AnyAbundance'), agencyConst.REAGENTS_RICHNESS_ALL),
         (GetByLabel(richnessLabelPaths[RICHNESS_MODEST]), agencyConst.REAGENTS_RICHNESS_MODEST),
         (GetByLabel(richnessLabelPaths[RICHNESS_AVG]), agencyConst.REAGENTS_RICHNESS_AVERAGE),
         (GetByLabel(richnessLabelPaths[RICHNESS_ABUNDANT]), agencyConst.REAGENTS_RICHNESS_ABUNDANT)]

    def _GetOrbitalStructureCheck(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_ORBITAL_STRUCTURES)

    def _GetPowerOutput(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_POWEROUTPUT)

    def _GetWorkforceOutput(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_WORKFORCEOUTPUT)

    def _GetSelectedDistance(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_DISTANCE)

    def _GetSelectedRegion(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_REGION)

    def _GetSelectedSovereignty(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_SOVEREIGNTY)

    def _GetSelectedSkyhook(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_SKYHOOK_THEFT_VULNERABILITY)

    def _GetReagentsType(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_REAGENTS_TYPE)

    def _GetReagentsRichness(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_REAGENTS_RICHNESS)

    def _GetMagmaticGasRichness(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_REAGENTS_MAGMATIC_GAS_RICHNESS)

    def _GetSuperionicIceRichness(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_REAGENTS_SUPERIONIC_ICE_RICHNESS)

    def OnTimeSensitiveValueChanged(self):
        now = gametime.GetWallclockTime()
        self.last_filter_edit_time = now
        uthread2.start_tasklet(self.WaitForFilterInputToStabilize, now)

    def WaitForFilterInputToStabilize(self, filter_edit_time):
        uthread2.sleep(1)
        if self.last_filter_edit_time != filter_edit_time:
            return
        power_output_value = self.power_output_control.GetValue()
        workforce_output_value = self.workforce_output_control.GetValue()
        self._SetPowerOutput(power_output_value)
        self._SetWorkforceOutput(workforce_output_value)
        self._SetPerSystemPlanet(self.per_system_planet_value)
        agencyFilters.onFilterChanged(self.contentGroupID, None, None)

    def OnDistanceCombo(self, combo, key, value):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_DISTANCE, value)
        self.CheckShowRegion(value)

    def OnRegionCombo(self, combo, key, value):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_REGION, value)

    def OnPerSystemPlanetChanged(self, button):
        self.per_system_planet_value = button.GetReturnValue()
        self.OnTimeSensitiveValueChanged()

    def _SetPerSystemPlanet(self, value):
        agencyFilters.SetFilterValueWithoutEvent(self.contentGroupID, agencyConst.FILTERTYPE_PER_SYSTEM_PLANET, value)

    def OnPowerOutputChanged(self, value):
        self.OnTimeSensitiveValueChanged()

    def _SetPowerOutput(self, value):
        try:
            intValue = int(value)
        except (ValueError, TypeError):
            pass
        else:
            agencyFilters.SetFilterValueWithoutEvent(self.contentGroupID, agencyConst.FILTERTYPE_POWEROUTPUT, intValue)

    def OnWorkforceOutputChanged(self, value):
        self.OnTimeSensitiveValueChanged()

    def _SetWorkforceOutput(self, value):
        try:
            intValue = int(value)
        except (ValueError, TypeError):
            pass
        else:
            agencyFilters.SetFilterValueWithoutEvent(self.contentGroupID, agencyConst.FILTERTYPE_WORKFORCEOUTPUT, intValue)

    def OnReagentsTypeCombo(self, *args):
        combo, selection, number = args
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_REAGENTS_TYPE, number)

    def OnReagentsRichnessCombo(self, *args):
        combo, selection, number = args
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_REAGENTS_RICHNESS, number)

    def OnMagmaticGasRichnessCombo(self, *args):
        combo, selection, number = args
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_REAGENTS_MAGMATIC_GAS_RICHNESS, number)

    def OnSuperionicIceRichnessCombo(self, *args):
        combo, selection, number = args
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_REAGENTS_SUPERIONIC_ICE_RICHNESS, number)

    def OnSovereigntyCombo(self, *args):
        combo, selection, number = args
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_SOVEREIGNTY, number)

    def OnSkyhookCombo(self, *args):
        combo, selection, number = args
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_SKYHOOK_THEFT_VULNERABILITY, number)

    def OnOrbitalStructuresCheckbox(self, checkbox):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_ORBITAL_STRUCTURES, checkbox.GetValue())
