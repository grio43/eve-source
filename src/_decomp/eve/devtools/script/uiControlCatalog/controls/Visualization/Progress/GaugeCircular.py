#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Progress\GaugeCircular.py
import uthread2
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from eve.client.script.ui.control.gaugeCircular import GaugeCircular
        gaugeCircular = GaugeCircular(parent=parent, colorStart=eveColor.WHITE, colorEnd=eveColor.BURNISHED_GOLD, radius=50)
        gaugeCircular.SetValue(1.0)
        uthread2.sleep(2.0)
        gaugeCircular.SetValue(0.0)


class Sample2(Sample):
    name = 'Counter clockwise and no marker'

    def sample_code(self, parent):
        from eve.client.script.ui.control.gaugeCircular import GaugeCircular
        gaugeCircular = GaugeCircular(parent=parent, clockwise=False, showMarker=False, radius=100, lineWidth=4.0)
        gaugeCircular.SetValue(0.75)
