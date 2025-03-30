#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\moreIcon.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui import eveColor

class BaseMoreIcon(Container):
    default_width = 27
    default_height = 27
    default_state = uiconst.UI_NORMAL
    iconPath = 'res:/UI/Texture/Shared/DarkStyle/buttonIconQuestion.png'

    def ApplyAttributes(self, attributes):
        super(BaseMoreIcon, self).ApplyAttributes(attributes)
        self.tooltipPanelClassInfo = attributes.Get('tooltipPanelClassInfo', None)
        self.ConstructLayout()

    def ConstructLayout(self):
        Sprite(name='', parent=self, align=uiconst.CENTER, pos=(0, 0, 16, 16), texturePath=self.iconPath, color=eveColor.CRYO_BLUE, state=uiconst.UI_DISABLED)
        self.backgroundSprite = Frame(name='backgroundColorSprite', bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/buttonSmall_Solid.png', color=Color.BLACK, padding=(1, 1, 1, 1), cornerSize=9)
        self.frame = Frame(name='borderFrame', bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/buttonSmall_Stroke.png', opacity=0.1)

    def AnimEnter(self, offsetValue):
        timeOffset = 0.05 * offsetValue
        duration = 0.3
        animations.FadeIn(self, duration=2 * duration, timeOffset=timeOffset)

    def OnMouseEnter(self, *args):
        animations.SpColorMorphTo(self.backgroundSprite, self.backgroundSprite.GetRGBA(), (0.1, 0.1, 0.1, 1), duration=0.1)
        animations.FadeTo(self.frame, self.frame.opacity, 0.2, duration=0.1)

    def OnMouseExit(self, *args):
        animations.SpColorMorphTo(self.backgroundSprite, self.backgroundSprite.GetRGBA(), Color.BLACK, duration=0.1)
        animations.FadeTo(self.frame, self.frame.opacity, 0.1, duration=0.1)


class DescriptionIcon(BaseMoreIcon):
    iconPath = 'res:/UI/Texture/Shared/DarkStyle/buttonIconQuestion.png'


class MoreIcon(BaseMoreIcon):
    iconPath = 'res:/UI/Texture/Shared/DarkStyle/buttonIconPlus.png'
