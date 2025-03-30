#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\fitting.py
from .base import Event

class FittingWindowAttributeChanged(Event):
    atom_id = 296
    __notifyevents__ = ['OnExpandableMenuItemExpanded', 'OnExpandableMenuItemCollapsed']

    def __init__(self, *args, **kwargs):
        super(FittingWindowAttributeChanged, self).__init__(*args, **kwargs)
        self._fitting_window_attribute_menus = None

    @property
    def fitting_window_attribute_menus(self):
        if self._fitting_window_attribute_menus is None:
            from eve.client.script.ui.shared.fittingScreen.statsPanel import MENU_NAME_BY_UI_NAME
            self._fitting_window_attribute_menus = MENU_NAME_BY_UI_NAME.values()
        return self._fitting_window_attribute_menus

    def is_fitting_window_attribute_menu(self, menu_name):
        return menu_name in self.fitting_window_attribute_menus

    def OnExpandableMenuItemExpanded(self, menu_name):
        self._on_expandable_menu_item_changed(menu_name)

    def OnExpandableMenuItemCollapsed(self, menu_name):
        self._on_expandable_menu_item_changed(menu_name)

    def _on_expandable_menu_item_changed(self, menu_name):
        if self.is_fitting_window_attribute_menu(menu_name):
            self.invoke(menu_name=menu_name)


class FittingWindowTabChange(Event):
    atom_id = 551
    __notifyevents__ = ['OnFittingWindowTabChange']

    def __init__(self, *args, **kwargs):
        super(FittingWindowTabChange, self).__init__(*args, **kwargs)

    def OnFittingWindowTabChange(self, tab_id):
        self.invoke(tab_id=tab_id)
