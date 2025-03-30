#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\buttonIcon.py
import telemetry
import trinity
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.loggers.buttonLogger import log_button_clicked
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.text.color import TextColor
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.themeColored import SpriteThemeColored
COLOR_ACTIVE = eveColor.WHITE
COLOR_DEFAULT = TextColor.NORMAL
COLOR_INACTIVE = eveColor.GUNMETAL_GREY
_ICON_COLOR_HOVERED = TextColor.HIGHLIGHT
_ICON_COLOR_IDLE = TextColor.NORMAL
_ICON_COLOR_DISABLED = TextColor.DISABLED
_ICON_COLOR_SELECTED = eveThemeColor.THEME_ACCENT

class ButtonIcon(Container):
    __guid__ = 'uicontrols.ButtonIcon'
    OPACITY_IDLE = 0.0
    GLOWAMOUNT_IDLE = 0.0
    GLOWAMOUNT_MOUSEHOVER = 0.35
    GLOWAMOUNT_MOUSECLICK = 1.0
    OPACITY_SELECTED = 0.5
    OPACITY_GLOW_IDLE = 0.0
    default_func = None
    default_args = None
    default_width = 32
    default_height = 32
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_texturePath = None
    default_isActive = True
    default_iconSize = 16
    default_rotation = 0
    default_noBgSize = 1
    default_iconColor = COLOR_DEFAULT
    default_iconEnabledOpacity = 1.0
    default_iconDisabledOpacity = 0.5
    default_colorSelected = None
    default_isHoverBGUsed = None
    default_isSelectedBgUsed = False
    default_hoverTexture = None
    default_downTexture = None
    default_showGlow = True
    default_glowColor = None
    default_soundClick = uiconst.SOUND_BUTTON_CLICK
    default_iconClass = SpriteThemeColored
    default_useThemeColor = True
    default_analyticID = ''
    default_iconBlendMode = trinity.TR2_SBM_ADD
    default_blendMode = trinity.TR2_SBM_BLEND

    def ApplyAttributes(self, attributes):
        super(ButtonIcon, self).ApplyAttributes(attributes)
        self.func = attributes.get('func', self.default_func)
        self.args = attributes.get('args', self.default_args)
        self.isActive = attributes.get('isActive', True)
        self.texturePath = attributes.get('texturePath', self.default_texturePath)
        self.iconSize = attributes.get('iconSize', self.default_iconSize)
        self.iconColor = attributes.get('iconColor', self.default_iconColor)
        self.iconEnabledOpacity = attributes.get('iconEnabledOpacity', self.default_iconEnabledOpacity)
        self.iconDisabledOpacity = attributes.get('iconDisabledOpacity', self.default_iconDisabledOpacity)
        self.isHoverBGUsed = attributes.Get('isHoverBGUsed', self.default_isHoverBGUsed)
        self.isSelectedBgUsed = attributes.Get('isSelectedBgUsed', self.default_isSelectedBgUsed)
        self.colorSelected = attributes.Get('colorSelected', self.default_colorSelected)
        self.rotation = attributes.Get('rotation', self.default_rotation)
        self.hoverTexture = attributes.Get('hoverTexture', self.default_hoverTexture)
        self.downTexture = attributes.Get('downTexture', self.default_downTexture)
        self.showGlow = attributes.Get('showGlow', self.default_showGlow)
        self.glowColor = attributes.Get('glowColor', self.default_glowColor)
        self.soundClick = attributes.Get('soundClick', self.default_soundClick)
        self.iconBlendMode = attributes.Get('iconBlendMode', self.default_iconBlendMode)
        self.blendMode = attributes.Get('blendMode', self.default_blendMode)
        self.iconClass = attributes.Get('iconClass', self.default_iconClass) or self.default_iconClass
        self.useThemeColor = attributes.Get('useThemeColor', self.default_useThemeColor)
        self.analyticID = attributes.Get('analyticID', self.default_analyticID)
        if self.isHoverBGUsed is None:
            if self.iconSize < self.default_noBgSize:
                self.isHoverBGUsed = True
            else:
                self.isHoverBGUsed = False
        self.isSelected = False
        self.enabled = True
        self.ConstructIcon()
        self.bgContainer = Container(name='bgCont', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.selectedBG = None
        self.ConstructBackground()
        self.blinkBg = None
        enabled = attributes.get('enabled', True)
        if not enabled:
            self.Disable()
        self.UpdateIconState(animate=False)

    def SetIconSize(self, iconSize):
        self.iconSize = iconSize
        self.icon.width = self.icon.height = iconSize

    def ConstructBackground(self):
        if self.useThemeColor:
            spriteClass = SpriteThemeColored
        else:
            spriteClass = Sprite
        self.mouseEnterBG = spriteClass(name='mouseEnterBG', bgParent=self.bgContainer, texturePath='res:/UI/Texture/classes/ButtonIcon/mouseEnter.png', opacity=0.0, color=self.colorSelected)
        self.mouseDownBG = spriteClass(name='mouseDownBG', bgParent=self.bgContainer, texturePath='res:/UI/Texture/classes/ButtonIcon/mouseDown.png', opacity=0.0, color=self.colorSelected)

    def ConstructIcon(self):
        self.icon = Sprite(name='icon', parent=self, align=uiconst.CENTER, width=self.iconSize, height=self.iconSize, texturePath=self.texturePath, state=uiconst.UI_DISABLED, rotation=self.rotation, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0, blendMode=self.blendMode)

    def SetTexturePath(self, texturePath):
        self.texturePath = texturePath
        self.icon.SetTexturePath(texturePath)
        self.mouseUpTexture = texturePath

    def SetIconColor(self, color):
        self.iconColor = color
        self.icon.SetRGBA(*color)

    def SetColor(self, color):
        self.mouseEnterBG.SetFixedColor(color)
        self.mouseDownBG.SetFixedColor(color)

    def ConstructBlinkBackground(self):
        if self.blinkBg:
            return
        if self.useThemeColor:
            spriteClass = SpriteThemeColored
        else:
            spriteClass = Sprite
        self.blinkBg = spriteClass(name='blinkBG', bgParent=self.bgContainer, texturePath='res:/UI/Texture/classes/ButtonIcon/mouseEnter.png', opacity=0.0)

    def ConstructSelectedBackground(self):
        if self.selectedBG:
            return
        if self.useThemeColor:
            frameClass = SpriteThemeColored
        else:
            frameClass = Sprite
        self.selectedBG = frameClass(name='selectedBG', bgParent=self.bgContainer, colorType=uiconst.COLORTYPE_UIHILIGHT, idx=0, color=self.colorSelected)
        self.UpdateSelectedColor()

    def Disable(self, opacity = None):
        self.enabled = 0
        if self.mouseEnterBG:
            self.mouseEnterBG.StopAnimations()
            self.mouseEnterBG.opacity = 0.0
        self.UpdateIconState(False)

    def Enable(self):
        self.enabled = 1
        self.UpdateIconState(False)

    def SetRotation(self, value):
        self.icon.rotation = value

    def UpdateIconState(self, animate = True):
        glowAmount = self._GetGlowAmount()
        if animate:
            uicore.animations.MorphScalar(self.icon, 'glowBrightness', self.icon.glowBrightness, glowAmount, duration=uiconst.TIME_ENTRY)
        else:
            uicore.animations.StopAnimation(self.icon, 'glowBrightness')
            self.icon.glowBrightness = glowAmount
        iconColor = self._GetIconColor()
        if animate:
            uicore.animations.SpColorMorphTo(self.icon, endColor=iconColor, duration=uiconst.TIME_ENTRY)
        else:
            uicore.animations.StopAnimation(self.icon, 'color')
            self.icon.SetRGBA(*iconColor)
        self.icon.blendMode = trinity.TR2_SBM_ADD if self.enabled else trinity.TR2_SBM_BLEND

    def _GetIconColor(self):
        if not self.enabled:
            return _ICON_COLOR_DISABLED
        elif uicore.uilib.mouseOver == self:
            return _ICON_COLOR_HOVERED
        elif self.isSelected:
            return self.colorSelected or _ICON_COLOR_SELECTED
        else:
            return self.iconColor or _ICON_COLOR_IDLE

    def _GetIconHoverColor(self):
        return COLOR_ACTIVE

    def _GetGlowAmount(self):
        if not self.enabled:
            return self.GLOWAMOUNT_IDLE
        if uicore.uilib.mouseOver == self or self.isSelected:
            if uicore.uilib.leftbtn:
                return self.GLOWAMOUNT_MOUSECLICK
            else:
                return self.GLOWAMOUNT_MOUSEHOVER
        else:
            return self.GLOWAMOUNT_IDLE

    def _CheckUpdateTexturePath(self):
        if (uicore.uilib.mouseOver == self or self.isSelected) and self.enabled:
            if uicore.uilib.leftbtn:
                texturePath = self.downTexture
            else:
                texturePath = self.hoverTexture
        else:
            texturePath = self.mouseUpTexture
        if texturePath:
            self.SetTexturePath(texturePath)

    def SetActive(self, isActive):
        pass

    def ToggleSelected(self):
        if self.isSelected:
            self.SetDeselected()
        else:
            self.SetSelected()

    @telemetry.ZONE_METHOD
    def SetSelected(self):
        if self.isSelected:
            return
        self.isSelected = True
        self.UpdateIconState()
        self.UpdateSelectedColor()

    @telemetry.ZONE_METHOD
    def SetDeselected(self):
        if not self.isSelected:
            return
        self.isSelected = False
        self.UpdateIconState()
        self.UpdateSelectedColor()

    def UpdateSelectedColor(self):
        if self.isSelected:
            if self.selectedBG:
                self.selectedBG.opacity = self.OPACITY_SELECTED
                iconColor = Color(*self.colorSelected).SetBrightness(1.0).SetSaturation(0.3).GetRGBA() if self.colorSelected else None
            else:
                iconColor = self.colorSelected
        else:
            if self.selectedBG:
                self.selectedBG.opacity = 0.0
            iconColor = self.iconColor
        if iconColor:
            self.icon.SetRGBA(*iconColor)

    def Blink(self, duration = 0.8, loops = 1):
        self.ConstructBlinkBackground()
        uicore.animations.FadeTo(self.blinkBg, 0.0, 0.9, duration=duration, curveType=uiconst.ANIM_WAVE, loops=loops)

    def StopBlink(self):
        if self.blinkBg:
            uicore.animations.FadeOut(self.blinkBg, 0.3)

    def OnClick(self, *args):
        if not self._IsClickable():
            return
        PlaySound(self.soundClick)
        log_button_clicked(self)
        self._ExecuteFunction()

    def _IsClickable(self):
        return self.enabled

    def _ExecuteFunction(self):
        if not self.func:
            return
        if type(self.args) == tuple:
            self.func(*self.args)
        elif self.args:
            self.func(self.args)
        else:
            self.func()

    def OnMouseEnter(self, *args):
        self.StopBlink()
        if not self.enabled:
            return
        self.UpdateIconState()
        if self.isHoverBGUsed:
            uicore.animations.FadeIn(self.mouseEnterBG, 0.5, duration=uiconst.TIME_ENTRY)
        PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def OnMouseExit(self, *args):
        self.UpdateIconState()
        if self.isHoverBGUsed:
            uicore.animations.FadeOut(self.mouseEnterBG, duration=uiconst.TIME_EXIT)

    def OnMouseDown(self, *args):
        if not self.enabled:
            return
        if self.isHoverBGUsed:
            uicore.animations.FadeTo(self.mouseDownBG, self.mouseDownBG.opacity, 1.0, duration=0.05)
            uicore.animations.FadeOut(self.mouseEnterBG, duration=0.05)
        self.UpdateIconState()

    def OnMouseUp(self, *args):
        if self.isHoverBGUsed:
            uicore.animations.FadeOut(self.mouseDownBG, duration=0.05)
        if not self.enabled:
            return
        self.UpdateIconState()
        if uicore.uilib.mouseOver == self:
            if self.isHoverBGUsed:
                uicore.animations.FadeIn(self.mouseEnterBG, 0.5, duration=0.05)

    def OnEndDrag(self, *args):
        if uicore.uilib.mouseOver != self:
            uicore.animations.FadeOut(self.mouseEnterBG, duration=0.2)
        elif self.isHoverBGUsed:
            uicore.animations.FadeIn(self.mouseEnterBG, duration=0.1)
        uicore.animations.FadeOut(self.mouseDownBG, duration=0.1)
        self.UpdateIconState()
