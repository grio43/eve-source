#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\ledger\ledgerGraph.py
from carbonui.primitives.frame import Frame
from collections import defaultdict, OrderedDict
import evetypes
from caching.memoize import Memoize
from carbon.common.script.util.format import FmtAmt, GetTimeParts, FmtDate
from carbonui import TextColor
from carbonui.graphs.axislabels import AxisLabels
from carbonui.graphs.graph import GraphArea
from carbonui.graphs.bargraph import BarGraph, DynamicHint
from carbonui.graphs.linegraph import LineGraph
from carbonui.graphs.pointgraph import PointGraph
from carbonui.graphs.pool import Pool
from carbonui.primitives.container import Container
import carbonui.graphs.axis as axis
import carbonui.const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveCaptionSmall, EveLabelMedium
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.shared.ledger.ledgerUtil import IsInRange, GetMaxDayTimeStamp, GetColorForBaseTypeID, GetColorsForTypeIDs, REST_ORE, GetMetaLevelByTypeID
from eve.common.script.util.eveFormat import FmtISK
from eveservices.menu import GetMenuService
from inventorycommon.typeHelpers import GetAveragePrice
from localization import GetByLabel
MAX_LINES = 15
MAX_BARS = 15
GRAPH_DISPLAY_UNITS_QTY = 1
GRAPH_DISPLAY_UNITS_VOLUME = 2
GRAPH_DISPLAY_UNITS_PRICE = 3
DEFAULT_DISPLAY_UNIT = GRAPH_DISPLAY_UNITS_QTY
SETTING_NAME_BARGRAPH = 'ledger_barGraph_displayUnits'
SETTING_NAME_POINTGRAPH = 'ledger_pointGraph_displayUnits'
DISPLAY_UNIT_TEXTS = {GRAPH_DISPLAY_UNITS_QTY: 'UI/Ledger/DisplayUnitQty',
 GRAPH_DISPLAY_UNITS_VOLUME: 'UI/Ledger/DisplayUnitVolume',
 GRAPH_DISPLAY_UNITS_PRICE: 'UI/Ledger/DisplayUnitPrice'}

