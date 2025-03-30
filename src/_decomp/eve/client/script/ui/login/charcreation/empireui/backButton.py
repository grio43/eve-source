#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\empireui\backButton.py
from carbonui import uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.frame import Frame
from carbonui.uicore import uicore
from carbonui.primitives.container import Container
import charactercreator.client.scalingUtils as ccScalingUtils
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.themeColored import FrameThemeColored
from eve.client.script.ui.login.charcreation.label import CCLabel
from eve.client.script.ui.login.charcreation.technologyViewUtils import TECH_NAV_ARROW_SIZE
from eve.client.script.ui.util.uix import GetTextWidth
from eve.common.lib.appConst import raceAmarr, raceCaldari, raceGallente, raceMinmatar
from localization import GetByLabel
from math import pi
ARROW_TEXTURE = 'res:/UI/Texture/Classes/EmpireSelection/navArrow_Up.png'
ARROW_TEXTURE_OVER = 'res:/UI/Texture/Classes/EmpireSelection/navArrow_Over.png'
ARROW_TEXTURE_DOWN = 'res:/UI/Texture/Classes/EmpireSelection/navArrow_Down.png'
BACK_BUTTON_UP_TEXTURE = 'res:/UI/Texture/Classes/EmpireSelection/largeButton_Up.png'
BACK_BUTTON_DOWN_TEXTURE = 'res:/UI/Texture/Classes/EmpireSelection/largeButton_Over.png'
BACK_BUTTON_OVER_TEXTURE = 'res:/UI/Texture/Classes/EmpireSelection/largeButton_Down.png'
ARROW_ICON_SIZE = 24.5
BACK_BUTTON_FONTSIZE = 12
BACK_BUTTON_ARROW_TEXT_PADDING = 4
BACK_BUTTON_ARROW_LEFT_PADDING_RATIO = 0.35
BACK_BUTTON_OPACITY = 1.0
BACK_BUTTON_TINT_BY_RACE = {raceAmarr: (0.51, 0.44, 0.32),
 raceCaldari: (0.29, 0.43, 0.5),
 raceGallente: (0.21, 0.4, 0.4),
 raceMinmatar: (0.4, 0.22, 0.2)}
BACK_BUTTON_LABEL = 'UI/Commands/Back'
BUTTON_HOVER_SOUND = 'ui_icc_button_mouse_over_play'
BUTTON_SELECT_SOUND = 'ui_icc_button_select_play'

