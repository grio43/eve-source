#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Progress\LoadingWheel.py
import carbonui.const as uiconst
import uthread2
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.uianimations import animations
from carbonui.uiconst import SpriteEffect
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def construct_sample(self, parent):
        grid = LayoutGrid(parent=parent, align=uiconst.CENTER, columns=3, cellSpacing=(64, 0))
        self.sample_code(grid)

    def sample_code(self, parent):
        from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
        LoadingWheel(parent=parent, align=uiconst.CENTER, width=64, height=64)
        LoadingWheel(parent=parent, align=uiconst.CENTER, width=32, height=32)
        LoadingWheel(parent=parent, align=uiconst.CENTER, width=16, height=16)


class Sample2(Sample):
    name = 'Fading in and out'

    def sample_code(self, parent):
        from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel

        def load_stuff():
            uthread2.sleep(2.0)

        loadingWheel = LoadingWheel(parent=parent, opacity=0.0)
        animations.FadeIn(loadingWheel)
        load_stuff()
        animations.FadeOut(loadingWheel)
