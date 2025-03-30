#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\charCreationButtons.py
import trinity
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from charactercreator.client.empireSelectionData import GetEmpireColor, GetEmpireLogo, GetEmpireButtonLogo
import charactercreator.client.scalingUtils as ccScalingUtils
from eve.client.script.ui import eveColor
from eve.common.lib.appConst import raceAmarr, raceCaldari, raceGallente, raceMinmatar
from localization import GetByLabel
FILL_SELECTION = 0.2
TEXT_NORMAL = 0.8
EXIT_BUTTON_SIZE = 16
TEMP_RACE_BUTTON_NORMAL = 'res:/UI/Texture/CharacterCreation/raceButtons/RaceButtonNormal_%s.dds'
TEMP_RACE_BUTTON_DOWN = 'res:/UI/Texture/CharacterCreation/raceButtons/RaceButtonDown_%s.dds'
BLOODLINE_HEADERS = {raceAmarr: GetByLabel('UI/Login/CharacterCreation/BloodlineSelection/AmarrBloodlines'),
 raceCaldari: GetByLabel('UI/Login/CharacterCreation/BloodlineSelection/CaldariBloodlines'),
 raceGallente: GetByLabel('UI/Login/CharacterCreation/BloodlineSelection/GallenteBloodlines'),
 raceMinmatar: GetByLabel('UI/Login/CharacterCreation/BloodlineSelection/MinmatarBloodlines')}
EMPIRE_TAB_BUTTON_OPACITY = 0.3
EMPIRE_TAB_BUTTON_TEXTURE_ACTIVE = 'res:/UI/Texture/classes/EmpireSelection/empireTabActive.png'
EMPIRE_TAB_BUTTON_TEXTURE_ACTIVE_GLOW = 'res:/UI/Texture/classes/EmpireSelection/empireTabActiveGlow.png'
EMPIRE_TAB_BUTTON_TEXTURE_INACTIVE = 'res:/UI/Texture/classes/EmpireSelection/empireTabInactive.png'
HEADER_SPOTLIGHT_HEIGHT_FACTOR = 1.6
EMPIRE_TAB_ICON_SIZE = 160
EMPIRE_ICON_SIZE_ACTIVE = 84
EMPIRE_ICON_PAD = 3
EMPIRE_ICON_GLOW_WIDTH = 64
EMPIRE_ICON_GLOW_HEIGHT = 17
EMPIRE_ICON_GRADIENT_HEIGHT = 1
EMPIRE_ICON_FRAME_ACTIVE_OPACITY = 1.0
EMPIRE_ICON_FRAME_INACTIVE_OPACITY = 0.6
EMPIRE_ICON_FRAME_HOVER_OPACITY = 1.5
EMPIRE_ICON_FRAME_DOWN_OPACITY = 3.0
EMPIRE_ICON_FRAME_GLOW_OPACITY = 1.0
EMPIRE_ICON_FRAME_GRADIENT_OPACITY = 1.0

def GetEmpireTabSizeLarge():
    return EMPIRE_ICON_SIZE_ACTIVE * ccScalingUtils.GetScaleFactor()


class BaseCCButton(Container):
    __guid__ = 'uicls.BaseCCButton'
    default_state = uiconst.UI_NORMAL
    default_left = 0
    default_top = 0
    default_width = 128
    default_height = 128
    default_align = uiconst.CENTER
    mouseoverSound = 'ui_icc_button_mouse_over_play'
    selectSound = 'ui_icc_button_select_play'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        spriteWidth = attributes.Get('spriteWidth', self.default_width)
        spriteHeight = attributes.Get('spriteHeight', self.default_height)
        self.normalSprite = Sprite(name='normalSprite', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='', width=spriteWidth, height=spriteHeight)
        self.hiliteSprite = Sprite(name='hiliteSprite', parent=self, align=uiconst.CENTER, state=uiconst.UI_HIDDEN, texturePath='', width=spriteWidth, height=spriteHeight)
        self.normalSprite.SetAlpha(0.3)

    def OnMouseEnter(self, *args):
        if self.mouseoverSound:
            sm.StartService('audio').SendUIEvent(unicode(self.mouseoverSound))
        self.normalSprite.SetAlpha(0.6)

    def OnMouseExit(self, *args):
        self.normalSprite.SetAlpha(0.3)

    def Deselect(self):
        self.hiliteSprite.state = uiconst.UI_HIDDEN
        self.normalSprite.state = uiconst.UI_DISABLED
        self.normalSprite.SetAlpha(0.3)

    def Select(self):
        if self.selectSound:
            sm.StartService('audio').SendUIEvent(unicode(self.selectSound))
        self.hiliteSprite.state = uiconst.UI_DISABLED
        self.normalSprite.state = uiconst.UI_HIDDEN

    def OnClick(self, *args):
        pass


class EmpireTabAnimationType:
    ACTIVATE = 1
    DEACTIVATE = 2
    HOVER = 3
    DEHOVER = 4


