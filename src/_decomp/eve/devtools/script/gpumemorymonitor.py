#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\gpumemorymonitor.py
from carbon.common.script.util.format import GetTimeParts
from carbonui import uiconst, TextAlign
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.scroll import Scroll
from carbonui.graphs import axis, axislabels
from carbonui.graphs.graph import GraphArea
from carbonui.graphs.grid import Grid
from carbonui.graphs.linegraph import LineGraph
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
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
from trinity.gpumemory import GetResourceListColumns, ResourceFilters, GetResourceRow

def _OnMouseExitLegend(graph):
    graph.lineWidth = 1


def _OnMouseEnterLegend(graph):
    graph.SetOrder(0)
    graph.lineWidth = 2


def _TimeLabel(t):
    year, month, wd, day, hour, minutes, sec, ms = GetTimeParts(t)
    return '%2.2d:%2.2d' % (hour, minutes)


class _Counter(object):

    def __init__(self, title, color, resourceFilter):
        self.title = title
        self.color = color
        self.values = []
        self.resourceFilter = resourceFilter

    def Collect(self, resources):
        value = 0
        for k, v in resources.items():
            value += sum((int(x.get('size', 0)) for x in v if self.resourceFilter(k, x)))

        self.values.append(value)


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

    def Build(self, resources):
        self.graph.Flush()
        self.legend.Flush()
        for counter in self.counters:
            counter.Collect(resources)

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


def GetScrollContent(resources, headers):
    entries = []
    for each in resources:
        columns = {k:i for i, k in enumerate(headers)}
        row = GetResourceRow(each, columns)
        entries.append(GetFromClass(SE_GenericCore, {'label': '<t>'.join((x[1] for x in row)),
         'sortValues': [ x[0] for x in row ]}))

    return entries


class Report(Container):

    def ApplyAttributes(self, attributes):
        super(Report, self).ApplyAttributes(attributes)
        self.padding = 10
        header = Container(parent=self, align=uiconst.TOTOP, height=30)
        Button(parent=header, align=uiconst.TOPRIGHT, label='Refresh', func=self.Refresh)
        self.types = Combo(parent=header, align=uiconst.TOPLEFT, label='Type', callback=self._OnTypeSelected)
        self.resourceList = Scroll(name='resourceList', parent=self, align=uiconst.TOALL, id='gpuMemoryResourceList')
        self.liveResources = {}

    def _OnTypeSelected(self, comboBox, key, value):
        resources = self.liveResources[value]
        headers = GetResourceListColumns(resources)
        self.resourceList.Load(contentList=GetScrollContent(resources, headers), headers=headers)
        return sorted(self.liveResources.keys())

    def Refresh(self, *_):
        wasEmpty = not self.liveResources
        self.liveResources = trinity.GetLiveALResources()
        self.types.LoadOptions([ (x, x) for x in sorted(self.liveResources.keys()) ])
        if wasEmpty:
            self._OnTypeSelected(self.types, self.types.selectedValue, self.types.selectedValue)


class SystemInfo(Container):

    def ApplyAttributes(self, attributes):
        super(SystemInfo, self).ApplyAttributes(attributes)
        self.padding = 10
        self.header = Container(parent=self, align=uiconst.TOALL)
        self.error = None
        self.rows = []
        self.Refresh()

    def Refresh(self):
        try:
            info = trinity.GetVideoMemoryInfo()
        except BaseException as e:
            if not self.error:
                self.header.Flush()
                del self.rows[:]
                self.error = Label(parent=self.header, text='Failed to get memory info (%s)' % e, align=uiconst.TOTOP, padLeft=20)
            return

        rows = []
        for k, v in info.items():
            if isinstance(v, dict):
                rows.append((k, ''))
                for kv, vv in v.items():
                    rows.append(('  ' + kv, FormatMemory(vv)))

            else:
                rows.append((k, FormatMemory(v)))

        same = True
        if len(rows) != len(self.rows):
            same = False
            self.header.Flush()
            del self.rows[:]
        else:
            for a, b in zip(rows, self.rows):
                if a[0] != b[0]:
                    same = False

        if same:
            for a, b in zip(rows, self.rows):
                b[1].SetText(a[1])

        else:
            for k, v in rows:
                r = Container(parent=self.header, align=uiconst.TOTOP, height=20)
                Label(parent=r, text=k, align=uiconst.TOLEFT)
                self.rows.append((k, Label(parent=r, text=v, align=uiconst.TOALL, textAlign=TextAlign.RIGHT)))


class GpuMemoryMonitor(Window):
    default_caption = 'GPU Memory Monitor'
    default_minSize = (700, 400)
    default_windowID = 'GpuMemoryMonitor'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        tabGroup = TabGroup(parent=self.sr.main, align=uiconst.TOTOP, padBottom=10, groupID='GpuMemoryMonitorTabs')
        self.totals = GpuMemoryGraph(parent=self.sr.main, counters=[_Counter('Total', Color.RED, lambda *_: True),
         _Counter('Buffers', Color.GREEN, ResourceFilters.IsBuffer),
         _Counter('Textures', Color.BLUE, ResourceFilters.IsTexture),
         _Counter('Other', Color.YELLOW, lambda x, y: not ResourceFilters.IsBuffer(x, y) and not ResourceFilters.IsTexture(x, y))])
        tabGroup.AddTab('Totals', self.totals)
        self.textures = GpuMemoryGraph(parent=self.sr.main, counters=[_Counter('Total', Color.RED, ResourceFilters.IsTexture),
         _Counter('Render Target', Color.GREEN, ResourceFilters.IsRenderTarget),
         _Counter('Depth Stencil', Color.BLUE, ResourceFilters.IsDepthStencil),
         _Counter('Immutable', Color.FUCHSIA, lambda x, y: ResourceFilters.IsTexture(x, y) and ResourceFilters.IsImmutable(x, y)),
         _Counter('Other', Color.YELLOW, lambda x, y: ResourceFilters.IsTexture(x, y) and not ResourceFilters.IsRenderTarget(x, y) and not ResourceFilters.IsDepthStencil(x, y) and not ResourceFilters.IsImmutable(x, y))])
        tabGroup.AddTab('Textures', self.textures)
        self.buffers = GpuMemoryGraph(parent=self.sr.main, counters=[_Counter('Total', Color.RED, ResourceFilters.IsBuffer),
         _Counter('Dynamic', Color.GREEN, lambda x, y: ResourceFilters.IsBuffer(x, y) and ResourceFilters.IsDynamic(x, y)),
         _Counter('Immutable', Color.FUCHSIA, lambda x, y: ResourceFilters.IsBuffer(x, y) and ResourceFilters.IsImmutable(x, y)),
         _Counter('Other', Color.YELLOW, lambda x, y: ResourceFilters.IsBuffer(x, y) and not ResourceFilters.IsDynamic(x, y) and not ResourceFilters.IsImmutable(x, y))])
        tabGroup.AddTab('Buffers', self.buffers)
        tabGroup.AddTab('Report', Report(parent=self.sr.main))
        self.systemInfo = SystemInfo(parent=self.sr.main)
        tabGroup.AddTab('System Info', self.systemInfo)
        tabGroup.AutoSelect()
        uthread2.StartTasklet(self.Tick)

    def Tick(self):
        while not self.destroyed:
            resources = trinity.GetLiveALResources()
            self.totals.Build(resources)
            self.textures.Build(resources)
            self.buffers.Build(resources)
            self.systemInfo.Refresh()
            uthread2.Sleep(1.5)
