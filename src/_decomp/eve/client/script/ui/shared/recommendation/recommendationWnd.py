#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\recommendation\recommendationWnd.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbonui import uiconst
from carbonui.primitives.frame import Frame
from carbonui.uianimations import animations
from contextualOffers.client.UI.bracketBorderWindow import BracketBorderWindow
from carbonui.control.button import Button
from carbonui.decorative.blurredSceneUnderlay import BlurredSceneUnderlay
from eve.client.script.ui.shared.recommendation.const import Sounds
from eve.client.script.ui.shared.recommendation.recommendationCont import RecommendationsCont

class RecommendationWnd(BracketBorderWindow):
    __notifyevents__ = ['OnTreatmentWndOpenedOtherWnd', 'OnRecommendationAccepted']
    default_windowID = 'recommendationWnd'
    default_fixedWidth = 1068
    default_fixedHeight = 500
    mainContentWidth = 950
    mainContentHeight = 415
    innerContWidth = 1050
    innerContHeight = 500
    bracketWidth = 1068
    bracketHeadWidth = 500
    bottomBracketOffset = 0
    openingDurationSec = 0.05
    openingDuration2Sec = 0.2
    closingDurationSec = 0.2
    closingDuration2Sec = 0.2
    fadeOutDurationSec = 0.1
    fadeInDurationSec = 0.3

    def DebugReload(self, *args):
        self.Close()
        wnd = RecommendationWnd.Open()
        wnd.ShowDialog(modal=True, state=uiconst.UI_PICKCHILDREN, closeWhenClicked=True)

    def ApplyAttributes(self, attributes):
        super(RecommendationWnd, self).ApplyAttributes(attributes)
        self.recommendationSvc = sm.GetService('recommendationSvc')
        self.innerCont.topPad = 40
        self.innerCont.bgFill.opacity = 0.2
        self.outerCont.state = uiconst.UI_NORMAL
        if session.role & ROLE_PROGRAMMER:
            self._ConstructDebugButtons()

    def _ConstructDebugButtons(self):
        Button(parent=self.sr.main, label='Reload', align=uiconst.TOPRIGHT, func=self.DebugReload, top=14, idx=0)

    def _AnimEnter(self):
        BracketBorderWindow._AnimEnter(self)
        animations.MorphScalar(self.blurredUnderlay, 'padTop', startVal=self.innerContHeight / 2, endVal=0.0, duration=self.openingDuration2Sec, timeOffset=self.openingDurationSec)
        animations.MorphScalar(self.blurredUnderlay, 'padBottom', startVal=self.innerContHeight / 2, endVal=0.0, duration=self.openingDuration2Sec, timeOffset=self.openingDurationSec)

    def _AnimExit(self):
        BracketBorderWindow._AnimExit(self)
        animations.MorphScalar(self.blurredUnderlay, 'padTop', startVal=0.0, endVal=self.innerContHeight / 2, duration=self.closingDuration2Sec, timeOffset=self.closingDurationSec)
        animations.MorphScalar(self.blurredUnderlay, 'padBottom', startVal=0.0, endVal=self.innerContHeight / 2, duration=self.closingDuration2Sec, timeOffset=self.closingDurationSec)

    def ConstructInnerFrame(self):
        BracketBorderWindow.ConstructInnerFrame(self)
        self.blurredUnderlay = BlurredSceneUnderlay(name='blurredUnderlay2', parent=self.innerCont, align=uiconst.TOALL, opacity=0.9)
        Frame(name='bgFillSprite', parent=self.frameCont, color=(0, 0, 0, 0.25), texturePath='res:/UI/Texture/Shared/BracketBorderWindow/mask_Window770.png', cornerSize=16, padding=1)

    def ConstructContent(self):
        RecommendationsCont(parent=self.frameCont)
        PlaySound(Sounds.ATMOSPHERE_START)

    def OnTreatmentWndOpenedOtherWnd(self, newWnd):
        self.Close()

    def OnRecommendationAccepted(self, *args, **kwargs):
        self.CloseButtonClicked()

    def CloseByUser(self, *args):
        self.CloseButtonClicked()

    def DeferredClose(self):
        super(RecommendationWnd, self).CloseByUser()

    def Close(self, *args, **kwargs):
        PlaySound(Sounds.ATMOSPHERE_STOP)
        BracketBorderWindow.Close(self, *args, **kwargs)