class LedgerGraphCont(Container):
    __notifyevents__ = ['OnLedgerMouseOverChanged']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.barGraph = None
        self.lineAndPointGraphsByTypeID = {}
        self.currentLineHilite = None
        self.leftCont = Container(name='leftCont', parent=self, align=uiconst.TOLEFT_PROP, width=0.5)
        self.leftInnerCont = Container(name='leftInnerCont', parent=self.leftCont, align=uiconst.TOALL)
        self.rightCont = Container(name='rightCont', parent=self, align=uiconst.TORIGHT_PROP, width=0.5)
        self.rightInnerCont = Container(name='rightInnerCont', parent=self.rightCont, align=uiconst.TOALL)
        self.AddLabelsAndSettings()
        sm.RegisterNotify(self)

    def AddLabelsAndSettings(self):
        self.ConstructLeftContHeader()
        self.UpdateTotalOreLabel()
        self.ConstructRightContHeader()
        self.UpdateOreByDayLabel()

    def ConstructLeftContHeader(self):
        topCont = ContainerAutoSize(name='topCont', align=uiconst.TOTOP, parent=self.leftCont, idx=0, padTop=10)
        self.totalOreLabel = EveCaptionSmall(parent=topCont, text='', align=uiconst.CENTERLEFT, left=50)
        UtilMenu(parent=topCont, align=uiconst.CENTERLEFT, GetUtilMenu=self.SettingsMenuForBarGraph, texturePath='res:/UI/Texture/SettingsCogWheel.png', opacity=TextColor.NORMAL.opacity, left=25)

    def ConstructRightContHeader(self):
        topCont = ContainerAutoSize(name='topCont', align=uiconst.TOTOP, parent=self.rightCont, idx=0, padTop=10)
        self.oreByDayLabel = EveCaptionSmall(parent=topCont, align=uiconst.CENTERLEFT, left=50)
        UtilMenu(parent=topCont, align=uiconst.CENTERLEFT, GetUtilMenu=self.SettingsMenuForPointGraph, texturePath='res:/UI/Texture/SettingsCogWheel.png', opacity=TextColor.NORMAL.opacity, left=25)

    def UpdateOreByDayLabel(self):
        pointGraphDisplayUnits = GetSetting(SETTING_NAME_POINTGRAPH, DEFAULT_DISPLAY_UNIT)
        pointGraphLabel = DISPLAY_UNIT_TEXTS.get(pointGraphDisplayUnits, None)
        pointGraphLabel = ' (%s)' % GetByLabel(pointGraphLabel) if pointGraphLabel else ''
        self.oreByDayLabel.text = GetByLabel('UI/Ledger/GraphHeaderOreByDay') + pointGraphLabel

    def UpdateTotalOreLabel(self):
        barGraphDisplayUnits = GetSetting(SETTING_NAME_BARGRAPH, DEFAULT_DISPLAY_UNIT)
        barGraphLabel = DISPLAY_UNIT_TEXTS.get(barGraphDisplayUnits, None)
        barGraphLabel = ' (%s)' % GetByLabel(barGraphLabel) if barGraphLabel else ''
        self.totalOreLabel.text = GetByLabel('UI/Ledger/GraphHeaderTotalOre') + barGraphLabel

    def SettingsMenuForBarGraph(self, menuParent):
        return self.SettingsMenuForGraph(menuParent, SETTING_NAME_BARGRAPH)

    def SettingsMenuForPointGraph(self, menuParent):
        return self.SettingsMenuForGraph(menuParent, SETTING_NAME_POINTGRAPH)

    def SettingsMenuForGraph(self, menuParent, settingName):
        for settingValue, labelPath in ((GRAPH_DISPLAY_UNITS_QTY, 'UI/Ledger/DisplayUnitQty'), (GRAPH_DISPLAY_UNITS_VOLUME, 'UI/Ledger/DisplayUnitVolume'), (GRAPH_DISPLAY_UNITS_PRICE, 'UI/Ledger/DisplayUnitPrice')):
            isChecked = GetSetting(settingName, DEFAULT_DISPLAY_UNIT) == settingValue
            menuParent.AddRadioButton(text=GetByLabel(labelPath), checked=isChecked, callback=(self.OnSettingChanged, settingName, settingValue))

    def OnSettingChanged(self, settingName, configName):
        SetSetting(settingName, configName)
        sm.ScatterEvent('OnMiningLedgerGraphSettingChanged')
        self.UpdateTotalOreLabel()
        self.UpdateOreByDayLabel()

    def UpdateGraphFromRawData(self, rawData, start, stop):
        self.leftInnerCont.Flush()
        self.rightInnerCont.Flush()
        displayUnits = GetSetting(SETTING_NAME_BARGRAPH, DEFAULT_DISPLAY_UNIT)
        oreByTypeIDOrdered = GetGroupDataToOreType(rawData, start, stop, MAX_BARS, displayUnits)
        self.LoadBarGraph(oreByTypeIDOrdered, displayUnits)
        self.LoadPointGraph(rawData, start, stop)

    def LoadBarGraph(self, oreByTypeIDOrdered, displayUnits):
        data = [ v for v in oreByTypeIDOrdered.itervalues() ]
        if not oreByTypeIDOrdered:
            EveLabelMedium(parent=self.leftInnerCont, text='<center>%s</center>' % GetByLabel('UI/Ledger/NoDataToDisplay'), idx=0, align=uiconst.TOTOP, top=20)
            return
        yMin, yMax, xNum = self.GetGraphRanges(data)
        graphArea, horizontalAxis, verticalAxis = self.GetCommonGraphElements(self.leftInnerCont, yMin, yMax, oreByTypeIDOrdered.items(), True)
        indexByTypeID = {typeID:i for i, typeID in enumerate(oreByTypeIDOrdered.keys())}

        def getHint(barIdx):
            typeID = oreByTypeIDOrdered.keys()[barIdx]
            value = data[barIdx]
            return GetTextForHint(typeID, value, displayUnits)

        colors = GetColorsForTypeIDs(oreByTypeIDOrdered.keys())
        self.barGraph = BarGraph(parent=graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=data, color=(0.9, 0.7, 0.3, 0.7), lineWidth=1, hint=DynamicHint(getHint), barSize=20, barColors=colors, barSizeMinMax=(10, 60))
        self.barGraph.indexByTypeID = indexByTypeID

    def GetGraphRanges(self, data):
        _, yMax = axis.GetRangeFromSequences(data)
        yMin = 0
        xNum = len(data)
        return (yMin, yMax, xNum)

    def GetCommonGraphElements(self, parent, yMin, yMax, data, showHorizontalAxis = False):
        main = Container(name='mainGraphContainer', parent=parent, align=uiconst.TOALL)
        verticalAxis = axis.AutoTicksAxis((yMin, yMax), tickCount=5, margins=(0.1, 0.1), behavior=axis.AXIS_FROM_ZERO)
        verticalAxis.GetTickLabel = self.GetTickLabel
        horizontalAxis = axis.CategoryAxis(data, labelFormat=int)
        xAxisHeight = 32
        AxisLabels(parent=main, align=uiconst.TOLEFT, width=50, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0, padBottom=xAxisHeight)
        axisCont = Container(parent=main, align=uiconst.TOBOTTOM, height=xAxisHeight)
        if showHorizontalAxis:
            AxisIcons(parent=axisCont, align=uiconst.TOBOTTOM, height=xAxisHeight, axis=horizontalAxis, orientation=axis.AxisOrientation.HORIZONTAL, minFactor=0.0, maxFactor=1.0)
        graphArea = GraphArea(name='graph', parent=main, align=uiconst.TOALL, clipChildren=False)
        Fill(bgParent=graphArea, padBottom=-4, color=(0.0, 0.0, 0.0, 0.3))
        Frame(bgParent=graphArea, padBottom=-4, color=(0.5, 0.5, 0.5, 0.2))
        graphArea.minLabel = EveLabelSmall(parent=graphArea, align=uiconst.BOTTOMLEFT, top=-18)
        graphArea.maxLabel = EveLabelSmall(parent=graphArea, align=uiconst.BOTTOMRIGHT, top=-18)
        graphArea.AddAxis(axis.AxisOrientation.VERTICAL, verticalAxis, 1.0, 0.0)
        graphArea.AddAxis(axis.AxisOrientation.HORIZONTAL, horizontalAxis)
        return (graphArea, horizontalAxis, verticalAxis)

    def LoadPointGraph(self, rawData, startTimestamp, endTimeStamp):
        endTimeStamp = GetMaxDayTimeStamp(endTimeStamp)
        dataByTypeID = defaultdict(list)
        for eachData in rawData:
            dataByTypeID[eachData.typeID].append(eachData)

        graphArea = None
        self.lineAndPointGraphsByTypeID.clear()
        displayUnits = GetSetting(SETTING_NAME_POINTGRAPH, DEFAULT_DISPLAY_UNIT)
        topOreTypes = GetGroupDataToOreType(rawData, startTimestamp, endTimeStamp, MAX_LINES, displayUnits)

        def HintFunc(data, oreTypeID):

            def getHint(barIdx):
                value = data[barIdx]
                return GetTextForHint(oreTypeID, value, displayUnits)

            return getHint

        maxYValue = 0
        qtyByDayOrderedByOreTypeID = defaultdict(dict)
        for oreTypeID in topOreTypes:
            if oreTypeID == REST_ORE:
                continue
            dataForType = dataByTypeID.get(oreTypeID, [])
            qtyByDayOrdered = GetNumByDay(dataForType, startTimestamp, endTimeStamp, displayUnits)
            qtyByDayOrderedByOreTypeID[oreTypeID] = qtyByDayOrdered
            maxYValue = max(maxYValue, max((x for x in qtyByDayOrdered.itervalues())))

        dataToMakeLineGraph = []
        for oreTypeID in topOreTypes:
            qtyByDayOrdered = qtyByDayOrderedByOreTypeID.get(oreTypeID)
            if not qtyByDayOrdered:
                continue
            data = qtyByDayOrdered.values()
            if graphArea is None:
                yMin, yMax, xNum = self.GetGraphRanges(data)
                graphArea, horizontalAxis, verticalAxis = self.GetCommonGraphElements(self.rightInnerCont, 0, maxYValue, range(0, xNum))
            color = GetColorForBaseTypeID(oreTypeID)
            pointGraph = PointGraph(parent=graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=data, pointColor=color, pointSize=4, hint=DynamicHint(HintFunc(data, oreTypeID)), hideZero=True)
            dataForLineGraph = (oreTypeID,
             data,
             color,
             pointGraph)
            dataToMakeLineGraph.append(dataForLineGraph)

        for eachOreTypeID, eachData, eachColor, eachPointGraph in dataToMakeLineGraph:
            lineGraph = LineGraph(parent=graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=eachData, color=eachColor, lineWidth=1, state=uiconst.UI_NORMAL)
            lineGraph.OnMouseEnter = (self.OnLineGraphEnter, lineGraph, eachPointGraph)
            lineGraph.OnMouseExit = (self.OnLineGraphExit, lineGraph, eachPointGraph)
            eachPointGraph.OnMouseEnter = (self.OnPointGraphEnter, lineGraph, eachPointGraph)
            eachPointGraph.OnMouseExit = (self.OnPointGraphExit, lineGraph, eachPointGraph)
            lineGraph.hint = evetypes.GetName(eachOreTypeID)
            lineGraph.GetTooltipPosition = lambda *args: self.GetTooltipPosition()
            self.lineAndPointGraphsByTypeID[eachOreTypeID] = (lineGraph, eachPointGraph)

        if graphArea:
            graphArea.minLabel.text = FmtDate(startTimestamp, 'ln')
            graphArea.maxLabel.text = FmtDate(endTimeStamp, 'ln')
        else:
            EveLabelMedium(parent=self.rightInnerCont, text='<center>%s</center>' % GetByLabel('UI/Ledger/NoDataToDisplay'), idx=0, align=uiconst.TOTOP, top=20)

    def GetTooltipPosition(self, *args):
        from carbonui.uicore import uicore
        return (uicore.uilib.x - 5,
         uicore.uilib.y - 5,
         10,
         10)

    def OnLineGraphEnter(self, lineGraph, pointGraph, *args):
        LineGraph.OnMouseEnter(lineGraph, *args)
        self.ChangeLineOpacity(lineGraph, pointGraph, highlighted=True)

    def OnLineGraphExit(self, lineGraph, pointGraph, *args):
        LineGraph.OnMouseExit(lineGraph, *args)
        self.ChangeLineOpacity(lineGraph, pointGraph, highlighted=False)

    def OnPointGraphEnter(self, lineGraph, pointGraph, *args):
        PointGraph.OnMouseEnter(pointGraph, *args)
        self.ChangeLineOpacity(lineGraph, pointGraph, highlighted=True)

    def OnPointGraphExit(self, lineGraph, pointGraph, *args):
        PointGraph.OnMouseExit(pointGraph, *args)
        self.ChangeLineOpacity(lineGraph, pointGraph, highlighted=False)

    def ChangeLineOpacity(self, lineGraph, pointGraph, highlighted = False):
        if highlighted:
            opacity = 2.0
        else:
            opacity = 1.0
        lineGraph.opacity = opacity
        pointGraph.opacity = opacity

    def OnLedgerMouseOverChanged(self, typeID):
        if self.barGraph:
            barIdx = self.barGraph.indexByTypeID.get(typeID)
            if barIdx is None:
                self.barGraph._RemoveBarHighlight()
            else:
                self.barGraph.AddBarHighlight(barIdx)
        if typeID:
            typeIDToChange = typeID
            doHilite = True
        else:
            typeIDToChange = self.currentLineHilite
            doHilite = False
        if typeIDToChange:
            lineGraph, pointGraph = self.lineAndPointGraphsByTypeID.get(typeIDToChange, (None, None))
            if lineGraph and pointGraph:
                self.ChangeLineOpacity(lineGraph, pointGraph, doHilite)
                self.currentLineHilite = typeID

    def GetTickLabel(self, tick):
        if tick < 1000:
            return int(tick)
        return FmtAmt(tick, fmt='sn', showFraction=0)


