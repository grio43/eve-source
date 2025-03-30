#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\button.py
from .base import Action

class ShowButton(Action):
    atom_id = 361

    def __init__(self, caption = None, button_text = None, node_graph_id = None, message_key = None, message_value = None, **kwargs):
        super(ShowButton, self).__init__(**kwargs)
        self.caption = caption
        self.button_text = button_text
        self.node_graph_id = node_graph_id
        self.message_key = message_key
        self.message_value = message_value
        self._button = None

    def start(self, **kwargs):
        super(ShowButton, self).start(**kwargs)
        self._construct_button()

    def stop(self):
        super(ShowButton, self).stop()
        self._close_button()

    def _construct_button(self):
        from nodegraph.client.ui.simplebuttonwindow import SimpleButtonWindow
        self._button = SimpleButtonWindow(caption=self.caption, button_text=self.button_text, on_click_function=self._on_click_function)

    def _close_button(self):
        if self._button and not self._button.destroyed:
            self._button.Close()

    def _get_node_graph(self):
        return sm.GetService('node_graph').get_active_node_graph_by_id(self.node_graph_id)

    def _on_click_function(self):
        node_graph = self._get_node_graph()
        if node_graph:
            node_graph.context.send_message(self.message_key, self.message_value)

    @classmethod
    def get_subtitle(cls, button_text = None, **kwargs):
        return str(button_text)


class HideButton(Action):
    atom_id = 362

    def __init__(self, button_text = None, **kwargs):
        super(HideButton, self).__init__(**kwargs)
        self.button_text = button_text

    def start(self, **kwargs):
        super(HideButton, self).start(**kwargs)
        button_window = self._get_button_window()
        if button_window and not button_window.destroyed:
            button_window.Close()

    def _get_button_window(self):
        from nodegraph.client.ui.simplebuttonwindow import get_simple_button_window_by_button_text
        return get_simple_button_window_by_button_text(self.button_text)

    @classmethod
    def get_subtitle(cls, button_text = None, **kwargs):
        return str(button_text)
