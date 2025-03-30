#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\empireui\empireBanner.py
import carbonui.const as uiconst
from eve.client.script.ui import eveColor
from carbonui.fontconst import STYLE_HEADER
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from charactercreator.client.empireSelectionData import GetEmpireLogo, GetEmpireSeal, GetEmpireQuote
import charactercreator.client.scalingUtils as ccScalingUtils
import charactercreator.const as ccConst
from eve.client.script.ui.login.charcreation.empireui.empireThemedButtons import FLARE_VIDEO_BY_RACE, CURVED_GRADIENT_TEXTURE_BY_RACE, HIGHLIGHT_TINT_BY_RACE
from eve.client.script.ui.login.charcreation.label import CCLabel
from eve.client.script.ui.login.charcreation.technologyViewUtils import LineDecoration
from eve.client.script.ui.shared.agencyNew.ui.controls.warningContainer import WarningContainer
from eve.client.script.ui.util.uix import GetTextHeight
from eve.common.lib.appConst import raceAmarr, raceCaldari, raceGallente, raceMinmatar
from localization import GetByMessageID, GetByLabel
import math
import trinity
from uthread2 import call_after_wallclocktime_delay
EMPIRE_BANNERS_OPACITY = 0.3
EMPIRE_QUOTE_FADE_IN_DELAY = 0.25
EMPIRE_QUOTE_FADE_IN_DURATION = 0.7
EMPIRE_QUOTE_TEXT_FADE_IN_DELAY = 0.25
EMPIRE_QUOTE_TEXT_FADE_IN_DURATION = 0.5
EMPIRE_QUOTE_TEXT_FADE_OUT_DURATION = 0.3
EMPIRE_QUOTE_FADE_OUT_DELAY = 0.0
EMPIRE_QUOTE_FADE_OUT_DURATION = 0.3
EMPIRE_LOGOS_TOP = -16
RACE_SPRITE_BG_OPACITY = 0.3
EMPIRE_QUOTE_FONTSIZE = 12
EMPIRE_QUOTE_LINESPACING = 0.25
EMPIRE_QUOTE_WIDTH = 166
EMPIRE_QUOTE_TOP = 40
EMPIRE_QUOTE_BOTTOM_MIN = 25
EMPIRE_QUOTE_PHRASE_OPACITY = 0.75
EMPIRE_QUOTE_ATTRIBUTION_OPACITY = 1.0
EMPIRE_QUOTE_TINT_BY_RACE = {raceAmarr: (1.0, 0.94, 0.84),
 raceCaldari: (0.85, 0.95, 1.0),
 raceGallente: (0.75, 1.0, 1.0),
 raceMinmatar: (1.0, 0.85, 0.8)}
UPPER_HEIGHT = 182
LOWER_HEIGHT = 164
FLARE_WIDTH = 284
FLARE_HEIGHT = 160
BANNER_TEXT_FONTSIZE = 14
EXTRA_FRAME_TITLE_PADDING = 12
CURVED_GRADIENT_OPACITY = 0.5
LINE_HEIGHT = 4
LINE_DECO_WIDTH_MIN_RES = 41
LINE_CURVED_GRADIENT_WIDTH = 156
LINE_CURVED_GRADIENT_HEIGHT = 22
CURVED_GRADIENT_TEXTURE_BASE = 'res:/UI/Texture/Classes/EmpireSelection/curvedGradientBase.png'
HEADER_BACKGROUND_OPACITY = 0.75

