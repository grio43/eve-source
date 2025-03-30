#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\history\page.py
import eveformat.client
import eveui
from raffles.client.localization import Text
from raffles.client.widget.banner_background import BannerBackground
from raffles.client.widget.virtual_list import VirtualList
from raffles.client.widget.dotted_progress import DottedProgress
from .list_item import RaffleListItem
from .banner import Banner
from .filter import Filter

class HistoryPage(eveui.Container):
    default_name = 'RafflesHistoryPage'

    def __init__(self, window_controller, background_layer, **kwargs):
        super(HistoryPage, self).__init__(**kwargs)
        self._controller = window_controller.history_page_controller
        self._navigation = window_controller.navigation_controller
        self._background_layer = background_layer
        self._layout()
        self.loading_indicator = None
        self._navigation.current_page_title = Text.page_title_history()
        self._controller.on_raffles_changed.connect(self._on_raffles_changed)
        if self._controller.fetching_raffles:
            self._construct_loading_indicator()
            self.loading_indicator.Show()
        else:
            self._controller.page_open()

    def Close(self):
        try:
            self._controller.filters.scroll_position = self.raffles_list.GetPositionVertical()
        finally:
            super(HistoryPage, self).Close()
            self._controller.on_raffles_changed.disconnect(self._on_raffles_changed)

    def _on_raffles_changed(self):
        if self.loading_indicator:
            eveui.fade(self.raffles_list, start_value=0, end_value=1, duration=0.5)
            self.loading_indicator.Close()
            self.loading_indicator = None
        load_scroll_pos = self.raffles_list.data is None
        self.raffles_list.data = self._controller.filtered_raffles
        if load_scroll_pos:
            self.raffles_list.scrollToVerticalPending = self._controller.filters.scroll_position
        else:
            self.raffles_list.ScrollToVertical(0)
        self._update_no_data_label()
        self.filter.update_filtered_count(self._controller.filtered_count, self._controller.total_count)

    def _layout(self):
        Banner(parent=self, stats=self._controller.stats)
        self._construct_filter()
        self.raffles_list = VirtualList(parent=self, align=eveui.Align.to_all, pushContent=True, render_item=self._render_list_item)
        self.no_data_label = eveui.EveCaptionSmall(parent=self, align=eveui.Align.to_top_no_push, state=eveui.State.hidden, top=20, opacity=0.5, text=eveformat.center(Text.no_data_available()))
        BannerBackground(parent=self._background_layer)

    def _render_list_item(self):
        return RaffleListItem(navigation=self._navigation)

    def _construct_filter(self):
        self.filter = Filter(parent=self, controller=self._controller.filters, top=24)
        container = eveui.Container(parent=self, align=eveui.Align.to_top, height=30, padTop=24, padBottom=12)

    def _construct_loading_indicator(self):
        container = eveui.Container(parent=self, align=eveui.Align.to_all)
        self.loading_indicator = DottedProgress(parent=container, align=eveui.Align.center)
        self.loading_indicator.Show()

    def _update_no_data_label(self):
        if self._controller.filtered_raffles:
            self.no_data_label.Hide()
        else:
            self.no_data_label.Show()
