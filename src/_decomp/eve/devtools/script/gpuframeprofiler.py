#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\gpuframeprofiler.py
import blue
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.control.scrollentries import SE_ListGroupCore
from carbonui.util.various_unsorted import SortListOfTuples
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
import trinity
from eve.client.script.ui.control.listgroup import ListGroup
from trinity import gpuprofiler

def _FormatGpuTime(time):
    if time == 0:
        return '0'
    elif time > 1:
        return '%.1fs' % time
    elif time > 0.001:
        return '%.1fms' % (time * 1000)
    else:
        return '%.1fus' % (time * 1000000)


def _FormatStat(name, value):
    if name == 'GPU Time':
        return _FormatGpuTime(value)
    else:
        return str(value)


def _GetColumnData(zone, columns):
    return (zone.GetOrder(), zone.name) + tuple((zone.stats.get(k, 0) for k in columns[2:]))


def _GetLabel(zone, columns):
    return '<t>'.join((str(zone.GetOrder()), zone.name) + tuple((zone.statText.get(k, '') for k in columns[2:])))


class ProfilerScroll(Scroll):

    def SortAsRoot(self, nodes, endOrder, columnName, columnIndex, reversedSorting = 0, groupIndex = None):
        rootSortList_Groups = []
        rootSortList_NotGroups = []
        for node in nodes:
            if groupIndex is None and node.isSub:
                continue
            val = (self.GetSortValue(columnName, node, columnIndex), self.GetStringFromNode(node).lower())
            if issubclass(node.decoClass, SE_ListGroupCore):
                rootSortList_Groups.append((val, node))
            else:
                rootSortList_NotGroups.append((val, node))

        combinedGroupsAndOthers = SortListOfTuples(rootSortList_Groups + rootSortList_NotGroups, reversedSorting)
        if groupIndex is not None:
            for subIndex, subNode in enumerate(combinedGroupsAndOthers):
                endOrder.insert(groupIndex + subIndex + 1, subNode)

        else:
            endOrder.extend(combinedGroupsAndOthers)
        if rootSortList_Groups:
            for _, groupNode in rootSortList_Groups:
                groupIdx = endOrder.index(groupNode)
                subNodes = groupNode.get('subNodes', [])
                self.SortAsRoot(subNodes, endOrder, columnName, columnIndex, reversedSorting, groupIndex=groupIdx)

        return nodes


class GpuFrameProfilerWnd(Window):
    __guid__ = 'form.GpuFrameProfiler'
    default_caption = 'GPU Frame Profiler'
    default_minSize = (500, 360)
    default_windowID = 'GpuFrameProfiler'

    def __init__(self, **kw):
        self.headers = []
        self.zones = None
        self.scroll = None
        super(GpuFrameProfilerWnd, self).__init__(**kw)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        main = self.GetMainArea()
        settingsContainer = Container(parent=main, align=uiconst.TOTOP, height=30, padding=10)
        Button(parent=settingsContainer, align=uiconst.TOLEFT, label='Capture Frame', func=self._Capture)
        self.scroll = ProfilerScroll(parent=main, align=uiconst.TOALL, padding=(5, 5, 5, 5))

    def _Capture(self, *_):
        try:
            trinity.settings.SetValue('enableMetalCounters', True)
        except LookupError:
            pass

        trinity.GetGpuProfiler().Capture()
        while True:
            blue.synchro.Yield()
            try:
                report = trinity.GetGpuProfiler().GetFrameReport()
            except RuntimeError:
                continue

            self.zones = gpuprofiler.BuildZoneTree(gpuprofiler.RawZone(report))
            self.PopulateContent()
            break

    def GetEntryFor(self, zone, sublevel):
        columns = _GetColumnData(zone, self.headers)
        node = {'label': _GetLabel(zone, self.headers),
         'sortValues': columns,
         'sublevel': sublevel,
         'showlen': 0,
         'id': (123, zone)}
        if zone.children:
            node['RefreshScroll'] = lambda *_: []
            node['GetSubContent'] = self._GroupGetSubContent
            node['showicon'] = 'hide'
            return GetFromClass(ListGroup, node)
        else:
            return GetFromClass(Generic, node)

    def _GroupGetSubContent(self, node, *_):
        ret = []
        sublevel = node.get('sublevel', 0)
        zone = node.id[1]
        for child in zone.children:
            ret.append(self.GetEntryFor(child, sublevel + 1))

        return ret

    def GetContent(self):
        return [self.GetEntryFor(self.zones, 0)]

    def PopulateContent(self):
        self.headers = ['#', 'Name']
        for k in sorted(gpuprofiler.GetStatKeys(self.zones)):
            if k not in self.headers:
                self.headers.append(k)

        self.scroll.Load(contentList=self.GetContent(), headers=self.headers, fixedEntryHeight=None)
