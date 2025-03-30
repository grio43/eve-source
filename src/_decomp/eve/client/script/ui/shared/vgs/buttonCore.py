#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\vgs\buttonCore.py
import math
import trinity
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveHeaderSmall
from eve.client.script.ui.util.uiComponents import Component, ButtonEffect

@Component(ButtonEffect(audioOnEntry=uiconst.SOUND_BUTTON_HOVER, audioOnClick=uiconst.SOUND_BUTTON_CLICK))

class ButtonCore(ContainerAutoSize):
    default_alignMode = uiconst.TOPLEFT
    default_color = (0.4, 0.4, 0.4, 1.0)
    default_contentSpacing = 3
    default_iconSize = (16, 16)
    default_iconColor = (1.0, 1.0, 1.0, 1.0)
    default_labelClass = EveHeaderSmall
    default_labelColor = (1.0, 1.0, 1.0, 1.0)
    default_labelShadow = False
    default_labelShadowColor = (0.0, 0.0, 0.0, 0.25)
    default_labelTop = 0
    default_padding = (4, 4, 4, 4)
    default_state = uiconst.UI_NORMAL
    default_text = None
    default_texturePath = None

    def ApplyAttributes(self, attributes):
        self.onClick = attributes.get('onClick', None)
        color = attributes.pop('color', self.default_color)
        contentSpacing = attributes.pop('contentSpacing', self.default_contentSpacing)
        iconSize = attributes.pop('iconSize', self.default_iconSize)
        iconColor = attributes.pop('iconColor', self.default_iconColor)
        labelClass = attributes.pop('labelClass', self.default_labelClass)
        labelColor = attributes.pop('labelColor', self.default_labelColor)
        labelShadow = attributes.pop('labelShadow', self.default_labelShadow)
        labelShadowColor = attributes.pop('labelShadowColor', self.default_labelShadowColor)
        labelTop = attributes.pop('labelTop', self.default_labelTop)
        padding = attributes.pop('padding', self.default_padding)
        attributes['padding'] = None
        text = attributes.pop('text', self.default_text)
        texturePath = attributes.pop('texturePath', self.default_texturePath)
        iconWidth, iconHeight = iconSize
        padLeft, padTop, padRight, padBottom = padding
        super(ButtonCore, self).ApplyAttributes(attributes)
        Fill(bgParent=self, align=uiconst.TOALL, padding=(1, 1, 1, 1), color=color)
        GradientSprite(bgParent=self, align=uiconst.TOALL, rgbData=((0.0, (0.9, 0.9, 0.9)), (0.5, (0.2, 0.2, 0.2)), (1.0, (0.9, 0.9, 0.9))), alphaData=((0.0, 0.3), (1.0, 0.3)), rotation=-math.pi / 4)
        Fill(bgParent=self, align=uiconst.TOALL, color=color)
        if texturePath:
            iconCont = Container(parent=self, align=uiconst.TOPLEFT, padding=(padLeft,
             padTop,
             contentSpacing if text else padRight,
             padBottom), height=iconHeight, width=iconWidth)
            Sprite(parent=iconCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath=texturePath, height=iconHeight, width=iconWidth, color=iconColor)
        if text:
            if texturePath:
                left = padLeft + iconWidth
                labelPadding = (contentSpacing,
                 padTop,
                 padRight,
                 padBottom)
                top = labelTop
            else:
                left = 0
                labelPadding = padding
                top = 0
            labelCont = ContainerAutoSize(parent=self, align=uiconst.TOPLEFT, alignMode=uiconst.TOPLEFT, left=left, top=top)
            labelClass(parent=labelCont, align=uiconst.TOPLEFT, padding=labelPadding, text=text, color=labelColor)
            if labelShadow:
                shadow = labelClass(parent=labelCont, align=uiconst.TOPLEFT, padding=labelPadding, text=text, color=labelShadowColor)
                shadow.renderObject.spriteEffect = trinity.TR2_SFX_BLUR
                Frame(parent=labelCont, align=uiconst.TOALL, texturePath='res:/UI/Texture/Vgs/radialShadow.png', cornerSize=8, color=labelShadowColor, opacity=labelShadowColor[3] * 0.5)
        self.SetSizeAutomatically()

    def OnClick(self, *args):
        if self.disabled:
            return
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        self.disabled = True
        uthread.new(self._OnClickThread)

    def _OnClickThread(self):
        try:
            if callable(self.onClick):
                self.onClick()
        finally:
            self.disabled = False

    def AnimShow(self):
        self.Show()
        animations.FadeTo(self, duration=0.4)
