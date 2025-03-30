#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\technologyViewUtils.py
from carbon.client.script.environment.AudioUtil import PlaySound
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from charactercreator.client.empireSelectionData import GetEmpireColor, GetEmpireButtonLogo, GetEmpireLogo
from charactercreator.client.scalingUtils import GetScaleFactor
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelSmall
from eve.client.script.ui.login.charcreation import ccUtil
from eve.client.script.ui.login.charcreation.charCreationButtons import EmpireTab, EmpireTabAnimationType
from eve.client.script.ui.login.charcreation.charCreationButtons import EMPIRE_TAB_ICON_SIZE, EMPIRE_ICON_PAD
from eve.client.script.ui.login.charcreation.charCreationButtons import GetEmpireTabSizeLarge
from eve.common.lib import appConst
from eve.common.lib.appConst import raceAmarr, raceGallente, raceCaldari, raceMinmatar
import math
from uthread2 import start_tasklet
from characterdata.races import CHARACTER_CREATION_RACE_IDS
TECH_EXAMPLE_BUTTON_TEXT_HEIGHT = 30
ARROW_TEXTURE = 'res:/UI/Texture/Classes/EmpireSelection/navArrow_Up.png'
ARROW_TEXTURE_OVER = 'res:/UI/Texture/Classes/EmpireSelection/navArrow_Over.png'
ARROW_TEXTURE_DOWN = 'res:/UI/Texture/Classes/EmpireSelection/navArrow_Down.png'
ARROW_BUTTON_UP_TEXTURE = 'res:/UI/Texture/Shared/sideButton_Up.png'
ARROW_BUTTON_DOWN_TEXTURE = 'res:/UI/Texture/Shared/sideButton_Down.png'
ARROW_BUTTON_OVER_TEXTURE = 'res:/UI/Texture/Shared/sideButton_Over.png'
LINE_DECORATION = 'res:/UI/Texture/classes/EmpireSelection/lineDeco.png'
LINE_DECORATION_WIDTH = 58
LINE_DECORATION_HEIGHT = 3
LINE_DECORATION_COLOR = (1.0, 1.0, 1.0)
LINE_DECORATION_OPACITY = 0.5
LINE_DECORATION_CORNERSIZE = 1
LINE_DECORATION_GRADIENT_WIDTH = 370
LINE_DECORATION_GRADIENT_HEIGHT = 1
LINE_DECORATION_GRADIENT_OPACITY = 0.25
ICON_FRAME_CORNER_SIZE = 6
ICON_BG_COLOR = (0.4, 0.4, 0.4, 1.0)
ICON_FRAME_COLOR = (1.0, 1.0, 1.0, 1.0)
ICON_PADDING = (10, 10, 10, 10)
TECH_NAV_BUTTON_SIZE_LARGE = 44
TECH_NAV_BUTTON_SIZE_SMALL = 32
TECH_NAV_BUTTON_FONTSIZE = 9
TECH_NAV_ARROW_SIZE = 24.25
TECH_NAV_ARROW_ICON_SIZE = 24.25
TECH_NAV_ARROW_SPACE_SIZE = 17
EMPIRE_TABS_ANIMATION_MSECS = 100
FORCE_TERMINATE_ANIMATION_SECS = 0.2

def GetTechNavButtonSizeLarge():
    return TECH_NAV_BUTTON_SIZE_LARGE * GetScaleFactor()


def GetTechNavButtonSizeSmall():
    return TECH_NAV_BUTTON_SIZE_SMALL * GetScaleFactor()


def GetTechNavButtonFontsize():
    return TECH_NAV_BUTTON_FONTSIZE * GetScaleFactor()


def GetTechNavArrowSize():
    return TECH_NAV_ARROW_SIZE * GetScaleFactor()


def GetTechNavArrowIconSize():
    return TECH_NAV_ARROW_ICON_SIZE * GetScaleFactor()


def GetTechNavArrowSpacingSize():
    return TECH_NAV_ARROW_SPACE_SIZE * GetScaleFactor()


def GetEmpireColorWithOpacity(raceID, opacity):
    r, g, b, a = GetEmpireColor(raceID)
    return (r,
     g,
     b,
     opacity)


