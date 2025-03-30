#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\underlay.py
from carbonui import uiconst
from carbonui.decorative.selectionIndicatorLine import SelectionIndicatorLine
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.decorative.blurredSceneUnderlay import BlurredSceneUnderlay

class BaseWindowUnderlay(Container):

    def EnableLightBackground(self):
        pass

    def DisableLightBackground(self):
        pass

    def AnimEntry(self):
        pass

    def AnimExit(self):
        pass


DURATION_ENTRY = 0.4
DURATION_EXIT = 0.6

class WindowUnderlay(BaseWindowUnderlay):
    default_name = 'underlay'
    default_state = uiconst.UI_DISABLED
    default_hasBlurredUnderlay = True
    ACCENT_LINE_THICKNESS = 1
    __notifyevents__ = ['OnCameraDragStart', 'OnCameraDragEnd']

    def ApplyAttributes(self, attributes):
        self.hasBlurredUnderlay = attributes.get('hasBlurredUnderlay', self.default_hasBlurredUnderlay)
        super(WindowUnderlay, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.isCameraDragging = False
        self.blurredUnderlay = None
        self.ConstructLayout()

    def ConstructLayout(self):
        self.ConstructAccentLine()
        Frame(parent=self, align=uiconst.TOALL, opacity=0.1)
        self.dotBG = Sprite(name='dotBG', bgParent=self, texturePath='res:/UI/Texture/Shared/dot_bg.png', opacity=0.0, tileX=True, tileY=True, translationPrimary=(-0.61, -0.61))
        self.ConstructBlurredUnderlay()

    def ConstructAccentLine(self):
        self.headerAccentLine = SelectionIndicatorLine(parent=self, align=uiconst.TOTOP_NOPUSH, weight=self.ACCENT_LINE_THICKNESS, opacity_active=0.5)

    def ConstructBlurredUnderlay(self):
        if self.hasBlurredUnderlay:
            self.blurredUnderlay = BlurredSceneUnderlay(bgParent=self, effectOpacity=0.5, saturation=0.5)

    def AnimEntry(self):
        self.headerAccentLine.Select()
        animations.FadeTo(self.dotBG, self.dotBG.opacity, 0.05, duration=DURATION_ENTRY, curveType=uiconst.ANIM_OVERSHOT3)

    def AnimExit(self):
        self.headerAccentLine.Deselect()
        animations.FadeTo(self.dotBG, self.dotBG.opacity, 0.0, duration=DURATION_EXIT)

    def OnCameraDragStart(self):
        if not self.blurredUnderlay:
            return
        self.blurredUnderlay.isCameraDragging = True
        self.blurredUnderlay.UpdateState()

    def OnCameraDragEnd(self):
        if not self.blurredUnderlay:
            return
        self.blurredUnderlay.isCameraDragging = False
        self.blurredUnderlay.UpdateState()

    def EnableLightBackground(self):
        if not self.blurredUnderlay:
            return
        self.blurredUnderlay.EnableLightBackground()

    def DisableLightBackground(self):
        if not self.blurredUnderlay:
            return
        self.blurredUnderlay.DisableLightBackground()
