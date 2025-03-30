#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\toggleButtonGroupCircular.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.control.toggleButtonGroupButton import BaseToggleButtonGroupButton

class ToggleButtonGroupButtonCircular(BaseToggleButtonGroupButton):
    default_iconSize = 32
    default_btnSize = 48
    default_label = None

    def ApplyAttributes(self, attributes):
        super(ToggleButtonGroupButtonCircular, self).ApplyAttributes(attributes)
        self.btnSize = attributes.Get('btnSize', self.default_btnSize)
        if self.iconPath:
            self.icon = Sprite(name='icon', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, color=eveColor.WHITE, texturePath=self.iconPath, pos=(0,
             0,
             self.iconSize,
             self.iconSize))
        elif self.label:
            self.icon = EveLabelLarge(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, text=self.label)
        selectedFrameSize = 2 * self.btnSize
        self.selectedFrame = Sprite(name='selectedFrame', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0,
         0,
         selectedFrameSize,
         selectedFrameSize), texturePath='res:/UI/Texture/Classes/SkillPlan/factionButtons/bgGlow.png', color=eveColor.WHITE, opacity=0.0)
        self.bgFill = Sprite(name='bg', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/SkillPlan/factionButtons/bgFill.png', color=eveColor.WHITE, pos=(0,
         0,
         self.btnSize,
         self.btnSize), opacity=0.0)
        self.bgStroke = Sprite(name='bgStroke', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/SkillPlan/factionButtons/bgStroke.png', pos=(0,
         0,
         self.btnSize,
         self.btnSize), opacity=0.1)

    def SetSelected(self, animate = True):
        super(ToggleButtonGroupButtonCircular, self).SetSelected(animate)
        if animate:
            duration = 0.15
            animations.FadeTo(self.selectedFrame, self.selectedFrame.opacity, 1.0, duration=duration)
            animations.FadeTo(self.bgFill, self.bgFill.opacity, 1.0, duration=duration)
            animations.SpColorMorphTo(self.icon, self.icon.GetRGBA(), Color.BLACK, duration=duration)
        else:
            self.bgFill.opacity = 1.0
            self.selectedFrame.opacity = 1.0
            self.icon.SetRGBA(*Color.BLACK)
        if self.label:
            self.icon.shadowOffset = (0, 0)

    def SetDeselected(self, animate = True):
        super(ToggleButtonGroupButtonCircular, self).SetDeselected(animate)
        if animate:
            duration = 0.15
            animations.FadeTo(self.selectedFrame, self.selectedFrame.opacity, 0.0, duration=duration)
            animations.FadeTo(self.bgFill, self.bgFill.opacity, 0.0, duration=duration)
            animations.SpColorMorphTo(self.icon, self.icon.GetRGBA(), eveColor.WHITE, duration=duration)
        else:
            self.selectedFrame.opacity = 0.0
            self.bgFill.opacity = 0.0
            self.icon.SetRGBA(*eveColor.WHITE)
        if self.label:
            self.icon.shadowOffset = EveLabelLarge.default_shadowOffset

    def OnMouseEnter(self, *args):
        if not self.isSelected:
            PlaySound(uiconst.SOUND_BUTTON_HOVER)
            animations.FadeTo(self.bgFill, self.bgFill.opacity, 0.5, duration=0.15)

    def OnMouseExit(self, *args):
        duration = 0.1
        if not self.isSelected:
            animations.FadeTo(self.bgFill, self.bgFill.opacity, 0.0, duration=duration)


class ToggleButtonGroupCircular(ToggleButtonGroup):
    default_btnClass = ToggleButtonGroupButtonCircular
    default_height = ToggleButtonGroupButtonCircular.default_btnSize

    def AddButton(self, btnID, label = '', panel = None, iconPath = None, iconSize = None, hint = None, isDisabled = False, colorSelected = None, btnClass = None, **kw):
        button = super(ToggleButtonGroupCircular, self).AddButton(btnID, label, panel, iconPath, iconSize, hint, isDisabled, colorSelected, btnClass, **kw)
        self.SetWidthAutomatically()
        return button

    def SetWidthAutomatically(self):
        if self.align != uiconst.TOALL:
            self.width = sum([ btn.btnSize for btn in self.buttons ]) + 10 * len(self.buttons)