def GetNumByDay(allData, startTimestamp, endTimeStamp, graphType = DEFAULT_DISPLAY_UNIT):
    qtyByDay = defaultdict(int)
    for eachData in allData:
        year, month, wd, day, hour, minutes, sec, ms = GetTimeParts(eachData.eventDate)
        dataKey = (year, month, day)
        qtyByDay[dataKey] += GetNumToTrack(eachData, graphType)

    dataInOrder = OrderedDict()
    currentTimestamp = startTimestamp
    counter = 0
    while currentTimestamp < endTimeStamp and counter < 1000:
        year, month, wd, day, hour, minutes, sec, ms = GetTimeParts(currentTimestamp)
        dataKey = (year, month, day)
        value = qtyByDay.get(dataKey, 0)
        dataInOrder[dataKey] = value
        currentTimestamp += const.DAY
        counter += 1

    return dataInOrder


def GetGroupDataToOreType(allData, start = None, end = None, numToGet = None, graphType = DEFAULT_DISPLAY_UNIT):
    qtyByOreTypeID = defaultdict(int)
    for eachData in allData:
        isInRange = IsInRange(eachData.eventDate, start, end)
        if not isInRange:
            continue
        qtyByOreTypeID[eachData.typeID] += GetNumToTrack(eachData, graphType)

    qtyAndOreTypeIDList = qtyByOreTypeID.items()
    qtyAndOreTypeIDList.sort(key=lambda x: (x[1], -GetMetaLevelByTypeID(x[0])), reverse=True)
    if numToGet:
        topOre = qtyAndOreTypeIDList[:numToGet]
        rest = qtyAndOreTypeIDList[numToGet:]
        restQty = sum((x[1] for x in rest))
    else:
        topOre = qtyAndOreTypeIDList
        restQty = 0
    oreByTypeIDOrdered = OrderedDict(topOre)
    if restQty:
        oreByTypeIDOrdered[REST_ORE] = restQty
    return oreByTypeIDOrdered


