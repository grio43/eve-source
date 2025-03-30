#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charSelection\surveyBanner.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from surveys import GetSurveyByID
from carbonui.uicore import uicore
FEATURE_BAR_INNER_HEIGHT = 90
BANNER_WIDTH = 550
IDLE_OPACITY = 0.8
DOWN_OPACITY = 1.2

class SurveyBanner(Container):
    default_state = uiconst.UI_NORMAL
    default_opacity = IDLE_OPACITY

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.surveyID = attributes.surveyID
        survey = GetSurveyByID(self.surveyID)
        self.bannerSprite = Sprite(name='bannerSprite', parent=self, align=uiconst.CENTER, pos=(0,
         0,
         BANNER_WIDTH,
         FEATURE_BAR_INNER_HEIGHT), state=uiconst.UI_DISABLED, texturePath=survey.GetBannerTexturePath())

    def OnClick(self):
        sm.GetService('survey').AccessSurvey()

    def OnMouseEnter(self, *args):
        animations.FadeTo(self, self.opacity, 1.0, duration=0.1)

    def OnMouseExit(self, *args):
        animations.FadeTo(self, self.opacity, IDLE_OPACITY, duration=0.1)

    def OnMouseDown(self, *args):
        animations.FadeTo(self, self.opacity, DOWN_OPACITY, duration=0.1)
        self.bannerSprite.top = 1

    def OnMouseUp(self, *args):
        self.bannerSprite.top = 0
        currentMouseOver = uicore.uilib.mouseOver
        animations.StopAnimation(self, 'opacity')
        if currentMouseOver == self or not currentMouseOver.IsUnder(self):
            self.opacity = 1.0
        else:
            self.opacity = IDLE_OPACITY
