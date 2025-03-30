#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\previewTierCont.py
from carbonui.primitives.container import Container
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite

class TierLineCont(Container):
    default_name = 'tierLineCont'
    default_align = uiconst.TOTOP_NOPUSH
    default_fullOpacity = 1.0

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.fullOpacity = attributes.get('fullOpacity', self.default_fullOpacity)
        self.tierLineGlow = Sprite(name='tierLineGlow', parent=self, align=uiconst.TOTOP_NOPUSH, texturePath='res:/UI/Texture/classes/LoginCampaign/todaysReward_gradientGlow_2.png', height=10)
        self.tierLine = Sprite(name='tierLine', parent=self, align=uiconst.TOTOP_NOPUSH, texturePath='res:/UI/Texture/classes/LoginCampaign/todaysReward_gradientGlow_1.png', pos=(0, 3, 0, 4), opacity=10)
        self.tierGradient = Sprite(name='tierGradient', parent=self, align=uiconst.TOTOP_NOPUSH, texturePath='res:/UI/Texture/classes/LoginCampaign/tierGradient.png', height=133, opacity=1.0, top=-self.top)

    def SetColor(self, color):
        self.tierLine.SetRGBA(*color)
        self.tierLineGlow.SetRGBA(*color)
        self.tierGradient.display = True
        self.tierGradient.SetRGBA(*color)
