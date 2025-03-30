#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\povCameraInSceneContainer.py
from carbonui.primitives.container import Container
from carbonui.ui3d import InSceneContainer
from eve.client.script.ui.control.themeColored import SpriteThemeColored
import carbonui.const as uiconst
import math
from carbonui.uicore import uicore

class PovCameraInSceneContainer(InSceneContainer):

    def ApplyAttributes(self, attributes):
        InSceneContainer.ApplyAttributes(self, attributes)
        cont = Container(parent=self, align=uiconst.CENTER, width=500, height=500)
        SpriteThemeColored(parent=cont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Camera/crosshair.png', colorType=uiconst.COLORTYPE_UIHILIGHT)
        self.crosshairPitchSprite = SpriteThemeColored(parent=cont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Camera/pitch.png', width=500, height=500, colorType=uiconst.COLORTYPE_UIHILIGHT)
        self.crosshairRotationSprite = SpriteThemeColored(parent=cont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Camera/rotate.png', width=500, height=500, colorType=uiconst.COLORTYPE_UIHILIGHT)
        self.crosshairRotationSprite.useTransform = True
        self.AnimEntry()

    def Update(self, pitch, roll):
        self.crosshairRotationSprite.rotation = roll + math.pi / 2
        prop = -(pitch - math.pi) / math.pi - 0.5
        self.crosshairPitchSprite.top = 465 * prop

    def AnimEntry(self):
        uicore.animations.FadeTo(self, 0.0, 1.0, duration=0.6)