class EmpireButton(ButtonIcon):
    default_mouseUpBGTexture = None
    default_mouseEnterBGTexture = None
    default_mouseDownBGTexture = None
    default_isBGFrameUsed = None
    default_frameOffset = 0
    default_frameCornerSize = 0

    def ApplyAttributes(self, attributes):
        raceID = attributes.Get('raceID', None)
        raceSetter = attributes.Get('raceSetter', None)
        ButtonIcon.ApplyAttributes(self, attributes)
        self.OnClick = lambda raceID = raceID: raceSetter(raceID=raceID)


class EmpireNavigation(Container):
    SELECTION_SOUND_BY_RACE = {raceAmarr: 'ui_es_button_mouse_down_amarr_play',
     raceCaldari: 'ui_es_button_mouse_down_caldari_play',
     raceGallente: 'ui_es_button_mouse_down_gallente_play',
     raceMinmatar: 'ui_es_button_mouse_down_minmatar_play'}
    HOVER_SOUND = 'ui_es_small_banner_mouse_over_play'

    def ApplyAttributes(self, attributes):
        self.raceSetter = attributes.Get('raceSetter', None)
        self.activeRace = attributes.Get('activeRace', None)
        self.audioSvc = sm.GetService('audio')
        Container.ApplyAttributes(self, attributes)
        self.tabs = []
        tabSizeLarge = GetEmpireTabSizeLarge()
        empireButtonsWrapper = Container(name='empireButtonsWrapper', parent=self, align=uiconst.CENTER, width=4 * tabSizeLarge, height=tabSizeLarge)
        for raceID in CHARACTER_CREATION_RACE_IDS:
            isActive = raceID == self.activeRace
            factionID = appConst.factionByRace[raceID]
            isDisabled = ccUtil.IsFactionSelectionDisabled(factionID)
            raceTab = EmpireTab(name='empireTab_%d' % raceID, parent=empireButtonsWrapper, align=uiconst.TOLEFT, width=tabSizeLarge, height=tabSizeLarge, raceID=raceID, raceSetter=self.OnTabRaceSelected, raceHoverer=self.OnTabRaceHovered, iconColor=GetEmpireColor(raceID), iconSize=EMPIRE_TAB_ICON_SIZE * GetScaleFactor(), texturePath=GetEmpireButtonLogo(raceID), empireLogoPath=GetEmpireLogo(raceID), isActive=isActive, isDisabled=isDisabled)
            isNotLastTab = len(self.tabs) < len(CHARACTER_CREATION_RACE_IDS)
            if isNotLastTab:
                raceTab.padRight = EMPIRE_ICON_PAD * GetScaleFactor()
            self.tabs.append(raceTab)

    def Close(self):
        super(EmpireNavigation, self).Close()

    def OnTabRaceSelected(self, raceID):
        self.NotifyTabsOfRaceChange(raceID)

    def OnTabRaceHovered(self, raceID):
        self.NotifyTabsOfRaceHover(raceID)

    def NotifyTabsOfRaceChange(self, raceID):
        animation = {}
        for tab in self.tabs:
            if tab.raceID == raceID:
                animation[tab.raceID] = EmpireTabAnimationType.ACTIVATE
            else:
                animation[tab.raceID] = EmpireTabAnimationType.DEACTIVATE

        self.ProcessAnimation(animation)

    def NotifyTabsOfRaceHover(self, raceID):
        animation = {}
        for tab in self.tabs:
            if tab.raceID == raceID:
                animation[tab.raceID] = EmpireTabAnimationType.HOVER
            else:
                animation[tab.raceID] = EmpireTabAnimationType.DEHOVER

        self.ProcessAnimation(animation)

    def ProcessAnimation(self, animation):
        for tab in self.tabs:
            raceID = tab.raceID
            if raceID in animation:
                animationType = animation[raceID]
                if animationType == EmpireTabAnimationType.ACTIVATE:
                    self.activeRace = raceID
                    tab.Activate()
                    start_tasklet(self.raceSetter, raceID)
                    self.PlaySelectSound(raceID)
                elif animationType == EmpireTabAnimationType.DEACTIVATE:
                    tab.Deactivate()
                elif animationType == EmpireTabAnimationType.HOVER:
                    if self.activeRace != raceID:
                        tab.Hover()
                        self.PlayHoverSound()
                elif animationType == EmpireTabAnimationType.DEHOVER:
                    if self.activeRace != raceID:
                        tab.Dehover()

    def PlaySelectSound(self, raceID):
        self.audioSvc.SendUIEvent(self.SELECTION_SOUND_BY_RACE[raceID])

    def PlayHoverSound(self):
        self.audioSvc.SendUIEvent(self.HOVER_SOUND)


