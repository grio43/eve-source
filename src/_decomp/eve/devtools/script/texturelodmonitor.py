#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\texturelodmonitor.py
from carbon.common.script.util.format import GetTimeParts
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.scroll import Scroll
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.graphs import axis, axislabels
from carbonui.graphs.graph import GraphArea
from carbonui.graphs.grid import Grid
from carbonui.graphs.linegraph import LineGraph
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.util.color import Color
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import Label
from carbonui.control.tabGroup import TabGroup
from nicenum import FormatMemory
from eve.devtools.script.engineinfopanel import GetMemoryLabel
from carbonui.control.window import Window
from carbonui.control.scrollentries import SE_GenericCore
import blue
import trinity
import uthread2

def _OnMouseExitLegend(graph):
    graph.lineWidth = 1


def _OnMouseEnterLegend(graph):
    graph.SetOrder(0)
    graph.lineWidth = 2


def _TimeLabel(t):
    year, month, wd, day, hour, minutes, sec, ms = GetTimeParts(t)
    return '%2.2d:%2.2d' % (hour, minutes)


class _Counter(object):

    def __init__(self, title, color, statName):
        self.title = title
        self.color = color
        self.values = []
        self.statName = statName

    def Collect(self):
        self.values.append(blue.statistics.GetSingleStat(self.statName))


class GpuMemoryGraph(Container):
    horizontalLabelWidth = 64

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.legend = Container(parent=self, align=uiconst.TORIGHT, width=200, padLeft=10)
        self.graph = Container(parent=self, align=uiconst.TOALL)
        self.counters = attributes.pop('counters', [])
        self.times = []

    def AddLegend(self, color, text, graph):
        legendCont = Container(parent=self.legend, align=uiconst.TOTOP, height=40)
        fill = Fill(parent=legendCont, color=color, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, width=16, height=16)
        fill.OnMouseEnter = lambda : _OnMouseEnterLegend(graph)
        fill.OnMouseExit = lambda : _OnMouseExitLegend(graph)
        Label(parent=legendCont, text=text, align=uiconst.TOTOP, padLeft=20)

    def Build(self):
        self.graph.Flush()
        self.legend.Flush()
        for counter in self.counters:
            counter.Collect()

        self.times.append(blue.os.GetWallclockTime())
        bottom = Container(parent=self.graph, align=uiconst.TOBOTTOM, height=24)
        Fill(parent=bottom, align=uiconst.TOLEFT, width=80, spriteEffect=trinity.TR2_SFX_NONE)
        categoryAxis = axis.AutoTicksCategoryAxis(self.times, labelFormat=_TimeLabel, tickCount=10)
        valueRange = axis.GetRangeFromSequences(*tuple((x.values for x in self.counters)))
        valueAxis = axis.AutoTicksAxis(valueRange, tickCount=10, tickBase=2, behavior=axis.AXIS_FROM_ZERO, margins=(0.1, 0.1), labelFormat=FormatMemory)
        axislabels.AxisLabels(parent=bottom, align=uiconst.TOBOTTOM, height=24, padRight=8, fontsize=12, axis=categoryAxis, orientation=axis.AxisOrientation.HORIZONTAL)
        axislabels.AxisLabels(parent=self.graph, align=uiconst.TOLEFT, width=80, axis=valueAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0)
        graphArea = GraphArea(parent=self.graph)
        graphArea.AddAxis(axis.AxisOrientation.HORIZONTAL, categoryAxis)
        graphArea.AddAxis(axis.AxisOrientation.VERTICAL, valueAxis, 1.0, 0.0)
        Grid(parent=graphArea, axis=valueAxis, orientation=axis.AxisOrientation.VERTICAL, color=(1, 1, 1, 0.2), minFactor=1.0, maxFactor=0.0)
        Fill(parent=self.graph, color=(0, 0, 0, 0.25))
        for counter in self.counters:
            graph = LineGraph(parent=graphArea, categoryAxis=categoryAxis, valueAxis=valueAxis, values=counter.values, color=counter.color, lineWidth=1, spriteEffect=trinity.TR2_SFX_FILL)
            text = counter.title
            if len(counter.values) > 1:
                text += ' ' + GetMemoryLabel(counter.values[-1], counter.values[-2], counter.values[0])
            self.AddLegend(counter.color, text, graph)


