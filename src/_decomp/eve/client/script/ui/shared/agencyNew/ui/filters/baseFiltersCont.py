#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\filters\baseFiltersCont.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.client.script.ui.shared.agencyNew import agencyFilters, agencyConst
from carbonui.control.section import Section
from eve.client.script.ui.shared.agencyNew.ui.controls.filterCombo import FilterCombo
from eve.common.script.sys.idCheckers import IsKnownSpaceRegion
from localization import GetByLabel, GetByMessageID
PAD = 12
DISTANCES = ((agencyConst.DISTANCE_CURRSYSTEM, GetByLabel('UI/Generic/CurrentSystem')),
 (agencyConst.DISTANCE_2JUMPS, GetByLabel('UI/Common/WithinJumps', numJumps=2)),
 (agencyConst.DISTANCE_5JUMPS, GetByLabel('UI/Common/WithinJumps', numJumps=5)),
 (agencyConst.DISTANCE_10JUMPS, GetByLabel('UI/Common/WithinJumps', numJumps=10)),
 (agencyConst.DISTANCE_ANY, GetByLabel('UI/Agency/ContentOfAnyDistance')),
 (agencyConst.DISTANCE_REGION, GetByLabel('UI/Agency/SpecificRegion')))

class BaseFiltersCont(Section):
    default_name = 'BaseFiltersCont'
    default_contentGroupID = None
    default_headerText = GetByLabel('UI/Calendar/CalendarWindow/Filters')

    def ApplyAttributes(self, attributes):
        super(BaseFiltersCont, self).ApplyAttributes(attributes)
        self.contentGroupID = attributes.get('contentGroupID', self.default_contentGroupID)
        self.ConstructBaseLayout()
        self.UpdateResetFiltersButton()
        agencyFilters.onFilterChanged.connect(self.OnAgencyFilterChanged)

    def UpdateResetFiltersButton(self):
        if any((agencyFilters.GetFilterValue(self.contentGroupID, filterType) != defaultValue for filterType, defaultValue in self.GetDefaultFilters().iteritems())):
            self.ActivateResetFiltersButton()
        else:
            self.DisableResetFiltersButton()

    def GetDefaultFilters(self):
        return agencyConst.FILTER_DEFAULTS

    def Close(self):
        agencyFilters.onFilterChanged.disconnect(self.OnAgencyFilterChanged)
        super(BaseFiltersCont, self).Close()

    def OnAgencyFilterChanged(self, *args, **kwargs):
        self.UpdateResetFiltersButton()

    def ConstructBaseLayout(self):
        self.ConstructResetButton()
        self.filtersCont = ScrollContainer(name='filtersCont', parent=self, padBottom=6)
        self.ConstructFilters()

    def ConstructResetButton(self):
        buttonCont = ContainerAutoSize(name='buttonCont', parent=self, align=uiconst.TOBOTTOM)
        self.resetFiltersButton = Button(name='resetButton', parent=buttonCont, align=uiconst.BOTTOMRIGHT, label=GetByLabel('UI/Commands/ResetAll'), hint=GetByLabel('UI/Agency/resetAllPageFilters'), func=self.OnResetFiltersButtonPressed)

    def OnResetFiltersButtonPressed(self, *args, **kwargs):
        self.ResetAllFilters()
        self.ReconstructFilters()

    def ResetAllFilters(self):
        for filterType, defaultValue in agencyConst.FILTER_DEFAULTS.iteritems():
            agencyFilters.ResetFilter(self.contentGroupID, filterType)

    def ReconstructFilters(self):
        self.filtersCont.Flush()
        self.ConstructFilters()

    def ActivateResetFiltersButton(self):
        self.resetFiltersButton.Enable()

    def DisableResetFiltersButton(self):
        self.resetFiltersButton.Disable()

    def ConstructFilters(self):
        self.ConstructDistanceCombo()
        self.ConstructSecurityCombo()

    def ConstructSecurityCombo(self):
        FilterCombo(name='securityStatusCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('Tooltips/CharacterSheet/SecurityStatus'), options=self.GetSecurityStatusOptions(), callback=self.OnSecurityStatusCombo, select=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_SECURITYSTATUS))

    def OnSecurityStatusCombo(self, combo, key, value):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_SECURITYSTATUS, value)

    def GetSecurityStatusOptions(self):
        return ((GetByLabel('UI/Agency/AnySecurity'), agencyConst.FILTERVALUE_ANY),
         (GetByLabel('UI/Common/HighSec'), agencyConst.SECURITYSTATUS_HIGHSEC),
         (GetByLabel('UI/Common/LowSec'), agencyConst.SECURITYSTATUS_LOWSEC),
         (GetByLabel('UI/Common/NullSec'), agencyConst.SECURITYSTATUS_NULLSEC))

    def ConstructDistanceCombo(self):
        FilterCombo(name='distanceCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/Common/Location'), options=self.GetDistanceComboOptions(), callback=self.OnDistanceCombo, select=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_DISTANCE))
        self.regionCombo = FilterCombo(name='regionCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/Common/LocationTypes/Region'), options=self.GetRegionComboOptions(), callback=self.OnRegionCombo, select=self._GetSelectedRegionID())
        self.constellationCombo = FilterCombo(name='constellationCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/Common/LocationTypes/Constellation'), callback=self.OnConstellationCombo)
        value = agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_DISTANCE)
        self.CheckShowRegionAndConstellationCombo(value)

    def OnDistanceCombo(self, combo, key, value):
        if value == agencyConst.DISTANCE_REGION:
            agencyFilters.SetFilterValueWithoutEvent(self.contentGroupID, agencyConst.FILTERTYPE_REGION, session.regionid)
            agencyFilters.SetFilterValueWithoutEvent(self.contentGroupID, agencyConst.FILTERTYPE_CONSTELLATION, agencyConst.CONSTELLATION_ANY)
        self.CheckShowRegionAndConstellationCombo(value)
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_DISTANCE, value)

    def CheckShowRegionAndConstellationCombo(self, value):
        if value == agencyConst.DISTANCE_REGION:
            self.regionCombo.Show()
            self.regionCombo.SelectItemByValue(self._GetSelectedRegionID())
            self.constellationCombo.Show()
            self.UpdateConstellationCombo()
        else:
            self.regionCombo.Hide()
            self.constellationCombo.Hide()

    def _GetSelectedRegionID(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_REGION) or session.regionid

    def GetDistanceComboOptions(self):
        return [ (label, value) for value, label in DISTANCES ]

    def GetRegionComboOptions(self):
        options = [ (self._GetRegionName(region), region.regionID) for region in cfg.mapRegionCache.values() if IsKnownSpaceRegion(region.regionID) ]
        return sorted(options)

    def _GetRegionName(self, region):
        regionName = GetByMessageID(region.nameID)
        if region.regionID == session.regionid:
            regionName = GetByLabel('UI/Agency/CurrentRegion', regionName=regionName)
        return regionName

    def OnRegionCombo(self, combo, key, value):
        agencyFilters.SetFilterValueWithoutEvent(self.contentGroupID, agencyConst.FILTERTYPE_CONSTELLATION, agencyConst.CONSTELLATION_ANY)
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_REGION, value)
        self.UpdateConstellationCombo()

    def GetConstellationComboOptions(self):
        regionID = self._GetSelectedRegionID()
        constIDs = cfg.mapRegionCache.Get(regionID).constellationIDs
        options = [ (self._GetConstellationName(constID), constID) for constID in constIDs ]
        options = sorted(options)
        options.insert(0, (GetByLabel('UI/Agency/AnyConstellation'), agencyConst.CONSTELLATION_ANY))
        return options

    def _GetConstellationName(self, constID):
        constellation = cfg.mapConstellationCache.Get(constID)
        constellationName = GetByMessageID(constellation.nameID)
        if constellation.constellationID == session.constellationid:
            constellationName = GetByLabel('UI/Agency/CurrentConstellation', constellationName=constellationName)
        return constellationName

    def OnConstellationCombo(self, combo, key, value):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_CONSTELLATION, value)

    def UpdateConstellationCombo(self):
        value = agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_CONSTELLATION)
        self.constellationCombo.LoadOptions(self.GetConstellationComboOptions(), select=value)
