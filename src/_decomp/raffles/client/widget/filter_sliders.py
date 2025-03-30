#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\filter_sliders.py
import eveformat
import eveui
import threadutils
from raffles.client import texture

class TicketCountSlider(eveui.ContainerAutoSize):
    default_align = eveui.Align.to_top

    def __init__(self, parent, filter_controller, **kwargs):
        self._controller = filter_controller
        super(TicketCountSlider, self).__init__(parent=parent, **kwargs)
        self._layout()

    def _layout(self):
        increments = self._controller.ticket_count_increments
        value = self._controller.ticket_count
        if any((count not in increments for count in value)):
            value = (increments[0], increments[-1])
        self._slider = eveui.OptionSlider(parent=self, align=eveui.Align.to_top, height=28, value=value, options=increments, show_mark_label=True, on_change_committed=self._on_ticket_count_changed)

    @threadutils.throttled(1.0)
    def _on_ticket_count_changed(self, value):
        self._controller.ticket_count = value

    def __getattr__(self, name):
        return getattr(self._slider, name)


class TicketPriceSlider(eveui.ContainerAutoSize):
    default_align = eveui.Align.to_top

    def __init__(self, parent, filter_controller, **kwargs):
        self._controller = filter_controller
        super(TicketPriceSlider, self).__init__(parent=parent, **kwargs)
        self._layout()

    def _layout(self):
        increments = self._controller.ticket_price_increments
        value = self._controller.ticket_price
        if any((count not in increments for count in value)):
            value = (increments[0], increments[-1])
        self._slider = eveui.OptionSlider(parent=self, align=eveui.Align.to_top, height=28, value=value, options=increments, min_distance=1, show_mark_label=True, mark_label_format=self._format_price_label, on_change=self._update_infinity, on_change_committed=self._on_ticket_price_changed)
        self._infinity = eveui.Sprite(parent=self._slider, align=eveui.Align.top_right, texturePath=texture.infinity, pos=(-4, 8, 16, 16), opacity=self._get_mark_opacity(value))

    def _format_price_label(self, value):
        if value is not None:
            return eveformat.number_readable_short(value)

    @threadutils.throttled(1.0)
    def _on_ticket_price_changed(self, value):
        self._controller.ticket_price = value

    def _update_infinity(self, value):
        self._infinity.opacity = self._get_mark_opacity(value)

    def _get_mark_opacity(self, value):
        if value[1] is None:
            return 0.8
        return 0.25

    def __getattr__(self, name):
        return getattr(self._slider, name)
