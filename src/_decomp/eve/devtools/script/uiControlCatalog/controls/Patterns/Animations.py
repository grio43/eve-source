#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Patterns\Animations.py
import random
import uthread2
from carbonui.primitives.fill import Fill
from carbonui.primitives.container import Container
import carbonui
from carbonui.control.button import Button
from carbonui.button.group import ButtonGroup
from carbonui.uiconst import Align, OutputMode
import eveicon
from carbonui import uiconst
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Fade In/Out'

    def construct_sample(self, parent):
        grid = LayoutGrid(parent=parent, align=uiconst.TOPLEFT, columns=1, cellSpacing=24)
        self.sample_code(grid)
        button_group = ButtonGroup(parent=grid, align=Align.CENTERTOP)
        Button(parent=button_group, label='Fade In', func=self.fade_in)
        Button(parent=button_group, label='Fade Out', func=self.fade_out)

    def fade_in(self, *args):
        animations.FadeTo(self.sprite, self.sprite.opacity, 1.0, duration=0.6)

    def fade_out(self, *args):
        animations.FadeTo(self.sprite, self.sprite.opacity, 0.0, duration=0.6)

    def sample_code(self, parent):
        self.sprite = Sprite(parent=parent, align=Align.CENTERTOP, state=uiconst.UI_DISABLED, width=128, height=128, texturePath=eveicon.soldier_of_fortune, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, color=eveColor.HOT_RED, opacity=0.0)
        animations.FadeTo(self.sprite, startVal=self.sprite.opacity, endVal=1.0, duration=0.6)


class Sample2(Sample):
    name = 'Position'

    def construct_sample(self, parent):
        grid = LayoutGrid(parent=parent, align=uiconst.TOPLEFT, columns=1, cellSpacing=24, minWidth=200)
        self.sample_code(grid)
        button_group = ButtonGroup(parent=grid, align=Align.CENTERTOP)
        Button(parent=button_group, label='Left', func=self.move_left)
        Button(parent=button_group, label='Right', func=self.move_right)

    def move_left(self, *args):
        animations.MorphScalar(self.sprite, 'left', self.sprite.left, -20, duration=0.6)

    def move_right(self, *args):
        animations.MorphScalar(self.sprite, 'left', self.sprite.left, 20, duration=0.6)

    def sample_code(self, parent):
        self.sprite = Sprite(parent=parent, align=Align.CENTERTOP, state=uiconst.UI_DISABLED, left=-20, width=128, height=128, texturePath=eveicon.soldier_of_fortune, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, color=eveColor.HOT_RED, opacity=0.0)
        animations.FadeTo(self.sprite, self.sprite.opacity, 1.0, duration=0.6)
        animations.MorphScalar(self.sprite, attrName='left', startVal=self.sprite.left, endVal=1.0, duration=0.6)


class Sample3(Sample):
    name = 'Color'

    def construct_sample(self, parent):
        grid = LayoutGrid(parent=parent, align=uiconst.TOPLEFT, columns=1, cellSpacing=24)
        self.sample_code(grid)
        button_group = ButtonGroup(parent=grid, align=Align.CENTERTOP)
        Button(parent=button_group, label='Red', func=self.make_red)
        Button(parent=button_group, label='Green', func=self.make_green)
        Button(parent=button_group, label='Blue', func=self.make_blue)

    def make_red(self, *args):
        animations.SpColorMorphTo(self.sprite, self.sprite.rgba, eveColor.HOT_RED, duration=0.6)

    def make_green(self, *args):
        animations.SpColorMorphTo(self.sprite, self.sprite.rgba, eveColor.LEAFY_GREEN, duration=0.6)

    def make_blue(self, *args):
        animations.SpColorMorphTo(self.sprite, self.sprite.rgba, eveColor.PARAGON_BLUE, duration=0.6)

    def sample_code(self, parent):
        self.sprite = Sprite(parent=parent, align=Align.CENTERTOP, state=uiconst.UI_DISABLED, width=128, height=128, texturePath=eveicon.soldier_of_fortune, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, opacity=0.0)
        animations.SpColorMorphTo(self.sprite, startColor=self.sprite.rgba, endColor=eveColor.HOT_RED, duration=0.6)


class Sample4(Sample):
    name = 'Time Offset'

    def construct_sample(self, parent):
        grid = LayoutGrid(parent=parent, align=uiconst.TOPLEFT, columns=3, cellSpacing=24, minWidth=200)
        self.sample_code(grid)

    def sample_code(self, parent):
        num_icons = 9
        duration = 0.3
        time_offset_const = 0.05
        for i in range(num_icons):
            sprite = Sprite(parent=parent, align=Align.CENTERTOP, state=uiconst.UI_DISABLED, width=64, height=64, texturePath=eveicon.soldier_of_fortune, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0, opacity=0.0)
            animations.SpColorMorphTo(sprite, endColor=eveColor.LEAFY_GREEN, duration=duration, timeOffset=i * time_offset_const)
            animations.MorphScalar(sprite, attrName='glowBrightness', startVal=sprite.glowBrightness, endVal=1.0, duration=duration, timeOffset=(num_icons + i) * time_offset_const)


