#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\scannerfiltereditor.py
import evetypes
from carbonui.button.const import HEIGHT_NORMAL
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from eve.client.script.parklife.state import GetNPCGroups
from eve.client.script.ui.control import eveLabel, eveScroll
import carbonui.const as uiconst
import localization
from eve.client.script.ui.control.entries.checkbox import CheckboxEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.common.lib import appConst as const
from probescanning.explorationSites import EXPLORATION_SITE_TYPES
SCAN_GROUP_NAMES = {const.probeScanGroupSignatures: localization.GetByLabel('UI/Inflight/Scanner/CosmicSignature'),
 const.probeScanGroupShips: localization.GetByLabel('UI/Inflight/Scanner/Ship'),
 const.probeScanGroupStructures: localization.GetByLabel('UI/Inflight/Scanner/Structure'),
 const.probeScanGroupDrones: localization.GetByLabel('UI/Inflight/Scanner/Drone'),
 const.probeScanGroupCharges: localization.GetByLabel('UI/Inflight/Scanner/Charge'),
 const.probeScanGroupNPCs: localization.GetByLabel('UI/Inflight/Scanner/NPC'),
 const.probeScanGroupFighters: localization.GetByLabel('UI/Inflight/Scanner/Fighter'),
 const.probeScanGroupStarBase: localization.GetByLabel('UI/Inflight/Scanner/StarBase'),
 const.probeScanGroupOrbitals: localization.GetByLabel('UI/Inflight/Scanner/Orbital'),
 const.probeScanGroupDeployable: localization.GetByLabel('UI/Inflight/Scanner/Deployable'),
 const.probeScanGroupSovereignty: localization.GetByLabel('UI/Inflight/Scanner/Sovereignty'),
 const.probeScanGroupAbyssalTraces: localization.GetByLabel('UI/Inflight/Scanner/AbyssalTrace')}

