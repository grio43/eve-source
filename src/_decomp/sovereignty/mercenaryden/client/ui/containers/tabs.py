#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\containers\tabs.py
from carbonui import Align
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from localization import GetByLabel
from sovereignty.mercenaryden.client.ui.containers.cargo import CargoContainer
from sovereignty.mercenaryden.client.ui.containers.management import ManagementContainer

class Tab(object):
    TAB_CARGO = 'tab_cargo'
    TAB_MANAGEMENT = 'tab_management'


class TabsContainer(ContainerAutoSize):
    LABEL_PATH_TAB_CARGO = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/TabCargo'
    LABEL_PATH_TAB_MANAGEMENT = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/TabManagement'
    COLOR_BACKGROUND = eveColor.BLACK
    OPACITY_BACKGROUND = 0.0
    PADDING_CONTENT = 16
    PADDING_BOTTOM_TAB_GROUP = 16
    default_bgColor = (COLOR_BACKGROUND[0],
     COLOR_BACKGROUND[1],
     COLOR_BACKGROUND[2],
     OPACITY_BACKGROUND)

    def __init__(self, controller, *args, **kwargs):
        self._controller = controller
        super(TabsContainer, self).__init__(*args, **kwargs)
        self._construct_content()

    def _construct_content(self):
        self._content = ContainerAutoSize(name='content', parent=self, align=Align.TOTOP, padding=self.PADDING_CONTENT)
        self._construct_tab_group()
        self._construct_cargo()
        self._construct_management()
        self._construct_tabs()

    def _construct_tab_group(self):
        self._tab_group = ToggleButtonGroup(name='tab_group', parent=self._content, groupID='tab_group_configuration_window', align=Align.TOTOP, callback=self._on_tab_selected, padBottom=self.PADDING_BOTTOM_TAB_GROUP)

    def _construct_cargo(self):
        self._cargo = CargoContainer(name='cargo', parent=self._content, align=Align.TOTOP, display=False, controller=self._controller, should_show_name=False)

    def _construct_management(self):
        self._management = ManagementContainer(name='management', parent=self._content, align=Align.TOTOP, display=False, controller=self._controller)

    def _construct_tabs(self):
        self._tab_group.AddButton(label=GetByLabel(self.LABEL_PATH_TAB_CARGO), panel=self._cargo, btnID=Tab.TAB_CARGO)
        self._tab_group.AddButton(label=GetByLabel(self.LABEL_PATH_TAB_MANAGEMENT), panel=self._management, btnID=Tab.TAB_MANAGEMENT)

    def _get_last_selected_tab(self):
        return settings.char.ui.Get('MercenaryDen_ConfigurationWindow_LastSelectedTab', Tab.TAB_CARGO)

    def _set_last_selected_tab(self, tab_id):
        settings.char.ui.Set('MercenaryDen_ConfigurationWindow_LastSelectedTab', tab_id)

    def _on_tab_selected(self, tab_id, *args):
        if tab_id == Tab.TAB_CARGO:
            self._cargo.display = True
            self._management.display = False
        elif tab_id == Tab.TAB_MANAGEMENT:
            self._cargo.display = False
            self._management.display = True
        self._set_last_selected_tab(tab_id)

    def load_controller(self, controller):
        self._controller = controller
        self._cargo.load_controller(self._controller)
        self._management.load_controller(self._controller)
        self._content.SetSizeAutomatically()
        self.SetSizeAutomatically()
        last_selected_tab = self._get_last_selected_tab()
        self._tab_group.SetSelectedByID(last_selected_tab, animate=False)
        self._on_tab_selected(last_selected_tab)

    def set_width(self, width):
        self.width = width
        self._management.set_width(width - 2 * self.PADDING_CONTENT)
