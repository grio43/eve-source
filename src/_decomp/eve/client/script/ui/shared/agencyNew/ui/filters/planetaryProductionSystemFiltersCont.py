#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\filters\planetaryProductionSystemFiltersCont.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.agencyNew import agencyFilters, agencyConst
from carbonui.control.section import SubSectionAutoSize
from eve.client.script.ui.shared.agencyNew.ui.filters.baseFiltersCont import BaseFiltersCont
from eve.client.script.ui.shared.planet import planetConst
from eve.common.lib import appConst
from localization import GetByLabel

class PlanetaryProductionSystemFiltersCont(BaseFiltersCont):
    default_name = 'PlanetaryProductionSystemFiltersCont'

    def ApplyAttributes(self, attributes):
        self.contentGroupID = attributes.contentGroupID
        self.checkBoxes = []
        self.UpdatePlanetTypeFilterDict()
        super(PlanetaryProductionSystemFiltersCont, self).ApplyAttributes(attributes)

    def UpdatePlanetTypeFilterDict(self):
        self.planetTypeFilterDict = agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_PLANETTYPES) or agencyConst.DEFAULT_PLANET_TYPES_FILTER.copy()

    def ConstructFilters(self):
        self.ConstructDistanceCombo()
        self.ConstructSecurityCombo()
        self.ConstructPlanetTypeCheckboxes()
        self.ConstructMultiSelectButtons()

    def ConstructPlanetTypeCheckboxes(self):
        self.checkboxSection = SubSectionAutoSize(headerText=GetByLabel('UI/Agency/PlanetaryProduction/planetTypes'), parent=self.filtersCont, align=uiconst.TOTOP)
        self.checkboxSection.caption.uppercase = False
        for planetTypeID in planetConst.PLANET_TYPES:
            if planetTypeID in [appConst.typePlanetShattered, appConst.typePlanetScorched]:
                continue
            self._ConstructPlanetTypeCheckbox(planetTypeID)

    def _ConstructPlanetTypeCheckbox(self, planetType):
        planetTypeFilterContainer = Container(name='planetTypeFilterContainer', parent=self.checkboxSection, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, height=16, padBottom=4)
        EveLabelMedium(name='planetTypeFilterLabel', parent=planetTypeFilterContainer, align=uiconst.CENTERLEFT, text=GetByLabel(planetConst.PLANETTYPE_NAMES[planetType]))
        isPlanetTypeChecked = self.planetTypeFilterDict[planetType]
        planetTypeCheckbox = Checkbox(name='planetTypeCheckbox', parent=planetTypeFilterContainer, align=uiconst.TORIGHT, checked=isPlanetTypeChecked, callback=lambda x: self.OnPlanetTypeCheckbox(planetTypeCheckbox, planetType))
        self.checkBoxes.append(planetTypeCheckbox)

    def ConstructMultiSelectButtons(self):
        multiSelectButtonsContainer = Container(name='multiSelectButtonsContainer', parent=self.filtersCont, align=uiconst.TOTOP, padTop=6, height=18)
        Button(name='selectAllButton', align=uiconst.TOLEFT, parent=multiSelectButtonsContainer, label=GetByLabel('UI/Common/SelectAll'), func=self.SelectAllPlanetTypes)
        Button(name='clearAllButton', align=uiconst.TOLEFT, parent=multiSelectButtonsContainer, label=GetByLabel('UI/Common/DeselectAll'), func=self.ClearAllPlanetTypes, padLeft=10)

    def SelectAllPlanetTypes(self, *args):
        self.SetAllValuesInPlanetTypeFilter(True)
        self.SetAllCheckboxes(True)
        self.PersistPlanetTypeFilter()

    def ClearAllPlanetTypes(self, *args):
        self.SetAllValuesInPlanetTypeFilter(False)
        self.SetAllCheckboxes(False)
        self.PersistPlanetTypeFilter()

    def SetAllCheckboxes(self, isActive):
        for checkbox in self.checkBoxes:
            checkbox.SetChecked(isActive, report=False)

    def SetAllValuesInPlanetTypeFilter(self, isActive):
        for planetType in self.planetTypeFilterDict.keys():
            self.planetTypeFilterDict[planetType] = isActive

    def OnPlanetTypeCheckbox(self, checkbox, planetType):
        self.planetTypeFilterDict[planetType] = bool(checkbox.GetValue())
        self.PersistPlanetTypeFilter()

    def PersistPlanetTypeFilter(self):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_PLANETTYPES, self.planetTypeFilterDict, log=False)

    def OnResetFiltersButtonPressed(self, *args, **kwargs):
        self.ResetAllFilters()
        self.UpdatePlanetTypeFilterDict()
        self.ReconstructFilters()