class RacialArrowButton(ButtonIcon):
    default_iconSize = TECH_NAV_ARROW_SIZE
    default_isHoverBGUsed = False
    default_texturePath = ARROW_TEXTURE
    default_iconColor = (1.0, 1.0, 1.0, 1.0)

    def ApplyAttributes(self, attributes):
        ButtonIcon.ApplyAttributes(self, attributes)


class ArrowTechButton(RacialArrowButton):

    def ApplyAttributes(self, attributes):
        super(ArrowTechButton, self).ApplyAttributes(attributes)
        self.order = attributes.Get('order', None)
        self.techSetter = attributes.Get('techSetter', None)
        self.func = lambda order = self.order: self.techSetter(techOrder=order)


class ArrowBackButton(RacialArrowButton):

    def ApplyAttributes(self, attributes):
        super(ArrowBackButton, self).ApplyAttributes(attributes)
        self.func = uicore.layer.charactercreation.controller.Back


class TechExampleButton(Container):
    OPACITY_ACTIVE = 0.9
    OPACITY_BG_ACTIVE = 0.0
    DEFAULT_OPACITY = 0.7
    OPACITY_ON_ENTER = 1.0
    DEFAULT_BG_OPACITY = 0.0
    OPACITY_BG_ON_ENTER = 0.5
    DEFAULT_IMAGE_OPACITY = 0.3
    IMAGE_OPACITY_ACTIVE = 0.9
    GRADIENT_COLOR = (0.5, 0.5, 0.5)
    GRADIENT_OPACITY = 0.3

    def ApplyAttributes(self, attributes):
        self.order = attributes.Get('order', None)
        self.techExampleSetter = attributes.Get('techExampleSetter', None)
        raceID = attributes.Get('raceID', None)
        techExample = attributes.Get('techExample', None)
        iconSize = attributes.Get('iconSize', 0)
        padIconToText = attributes.Get('padIconToText', 0)
        attributes.bgColor = GetEmpireColorWithOpacity(raceID=raceID, opacity=self.DEFAULT_BG_OPACITY)
        attributes.opacity = self.DEFAULT_OPACITY
        Container.ApplyAttributes(self, attributes)
        icon = techExample.GetIcon(raceID)
        self._AddFrame()
        self._AddGradient()
        self._AddIcon(icon, iconSize)
        title = techExample.GetTitle(raceID)
        subtitle = techExample.GetSubtitle(raceID)
        padLeft = iconSize + padIconToText
        self._AddText(title, subtitle, padLeft)
        self.active = False

    def _AddFrame(self):
        iconNo = 7
        cornerSize = -2
        offset = 0
        self.frame = Frame(parent=self, color=(1.0, 1.0, 1.0, 1.0), frameConst=('res://UI/Texture/classes/CharacterSelection/EmpireSelection2017/leftCornerFrame.png',
         iconNo,
         cornerSize,
         offset), opacity=0.0)

    def _AddGradient(self):
        self.gradient = GradientSprite(name='techExampleButtonGradient', bgParent=self, rgbData=((0, self.GRADIENT_COLOR),), alphaData=[(0.0, 1.0), (1.0, 0.0)], opacity=0.0)

    def _AddIcon(self, icon, iconSize):
        self.iconContainer = Container(name='techExampleButtonIconContainer', parent=self, align=uiconst.TOLEFT, width=iconSize, height=iconSize, bgColor=ICON_BG_COLOR, padding=ICON_PADDING)
        Frame(parent=self.iconContainer, color=ICON_FRAME_COLOR, cornerSize=ICON_FRAME_CORNER_SIZE)
        self.icon = Sprite(name='techExampleButtonIcon', parent=self.iconContainer, align=uiconst.TOLEFT, width=iconSize, height=iconSize, texturePath=icon)

    def _AddText(self, title, subtitle, padLeft):
        textContainer = Container(name='techExampleButtonTextContainer', parent=self, align=uiconst.CENTERLEFT, width=self.width - padLeft, height=TECH_EXAMPLE_BUTTON_TEXT_HEIGHT, left=padLeft + ICON_FRAME_CORNER_SIZE)
        self.titleLabel = EveLabelMediumBold(name='techExampleButtonTitle', parent=textContainer, align=uiconst.TOPLEFT, text=title)
        self.subtitleLabel = EveLabelSmall(name='techExampleButtonSubtitle', parent=textContainer, align=uiconst.BOTTOMLEFT, text=subtitle.upper())

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self.icon.OnMouseEnter()
        uicore.animations.FadeTo(self, self.opacity, self.OPACITY_ON_ENTER, duration=0.15)
        uicore.animations.FadeTo(self.bgFill, self.bgFill.opacity, self.OPACITY_BG_ON_ENTER, duration=0.15)

    def OnMouseExit(self, *args):
        self.icon.OnMouseExit()
        opacity = self.OPACITY_ACTIVE if self.active else self.DEFAULT_OPACITY
        opacityBg = self.OPACITY_BG_ACTIVE if self.active else self.DEFAULT_BG_OPACITY
        uicore.animations.FadeTo(self, self.opacity, opacity, duration=0.3, callback=self.UpdateOpacity)
        uicore.animations.FadeTo(self.bgFill, self.bgFill.opacity, opacityBg, duration=0.3, callback=self.UpdateBgOpacity)

    def OnClick(self):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        self.techExampleSetter(order=self.order)

    def SetActive(self):
        self.active = True
        self.UpdateOpacity()
        self.UpdateBgOpacity()
        self.subtitleLabel.Show()
        self.titleLabel.align = uiconst.TOPLEFT

    def SetInactive(self):
        self.active = False
        self.UpdateOpacity()
        self.UpdateBgOpacity()
        self.subtitleLabel.Hide()
        self.titleLabel.align = uiconst.CENTERLEFT

    def UpdateOpacity(self):
        if self.active:
            self.opacity = self.OPACITY_ACTIVE
            self.iconContainer.opacity = self.IMAGE_OPACITY_ACTIVE
            self.frame.opacity = 1.0
            self.gradient.opacity = self.GRADIENT_OPACITY
        else:
            self.opacity = self.DEFAULT_OPACITY
            self.iconContainer.opacity = self.DEFAULT_IMAGE_OPACITY
            self.frame.opacity = 0.0
            self.gradient.opacity = 0.0

    def UpdateBgOpacity(self):
        self.bgFill.opacity = self.OPACITY_BG_ACTIVE if self.active else self.DEFAULT_BG_OPACITY


