#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\empireui\empireThemedButtons.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.primitives.transform import Transform
from carbonui.uicore import uicore
from charactercreator.client.empireSelectionData import GetEmpireButtonLogo
from charactercreator.client.scalingUtils import GetScaleFactor
from collections import defaultdict
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.login.charcreation.label import CCLabel
from eve.client.script.ui.login.charcreation.technologyViewUtils import LineDecoration
from eve.common.lib.appConst import raceAmarr, raceCaldari, raceGallente, raceMinmatar
from trinity import TR2_SBM_BLEND, TR2_SFX_COPY

class EmpireThemedButtonState:
    DISABLED = 0
    DARKENED = 1
    NORMAL = 2


class MouseState:
    UP = 0
    OVER = 1
    DOWN = 2


BG_TEXTURE_OUTLINE = 'res:/UI/Texture/Classes/EmpireSelection/largeButton_Outline.png'
BG_TEXTURE_UP = 'res:/UI/Texture/Classes/EmpireSelection/largeButton_Up.png'
BG_TEXTURE_OVER = 'res:/UI/Texture/Classes/EmpireSelection/largeButton_Over.png'
BG_TEXTURE_DOWN = 'res:/UI/Texture/Classes/EmpireSelection/largeButton_Down.png'
BG_TEXTURE_DISABLED = 'res:/UI/Texture/Classes/EmpireSelection/largeButton_Disabled.png'
SIDE_DECO_TEXTURE_BY_RACE = {raceAmarr: 'res:/UI/Texture/Classes/EmpireSelection/sideDecoAmarr.png',
 raceCaldari: 'res:/UI/Texture/Classes/EmpireSelection/sideDecoCaldari.png',
 raceGallente: 'res:/UI/Texture/Classes/EmpireSelection/sideDecoGallente.png',
 raceMinmatar: 'res:/UI/Texture/Classes/EmpireSelection/sideDecoMinmatar.png'}
CURVED_GRADIENT_TEXTURE_BY_RACE = {raceAmarr: 'res:/UI/Texture/Classes/EmpireSelection/curvedGradientAmarr.png',
 raceCaldari: 'res:/UI/Texture/Classes/EmpireSelection/curvedGradientCaldari.png',
 raceGallente: 'res:/UI/Texture/Classes/EmpireSelection/curvedGradientGallente.png',
 raceMinmatar: 'res:/UI/Texture/Classes/EmpireSelection/curvedGradientMinmatar.png'}
HIGHLIGHT_TINT_BY_RACE = {raceAmarr: (1.0, 0.89, 0.7),
 raceCaldari: (0.77, 0.92, 1.0),
 raceGallente: (0.7, 1.0, 1.0),
 raceMinmatar: (1.0, 0.8, 0.7)}
BUTTON_TINT_BY_STATE_AND_RACE = {EmpireThemedButtonState.NORMAL: {raceAmarr: (0.82, 0.7, 0.51),
                                  raceCaldari: (0.46, 0.68, 0.8),
                                  raceGallente: (0.42, 0.8, 0.8),
                                  raceMinmatar: (0.8, 0.44, 0.41)},
 EmpireThemedButtonState.DARKENED: {raceAmarr: (0.61, 0.52, 0.38),
                                    raceCaldari: (0.29, 0.43, 0.5),
                                    raceGallente: (0.21, 0.4, 0.4),
                                    raceMinmatar: (0.4, 0.22, 0.2)},
 EmpireThemedButtonState.DISABLED: {raceAmarr: (0.45, 0.45, 0.45),
                                    raceCaldari: (0.45, 0.45, 0.45),
                                    raceGallente: (0.45, 0.45, 0.45),
                                    raceMinmatar: (0.45, 0.45, 0.45)}}
