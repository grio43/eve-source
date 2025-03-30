#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\factionalWarfare\enlistmentFlow\backgroundDeco.py
import math
import random
from carbonui.primitives.transform import Transform
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbon.common.script.util.mathCommon import FloatCloseEnough
from carbonui.control.button import Button
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui import const as uiconst, TextCustom
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.vectorlinetrace import DashedCircle
from carbonui.uianimations import animations
from carbonui.util.dpi import ScaleDpi
from eve.client.script.ui import eveColor

class BackgroundDeco(Container):
    default_align = uiconst.TOPLEFT
    default_width = 470
    default_height = 470
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(BackgroundDeco, self).ApplyAttributes(attributes)
        self.colorSprites = []
        self.ConstructCentralDeco()
        self.ConstructedCircles()
        self.ConstuctInnerElements()
        self.ConstructResizingElements()
        self.ColorSprites(eveColor.CRYO_BLUE)

    def ColorSprites(self, color):
        for sprite in self.colorSprites:
            sprite.SetRGBA(*color)

    def ConstructSides(self):
        self.sides = Sprite(name='sides', parent=self, align=uiconst.CENTER, pos=(0, 0, 1259, 340), opacity=1.0, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/circle/sides.png')
        self.sidesDashes = Sprite(name='sidesDashes', parent=self, align=uiconst.CENTER, pos=(0, 0, 1257, 340), opacity=1.0, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/circle/sideDashes.png', color=eveColor.CRYO_BLUE)

    def ConstructOutCircles(self):
        self.outerCircle1 = Sprite(name='outerCircle1', parent=self, align=uiconst.CENTER, pos=(0, 0, 1036, 1056), opacity=3.0, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/circle/outeCircle1.png')
        self.outerCircle2 = Sprite(name='outerCircle2', parent=self, align=uiconst.CENTER, pos=(0, 0, 1006, 1026), opacity=3.0, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/circle/outerCircle2.png', color=eveColor.CRYO_BLUE)
        self.ellipse720 = Sprite(name='ellipse720', parent=self, align=uiconst.CENTER, pos=(0, 0, 834, 834), opacity=3.0, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/circle/ellipse720.png', color=eveColor.CRYO_BLUE)

    def SetMainCircleSize(self, isBig, animate = True):
        if isBig:
            newScale = (1.0, 1.0)
        else:
            newScale = (0.75, 0.75)
        if animate:
            animations.MorphVector2(self.resizingTransform, 'scale', self.resizingTransform.scale, newScale)
        else:
            self.resizingTransform.scale = newScale

    def Animate(self, sleep = False):
        pass

    def ConstructCentralDeco(self):
        self.Construct_central_deco_1a()
        self.Construct_central_deco_1a_color()
        self.Construct_central_deco_1b()
        self.Construct_central_deco_1b_color()
        self.Construct_central_deco_2a()
        self.Construct_central_deco_2a_color()
        self.Construct_central_deco_2b()
        self.Construct_central_deco_2b_color()

    def Construct_central_deco_1a(self):
        self.central_deco_1_a = Sprite(name='central_deco_1_a', parent=self, align=uiconst.CENTER, pos=(0, 0, 198, 340), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Central_decoration_1_A.png')

    def Construct_central_deco_1a_color(self):
        self.central_deco_1a_color = Sprite(name='central_deco_1a_color', parent=self, align=uiconst.CENTER, pos=(0, 0, 198, 340), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Central_decoration_1_A_Colour.png')
        self.colorSprites.append(self.central_deco_1a_color)

    def Construct_central_deco_1b(self):
        self.central_deco_ab = Sprite(name='central_deco_ab', parent=self, align=uiconst.CENTER, pos=(0, 0, 198, 340), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Central_decoration_1_B.png')

    def Construct_central_deco_1b_color(self):
        self.central_deco_1b_color = Sprite(name='central_deco_1b_color', parent=self, align=uiconst.CENTER, pos=(0, 0, 198, 340), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Central_decoration_1_B_Colour.png')
        self.colorSprites.append(self.central_deco_1b_color)

    def Construct_central_deco_2a(self):
        self.central_deco_2a = Sprite(name='central_deco_2a', parent=self, align=uiconst.CENTER, pos=(0, 0, 198, 340), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Central_decoration_2_A.png')

    def Construct_central_deco_2a_color(self):
        self.central_deco_2a_color = Sprite(name='central_deco_2a_color', parent=self, align=uiconst.CENTER, pos=(0, 0, 198, 340), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Central_decoration_2_A_Colour.png')
        self.colorSprites.append(self.central_deco_2a_color)

    def Construct_central_deco_2b(self):
        self.central_deco_2b = Sprite(name='central_deco_2b', parent=self, align=uiconst.CENTER, pos=(0, 0, 198, 340), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Central_decoration_2_B.png')

    def Construct_central_deco_2b_color(self):
        self.central_deco_2b_color = Sprite(name='central_deco_2b_color', parent=self, align=uiconst.CENTER, pos=(0, 0, 198, 340), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Central_decoration_2_B_colour.png')
        self.colorSprites.append(self.central_deco_2b_color)

    def ConstructedCircles(self):
        self.Construct_dashed_large_circle_outer()
        self.Construct_dashed_large_circle_color()
        self.Construct_dashed_large_circle_inner_ring()
        self.Construct_external_deco()
        self.Construct_external_deco_lights_color()

    def Construct_dashed_large_circle_outer(self):
        self.dashed_large_circle_outer = Sprite(name='dashed_large_circle_outer', parent=self, align=uiconst.CENTER, pos=(0, 0, 1034, 1056), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Dashed_large_circles_Outer_ring.png')

    def Construct_dashed_large_circle_color(self):
        self.dashed_large_circle_color = Sprite(name='dashed_large_circle_color', parent=self, align=uiconst.CENTER, pos=(0, 0, 834, 474), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Dashed_large_circles_Colour.png')
        self.colorSprites.append(self.dashed_large_circle_color)

    def Construct_dashed_large_circle_inner_ring(self):
        self.dashed_large_circle_inner_ring = Sprite(name='dashed_large_circle_inner_ring', parent=self, align=uiconst.CENTER, pos=(0, 0, 642, 641), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Dashed_large_circles_Inner_ring.png')

    def Construct_ellipse_dashes_color(self):
        self.dashed_large_circle_inner_ring = Sprite(name='Construct_ellipse_dashes_color', parent=self.resizingTransform, align=uiconst.CENTER, pos=(0, 0, 418, 420), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Ellipse_dashes_Colour.png')
        self.colorSprites.append(self.dashed_large_circle_inner_ring)

    def Construct_external_deco(self):
        self.external_deco = Sprite(name='external_deco', parent=self, align=uiconst.CENTER, pos=(0, 0, 1131, 666), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/External_decorations.png')

    def Construct_external_deco_lights_color(self):
        self.external_deco_lights_color = Sprite(name='external_deco_lights_color', parent=self, align=uiconst.CENTER, pos=(0, 0, 939, 654), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/External_decorations_lights_Colour.png')
        self.colorSprites.append(self.external_deco_lights_color)

    def ConstructHorizontal(self):
        self.Construct_horizontal_deco_bottom_row()
        self.Construct_horizontal_deco_bottom_row_detail_color()
        self.Construct_horizontal_deco_top_row()
        self.Construct_horizontal_deco_top_row_detail_color()

    def Construct_horizontal_deco_bottom_row(self):
        self.horizontal_deco_bottom_row = Sprite(name='horizontal_deco_bottom_row', parent=self, align=uiconst.CENTER, pos=(0, 0, 1260, 339), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Horizontal_decoration_BottomRow.png')

    def Construct_horizontal_deco_bottom_row_detail_color(self):
        self.external_deco_lights_color = Sprite(name='Construct_horizontal_deco_bottom_row_detail_color', parent=self, align=uiconst.CENTER, pos=(0, 0, 1260, 339), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Horizontal_decoration_BottomRow_Detail_Colour.png')
        self.colorSprites.append(self.external_deco_lights_color)

    def Construct_horizontal_deco_top_row(self):
        self.horizontal_deco_top_row = Sprite(name='horizontal_deco_top_row', parent=self, align=uiconst.CENTER, pos=(0, 0, 1260, 339), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Horizontal_decoration_TopRow.png')

    def Construct_horizontal_deco_top_row_detail_color(self):
        self.horizontal_deco_top_row_detail_color = Sprite(name='horizontal_deco_top_row_detail_color', parent=self, align=uiconst.CENTER, pos=(0, 0, 1260, 339), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Horizontal_decoration_TopRow_Detail_Colour.png')
        self.colorSprites.append(self.horizontal_deco_top_row_detail_color)

    def ConstuctInnerElements(self):
        self.Construct_inner_elements()
        self.Construct_inner_elements_lights_color()
        self.Construct_middle_edge_elements()

    def ConstructResizingElements(self):
        self.resizingTransform = Transform(parent=self, pos=(0, 0, 496, 496), align=uiconst.CENTER, scalingCenter=(0.5, 0.5))
        self.Construct_inner_dashed_ring()
        self.Construct_inner_solid_ring()
        self.Construct_radial_inner_glow()
        self.Construct_radial_outer_glow_color()
        self.Construct_ellipse_dashes_color()

    def Construct_inner_dashed_ring(self):
        self.inner_dashed_ring = Sprite(name='inner_dashed_ring', parent=self.resizingTransform, align=uiconst.CENTER, pos=(0, 0, 496, 496), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Inner_dashed_ring.png')

    def Construct_inner_elements(self):
        self.inner_elements = Sprite(name='inner_elements', parent=self, align=uiconst.CENTER, pos=(0, 0, 752, 688), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Inner_elements.png')

    def Construct_inner_elements_lights_color(self):
        self.inner_elements_lights_color = Sprite(name='inner_elements_lights_color', parent=self, align=uiconst.CENTER, pos=(0, 0, 691, 402), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Inner_elements_lights_Colour.png')
        self.colorSprites.append(self.inner_elements_lights_color)

    def Construct_inner_solid_ring(self):
        self.inner_solid_ring = Sprite(name='inner_solid_ring', parent=self.resizingTransform, align=uiconst.CENTER, pos=(0, 0, 496, 496), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Inner_solid_ring.png')

    def Construct_middle_edge_elements(self):
        self.middle_edge_elements = Sprite(name='middle_edge_elements', parent=self, align=uiconst.CENTER, pos=(0, 0, 1209, 206), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Middle_edge_elements.png')

    def Construct_radial_inner_glow(self):
        self.radial_inner_glow = Sprite(name='radial_inner_glow', parent=self.resizingTransform, align=uiconst.CENTER, pos=(0, 0, 475, 492), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Radia_inner_glow.png')

    def Construct_radial_outer_glow_color(self):
        self.radial_outer_glow_color = Sprite(name='radial_outer_glow_color', parent=self.resizingTransform, align=uiconst.CENTER, pos=(0, 0, 599, 681), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Enlistment/deco/Radial_outer_glow_Colour.png')
        self.colorSprites.append(self.radial_outer_glow_color)


class TestBgDeco(Window):
    default_width = 1280
    default_height = 720
    default_windowID = 'testBgDeco'
    default_minSize = (1280, 720)
    default_fixedWidth = 1280
    default_fixedHeight = 720

    def DebugReload(self, *args):
        self.Reload(self)

    def ApplyAttributes(self, attributes):
        super(TestBgDeco, self).ApplyAttributes(attributes)
        bcgDeco = BackgroundDeco(parent=self.content, align=uiconst.CENTER)
        reloadBtn = Button(parent=self.content, label='Reload', align=uiconst.TOPLEFT, func=self.DebugReload, top=0, idx=0)

        def RotateDeco(deco):
            print 'deco.rotation = ',
            if FloatCloseEnough(deco.rotation, 0):
                change = math.radians(22.5)
                newValue = deco.rotation + change
            else:
                newValue = 0
            animations.MorphScalar(deco, 'rotation', deco.rotation, newValue, duration=0.2)

        Button(parent=self.content, label='elllipses', align=uiconst.TOPLEFT, func=lambda *args: RotateDeco(bcgDeco.ellipse720), top=30, idx=0)
        Button(parent=self.content, label='outeCircle1', align=uiconst.TOPLEFT, func=lambda *args: RotateDeco(bcgDeco.outerCircle1), top=60, idx=0)
        Button(parent=self.content, label='outeCircle2', align=uiconst.TOPLEFT, func=lambda *args: RotateDeco(bcgDeco.outerCircle2), top=90, idx=0)
        Button(parent=self.content, label='change Color', align=uiconst.TOPLEFT, func=lambda *args: self.ChangeColor(bcgDeco), top=120, idx=0)

    def ChangeColor(self, bgDeco):
        colors = [eveColor.HOT_RED, eveColor.CRYO_BLUE, eveColor.WARNING_ORANGE]
        color = random.choice(colors)
        for sprite in bgDeco.colorSprites:
            sprite.SetRGBA(*color)