class Settings(Container):

    def ApplyAttributes(self, attributes):
        super(Settings, self).ApplyAttributes(attributes)
        self.padding = 10
        mainGrid = LayoutGrid(columns=2, parent=self, align=uiconst.TOALL, cellPadding=5, cellSpacing=10)
        gpu = trinity.settings.GetValue('textureLodGpuBudget')
        self._gpu = SingleLineEditText(parent=mainGrid, width=200, label='GPU Budget (MB)', setvalue=str(gpu / 1024 / 1024))
        self._currentGpu = Label(parent=mainGrid, text=FormatMemory(gpu))
        cpu = trinity.settings.GetValue('textureLodCpuBudget')
        self._cpu = SingleLineEditText(parent=mainGrid, width=200, label='CPU Budget (MB)', setvalue=str(cpu / 1024 / 1024))
        self._currentCpu = Label(parent=mainGrid, text=FormatMemory(cpu))
        latency = trinity.settings.GetValue('textureLodSimulateDiskLatency')
        self._loadLatency = SingleLineEditText(parent=mainGrid, width=200, label='Load Latency (usec)', setvalue=str(latency))
        self._currentLatency = Label(parent=mainGrid, text='%s usec' % latency)
        Button(parent=mainGrid, label='Set Values', func=self.SetValues)

    def SetValues(self, *_):
        trinity.settings.SetValue('textureLodGpuBudget', int(self._gpu.GetValue()) * 1024 * 1024)
        trinity.settings.SetValue('textureLodCpuBudget', int(self._cpu.GetValue()) * 1024 * 1024)
        trinity.settings.SetValue('textureLodSimulateDiskLatency', int(self._loadLatency.GetValue()))

    def Refresh(self):
        self._currentGpu.SetText(FormatMemory(trinity.settings.GetValue('textureLodGpuBudget')))
        self._currentCpu.SetText(FormatMemory(trinity.settings.GetValue('textureLodCpuBudget')))
        self._currentLatency.SetText(str(trinity.settings.GetValue('textureLodSimulateDiskLatency')))


def GetScrollContent(resources):
    entries = []
    for x in resources:
        text = ('Yes' if x[0] else 'No',
         str(x[1]),
         str(x[2]),
         FormatMemory(x[3]),
         FormatMemory(x[4]),
         trinity.TEXTURE_TYPE.GetNameFromValue(x[5]).split('_')[-1],
         str(x[6]),
         str(x[7]),
         x[8])
        entries.append(GetFromClass(SE_GenericCore, {'label': '<t>'.join(text),
         'sortValues': x}))

    return entries


class Report(Container):

    def ApplyAttributes(self, attributes):
        super(Report, self).ApplyAttributes(attributes)
        self.padding = 10
        header = Container(parent=self, align=uiconst.TOTOP, height=30)
        rheader = ContainerAutoSize(parent=header, align=uiconst.TOPRIGHT, height=30)
        Button(parent=rheader, align=uiconst.TORIGHT, label='Refresh', func=self.OnRefresh)
        self._autoRefresh = Checkbox(text='Auto Refresh', parent=rheader, checked=True, align=uiconst.TORIGHT)
        self._filter = Combo(parent=header, align=uiconst.TOPLEFT, label='Filter', callback=self._OnTypeSelected, options=[('All', 'All'), ('With LOD', 'With LOD'), ('Without LOD', 'Without LOD')])
        self.resourceList = Scroll(name='resourceList', parent=self, align=uiconst.TOALL, id='textureLodList')
        self._textures = []
        self._currentData = []
        self._isActive = False

    def _OnTypeSelected(self, comboBox, key, value):
        if value == 'With LOD':
            resources = [ x.object for x in self._textures if x.object and x.object.hadLodRequests ]
        elif value == 'Without LOD':
            resources = [ x.object for x in self._textures if x.object and not x.hadLodRequests ]
        else:
            resources = [ x.object for x in self._textures if x.object ]
        headers = ['LOD Requested',
         'GPU LOD',
         'CPU LOD',
         'Size',
         'Original Size',
         'Type',
         'Width',
         'Height',
         'Path']
        newData = [ (each.hadLodRequests,
         each.gpuMip,
         each.cpuMip,
         each.GetMemoryUsage(),
         each.GetOriginalMemoryUsage(),
         each.type,
         each.width,
         each.height,
         each.path) for each in resources ]
        if newData != self._currentData:
            self._currentData = newData
            self.resourceList.Load(contentList=GetScrollContent(newData), headers=headers)

    def OnRefresh(self, *_):
        self._textures = [ blue.BluePythonWeakRef(x) for x in trinity.GetTextureLodManager().GetManagedTextures() if x.lodEnabled ]
        self._OnTypeSelected(self._filter, self._filter.selectedValue, self._filter.selectedValue)

    def Refresh(self):
        if self._isActive and self._autoRefresh.GetValue():
            self.OnRefresh()

    def OnTabDeselect(self):
        self._isActive = False

    def OnTabSelect(self):
        self._isActive = True
        self.Refresh()


class TextureLodMonitor(Window):
    default_caption = 'Texture LOD Monitor'
    default_minSize = (700, 400)
    default_windowID = 'TextureLodMonitor'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        tabGroup = TabGroup(parent=self.sr.main, align=uiconst.TOTOP, padBottom=10, groupID='GpuMemoryMonitorTabs')
        self.totals = GpuMemoryGraph(parent=self.sr.main, counters=[_Counter('GPU Memory', Color.RED, 'Trinity/TextureLod/GpuSize'), _Counter('CPU Memory', Color.GREEN, 'Trinity/TextureLod/CpuSize'), _Counter('Upload Size', Color.BLUE, 'Trinity/TextureLod/UploadSize')])
        tabGroup.AddTab('Stats', self.totals)
        self.settings = Settings(parent=self.sr.main)
        tabGroup.AddTab('Settings', self.settings)
        self.report = Report(parent=self.sr.main)
        tabGroup.AddTab('Report', self.report)
        tabGroup.AutoSelect()
        uthread2.StartTasklet(self.Tick)

    def Tick(self):
        while not self.destroyed:
            self.totals.Build()
            self.settings.Refresh()
            self.report.Refresh()
            uthread2.Sleep(1.5)
