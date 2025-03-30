#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\graphtools\basetool.py
from carbonui.primitives.container import Container

class BaseTool(object):

    def __init__(self, graph = None):
        self._graph = graph
        self._is_folded = False

    def set_graph(self, graph):
        self._graph = graph

    def on_scroll(self, scroll_amount):
        pass

    def on_mouse_move(self, horizontal_mouse_value, vertical_mouse_value):
        pass

    def on_mouse_hover(self, horizontal_mouse_value, vertical_mouse_value):
        pass

    def on_mouse_down(self, horizontal_mouse_value, vertical_mouse_value):
        pass

    def on_mouse_up(self, horizontal_mouse_value, vertical_mouse_value):
        pass

    def on_mouse_enter(self, horizontal_mouse_value, vertical_mouse_value):
        pass

    def on_mouse_exit(self, horizontal_mouse_value, vertical_mouse_value):
        pass

    def on_click(self, horizontal_mouse_value, vertical_mouse_value):
        pass

    def on_tool_set(self):
        pass

    def on_tool_unset(self):
        pass

    def set_is_folded(self, is_folded):
        self._is_folded = is_folded

    def get_tool_tip_object(self):
        return Container(name='Tooltip')