class ScannerFilterEditor(Window):
    default_windowID = 'probeScannerFilterEditor'
    default_minSize = (420, 250)
    default_width = 500
    default_height = 500
    default_scope = uiconst.SCOPE_INFLIGHT
    default_captionLabelPath = 'UI/Inflight/Scanner/ScannerFilterEditor'

    def ApplyAttributes(self, attributes):
        super(ScannerFilterEditor, self).ApplyAttributes(attributes)
        self.specialGroups = GetNPCGroups()
        self.filterID = None
        self.main = self.sr.main
        self.topParent = Container(name='topParent', parent=self.main, height=64, align=uiconst.TOTOP, padding=(const.defaultPadding,) * 4)
        eveLabel.EveLabelMedium(name='filterNameLabel', text=localization.GetByLabel('UI/Inflight/Scanner/FilterName'), parent=self.topParent, state=uiconst.UI_DISABLED, align=uiconst.TOTOP)
        nameContainer = Container(name='nameContainer', parent=self.topParent, align=uiconst.TOTOP, height=SingleLineEditText.default_height)
        self.filterNameEdit = SingleLineEditText(name='filterNameEdit', parent=nameContainer, setvalue=None, align=uiconst.TOLEFT, width=200, maxLength=64)
        self.descriptionAndSearchContainer = Container(name='descriptionAndSearchContainer', parent=self.topParent, align=uiconst.TOTOP, height=HEIGHT_NORMAL, padTop=8)
        eveLabel.EveLabelMedium(name='descriptionLabel', text=localization.GetByLabel('UI/Inflight/Scanner/SelectGroupsToFilter'), parent=self.descriptionAndSearchContainer, align=uiconst.CENTERLEFT)
        self.searchBar = QuickFilterEdit(name='searchBar', parent=self.descriptionAndSearchContainer, align=uiconst.CENTERRIGHT)
        self.searchBar.ReloadFunction = self.LoadTypes
        self.scroll = eveScroll.Scroll(name='filterGroupsScroll', parent=self.sr.main, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         const.defaultPadding), multiSelect=0)
        self.DefineButtons(uiconst.OKCANCEL, okLabel=localization.GetByLabel('UI/Common/Buttons/Save'), okFunc=self.SaveChanges, cancelFunc=self.Close)

    def LoadData(self, filterID):
        self.tempState = {}
        self.filterID = filterID
        self._originalGroups = []
        if filterID is None:
            filterName = ''
        else:
            filterName, self._originalGroups = sm.GetService('scanSvc').GetResultFilter(filterID)
            self.filterNameEdit.SetValue(filterName)
            for each in self._originalGroups:
                self.tempState[each] = True

        self._originalName = filterName
        self.LoadTypes()

    def OnResizeUpdate(self, *args):
        self.topParent.height = sum([ each.height + each.top + each.padTop + each.padBottom for each in self.topParent.children if each.align == uiconst.TOTOP ])

    def SaveChanges(self, *args):
        newFilterName = self.filterNameEdit.GetValue()
        if newFilterName is None or newFilterName == '':
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/Scanner/PleaseNameFilter')})
            self.filterNameEdit.SetFocus()
            return
        if newFilterName.lower() == localization.GetByLabel('UI/Common/Show all').lower():
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/Scanner/CannotNameFilter')})
            return
        groups = [ key for key, value in self.tempState.iteritems() if bool(value) ]
        if not groups:
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/Scanner/SelectGroupsForFilter')})
            self.scroll.SetFocus()
            return
        customFilters = settings.user.ui.Get('probescanning.resultFilter.filters', {})
        existingFilterNames = [ x[0] for x in customFilters.values() ]
        if newFilterName in existingFilterNames and not self._originalName:
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/Scanner/FilterAlreadyExists')})
            self.filterNameEdit.SetFocus()
            return
        if newFilterName in existingFilterNames and groups != self._originalGroups or newFilterName != self._originalName and self._originalName:
            if eve.Message('OverwriteFilter', {'filter': newFilterName}, uiconst.YESNO) != uiconst.ID_YES:
                return
        if self.filterID is None:
            sm.GetService('scanSvc').CreateResultFilter(newFilterName, groups)
        else:
            sm.GetService('scanSvc').EditResultFilter(self.filterID, newFilterName, groups)
        oldFilterFormat = {filter[0]:filter[1] for filter in customFilters.values()}
        settings.user.ui.Set('probeScannerFilters', oldFilterFormat)
        settings.user.ui.Set('activeProbeScannerFilter', newFilterName)
        sm.ScatterEvent('OnNewScannerFilterSet')
        self.Close()

    def LoadTypes(self):
        searchText = self.searchBar.GetValue().lower()
        categoryList = {}
        for scanGroupID, groupSet in const.probeScanGroups.iteritems():
            if scanGroupID not in SCAN_GROUP_NAMES:
                continue
            catName = SCAN_GROUP_NAMES[scanGroupID]
            for groupID in groupSet:
                if groupID == const.groupCosmicSignature:
                    for signatureType in const.probeScanCosmicSignatureAttributes:
                        name = localization.GetByLabel(EXPLORATION_SITE_TYPES[signatureType])
                        if searchText and name.lower().find(searchText) < 0:
                            continue
                        if catName not in categoryList:
                            categoryList[catName] = [(groupID, signatureType)]
                        elif (groupID, signatureType) not in categoryList[catName]:
                            categoryList[catName].append((groupID, signatureType))

                else:
                    name = evetypes.GetGroupNameByGroup(groupID)
                    if searchText and name.lower().find(searchText) < 0:
                        continue
                    if catName not in categoryList:
                        categoryList[catName] = [(groupID, name)]
                    elif (groupID, name) not in categoryList[catName]:
                        categoryList[catName].append((groupID, name))

        sortCat = categoryList.keys()
        sortCat.sort()
        scrolllist = []
        for catName in sortCat:
            scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetCatSubContent,
             'MenuFunction': self.GetSubFolderMenu,
             'label': catName,
             'id': ('ProberScannerGroupSel', catName),
             'groupItems': categoryList[catName],
             'showlen': 1,
             'showicon': 'hide',
             'sublevel': 0,
             'state': 'locked',
             'BlockOpenWindow': 1}))

        self.cachedScrollPos = self.scroll.GetScrollProportion()
        self.scroll.Load(contentList=scrolllist, scrolltotop=0, scrollTo=getattr(self, 'cachedScrollPos', 0.0))

    def GetSubFolderMenu(self, node):
        m = [None, (localization.GetByLabel('UI/Common/SelectAll'), self.SelectGroup, (node, True)), (localization.GetByLabel('UI/Common/DeselectAll'), self.SelectGroup, (node, False))]
        return m

    def SelectGroup(self, node, isSelect):
        for groupID, label in node.groupItems:
            if groupID == const.groupCosmicSignature:
                for signatureType in const.probeScanCosmicSignatureAttributes:
                    self.tempState[groupID, signatureType] = isSelect

            else:
                self.tempState[groupID] = isSelect

        self.LoadTypes()

    def GetCatSubContent(self, nodedata, newitems = 0):
        scrolllist = []
        for groupID, groupName in nodedata.groupItems:
            if groupID == const.groupCosmicSignature:
                signatureType = groupName
                name = localization.GetByLabel(EXPLORATION_SITE_TYPES[signatureType])
                checked = self.tempState.get((groupID, signatureType), 0)
                retval = (groupID, signatureType)
            else:
                name = groupName
                checked = self.tempState.get(groupID, 0)
                retval = groupID
            scrolllist.append(GetFromClass(CheckboxEntry, {'label': name,
             'checked': checked,
             'cfgname': 'probeScannerFilters',
             'retval': retval,
             'OnChange': self.CheckBoxChange,
             'sublevel': 0}))

        return localization.util.Sort(scrolllist, key=lambda x: x.label)

    def CheckBoxChange(self, checkbox, node = None, *args):
        self.tempState[node.retval] = checkbox.checked
