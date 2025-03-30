#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\virtual_list.py
import eveui
import math
import threadutils

class VirtualList(eveui.ScrollContainer):
    default_name = 'VirtualList'

    def __init__(self, render_item, data = None, item_height = 0, overscan_count = 0, **kwargs):
        super(VirtualList, self).__init__(**kwargs)
        self._render_item = render_item
        self._item_height = item_height
        self._overscan_count = 3 + overscan_count
        self._extra_height = 0
        self.items = []
        self._top_index = None
        self._bottom_index = None
        self._last_fraction = 0.0
        self._force_rerender = False
        self._layout()
        self._data = None
        if data:
            self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self._force_rerender = True
        height = self._item_height * len(self.data)
        if self.items_container.height == height:
            self.OnScrolledVertical(self._last_fraction)
        else:
            self.items_container.height = height

    def scroll_to_index(self, index):
        item_position = index * self._item_height
        fraction = item_position / float(self.items_container.height - self._visible_height)
        self.ScrollToVertical(fraction)

    def _layout(self):
        self.items_container = eveui.Container(parent=self, align=eveui.Align.to_top)
        self._add_item()
        if not self._item_height:
            self._item_height = self.items[0].height + self.items[0].padBottom + self.items[0].padTop
        render_count = self._visible_height / self._item_height + self._overscan_count
        self._extra_height = (render_count * self._item_height - self._visible_height) * 0.5
        for _ in range(render_count - 1):
            self._add_item()

        self._top_index = 0
        self._bottom_index = render_count - 1

    def _add_item(self):
        item = self._render_item()
        item.align = eveui.Align.to_top_no_push
        item.SetParent(self.items_container)
        item.data_index = -1
        self.items.append(item)

    @threadutils.threaded
    def _render_all(self):
        top_position = self._get_top_position(self.GetPositionVertical())
        item_pos = top_position / self._item_height
        item_index = int(math.floor(item_pos))
        top_position -= (item_pos - item_index) * self._item_height
        max_index = len(self.data) - 1
        for index, item in enumerate(self.items):
            item.top = top_position
            if item_index <= max_index:
                item.data_index = item_index
                item.update_item(self.data[item_index])
            else:
                item.data_index = -1
                item.update_item(None)
            top_position += self._item_height
            item_index += 1

        self._top_index = 0
        self._bottom_index = len(self.items) - 1

    @property
    def _visible_height(self):
        return self.GetAbsoluteSize()[1]

    def OnScrolledVertical(self, fraction):
        self._check_render(fraction)

    def _check_render(self, fraction):
        if self._last_fraction == fraction and not self._force_rerender:
            return
        forced = self._force_rerender
        self._force_rerender = False
        scroll_distance = math.fabs(fraction - self._last_fraction) * self.items_container.height
        if forced or scroll_distance >= self._visible_height:
            self._render_all()
        elif self._last_fraction < fraction:
            self._scroll_down(fraction)
        elif self._last_fraction > fraction:
            self._scroll_up(fraction)
        self._last_fraction = fraction

    def _scroll_down(self, fraction):
        item = self.items[self._top_index]
        top_position = self._get_top_position(fraction) - self._extra_height
        if top_position >= item.top:
            data_index = self.items[self._bottom_index].data_index + 1
            if data_index >= len(self.data):
                return
            item.data_index = data_index
            item.top = data_index * self._item_height
            self._update_item(item)
            self._bottom_index = self._top_index
            self._top_index += 1
            if self._top_index >= len(self.items):
                self._top_index = 0
            self._check_render(fraction)

    def _scroll_up(self, fraction):
        item = self.items[self._bottom_index]
        bottom_position = self._get_bottom_position(fraction) + self._extra_height
        if bottom_position <= item.top:
            data_index = self.items[self._top_index].data_index - 1
            if data_index < 0:
                return
            item.data_index = data_index
            item.top = data_index * self._item_height
            self._update_item(item)
            self._top_index = self._bottom_index
            self._bottom_index -= 1
            if self._bottom_index < 0:
                self._bottom_index = len(self.items) - 1
            self._check_render(fraction)

    def _get_top_position(self, fraction):
        return fraction * (self.items_container.height - self._visible_height)

    def _get_bottom_position(self, fraction):
        return self._get_top_position(fraction) + self._visible_height

    @threadutils.threaded
    def _update_item(self, item):
        item.update_item(self.data[item.data_index])
