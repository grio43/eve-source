#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Sprites\Frame.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from eve.devtools.script.uiControlCatalog import sampleUtil
from eve.devtools.script.uiControlCatalog.sample import Sample
from carbonui.primitives.frame import Frame

class Sample1(Sample):
    name = 'Basic'
    description = Frame.__doc__

    def construct_sample(self, parent):
        mainCont = sampleUtil.GetCollapsableCont(parent, 200, 200, None)
        self.sample_code(mainCont)

    def sample_code(self, parent):
        from carbonui.primitives.frame import Frame
        Frame(name='myFrame', bgParent=parent)


class Sample2(Sample):
    name = 'Frame constants'

    def construct_sample(self, parent):
        mainCont = sampleUtil.GetCollapsableCont(parent, 200, 200, None)
        self.sample_code(mainCont)

    def sample_code(self, parent):
        from carbonui.primitives.frame import Frame
        Frame(name='myFrame', bgParent=parent, frameConst=uiconst.FRAME_FILLED_CORNER5)


class Sample3(Sample):
    name = 'Custom texture'

    def construct_sample(self, parent):
        mainCont = sampleUtil.GetCollapsableCont(parent, 200, 200, None)
        self.sample_code(mainCont)

    def sample_code(self, parent):
        from carbonui.primitives.frame import Frame
        Frame(name='myFrame', bgParent=parent, texturePath='res:/UI/Texture/classes/shipTree/infoPanel/selected.png', cornerSize=10)
