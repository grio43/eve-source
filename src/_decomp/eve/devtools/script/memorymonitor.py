#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\memorymonitor.py
from carbon.common.script.util.format import GetTimeParts
from carbonui import const as uiconst
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.graphs import axis, axislabels
from carbonui.graphs.graph import GraphArea
from carbonui.graphs.grid import Grid
from carbonui.graphs.linegraph import LineGraph
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.util.color import Color
from carbonui.control.window import Window
from eve.devtools.script.engineinfopanel import EngineInfoPanel
from eve.client.script.ui.control.eveLabel import Label
from nicenum import FormatMemory
import blue
import trinity
import uthread2
import platform

def _OnMouseExitLegend(graph):
    graph.lineWidth = 1


def _OnMouseEnterLegend(graph):
    graph.SetOrder(0)
    graph.lineWidth = 2


def OnRefreshRateEdit(value):
    if value:
        value = max(0.1, float(value))
        value = min(10.0, value)
        refreshRate = int(10000000.0 * value)
        blue.pyos.performanceUpdateFrequency = refreshRate


def _TimeLabel(t):
    year, month, wd, day, hour, minutes, sec, ms = GetTimeParts(long(t))
    return '%2.2d:%2.2d' % (hour, minutes)


class MemoryGraph(Container):
    horizontalLabelWidth = 64

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        info = Container(parent=self, align=uiconst.TOTOP, height=64)
        EngineInfoPanel(parent=info, align=uiconst.TOLEFT_PROP, width=0.8)
        infoRight = Container(parent=info, align=uiconst.TOALL)
        refreshRate = blue.pyos.performanceUpdateFrequency / 10000000.0
        self.refreshRateEdit = SingleLineEditFloat(parent=infoRight, align=uiconst.TOTOP, label='Refresh rate (seconds):', setvalue=refreshRate, minValue=0.1, maxValue=10.0, OnChange=OnRefreshRateEdit)
        self.legend = Container(parent=self, align=uiconst.TOBOTTOM, height=16)
        self.graph = Container(parent=self, align=uiconst.TOALL)

    def UpdateGraph(self):
        while not self.destroyed:
            self.Build()
            uthread2.Sleep(0.5)

    def AddLegend(self, color, text, graph):
        fill = Fill(parent=self.legend, color=color, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, width=16)
        fill.OnMouseEnter = lambda : _OnMouseEnterLegend(graph)
        fill.OnMouseExit = lambda : _OnMouseExitLegend(graph)
        Label(parent=self.legend, text=text, align=uiconst.TOLEFT, padLeft=8, padRight=16)

    def Build(self):
        self.graph.Flush()
        self.legend.Flush()
        minutes = 60
        times = []
        memData = []
        pymemData = []
        workingsetData = []
        for sample in blue.pyos.cpuUsage[-minutes * 60 / 10:]:
            memData.append(sample.virtualMemory)
            pymemData.append(sample.pythonMemoryUsage)
            workingsetData.append(sample.workingSetSize)
            times.append(sample.timestamp)

        bottom = Container(parent=self.graph, align=uiconst.TOBOTTOM, height=24)
        Fill(parent=bottom, align=uiconst.TOLEFT, width=80, spriteEffect=trinity.TR2_SFX_NONE)
        categoryAxis = axis.AutoTicksCategoryAxis(times, labelFormat=_TimeLabel, tickCount=10)
        valueRange = axis.GetRangeFromSequences(memData, pymemData, workingsetData)
        valueAxis = axis.AutoTicksAxis(valueRange, tickCount=10, tickBase=2, behavior=axis.AXIS_FROM_ZERO, margins=(0.1, 0.1), labelFormat=FormatMemory)
        axislabels.AxisLabels(parent=bottom, align=uiconst.TOBOTTOM, height=24, padRight=8, fontsize=12, axis=categoryAxis, orientation=axis.AxisOrientation.HORIZONTAL)
        axislabels.AxisLabels(parent=self.graph, align=uiconst.TOLEFT, width=80, axis=valueAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0)
        graphArea = GraphArea(parent=self.graph)
        graphArea.AddAxis(axis.AxisOrientation.HORIZONTAL, categoryAxis)
        graphArea.AddAxis(axis.AxisOrientation.VERTICAL, valueAxis, 1.0, 0.0)
        Grid(parent=graphArea, axis=valueAxis, orientation=axis.AxisOrientation.VERTICAL, color=(1, 1, 1, 0.2), minFactor=1.0, maxFactor=0.0)
        Fill(parent=self.graph, color=(0, 0, 0, 0.25))
        Fill(parent=self.legend, align=uiconst.TOLEFT, width=80, spriteEffect=trinity.TR2_SFX_NONE)
        graphSources = [(memData, Color.RED, 'Total memory'), (pymemData, Color.GREEN, 'Python memory'), (workingsetData, Color.AQUA, 'Working set')]
        for source, color, text in graphSources:
            graph = LineGraph(parent=graphArea, categoryAxis=categoryAxis, valueAxis=valueAxis, values=source, color=color, lineWidth=1, spriteEffect=trinity.TR2_SFX_FILL)
            self.AddLegend(color, text, graph)


class MemoryMonitor(Window):
    default_caption = 'Memory Monitor'
    default_minSize = (700, 400)
    default_windowID = 'MemoryMonitor'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.graph = MemoryGraph(parent=self.sr.main, align=uiconst.TOALL, padding=16)
        uthread2.StartTasklet(self.graph.UpdateGraph)