TEXT_TINT_BY_STATE_AND_RACE = {EmpireThemedButtonState.NORMAL: {raceAmarr: (1.0, 0.94, 0.84),
                                  raceCaldari: (0.85, 0.95, 1.0),
                                  raceGallente: (0.75, 1.0, 1.0),
                                  raceMinmatar: (1.0, 0.85, 0.8)},
 EmpireThemedButtonState.DARKENED: {raceAmarr: (0.7, 0.61, 0.47),
                                    raceCaldari: (0.42, 0.6, 0.7),
                                    raceGallente: (0.42, 0.7, 0.7),
                                    raceMinmatar: (0.7, 0.48, 0.42)},
 EmpireThemedButtonState.DISABLED: {raceAmarr: (0.55, 0.55, 0.55),
                                    raceCaldari: (0.55, 0.55, 0.55),
                                    raceGallente: (0.55, 0.55, 0.55),
                                    raceMinmatar: (0.55, 0.55, 0.55)}}
BUTTON_GRADIENT_BY_STATES = {EmpireThemedButtonState.DISABLED: defaultdict(lambda : BG_TEXTURE_DISABLED),
 EmpireThemedButtonState.DARKENED: defaultdict(lambda : BG_TEXTURE_UP),
 EmpireThemedButtonState.NORMAL: {MouseState.UP: BG_TEXTURE_UP,
                                  MouseState.OVER: BG_TEXTURE_OVER,
                                  MouseState.DOWN: BG_TEXTURE_DOWN}}
IS_TINTED_BY_STATE = {EmpireThemedButtonState.DISABLED: False,
 EmpireThemedButtonState.DARKENED: True,
 EmpireThemedButtonState.NORMAL: True}
IS_DECORATED_BY_STATE = {EmpireThemedButtonState.DISABLED: False,
 EmpireThemedButtonState.DARKENED: False,
 EmpireThemedButtonState.NORMAL: True}
DOES_REACT_TO_MOUSE_BY_STATE = {EmpireThemedButtonState.DISABLED: False,
 EmpireThemedButtonState.DARKENED: True,
 EmpireThemedButtonState.NORMAL: True}
BG_TEXTURE_OUTLINE_OPACITY_BY_MOUSE_STATE = {MouseState.UP: 0.5,
 MouseState.OVER: 0.75,
 MouseState.DOWN: 1.0}
BUTTON_TEXT_OPACITY_BY_MOUSE_STATE = {MouseState.UP: 0.75,
 MouseState.OVER: 1.0,
 MouseState.DOWN: 1.0}
SIDE_DECO_OPACITY_BY_STATES = {EmpireThemedButtonState.DISABLED: defaultdict(lambda : 0.15),
 EmpireThemedButtonState.DARKENED: {MouseState.UP: 0.25,
                                    MouseState.OVER: 0.5,
                                    MouseState.DOWN: 0.5},
 EmpireThemedButtonState.NORMAL: {MouseState.UP: 0.25,
                                  MouseState.OVER: 0.5,
                                  MouseState.DOWN: 0.5}}
CURVED_GRADIENT_OPACITY_BY_STATE = {EmpireThemedButtonState.DISABLED: 0.0,
 EmpireThemedButtonState.DARKENED: 0.5,
 EmpireThemedButtonState.NORMAL: 0.5}
MOUSE_STATE_CHANGE_ANIMATION_DURATION = 0.2
DECORATION_ANIMATION_DURATION_FADE_IN = 0.5
DECORATION_ANIMATION_DURATION_FADE_OUT = 0.5
BUTTON_TEXT_FONTSIZE_MIN_RES = 14
LINE_WIDTH_MIN_RES = 166
LINE_HEIGHT = 4
LINE_DECO_WIDTH_MIN_RES = 41
SIDE_DECO_WIDTH_MIN_RES = 77
SIDE_DECO_HEIGHT_MIN_RES = 46
CURVED_GRADIENT_WIDTH_MIN_RES = 135
CURVED_GRADIENT_HEIGHT_MIN_RES = 17
LOGO_WIDTH_MIN_RES = 82
LOGO_HEIGHT_MIN_RES = 82
LOGO_TOP_PADDING = 18
BURST_WIDTH_MIN_RES = 300
BURST_HEIGHT_MIN_RES = 169
SEAL_WIDTH_MIN_RES = 166
SEAL_HEIGHT_MIN_RES = 78
SEAL_TEXTURE_BY_RACE = {raceAmarr: 'res:/UI/Texture/Classes/EmpireSelection/logoButtonSealAmarr.png',
 raceCaldari: 'res:/UI/Texture/Classes/EmpireSelection/logoButtonSealCaldari.png',
 raceGallente: 'res:/UI/Texture/Classes/EmpireSelection/logoButtonSealGallente.png',
 raceMinmatar: 'res:/UI/Texture/Classes/EmpireSelection/logoButtonSealMinmatar.png'}
