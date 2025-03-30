#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\containers\cargo_item_icon.py
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import Align, TextDetail, PickState
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.control.itemIcon import ItemIcon
from gametime import DAY, HOUR, MIN, SEC
from localization import GetByLabel
from localization.formatters.timeIntervalFormatters import FormatTimeIntervalShortWritten
from logging import getLogger
logger = getLogger('mercenary_den')

class CargoItemIcon(Container):
    LABEL_PATH_TIMER_TOOLTIP = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/TimerTooltip'
    CONTAINER_SIZE = 64
    ICON_SIZE = 44
    LINE_WIDTH_CIRCULAR_GAUGE = 2.0
    COLOR_CIRCULAR_GAUGE_START = eveThemeColor.THEME_FOCUS
    COLOR_CIRCULAR_GAUGE_END = eveThemeColor.THEME_FOCUS
    COLOR_CIRCULAR_GAUGE_BACKGROUND = (0.0, 0.0, 0.0, 0.0)
    MSECS_BETWEEN_TIMER_UPDATES = 500
    default_width = CONTAINER_SIZE
    default_height = CONTAINER_SIZE

    def __init__(self, controller, *args, **kwargs):
        self._controller = controller
        self.amount_available = 0
        self._update_timer_thread = None
        super(CargoItemIcon, self).__init__(*args, **kwargs)
        self._construct_content()

    def Close(self):
        self._stop_timer()
        super(CargoItemIcon, self).Close()

    def _construct_content(self):
        self._icon = ItemIcon(name='cargo_item_icon', parent=self, align=Align.CENTER, width=self.ICON_SIZE, height=self.ICON_SIZE, pickState=PickState.OFF)
        self._gauge = GaugeCircular(name='cargo_item_time_gauge', parent=self, align=Align.CENTER, clockwise=False, showMarker=False, radius=self.width / 2, lineWidth=self.LINE_WIDTH_CIRCULAR_GAUGE, colorStart=self.COLOR_CIRCULAR_GAUGE_START, colorEnd=self.COLOR_CIRCULAR_GAUGE_END, colorBg=self.COLOR_CIRCULAR_GAUGE_BACKGROUND, pickState=PickState.OFF)
        time_text_container = ContainerAutoSize(name='cargo_item_time_text_container', parent=self, align=Align.HORIZONTALLY_CENTERED, width=self.width - self.width / 4, clipChildren=True, alignMode=Align.TOTOP)
        self._time_text = TextDetail(name='cargo_item_time_text', parent=time_text_container, align=Align.CENTER, pickState=PickState.OFF, display=False, maxWidth=time_text_container.width)
        self.hint = GetByLabel(self.LABEL_PATH_TIMER_TOOLTIP)

    def _update_timer(self):
        time_left, tick_progress = self._controller.get_infomorph_tick_progress()
        self._gauge.SetValue(tick_progress)
        seconds_left = time_left * SEC
        if seconds_left > DAY:
            show_from = 'day'
            show_to = 'hour'
        elif seconds_left > HOUR:
            show_from = 'hour'
            show_to = 'minute'
        elif seconds_left > 10 * MIN:
            show_from = 'minute'
            show_to = 'minute'
        elif seconds_left > MIN:
            show_from = 'minute'
            show_to = 'second'
        else:
            show_from = 'second'
            show_to = 'second'
        self._time_text.text = FormatTimeIntervalShortWritten(seconds_left, showFrom=show_from, showTo=show_to)

    def _start_timer(self):
        self._stop_timer()
        logger.info('UI: Cargo Item: Starting autoupdates for timer every %s msecs', self.MSECS_BETWEEN_TIMER_UPDATES)
        self._update_timer_thread = AutoTimer(self.MSECS_BETWEEN_TIMER_UPDATES, self._update_timer)

    def _stop_timer(self):
        if self._update_timer_thread:
            logger.info('UI: Cargo Item: Stopping autoupdates for timer every %s msecs', self.MSECS_BETWEEN_TIMER_UPDATES)
            self._update_timer_thread.KillTimer()

    def load(self, amount):
        self.amount_available = amount
        type_id = self._controller.get_infomorph_type_id()
        self._icon.SetTypeID(type_id)
        self._start_timer()

    def OnMouseEnter(self, *args):
        self._icon.display = False
        self._time_text.display = True

    def OnMouseExit(self, *args):
        self._icon.display = True
        self._time_text.display = False
