#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Progress\Gauge.py
import uthread2
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from eve.client.script.ui.control.gauge import Gauge
        gauge = Gauge(parent=parent, color=eveColor.DANGER_RED)
        gauge.SetValue(1.0)


class Sample2(Sample):
    name = 'Using markers'

    def sample_code(self, parent):
        from eve.client.script.ui.control.gauge import Gauge
        numMarkers = 5
        gauge = Gauge(parent=parent, color=eveColor.LEAFY_GREEN)
        for i in xrange(1, numMarkers):
            gauge.ShowMarker(float(i) / numMarkers, color=(0, 0, 0, 0.3))

        for i in xrange(1, numMarkers + 1):
            gauge.SetValue(float(i) / numMarkers)
            uthread2.sleep(1.2)


class Sample3(Sample):
    name = 'Multi Value'

    def sample_code(self, parent):
        from eve.client.script.ui.control.gauge import GaugeMultiValue
        gauge = GaugeMultiValue(parent=parent, colors=(eveColor.BURNISHED_GOLD, eveColor.SAND_YELLOW), values=(0.0, 0.0))
        gauge.SetValue(0, 0.3)
        gauge.SetValue(1, 0.7)
