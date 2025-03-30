#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\cosmetics\cosmeticFittingLayout.py
import trinity
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.shared.fitting.fittingUtil import GetScaleFactor
from eveui import Sprite

class CosmeticFittingLayout(Container):
    default_name = 'CosmeticFittingLayout'
    default_width = 550
    default_height = 550
    default_align = uiconst.CENTERLEFT
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        super(CosmeticFittingLayout, self).ApplyAttributes(attributes)
        self.ConstructLayout()

    def ConstructLayout(self):
        width = self.width * GetScaleFactor()
        circlePadding = 105 * GetScaleFactor()
        circleSize = width + circlePadding
        self.circleContainer = Container(name='circleContainer', parent=self, align=uiconst.CENTER, width=circleSize, height=circleSize)
        Sprite(parent=self.circleContainer, name='baseDOT', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/fittingbase_dotproduct.png', spriteEffect=trinity.TR2_SFX_DOT, blendMode=trinity.TR2_SBM_ADD)
        self.baseColor = SpriteThemeColored(parent=self.circleContainer, name='baseColor', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/fittingbase_basecircle.png', colorType=uiconst.COLORTYPE_UIBASE)
        self.baseShape = Sprite(parent=self.circleContainer, name='baseShape', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/fittingbase.png', color=(0.0, 0.0, 0.0, 0.86))
