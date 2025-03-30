#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Sprites\Fill.py
import carbonui.const as uiconst
from carbonui.primitives.fill import Fill
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'
    description = Fill.__doc__

    def sample_code(self, parent):
        from carbonui.primitives.fill import Fill
        Fill(name='myFill', parent=parent, align=uiconst.TOPLEFT, width=100, height=100, color=eveColor.LEAFY_GREEN)
