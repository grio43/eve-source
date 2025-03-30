#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Progress\ProgressWnd.py
import uthread2
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'
    description = 'In most cases we should be using contextual loading indication instead of this pop-up approach'

    def sample_code(self, parent):
        from eve.client.script.ui.shared.progressWnd import ProgressWnd
        numSteps = 5
        for i in xrange(1, numSteps + 1):
            sm.GetService('loading').ProgressWnd('Title', 'Step %s / %s' % (i, numSteps), i, numSteps, useMorph=True)
            uthread2.sleep(0.5)
