#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\itemTierCont.py
from carbonui.primitives.container import Container
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite

class ItemTierCont(Container):
    default_name = 'itemTierCont'
    default_align = uiconst.TOTOP_NOPUSH
    default_height = 180
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.tierGradient = Sprite(name='tierGradient', parent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/LoginCampaign/dli_glow.png', opacity=1.0, state=uiconst.UI_DISABLED)
        self.display = False

    def SetColor(self, color):
        gradientColor = color[:3] + (self.tierGradient.GetAlpha(),)
        self.tierGradient.SetRGBA(*gradientColor)

    def SetTierLineOpacity(self, opacity):
        self.opacity = opacity
