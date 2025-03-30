#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\intromovie\ui\blackoverlay.py
import carbonui.const as uiconst
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbonui.uicore import uicore

class BlackOverlay(Fill):
    default_align = uiconst.TOALL
    default_color = (0.0, 0.0, 0.0, 0.0)
    default_idx = 0
    default_name = 'blackOverlay'
    default_opacity = 0.0
    default_parent = uicore.layer.videoOverlay
    default_state = uiconst.UI_DISABLED
    FADE_IN_DURATION_SECONDS = 3.0

    def fade_in(self, callback):
        animations.FadeIn(self, duration=self.FADE_IN_DURATION_SECONDS, callback=callback)
