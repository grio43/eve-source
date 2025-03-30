#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\ledger\ledgerPanel.py
import evetypes
import telemetry
import threadutils
import uthread
from caching.memoize import Memoize
from carbonui.button.const import HEIGHT_NORMAL
from carbonui.control.combo import Combo
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.line import Line
from carbonui.util.sortUtil import SortListOfTuples
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.dateSinglelineEdit import DateRangePicker
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.control.eveScroll import Scroll
import eve.client.script.ui.shared.ledger.ledgerUtil as ledgerUtil
from eve.client.script.ui.control.filter import OptionObject, FilterController, Filter
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from eve.client.script.ui.shared.ledger.ledgerEntry import GetLedgerEntriesPersonal, GetLedgerEntriesCorp
from eve.client.script.ui.shared.ledger.ledgerGraph import LedgerGraphCont
from eve.client.script.ui.shared.ledger.ledgerMinimap import LedgerMinimap, MiniMapSliderController
from eveservices.ledger import GetLedgerService
from localization import GetByLabel
from signals.signalUtil import ChangeSignalConnect
import blue
from utillib import KeyVal
OPTION_TYPEID = 1
OPTION_ITEMID = 2
OPTION_TYPE_GROUPINGID = 3

class LedgerPanelPersonal(Container):
    __notifyevents__ = ['OnMiningLedgerGraphSettingChanged']
    default_align = uiconst.TOALL

    def ApplyAttributes(self, attributes):
        self.filterController = None
        self.currentNormalOreGroupIDs = set()
        self.currentMoonTypeIDsByGroupID = set()
        self.currentPersonalDataVersion = -1
        Container.ApplyAttributes(self, attributes)
        addInfoIcon = attributes.addInfoIcon
        if addInfoIcon:
            self.AddMoreInfoIcon()
        self.graphParent = DragResizeCont(name='scrollCont', parent=self, align=uiconst.TOTOP_PROP, minSize=200, maxSize=0.6, defaultSize=250, settingsID='ledgerPanel_left')
        Line(parent=self.graphParent.dragArea, align=uiconst.TOBOTTOM, opacity=0.08)
        Line(parent=self.graphParent.dragArea, align=uiconst.TOTOP, opacity=0.08)
        self.bottomCont = Container(name='bottomCont', parent=self, align=uiconst.TOALL, clipChildren=True, padTop=16)
        self.filterCont = ContainerAutoSize(name='filterCont', parent=self.bottomCont, align=uiconst.TOTOP)
        self.ConstructFilterCont()
        self.scrollCont = Container(name='scrollCont', parent=self.bottomCont, align=uiconst.TOALL)
        EveLabelLarge(parent=self.scrollCont, text=GetByLabel('UI/Ledger/LogsHeader'), align=uiconst.TOTOP, padTop=8)
        self.ChangeSignalConnection()
        self.AddGraphs()
        self.AddCopyBtns()
        self.scroll = Scroll(parent=self.scrollCont, padding=(0, 4, 0, 0), id='ledgerPanelPersonal')
        self.scroll.ApplyTabstopsToNode = self.ScrollApplyTabstopsToNode
        uthread.new(self.LoadContent)
        sm.RegisterNotify(self)

    def OnTabSelect(self):
        self.LoadContent()

    def LoadContent(self):
        self.LoadOreFilter()
        self.ReloadContent()

    def ScrollApplyTabstopsToNode(self, node, fromWhere = ''):
        Scroll.ApplyTabstopsToNode(self.scroll, node, fromWhere)
        if node.panel and node.tabs:
            node.panel.UpdateLegendFillPos(node.tabs[0])

    def ConstructFilterCont(self):
        EveLabelLarge(parent=self.filterCont, text=GetByLabel('UI/Ledger/FiltersHeader'), align=uiconst.TOTOP)
        self.innerFilterCont = Container(name='innerFilterCont', parent=self.filterCont, align=uiconst.TOTOP, height=HEIGHT_NORMAL, padTop=4)
        startTime, endTime = ledgerUtil.GetMiniMapRange()
        self.sliderController = MiniMapSliderController(startTime, endTime)
        fromTime, toTime = self.sliderController.GetVisibleRange()
        labelPaths = ['UI/Ledger/DateRange', 'UI/Ledger/DateRangeTo']
        DateRangePicker(name='DateRangePicker', parent=self.innerFilterCont, pos=(150, 4, 50, 0), fromTime=fromTime, toTime=toTime, sliderController=self.sliderController, labelPaths=labelPaths)
        self.filterController = FilterController('ledgerWnd_personal_oreType', [], doSortChildren=False)
        Filter(name='oreFilter', parent=self.innerFilterCont, filterText=GetByLabel('UI/Ledger/OreTypeFilter'), filterController=self.filterController, columns=1, align=uiconst.CENTERLEFT, maxSize=300)
        EveLabelMedium(parent=self.filterCont, align=uiconst.TOTOP, text=GetByLabel('UI/Ledger/DateSelectionText'), padTop=8)
        minimapCont = Container(name='miniMapCont', parent=self.filterCont, align=uiconst.TOTOP, height=60, top=0, padTop=4)
        minimapCont.isTabStop = True
        ledgerMinimap = LedgerMinimap(parent=minimapCont, sliderController=self.sliderController)
        ledgerMinimap.LoadMiniMap(ledgerUtil.GetDataForPersonaMinimap())
        Fill(bgParent=minimapCont, color=(1, 1, 1, 0.05))

    def LoadOreFilter(self):
        data, self.currentPersonalDataVersion = GetLedgerService().GetPersonalData()
        self._LoadOreFilterData(data)

    def _LoadOreFilterData(self, data):
        options = GetOreOptionsFromData(data)
        self.filterController.SetOptions(options)

    def LoadOreFilterIfNeeded(self, data):
        normalOreGroupIDs, moonTypeIDsByGroupID = ledgerUtil.GetGroupingsForOreFromData(data)
        if self.currentNormalOreGroupIDs == normalOreGroupIDs and self.currentMoonTypeIDsByGroupID == set(moonTypeIDsByGroupID.keys()):
            return
        self.currentNormalOreGroupIDs = normalOreGroupIDs
        self.currentMoonTypeIDsByGroupID = set(moonTypeIDsByGroupID.keys())
        self._LoadOreFilterData(data)

    def AddCopyBtns(self):
        self.btnGroup = ButtonGroup(parent=self.scrollCont, idx=0)
        text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ExportToClipboard')
        self.btnGroup.AddButton(text, self.CopyToClipboard, ())

    def OnFiltersChanged(self, controller):
        self.ReloadContent()

    def AddGraphs(self):
        EveLabelLarge(parent=self.graphParent, text=GetByLabel('UI/Ledger/GraphsHeader'), align=uiconst.TOTOP)
        self.graphCont = LedgerGraphCont(parent=self.graphParent, padBottom=8)

    def OnMiningLedgerGraphSettingChanged(self):
        self.ReloadContent()

    @threadutils.throttled(0.5)
    def ReloadContent(self):
        visibleRange = self.sliderController.GetVisibleRange()
        data, personalDataVersion = GetLedgerService().GetPersonalData()
        if self.currentPersonalDataVersion != personalDataVersion:
            self.LoadOreFilterIfNeeded(data)
            self.currentPersonalDataVersion = personalDataVersion
        data = self.FilterOutData(data)
        self.LoadScroll(data, visibleRange)
        self.graphCont.UpdateGraphFromRawData(data, *visibleRange)

    def LoadScroll(self, data, visibleRange):
        contentList = GetLedgerEntriesPersonal(data, *visibleRange)
        self.scroll.Load(contentList=contentList, headers=ledgerUtil.SCROLL_HEADERS_PERSONAL, noContentHint=GetByLabel('UI/Ledger/NoLogsToShow'))

    def OnOreFilterChanged(self, *args):
        self.ReloadContent()

    def FilterOutData(self, dataList):
        newDataList = []
        for each in dataList:
            if self.IsFilteredOut(each):
                continue
            newDataList.append(each)

        return newDataList

    def IsFilteredOut(self, info):
        isFilterActive = self.filterController.IsActive()
        if not isFilterActive:
            return False
        selectedOptions = self.filterController.GetSelectedOptions()
        groupsSelected = {x[1] for x in selectedOptions if x[0] == OPTION_TYPE_GROUPINGID}
        typesSelected = filter(None, {x[1] for x in selectedOptions if x[0] == OPTION_TYPEID})
        if evetypes.GetGroupID(info.typeID) in groupsSelected or ledgerUtil.GetBasicOreForTypeID(info.typeID) in typesSelected:
            return False
        return True

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.sliderController.on_change, self.ReloadContent), (self.filterController.on_filter_changed, self.OnFiltersChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def CopyToClipboard(self, *args):
        extraColumns = [GetByLabel('UI/Ledger/OreTypeID'), GetByLabel('UI/Ledger/SolarSystemID')]
        allLines = ['\t'.join(ledgerUtil.SCROLL_HEADERS_PERSONAL + extraColumns)]
        for eachData in self.scroll.GetNodes():
            text = '\t'.join([eachData.formattedText['date'],
             eachData.formattedText['typeName'],
             unicode(eachData.formattedText['qty']),
             unicode(eachData.formattedText['qtyWasted']),
             unicode(eachData.formattedText['volume']),
             unicode(eachData.formattedText['volumeWasted']),
             unicode(eachData.formattedText['estPrice']),
             unicode(eachData.formattedText['estPriceWasted']),
             unicode(eachData.formattedText['locationName']),
             unicode(eachData.ledgerData.typeID),
             unicode(eachData.ledgerData.solarsystemID)])
            allLines.append(text)

        allText = '\r\n'.join(allLines)
        if allText:
            blue.pyos.SetClipboardData(allText)

    def AddMoreInfoIcon(self):
        moreinfoicon = MoreInfoIcon(left=2, top=-1, parent=self, idx=0, align=uiconst.TOPRIGHT)
        moreinfoicon.hint = GetByLabel('UI/Ledger/PersonalLedgerCacheHint')

    def Close(self):
        with EatSignalChangingErrors(errorMsg='LedgerPanelPersonal'):
            self.ChangeSignalConnection(connect=False)
        Container.Close(self)


class LedgerPanelCorp(Container):
    default_align = uiconst.TOALL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.oreTypeFilterController = FilterController('ledgerWnd_corp_oreType', ())
        self.corpFilterController = FilterController('ledgerWnd_corp_corp', ())
        self.filterCont = Container(parent=self, align=uiconst.TOTOP, height=30, padLeft=4, padRight=4)
        self.rangeCont = Container(parent=self, align=uiconst.TOTOP, height=70, padLeft=4, padRight=4)
        self.AddComboFilters()
        self.AddRangeSlider()
        self.AddCopyBtns()
        self.scroll = Scroll(parent=self, padding=4, id='ledgerPanelCorp')
        self.scroll.LoadContent(noContentHint=GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/FetchingData'))
        uthread.new(self.PopulateStructureCombo)
        self.ChangeSignalConnection()

    def AddComboFilters(self):
        structureOptions = []
        self.structureCombo = Combo(parent=self.filterCont, name='ledger_corp_oreFilter', options=structureOptions, prefskey='ledger_corp_oreFilter', callback=self.OnStructureChanged, align=uiconst.CENTERLEFT, width=280)
        left = self.structureCombo.left + self.structureCombo.width + 16
        self.oreFilter = Filter(name='oreFilter', parent=self.filterCont, filterText=GetByLabel('UI/Ledger/OreTypeFilter'), filterController=self.oreTypeFilterController, columns=1, align=uiconst.CENTERLEFT, left=left, maxSize=300)
        left = self.oreFilter.left + self.oreFilter.width + 16
        self.corpFilter = Filter(name='corpFilter', parent=self.filterCont, filterText=GetByLabel('UI/Ledger/CorpFilter'), filterController=self.corpFilterController, columns=1, align=uiconst.CENTERLEFT, left=left, maxSize=300)
        self.filterInput = QuickFilterEdit(name='filterInput', parent=self.filterCont, setvalue='', hintText=GetByLabel('UI/Inventory/Filter'), maxLength=64, pos=(6, 0, 100, 0), align=uiconst.CENTERRIGHT, OnClearFilter=self.LoadScroll, isCharacterField=True)
        self.filterInput.OnReturn = self.LoadScroll
        self.filterInput.ReloadFunction = self.LoadScroll

    def AddRangeSlider(self):
        startTime, endTime = ledgerUtil.GetMiniMapRange()
        self.sliderController = MiniMapSliderController(startTime, endTime)
        fromTime, toTime = self.sliderController.GetVisibleRange()
        labelPaths = ['UI/Ledger/DateRange', 'UI/Ledger/DateRangeTo']
        DateRangePicker(name='DateRangePicker', parent=self.rangeCont, fromTime=fromTime, toTime=toTime, sliderController=self.sliderController, labelPaths=labelPaths)
        minimapCont = Container(name='minimapCont', parent=self.rangeCont, align=uiconst.TOTOP, height=40, top=24)
        minimapCont.isTabStop = True
        self.ledgerMinimap = LedgerMinimap(parent=minimapCont, sliderController=self.sliderController)
        Fill(bgParent=minimapCont, color=(1, 1, 1, 0.05))

    def PopulateStructureCombo(self):
        select = settings.user.ui.Get(self.structureCombo.prefskey, None)
        structureOptions = self.GetStructureComboOptions()
        self.structureCombo.LoadOptions(structureOptions, select)
        structureIdSelected = self.structureCombo.GetValue()
        if structureIdSelected:
            self.LoadFiltersAndScroll(structureIdSelected)

    def LoadFiltersAndScroll(self, structureIdSelected):
        data = self.GetCorpData(structureIdSelected)
        self.LoadExtraFilters(data)
        self.LoadScroll()

    def AddCopyBtns(self):
        self.btnGroup = ButtonGroup(parent=self, idx=0)
        text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ExportToClipboard')
        self.btnGroup.AddButton(text, self.CopyToClipboard, ())

    def GetStructureComboOptions(self):
        allStructuresByID, allSolarSystemIDs = GetLedgerService().GetStructuresForCorpData()
        options = []
        for eachItemID, eachItemInfo in allStructuresByID.iteritems():
            name = eachItemInfo.itemName
            options.append((name.lower(), (name, eachItemID)))

        options = SortListOfTuples(options)
        return options

    def LoadExtraFilters(self, data):
        allCorps, allCharIDs = ledgerUtil.GetGroupsForData(data)
        toPrime = allCorps.union(allCharIDs.union(allCorps))
        cfg.eveowners.Prime(toPrime)
        corpOptions = [ (cfg.eveowners.Get(x).name, x) for x in allCorps ]
        corpOptions.sort(key=lambda x: x[0])
        oreFilterOptions = GetOreOptionsFromData(data)
        self.oreTypeFilterController.SetOptions(oreFilterOptions)
        corpFilterOptions = [ OptionObject(cfg.eveowners.Get(corpID).name, corpID, OPTION_ITEMID) for corpID in allCorps ]
        self.corpFilterController.SetOptions(corpFilterOptions)

    def GetCorpData(self, structureID):
        data = GetLedgerService().GetCorpData(structureID)
        return data

    def LoadScroll(self):
        structureID = self.structureCombo.GetValue()
        self.ledgerMinimap.LoadMiniMap(ledgerUtil.GetDataForCorpMinimap(structureID))
        data = self.GetCorpData(structureID)
        data = self.FilterOutData(data)
        filterText = self.filterInput.GetValue()
        contentList = GetLedgerEntriesCorp(data, filterText.lower())
        self.scroll.Load(contentList=contentList, headers=ledgerUtil.SCROLL_HEADERS_CORP, noContentHint=GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/FiltersReturnedNoResults'))
        self.scroll.HideLoading()

    def OnSliderChanged(self):
        self.scroll.ShowLoading()
        uthread.new(self.ReloadContent)

    @threadutils.throttled(1.0)
    def ReloadContent(self):
        self.LoadScroll()

    def OnStructureChanged(self, combo, key, structureID):
        settings.user.ui.Set(combo.prefskey, structureID)
        self.LoadFiltersAndScroll(structureID)

    def OnMainFilterChanged(self, *args):
        self.LoadScroll()

    @telemetry.ZONE_METHOD
    def FilterOutData(self, dataList):
        fromTime, toTime = self.sliderController.GetVisibleRange()
        selectedOreOptions = self.oreTypeFilterController.GetSelectedOptions()
        oreTypeIDs = [ x[1] for x in selectedOreOptions if x[0] == OPTION_TYPEID ]
        oreGroupIDs = {x[1] for x in selectedOreOptions if x[0] == OPTION_TYPE_GROUPINGID}
        filterInfo = KeyVal(oreTypeIDs=oreTypeIDs, oreGroupIDs=oreGroupIDs, corpIDs=[ x[1] for x in self.corpFilterController.GetSelectedOptions() ], oreActive=self.oreTypeFilterController.IsActive(), corpActive=self.corpFilterController.IsActive(), fromTime=fromTime, toTime=toTime)
        newDataList = []
        for each in dataList:
            if self.IsFilteredOut(each, filterInfo):
                continue
            newDataList.append(each)

        return newDataList

    @telemetry.ZONE_METHOD
    def IsFilteredOut(self, info, filterInfo):
        if not ledgerUtil.IsInRange(info.eventDate, filterInfo.fromTime, filterInfo.toTime):
            return True
        if not filterInfo.oreActive and not filterInfo.corpActive:
            return False
        if filterInfo.corpActive and info.corporationID not in filterInfo.corpIDs:
            return True
        if filterInfo.oreActive and self._IsOreTypeFilteredOut(info.typeID, filterInfo):
            return True
        return False

    def _IsOreTypeFilteredOut(self, typeID, filterInfo):
        if typeID in filterInfo.oreTypeIDs:
            return False
        if _GetGroupID(typeID) in filterInfo.oreGroupIDs:
            return False
        if _GetBasicOreForTypeID(typeID) in filterInfo.oreTypeIDs:
            return False
        return True

    def OnTabSelect(self):
        self.PopulateStructureCombo()
        self.LoadScroll()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.oreTypeFilterController.on_filter_changed, self.OnMainFilterChanged), (self.corpFilterController.on_filter_changed, self.OnMainFilterChanged), (self.sliderController.on_change, self.OnSliderChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def CopyToClipboard(self, *args):
        extraColumns = [GetByLabel('UI/Ledger/OreTypeID'), GetByLabel('UI/Ledger/SolarSystemID')]
        allLines = ['\t'.join(ledgerUtil.SCROLL_HEADERS_CORP + extraColumns)]
        for eachData in self.scroll.GetNodes():
            text = '\t'.join([eachData.formattedText['date'],
             eachData.formattedText['corpName'],
             eachData.formattedText['charName'],
             eachData.formattedText['typeName'],
             unicode(eachData.formattedText['qty']),
             unicode(eachData.formattedText['volume']),
             unicode(eachData.formattedText['estPrice']),
             unicode(eachData.ledgerData.typeID),
             unicode(eachData.ledgerData.solarsystemID)])
            allLines.append(text)

        allText = '\r\n'.join(allLines)
        if allText:
            blue.pyos.SetClipboardData(allText)

    def Close(self):
        with EatSignalChangingErrors(errorMsg='LedgerPanelCorp'):
            self.ChangeSignalConnection(connect=False)
        Container.Close(self)


def GetOreOptionsFromData(data):
    normalOreGroupIDs, moonTypeIDsByGroupID = ledgerUtil.GetGroupingsForOreFromData(data)
    moonOptions = []
    for moonGroupID, typeIDs in moonTypeIDsByGroupID.iteritems():
        basicTypeIDs = {ledgerUtil.GetBasicOreForTypeID(x) for x in typeIDs}
        subOptions = [ OptionObject(evetypes.GetName(x), x, OPTION_TYPEID) for x in basicTypeIDs ]
        moonOptions.append(OptionObject(evetypes.GetGroupNameByGroup(moonGroupID), moonGroupID, OPTION_TYPE_GROUPINGID, subOptions))

    moonOptions.sort(key=lambda x: x.value)
    normalOptions = [ OptionObject(evetypes.GetGroupNameByGroup(x), x, OPTION_TYPE_GROUPINGID) for x in normalOreGroupIDs ]
    normalOptions.sort(key=lambda x: x.name)
    options = moonOptions + normalOptions
    return options


@Memoize(1)
def _GetGroupID(typeID):
    return evetypes.GetGroupID(typeID)


@Memoize(1)
def _GetBasicOreForTypeID(typeID):
    return ledgerUtil.GetBasicOreForTypeID(typeID)
