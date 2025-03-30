#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\Containers\Container.py
from carbonui import uiconst, TextBody, Align, PickState
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample
from eve.devtools.script.uiControlCatalog.sampleUtil import GetHorizCollapsableCont, GetCollapsableCont
from eveui import Sprite

class Sample1(Sample):
    name = 'Basic'
    description = Container.__doc__

    def sample_code(self, parent):
        from carbonui.primitives.container import Container
        Container(name='myCont', parent=parent, align=uiconst.TOPLEFT, pos=(0, 0, 250, 250), bgColor=eveColor.MATTE_BLACK)


class Sample2(Sample):
    name = 'Push alignment'
    description = 'Push alignment modes will fill upp either all horizontal space (TOTOP and TOBOTOTM) or vertical space (TOLEFT and TORIGHT) available. TOALL will fill up both.'

    def construct_sample(self, parent):
        cont = GetCollapsableCont(parent)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.container import Container
        Container(name='leftCont', parent=parent, align=uiconst.TOLEFT, width=50, bgColor=eveColor.SAND_YELLOW)
        Container(name='leftCont', parent=parent, align=uiconst.TORIGHT, width=50, bgColor=eveColor.CHERRY_RED)
        Container(name='topCont', parent=parent, align=uiconst.TOTOP, height=50, bgColor=eveColor.SUCCESS_GREEN)
        Container(name='bottomCont', parent=parent, align=uiconst.TOBOTTOM, height=50, bgColor=eveColor.PRIMARY_BLUE)


class Sample3(Sample):
    name = 'Non-push alignment'
    description = "UI objects using these alignment modes are not affected by their children at all and order of construction only matters for the sake of what's on top if objects intersect"

    def construct_sample(self, parent):
        cont = GetCollapsableCont(parent)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.container import Container
        Container(name='topLeftCont', parent=parent, align=uiconst.TOPLEFT, height=50, width=50, bgColor=eveColor.SAND_YELLOW)
        Container(name='topLeftCont', parent=parent, align=uiconst.TOPRIGHT, height=50, width=50, bgColor=eveColor.WARNING_ORANGE)
        Container(name='centerCont', parent=parent, align=uiconst.CENTER, height=50, width=50, bgColor=eveColor.COPPER_OXIDE_GREEN)
        Container(name='bottomRightCont', parent=parent, align=uiconst.BOTTOMRIGHT, height=50, width=50, bgColor=eveColor.CHERRY_RED)
        Container(name='bottomRightCont', parent=parent, align=uiconst.BOTTOMLEFT, height=50, width=50, bgColor=eveColor.SMOKE_BLUE)


class Sample4(Sample):
    name = 'Proportional alignment'
    description = 'These alignment modes will take up a percentage of the available space and not a fixed amount of pixels'

    def construct_sample(self, parent):
        cont = GetCollapsableCont(parent)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.container import Container
        Container(name='leftCont', parent=parent, align=uiconst.TOLEFT_PROP, width=0.5, bgColor=eveColor.SAND_YELLOW)
        Container(name='leftCont', parent=parent, align=uiconst.TORIGHT_PROP, width=0.3, bgColor=eveColor.CHERRY_RED)
        Container(name='topCont', parent=parent, align=uiconst.TOTOP_PROP, height=0.4, bgColor=eveColor.SUCCESS_GREEN)
        Container(name='bottomCont', parent=parent, align=uiconst.TOBOTTOM_PROP, height=0.2, bgColor=eveColor.PRIMARY_BLUE)


class Sample5(Sample):
    name = 'Clipping'
    description = 'Passing in a clipChildren=True will clip anything that falls outside of the Container'

    def construct_sample(self, parent):
        cont = GetCollapsableCont(parent)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.container import Container
        Container(name='circleCont', parent=parent, align=uiconst.CENTERLEFT, pos=(-50, 0, 250, 250), bgTexturePath='res:/UI/Texture/circle_full.png', bgColor=eveColor.CRYO_BLUE)


class Sample6(Sample):
    name = 'Pick mask'
    description = 'Using a pickingMaskTexture. All pixels in picking mask texture with opacity > 0 are pickable'

    def sample_code(self, parent):
        from carbonui.primitives.container import Container
        TEXTURE_PATH = 'res:/UI/Texture/corpLogoLibs/large/478.png'

        class HoverCont(Container):

            def ApplyAttributes(self, attributes):
                super(HoverCont, self).ApplyAttributes(attributes)
                self.sprite = Sprite(name='sprite', parent=self, align=uiconst.TOALL, texturePath=TEXTURE_PATH, color=eveColor.SMOKE_BLUE, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0)

            def OnMouseEnter(self, *args):
                super(HoverCont, self).OnMouseEnter(*args)
                self.sprite.glowBrightness = 1.0

            def OnMouseExit(self, *args):
                super(HoverCont, self).OnMouseExit(*args)
                self.sprite.glowBrightness = 0.0

        HoverCont(name='mainCont', parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, width=256, height=256, pickingMaskTexturePath=TEXTURE_PATH)


class Sample7(Sample):
    name = 'Centered alignments'

    def construct_sample(self, parent):
        cont = Container(parent=parent, align=uiconst.TOPLEFT, width=400, height=400, bgColor=eveColor.MATTE_BLACK)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.container import Container
        horizontalCont = ContainerAutoSize(name='myHorizontalCenteredCont', parent=parent, align=uiconst.VERTICALLY_CENTERED, height=100, bgColor=eveColor.PRIMARY_BLUE, opacity=0.8)
        TextBody(parent=horizontalCont, padding=16, text='This is some really long text that I just made up... ' * 5, align=uiconst.TOTOP)
        Container(name='myVerticalCenteredCont', parent=parent, align=uiconst.HORIZONTALLY_CENTERED, width=100, bgColor=eveColor.SAND_YELLOW, opacity=0.8)


class Sample8(Sample):
    name = 'Sticky alignment'

    def construct_sample(self, parent):
        cont = GetCollapsableCont(parent)
        cont = ScrollContainer(parent=cont, align=uiconst.TOALL, bgColor=eveColor.MATTE_BLACK)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.container import Container
        TextBody(parent=parent, text='This text will disappear ... ' * 5, align=uiconst.TOTOP)
        sticky_cont = ContainerAutoSize(parent=parent, align=Align.TOTOP_STICKY, bgColor=eveColor.COPPER_OXIDE_GREEN, padTop=16, pickState=PickState.ON)
        TextBody(parent=sticky_cont, text='This text will stick around!', align=uiconst.TOTOP, padding=8)
        TextBody(parent=parent, text='And this is some really long text that keeps on repeating itself... ' * 40, align=uiconst.TOTOP, padTop=16)
