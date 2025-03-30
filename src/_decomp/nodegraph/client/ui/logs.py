#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\logs.py
import json
import blue
import eveui
from raffles.client.widget.virtual_list import VirtualList
from .collapse_section import CollapseSection

class LogHistory(CollapseSection):
    default_name = 'LogHistory'

    def __init__(self, controller, **kwargs):
        self._graph_logger = controller.node_graph.log
        self._controller = controller
        super(LogHistory, self).__init__(title='Logs', **kwargs)

    def close(self):
        self._graph_logger.on_log.disconnect(self._on_graph_log)

    def construct_content(self):
        self._filter_field = eveui.TextField(parent=self.content_container, align=eveui.Align.to_top, padTop=8, padBottom=8, placeholder='Filter...')
        self._filter_field.controller.bind(text=self._on_text_changed)
        self._list = VirtualList(parent=self.content_container, align=eveui.Align.to_top, height=250, render_item=self._render_list_item)
        if self._expanded:
            self._list.data = self._graph_logger.history[::-1]
            self._graph_logger.on_log.connect(self._on_graph_log)

    def _on_header_click(self, *args):
        super(LogHistory, self)._on_header_click(*args)
        if self._expanded:
            self._graph_logger.on_log.connect(self._on_graph_log)
            self._update_data()
        else:
            self._graph_logger.on_log.disconnect(self._on_graph_log)

    def _on_graph_log(self, log):
        if not self.is_content_constructed:
            return
        if not self._filter_field.text or self._filter_field.text in format_log_label(log):
            self._update_data()

    def _render_list_item(self):
        return LogHistoryItem(self._controller)

    def _on_text_changed(self, controller, text):
        self._update_data()

    def _update_data(self):
        text = self._filter_field.text
        self._list.data = [ log for log in self._graph_logger.history[::-1] if text in format_log_label(log) ]


class LogHistoryItem(eveui.Container):
    default_state = eveui.State.normal
    default_align = eveui.Align.to_top
    default_height = 25

    def __init__(self, controller, **kwargs):
        super(LogHistoryItem, self).__init__(**kwargs)
        self._controller = controller
        self._log = None
        self._bg_fill = eveui.Fill(bgParent=self, opacity=0)
        text_container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_top, padding=(8, 4, 8, 4))
        self._label = eveui.EveLabelMedium(parent=text_container, align=eveui.Align.to_top, maxLines=1)

    def update_item(self, log):
        self._hint = None
        self._log = log
        if log:
            self._label.text = format_log_label(log)
            self.state = eveui.State.normal
        else:
            self.state = eveui.State.hidden

    def filter_item(self, filter):
        if filter in self._label.text:
            self.state = eveui.State.normal
        else:
            self.state = eveui.State.hidden

    def OnClick(self, *args):
        if self._log['type'] == 'node':
            self._controller.focus_node(self._log['info']['node_id'])

    def OnMouseEnter(self, *args):
        if self._log['type'] == 'node':
            self._controller.highlight_node(self._log['info']['node_id'])
        if self._hint is None:
            self.SetHint(json.dumps(self._log, indent=2, sort_keys=True))
        eveui.fade_in(self._bg_fill, end_value=0.05, duration=0.1)

    def OnMouseExit(self, *args):
        if self._log['type'] == 'node':
            self._controller.unhighlight_node(self._log['info']['node_id'])
        eveui.fade_out(self._bg_fill, duration=0.1)

    def GetMenu(self):
        return [('Copy', blue.pyos.SetClipboardData(self.hint))]


def format_log_label(log):
    if log['type'] == 'node':
        info = log['info']['node_id']
    elif log['type'] == 'blackboard' and log['event'] == 'update':
        info = log['info']['key']
    elif log['type'] == 'graph':
        info = ''
    else:
        info = ''
    return u'{} - {} - {}'.format(log['type'], log['event'], info)
