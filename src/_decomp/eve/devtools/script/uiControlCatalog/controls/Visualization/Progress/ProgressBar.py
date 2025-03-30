#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Progress\ProgressBar.py
import carbonui.const as uiconst
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from carbonui.control.progressBar import ProgressBar
        ProgressBar(parent=parent, align=uiconst.TOPLEFT, width=200, height=8)


class Sample2(Sample):
    name = 'Thicker bars'

    def sample_code(self, parent):
        from carbonui.control.progressBar import ProgressBar
        ProgressBar(parent=parent, align=uiconst.TOPLEFT, width=200, height=16, barWidth=16)


class Sample3(Sample):
    name = 'Thinner bars'

    def sample_code(self, parent):
        from carbonui.control.progressBar import ProgressBar
        ProgressBar(parent=parent, align=uiconst.TOPLEFT, width=200, height=8, barWidth=2)
