#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\configuration_window.py
from carbonui import Align, IdealSize
from carbonui.control.window import Window
import eveicon
from sovereignty.mercenaryden.client import mercenary_den_signals
from sovereignty.mercenaryden.client.ui import ui_signals
from sovereignty.mercenaryden.client.ui.containers.reload import ReloadContainer
from sovereignty.mercenaryden.client.ui.containers.summary import SummaryContainer
from sovereignty.mercenaryden.client.ui.containers.tabs import TabsContainer
from sovereignty.mercenaryden.client.ui.controller import MercenaryDenController
from sovereignty.mercenaryden.client.ui.qa import add_qa_menu
from uthread2 import StartTasklet, debounce

@debounce(leading=True)
def open_mercenary_den_window(item_id, type_id):
    window = MercenaryDenWindow.GetIfOpen()
    if window and not window.destroyed:
        window.Maximize()
    else:
        MercenaryDenWindow.Open(item_id=item_id, type_id=type_id)


class MercenaryDenWindow(Window):
    __guid__ = 'MercenaryDenWindow'
    default_windowID = 'mercenaryDenWindow'
    default_iconNum = eveicon.mercenary_den_product_icon
    FIXED_HEIGHT_WITHOUT_WARNINGS = IdealSize.SIZE_410
    MIN_WIDTH = IdealSize.SIZE_410
    MAX_WIDTH = IdealSize.SIZE_720
    default_width = MIN_WIDTH
    default_height = FIXED_HEIGHT_WITHOUT_WARNINGS
    default_minSize = (MIN_WIDTH, FIXED_HEIGHT_WITHOUT_WARNINGS)
    default_maxSize = (MAX_WIDTH, FIXED_HEIGHT_WITHOUT_WARNINGS)
    default_apply_content_padding = False
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self, item_id, type_id, *args, **kwargs):
        self._controller = MercenaryDenController(item_id, type_id)
        if not self._controller.is_observable:
            return
        self._is_paused = False
        self._header_container = None
        self._tabs_container = None
        self._reload_container = None
        super(MercenaryDenWindow, self).__init__(*args, **kwargs)
        self._connect_signals()
        StartTasklet(self._construct_layout)

    def Close(self, *args, **kwargs):
        self._disconnect_signals()
        self._controller.clear()
        self._controller = None
        super(MercenaryDenWindow, self).Close(*args, **kwargs)

    def _connect_signals(self):
        mercenary_den_signals.on_feature_version_changed.connect(self._reload_content)
        mercenary_den_signals.on_mercenary_den_changed.connect(self._reload_content)
        ui_signals.on_qa_settings_changed.connect(self._qa_close_and_reopen_window)

    def _disconnect_signals(self):
        mercenary_den_signals.on_feature_version_changed.disconnect(self._reload_content)
        mercenary_den_signals.on_mercenary_den_changed.disconnect(self._reload_content)
        ui_signals.on_qa_settings_changed.disconnect(self._qa_close_and_reopen_window)

    def GetMenuMoreOptions(self):
        menu_data = super(MercenaryDenWindow, self).GetMenuMoreOptions()
        add_qa_menu(menu_data, reload=self._qa_close_and_reopen_window)
        return menu_data

    def OnSessionChanged(self, isRemote, session, change):
        if 'solarsystemid' in change or 'structureid' in change:
            self.Close()

    def _construct_layout(self):
        if self.destroyed:
            return
        self._construct_caption()
        self._construct_header()
        self._construct_tabs()
        self._construct_failed_to_load()

    def _construct_caption(self):
        self.caption = self._controller.get_mercenary_den_name()

    def _construct_header(self):
        has_header_container = self._header_container and not self._header_container.destroyed
        if self._controller.mercenary_den:
            if not has_header_container:
                self._header_container = SummaryContainer(name='header_container', parent=self.content, align=Align.TOTOP, controller=self._controller, should_show_owner=True, should_show_skyhook_owner=True, should_show_infomorphs_collected=False, should_show_workforce_cost=True)
            self._header_container.display = True
            self._header_container.load_controller(self._controller)
        elif has_header_container:
            self._header_container.display = False

    def _construct_tabs(self):
        has_tabs_container = self._tabs_container and not self._tabs_container.destroyed
        if self._controller.mercenary_den:
            if not has_tabs_container:
                self._tabs_container = TabsContainer(name='tabs_container', parent=self.content, align=Align.TOTOP, controller=self._controller, callback=self._on_tabs_size_changed, only_use_callback_when_size_changes=True)
            self._tabs_container.display = True
            self._tabs_container.load_controller(self._controller)
        elif has_tabs_container:
            self._tabs_container.display = False

    def _construct_failed_to_load(self):
        has_reload_container = self._reload_container and not self._reload_container.destroyed
        if self._controller.mercenary_den:
            if has_reload_container:
                self._reload_container.display = False
        else:
            if not has_reload_container:
                self._reload_container = ReloadContainer(name='reload_container', parent=self.content, align=Align.TOTOP, reload=self._reload_content)
            self._reload_container.display = True

    def _update_sizes(self):
        if self.collapsed:
            return
        if self._controller.mercenary_den:
            if self._header_container and not self._header_container.destroyed and self._tabs_container and not self._tabs_container.destroyed:
                self._header_container.update_height()
                self._tabs_container.set_width(self.width)
                self._update_height(self._header_container.height + self._tabs_container.height)
        elif self._reload_container and not self._reload_container.destroyed:
            self._update_height(self._reload_container.height)

    def _update_height(self, height):
        if self.stacked:
            height += self.stack.header_height
        self.SetFixedHeightFromContentHeight(height)
        self.SetMinSize((self.minsize[0], height))

    def _reload_content(self, *args):
        if self.destroyed:
            return
        self._controller.reload_data()
        StartTasklet(self._construct_layout)

    def _qa_close_and_reopen_window(self, *args):
        item_id = self._controller.item_id
        type_id = self._controller.type_id
        self.Close()
        open_mercenary_den_window(item_id, type_id)

    def OnResizeUpdate(self, *args):
        if self.destroyed:
            return
        self._update_sizes()

    def OnEndMinimize_(self, *args):
        self._controller.pause()

    def OnStartMaximize_(self, *args):
        self._controller.resume()

    def _on_tabs_size_changed(self, *args):
        self._update_sizes()

    def OnGlobalFontSizeChanged(self):
        if self.destroyed:
            return
        self._qa_close_and_reopen_window()
