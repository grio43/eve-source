#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\blinks.py
import uiblinker
from .base import Action
NODE_GRAPH_UI_BLINKER_GROUP_NAME = 'global'

class ClearAllUiBlinks(Action):
    atom_id = 274

    def start(self, **kwargs):
        super(ClearAllUiBlinks, self).start(**kwargs)
        store = uiblinker.get_service().get_node_graph_blinker_store()
        store.stop_all_blinkers()


class BlinkUiElement(Action):
    atom_id = 273

    def __init__(self, blink_type = None, ui_element_path = None, **kwargs):
        super(BlinkUiElement, self).__init__(**kwargs)
        self.blink_type = getattr(uiblinker.BlinkerType, self.get_atom_parameter_value('blink_type', blink_type))
        self.ui_element_path = ui_element_path

    def start(self, **kwargs):
        super(BlinkUiElement, self).start(**kwargs)
        if self.ui_element_path:
            store = uiblinker.get_service().get_node_graph_blinker_store()
            store.start_blinker_by_path(ui_element_path=self.ui_element_path, blinker_type=self.blink_type, group=NODE_GRAPH_UI_BLINKER_GROUP_NAME)

    def stop(self):
        super(BlinkUiElement, self).stop()
        if self.ui_element_path:
            store = uiblinker.get_service().get_node_graph_blinker_store()
            store.stop_blinker_by_path(self.ui_element_path)

    @classmethod
    def get_subtitle(cls, blink_type = None, ui_element_path = None, **kwargs):
        return '{} [{}]'.format(ui_element_path or '', cls.get_atom_parameter_value('blink_type', blink_type))


class BlinkUiElementByUniqueName(Action):
    atom_id = 479

    def __init__(self, blink_type = None, unique_ui_name = None, chain_blinks = None, **kwargs):
        super(BlinkUiElementByUniqueName, self).__init__(**kwargs)
        self.blink_type = getattr(uiblinker.BlinkerType, self.get_atom_parameter_value('blink_type', blink_type))
        self.unique_ui_name = unique_ui_name
        self.chain_blinks = self.get_atom_parameter_value('chain_blinks', chain_blinks)

    def start(self, **kwargs):
        super(BlinkUiElementByUniqueName, self).start(**kwargs)
        if self.unique_ui_name:
            store = uiblinker.get_service().get_node_graph_blinker_store()
            store.start_blinker_by_name(unique_ui_name=self.unique_ui_name, blinker_type=self.blink_type, group=NODE_GRAPH_UI_BLINKER_GROUP_NAME, chain_blinks=self.chain_blinks)

    def stop(self):
        super(BlinkUiElementByUniqueName, self).stop()
        if self.unique_ui_name:
            store = uiblinker.get_service().get_node_graph_blinker_store()
            store.stop_blinker_by_path(self.unique_ui_name)

    @classmethod
    def get_subtitle(cls, blink_type = None, unique_ui_name = None, chain_blinks = None, **kwargs):
        return '{} [{} {}]'.format(unique_ui_name or '', cls.get_atom_parameter_value('chain_blinks', chain_blinks), cls.get_atom_parameter_value('blink_type', blink_type))


class ClearUiElementBlink(Action):
    atom_id = 275

    def __init__(self, ui_element_path = None, **kwargs):
        super(ClearUiElementBlink, self).__init__(**kwargs)
        self.ui_element_path = ui_element_path

    def start(self, **kwargs):
        super(ClearUiElementBlink, self).start(**kwargs)
        if self.ui_element_path:
            store = uiblinker.get_service().get_node_graph_blinker_store()
            store.stop_blinker_by_path(self.ui_element_path, group=NODE_GRAPH_UI_BLINKER_GROUP_NAME)

    @classmethod
    def get_subtitle(cls, ui_element_path = None, **kwargs):
        return str(ui_element_path)
