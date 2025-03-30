#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\newFeatureNotifyWnd.py
import math
import trinity
import uthread2
from carbonui import uiconst, TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from carbon.client.script.environment.AudioUtil import PlaySound
from eve.client.script.ui.control.eveLabel import Label
from carbonui.control.window import Window
from eveui import ButtonIcon
from localization import GetByLabel
from eve.client.script.ui.shared.message_bus.newsCarouselMessenger import NewsCarouselMessenger
SPRITE_OPACITY = 0.2
IMG_HEIGHT = 400
DURATION = 0.3
SECOND_DURATION = 0.3
OUT_DURATION = 0.2
OUT_SECOND_DURATION = 0.2
MAIN_SPRITE_WIDTH = 946
MAIN_SPRITE_HEIGHT = 416

class OverlayButton(Container):
    FRAME_OPACITY_IDLE = 0.2
    FRAME_OPACITY_HOVER = 0.7
    FRAME_GLOW_BRIGHTNESS_IDLE = 0.0
    FRAME_GLOW_BRIGHTNESS_HOVER = 0.7
    _hovered = False

    def __init__(self, callback, state = uiconst.UI_NORMAL, **kwargs):
        self._callback = callback
        super(OverlayButton, self).__init__(state=state, **kwargs)
        self._frame = Frame(parent=self, align=uiconst.TOALL, opacity=self._get_frame_opacity(), outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=self._get_frame_glow_brightness(), texturePath='res:/UI/Texture/classes/NewFeatureNotify/frame_Window.png', cornerSize=10, idx=0)

    def _get_frame_opacity(self):
        if self._hovered:
            return self.FRAME_OPACITY_HOVER
        else:
            return self.FRAME_OPACITY_IDLE

    def _get_frame_glow_brightness(self):
        if self._hovered:
            return self.FRAME_GLOW_BRIGHTNESS_HOVER
        else:
            return self.FRAME_GLOW_BRIGHTNESS_IDLE

    def _update_frame_opacity(self, duration = 0.0):
        if duration > 0.0:
            animations.FadeTo(self._frame, startVal=self._frame.opacity, endVal=self._get_frame_opacity(), duration=duration)
        else:
            self._frame.opacity = self._get_frame_opacity()

    def _update_frame_glow_brightness(self, duration = 0.0):
        if duration > 0.0:
            animations.MorphScalar(self._frame, 'glowBrightness', startVal=self._frame.glowBrightness, endVal=self._get_frame_glow_brightness(), duration=duration)
        else:
            self._frame.glowBrightness = self._get_frame_glow_brightness()

    def OnMouseEnter(self, *args):
        self._hovered = True
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self._update_frame_opacity(duration=uiconst.TIME_ENTRY)
        self._update_frame_glow_brightness(duration=uiconst.TIME_ENTRY)

    def OnMouseExit(self, *args):
        self._hovered = False
        self._update_frame_opacity(duration=uiconst.TIME_EXIT)
        self._update_frame_glow_brightness(duration=uiconst.TIME_EXIT)

    def OnClick(self, *args):
        self._callback()


