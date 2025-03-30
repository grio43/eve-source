#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\highlights.py
from evetypes import GetGroupNameByGroup, GetName
from uihighlighting.fsdloaders import MenuHighlightsLoader
from uihighlighting.fsdloaders import SpaceObjectHighlightsLoader
from uihighlighting.fsdloaders import UIHighlightsLoader
from .base import Action

def get_ui_highlight_name(highlight_id):
    if highlight_id:
        return UIHighlightsLoader.GetByID(highlight_id).name
    return ''


def get_space_object_highlight_info(highlight_id, object_id, entity_group_id, item_id, type_id, group_id):
    attributes_dict = {'object_id': object_id,
     'entity_group_id': entity_group_id,
     'item_id': item_id,
     'type_id': GetName(type_id) if type_id else None,
     'group_id': GetGroupNameByGroup(group_id) if group_id else None}
    attributes_string = ', '.join([ '{name}: {value}'.format(name=attribute_name, value=attribute_value) for attribute_name, attribute_value in attributes_dict.items() if attribute_value is not None ])
    if highlight_id:
        highlight_name = SpaceObjectHighlightsLoader.GetByID(highlight_id).name
        if attributes_string:
            return '{highlight_name} ({attributes})'.format(highlight_name=highlight_name, attributes=attributes_string)
        return highlight_name
    return attributes_string


class ClearAllUiHighlights(Action):
    atom_id = 122

    def start(self, **kwargs):
        super(ClearAllUiHighlights, self).start(**kwargs)
        sm.GetService('uiHighlightingService').clear_all_highlighting()


class ClearMenuItemHighlights(Action):
    atom_id = 15

    def start(self, **kwargs):
        super(ClearMenuItemHighlights, self).start(**kwargs)
        sm.GetService('uiHighlightingService').clear_menu_highlighting()


class ClearSpaceObjectHighlights(Action):
    atom_id = 16

    def start(self, **kwargs):
        super(ClearSpaceObjectHighlights, self).start(**kwargs)
        sm.GetService('uiHighlightingService').clear_space_object_highlighting()


class ClearUiElementHighlights(Action):
    atom_id = 17

    def start(self, **kwargs):
        super(ClearUiElementHighlights, self).start(**kwargs)
        sm.GetService('uiHighlightingService').clear_ui_element_highlighting()


class HighlightMenuItem(Action):
    atom_id = 12

    def __init__(self, highlight_id = None, **kwargs):
        super(HighlightMenuItem, self).__init__(**kwargs)
        self.highlight_id = highlight_id

    def start(self, **kwargs):
        super(HighlightMenuItem, self).start(**kwargs)
        if self.highlight_id:
            sm.GetService('uiHighlightingService').highlight_menu_by_ids([self.highlight_id])

    def stop(self):
        super(HighlightMenuItem, self).stop()
        sm.GetService('uiHighlightingService').clear_menu_highlighting()

    @classmethod
    def get_subtitle(cls, highlight_id = None, **kwargs):
        if highlight_id:
            return MenuHighlightsLoader.GetByID(highlight_id).name
        return ''


class HighlightSpaceObject(Action):
    atom_id = 13

    def __init__(self, highlight_id = None, object_id = None, entity_group_id = None, item_id = None, type_id = None, group_id = None, **kwargs):
        super(HighlightSpaceObject, self).__init__(**kwargs)
        self.highlight_id = highlight_id
        self.object_id = object_id
        self.entity_group_id = entity_group_id
        self.item_id = item_id
        self.type_id = type_id
        self.group_id = group_id

    def start(self, **kwargs):
        super(HighlightSpaceObject, self).start(**kwargs)
        sm.GetService('uiHighlightingService').highlight_space_object(self.highlight_id, self.object_id, self.entity_group_id, self.type_id, self.group_id, self.item_id)

    def stop(self):
        super(HighlightSpaceObject, self).stop()
        sm.GetService('uiHighlightingService').clear_space_object_highlight(self.highlight_id, self.object_id, self.entity_group_id, self.type_id, self.group_id, self.item_id)

    @classmethod
    def get_subtitle(cls, highlight_id = None, object_id = None, entity_group_id = None, item_id = None, type_id = None, group_id = None, **kwargs):
        return get_space_object_highlight_info(highlight_id, object_id, entity_group_id, item_id, type_id, group_id)


