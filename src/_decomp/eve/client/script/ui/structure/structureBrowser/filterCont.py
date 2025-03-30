#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\filterCont.py
from carbonui.control.combo import Combo
from carbonui.primitives.base import ReverseScaleDpi
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.filter import Filter
from eve.client.script.ui.quickFilter import QuickFilterEdit
import eve.client.script.ui.structure.structureBrowser.browserUIConst as browserUIConst
from eve.client.script.ui.structure.structureBrowser.filterContUtil import GetLocationOptions
from eve.common.script.sys import idCheckers
from localization import GetByLabel
import carbonui.const as uiconst
from eve.common.lib import appConst as const
import uthread2
locationToName = {const.rangeRegion: GetByLabel('UI/Common/LocationTypes/Region'),
 const.rangeConstellation: GetByLabel('UI/Common/LocationTypes/Constellation'),
 const.rangeSolarSystem: GetByLabel('UI/Common/LocationTypes/SolarSystem')}

class FilterCont(Container):
    __notifyevents__ = ['OnSessionChanged']
    default_height = 32
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        self.filterContController = attributes.filterContController
        Container.ApplyAttributes(self, attributes)
        self.innerCont = Container(name='innerCont', parent=self, align=uiconst.TOALL, padRight=100, clipChildren=True)
        self.innerCont._OnResize = self.OnResizeInner
        self.lastInnerPercentage = 1.0
        self.innerContElements = []
        self.ConstructUI()
        self.OnResizeInner()
        sm.RegisterNotify(self)

    def ConstructUI(self):
        self.AddFilterBox()
        self.AddStructureFilter()
        self.AddServiceFilter()

    def AddStructureFilter(self):
        structureOptions = self.GetStructureOptions()
        self.filterContController.structureTypeFilterController.SetOptions(structureOptions)
        structureTypeFilterParent = Container(name='structureTypeFilterParent', align=uiconst.TOLEFT, parent=self.innerCont, padRight=10)
        structureTypeFilter = Filter(name='structureTypeFilter', parent=structureTypeFilterParent, filterText=GetByLabel('UI/Structures/Browser/StructureType'), filterTextShort=GetByLabel('UI/Structures/Browser/StructureTypeShort'), filterController=self.filterContController.structureTypeFilterController, columns=1, align=uiconst.CENTERLEFT)
        structureTypeFilterParent.width = structureTypeFilter.width
        structureTypeFilterParent.fullWidthOfElement = structureTypeFilter.width
        self.innerContElements.append(structureTypeFilterParent)

    def AddServiceFilter(self):
        serviceOptions = self.filterContController.GetServiceOptions()
        self.filterContController.serviceFilterController.SetOptions(serviceOptions)
        serviceFilterParent = Container(name='serviceFilterParent', align=uiconst.TOLEFT, parent=self.innerCont, padRight=10)
        serviceFilter = Filter(name='structureServiceFilter', parent=serviceFilterParent, filterText=GetByLabel('UI/Structures/Browser/ServiceFilter'), filterTextShort=GetByLabel('UI/Structures/Browser/ServiceFilterShort'), filterController=self.filterContController.serviceFilterController, columns=1, align=uiconst.CENTERLEFT)
        serviceFilterParent.width = serviceFilter.width
        serviceFilterParent.fullWidthOfElement = serviceFilter.width
        self.innerContElements.append(serviceFilterParent)

    def AddFilterBox(self):
        text = self.filterContController.GetTextFilter()
        self.filterEdit = QuickFilterEdit(name='searchField', parent=self, hintText=GetByLabel('UI/Inventory/Filter'), maxLength=64, align=uiconst.CENTERRIGHT, OnClearFilter=self.OnFilterEditCleared, padRight=4, setvalue=text)
        self.filterEdit.ReloadFunction = self.OnFilterEdit

    def OnFilterEdit(self):
        self.RecordTextFieldChanges()

    def OnFilterEditCleared(self):
        self.RecordTextFieldChanges()

    def RecordTextFieldChanges(self):
        filterText = self.filterEdit.GetValue().strip().lower()
        self.filterContController.TextFilterChanged(filterText)

    def OnSessionChanged(self, isremote, sess, change):
        pass

    def GetStructureOptions(self):
        return self.filterContController.GetStructureOptions()

    def OnResizeInner(self, *args):
        resizableInnerElements = {x for x in self.innerContElements if getattr(x, 'isResizable', True)}
        unresizableInnerElements = {x for x in self.innerContElements if not getattr(x, 'isResizable', True)}
        spaceForResizables = ReverseScaleDpi(self.innerCont.displayWidth)
        spaceForResizables -= sum((x.fullWidthOfElement for x in unresizableInnerElements))
        padRights = sum((x.padRight for x in self.innerContElements))
        spaceForResizables -= padRights
        fullWidthOfResizableElements = sum((x.fullWidthOfElement for x in resizableInnerElements))
        currentWidthOfResizableElements = sum((x.width for x in resizableInnerElements))
        if fullWidthOfResizableElements <= 0:
            return
        percentageBefore = self.lastInnerPercentage
        percentage = float(spaceForResizables) / fullWidthOfResizableElements
        if percentage < 1.0:
            if abs(percentage - percentageBefore) < 0.01:
                return
            self.lastInnerPercentage = percentage
            for each in resizableInnerElements:
                newWidth = int(each.fullWidthOfElement * percentage)
                each.width = newWidth
                child = each.children[0]
                child.width = newWidth
                if isinstance(child, Filter):
                    child.ChangeLabelIfNeeded()

        elif currentWidthOfResizableElements < fullWidthOfResizableElements:
            for each in resizableInnerElements:
                each.width = each.fullWidthOfElement
                child = each.children[0]
                child.width = each.fullWidthOfElement
                if isinstance(child, Filter):
                    child.ResetLabel()


