#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\glowSprite.py
import carbonui.const as uiconst
import trinity
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.themeColored import SpriteThemeColored
GLOWAMOUNT_IDLE = 0.0
GLOWAMOUNT_HOVER = 1.0
GLOWAMOUNT_MOUSEDOWN = 1.5

class GlowSprite(Container):
    default_name = 'GlowSprite'
    default_texturePath = ''
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_glowAmount = 0.0
    default_glowExpand = 0
    default_color = None
    default_rotation = 0.0
    default_iconOpacity = 0.9
    default_gradientStrength = 1.0
    default_ignoreColorBlindMode = True
    default_colorType = uiconst.COLORTYPE_UIHILIGHTGLOW
    default_iconClass = Sprite
    default_iconBlendMode = Sprite.default_blendMode

    def ApplyAttributes(self, attributes):
        super(GlowSprite, self).ApplyAttributes(attributes)
        self.texturePath = attributes.Get('texturePath', self.default_texturePath)
        self.rotation = attributes.Get('rotation', self.default_rotation)
        self.iconOpacity = attributes.Get('iconOpacity', self.default_iconOpacity)
        self.gradientStrength = attributes.get('gradientStrength', self.default_gradientStrength)
        self.color = attributes.get('color', self.default_color)
        self.glowColor = attributes.get('glowColor', self.default_color)
        self.ignoreColorBlindMode = attributes.get('ignoreColorBlindMode', self.default_ignoreColorBlindMode)
        self.iconClass = attributes.get('iconClass', self.default_iconClass)
        self.iconBlendMode = attributes.get('iconBlendMode', self.default_iconBlendMode)
        colorType = attributes.get('colorType', self.default_colorType)
        self._glowAmount = attributes.get('glowAmount', self.default_glowAmount)
        self.spriteEffect = None
        self.glowExpand = None
        self.icon = Sprite(bgParent=self, name='icon', state=uiconst.UI_DISABLED, align=uiconst.TOALL, color=self.color, texturePath=self.texturePath, rotation=self.rotation, ignoreColorBlindMode=self.ignoreColorBlindMode, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=self._glowAmount, blendMode=self.iconBlendMode)
        self.glowIcon = None
        self.bgGradient = None

    def _ConstructGlow(self):
        if not self.glowIcon:
            self.OnSizeUpdate()
            self.glowIcon = self.iconClass(name='glowIcon', bgParent=self, state=uiconst.UI_DISABLED, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, spriteEffect=self.spriteEffect, padding=-self.glowExpand, blendMode=trinity.TR2_SBM_ADDX2, opacity=0.0, texturePath=self.texturePath, rotation=self.rotation, color=self.glowColor)
            self.bgGradient = self.iconClass(name='bgGradient', bgParent=self, texturePath='res:/UI/Texture/shared/circularGradient.png', opacity=0.0, padding=-self.glowExpand, color=self.glowColor)

    def UpdateSpriteEffect(self, size):
        if size > 20:
            self.spriteEffect = trinity.TR2_SFX_GLOW
        else:
            self.spriteEffect = trinity.TR2_SFX_BLUR

    def OnSizeUpdate(self):
        w, h = self.GetAbsoluteSize()
        size = max(w, h)
        self.UpdateSpriteEffect(size)
        self.UpdateGlowExpand(size)

    def _OnResize(self, *args):
        self.OnSizeUpdate()

    def UpdateGlowExpand(self, size):
        g = size / 20
        g = max(1, min(g, 3))
        self.glowExpand = g
        if self.glowIcon:
            self.glowIcon.padding = (-g,
             -g,
             -g,
             -g)
            self.bgGradient.padding = (-g,
             -g,
             -g,
             -g)

    def SetTexturePath(self, texturePath):
        self.texturePath = texturePath
        self.icon.SetTexturePath(texturePath)
        if self.glowIcon:
            self.glowIcon.SetTexturePath(texturePath)

    def LoadTexture(self, texturePath):
        self.SetTexturePath(texturePath)

    def LoadIcon(self, iconNo, ignoreSize = False):
        texturePath, _ = Icon.ConvertIconNoToResPath(iconNo)
        self.SetTexturePath(texturePath)

    def LoadIconByTypeID(self, typeID, itemID, *args, **kw):
        icon = Icon(typeID=typeID, itemID=itemID)
        self.SetTexturePath(icon.texturePath)

    def SetRGBA(self, *color):
        self.color = color
        self.icon.SetRGBA(*color)
        if self.glowIcon and self.iconClass == SpriteThemeColored:
            self.glowIcon.SetFixedColor(color)
            self.bgGradient.SetFixedColor(color)

    def SetRGB(self, *args):
        self.SetRGBA(*args)

    def GetRGBA(self):
        return self.icon.GetRGBA()

    def OnMouseEnter(self, *args):
        self._AnimateGlow(GLOWAMOUNT_HOVER, uiconst.TIME_ENTRY)

    def OnMouseExit(self, *args):
        self._AnimateGlow(GLOWAMOUNT_IDLE, uiconst.TIME_EXIT)

    def OnMouseDown(self, *args):
        self._AnimateGlow(GLOWAMOUNT_HOVER, 0.1)

    def OnMouseUp(self, *args):
        self._AnimateGlow(1.0, 0.3)

    def _AnimateGlow(self, value, duration):
        uicore.animations.MorphScalar(self, 'glowAmount', self.glowAmount, value, duration=duration)

    @property
    def glowAmount(self):
        return self.icon.glowBrightness

    @glowAmount.setter
    def glowAmount(self, value):
        self.icon.glowBrightness = value

    def SetRotation(self, value):
        self.rotation = value
        self.icon.rotation = value
        if self.glowIcon:
            self.glowIcon.rotation = value
