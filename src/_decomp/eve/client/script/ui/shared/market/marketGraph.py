#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\marketGraph.py
from carbon.common.script.util.format import FmtDate, FmtAmt
import carbonui.const as uiconst
from carbonui import ButtonVariant, Density
from carbonui.primitives.container import Container
from carbonui.control.button import Button
from carbonui.graphs.minimap import MiniMap
from carbonui.graphs.pointgraph import PointGraph
from carbonui.graphs.donchianchannel import DonchianChannel
from carbonui.graphs import axis, axislabels, graph
from carbonui.graphs.lowhighvaluegraph import LowHighValueGraph
from carbonui.graphs.graphsutil import MovingAvg
from carbonui.graphs.linegraph import LineGraph
from carbonui.graphs.bargraph import BarGraph, DynamicHint
from carbonui.graphs.areagraph import AreaGraph
from carbonui.graphs.grid import Grid
from carbonui.graphs.legend import Legend
from carbonui.graphs import animations
import localization
from eve.client.script.ui.control.utilMenu import UtilMenu
_cachedRange = ()
graphColors = ((0.0, 0.247, 0.31, 1.0),
 (0.098, 0.4, 0.479, 1.0),
 (0.082, 0.663, 0.812, 1.0),
 (0.569, 0.275, 0.0, 1.0),
 (0.812, 0.435, 0.082, 1.0))
TOP_AXIS_HEIGHT = 30
LEFT_AXIS_WIDTH = 70
RIGHT_AXIS_WIDTH = 50

def _GetSetting(name, default):
    return settings.user.ui.Get('market_setting_%s' % name, default)


def _SetSetting(name, value):
    settings.user.ui.Set('market_setting_%s' % name, value)


def _OnAnimationCheckbox():
    curr = _GetSetting('animations', 1)
    _SetSetting('animations', not curr)


def _FormatAmount(x):
    if abs(x) < 100:
        return FmtAmt(x, 'ln', 1)
    try:
        return FmtAmt(x, 'sn')
    except:
        return ''