class LineDecoration(Container):
    default_lineWidth = LINE_DECORATION_GRADIENT_WIDTH
    default_lineDecorationWidth = LINE_DECORATION_WIDTH
    default_lineColor = LINE_DECORATION_COLOR

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        invert = attributes.Get('invert', False)
        lineWidth = attributes.Get('lineWidth', self.default_lineWidth)
        lineDecorationWidth = attributes.Get('lineDecorationWidth', self.default_lineDecorationWidth)
        lineColor = attributes.Get('lineColor', self.default_lineColor) or self.default_lineColor
        self.lineGradientContainer = Container(name='lineGradientContainer', align=uiconst.TOTOP, parent=self, width=lineWidth, height=LINE_DECORATION_GRADIENT_HEIGHT, padTop=LINE_DECORATION_HEIGHT if invert else 0)
        self.line = GradientSprite(name='line', width=lineWidth, height=LINE_DECORATION_GRADIENT_HEIGHT, align=uiconst.CENTER, parent=self.lineGradientContainer, rgbData=((0.0, lineColor),), alphaData=((0.0, 0.0), (0.5, 0.5), (1.0, 0.0)), rotation=0, opacity=LINE_DECORATION_GRADIENT_OPACITY)
        self.deco = Frame(name='lineDeco', align=uiconst.CENTERTOP, parent=self, width=lineDecorationWidth, height=LINE_DECORATION_HEIGHT if invert else LINE_DECORATION_HEIGHT + LINE_DECORATION_GRADIENT_HEIGHT, texturePath=LINE_DECORATION, cornerSize=LINE_DECORATION_CORNERSIZE, opacity=LINE_DECORATION_OPACITY, padTop=0 if invert else LINE_DECORATION_GRADIENT_HEIGHT, rotation=math.pi if invert else 0, color=lineColor)

    def ResizeContents(self, lineWidth, lineDecorationWidth):
        self.lineGradientContainer.width = lineWidth
        self.line.width = lineWidth
        self.deco.width = lineDecorationWidth