class FilterContAllStructures(FilterCont):

    def ConstructUI(self):
        self.AddOwnerCombo()
        self.AddLocationCombo()
        FilterCont.ConstructUI(self)

    def AddOwnerCombo(self):
        ownerOptions = [(GetByLabel('UI/Industry/AllFacilities'), browserUIConst.OWNER_ANY), (GetByLabel('UI/Industry/PublicFacilities'),
          browserUIConst.OWNER_NPC,
          None,
          'res:/UI/Texture/Classes/Inventory/readOnly.png'), (GetByLabel('UI/Industry/CorpOwnedFacilities'),
          browserUIConst.OWNER_CORP,
          None,
          'res:/UI/Texture/Classes/Industry/iconCorp.png')]
        selected = self.filterContController.GetStructureOwnerValue()
        ownerComboParent = Container(name='ownerComboParent', align=uiconst.TOLEFT, parent=self.innerCont, padRight=10)
        self.ownerCombo = Combo(name='ownerCombo', parent=ownerComboParent, align=uiconst.CENTERLEFT, prefsKey='StructureBrowserOwner', callback=self.ChangeStructureOwnerFilter, options=ownerOptions, select=selected, padRight=4)
        ownerComboParent.width = self.ownerCombo.width

    def AddLocationCombo(self):
        locationOptions = self.GetLocationOptions()
        selected = self.filterContController.GetRange()
        locationRangeParent = Container(name='locationRangeParent', align=uiconst.TOLEFT, parent=self.innerCont, padRight=10)
        self.locationRange = Combo(label='', parent=locationRangeParent, options=locationOptions, name='locationRange', select=selected, callback=self.ChangeLocationRange, align=uiconst.CENTERLEFT)
        locationRangeParent.width = self.locationRange.width

    def GetLocationOptions(self):
        locationOptions = []
        locationIDs = GetLocationOptions()
        for locationID in locationIDs:
            text = locationToName[locationID]
            locationOptions.append((text, locationID))

        return locationOptions

    def ChangeStructureOwnerFilter(self, cb, label, value):
        self.filterContController.ChangeStructureOwnerFilter(value)

    def ChangeLocationRange(self, cb, label, value):
        self.filterContController.ChangeLocationRange(value)

    def OnSessionChanged(self, isremote, sess, change):
        if 'regionid' in change:
            oldRegionID, newRegionID = change['regionid']
            if idCheckers.IsWormholeRegion(oldRegionID) or idCheckers.IsWormholeRegion(newRegionID):
                self.SetLocationOptions()

    def SetLocationOptions(self):
        selected = self.filterContController.GetRange()
        locationOptions = self.GetLocationOptions()
        self.locationRange.LoadOptions(locationOptions, select=selected)


