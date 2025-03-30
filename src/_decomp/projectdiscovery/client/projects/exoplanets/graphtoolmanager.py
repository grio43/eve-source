#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\graphtoolmanager.py
from carbonui.uicore import uicore
import carbonui.const as uiconst
from projectdiscovery.client.projects.exoplanets.graphtools.basetool import BaseTool

class GraphToolManager(object):
    __notifyevents__ = ['OnSolutionSubmit', 'OnContinueFromRewards']

    def __init__(self, graph, default_tool, ctrl_tool, *args, **kwargs):
        super(GraphToolManager, self).__init__()
        self._is_ctr_tool_on = False
        self._graph = graph
        self._default_tool = default_tool
        self._ctrl_tool = ctrl_tool
        self._key_up_cookie = None
        self._key_down_cookie = None
        self._is_empty_tool = False

    def register_key_listeners(self):
        self._key_down_cookie = uicore.uilib.RegisterForTriuiEvents([uiconst.UI_KEYDOWN], self._on_key_down)
        self._key_up_cookie = uicore.uilib.RegisterForTriuiEvents([uiconst.UI_KEYUP], self._on_key_up)
        sm.RegisterNotify(self)

    def unregister_key_listeners(self):
        uicore.uilib.UnregisterForTriuiEvents(self._key_down_cookie)
        uicore.uilib.UnregisterForTriuiEvents(self._key_up_cookie)
        self._key_up_cookie = None
        self._key_down_cookie = None
        sm.UnregisterNotify(self)

    def _on_key_down(self, *args):
        if not self._is_ctr_tool_on and uicore.uilib.Key(uiconst.VK_CONTROL) and self._graph.get_graph_data():
            self._is_ctr_tool_on = True
            self._graph.set_tool(self._ctrl_tool)
        return True

    def _on_key_up(self, *args):
        if self._is_ctr_tool_on and not uicore.uilib.Key(uiconst.VK_CONTROL) and self._graph.get_graph_data():
            self._is_ctr_tool_on = False
            self._graph.set_tool(self._default_tool if not self._is_empty_tool else BaseTool())
        return True

    def OnSolutionSubmit(self, *args, **kwargs):
        self._is_empty_tool = True
        if not self._is_ctr_tool_on:
            self._graph.set_tool(BaseTool())

    def OnContinueFromRewards(self, *args, **kwargs):
        self._is_empty_tool = False
        if not self._is_ctr_tool_on:
            self._graph.set_tool(self._default_tool)
