#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\regionalui\kr\koreansplash.py
import logging
import carbonui.fontconst
log = logging.getLogger(__name__)
import localization
from carbonui import const as uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel
from carbonui.primitives import container
from carbonui.primitives import fill
import uthread2
from carbonui.uianimations import animations
from regionalui import const as regionalui_const
from regionalui.addictionwarningcontainer import AddictionWarningContainer
import trinity
_WHITE = (1.0, 1.0, 1.0, 1.0)
_BLACK = (0.0, 0.0, 0.0, 1.0)
_TRANSPARENT = (0.0, 0.0, 0.0, 0.0)
_FADE_IN_DELAY = 0.1
_FADE_IN_DURATION = 0.4
_DISPLAY_DURATION = 6.0
_FADE_OUT_DURATION = 0.4
_CLOSE_OUT_DURATION = 0.2
TOTAL_DURATION = _FADE_IN_DELAY + _FADE_IN_DURATION + _DISPLAY_DURATION + _FADE_OUT_DURATION + _CLOSE_OUT_DURATION

class AutoScalingCaption(eveLabel.EveStyleLabel):
    default_name = 'AutoScalingCaption'
    default_fontsize = 26
    default_bold = False
    default_color = _WHITE
    default_fontStyle = carbonui.fontconst.STYLE_HEADER
    default_lineSpacing = 0.5

    def __init__(self, ratioOfWidth = 1.0, relativeTo = None, resizeThreshold = 0.01, **kwargs):
        self.ratioOfWidth = ratioOfWidth
        self.relativeTo = relativeTo
        self.resizeThreshold = resizeThreshold
        super(AutoScalingCaption, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        super(AutoScalingCaption, self).ApplyAttributes(attributes)

    def GetRelativeTo(self):
        return self.relativeTo or self.parent

    def GetCurrentWidthRatio(self):
        if self.GetRelativeTo().displayWidth <= 0:
            return -1.0
        myWidth = self.displayWidth
        if myWidth <= 0:
            myWidth = self.MeasureTextSize(self.text)[0]
        return float(myWidth) / self.GetRelativeTo().displayWidth

    def AdaptSize(self):
        currentRatio = self.GetCurrentWidthRatio()
        if currentRatio <= 0.0:
            log.debug("AutoScalingCaption::AdaptSize() - Don't adapt yet... I or my parent have no size yet!!!")
        elif abs(currentRatio - self.ratioOfWidth) >= self.resizeThreshold:
            modifier = self.ratioOfWidth / currentRatio
            self.fontsize = int(self.fontsize * modifier / uicore.desktop.dpiScaling)

    def OnUIScalingChange(self, *args):
        super(AutoScalingCaption, self).OnUIScalingChange(*args)
        self.AdaptSize()

    def OnParentResize(self):
        self.AdaptSize()


class KoreanSplashScreen(container.Container):
    default_name = 'KoreanSplashScreen'
    default_align = uiconst.TOALL
    default_state = uiconst.UI_NORMAL
    default_bgColor = _BLACK

    def ApplyAttributes(self, attributes):
        super(KoreanSplashScreen, self).ApplyAttributes(attributes)
        self.fade_overlay = fill.Fill(parent=self, align=uiconst.TOALL, color=_BLACK, opacity=1.0)
        self.warning_text = AutoScalingCaption(parent=self, align=uiconst.CENTER, text=localization.GetByLabel(regionalui_const.SPLASH_TEXT_PATH), ratioOfWidth=0.7, opacity=1.0)
        self.rating_icons = AddictionWarningContainer(name='KoreanRatingIcons', parent=self, opacity=1.0, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, bgColor=_TRANSPARENT, width=regionalui_const.get_ratings_width(), display=False)
        trinity.WaitForResourceLoads()
        self.rating_icons.display = True
        uthread2.call_after_wallclocktime_delay(self.FadeIn, _FADE_IN_DELAY)

    def FadeIn(self):
        animations.FadeOut(obj=self.fade_overlay, duration=_FADE_IN_DURATION, callback=self.OnFadeInDone)

    def OnFadeInDone(self):
        self.fade_overlay.display = False
        uthread2.call_after_wallclocktime_delay(self.FadeOut, _DISPLAY_DURATION)

    def FadeOut(self):
        self.fade_overlay.display = True
        animations.FadeIn(obj=self.fade_overlay, duration=_FADE_OUT_DURATION, callback=self.OnFadeOutDone)
        try:
            sm.GetService('loading').FadeIn(_FADE_OUT_DURATION)
        except Exception as ex:
            log.exception('KoreanSplashScreen::FadeOut Exception: %r', ex)

    def OnFadeOutDone(self):
        self.warning_text.display = False
        self.rating_icons.display = False
        self.fade_overlay.display = True
        self.fade_overlay.opacity = 1.0
        self.fade_overlay.color = _BLACK
        self.bgFill.display = False
        self.CloseOut()

    def CloseOut(self):
        animations.FadeOut(obj=self.fade_overlay, duration=_CLOSE_OUT_DURATION, callback=self.OnCloseOutDone)

    def OnCloseOutDone(self):
        self.Close()

    def _OnResize(self, *args):
        super(KoreanSplashScreen, self)._OnResize(*args)
        self.warning_text.OnParentResize()