class NewFeatureNotifyWnd(Window):
    default_name = 'NewFeatureNotifyWnd'
    default_windowID = 'NewFeatureNotifyWnd'
    default_fixedWidth = 1043
    default_fixedHeight = 550
    default_isLightBackgroundConfigurable = False
    default_isMinimizable = False
    default_isCollapseable = False
    default_isStackable = False
    default_isKillable = False
    default_isLockable = False
    default_isOverlayable = False
    hasAnimated = False

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.features = attributes.newFeatures
        self.currentFeature = None
        self.sr.headerParent.Hide()
        self.mainCont = Container(name='mainCont', parent=self.sr.main, state=uiconst.UI_PICKCHILDREN, opacity=1.0, padding=2, clipChildren=True)
        self.contentCont = Container(name='contentCont', parent=self.mainCont, align=uiconst.CENTERTOP, opacity=0.0, top=42, width=MAIN_SPRITE_WIDTH, height=MAIN_SPRITE_HEIGHT)
        self.underlayCont = Container(name='underlayCont', parent=self.mainCont, align=uiconst.CENTERTOP, opacity=0, top=42, width=MAIN_SPRITE_WIDTH, height=MAIN_SPRITE_HEIGHT)
        self.backgroundCont = Container(name='backgroundCont', parent=self.mainCont, align=uiconst.CENTERTOP, bgColor=(0, 0, 0, 0.3), opacity=0.0, width=self.width - 30, height=500)
        self.bannerSprite = Sprite(name='bannerSprite', parent=self.underlayCont, align=uiconst.CENTERTOP, width=MAIN_SPRITE_WIDTH, height=MAIN_SPRITE_HEIGHT, textureSecondaryPath='res:/UI/Texture/classes/newFeatureNotify/mask_Window.png', spriteEffect=trinity.TR2_SFX_MODULATE)
        self.bannerVideoSprite = StreamingVideoSprite(name='bannerVideoSprite', parent=self.underlayCont, align=uiconst.CENTERTOP, width=MAIN_SPRITE_WIDTH, height=MAIN_SPRITE_HEIGHT, textureSecondaryPath='res:/UI/Texture/classes/newFeatureNotify/mask_Window.png', spriteEffect=trinity.TR2_SFX_MODULATE)
        self.SetUpBracketSprites()
        backgroundWhite = (0.9, 0.9, 0.9, 1.0)
        self.SetUpTopLeftCorner(backgroundWhite)
        self.ConstructButtons(MAIN_SPRITE_WIDTH, MAIN_SPRITE_HEIGHT)
        self.LoadFeature()

    def SetUpTexts(self, myWidth):
        bulletContHeight = len(self.bulletPoints) * 20 + 20
        self.bulletCont = Container(parent=self.contentCont, name='bulletCont', align=uiconst.TOBOTTOM, width=myWidth - 4, height=bulletContHeight, bgColor=(0, 0, 0, 0.3), padLeft=2, padRight=2, padBottom=12)
        self.descriptionContainer = Container(parent=self.contentCont, name='descriptionCont', align=uiconst.TOBOTTOM, height=25, width=MAIN_SPRITE_WIDTH)
        self.titleContainer = Container(parent=self.contentCont, name='titleCont', align=uiconst.TOBOTTOM, height=45, width=MAIN_SPRITE_WIDTH)
        self.bulletPointCont = Container(parent=self.bulletCont, align=uiconst.TOALL)
        self.titleCaption = Label(parent=self.titleContainer, align=uiconst.CENTERLEFT, color=TextColor.HIGHLIGHT, fontsize=36, left=20)
        self.descriptionLabel = Label(parent=self.descriptionContainer, align=uiconst.TOPLEFT, fontsize=16, color=(1.0, 1.0, 1.0, 1.0), maxHeight=10, left=20, shadowSpriteEffect=None, bold=True)

    def PopulateBulletPoints(self):
        bulletContainerParentHeight = 20
        for i, bulletPoint in enumerate(self.bulletPoints):
            bulletContainer = Container(parent=self.bulletPointCont, align=uiconst.TOTOP, width=MAIN_SPRITE_WIDTH, height=20, top=0 if i else 10)
            Sprite(parent=bulletContainer, align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/classes/NewFeatureNotify/bulletpoint.png', width=8, height=8, color=(0.75, 0.51, 0.08, 1.0), left=20, top=0)
            bulletLabel = Label(parent=bulletContainer, align=uiconst.CENTERLEFT, text=bulletPoint, fontsize=16, bold=True, color=TextColor.HIGHLIGHT, left=35, wrapMode=uiconst.WRAPMODE_FORCEWORD, maxWidth=900)
            w, h = bulletLabel.GetAbsoluteSize()
            bulletContainerParentHeight += h * 1.1
            bulletContainer.height = h * 1.1

        self.bulletCont.height = bulletContainerParentHeight

    def SetUpTopLeftCorner(self, backgroundWhite):
        self.newTextContainer = Container(parent=self.contentCont, align=uiconst.TOPLEFT, width=42, height=41, left=42, top=1)
        Label(parent=self.newTextContainer, text=GetByLabel('UI/NewFeatureNotify/New'), align=uiconst.CENTERLEFT, fontsize=18, padLeft=4, uppercase=True, color=(0.9, 0.9, 0.9, 1.0))
        Sprite(name='newsIcon', parent=self.contentCont, align=uiconst.TOPLEFT, width=30, height=30, top=6, left=6, color=(0, 0, 0, 1), texturePath='res:/UI/Texture/classes/NewFeatureNotify/news_Icon.png')
        Sprite(name='typeHighlight', parent=self.contentCont, align=uiconst.TOPLEFT, width=42, height=42, color=backgroundWhite, texturePath='res:/UI/Texture/classes/NewFeatureNotify/type_Highlight.png')

    def SetUpBracketSprites(self):
        self.topBracketContainer = Container(name='topBracketCont', parent=self.mainCont, align=uiconst.CENTERTOP, width=1030, height=7, opacity=0)
        self.topBracketTail = StretchSpriteHorizontal(name='topSpriteBracket', parent=self.topBracketContainer, align=uiconst.CENTERTOP, width=1030, height=7, leftEdgeSize=16, rightEdgeSize=16, texturePath='res:/UI/Texture/classes/NewFeatureNotify/bracketTails_Window.png')
        self.topBracketHead = Sprite(name='topSpriteHead', parent=self.topBracketContainer, align=uiconst.CENTERTOP, width=270, height=5, top=1, texturePath='res:/UI/Texture/classes/NewFeatureNotify/bracketHead_Window.png')
        self.bottomBracketContainer = Container(name='bottomBracketCont', parent=self.mainCont, align=uiconst.CENTERBOTTOM, width=1030, height=7, top=46, opacity=0)
        self.bottomBracketTail = StretchSpriteHorizontal(name='bottomSpriteBracket', parent=self.bottomBracketContainer, align=uiconst.CENTERBOTTOM, width=1030, height=7, leftEdgeSize=16, rightEdgeSize=16, texturePath='res:/UI/Texture/classes/NewFeatureNotify/bracketTails_Window.png', rotation=math.pi)
        self.bottomBracketHead = Sprite(name='bottomSpriteHead', parent=self.bottomBracketContainer, align=uiconst.CENTERBOTTOM, width=270, height=5, top=1, texturePath='res:/UI/Texture/classes/NewFeatureNotify/bracketHead_Window.png', rotation=math.pi)

    def ConstructButtons(self, mainSpriteWidth, mainSpriteHeight):
        self.closeButton = ButtonIcon(name='closeButton', parent=self.mainCont, align=uiconst.TOPRIGHT, size=16, left=12, top=12, color=(1, 1, 1), on_click=self.CloseByUser, hint=GetByLabel('UI/Common/Buttons/Close'), texture_path='res:/UI/Texture/Shared/DarkStyle/windowClose.png')
        OverlayButton(name='callToActionButton', parent=self.contentCont, align=uiconst.CENTERTOP, width=mainSpriteWidth, height=mainSpriteHeight, callback=self.ExecuteAction)

    def LoadFeature(self):
        uthread2.start_tasklet(self._DisplayFeature)

    def _DisplayFeature(self):
        self.GetCurrentFeature()
        self.bulletPoints = self.currentFeature.GetBulletPoints()
        self.SetUpTexts(MAIN_SPRITE_WIDTH)
        self._UpdateSpriteAndVideoSprite(self.currentFeature)
        self.titleCaption.text = self.currentFeature.GetName()
        self.descriptionLabel.text = self.currentFeature.GetDescription()
        if self.currentFeature.GetNeocomBtnID():
            sm.GetService('neocom').Blink(self.currentFeature.GetNeocomBtnID())
        self.currentFeature.MarkAsSeen()
        self.PopulateBulletPoints()
        self._AnimEnter()
        self.LogFeatureDisplayed()

    def LogFeatureDisplayed(self):
        if not self.currentFeature or not self.currentFeature.featureID:
            return
        message_bus = NewsCarouselMessenger(sm.GetService('publicGatewaySvc'))
        message_bus.displayed(self.currentFeature.featureID)

    def GetCurrentFeature(self):
        self.currentFeature = self.features[0]
        for feature in self.features:
            if feature.featureID > self.currentFeature.featureID:
                self.currentFeature = feature

    def ExecuteAction(self, *args):
        uthread2.start_tasklet(self.currentFeature.ExecuteCallToAction)
        if self.currentFeature.GetCallToActionMethod():
            self.LogFeatureAcknowledged()
            self._AnimExit()
            self.CloseByUser()

    def LogFeatureAcknowledged(self):
        if not self.currentFeature or not self.currentFeature.featureID:
            return
        message_bus = NewsCarouselMessenger(sm.GetService('publicGatewaySvc'))
        message_bus.acknowledged(self.currentFeature.featureID)

    def _UpdateSpriteAndVideoSprite(self, feature):
        if feature.IsVideo():
            self.bannerVideoSprite.SetVideoPath(feature.GetTexturePath(), videoLoop=True)
        else:
            self.bannerSprite.texturePath = feature.GetTexturePath()
        self.bannerSprite.display = not feature.IsVideo()
        self.bannerVideoSprite.display = feature.IsVideo()

    def _AnimExit(self, shouldExecuteAction = False):
        animations.FadeOut(self.contentCont, duration=OUT_DURATION)
        animations.FadeOut(self.underlayCont, duration=OUT_DURATION)
        animations.FadeOut(self.backgroundCont, duration=OUT_DURATION)
        animations.FadeOut(self.mainCont, duration=OUT_DURATION + OUT_SECOND_DURATION + 0.1)
        animations.MoveTo(self.topBracketContainer, None, (0, 267), OUT_SECOND_DURATION, timeOffset=OUT_DURATION)
        animations.MoveTo(self.bottomBracketContainer, (0, 46), (0, 267), OUT_SECOND_DURATION, timeOffset=OUT_DURATION)
        animations.FadeOut(self.topBracketContainer, duration=0.1, timeOffset=OUT_DURATION + OUT_SECOND_DURATION, callback=self.FinalizeAnimation)

    def FinalizeAnimation(self):
        self.hasAnimated = True

    def _AnimEnter(self):
        openingOffset = 0.3
        animations.FadeIn(self.topBracketContainer, endVal=SPRITE_OPACITY, duration=openingOffset)
        animations.FadeIn(self.bottomBracketContainer, endVal=SPRITE_OPACITY, duration=openingOffset)
        animations.MoveTo(self.topBracketContainer, (0, 267), None, SECOND_DURATION, timeOffset=openingOffset)
        animations.MoveTo(self.bottomBracketContainer, (0, 267), (0, 46), SECOND_DURATION, timeOffset=openingOffset)
        animations.FadeIn(self.contentCont, duration=DURATION, timeOffset=SECOND_DURATION + openingOffset)
        animations.FadeIn(self.underlayCont, duration=DURATION, timeOffset=SECOND_DURATION + openingOffset)
        animations.FadeIn(self.backgroundCont, duration=DURATION, timeOffset=SECOND_DURATION + openingOffset)
        animations.FadeTo(self.descriptionLabel, 0.0, 1.0, duration=0.1, timeOffset=0.2 + DURATION + openingOffset)

    @classmethod
    def Open(cls, *args, **kwargs):
        PlaySound('news_window_open_play')
        return super(NewFeatureNotifyWnd, cls).Open(*args, **kwargs)

    def Close(self, *args, **kwargs):
        PlaySound('news_window_close_play')
        super(NewFeatureNotifyWnd, self).Close(*args, **kwargs)

    def CloseByUser(self, *args):
        if not self.hasAnimated:
            self._AnimExit()
            uthread2.Sleep(OUT_DURATION + OUT_SECOND_DURATION)
        self.killable = True
        super(NewFeatureNotifyWnd, self).CloseByUser(*args)