class BannerContents(Container):

    def ApplyAttributes(self, attributes):
        super(BannerContents, self).ApplyAttributes(attributes)
        self.raceID = attributes.raceID
        self.audioSvc = sm.GetService('audio')
        self.raceSprite = None
        self.raceSpriteBg = None
        self.isHovered = False
        self.CalculateSizes()
        self._ShowRaceIcon()
        self._ShowEmpireQuote()
        self._ShowFlare()
        self._ShowEmpireQuoteBackground()
        self._ShowCurvedGradient()

    def CalculateSizes(self):
        scaleFactor = ccScalingUtils.GetScaleFactor()
        self.upperHeight = UPPER_HEIGHT * scaleFactor
        self.lowerHeight = LOWER_HEIGHT * scaleFactor
        self.raceIconsTop = EMPIRE_LOGOS_TOP * scaleFactor
        self.raceIconBgTop = ccConst.RACE_ICON_BG_TOP * scaleFactor
        self.raceIconSize = ccConst.RACE_ICON_SIZE * scaleFactor
        self.raceIconSizeHover = ccConst.RACE_ICON_HOVER_SIZE * scaleFactor
        self.flareWidth = FLARE_WIDTH * scaleFactor
        self.flareHeight = FLARE_HEIGHT * scaleFactor
        self.CalculateEmpireQuoteSizes(scaleFactor)

    def CalculateEmpireQuoteSizes(self, scaleFactor):
        self.quoteFontsize = EMPIRE_QUOTE_FONTSIZE * scaleFactor
        self.quoteTop = EMPIRE_QUOTE_TOP * scaleFactor
        self.quoteWidth = EMPIRE_QUOTE_WIDTH * scaleFactor
        phrase, attribution = self.GetEmpireQuoteBreakdown()
        self.quoteHeightPhrase = self.CalculateEmpireQuoteTextHeight(phrase)
        self.quoteHeightAttribution = self.CalculateEmpireQuoteTextHeight(attribution)

    def GetEmpireQuoteBreakdown(self):
        empireText = GetByMessageID(GetEmpireQuote(self.raceID))
        quoteBreakdown = empireText.split('<br/><br/>')
        attribution = quoteBreakdown[-1]
        phrase = empireText.replace(attribution, '')
        return (phrase, attribution)

    def CalculateEmpireQuoteTextHeight(self, text):
        textHeight = 0
        for line in text.split('<br/><br/>'):
            lineHeight = GetTextHeight(strng=line or '0', width=self.quoteWidth, fontsize=self.quoteFontsize, fontStyle=STYLE_HEADER)
            textHeight += lineHeight + lineHeight * EMPIRE_QUOTE_LINESPACING

        return textHeight

    def _ShowRaceIcon(self):
        self.raceSprite = Sprite(name='raceSprite', parent=self, align=uiconst.CENTERTOP, texturePath='', width=self.raceIconSize, height=self.raceIconSize, state=uiconst.UI_DISABLED, top=self.raceIconsTop)
        self.raceSpriteBg = Sprite(name='raceSpriteBg', parent=self, align=uiconst.CENTERTOP, texturePath='', width=self.raceIconSize, height=self.raceIconSize, state=uiconst.UI_DISABLED, top=self.raceIconBgTop + self.raceIconsTop)
        spritePath = GetEmpireLogo(self.raceID)
        bgSpritePath = GetEmpireSeal(self.raceID)
        self.raceSprite.SetTexturePath(spritePath)
        self.raceSpriteBg.SetTexturePath(bgSpritePath)
        self.raceSpriteBg.SetAlpha(0.0)

    def DesaturateRaceIcon(self):
        self.raceSprite.spriteEffect = trinity.TR2_SFX_SOFTLIGHT
        self.raceSprite.opacity = 0.5
        self.raceSprite.saturation = 0.0

    def _ShowCurvedGradient(self):
        bannerWidth = ccScalingUtils.GetBannerWidth()
        self.curvedGradientContainer = Container(name='curvedGradientContainer', parent=self, align=uiconst.TOTOP_NOPUSH, width=bannerWidth, height=self.upperHeight, state=uiconst.UI_DISABLED, opacity=0.0)
        self.curvedGradient = Sprite(name='curvedGradient', parent=self.curvedGradientContainer, align=uiconst.TOLEFT, texturePath=CURVED_GRADIENT_TEXTURE_BY_RACE[self.raceID], width=bannerWidth, height=self.upperHeight, opacity=CURVED_GRADIENT_OPACITY)

    def _ShowEmpireQuote(self):
        self.textCont = Container(name='empireQuoteContainer', parent=self, align=uiconst.TOTOP_NOPUSH, width=self.quoteWidth, height=self.quoteHeightPhrase + self.quoteHeightAttribution, top=self.upperHeight + self.quoteTop, opacity=0.0)
        self.textWrapper = Container(name='empireQuoteWrapper', parent=self.textCont, align=uiconst.CENTER, width=self.quoteWidth, height=self.quoteHeightPhrase + self.quoteHeightAttribution)
        phrase, attribution = self.GetEmpireQuoteBreakdown()
        self.empireQuotePhrase = CCLabel(name='empireQuotePhrase', parent=self.textWrapper, text='<center>%s</center>' % phrase, align=uiconst.TOTOP, width=self.quoteWidth, height=self.quoteHeightPhrase, color=EMPIRE_QUOTE_TINT_BY_RACE[self.raceID], fontsize=self.quoteFontsize, fontStyle=STYLE_HEADER, bold=False, letterspace=0, lineSpacing=EMPIRE_QUOTE_LINESPACING, opacity=EMPIRE_QUOTE_PHRASE_OPACITY)
        self.empireQuoteAttribution = CCLabel(name='empireQuoteAttribution', parent=self.textWrapper, text='<center>%s</center>' % attribution, align=uiconst.TOTOP, width=self.quoteWidth, height=self.quoteHeightAttribution, color=EMPIRE_QUOTE_TINT_BY_RACE[self.raceID], fontsize=self.quoteFontsize, fontStyle=STYLE_HEADER, bold=True, letterspace=0, lineSpacing=EMPIRE_QUOTE_LINESPACING, opacity=EMPIRE_QUOTE_ATTRIBUTION_OPACITY)

    def _ShowEmpireQuoteBackground(self):
        bannerWidth = ccScalingUtils.GetBannerWidth()
        scaleFactor = ccScalingUtils.GetScaleFactor()
        bottomMin = EMPIRE_QUOTE_BOTTOM_MIN * scaleFactor
        height = max(self.lowerHeight, self.quoteTop + self.quoteHeightPhrase + self.quoteHeightAttribution + bottomMin)
        self.empireQuoteBackgroundContainer = Container(name='empireQuoteBackgroundContainer', parent=self, align=uiconst.TOTOP_NOPUSH, width=bannerWidth, height=height, top=self.upperHeight, opacity=0.0)
        GradientSprite(name='empireQuoteBackgroundGradient', bgParent=self.empireQuoteBackgroundContainer, rgbData=[(0, (0.0, 0.0, 0.0))], alphaData=[(0, 0.0),
         (0.4, 0.5),
         (0.6, 0.5),
         (1.0, 0.0)])
        self.lineDecoration = LineDecoration(name='empireQuoteLineDecoration', parent=self.empireQuoteBackgroundContainer, align=uiconst.TOBOTTOM_NOPUSH, width=bannerWidth, height=LINE_HEIGHT, lineWidth=bannerWidth, lineDecorationWidth=LINE_DECO_WIDTH_MIN_RES * scaleFactor, invert=True, lineColor=HIGHLIGHT_TINT_BY_RACE[self.raceID])
        self.lineDecorationCurvedGradientContainer = Container(name='lineDecorationCurvedGradientContainer', parent=self.empireQuoteBackgroundContainer, align=uiconst.TOBOTTOM_NOPUSH, width=LINE_CURVED_GRADIENT_WIDTH * scaleFactor, height=LINE_CURVED_GRADIENT_HEIGHT * scaleFactor, state=uiconst.UI_DISABLED)
        self.lineDecorationCurvedGradient = Sprite(name='lineDecorationCurvedGradient', parent=self.lineDecorationCurvedGradientContainer, align=uiconst.CENTERTOP, texturePath=CURVED_GRADIENT_TEXTURE_BY_RACE[self.raceID], width=LINE_CURVED_GRADIENT_WIDTH * scaleFactor, height=LINE_CURVED_GRADIENT_HEIGHT * scaleFactor, opacity=CURVED_GRADIENT_OPACITY)

    def _ShowFlare(self):
        bannerWidth = ccScalingUtils.GetBannerWidth()
        self.flareContainer = Container(name='flareContainer', parent=self, align=uiconst.TOTOP_NOPUSH, width=self.flareWidth, height=self.flareHeight, top=self.upperHeight - self.flareHeight / 2, left=-(self.flareWidth - bannerWidth) / 2, opacity=0.0)
        self.flareWrapper = Container(name='flareWrapper', parent=self.flareContainer, align=uiconst.TOLEFT, width=self.flareWidth, height=self.flareHeight)
        self.flare = StreamingVideoSprite(name='flare', parent=self.flareWrapper, align=uiconst.TOALL, videoPath=FLARE_VIDEO_BY_RACE[self.raceID], state=uiconst.UI_DISABLED, blendMode=trinity.TR2_SBM_BLEND, spriteEffect=trinity.TR2_SFX_COPY, videoLoop=True, disableAudio=True)

    def AnimateEntered(self):
        self.isHovered = True
        quoteDuration = EMPIRE_QUOTE_FADE_IN_DURATION
        quoteOffset = EMPIRE_QUOTE_FADE_IN_DELAY
        quoteTextDuration = EMPIRE_QUOTE_TEXT_FADE_IN_DURATION
        quoteTextOffset = quoteOffset + EMPIRE_QUOTE_TEXT_FADE_IN_DELAY
        self.raceSpriteBg.width = self.raceIconSizeHover
        self.raceSpriteBg.height = self.raceIconSizeHover
        animation = animations.FadeIn
        animation(self.raceSpriteBg, duration=quoteDuration, timeOffset=quoteOffset, endVal=RACE_SPRITE_BG_OPACITY)
        animation(self.curvedGradientContainer, duration=quoteDuration, timeOffset=quoteOffset)
        animation(self.flareContainer, duration=quoteDuration, timeOffset=quoteOffset)
        animation(self.empireQuoteBackgroundContainer, duration=quoteDuration, timeOffset=quoteOffset)
        animation(self.textCont, duration=quoteTextDuration, timeOffset=quoteTextOffset)

    def AnimateExited(self):
        self.isHovered = False
        quoteTextDuration = EMPIRE_QUOTE_TEXT_FADE_OUT_DURATION
        quoteDuration = EMPIRE_QUOTE_FADE_OUT_DURATION
        quoteOffset = EMPIRE_QUOTE_FADE_OUT_DELAY
        animation = animations.FadeOut
        animation(self.textCont, duration=quoteTextDuration)
        animation(self.curvedGradientContainer, duration=quoteDuration, timeOffset=quoteOffset)
        animation(self.raceSpriteBg, duration=quoteDuration, timeOffset=quoteOffset)
        animation(self.flareContainer, duration=quoteDuration, timeOffset=quoteOffset)
        animation(self.empireQuoteBackgroundContainer, duration=quoteDuration, timeOffset=quoteOffset)

    def AdjustTextSize(self):
        self.textCont.width = self.quoteWidth
        self.textCont.height = self.quoteHeightPhrase + self.quoteHeightAttribution
        self.textCont.top = self.upperHeight + self.quoteTop
        self.textWrapper.width = self.quoteWidth
        self.textWrapper.height = self.quoteHeightPhrase + self.quoteHeightAttribution
        self.empireQuotePhrase.width = self.quoteWidth
        self.empireQuotePhrase.height = self.quoteHeightPhrase
        self.empireQuotePhrase.fontsize = self.quoteFontsize
        self.empireQuoteAttribution.width = self.quoteWidth
        self.empireQuoteAttribution.height = self.quoteHeightAttribution
        self.empireQuoteAttribution.fontsize = self.quoteFontsize

    def AdjustLogoSize(self):
        if self.raceSprite:
            self.raceSprite.width = self.raceIconSize
            self.raceSprite.height = self.raceIconSize
            self.raceSprite.top = self.raceIconsTop
        if self.raceSpriteBg:
            spriteSize = self.raceIconSizeHover if self.isHovered else self.raceIconSize
            self.raceSpriteBg.width = spriteSize
            self.raceSpriteBg.height = spriteSize
            self.raceSpriteBg.top = self.raceIconBgTop + self.raceIconsTop

    def AdjustFlareSize(self):
        bannerWidth = ccScalingUtils.GetBannerWidth()
        self.flareContainer.width = self.flareWidth
        self.flareContainer.height = self.flareHeight
        self.flareContainer.top = self.upperHeight - self.flareHeight / 2
        self.flareContainer.left = -(self.flareWidth - bannerWidth) / 2
        self.flareWrapper.width = self.flareWidth
        self.flareWrapper.height = self.flareHeight

    def AdjustCurvedGradientSize(self):
        bannerWidth = ccScalingUtils.GetBannerWidth()
        self.curvedGradientContainer.width = bannerWidth
        self.curvedGradientContainer.height = self.upperHeight
        self.curvedGradient.width = bannerWidth
        self.curvedGradient.height = self.upperHeight

    def AdjustEmpireQuoteBackgroundSize(self):
        bannerWidth = ccScalingUtils.GetBannerWidth()
        scaleFactor = ccScalingUtils.GetScaleFactor()
        bottomMin = EMPIRE_QUOTE_BOTTOM_MIN * scaleFactor
        height = max(self.lowerHeight, self.quoteTop + self.quoteHeightPhrase + self.quoteHeightAttribution + bottomMin)
        self.empireQuoteBackgroundContainer.width = bannerWidth
        self.empireQuoteBackgroundContainer.height = height
        self.empireQuoteBackgroundContainer.top = self.upperHeight
        lineWidth = bannerWidth
        lineDecorationWidth = LINE_DECO_WIDTH_MIN_RES * scaleFactor
        self.lineDecoration.ResizeContents(lineWidth, lineDecorationWidth)
        self.lineDecorationCurvedGradientContainer.width = LINE_CURVED_GRADIENT_WIDTH * scaleFactor
        self.lineDecorationCurvedGradientContainer.height = LINE_CURVED_GRADIENT_HEIGHT * scaleFactor
        self.lineDecorationCurvedGradient.width = LINE_CURVED_GRADIENT_WIDTH * scaleFactor
        self.lineDecorationCurvedGradient.height = LINE_CURVED_GRADIENT_HEIGHT * scaleFactor

    def Resize(self):
        self.CalculateSizes()
        self.AdjustLogoSize()
        self.AdjustTextSize()
        self.AdjustFlareSize()
        self.AdjustCurvedGradientSize()
        self.AdjustEmpireQuoteBackgroundSize()