class Sample5(Sample):
    name = 'Loops'

    def construct_sample(self, parent):
        grid = LayoutGrid(parent=parent, align=uiconst.TOPLEFT, columns=2, cellSpacing=24, minWidth=200)
        self.sample_code(grid)

    def sample_code(self, parent):
        sprite = Sprite(parent=parent, align=Align.CENTERTOP, state=uiconst.UI_DISABLED, width=64, height=64, texturePath=eveicon.soldier_of_fortune, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW)
        animations.MorphScalar(sprite, attrName='glowBrightness', startVal=0.2, endVal=1.0, duration=0.6)
        carbonui.TextBody(parent=parent, align=Align.CENTERLEFT, text='1 loop')
        sprite = Sprite(parent=parent, align=Align.CENTERTOP, state=uiconst.UI_DISABLED, width=64, height=64, texturePath=eveicon.soldier_of_fortune, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW)
        animations.MorphScalar(sprite, attrName='glowBrightness', startVal=0.2, endVal=1.0, duration=0.6, loops=5)
        carbonui.TextBody(parent=parent, align=Align.CENTERLEFT, text='5 loops')
        sprite = Sprite(parent=parent, align=Align.CENTERTOP, state=uiconst.UI_DISABLED, width=64, height=64, texturePath=eveicon.soldier_of_fortune, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW)
        animations.MorphScalar(sprite, attrName='glowBrightness', startVal=0.5, endVal=1.0, duration=0.6, loops=uiconst.ANIM_REPEAT)
        carbonui.TextBody(parent=parent, align=Align.CENTERLEFT, text='Infinite loops')


class SkullAnimCont(Container):
    default_height = 32
    default_width = 256

    def __init__(self, **kw):
        super(SkullAnimCont, self).__init__(**kw)
        self.skull_sprite = Sprite(parent=self, align=Align.CENTERLEFT, state=uiconst.UI_DISABLED, width=self.default_height, height=self.default_height, texturePath=eveicon.soldier_of_fortune, outputMode=OutputMode.COLOR_AND_GLOW, glowBrightness=0.5)
        Fill(bgParent=self, padding=(0, 12, 0, 12), color=(1, 1, 1, 0.1))

    @property
    def x(self):
        pass

    @x.setter
    def x(self, value):
        self.skull_sprite.left = value * float(self.default_width) - self.default_height / 2
        self.skull_sprite.opacity = value


class Sample6(Sample):
    name = 'Curves'

    def construct_sample(self, parent):
        grid = LayoutGrid(parent=parent, align=uiconst.TOPLEFT, columns=2, cellSpacing=24)
        self.sample_code(grid)

    def sample_code(self, parent):
        duration = 2.0
        for curve_type, label in ((uiconst.ANIM_LINEAR, 'Linear'),
         (uiconst.ANIM_SMOOTH, 'Smooth'),
         (uiconst.ANIM_OVERSHOT, 'Overshot'),
         (uiconst.ANIM_OVERSHOT3, 'Overshot3'),
         (uiconst.ANIM_OVERSHOT5, 'Overshot5'),
         (uiconst.ANIM_WAVE, 'Wave'),
         (((0.0, 0.0),
           (0.3, 0.5),
           (0.6, 0.5),
           (1.0, 1.0)), 'Custom Curve')):
            anim_cont = SkullAnimCont(parent=parent, align=Align.CENTERLEFT)
            animations.MorphScalar(anim_cont, attrName='x', startVal=0.0, endVal=1.0, duration=duration, curveType=curve_type, loops=uiconst.ANIM_REPEAT)
            carbonui.TextBody(parent=parent, align=Align.CENTERLEFT, text=label)


class AnimatedSkull(Container):
    default_height = 16
    default_width = 16

    def __init__(self, **kw):
        super(AnimatedSkull, self).__init__(**kw)
        color = random.choice((eveColor.HOT_RED, eveColor.PARAGON_BLUE, eveColor.LIME_GREEN))
        self.skull_sprite = Sprite(parent=self, align=Align.CENTERLEFT, state=uiconst.UI_DISABLED, width=self.default_height, height=self.default_height, texturePath=eveicon.soldier_of_fortune, outputMode=OutputMode.COLOR_AND_GLOW, color=color, glowBrightness=1.0)
        animations.MorphScalar(self.skull_sprite, 'glowBrightness', 0.1, 1.5, duration=0.6 + 1.0 * random.random())


class Sample7(Sample):
    name = 'Skullfall'

    def construct_sample(self, parent):
        parent = Container(parent=parent, align=uiconst.TOPLEFT, pos=(0, 0, 640, 640), clipChildren=True)
        self.sample_code(parent)

    def sample_code(self, parent):
        while not parent.destroyed:
            skull = AnimatedSkull(parent=parent, align=Align.TOPLEFT, left=random.randint(32, parent.width - 32))
            animations.MorphScalar(skull, 'top', -skull.height, parent.height, duration=5.0 + random.random() * 5.0)
            left = random.randint(5, 30)
            animations.MorphScalar(skull, attrName='left', startVal=skull.left - left, endVal=skull.left + left, duration=3.0 + random.random(), curveType=uiconst.ANIM_WAVE)
            uthread2.Sleep(random.random() * 0.15)
