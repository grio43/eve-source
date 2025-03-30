#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\cloneGrade\upgradeButton.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui import TextBody
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from carbonui.util.color import Color
from clonegrade.const import COLOR_OMEGA_ORANGE
from eve.client.script.ui.control.eveLabel import Label
from carbonui.loggers.buttonLogger import log_button_clicked
import signals
COLOR_IDLE = (1.0, 1.0, 1.0, 0.0)

class UpgradeButton(Container):
    default_state = uiconst.UI_NORMAL
    default_color = COLOR_OMEGA_ORANGE
    default_fontSize = 18
    default_upperCase = True
    default_stretchTexturePath = 'res:/UI/Texture/Classes/CloneGrade/omegaBG.png'
    default_hiliteTexturePath = 'res:/UI/Texture/Classes/CloneGrade/omegaHilite.png'
    default_textureEdgeSize = 18
    default_hoverSound = 'upgrade_menu_button_hover_play'
    default_clickSound = 'upgrade_future_play'
    default_onMouseEnterCallback = None
    default_onMouseExitCallback = None
    default_glowBrightness = 0

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.text = attributes.text
        self.labelColor = attributes.get('labelColor', self.default_color)
        self.fillColor = attributes.get('fillColor', self.default_color)
        self.onMouseEnterCallback = attributes.get('onMouseEnterCallback', self.default_onMouseEnterCallback)
        self.onMouseExitCallback = attributes.get('onMouseExitCallback', self.default_onMouseExitCallback)
        self.onClick = attributes.onClick
        self.fontSize = attributes.get('fontSize', self.default_fontSize)
        self.upperCase = attributes.get('upperCase', self.default_upperCase)
        self.stretchTexturePath = attributes.get('stretchTexturePath', self.default_stretchTexturePath)
        self.stretchTextureColor = attributes.Get('stretchTextureColor', Color.WHITE)
        self.textureEdgeSize = attributes.get('textureEdgeSize', self.default_textureEdgeSize)
        self.hiliteTexturePath = attributes.get('hiliteTexturePath', self.default_hiliteTexturePath)
        self.hoverSound = attributes.get('hoverSound', self.default_hoverSound)
        self.clickSound = attributes.get('clickSound', self.default_clickSound)
        self.glowBrightness = attributes.get('glowBrightness', self.default_glowBrightness)
        self.analyticID = attributes.analyticID
        self._layout()

    def _layout(self):
        self._construct_content()
        self.hilite = StretchSpriteHorizontal(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=self.hiliteTexturePath, rightEdgeSize=self.textureEdgeSize, leftEdgeSize=self.textureEdgeSize, opacity=0.0, glowBrightness=self.glowBrightness)
        self.bg = StretchSpriteHorizontal(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=self.stretchTexturePath, color=self.stretchTextureColor, rightEdgeSize=self.textureEdgeSize, leftEdgeSize=self.textureEdgeSize, opacity=0.85, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=self.glowBrightness)

    def _construct_content(self):
        self.label = Label(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, text=self.text, fontsize=self.fontSize, uppercase=self.upperCase, bold=True, color=self.labelColor)

    def OnMouseEnter(self, *args):
        if self.hoverSound is not None:
            PlaySound(self.hoverSound)
        animations.SpColorMorphTo(self.hilite, (1.0, 1.0, 1.0, 0.5), self.fillColor, duration=0.3)
        animations.SpColorMorphTo(self.label, self.label.GetRGBA(), Color.BLACK, duration=0.3)
        if self.onMouseEnterCallback:
            self.onMouseEnterCallback()

    def OnMouseExit(self, *args):
        duration = 0.15
        animations.SpColorMorphTo(self.hilite, self.hilite.GetRGBA(), COLOR_IDLE, duration=duration)
        animations.SpColorMorphTo(self.label, self.label.GetRGBA(), self.labelColor, duration=duration)
        if self.onMouseExitCallback:
            self.onMouseExitCallback()

    def OnClick(self, *args):
        if self.clickSound is not None:
            PlaySound(self.clickSound)
        log_button_clicked(self)
        self.onClick()
        animations.SpColorMorphTo(self.label, self.label.GetRGBA(), self.labelColor, duration=0.3)
        animations.SpColorMorphTo(self.hilite, (1.0, 1.0, 1.0, 1.0), COLOR_IDLE, duration=0.3)


class UpgradeIconButton(UpgradeButton):

    def ApplyAttributes(self, attributes):
        self._iconTexturePath = attributes.icon or 'res:/UI/Texture/classes/CloneGrade/omega_16.png'
        self._iconSize = attributes.iconSize or (16, 17)
        self._animate = attributes.animate
        self.on_mouse_enter = signals.Signal('on_mose_enter_button')
        self.on_mouse_exit = signals.Signal('on_mouse_exit_button')
        UpgradeButton.ApplyAttributes(self, attributes)

    def start_pulse_glow(self):
        if self._animate:
            self._pulse_glow()

    def stop_pulse_glow(self):
        if self._animate:
            animations.StopAnimation(self.bg, 'glowBrightness')
            self.bg.glowBrightness = 0

    def _layout(self):
        super(UpgradeIconButton, self)._layout()
        self.bg.opacity = 1
        if self._animate:
            self._pulse_glow()

    def _construct_content(self):
        container = ContainerAutoSize(parent=self, align=uiconst.CENTER)
        self.icon = Sprite(parent=container, align=uiconst.CENTERLEFT, texturePath=self._iconTexturePath, width=self._iconSize[0], height=self._iconSize[1], left=12, color=self.labelColor)
        self.icon.OnClick = self.OnClick
        self.label = TextBody(parent=container, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, left=self.icon.width + 16, padRight=12, text=self.text, color=self.labelColor)
        self.width = container.GetAbsoluteSize()[0]

    def _pulse_glow(self):
        animations.MorphScalar(self.bg, 'glowBrightness', duration=3, startVal=self.bg.glowBrightness, endVal=1.2, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_BOUNCE)

    def OnMouseEnter(self, *args):
        super(UpgradeIconButton, self).OnMouseEnter(*args)
        self.on_mouse_enter()
        animations.SpColorMorphTo(self.icon, self.icon.GetRGBA(), Color.BLACK, duration=0.3)

    def OnMouseExit(self, *args):
        super(UpgradeIconButton, self).OnMouseExit(*args)
        self.on_mouse_exit()
        animations.SpColorMorphTo(self.icon, self.icon.GetRGBA(), self.labelColor, duration=0.15)
        if self._animate:
            self._pulse_glow()
