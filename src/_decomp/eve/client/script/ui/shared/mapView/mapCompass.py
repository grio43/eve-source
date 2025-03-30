#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\mapCompass.py
import math
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from eve.client.script.ui.control.themeColored import SpriteThemeColored
COMPASS_DIRECTIONS_COLOR = (1, 1, 1, 1)
COMPASS_SWEEP_COLOR = (1, 1, 1, 1)

class MapCompass(Container):
    default_name = 'MapCompass'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.onClickCallback = attributes.onClickCallback
        self.compassTransform = Transform(name='compass_transform', parent=self, width=self.width - 4, height=self.height - 4, align=uiconst.CENTER, opacity=1.0)
        self.frameContainer = Container(name='compass_transform', parent=self, width=self.width, height=self.height, align=uiconst.CENTER)
        self.ConstructDirectionIndicationSprites()
        self.ConstructBackground()

    def ConstructBackground(self):
        SpriteThemeColored(name='compass_underlay', bgParent=self.frameContainer, texturePath='res:/UI/Texture/classes/MapView/MapCompass/bgCircle.png', colorType=uiconst.COLORTYPE_UIBASECONTRAST, opacity=0.5)

    def ConstructDirectionIndicationSprites(self):
        SpriteThemeColored(name='north', parent=self.compassTransform, align=uiconst.CENTERTOP, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, texturePath='res:/UI/Texture/classes/MapView/MapCompass/northArrow.png', pos=(0, 0, 10, 10))
        SpriteThemeColored(name='west', parent=self.compassTransform, align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/classes/MapView/MapCompass/dash.png', pos=(0, 0, 10, 10))
        SpriteThemeColored(name='south', parent=self.compassTransform, align=uiconst.CENTERBOTTOM, texturePath='res:/UI/Texture/classes/MapView/MapCompass/dash.png', pos=(0, 0, 10, 10), rotation=math.pi / 2)
        SpriteThemeColored(name='east', parent=self.compassTransform, align=uiconst.CENTERRIGHT, texturePath='res:/UI/Texture/classes/MapView/MapCompass/dash.png', pos=(0, 0, 10, 10))

    def Update(self, yaw):
        self.compassTransform.rotation = -yaw

    def OnMouseEnter(self, *args):
        animations.FadeTo(self, self.opacity, 1.5, duration=0.15)

    def OnMouseExit(self, *args):
        animations.FadeTo(self, self.opacity, 1.0, duration=0.3)

    def OnClick(self, *args):
        self.onClickCallback()
