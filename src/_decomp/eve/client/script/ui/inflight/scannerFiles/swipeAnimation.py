#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\scannerFiles\swipeAnimation.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.gradientSprite import GradientSprite, GradientConst
from carbonui.uianimations import animations
import trinity

class SwipeAnimator(Container):

    def ApplyAttributes(self, attributes):
        super(SwipeAnimator, self).ApplyAttributes(attributes)
        GradientSprite(parent=self, align=uiconst.TORIGHT, blendMode=trinity.TR2_SBM_ADD, pos=(0, 0, 200, 0), rgbData=[(0, (0.2941177, 0.7921569, 1.0))], alphaData=[(0, 0),
         (0.95, 0.3),
         (0.99, 0.5),
         (1, 1)], alphaInterp=GradientConst.INTERP_LINEAR, colorInterp=GradientConst.INTERP_LINEAR)

    def start(self, swipe_duration, fade_in_duration = None, highlight_duration = None, fade_out_duration = None):
        self.SetState(uiconst.UI_NORMAL)
        fade_in_duration = fade_in_duration or 0.15 * swipe_duration
        fade_out_duration = fade_out_duration or 0.15 * swipe_duration
        highlight_duration = highlight_duration or 0.09 * swipe_duration
        animations.FadeIn(self, duration=fade_in_duration)
        animations.MorphScalar(obj=self, attrName='width', startVal=0, endVal=1, duration=swipe_duration, callback=lambda : self._highlight_and_fade_out(highlight_duration, fade_out_duration), curveType=uiconst.ANIM_LINEAR)

    def _highlight_and_fade_out(self, highlight_duration, fade_out_duration):
        animations.FadeTo(obj=self, startVal=1.0, endVal=1.5, duration=highlight_duration, callback=lambda : self._fade_out(fade_out_duration))

    def _fade_out(self, fade_out_duration):
        animations.FadeOut(self, duration=fade_out_duration, callback=self._hide)

    def _hide(self):
        self.state = uiconst.UI_HIDDEN
        self.width = 0
