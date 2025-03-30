#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\enginetools.py
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_QA
from carbonui import Density, uiconst
from carbonui.modules.fpsmonitor import FpsMonitor
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.control.button import Button
from carbonui.control.window import Window
from eve.devtools.script.bdqmonitor import BackgroundDownloadQueueMonitor
from eve.devtools.script.engineinfopanel import EngineInfoPanel
from eve.devtools.script.graphswindow import GraphsWindow
from eve.devtools.script.livecountmonitor import LiveCountMonitor
from eve.devtools.script.logviewer import LogViewer
from eve.devtools.script.gpumemorymonitor import GpuMemoryMonitor
from eve.devtools.script.memorymonitor import MemoryMonitor
from eve.devtools.script.methodcallsmonitor import MethodCallsMonitor
from eve.devtools.script.networkdatamonitor import NetworkDataMonitor
from eve.devtools.script.outstandingmonitor import OutstandingMonitor
from eve.devtools.script.pythonobjects import PythonObjectsMonitor
from eve.devtools.script.resmanmonitor import ResManMonitor
from eve.devtools.script.taskletMonitor import TaskletMonitor
from eve.devtools.script.telemetrypanel import TelemetryPanel
from eve.devtools.script.texturelodmonitor import TextureLodMonitor
from eve.devtools.script.threadmonitor import ThreadMonitor
from eve.devtools.script.gpuframeprofiler import GpuFrameProfilerWnd
from eve.devtools.script.carboninfo import CarbonInfo
TOOLS = [['System Memory', MemoryMonitor, 0],
 ['GPU Memory', GpuMemoryMonitor, ROLE_GML],
 ['Texture LOD', TextureLodMonitor, ROLE_GML],
 ['LiveCount', LiveCountMonitor, ROLE_GML],
 ['Python objects', PythonObjectsMonitor, ROLE_GML],
 ['Log viewer', LogViewer, 0],
 ['Method Calls', MethodCallsMonitor, ROLE_GML],
 ['Outstanding Calls', OutstandingMonitor, 0],
 ['Network', NetworkDataMonitor, 0],
 ['Background download queue monitor', BackgroundDownloadQueueMonitor, ROLE_QA],
 ['Threads', ThreadMonitor, ROLE_QA],
 ['Tasklets', TaskletMonitor, ROLE_QA],
 ['Blue statistics graphs', GraphsWindow, ROLE_QA],
 ['Telemetry panel', TelemetryPanel, ROLE_QA],
 ['Resource Manager', ResManMonitor, ROLE_QA],
 ['GPU Frame Profiler', GpuFrameProfilerWnd, ROLE_QA],
 ['FPS Monitor', FpsMonitor, 0],
 ['Carbon Info', CarbonInfo, 0]]

class EngineToolsLauncher(Window):
    default_caption = 'Engine Tools'
    default_windowID = 'EngineTools'
    default_width = 740
    default_height = 250
    default_minSize = (default_width, default_height)
    default_maxSize = (default_width, default_height)
    default_fixedWidth = default_width
    default_fixedHeight = default_height

    def ApplyAttributes(self, attributes):
        super(EngineToolsLauncher, self).ApplyAttributes(attributes)
        self.main_cont = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, callback=self._on_main_cont_size_changed, only_use_callback_when_size_changes=True)
        EngineInfoPanel(parent=self.main_cont, align=uiconst.TOTOP, height=60)
        flowCont = FlowContainer(parent=self.main_cont, align=uiconst.TOTOP, top=16, contentSpacing=(8, 8))
        for name, window, roleRequired in TOOLS:
            if roleRequired and session.role & roleRequired == 0:
                continue
            Button(parent=flowCont, label=name, align=uiconst.NOALIGN, func=lambda _window: _window.Open(), args=window, fixedheight=24, density=Density.COMPACT)

    def _on_main_cont_size_changed(self):
        _, self.height = self.GetWindowSizeForContentSize(height=self.main_cont.height)
