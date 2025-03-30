#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\create\statistics.py
import eveformat
import eveui
from raffles.client.localization import Text
from raffles.client.widget.dotted_progress import DottedProgress
from .label_value import LabelValue

class Statistics(eveui.Container):

    def __init__(self, controller, **kwargs):
        super(Statistics, self).__init__(**kwargs)
        self._controller = controller
        self._layout()
        self._controller.on_statistics_changed.connect(self._on_statistics_changed)

    def Close(self):
        super(Statistics, self).Close()
        self._controller.on_statistics_changed.disconnect(self._on_statistics_changed)

    def _on_statistics_changed(self):
        self.Flush()
        self._layout()

    def _layout(self):
        if not self._controller.statistics_fetched:
            DottedProgress(parent=self, align=eveui.Align.center, dot_size=6, wait_time=0.5).Show()
            opacity = 0.3
        else:
            opacity = 1.0
        content_container = eveui.Container(parent=self, align=eveui.Align.to_all, opacity=opacity)
        historical_container = eveui.Container(parent=content_container, align=eveui.Align.to_top, height=82)
        self._construct_section(historical_container, Text.historical_statistics(), 'historic')
        active_container = eveui.Container(parent=content_container, align=eveui.Align.to_bottom, height=82)
        self._construct_section(active_container, Text.active_statistics(), 'active')

    def _construct_section(self, container, label, prefix):
        label = eveui.EveLabelMedium(parent=container, align=eveui.Align.to_top, text=label, padBottom=6)
        count = self._get_count(prefix + '_count')
        if count:
            label.text += u' ({})'.format(count)
        LabelValue(parent=container, align=eveui.Align.to_top, label=Text.maximum_price(), value=self._format_price(prefix + '_max'))
        LabelValue(parent=container, align=eveui.Align.to_top, label=Text.minimum_price(), value=self._format_price(prefix + '_min'))
        LabelValue(parent=container, align=eveui.Align.to_top, label=Text.average_price(), value=self._format_price(prefix + '_average'))

    def _format_price(self, key):
        if not self._controller.statistics or not self._controller.statistics[key]:
            return '-'
        return eveformat.isk_readable(self._controller.statistics[key])

    def _get_count(self, key):
        if not self._controller.statistics:
            return 0
        return self._controller.statistics[key] or 0