class MarketGraph(Container):
    default_state = uiconst.UI_ACTIVE
    default_zoom = 30

    def ApplyAttributes(self, attributes):
        global _cachedRange
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.get('typeID', None)
        self.data = attributes.get('data', None)
        count = len(self.data)
        self.zoom = attributes.get('zoom', None)
        if self.zoom is None:
            self.zoom = _GetSetting('dateRange', self.default_zoom)
        self.zoom = min(self.zoom, count)
        if _cachedRange:
            timeRange = _cachedRange
            if timeRange[1] > count:
                timeRange = (count - self.zoom - 0.5, count - 0.5)
        else:
            timeRange = (count - self.zoom - 0.5, count - 0.5)
        self.resetZoomBtn = Button(name='resetZoom', label=localization.GetByLabel('UI/Market/PriceHistory/ResetAxis'), parent=self, align=uiconst.CENTERTOP, func=self._ResetAutoZoom, density=Density.COMPACT, variant=ButtonVariant.GHOST)
        self.topAxisContainer = Container(parent=self, name='TopAxisContainer', align=uiconst.TOTOP, height=TOP_AXIS_HEIGHT)
        self.miniMapContainer = Container(parent=self, name='MinimapContainer', align=uiconst.TOBOTTOM, height=60)
        self.leftAxisContainer = Container(parent=self, name='LeftAxisContainer', align=uiconst.TOLEFT, width=LEFT_AXIS_WIDTH)
        self.rightAxisContainer = Container(parent=self, name='RightAxisContainer', align=uiconst.TORIGHT, width=RIGHT_AXIS_WIDTH)
        self.leftAxis = axis.AutoTicksAxis(self._GetLeftAxisData(), tickCount=10, margins=(0.4, 0.15), tickFilter=lambda t: t >= 0, labelFormat=_FormatAmount)
        self.rightAxis = axis.AutoTicksAxis(self._GetRightAxisData(), behavior=axis.AXIS_FROM_ZERO, tickCount=4, labelFormat=_FormatAmount)
        self.topAxis = axis.MonthlyTimeAxis([ x[0] for x in self.data ], visibleRange=timeRange, behavior=axis.AXIS_CUSTOM, interactionLimit=axis.InteractionLimit.DATA_RANGE)
        self.graphArea = graph.GraphArea(parent=self, name='GraphArea')
        self.graphArea.AddAxis(axis.AxisOrientation.HORIZONTAL, self.topAxis)
        self.graphArea.AddAxis(axis.AxisOrientation.VERTICAL, self.leftAxis, 1.0, 0.0)
        self.graphArea.AddAxis(axis.AxisOrientation.VERTICAL, self.rightAxis, 1.0, 0.7)
        self.graphArea.AddZoomAxis(self.leftAxis)
        self.graphArea.AddPanAxis(self.leftAxis)
        self.graphArea.AddPanAxis(self.topAxis)
        if _GetSetting('scale_to_data', 1) and self.leftAxis.GetBehavior() != axis.AXIS_CUSTOM:
            self.leftAxis.ZoomOn(self._GetLeftAxisData(True))
            self.rightAxis.ZoomOn(self._GetRightAxisData(True))
        self.median = None
        self.donchian = None
        self.lowHigh = None
        self.movingAvg5 = None
        self.movingAvg20 = None
        self.barGraph = None
        self._isPanning = False
        self._prevPanPosition = (0, 0)
        self._ajustZoomToVisible = _GetSetting('scale_to_data', 1)
        if len(self.data) < 1:
            return
        self.Build(_GetSetting('animations', 1))
        self.leftAxis.onChange.connect(self._LeftAxisChanged)
        self.topAxis.onChange.connect(self._TopAxisChanged)

    def _OnScaleToDataCheckbox(self):
        curr = _GetSetting('scale_to_data', 1)
        _SetSetting('scale_to_data', not curr)
        if _GetSetting('scale_to_data', 1):
            if self.leftAxis.GetBehavior() != axis.AXIS_CUSTOM:
                self.leftAxis.ZoomOn(self._GetLeftAxisData(True))
            self.rightAxis.ZoomOn(self._GetRightAxisData(True))
        else:
            self.leftAxis.ZoomOn(None)
            self.rightAxis.ZoomOn(None)

    def _OnLegendCheckbox(self):
        curr = _GetSetting('legend', 1)
        _SetSetting('legend', not curr)
        if _GetSetting('legend', 1):
            if not self.legend:
                self.legend = Legend(parent=self, align=uiconst.TOTOP, autoHeight=True, centerContent=True, contentSpacing=(6, 6))
            self._RebuildLegend()
        elif self.legend:
            self.legend.Close()
            self.legend = None

    def _OnGraphCheckbox(self, name):
        curr = _GetSetting(name, 1)
        _SetSetting(name, not curr)
        self.leftAxis.SetDataRange(self._GetLeftAxisData(False))
        self.rightAxis.SetDataRange(self._GetRightAxisData(False))
        if name == 'movingavg5':
            self.AddMovingAverage5()
        elif name == 'movingavg20':
            self.AddMovingAverage20()
        elif name == 'donchian':
            self.AddDonchianChannel()
        elif name == 'mediandayprice':
            self.AddMedianPoints()
        elif name == 'minmax':
            self.AddMinMaxGraph()
        elif name == 'volume':
            self.AddBarGraph()
        self._RebuildLegend()

    def GetGraphMenu(self, menuParent):
        avg5 = localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantityShort/Day', value=5)
        avg20 = localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantityShort/Day', value=20)
        GetLabel = localization.GetByLabel
        PRICE_FILTERS = [('movingavg5', GetLabel('UI/Market/PriceHistory/ShowMovingAvg', numDays=avg5)),
         ('movingavg20', GetLabel('UI/Market/PriceHistory/ShowMovingAvg', numDays=avg20)),
         ('donchian', GetLabel('UI/Market/PriceHistory/ShowDonchianChannel')),
         ('mediandayprice', GetLabel('UI/Market/PriceHistory/ShowMedianDayPrice')),
         ('minmax', GetLabel('UI/Market/PriceHistory/ShowMinMax')),
         ('volume', GetLabel('UI/Market/PriceHistory/ShowVolume'))]
        menuParent.AddCheckBox(text=GetLabel('UI/Market/PriceHistory/ShowAnimations'), checked=_GetSetting('animations', 1), callback=_OnAnimationCheckbox)
        menuParent.AddCheckBox(text=GetLabel('UI/Market/PriceHistory/ScaleToData'), checked=_GetSetting('scale_to_data', 1), callback=self._OnScaleToDataCheckbox)
        menuParent.AddSpace()
        for settingName, label in PRICE_FILTERS:
            menuParent.AddCheckBox(text=label, checked=_GetSetting(settingName, 1), callback=(self._OnGraphCheckbox, settingName))

        menuParent.AddCheckBox(text=GetLabel('UI/Market/PriceHistory/ShowLegend'), checked=_GetSetting('legend', 1), callback=self._OnLegendCheckbox)

    def Build(self, animate = False):
        self.topAxisLabels = axislabels.AxisLabels(parent=self.topAxisContainer, align=uiconst.TOTOP, axis=self.topAxis, orientation=axis.AxisOrientation.HORIZONTAL, padding=(LEFT_AXIS_WIDTH,
         0,
         RIGHT_AXIS_WIDTH,
         0), height=TOP_AXIS_HEIGHT, textAlignment=uiconst.CENTERBOTTOM)
        self.leftAxisLabels = axislabels.AxisLabels(parent=self.leftAxisContainer, axis=self.leftAxis, orientation=axis.AxisOrientation.VERTICAL, align=uiconst.TOLEFT, width=LEFT_AXIS_WIDTH, minFactor=1.0, maxFactor=0.0, hints=True)
        self.rightAxisLabels = axislabels.AxisLabels(parent=self.rightAxisContainer, axis=self.rightAxis, orientation=axis.AxisOrientation.VERTICAL, textAlignment=uiconst.BOTTOMLEFT, align=uiconst.TOBOTTOM_PROP, height=0.3, width=self.rightAxisContainer.width, minFactor=1.0, maxFactor=0.0, hints=True)
        if _GetSetting('legend', 1):
            self.legend = Legend(parent=self, align=uiconst.TOTOP, autoHeight=True, centerContent=True, contentSpacing=(6, 6))
        else:
            self.legend = None
        self.AddMiniMap()
        self.AddMedianPoints(animate)
        self.AddMinMaxGraph()
        self.AddMovingAverage5()
        self.AddMovingAverage20()
        self.AddDonchianChannel()
        self.AddGrid()
        self.AddBarGraph(animate)
        if self.legend:
            self._RebuildLegend()
        self.utilMenu = UtilMenu(menuAlign=uiconst.TOPLEFT, parent=self, align=uiconst.TOPRIGHT, GetUtilMenu=self.GetGraphMenu, texturePath='res:/UI/Texture/SettingsCogwheel.png', top=4, width=18, height=18, iconSize=18)
        self.resetZoomBtn.display = self.leftAxis.GetBehavior() == axis.AXIS_CUSTOM

    def _ResetAutoZoom(self, *_):
        self.resetZoomBtn.display = False
        self.leftAxis.SetBehavior(axis.AXIS_TIGHT)
        if _GetSetting('scale_to_data', 1):
            self.leftAxis.ZoomOn(self._GetLeftAxisData(True))

    def _LeftAxisChanged(self, _):
        self.resetZoomBtn.display = self.leftAxis.GetBehavior() == axis.AXIS_CUSTOM

    def _TopAxisChanged(self, _):
        global _cachedRange
        _cachedRange = self.topAxis.GetVisibleRange()
        _SetSetting('dateRange', int(_cachedRange[1] - _cachedRange[0]))
        if _GetSetting('scale_to_data', 1):
            if self.leftAxis.GetBehavior() != axis.AXIS_CUSTOM:
                self.leftAxis.ZoomOn(self._GetLeftAxisData(True))
            self.rightAxis.ZoomOn(self._GetRightAxisData(True))

    def _GetLeftAxisData(self, visibleRange = False):
        if visibleRange:
            inputData = self.data[max(0, int(self.topAxis.GetVisibleRange()[0])):int(self.topAxis.GetVisibleRange()[1]) + 1]
        else:
            inputData = self.data
        data = []
        if _GetSetting('mediandayprice', True):
            data.extend((x[3] for x in inputData))
        if _GetSetting('minmax', True):
            data.extend((x[1] for x in inputData))
            data.extend((x[2] for x in inputData))
        closing = [ x[3] for x in inputData ]
        if _GetSetting('movingavg5', True):
            data.extend(MovingAvg(closing, 5))
        if _GetSetting('movingavg20', True):
            data.extend(MovingAvg(closing, 20))
        if _GetSetting('donchian', True):
            data.extend((x[1] for x in inputData))
            data.extend((y[2] for y in inputData))
        if not data:
            return (0, 1)
        return (min(data), max(data))

    def _GetRightAxisData(self, visibleRange = False):
        data = []
        if _GetSetting('volume', True):
            if visibleRange:
                inputData = self.data[max(0, int(self.topAxis.GetVisibleRange()[0])):int(self.topAxis.GetVisibleRange()[1]) + 1]
            else:
                inputData = self.data
            data.extend((x[4] for x in inputData))
        return axis.GetRangeFromSequences([0], data)

    def AddGrid(self):
        Grid(parent=self.graphArea, axis=self.leftAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0, color=(1.0, 1.0, 1.0, 0.1), zeroColor=(1, 1, 1, 1))
        Grid(parent=self.graphArea, axis=self.topAxis, orientation=axis.AxisOrientation.HORIZONTAL, color=(1.0, 1.0, 1.0, 0.1))

    def AddBarGraph(self, animate = False):
        if _GetSetting('volume', True):
            self.rightAxisLabels.display = True
            if _GetSetting('scale_to_data', 1):
                self.rightAxis.ZoomOn(self._GetRightAxisData(True))
            if self.barGraph:
                return
            data = [ x[4] for x in self.data ]

            def getHint(index):
                point = self.data[index]
                return localization.GetByLabel('UI/PriceHistory/VolumeHint', date=FmtDate(point[0], 'ln'), orders=FmtAmt(point[5], 'sn'), quantity=FmtAmt(point[4], 'sn'))

            self.barGraph = BarGraph(parent=self.graphArea, categoryAxis=self.topAxis, valueAxis=self.rightAxis, barSizeMinMax=(2, 20), values=data, hint=DynamicHint(getHint), color=graphColors[0], hoverColor=graphColors[0][0:3] + (2,))
            if animate:
                self.barGraph.Animate(animations.AnimationType.FADE, animations.AnimationDynamics.SIMULTANEOUS, 1.0)
        else:
            if self.barGraph:
                self.barGraph.Close()
                self.barGraph = None
            self.rightAxisLabels.display = False

    def AddMovingAverage5(self):
        if _GetSetting('movingavg5', True):
            if self.movingAvg5:
                return
            closing = [ x[3] for x in self.data ]
            avg5Data = MovingAvg(closing, 5)
            idx = 0
            if self.median:
                idx += 1
            if self.lowHigh:
                idx += 1
            self.movingAvg5 = LineGraph(parent=self.graphArea, categoryAxis=self.topAxis, valueAxis=self.leftAxis, values=avg5Data, lineColor=graphColors[2], idx=idx)
        elif self.movingAvg5:
            self.movingAvg5.Close()
            self.movingAvg5 = None

    def AddMovingAverage20(self):
        if _GetSetting('movingavg20', True):
            if self.movingAvg20:
                return
            closing = [ x[3] for x in self.data ]
            avg20Data = MovingAvg(closing, 20)
            idx = 0
            if self.median:
                idx += 1
            if self.lowHigh:
                idx += 1
            if self.movingAvg5:
                idx += 1
            self.movingAvg20 = LineGraph(parent=self.graphArea, categoryAxis=self.topAxis, valueAxis=self.leftAxis, values=avg20Data, lineColor=graphColors[4], idx=idx)
        elif self.movingAvg20:
            self.movingAvg20.Close()
            self.movingAvg20 = None

    def AddMinMaxGraph(self):
        if _GetSetting('minmax', True):
            if self.lowHigh:
                return
            data = [ (x[1], x[2]) for x in self.data ]
            idx = 1 if self.median else 0
            self.lowHigh = LowHighValueGraph(parent=self.graphArea, categoryAxis=self.topAxis, valueAxis=self.leftAxis, values=data, idx=idx)
        elif self.lowHigh:
            self.lowHigh.Close()
            self.lowHigh = None

    def AddDonchianChannel(self):
        if _GetSetting('donchian', True):
            if self.donchian:
                return
            data = ([ x[1] for x in self.data ], [ y[2] for y in self.data ])
            idx = 0
            if self.median:
                idx += 1
            if self.lowHigh:
                idx += 1
            if self.movingAvg5:
                idx += 1
            if self.movingAvg20:
                idx += 1
            self.donchian = DonchianChannel(parent=self.graphArea, categoryAxis=self.topAxis, valueAxis=self.leftAxis, values=data, graphColor=(0.8,
             0.8,
             1.0,
             0.12249999999999998), state=uiconst.UI_DISABLED, idx=idx)
        elif self.donchian:
            self.donchian.Close()
            self.donchian = None

    def AddMiniMap(self):
        data = [ x[3] for x in self.data ]
        categoryAxis = axis.MonthlyTimeAxis([ x[0] for x in self.data ])
        valueAxis = axis.AutoTicksAxis((min(data), max(data)), behavior=axis.AXIS_FROM_ZERO)
        miniMap = MiniMap(name='MiniMap', parent=self.miniMapContainer, align=uiconst.TOALL, controlAxis=self.topAxis, padTop=4)
        miniMap.AddAxis(axis.AxisOrientation.HORIZONTAL, categoryAxis)
        miniMap.AddAxis(axis.AxisOrientation.VERTICAL, valueAxis, 1.0, 0.0)
        Grid(parent=miniMap, axis=categoryAxis, orientation=axis.AxisOrientation.HORIZONTAL, color=(1.0, 1.0, 1.0, 0.1))
        AreaGraph(parent=miniMap, categoryAxis=categoryAxis, valueAxis=valueAxis, values=data, graphColor=(1.0,
         1.0,
         1.0,
         0.09), state=uiconst.UI_DISABLED)

    def AddMedianPoints(self, animate = False):
        if _GetSetting('mediandayprice', True):
            if self.median:
                return

            def getHint(index):
                point = self.data[index]
                return '%s\n%s' % (FmtDate(point[0], 'ln'), FmtAmt(point[3], 'sn'))

            data = [ x[3] for x in self.data ]
            self.median = PointGraph(parent=self.graphArea, categoryAxis=self.topAxis, valueAxis=self.leftAxis, values=data, hint=DynamicHint(getHint), pointSizeMinMax=(5, 10), pointColor=graphColors[3], idx=0)
            if animate:
                self.median.Animate(animations.AnimationType.GROW, animations.AnimationDynamics.ALONG_AXIS, 1.0)
        elif self.median:
            self.median.Close()
            self.median = None

    def _RebuildLegend(self):
        if self.legend is None:
            return
        self.legend.Flush()
        if self.median:
            self.legend.AddItem(self.median.GetLegendItem(), localization.GetByLabel('UI/PriceHistory/MedianDayPrice'))
        if self.lowHigh:
            self.legend.AddItem(self.lowHigh.GetLegendItem(), localization.GetByLabel('UI/PriceHistory/MinMax'))
        if self.movingAvg5:
            numDays = localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantityShort/Day', value=5)
            self.legend.AddItem(self.movingAvg5.GetLegendItem(), localization.GetByLabel('UI/PriceHistory/MovingAvg', numDays=numDays))
        if self.movingAvg20:
            numDays = localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantityShort/Day', value=20)
            self.legend.AddItem(self.movingAvg20.GetLegendItem(), localization.GetByLabel('UI/PriceHistory/MovingAvg', numDays=numDays))
        if self.donchian:
            self.legend.AddItem(self.donchian.GetLegendItem(), localization.GetByLabel('UI/PriceHistory/DonchianChannel'))
        if self.barGraph:
            self.legend.AddItem(self.barGraph.GetLegendItem(), localization.GetByLabel('UI/PriceHistory/Volume'))