class VerticalLineDecoration(Container):
    default_lineHeight = LINE_DECORATION_GRADIENT_WIDTH
    default_lineDecorationHeight = LINE_DECORATION_WIDTH
    default_lineColor = LINE_DECORATION_COLOR

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        invert = attributes.Get('invert', False)
        lineHeight = attributes.Get('lineHeight', self.default_lineHeight)
        lineDecorationHeight = attributes.Get('lineDecorationHeight', self.default_lineDecorationHeight)
        lineColor = attributes.Get('lineColor', self.default_lineColor) or self.default_lineColor
        lineGradientContainer = Container(name='lineGradientContainer', align=uiconst.TOLEFT, parent=self, width=LINE_DECORATION_GRADIENT_HEIGHT, height=lineDecorationHeight, padLeft=LINE_DECORATION_HEIGHT if invert else 0)
        GradientSprite(name='line', width=LINE_DECORATION_GRADIENT_HEIGHT, height=lineHeight, align=uiconst.CENTER, parent=lineGradientContainer, rgbData=((0.0, lineColor),), alphaData=((0.0, 0.0), (0.5, 0.5), (1.0, 0.0)), rotation=math.pi / 2, opacity=LINE_DECORATION_GRADIENT_OPACITY)
        Frame(name='lineDeco', align=uiconst.CENTERLEFT, parent=self, width=LINE_DECORATION_HEIGHT if invert else LINE_DECORATION_HEIGHT + LINE_DECORATION_GRADIENT_HEIGHT, height=lineDecorationHeight, texturePath=LINE_DECORATION, cornerSize=0, opacity=LINE_DECORATION_OPACITY, padLeft=0 if invert else LINE_DECORATION_GRADIENT_HEIGHT, rotation=3 * math.pi / 2 if invert else math.pi / 2, color=lineColor)


class TechNavigationButton(Container):
    default_state = uiconst.UI_NORMAL
    ACTIVATION_DURATION = 1.0
    DEACTIVATION_DURATION = 1.0
    INACTIVE_OPACITY = 0.25
    MOUSEOVER_OPACITY = 0.5
    ACTIVE_OPACITY = 1.0
    MOUSEOVER_SOUND = 'ui_icc_button_mouse_over_play'
    SELECT_SOUND = 'ui_icc_button_select_play'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isActive = attributes.isActive
        self.techSetter = attributes.techSetter
        self.raceID = attributes.raceID
        self.order = attributes.order
        iconRotation = attributes.Get('rotation', 0.0)
        iconTexture = attributes.iconTexture
        iconSize = attributes.iconSize
        iconOpacity = self.ACTIVE_OPACITY if self.isActive else self.INACTIVE_OPACITY
        self.icon = Sprite(name='techNavigationButtonIcon', parent=self, align=uiconst.CENTER, texturePath=iconTexture, width=iconSize, height=iconSize, opacity=iconOpacity, state=uiconst.UI_DISABLED, rotation=iconRotation)

    def OnMouseEnter(self, *args):
        if not self.isActive:
            self.icon.SetAlpha(self.MOUSEOVER_OPACITY)
        if self.MOUSEOVER_SOUND:
            sm.StartService('audio').SendUIEvent(unicode(self.MOUSEOVER_SOUND))

    def OnMouseExit(self, *args):
        if not self.isActive:
            self.icon.SetAlpha(self.INACTIVE_OPACITY)

    def OnMouseDown(self, *args):
        self.icon.SetAlpha(self.ACTIVE_OPACITY)
        if self.SELECT_SOUND:
            sm.StartService('audio').SendUIEvent(unicode(self.SELECT_SOUND))

    def OnClick(self):
        self.techSetter(self.order)