FLARE_VIDEO_BY_RACE = {raceAmarr: 'res:/UI/Texture/Classes/EmpireSelection/Flare_Amarr.webm',
 raceCaldari: 'res:/UI/Texture/Classes/EmpireSelection/Flare_Caldari.webm',
 raceGallente: 'res:/UI/Texture/Classes/EmpireSelection/Flare_Gallente.webm',
 raceMinmatar: 'res:/UI/Texture/Classes/EmpireSelection/Flare_Minmatar.webm'}

class EmpireThemedButton(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.buttonOutline = None
        self.buttonGradient = None
        self.buttonLabel = None
        self.lineDecoration = None
        self.curvedGradient = None
        self.sideDecorationLeft = None
        self.sideDecorationRight = None
        self.mouseState = MouseState.UP
        self.buttonState = attributes.Get('buttonState', None)
        self.raceID = attributes.Get('raceID', None)
        self.label = attributes.Get('label', None)
        self.audioSvc = sm.GetService('audio')
        self.mouseOverSound = attributes.Get('mouseOverSound', None)
        self.mouseExitSound = attributes.Get('mouseExitSound', None)
        if self.buttonState == EmpireThemedButtonState.DISABLED:
            self.state = uiconst.UI_DISABLED
        self.buttonContainer = Container(name='EmpireThemedButton_ButtonContainer', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.AddButtonLabel()
        self.AddButtonOutline()
        self.AddLineDecoration()
        self.AddCurvedGradient()
        self.AddButtonGradient()
        self.AddSideDecoration()
        self.UpdateMouseState()

    def AddLineDecoration(self):
        self.lineDecoration = LineDecoration(name='EmpireThemedButton_LineDecoration', parent=self.buttonContainer, align=uiconst.TOBOTTOM_NOPUSH, width=self.width, height=LINE_HEIGHT, lineWidth=LINE_WIDTH_MIN_RES * GetScaleFactor(), lineDecorationWidth=LINE_DECO_WIDTH_MIN_RES * GetScaleFactor(), invert=True, lineColor=HIGHLIGHT_TINT_BY_RACE[self.raceID] if IS_TINTED_BY_STATE[self.buttonState] else None, opacity=0.0)

    def AddCurvedGradient(self):
        self.curvedGradient = Sprite(name='EmpireThemedButton_CurvedGradient', parent=self.buttonContainer, align=uiconst.TOBOTTOM_NOPUSH, width=CURVED_GRADIENT_WIDTH_MIN_RES * GetScaleFactor(), height=CURVED_GRADIENT_HEIGHT_MIN_RES * GetScaleFactor(), texturePath=CURVED_GRADIENT_TEXTURE_BY_RACE[self.raceID], opacity=0.0)

    def AddButtonOutline(self):
        r, g, b = HIGHLIGHT_TINT_BY_RACE[self.raceID]
        color = (r,
         g,
         b,
         0.0) if IS_TINTED_BY_STATE[self.buttonState] else None
        self.buttonOutline = Sprite(name='EmpireThemedButton_Button_Outline', parent=self.buttonContainer, align=uiconst.TOTOP_NOPUSH, width=self.width, height=self.height, texturePath=BG_TEXTURE_OUTLINE, opacity=0.0, color=color)

    def AddButtonGradient(self):
        gradientTexture = BUTTON_GRADIENT_BY_STATES[self.buttonState][self.mouseState]
        if IS_TINTED_BY_STATE[self.buttonState]:
            r, g, b = BUTTON_TINT_BY_STATE_AND_RACE[self.buttonState][self.raceID]
            self.buttonGradient = SpriteThemeColored(name='EmpireThemedButton_Button_TintedGradient', parent=self.buttonContainer, align=uiconst.TOTOP_NOPUSH, width=self.width, height=self.height, texturePath=gradientTexture, color=(r,
             g,
             b,
             0.0))
        else:
            self.buttonGradient = Sprite(name='EmpireThemedButton_Button_Gradient', parent=self.buttonContainer, align=uiconst.TOTOP_NOPUSH, width=self.width, height=self.height, texturePath=gradientTexture, opacity=0.0)

    def AddButtonLabel(self):
        self.buttonLabel = CCLabel(text=self.label, name='EmpireThemedButton_Button_Label', parent=self.buttonContainer, align=uiconst.CENTER, uppercase=1, letterspace=0, bold=False, fontsize=BUTTON_TEXT_FONTSIZE_MIN_RES * GetScaleFactor(), color=TEXT_TINT_BY_STATE_AND_RACE[self.buttonState][self.raceID], opacity=0.0)

    def AddSideDecoration(self):
        sideDecorationTexture = SIDE_DECO_TEXTURE_BY_RACE[self.raceID]
        sideDecorationWidth = SIDE_DECO_WIDTH_MIN_RES * GetScaleFactor()
        sideDecorationHeight = SIDE_DECO_HEIGHT_MIN_RES * GetScaleFactor()
        sideDecorationLeftTransform = Transform(name='EmpireThemedButton_SideDecoration_TransformLeft', parent=self.buttonContainer, align=uiconst.TOLEFT_NOPUSH, width=-sideDecorationWidth, height=sideDecorationHeight, scale=(-1, 1))
        if IS_TINTED_BY_STATE[self.buttonState]:
            r, g, b = HIGHLIGHT_TINT_BY_RACE[self.raceID]
            self.sideDecorationLeft = SpriteThemeColored(name='EmpireThemedButton_SideDecoration_TintedLeft', parent=sideDecorationLeftTransform, align=uiconst.TOLEFT_NOPUSH, width=sideDecorationWidth, height=sideDecorationHeight, texturePath=sideDecorationTexture, color=(r,
             g,
             b,
             0.0))
            self.sideDecorationRight = SpriteThemeColored(name='EmpireThemedButton_SideDecoration_TintedRight', parent=self.buttonContainer, align=uiconst.TORIGHT_NOPUSH, width=sideDecorationWidth, height=sideDecorationHeight, texturePath=sideDecorationTexture, color=(r,
             g,
             b,
             0.0), left=-sideDecorationWidth)
        else:
            self.sideDecorationLeft = Sprite(name='EmpireThemedButton_SideDecoration_Left', parent=sideDecorationLeftTransform, align=uiconst.TOLEFT_NOPUSH, width=sideDecorationWidth, height=sideDecorationHeight, texturePath=sideDecorationTexture, opacity=0.0)
            self.sideDecorationRight = Sprite(name='EmpireThemedButton_SideDecoration_Right', parent=self.buttonContainer, align=uiconst.TORIGHT_NOPUSH, width=sideDecorationWidth, height=sideDecorationHeight, texturePath=sideDecorationTexture, left=-sideDecorationWidth, opacity=0.0)

    def OnMouseEnter(self, *args):
        newMouseState = MouseState.OVER if DOES_REACT_TO_MOUSE_BY_STATE[self.buttonState] else MouseState.UP
        self.ChangeMouseState(newMouseState)

    def OnMouseExit(self, *args):
        newMouseState = MouseState.UP
        self.ChangeMouseState(newMouseState)

    def OnMouseDown(self, *args):
        newMouseState = MouseState.DOWN if DOES_REACT_TO_MOUSE_BY_STATE[self.buttonState] else MouseState.UP
        self.ChangeMouseState(newMouseState)

    def ChangeMouseState(self, mouseState):
        if self.mouseState == mouseState:
            return
        self.mouseState = mouseState
        if self.mouseOverSound and self.mouseState == MouseState.OVER:
            self.audioSvc.SendUIEvent(self.mouseOverSound)
        if self.mouseExitSound and self.mouseState == MouseState.UP:
            self.audioSvc.SendUIEvent(self.mouseExitSound)
        self.UpdateMouseState()

    def UpdateMouseState(self):
        self.SetButtonLabelMouseState()
        self.SetButtonOutlineMouseState()
        self.SetLineDecorationMouseState()
        self.SetCurvedGradientMouseState()
        self.SetButtonGradientMouseState()
        self.SetSideDecorationMouseState()

    def SetButtonOutlineMouseState(self):
        if self.buttonOutline:
            newButtonOutlineOpacity = BG_TEXTURE_OUTLINE_OPACITY_BY_MOUSE_STATE[self.mouseState]
            uicore.animations.MorphScalar(self.buttonOutline, 'opacity', self.buttonOutline.opacity, newButtonOutlineOpacity, duration=MOUSE_STATE_CHANGE_ANIMATION_DURATION)

    def SetButtonGradientMouseState(self):
        if self.buttonGradient:
            uicore.animations.MorphScalar(self.buttonGradient, 'opacity', self.buttonGradient.opacity, 1.0, duration=MOUSE_STATE_CHANGE_ANIMATION_DURATION)

    def SetButtonLabelMouseState(self):
        if self.buttonLabel:
            newButtonLabelOpacity = BUTTON_TEXT_OPACITY_BY_MOUSE_STATE[self.mouseState]
            uicore.animations.MorphScalar(self.buttonLabel, 'opacity', self.buttonLabel.opacity, newButtonLabelOpacity, duration=MOUSE_STATE_CHANGE_ANIMATION_DURATION)

    def SetLineDecorationMouseState(self):
        if self.lineDecoration:
            newLineDecorationOpacity = 1.0
            uicore.animations.MorphScalar(self.lineDecoration, 'opacity', self.lineDecoration.opacity, newLineDecorationOpacity, duration=MOUSE_STATE_CHANGE_ANIMATION_DURATION)

    def SetCurvedGradientMouseState(self):
        if self.curvedGradient:
            newCurvedGradientOpacity = CURVED_GRADIENT_OPACITY_BY_STATE[self.buttonState]
            uicore.animations.MorphScalar(self.curvedGradient, 'opacity', self.curvedGradient.opacity, newCurvedGradientOpacity, duration=MOUSE_STATE_CHANGE_ANIMATION_DURATION)

    def SetSideDecorationMouseState(self):
        newSideDecorationOpacity = SIDE_DECO_OPACITY_BY_STATES[self.buttonState][self.mouseState]
        if self.sideDecorationLeft:
            uicore.animations.MorphScalar(self.sideDecorationLeft, 'opacity', self.sideDecorationLeft.opacity, newSideDecorationOpacity, duration=MOUSE_STATE_CHANGE_ANIMATION_DURATION)
        if self.sideDecorationRight:
            uicore.animations.MorphScalar(self.sideDecorationRight, 'opacity', self.sideDecorationRight.opacity, newSideDecorationOpacity, duration=MOUSE_STATE_CHANGE_ANIMATION_DURATION)


class EmpireThemedDecoration(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.audioSvc = sm.GetService('audio')
        self.flareSoundIntro = attributes.Get('flareSoundIntro', None)
        self.flareSoundOutro = attributes.Get('flareSoundOutro', None)
        self.flare = None
        self.seal = None
        self.logo = None
        self.buttonState = None
        self.raceID = None
        self.mainContainer = Container(name='EmpireThemedDecoration_MainContainer', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)

    def Close(self):
        self.RemoveLogo()
        self.RemoveSeal()
        self.RemoveFlare()
        Container.Close(self)

    def UpdateDecoration(self, raceID, buttonState):
        shouldUpdate = self.raceID != raceID or self.buttonState != buttonState
        if not shouldUpdate:
            return
        self.buttonState = buttonState
        self.raceID = raceID
        self.RemoveLogo()
        self.RemoveFlare()
        self.RemoveSeal()
        if self.buttonState == EmpireThemedButtonState.NORMAL:
            self.AddLogo()
            self.AddFlare()
            self.AddSeal()

    def RemoveLogo(self):
        if self.logo and not self.logo.destroyed:
            uicore.animations.MorphScalar(self.logo, 'opacity', self.logo.opacity, 0.0, duration=DECORATION_ANIMATION_DURATION_FADE_OUT)
            self.logo.Close()

    def RemoveSeal(self):
        if self.seal and not self.seal.destroyed:
            uicore.animations.MorphScalar(self.seal, 'opacity', self.seal.opacity, 0.0, duration=DECORATION_ANIMATION_DURATION_FADE_OUT)
            self.seal.Close()

    def RemoveFlare(self):
        if self.flare and not self.flare.destroyed:
            if self.flareSoundOutro:
                self.audioSvc.SendUIEvent(self.flareSoundOutro)
            uicore.animations.MorphScalar(self.flare, 'opacity', self.flare.opacity, 0.0, duration=DECORATION_ANIMATION_DURATION_FADE_OUT)
            self.flare.Close()

    def AddLogo(self):
        logoWidth = LOGO_WIDTH_MIN_RES * GetScaleFactor()
        logoHeight = LOGO_HEIGHT_MIN_RES * GetScaleFactor()
        self.logo = Container(name='EmpireThemedDecoration_LogoContainer', parent=self.mainContainer, align=uiconst.TOTOP_NOPUSH, top=LOGO_TOP_PADDING * GetScaleFactor(), width=self.width, height=self.height, opacity=0.0)
        Sprite(name='EmpireThemedDecoration_LogoSprite', parent=self.logo, align=uiconst.CENTERTOP, width=logoWidth, height=logoHeight, texturePath=GetEmpireButtonLogo(self.raceID))
        uicore.animations.MorphScalar(self.logo, 'opacity', self.logo.opacity, 1.0, duration=DECORATION_ANIMATION_DURATION_FADE_IN)

    def AddSeal(self):
        sealWidth = SEAL_WIDTH_MIN_RES * GetScaleFactor()
        sealHeight = SEAL_HEIGHT_MIN_RES * GetScaleFactor()
        self.seal = Container(name='EmpireThemedDecoration_SealContainer', parent=self.mainContainer, align=uiconst.TOTOP_NOPUSH, width=self.width, height=self.height, opacity=0.0)
        Sprite(name='EmpireThemedDecoration_SealSprite', parent=self.seal, align=uiconst.CENTERTOP, width=sealWidth, height=sealHeight, texturePath=SEAL_TEXTURE_BY_RACE[self.raceID])
        uicore.animations.MorphScalar(self.seal, 'opacity', self.seal.opacity, 1.0, duration=DECORATION_ANIMATION_DURATION_FADE_IN)

    def AddFlare(self):
        flareWidth = BURST_WIDTH_MIN_RES * GetScaleFactor()
        flareHeight = BURST_HEIGHT_MIN_RES * GetScaleFactor()
        sealHeight = SEAL_HEIGHT_MIN_RES * GetScaleFactor()
        self.flare = Container(name='EmpireThemedDecoration_FlareContainer', parent=self.mainContainer, align=uiconst.TOTOP_NOPUSH, width=self.width, height=self.height, opacity=0.0, top=sealHeight - flareHeight / 2)
        StreamingVideoSprite(name='EmpireThemedDecoration_Flare', parent=self.flare, align=uiconst.CENTERTOP, width=flareWidth, height=flareHeight, videoPath=FLARE_VIDEO_BY_RACE[self.raceID], state=uiconst.UI_DISABLED, blendMode=TR2_SBM_BLEND, spriteEffect=TR2_SFX_COPY, videoLoop=True, disableAudio=True)
        if self.flareSoundIntro:
            self.audioSvc.SendUIEvent(self.flareSoundIntro)
        uicore.animations.MorphScalar(self.flare, 'opacity', self.flare.opacity, 1.0, duration=DECORATION_ANIMATION_DURATION_FADE_IN)


def GetEmpireThemedDecorationSize():
    return (BURST_WIDTH_MIN_RES * GetScaleFactor(), BURST_HEIGHT_MIN_RES * GetScaleFactor())


def GetSealHeight():
    return SEAL_HEIGHT_MIN_RES * GetScaleFactor()
