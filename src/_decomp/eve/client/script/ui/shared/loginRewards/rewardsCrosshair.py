#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\rewardsCrosshair.py
import math
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite

class RewardCrosshair(Container):
    default_align = uiconst.CENTER
    default_width = 96
    default_height = 96
    LINE_OPACITY = 0.2

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        linePad = 4
        self.leftSprite = Sprite(name='leftSprite', parent=self, opacity=self.LINE_OPACITY, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/LoginCampaign/todaysRewardContainerStroke.png', pos=(self.width + linePad,
         0,
         99,
         5), rotation=math.pi)
        self.rightSprite = Sprite(name='rightSprite', parent=self, opacity=self.LINE_OPACITY, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/LoginCampaign/todaysRewardContainerStroke.png', pos=(self.width + linePad,
         0,
         99,
         5))
        self.topSprite = Sprite(name='topSprite', parent=self, opacity=self.LINE_OPACITY, align=uiconst.CENTERBOTTOM, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/LoginCampaign/todaysRewardLine.png', pos=(0,
         self.height + linePad,
         6,
         1))
        self.bottomSprite = Sprite(name='bottomSprite', parent=self, opacity=self.LINE_OPACITY, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/LoginCampaign/todaysRewardLine.png', pos=(0,
         self.height + linePad,
         6,
         1))

    def SetRGBA(self, newColor):
        self.leftSprite.SetRGBA(*newColor)
        self.rightSprite.SetRGBA(*newColor)
        self.topSprite.SetRGBA(*newColor)
        self.bottomSprite.SetRGBA(*newColor)

    def SetSideSpriteDisplay(self, isOn):
        self.leftSprite.display = isOn
        self.rightSprite.display = isOn