class EmpireBanner(Container):
    default_state = uiconst.UI_NORMAL
    default_left = 0
    default_top = 0
    default_width = ccScalingUtils.BANNER_WIDTH
    default_height = ccScalingUtils.BANNER_HEIGHT
    STATE_PICK = 1
    STATE_PARENT = 2
    RACIAL_MUSIC_ON_CLICK = {raceAmarr: 'ui_es_banner_mouse_down_amarr_play',
     raceCaldari: 'ui_es_banner_mouse_down_caldari_play',
     raceGallente: 'ui_es_banner_mouse_down_gallente_play',
     raceMinmatar: 'ui_es_banner_mouse_down_minmatar_play'}
    RACIAL_MUSIC_ON_HOVER = {raceAmarr: 'music_switch_race_amarr',
     raceCaldari: 'music_switch_race_caldari',
     raceGallente: 'music_switch_race_gallente',
     raceMinmatar: 'music_switch_race_minmatar'}
    SOUND_ON_HOVER = 'ui_es_banner_mouse_over_play'

    def ApplyAttributes(self, attributes):
        self.raceID = attributes.raceID
        self.isHovered = False
        Container.ApplyAttributes(self, attributes)
        self.audioSvc = sm.GetService('audio')
        self.bannerState = attributes.Get('bannerState', EmpireBanner.STATE_PICK)
        self.isDisabled = attributes.Get('isDisabled', False)
        self.contents = None
        self.headerText = ''
        self.animationEnder = attributes.Get('animationEnder', None)
        self.bannerEnterer = attributes.Get('bannerEnterer', None)
        self.bannerExiter = attributes.Get('bannerExiter', None)
        self.bannerClicker = attributes.Get('bannerClicker', None)
        self.AddPanelCaps()
        self.AddTopBlackGradient()
        if self.bannerState == EmpireBanner.STATE_PICK:
            self.contents = BannerContents(parent=self, align=uiconst.TOALL, raceID=attributes.raceID)
        else:
            self.Expand()
        if self.isDisabled:
            self.Disable()
            WarningContainer(parent=self.contents, align=uiconst.CENTER, color=eveColor.WARNING_ORANGE, text=GetByLabel('UI/CharacterCreation/FactionDisabled'), width=250)
            self.contents.DesaturateRaceIcon()

    def ResizeContents(self, width, height):
        if self.contents and not self.contents.destroyed:
            self.contents.Resize()

    def OnClick(self, *args):
        if self.isDisabled:
            return
        if self.bannerClicker and self.bannerState == EmpireBanner.STATE_PICK:
            self.bannerClicker(self.raceID)
        if self.contents is not None and hasattr(self.contents, 'OnClick'):
            self.contents.OnClick(*args)
        sound = self.RACIAL_MUSIC_ON_CLICK[self.raceID]
        self.audioSvc.SendUIEvent(sound)

    def OnDblClick(self, *args):
        activeStep = uicore.layer.charactercreation.controller.stepID
        selectedRace = uicore.layer.charactercreation.controller.raceID
        if activeStep == ccConst.TECHNOLOGYSTEP and self.raceID == selectedRace:
            uicore.layer.charactercreation.controller.Approve()

    def OnMouseEnter(self, *args):
        if self.isDisabled:
            return
        Container.OnMouseEnter(self, args)
        if self.bannerEnterer:
            self.bannerEnterer(self.raceID)

    def OnMouseExit(self, *args):
        if self.isDisabled:
            return
        Container.OnMouseExit(self, args)
        if self.bannerExiter:
            self.bannerExiter()

    def PlaySoundsOnEntered(self):
        self.audioSvc.SendUIEvent(self.SOUND_ON_HOVER)
        self.audioSvc.SendUIEvent(self.RACIAL_MUSIC_ON_HOVER[self.raceID])

    def AdjustTextSize(self):
        self.contents.AdjustTextSize()

    def AnimateEntered(self):
        if self.bannerState != EmpireBanner.STATE_PICK:
            return
        self.isHovered = True
        self.AdjustTextSize()
        self.contents.AnimateEntered()
        quoteTime = EMPIRE_QUOTE_FADE_IN_DELAY + EMPIRE_QUOTE_FADE_IN_DURATION
        textTime = EMPIRE_QUOTE_FADE_IN_DELAY + EMPIRE_QUOTE_TEXT_FADE_IN_DELAY + EMPIRE_QUOTE_TEXT_FADE_IN_DURATION
        timeToEnd = max(quoteTime, textTime)
        call_after_wallclocktime_delay(self.NotifyOfAnimationEnd, timeToEnd)

    def AnimateExited(self):
        if self.bannerState != EmpireBanner.STATE_PICK:
            return
        self.isHovered = False
        self.contents.AnimateExited()
        textTime = EMPIRE_QUOTE_TEXT_FADE_OUT_DURATION
        quoteTime = EMPIRE_QUOTE_FADE_OUT_DELAY + EMPIRE_QUOTE_FADE_OUT_DURATION
        timeToEnd = max(quoteTime, textTime)
        call_after_wallclocktime_delay(self.NotifyOfAnimationEnd, timeToEnd)

    def NotifyOfAnimationEnd(self):
        if self.animationEnder:
            self.animationEnder(self.raceID)

    def ConstructHeader(self, text = None):
        if text is not None:
            self.headerText = text
        if hasattr(self, 'header'):
            self.header.Close()
        headerHeight = ccScalingUtils.GetBannerHeaderHeight()
        self.header = BannerHeader(name='bannerHeader', parent=self, align=uiconst.TOTOP, width=self.width, height=headerHeight, text=self.headerText)
        self.header.SetOrder(0)

    def Resize(self, width, height):
        self.width = width
        self.height = height
        self.ConstructHeader()
        self.ResizePanelCaps()
        self.ResizeTopBlackGradient()

    def ResizePanelCaps(self):
        width = ccScalingUtils.GetMainPanelWidth()
        height = ccScalingUtils.GetBannerHeaderHeight()
        self.topPanelCap.width = width
        self.topPanelCap.height = height
        self.topPanelCap.top = -height
        self.bottomPanelCap.width = width
        self.bottomPanelCap.height = height

    def ResizeTopBlackGradient(self):
        width = ccScalingUtils.GetMainPanelWidth()
        height = ccScalingUtils.GetBannerHeaderHeight()
        self.topBlackGradient.width = width
        self.topBlackGradient.height = height
        self.topBlackGradient.top = -height

    def Expand(self):
        self.isHovered = False
        self.state = uiconst.UI_DISABLED
        if self.contents is not None:
            self.contents.Close()
        self.bannerState = EmpireBanner.STATE_PARENT
        height = ccScalingUtils.GetMainPanelHeight()
        width = ccScalingUtils.GetMainPanelWidth()
        self.Resize(width, height)
        self.state = uiconst.UI_DISABLED
        self.ShowBottomPanelCap()

    def AddPanelCaps(self):
        width = ccScalingUtils.GetMainPanelWidth()
        height = ccScalingUtils.GetBannerHeaderHeight()
        texturePath = CURVED_GRADIENT_TEXTURE_BY_RACE[self.raceID] if self.raceID else CURVED_GRADIENT_TEXTURE_BASE
        self.topPanelCap = Sprite(name='topPanelCap', parent=self, align=uiconst.TOTOP_NOPUSH, texturePath=texturePath, state=uiconst.UI_DISABLED, width=width, height=height, top=-height, rotation=math.pi, opacity=0.0)
        self.bottomPanelCap = Sprite(name='bottomPanelCap', parent=self, align=uiconst.TOBOTTOM_NOPUSH, texturePath=texturePath, state=uiconst.UI_DISABLED, width=width, height=height, rotation=0.0, opacity=0.0)

    def AddTopBlackGradient(self):
        width = ccScalingUtils.GetMainPanelWidth()
        height = ccScalingUtils.GetBannerHeaderHeight()
        self.topBlackGradient = GradientSprite(name='topBlackGradient', parent=self, align=uiconst.TOTOP_NOPUSH, width=width, height=height, top=-height, rgbData=[(0, (0.0, 0.0, 0.0))], alphaData=[(0, 0.0),
         (0.4, 0.5),
         (0.6, 0.5),
         (1.0, 0.0)], opacity=0.0)

    def ShowTopPanelCap(self):
        self.topPanelCap.opacity = CURVED_GRADIENT_OPACITY

    def ShowBottomPanelCap(self):
        self.bottomPanelCap.opacity = CURVED_GRADIENT_OPACITY

    def HideTopPanelCap(self):
        self.topPanelCap.opacity = 0.0

    def HideBottomPanelCap(self):
        self.bottomPanelCap.opacity = 0.0

    def ShowTopBlackGradient(self):
        self.topBlackGradient.opacity = HEADER_BACKGROUND_OPACITY

    def HideTopBlackGradient(self):
        self.topBlackGradient.opacity = 0.0


