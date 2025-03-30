#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Effects\Glow.py
from carbonui import uiconst
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Description'
    description = 'The universal UI glow effect rendered in one swoop as a post process. Moving the mouse towards a glowing UI object will increase the glow of that object.'

    def construct_sample(self, parent):
        grid = LayoutGrid(parent=parent, align=uiconst.TOPLEFT, columns=2, cellSpacing=24)
        Sprite(parent=grid, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=64, height=64, texturePath='res:/UI/Texture/Icons/78_64_4.png', outputMode=uiconst.OUTPUT_COLOR_AND_GLOW)
        eveLabel.EveLabelMedium(parent=grid, align=uiconst.CENTERLEFT, width=270, padTop=8, text='Anything derived from <b>VisibleBase</b> (Sprite, Fill, VectorLineTrace, etc.) can have a glow effect applied to it by setting the <b>outputMode</b> property to:\n\n<b>uiconst.OUTPUT_COLOR_AND_GLOW</b>')
        Sprite(parent=grid, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=64, height=64, texturePath='res:/UI/Texture/Icons/78_64_4.png', outputMode=uiconst.OUTPUT_GLOW)
        eveLabel.EveLabelMedium(parent=grid, align=uiconst.CENTERLEFT, width=270, padTop=8, text='You can also render only the glow portion by assigning the following to the <b>outputMode</b> property:\n\n<b>uiconst.OUTPUT_GLOW</b>')


class Sample2(Sample):
    name = 'Color and glow'

    def sample_code(self, parent):
        Sprite(parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=64, height=64, texturePath='res:/UI/Texture/Classes/overview/shareableOverview.png', color=eveColor.LIME_GREEN, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.75)


class Sample3(Sample):
    name = 'Glow only'

    def sample_code(self, parent):
        Sprite(parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=64, height=64, texturePath='res:/UI/Texture/Classes/overview/shareableOverview.png', color=eveColor.LIME_GREEN, outputMode=uiconst.OUTPUT_GLOW, glowBrightness=1.0)


class Sample4(Sample):
    name = 'Animations'

    def sample_code(self, parent):
        sprite = Sprite(parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=64, height=64, texturePath='res:/UI/Texture/Icons/78_64_4.png', outputMode=uiconst.OUTPUT_COLOR_AND_GLOW)
        animations.MorphScalar(sprite, 'glowBrightness', 0.0, 2.0, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