class ClearSpaceObjectHighlight(Action):
    atom_id = 178

    def __init__(self, highlight_id = None, object_id = None, entity_group_id = None, item_id = None, type_id = None, group_id = None, **kwargs):
        super(ClearSpaceObjectHighlight, self).__init__(**kwargs)
        self.highlight_id = highlight_id
        self.object_id = object_id
        self.entity_group_id = entity_group_id
        self.item_id = item_id
        self.type_id = type_id
        self.group_id = group_id

    def start(self, **kwargs):
        super(ClearSpaceObjectHighlight, self).start(**kwargs)
        sm.GetService('uiHighlightingService').clear_space_object_highlight(self.highlight_id, self.object_id, self.entity_group_id, self.type_id, self.group_id, self.item_id)

    @classmethod
    def get_subtitle(cls, highlight_id = None, object_id = None, entity_group_id = None, item_id = None, type_id = None, group_id = None, **kwargs):
        return get_space_object_highlight_info(highlight_id, object_id, entity_group_id, item_id, type_id, group_id)


class HighlightUiElement(Action):
    atom_id = 14

    def __init__(self, highlight_id = None, ui_element_name = None, **kwargs):
        super(HighlightUiElement, self).__init__(**kwargs)
        self.highlight_id = highlight_id
        self.ui_element_name = ui_element_name

    def _get_highlighting_service(self):
        return sm.GetService('uiHighlightingService')

    def start(self, **kwargs):
        super(HighlightUiElement, self).start(**kwargs)
        if self.highlight_id:
            highlighting_service = self._get_highlighting_service()
            if self.ui_element_name:
                highlighting_service.highlight_ui_element_by_id_and_name(self.highlight_id, self.ui_element_name)
            else:
                highlighting_service.highlight_ui_element(self.highlight_id)

    def stop(self):
        super(HighlightUiElement, self).stop()
        if self.highlight_id:
            highlighting_service = self._get_highlighting_service()
            if self.ui_element_name:
                highlighting_service.remove_highlight_from_ui_element_by_name(self.ui_element_name)
            else:
                highlighting_service.remove_highlight_from_ui_element_by_id(self.highlight_id)

    @classmethod
    def get_subtitle(cls, highlight_id = None, **kwargs):
        return get_ui_highlight_name(highlight_id)


class ClearUiElementHighlight(Action):
    atom_id = 179

    def __init__(self, highlight_id = None, **kwargs):
        super(ClearUiElementHighlight, self).__init__(**kwargs)
        self.highlight_id = highlight_id

    def start(self, **kwargs):
        super(ClearUiElementHighlight, self).start(**kwargs)
        if self.highlight_id:
            sm.GetService('uiHighlightingService').remove_highlight_from_ui_element_by_id(self.highlight_id)

    @classmethod
    def get_subtitle(cls, highlight_id = None, **kwargs):
        return get_ui_highlight_name(highlight_id)


class HighlightSpaceObjectCommand(Action):
    atom_id = 471

    def __init__(self, command_name = None, stop_on_click = None, item_id = None, type_id = None, group_id = None, **kwargs):
        super(HighlightSpaceObjectCommand, self).__init__(**kwargs)
        self.command_name = command_name
        self.stop_on_click = self.get_atom_parameter_value('stop_on_click', stop_on_click)
        self.item_id = item_id
        self.type_id = type_id
        self.group_id = group_id
        self._event = None
        self._condition = None
        self._highlight = None
        self._on_click_event = None

    def start(self, **kwargs):
        super(HighlightSpaceObjectCommand, self).start(**kwargs)
        if not self.command_name:
            return
        from nodegraph.client.actions.blinks import BlinkUiElement
        from nodegraph.client.conditions.target import SpaceObjectSelected
        from nodegraph.client.events.target import SpaceObjectSelectionChanged
        from nodegraph.client.events.ui import SelectedItemButtonClicked
        self._condition = SpaceObjectSelected(item_id=self.item_id, type_id=self.type_id, group_id=self.group_id)
        self._highlight = BlinkUiElement(ui_element_path='selectedItem{}'.format(self.command_name))
        self._event = SpaceObjectSelectionChanged(self._selection_changed, keep_listening=True)
        self._event.start()
        if self.stop_on_click:
            self._on_click_event = SelectedItemButtonClicked(self._selected_item_button_clicked, keep_listening=True)
            self._on_click_event.start()
        self._selection_changed()

    def stop(self):
        if self._event:
            self._event.stop()
            self._event = None
        if self._highlight:
            self._highlight.stop()
            self._highlight = None
        if self._condition:
            self._condition = None
        if self._on_click_event:
            self._on_click_event.stop()
            self._on_click_event = None

    def _selection_changed(self, *args, **kwargs):
        if self._condition.validate():
            self._highlight.start()
        else:
            self._highlight.stop()

    def _selected_item_button_clicked(self, command_name):
        if self.stop_on_click and self.command_name == command_name and self._condition.validate():
            self.stop()
            self._on_end()

    @classmethod
    def get_subtitle(cls, command_name = None, **kwargs):
        return command_name
