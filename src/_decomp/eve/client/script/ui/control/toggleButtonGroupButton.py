#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\toggleButtonGroupButton.py
import trinity
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import Density, TextColor, uiconst
from carbonui.button import styling
from carbonui.control.button import ButtonUnderlay, OPACITY_LABEL_HOVER, OPACITY_LABEL_IDLE
from carbonui.fontconst import EVE_SMALL_FONTSIZE
from carbonui.loggers.buttonLogger import log_button_clicked
from carbonui.primitives.base import ReverseScaleDpi
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.themeColored import LabelThemeColored
from eve.client.script.ui.control.toggleButtonUnderlay import FrameType, ToggleButtonUnderlay

class BaseToggleButtonGroupButton(Container):
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOLEFT_PROP
    default_analyticID = None
    default_iconPath = None
    default_iconSize = None
    default_label = None
    default_underlayClass = ToggleButtonUnderlay
    AUTO_HEIGHT_ENABLED_BY_DEFAULT = False

    def __init__(self, colorSelected = None, density = Density.NORMAL, **kwargs):
        self._density = density
        self.colorSelected = colorSelected
        super(BaseToggleButtonGroupButton, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        super(BaseToggleButtonGroupButton, self).ApplyAttributes(attributes)
        self.btnID = attributes.Get('btnID', None)
        self.panel = attributes.Get('panel', None)
        self.isDisabled = attributes.Get('isDisabled', False)
        self.analyticID = attributes.Get('analyticID', self.default_analyticID)
        self.underlayClass = attributes.Get('underlayClass', self.default_underlayClass)
        self.controller = attributes.controller
        self.iconPath = attributes.iconPath or self.default_iconPath
        self.iconSize = attributes.iconSize or self.default_iconSize
        self.label = attributes.label or self.default_label
        self.isSelected = False

    @property
    def density(self):
        return self._density

    @density.setter
    def density(self, value):
        if self._density != value:
            self._density = value
            self.FlagAlignmentDirty('{}.density'.format(self.__class__.__name__))

    def GetAutoHeight(self):
        return None

    def SetSelected(self, animate = True):
        self.isSelected = True

    def SetDeselected(self, animate = True):
        self.isSelected = False

    def IsSelected(self):
        return self.isSelected

    def OnClick(self, *args):
        if self.isDisabled:
            return
        if self.IsSelected():
            if self.controller.IsOptional():
                self.controller.DeselectAll()
        else:
            self.controller.Select(self, playSound=True)
            log_button_clicked(self)

    def OnButtonAdded(self):
        pass


class LegacyToggleButtonGroupButton(BaseToggleButtonGroupButton):
    OPACITY_SELECTED = 1.0
    OPACITY_HOVER = 0.125
    TEXT_TOPMARGIN = 4
    default_padRight = 1
    default_iconSize = 32
    default_colorSelected = None
    default_iconOpacity = 1.0
    default_showBg = True
    default_fontSize = EVE_SMALL_FONTSIZE

    def ApplyAttributes(self, attributes):
        super(LegacyToggleButtonGroupButton, self).ApplyAttributes(attributes)
        self.colorSelected = attributes.Get('colorSelected', self.default_colorSelected)
        label = attributes.Get('label', None)
        self.fontSize = attributes.Get('fontSize', self.default_fontSize)
        iconPath = attributes.Get('iconPath', None)
        iconSize = attributes.Get('iconSize', None)
        iconSize = iconSize or self.default_iconSize
        iconOpacity = attributes.get('iconOpacity', self.default_iconOpacity)
        self.showBg = attributes.Get('showBg', self.default_showBg)
        self.ConstructLayout(iconOpacity, iconPath, iconSize, label)
        self.selectedBG = ButtonUnderlay(parent=self)
        if not self.showBg:
            self.selectedBG.display = False
        if self.isDisabled:
            self.SetDisabled()

    def ConstructLayout(self, iconOpacity, iconPath, iconSize, label):
        if iconPath:
            self.AddIcon(self, iconOpacity, iconPath, iconSize)
            self.label = None
        else:
            clipper = Container(parent=self, clipChildren=True, padding=(2, 0, 2, 0))
            self.AddLabel(clipper, label)
            self.icon = None

    def AddIcon(self, parent, iconOpacity, iconPath, iconSize):
        self.icon = GlowSprite(parent=parent, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=iconSize, height=iconSize, texturePath=iconPath, iconOpacity=iconOpacity, color=Color.GRAY6)

    def AddLabel(self, parent, label, maxWidth = None):
        self.label = LabelThemeColored(text=label, parent=parent, align=uiconst.CENTER, fontsize=self.fontSize, maxWidth=maxWidth, autoFadeSides=20)

    def GetAutoHeight(self):
        if self.label:
            return ReverseScaleDpi(self.label.textheight) + self.TEXT_TOPMARGIN * 2
        if self.icon:
            return self.icon.height
        return 0

    def SetDisabled(self):
        self.isDisabled = True
        if self.icon:
            self.icon.opacity = 0.1
        if self.label:
            self.label.opacity = 0.1
        if self.showBg:
            self.selectedBG.SetDisabled()

    def SetEnabled(self):
        self.isDisabled = False
        if self.showBg:
            self.selectedBG.SetEnabled()

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        if not self.isSelected and not self.isDisabled:
            self.selectedBG.OnMouseEnter()
            if self.icon:
                self.icon.OnMouseEnter()
            else:
                uicore.animations.FadeTo(self.label, self.label.opacity, OPACITY_LABEL_HOVER, duration=uiconst.TIME_ENTRY)

    def OnMouseExit(self, *args):
        if self.isDisabled:
            return
        if not self.isSelected:
            self.selectedBG.OnMouseExit()
        if self.icon:
            self.icon.OnMouseExit()
        elif not self.isSelected:
            uicore.animations.FadeTo(self.label, self.label.opacity, OPACITY_LABEL_IDLE, duration=uiconst.TIME_EXIT)

    def OnMouseDown(self, *args):
        if self.isDisabled:
            return
        if self.icon:
            self.icon.OnMouseDown()
        self.selectedBG.OnMouseDown()

    def OnMouseUp(self, *args):
        if self.isDisabled:
            return
        if self.icon:
            self.icon.OnMouseUp()
        self.selectedBG.OnMouseUp()

    def SetSelected(self, animate = True):
        super(LegacyToggleButtonGroupButton, self).SetSelected(animate)
        if not self.showBg:
            self.selectedBG.display = True
        self.selectedBG.Select()
        if self.label:
            self.label.opacity = OPACITY_LABEL_HOVER
        if self.icon:
            self.icon.OnMouseExit()

    def SetDeselected(self, animate = True):
        super(LegacyToggleButtonGroupButton, self).SetDeselected(animate)
        if self.label:
            self.label.opacity = OPACITY_LABEL_IDLE
        if self.isDisabled:
            return
        if not self.showBg:
            self.selectedBG.display = False
        self.selectedBG.Deselect()


class ToggleButtonGroupButton(BaseToggleButtonGroupButton):
    _hovered = False
    _label = None
    _pressed = False
    _underlay = None
    AUTO_HEIGHT_ENABLED_BY_DEFAULT = True

    def __init__(self, **kwargs):
        super(ToggleButtonGroupButton, self).__init__(**kwargs)
        self._layout()

    def GetAutoHeight(self):
        return styling.get_height(self._density)

    def _layout(self):
        self._label = EveLabelMedium(parent=Container(parent=self, align=uiconst.TOALL, padding=(8, 0, 8, 0)), text=self.label, align=uiconst.CENTER, autoFadeSides=8, shadowSpriteEffect=trinity.TR2_SFX_GLOW, color=self._get_label_color())
        self._underlay = self.underlayClass(bgParent=self, selected=self.isSelected, enabled=not self.isDisabled, selected_color_override=self.colorSelected)
        if self.isDisabled:
            self.SetDisabled()

    def OnButtonAdded(self):
        if not self.parent:
            return
        idx = self.GetOrder()
        is_first = idx == 0
        is_last = idx == len(self.parent.children) - 1
        if self._underlay:
            if is_first:
                self._underlay.frame_type = FrameType.LEFT
            elif is_last:
                self._underlay.frame_type = FrameType.RIGHT
            else:
                self._underlay.frame_type = FrameType.MIDDLE
        if not is_first:
            self.padLeft = 2
        if not is_last:
            self.padRight = 2

    def SetDisabled(self):
        self.isDisabled = True
        if self._underlay:
            self._underlay.enabled = False
        self._update_label_color(duration=uiconst.TIME_EXIT)

    def SetEnabled(self):
        self.isDisabled = False
        if self._underlay:
            self._underlay.enabled = True
        self._update_label_color(duration=uiconst.TIME_ENTRY)

    def OnMouseEnter(self, *args):
        self._hovered = True
        if self._underlay:
            self._underlay.hovered = True
        self._update_label_color(duration=uiconst.TIME_ENTRY)
        if not self.isSelected and not self.isDisabled:
            PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def OnMouseExit(self, *args):
        self._hovered = False
        if self._underlay:
            self._underlay.hovered = False
        self._update_label_color(duration=uiconst.TIME_EXIT)

    def OnMouseDown(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self._pressed = True
            if self._underlay:
                self._underlay.pressed = True
            self._update_label_color(duration=uiconst.TIME_MOUSEDOWN)

    def OnMouseUp(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self._pressed = False
            if self._underlay:
                self._underlay.pressed = False
            self._update_label_color(duration=uiconst.TIME_MOUSEUP)

    def SetSelected(self, animate = True):
        super(ToggleButtonGroupButton, self).SetSelected(animate)
        if self._underlay:
            self._underlay.set_selected(True, animate)
        self._update_label_color(duration=uiconst.TIME_SELECT)

    def SetDeselected(self, animate = True):
        super(ToggleButtonGroupButton, self).SetDeselected(animate)
        if self._underlay:
            self._underlay.set_selected(False, animate)
        self._update_label_color(duration=uiconst.TIME_SELECT)

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        result = super(ToggleButtonGroupButton, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
        if self._label:
            label_clipper_width, _ = self._label.parent.GetCurrentAbsoluteSize()
            if self._label.width > label_clipper_width:
                self._label.align = uiconst.CENTERLEFT
            else:
                self._label.align = uiconst.CENTER
            if self._childrenAlignmentDirty:
                super(ToggleButtonGroupButton, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly=True)
        return result

    def _get_label_color(self):
        if self.isDisabled:
            return TextColor.DISABLED
        elif self.isSelected:
            return TextColor.HIGHLIGHT
        elif self._pressed:
            return eveColor.BLACK
        elif self._hovered:
            return TextColor.HIGHLIGHT
        else:
            return TextColor.NORMAL

    def _update_label_color(self, duration):
        if self._label:
            if duration > 0.0:
                animations.SpColorMorphTo(self._label, endColor=self._get_label_color(), duration=duration)
            else:
                animations.StopAnimation(self._label, 'color')
                self._label.color = self._get_label_color()


class ToggleButtonGroupButtonIcon(BaseToggleButtonGroupButton):
    _icon = None
    _pressed = False
    _underlay = None

    def __init__(self, **kwargs):
        super(ToggleButtonGroupButtonIcon, self).__init__(**kwargs)
        self._layout()
        if self.isDisabled:
            self.SetDisabled()

    def _layout(self):
        self._icon = Sprite(parent=self, align=uiconst.CENTER, width=self.iconSize, height=self.iconSize, state=uiconst.UI_DISABLED, texturePath=self.iconPath, color=self._get_icon_color())
        self._underlay = self.underlayClass(bgParent=self, selected=self.isSelected, enabled=not self.isDisabled, selected_color_override=self.colorSelected)

    def GetAutoHeight(self):
        return self.iconSize + 8

    def OnButtonAdded(self):
        idx = self.GetOrder()
        is_first = idx == 0
        is_last = idx == len(self.parent.children) - 1
        if self._underlay:
            if is_first:
                self._underlay.frame_type = FrameType.LEFT
            elif is_last:
                self._underlay.frame_type = FrameType.RIGHT
            else:
                self._underlay.frame_type = FrameType.MIDDLE
        if not is_first:
            self.padLeft = 2
        if not is_last:
            self.padRight = 2

    def SetDisabled(self):
        self.isDisabled = True
        if self._underlay:
            self._underlay.enabled = False
        self._update_icon_color(duration=uiconst.TIME_SELECT)

    def SetEnabled(self):
        self.isDisabled = False
        if self._underlay:
            self._underlay.enabled = True
        self._update_icon_color(duration=uiconst.TIME_DESELECT)

    def OnMouseEnter(self, *args):
        if self._underlay:
            self._underlay.hovered = True
        if not self.isSelected and not self.isDisabled:
            PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def OnMouseExit(self, *args):
        if self._underlay:
            self._underlay.hovered = False

    def OnMouseDown(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self._pressed = True
            if self._underlay:
                self._underlay.pressed = True
            self._update_icon_color(duration=uiconst.TIME_MOUSEDOWN)

    def OnMouseUp(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self._pressed = False
            if self._underlay:
                self._underlay.pressed = False
            self._update_icon_color(duration=uiconst.TIME_MOUSEUP)

    def SetSelected(self, animate = True):
        super(ToggleButtonGroupButtonIcon, self).SetSelected(animate)
        if self._underlay:
            self._underlay.set_selected(True, animate)
        self._update_icon_color(duration=uiconst.TIME_SELECT)

    def SetDeselected(self, animate = True):
        super(ToggleButtonGroupButtonIcon, self).SetDeselected(animate)
        if self._underlay:
            self._underlay.set_selected(False, animate)
        self._update_icon_color(duration=uiconst.TIME_DESELECT)

    def _get_icon_color(self):
        if self.isDisabled:
            return TextColor.DISABLED
        elif self.isSelected:
            return eveColor.WHITE
        elif self._pressed:
            return eveColor.BLACK
        else:
            return eveColor.WHITE

    def _update_icon_color(self, duration):
        if self._icon:
            if duration > 0.0:
                animations.SpColorMorphTo(self._icon, endColor=self._get_icon_color(), duration=duration)
            else:
                animations.StopAnimation(self._icon, 'color')
                self._icon.color = self._get_icon_color()