def GetNumToTrack(eachData, graphType):
    if graphType == GRAPH_DISPLAY_UNITS_QTY:
        return eachData.quantity
    if graphType == GRAPH_DISPLAY_UNITS_VOLUME:
        return eachData.quantity * GetTypeVolume(eachData.typeID)
    if graphType == GRAPH_DISPLAY_UNITS_PRICE:
        return eachData.quantity * GetPrice(eachData.typeID)
    return 0


def GetTextForHint(typeID, value, displayUnits):
    if typeID == REST_ORE:
        oreName = GetByLabel('UI/Ledger/OtherOre')
    else:
        oreName = evetypes.GetName(typeID)
    if displayUnits == GRAPH_DISPLAY_UNITS_QTY:
        fmtValue = FmtAmt(value)
    if displayUnits == GRAPH_DISPLAY_UNITS_VOLUME:
        fmtValue = GetByLabel('UI/Moonmining/NumM3', amount=FmtAmt(value))
    if displayUnits == GRAPH_DISPLAY_UNITS_PRICE:
        fmtValue = FmtISK(value, showFractionsAlways=0)
    return '%s<br>%s' % (oreName, fmtValue)


@Memoize(1)
def GetTypeVolume(typeID):
    return evetypes.GetVolume(typeID)


@Memoize(1)
def GetPrice(typeID):
    price = GetAveragePrice(typeID) or evetypes.GetBasePrice(typeID) or 0
    return price


def SetSetting(settingName, configName):
    settings.user.ui.Set(settingName, configName)


def GetSetting(settingName, defaultValue):
    return settings.user.ui.Get(settingName, defaultValue)


class AxisIcons(AxisLabels):

    def CreatePools(self):
        self._label_pool = Pool(Icon)
        self._container_pool = Pool(Container)

    def AddLabel(self, cont, tick):
        cont.padding = (0, 0, 0, 0)
        icon = self._label_pool.get_instance()
        typeID, value = self._axis.GetDataPoints()[tick]
        if typeID > -1:
            cont.state = uiconst.UI_NORMAL
            icon.SetParent(cont)
            icon.state = uiconst.UI_NORMAL
            icon.SetAlign(uiconst.CENTERTOP)
            icon.SetSize(32, 32)
            icon.LoadIconByTypeID(typeID=typeID)
            icon.GetHint = lambda *args: GetTextForHint(typeID, value, GetSetting(SETTING_NAME_BARGRAPH, DEFAULT_DISPLAY_UNIT))
            icon.GetMenu = lambda *args: GetMenuService().GetMenuFromItemIDTypeID(None, typeID=typeID)
        return icon