class FilterContMyStructures(FilterCont):

    def ConstructUI(self):
        FilterCont.ConstructUI(self)
        self.AddLowPowerCb()

    def AddLowPowerCb(self):
        cbParent = Container(name='cbParent', align=uiconst.TOLEFT, parent=self.innerCont)
        text = GetByLabel('UI/Structures/Browser/LowPowerFilter')
        cb = Checkbox(parent=cbParent, text=text, checked=self.filterContController.OnlyShowLowPower(), align=uiconst.CENTERLEFT, callback=self.ChangeLowPower)
        w, _ = cb.label.MeasureTextSize(text)
        w += cb.label.padLeft
        cb.width = w
        cbParent.width = cb.width
        cbParent.fullWidthOfElement = cb.width
        cbParent.isResizable = False
        self.innerContElements.append(cbParent)

    def ChangeLowPower(self, cb, *args):
        value = cb.GetValue()
        self.filterContController.ChangeLowPower(value)


class FilterContMySkyhooks(Container):
    __notifyevents__ = ['OnSessionChanged']
    default_height = 32
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        self.filterContController = attributes.filterContController
        Container.ApplyAttributes(self, attributes)
        self.innerCont = Container(name='innerCont', parent=self, align=uiconst.TOALL, padRight=100, clipChildren=True)
        self.ConstructUI()
        sm.RegisterNotify(self)

    def ConstructUI(self):
        self.AddFilterBox()
        self.AddLocationCombo()
        self.AddStateCombo()
        self.AddTheftVulnerabilityCombo()

    def AddFilterBox(self):
        text = self.filterContController.GetTextFilter()
        self.filterEdit = QuickFilterEdit(name='searchField', parent=self, hintText=GetByLabel('UI/Inventory/Filter'), maxLength=64, align=uiconst.CENTERRIGHT, OnClearFilter=self.OnFilterEditCleared, padRight=4, setvalue=text)
        self.filterEdit.ReloadFunction = self.OnFilterEdit

    def AddLocationCombo(self):
        container = ContainerAutoSize(name='locationRangeParent', align=uiconst.TOLEFT, parent=self.innerCont, padRight=10)
        Combo(name='locationRange', parent=container, options=self.filterContController.GetLocationOptions(), select=self.filterContController.GetSelectedLocationOption(), callback=self.OnDistanceCombo, align=uiconst.TOLEFT, label='')
        self._regionCombo = Combo(name='regionCombo', parent=container, align=uiconst.TOLEFT, label='', options=self.filterContController.GetRegionOptions(), select=self.filterContController.GetSelectedRegionOption(), callback=self.OnRegionCombo, nothingSelectedText=GetByLabel('UI/Common/LocationTypes/Region'))
        self._regionCombo.display = self._ShouldDisplayRegionCombo()

    def AddStateCombo(self):
        Combo(name='stateCombo', parent=self.innerCont, align=uiconst.TOLEFT, padRight=10, options=self.filterContController.GetStateOptions(), select=self.filterContController.GetSelectedStateOption(), callback=self.OnStateCombo, label='')

    def _ShouldDisplayRegionCombo(self):
        return self.filterContController.GetSelectedLocationOption() == -1

    def OnDistanceCombo(self, combo, key, value):
        self.filterContController.SetSelectedLocationOption(value)
        self._regionCombo.display = self._ShouldDisplayRegionCombo()

    def OnRegionCombo(self, combo, key, value):
        self.filterContController.SetSelectedRegionOption(value)

    def OnStateCombo(self, combo, key, value):
        self.filterContController.SetSelectedStateOption(value)

    def OnTheftVulnerabilityCombo(self, combo, key, value):
        self.filterContController.SetSelectedTheftVulnerabilityOption(value)

    def OnFilterEdit(self):
        self.RecordTextFieldChanges()

    def OnFilterEditCleared(self):
        self.RecordTextFieldChanges()

    @uthread2.debounce(0.2)
    def RecordTextFieldChanges(self):
        filterText = self.filterEdit.GetValue().strip().lower()
        self.filterContController.TextFilterChanged(filterText)

    def OnSessionChanged(self, isremote, sess, change):
        pass

    def AddTheftVulnerabilityCombo(self):
        Combo(name='theftCombo', parent=self.innerCont, align=uiconst.TOLEFT, padRight=10, options=self.filterContController.GetTheftVulnerabilityOptions(), select=self.filterContController.GetSelectedTheftVulnerabilityOption(), callback=self.OnTheftVulnerabilityCombo, label='')