class EmpireTabButton(BaseCCButton):
    selectSound = None
    mouseoverSound = None

    def ApplyAttributes(self, attributes):
        self.isActive = attributes.isActive
        self.isHovered = False
        tabSize = GetEmpireTabSizeLarge()
        attributes.spriteWidth = tabSize
        attributes.spriteHeight = tabSize
        super(EmpireTabButton, self).ApplyAttributes(attributes)
        self.raceSetter = attributes.raceSetter
        self.raceHoverer = attributes.raceHoverer
        self.raceID = attributes.raceID
        self.isDisabled = attributes.get('isDisabled', False)
        r, g, b, _ = GetEmpireColor(self.raceID)
        self.buttonLogo = Sprite(name='buttonLogo', texturePath=GetEmpireButtonLogo(self.raceID), parent=self, width=tabSize, height=tabSize, state=uiconst.UI_DISABLED, align=uiconst.CENTER, opacity=float(not self.isActive))
        self.empireLogo = Sprite(name='empireLogo', texturePath=GetEmpireLogo(self.raceID), parent=self, width=tabSize, height=tabSize, state=uiconst.UI_DISABLED, align=uiconst.CENTER, opacity=float(self.isActive))
        self.BuildFrames()

    def BuildFrames(self):
        scaleFactor = ccScalingUtils.GetScaleFactor()
        r, g, b, _ = GetEmpireColor(self.raceID)
        tabSize = GetEmpireTabSizeLarge()
        self.frameGradientContainer = Container(parent=self, name='frameGradientContainer', align=uiconst.TOTOP_NOPUSH, width=tabSize, height=tabSize)
        self.frameGradient = GradientSprite(parent=self.frameGradientContainer, name='frameGradient', align=uiconst.CENTERBOTTOM, width=tabSize, height=EMPIRE_ICON_GRADIENT_HEIGHT, rgbData=[(0, (1.0, 1.0, 1.0))], alphaData=[(0, 0.0),
         (0.4, 0.5),
         (0.6, 0.5),
         (1.0, 0.0)], opacity=EMPIRE_ICON_FRAME_GRADIENT_OPACITY * self.isActive)
        self.frameGlowContainer = Container(parent=self, name='frameGlowContainer', align=uiconst.TOTOP_NOPUSH, width=tabSize, height=tabSize)
        self.frameGlow = Frame(parent=self.frameGlowContainer, name='frameGlow', align=uiconst.CENTERBOTTOM, width=EMPIRE_ICON_GLOW_WIDTH * scaleFactor, height=EMPIRE_ICON_GLOW_HEIGHT * scaleFactor, texturePath=EMPIRE_TAB_BUTTON_TEXTURE_ACTIVE_GLOW, color=(r,
         g,
         b,
         EMPIRE_ICON_FRAME_GLOW_OPACITY * self.isActive))
        self.frameActiveContainer = Container(parent=self, name='frameActiveContainer', align=uiconst.TOTOP_NOPUSH, width=tabSize, height=tabSize)
        self.frameActive = Frame(parent=self.frameActiveContainer, name='frameActive', align=uiconst.TOALL, texturePath=EMPIRE_TAB_BUTTON_TEXTURE_ACTIVE, color=(r,
         g,
         b,
         EMPIRE_ICON_FRAME_ACTIVE_OPACITY * self.isActive))
        self.frameInactiveContainer = Container(parent=self, name='frameInactiveContainer', align=uiconst.TOTOP_NOPUSH, width=tabSize, height=tabSize)
        self.frameInactive = Frame(parent=self.frameInactiveContainer, name='frameInactive', align=uiconst.TOALL, texturePath=EMPIRE_TAB_BUTTON_TEXTURE_INACTIVE, color=(r,
         g,
         b,
         EMPIRE_ICON_FRAME_INACTIVE_OPACITY))

    def DesaturateRaceIcon(self):
        self.buttonLogo.spriteEffect = trinity.TR2_SFX_SOFTLIGHT
        self.buttonLogo.saturation = 0

    def GetMaximumAllowedLogoOpacity(self):
        if self.isDisabled:
            return 0.5
        return 1.0

    def Activate(self):
        self.isActive = True
        self.ActivateFrame()
        self.buttonLogo.opacity = 0.0
        self.empireLogo.opacity = 1.0

    def ActivateFrame(self):
        self.frameActive.opacity = EMPIRE_ICON_FRAME_ACTIVE_OPACITY
        self.frameGlow.opacity = EMPIRE_ICON_FRAME_GLOW_OPACITY
        self.frameGradient.opacity = EMPIRE_ICON_FRAME_GRADIENT_OPACITY

    def Deactivate(self):
        self.isActive = False
        self.DeactivateFrame()
        self.buttonLogo.opacity = self.GetMaximumAllowedLogoOpacity()
        self.empireLogo.opacity = 0.0

    def DeactivateFrame(self):
        self.frameActive.opacity = 0.0
        self.frameGlow.opacity = 0.0
        self.frameGradient.opacity = 0.0

    def Hover(self):
        self.isHovered = True
        self.HoverFrame()
        self.buttonLogo.opacity = self.GetMaximumAllowedLogoOpacity()
        self.empireLogo.opacity = 0.0

    def HoverFrame(self):
        self.frameActive.opacity = EMPIRE_ICON_FRAME_HOVER_OPACITY
        self.frameGlow.opacity = 0.0
        self.frameGradient.opacity = 0.0

    def Dehover(self):
        self.isHovered = False
        self.DeactivateFrame()
        self.buttonLogo.opacity = self.GetMaximumAllowedLogoOpacity()
        self.empireLogo.opacity = 0.0

    def OnClick(self):
        self.raceSetter(self.raceID)

    def OnMouseDown(self, *args):
        animations.MorphScalar(self.frameActive, 'opacity', self.frameActive.opacity, EMPIRE_ICON_FRAME_DOWN_OPACITY, 0.05)
        super(EmpireTabButton, self).OnMouseDown(self, *args)

    def OnMouseUp(self, *args):
        animations.MorphScalar(self.frameActive, 'opacity', self.frameActive.opacity, EMPIRE_ICON_FRAME_ACTIVE_OPACITY, 0.25)
        super(EmpireTabButton, self).OnMouseUp(self, *args)

    def OnMouseEnter(self):
        if not self.isActive and not self.isHovered:
            self.raceHoverer(self.raceID)
        super(EmpireTabButton, self).OnMouseEnter()

    def OnMouseExit(self):
        if not self.isActive and self.isHovered:
            self.raceHoverer(None)
        super(EmpireTabButton, self).OnMouseExit()


