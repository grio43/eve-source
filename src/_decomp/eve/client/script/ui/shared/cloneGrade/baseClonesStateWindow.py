#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\cloneGrade\baseClonesStateWindow.py
import trinity
from carbonui import uiconst
from carbonui.control.window import Window
from carbonui.decorative.selectionIndicatorLine import SelectionIndicatorLine
from carbonui.primitives.sprite import StreamingVideoSprite, Sprite
from carbonui.util.color import Color
from carbonui.window.underlay import WindowUnderlay
from clonegrade.const import COLOR_OMEGA_ORANGE
x = 0.5
VIDEO_WIDTH = 1280 * x
VIDEO_HEIGHT = 720 * x

class CloneStateSelectionIndicatorLine(SelectionIndicatorLine):
    default_color = COLOR_OMEGA_ORANGE


class CloneStateWindowUnderlay(WindowUnderlay):
    default_clipChildren = True

    def ConstructLayout(self):
        super(CloneStateWindowUnderlay, self).ConstructLayout()
        self.video = StreamingVideoSprite(parent=self, videoPath='res:/video/shared/SplashBGLoop.webm', videoLoop=True, align=uiconst.CENTER, pos=(0,
         -86,
         VIDEO_WIDTH,
         VIDEO_HEIGHT), color=Color(*COLOR_OMEGA_ORANGE).SetSaturation(0.5).GetRGBA(), opacity=0.0, spriteEffect=trinity.TR2_SFX_COPY, blendMode=trinity.TR2_SBM_ADD)
        self.background_image = Sprite(name='bgTexture', parent=self, align=uiconst.CENTER, pos=(0, 0, 547, 690), texturePath='res:/UI/Texture/Classes/CloneGrade/bgScene.png', spriteEffect=trinity.TR2_SFX_SOFTLIGHT, effectOpacity=0.0)

    def ConstructAccentLine(self):
        self.headerAccentLine = CloneStateSelectionIndicatorLine(parent=self, align=uiconst.TOTOP_NOPUSH, weight=self.ACCENT_LINE_THICKNESS)

    def OnColorThemeChanged(self):
        pass


class BaseCloneStateWindow(Window):
    default_isCollapseable = False
    default_isMinimizable = False
    default_isLightBackgroundConfigurable = False
    default_isStackable = False
    default_isLockable = False
    default_isOverlayable = False
    default_extend_content_into_header = True

    def ApplyAttributes(self, attributes):
        self.hasWindowIcon = False
        Window.ApplyAttributes(self, attributes)
        self.ConstructLayout()
        self.LoadContent(animate=False)

    @property
    def bgVideo(self):
        return self.sr.underlay.video

    @property
    def bgSprite(self):
        return self.sr.underlay.background_image

    def ConstructBackground(self):
        pass

    def Prepare_Background_(self):
        self.sr.underlay = CloneStateWindowUnderlay(parent=self, padding=1)

    def ConstructLayout(self):
        pass

    def LoadContent(self, animate = True):
        pass