class BannerHeader(Container):
    default_align = uiconst.CENTERTOP

    def ApplyAttributes(self, attributes):
        self.headerSpotlight = None
        Container.ApplyAttributes(self, attributes)
        text = attributes.text
        self._AddText(text)

    def _AddText(self, text):
        scaleFactor = ccScalingUtils.GetScaleFactor()
        self.headerTextBox = Container(name='headerTextBox', parent=self, height=self.height, align=uiconst.TOTOP_NOPUSH)
        self.header = CCLabel(text=text, name='headerLabel', parent=self.headerTextBox, align=uiconst.CENTER, uppercase=1, color=(0.9, 0.9, 0.9, 0.8), fontsize=BANNER_TEXT_FONTSIZE * scaleFactor, bold=True, letterspace=0)

    def ResizeContent(self):
        self.headerTextBox.height = self.height
        scaleFactor = ccScalingUtils.GetScaleFactor()
        self.header.fontsize = BANNER_TEXT_FONTSIZE * scaleFactor


class MinimalEmpireBanner(Container):
    frameDecorationWidthFactor = 1.35
    frameDecorationHeightFactor = 0.23
    frameDecorationTopFactor = 0.685
    frameDecoration = 'res:/UI/Texture/classes/EmpireSelection/factionBannerTop.png'

    def ApplyAttributes(self, attributes):
        logo = attributes.logo
        logoSize = attributes.logoSize
        iconView = attributes.Get('iconView', None)
        iconText = attributes.Get('iconText', '')
        iconTextFontsize = attributes.Get('iconTextFontsize', None)
        iconColor = attributes.Get('iconColor', None)
        Container.ApplyAttributes(self, attributes)
        self.AddLogo(logo, logoSize)
        self.AddBanner(iconView, iconText, iconTextFontsize, iconColor)

    def AddLogo(self, logo, logoSize):
        Sprite(name='empireLogo', parent=self, align=uiconst.CENTERTOP, texturePath=logo, width=logoSize, height=logoSize, top=self.height * self.frameDecorationHeightFactor * self.frameDecorationTopFactor / 2)

    def AddBanner(self, iconView, iconText, iconTextFontsize, iconColor):
        if not iconView:
            return
        decorationWidth = self.width * self.frameDecorationWidthFactor
        decorationHeight = self.height * self.frameDecorationHeightFactor
        frameDecorationTitle = CCLabel(parent=self, name='frameDecorationTitle', align=uiconst.TOLEFT_NOPUSH, text=iconText, bold=True, fontsize=iconTextFontsize, letterspace=0)
        frameDecorationTitleWidth = frameDecorationTitle.width
        frameDecorationTitleHeight = GetTextHeight(strng=iconText, width=frameDecorationTitleWidth, fontsize=iconTextFontsize, hspace=0)
        frameDecorationTitle.top = -frameDecorationTitleHeight / 2 - EXTRA_FRAME_TITLE_PADDING
        frameDecorationTitle.left = (self.width - frameDecorationTitleWidth) / 2
        Frame(parent=self, name='iconView', align=uiconst.TOALL, texturePath=iconView, color=iconColor)
        Frame(parent=self, name='frameDecoration', align=uiconst.ANCH_CENTERTOP, texturePath=self.frameDecoration, width=decorationWidth, height=decorationHeight, top=-decorationHeight * self.frameDecorationTopFactor, left=-(decorationWidth - self.width) / 2)