class EmpireTab(Container):
    default_mouseUpBGTexture = None
    default_mouseEnterBGTexture = None
    default_mouseDownBGTexture = None
    default_isBGFrameUsed = None
    default_frameOffset = 0
    default_frameCornerSize = 0

    def ApplyAttributes(self, attributes):
        self.isActive = attributes.Get('isActive', False)
        self.isHovered = attributes.Get('isActive', False)
        self.raceID = attributes.Get('raceID', None)
        self.raceSetter = attributes.Get('raceSetter', None)
        self.raceHoverer = attributes.Get('raceHoverer', None)
        self.empireLogoPath = attributes.Get('empireLogoPath', None)
        self.isDisabled = attributes.Get('isDisabled', False)
        super(EmpireTab, self).ApplyAttributes(attributes)
        self.iconSize = self.width / 2.0
        tabSize = GetEmpireTabSizeLarge()
        self.buttonContainer = Container(parent=self, align=uiconst.BOTTOMLEFT, width=self.width, height=self.height)
        self.button = EmpireTabButton(parent=self.buttonContainer, width=tabSize, height=tabSize, raceID=self.raceID, align=uiconst.BOTTOMLEFT, raceSetter=self.raceSetter, raceHoverer=self.raceHoverer, isActive=self.isActive, isDisabled=self.isDisabled)
        self.gradientFill = None
        self.gradientBgFill = None
        self.width = tabSize
        self.height = tabSize
        if self.isDisabled:
            Sprite(name='warningIcon', parent=self.buttonContainer, align=uiconst.BOTTOMLEFT, width=26, height=26, left=5, texturePath='res:/UI/Texture/classes/agency/iconExclamation.png', color=eveColor.WARNING_ORANGE, state=uiconst.UI_NORMAL, hint=GetByLabel('UI/CharacterCreation/FactionDisabled'))
            self.button.Disable()
            self.button.DesaturateRaceIcon()

    def Activate(self):
        self.isActive = True
        self.button.Activate()

    def Deactivate(self):
        self.isActive = False
        self.button.Deactivate()

    def Hover(self):
        self.isHovered = True
        self.button.Hover()

    def Dehover(self):
        self.isHovered = False
        self.button.Dehover()


class StaticBloodlineButton(Container):
    __guid__ = 'uicls.SmallerBloodlineButton'
    default_width = 125
    default_height = 100

    def ApplyAttributes(self, attributes):
        iconTexturePath = attributes.iconTexturePath
        super(StaticBloodlineButton, self).ApplyAttributes(attributes)
        self.bloodlineID = attributes.bloodlineID
        self.sprite = Sprite(parent=self, align=uiconst.CENTER, texturePath=iconTexturePath, width=self.width, height=self.height)

    def Resize(self, width, height):
        self.width = width
        self.height = height
        self.sprite.width = width
        self.sprite.height = height


class ExitButton(Container):
    default_name = 'exitButton'
    default_width = EXIT_BUTTON_SIZE
    default_height = EXIT_BUTTON_SIZE
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.onClick = attributes.onClick
        width = attributes.Get('width', self.default_width)
        height = attributes.Get('height', self.default_height)
        Sprite(parent=self, texturePath='res:/UI/Texture/Icons/73_16_45.png', width=width, height=height, align=uiconst.CENTER, state=uiconst.UI_DISABLED, color=Color.GRAY7)

    def OnClick(self):
        self.onClick()