class BackButton(ButtonIcon):
    default_iconColor = (1.0, 1.0, 1.0, 1.0)
    default_iconSize = TECH_NAV_ARROW_SIZE
    default_rotation = pi
    default_isBGFrameUsed = True
    default_isHoverBGUsed = True
    default_showGlow = False
    default_texturePath = ARROW_TEXTURE
    default_hoverTexture = ARROW_TEXTURE_OVER
    default_downTexture = ARROW_TEXTURE_DOWN
    default_mouseUpBGTexture = BACK_BUTTON_UP_TEXTURE
    default_mouseEnterBGTexture = BACK_BUTTON_OVER_TEXTURE
    default_mouseDownBGTexture = BACK_BUTTON_DOWN_TEXTURE
    default_frameCornerSize = 7
    default_frameOffset = 0

    def ApplyAttributes(self, attributes):
        self.mouseUpBGTexture = attributes.Get('mouseUpBGTexture', self.default_mouseUpBGTexture)
        self.mouseEnterBGTexture = attributes.Get('mouseEnterBGTexture', self.default_mouseEnterBGTexture)
        self.mouseDownBGTexture = attributes.Get('mouseDownBGTexture', self.default_mouseDownBGTexture)
        self.isBGFrameUsed = attributes.Get('isBGFrameUsed', self.default_isBGFrameUsed)
        self.frameOffset = attributes.Get('frameOffset', self.default_frameOffset)
        self.frameCornerSize = attributes.Get('frameCornerSize', self.default_frameCornerSize)
        self.bgRotation = attributes.Get('bgRotation', self.default_bgRotation)
        self.mouseUpBG = None
        self.mouseEnterBG = None
        self.mouseDownBG = None
        super(BackButton, self).ApplyAttributes(attributes)
        raceID = attributes.Get('raceID', None)
        r, g, b = BACK_BUTTON_TINT_BY_RACE[raceID]
        color = (r,
         g,
         b,
         BACK_BUTTON_OPACITY)
        self.SetColor(color)
        backText = GetByLabel(BACK_BUTTON_LABEL)
        backTextFontsize = BACK_BUTTON_FONTSIZE * ccScalingUtils.GetScaleFactor()
        backStringWidth = GetTextWidth(backText, fontsize=backTextFontsize, uppercase=1, hspace=1)
        labelContainer = Container(name='labelContainer', parent=self, align=uiconst.TOTOP_NOPUSH, width=self.width, height=self.height)
        backLabel = CCLabel(text=backText, name='backLabel', parent=labelContainer, align=uiconst.CENTERLEFT, uppercase=1, bold=False, fontsize=backTextFontsize)
        margin = BACK_BUTTON_ARROW_TEXT_PADDING * ccScalingUtils.GetScaleFactor()
        self.icon.align = uiconst.CENTERLEFT
        contentsWidth = self.iconSize + backStringWidth + margin
        freeSpace = max(0, self.width - contentsWidth)
        iconLeft = freeSpace * BACK_BUTTON_ARROW_LEFT_PADDING_RATIO
        self.icon.left = iconLeft
        backLabel.left = iconLeft + self.iconSize + margin

    def ConstructIcon(self):
        iconContainer = Container(name='iconContainer', parent=self, width=self.width, height=self.height, align=uiconst.TOTOP_NOPUSH)
        self.icon = GlowSprite(name='icon', parent=iconContainer, align=uiconst.CENTER, width=self.iconSize, height=self.iconSize, texturePath=self.texturePath, state=uiconst.UI_DISABLED, color=self.iconColor, iconOpacity=self.iconDisabledOpacity, gradientStrength=self.iconDisabledOpacity, rotation=self.rotation)
        if self.isBGFrameUsed and self.mouseUpBGTexture:
            self.mouseUpBG = Frame(name='bg_frame', texturePath=self.mouseUpBGTexture, offset=self.frameOffset, cornerSize=self.frameCornerSize, parent=self, align=uiconst.TOTOP_NOPUSH, width=self.width, height=self.height, rotation=self.bgRotation, color=(1.0, 1.0, 1.0, 0.5))

    def ConstructBackground(self):
        if self.mouseEnterBGTexture and self.mouseDownBGTexture:
            self.mouseEnterBG = FrameThemeColored(name='mouseEnterBG', bgParent=self.bgContainer, texturePath=self.mouseEnterBGTexture, width=self.width, height=self.height, opacity=0.0, colorType=uiconst.COLORTYPE_UIHILIGHT, rotation=self.bgRotation, cornerSize=self.frameCornerSize)
            self.mouseDownBG = FrameThemeColored(name='mouseDownBG', bgParent=self.bgContainer, texturePath=self.mouseDownBGTexture, width=self.width, height=self.height, opacity=0.0, colorType=uiconst.COLORTYPE_UIHILIGHT, rotation=self.bgRotation, cornerSize=self.frameCornerSize)
            return
        super(BackButton, self).ConstructBackground()

    def OnMouseDown(self, *args):
        if not self.enabled:
            return
        if self.isHoverBGUsed:
            uicore.animations.FadeTo(self.mouseDownBG, self.mouseDownBG.opacity, 1.0, duration=0.1, callback=self.ShowMouseDownBG)
            uicore.animations.FadeOut(self.mouseEnterBG, duration=0.1)
        self.UpdateIconState()

    def OnMouseUp(self, *args):
        if self.isHoverBGUsed:
            uicore.animations.FadeOut(self.mouseDownBG, duration=0.1)
        if not self.enabled:
            return
        self.UpdateIconState()
        if uicore.uilib.mouseOver == self:
            if self.isHoverBGUsed:
                uicore.animations.FadeIn(self.mouseEnterBG, 0.5, duration=0.1, callback=self.ShowMouseEnterBG)

    def ShowMouseEnterBG(self):
        self.mouseEnterBG.opacity = 1.0

    def ShowMouseDownBG(self):
        self.mouseDownBG.opacity = 1.0

    def SetColor(self, color):
        if self.mouseUpBG:
            self.mouseUpBG.color = color
        if self.mouseEnterBG:
            self.mouseEnterBG.SetFixedColor(color)
        if self.mouseDownBG:
            self.mouseDownBG.SetFixedColor(color)

    def OnMouseEnter(self, *args):
        super(BackButton, self).OnMouseEnter()
        sm.GetService('audio').SendUIEvent(BUTTON_HOVER_SOUND)

    def OnClick(self, *args):
        sm.GetService('audio').SendUIEvent(BUTTON_SELECT_SOUND)
        uicore.layer.charactercreation.controller.Back()
