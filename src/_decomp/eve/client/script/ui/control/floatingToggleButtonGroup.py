#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\floatingToggleButtonGroup.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import TextColor, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.control.toggleButtonGroupButton import BaseToggleButtonGroupButton
OPACITY_LABEL_IDLE = TextColor.NORMAL.opacity
OPACITY_LABEL_HOVER = TextColor.HIGHLIGHT.opacity
OPACITY_LABEL_SELECTED = TextColor.HIGHLIGHT.opacity
OPACITY_GLOW_IDLE = 0.0
OPACITY_GLOW_HOVER = 0.5
OPACITY_GLOW_SELECTED = 0.8
OPACITY_LINE_IDLE = 0.2
OPACITY_LINE_HOVER = 0.3
OPACITY_LINE_SELECTED = 1.0

class FloatingToggleButtonGroupButton(BaseToggleButtonGroupButton):
    default_padRight = 4
    default_iconSize = 16

    def ApplyAttributes(self, attributes):
        super(FloatingToggleButtonGroupButton, self).ApplyAttributes(attributes)
        label = attributes.label
        labelLeft = 10
        if self.iconPath:
            self.icon = Sprite(parent=self, texturePath=self.iconPath, align=uiconst.TOPLEFT, pos=(labelLeft,
             0,
             self.iconSize,
             self.iconSize), state=uiconst.UI_DISABLED)
            labelLeft += self.iconSize + 6
        self.label = EveLabelLarge(text=label, parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, left=labelLeft, opacity=OPACITY_LABEL_IDLE, autoFadeSides=True)
        lineCont = Container(parent=self, align=uiconst.TOBOTTOM, height=4)
        self.line = Fill(parent=lineCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=eveThemeColor.THEME_ACCENT, opacity=OPACITY_LINE_IDLE, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=OPACITY_GLOW_IDLE)

    def OnColorThemeChanged(self):
        self.line.rgb = eveThemeColor.THEME_ACCENT.rgb

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        animations.FadeTo(self.label, self.label.opacity, OPACITY_LABEL_HOVER, duration=0.1)
        if not self.isSelected:
            animations.MorphScalar(self.line, 'glowBrightness', self.line.glowBrightness, OPACITY_GLOW_HOVER, duration=0.1)

    def OnMouseExit(self, *args):
        if not self.isSelected:
            animations.FadeTo(self.label, self.label.opacity, OPACITY_LABEL_IDLE, duration=0.1)
            animations.MorphScalar(self.line, 'glowBrightness', self.line.glowBrightness, OPACITY_LINE_HOVER, duration=0.1)

    def SetSelected(self, animate = True):
        super(FloatingToggleButtonGroupButton, self).SetSelected(animate)
        animations.FadeTo(self.label, self.label.opacity, OPACITY_LABEL_SELECTED, duration=0.1)
        animations.MorphScalar(self.line, 'glowBrightness', self.line.glowBrightness, OPACITY_GLOW_SELECTED, duration=0.1)
        animations.FadeTo(self.line, self.line.opacity, OPACITY_GLOW_SELECTED, duration=0.1)

    def SetDeselected(self, animate = True):
        super(FloatingToggleButtonGroupButton, self).SetDeselected(animate)
        animations.FadeTo(self.label, self.label.opacity, OPACITY_LABEL_IDLE, duration=0.1)
        animations.MorphScalar(self.line, 'glowBrightness', self.line.glowBrightness, OPACITY_GLOW_IDLE, duration=0.1)
        animations.FadeTo(self.line, self.line.opacity, OPACITY_LINE_IDLE, duration=0.1)


class FloatingToggleButtonGroup(ToggleButtonGroup):
    default_btnClass = FloatingToggleButtonGroupButton
    default_height = 32
