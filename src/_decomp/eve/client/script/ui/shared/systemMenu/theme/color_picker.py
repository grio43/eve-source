#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\theme\color_picker.py
from __future__ import division
import math
import carbonui
import localization
import mathext
import signals
from carbonui import Align, Axis, Density, uiconst
from carbonui.button import styling
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.decorative.inputUnderlay import InputUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.tooltips import TooltipPersistentPanel
from eve.client.script.ui.shared.systemMenu.theme import theme_util

class ColorField(Container):
    _color_fill = None
    _color_cont = None

    def __init__(self, color = carbonui.Color.from_hex('#000000'), density = Density.NORMAL, width = 160, on_color_changed = None, brightness_range = (0.0, 1.0), saturation_range = (0.0, 1.0), ignore_color_blind_mode = False, **kwargs):
        self._color = color
        self._brightness_range = brightness_range
        self._saturation_range = saturation_range
        self._density = density
        self._on_color_changed = signals.Signal()
        self._ignore_color_blind_mode = ignore_color_blind_mode
        super(ColorField, self).__init__(setvalue=self._get_color_text(), width=width, height=self._get_height(), **kwargs)
        self._layout()
        if on_color_changed:
            self._on_color_changed.connect(on_color_changed)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        value = carbonui.Color.from_any(value)
        if self._color != value:
            self._color = value
            self._update_field_text()
            self._update_color_fill()
            self._on_color_changed(self)

    def _layout(self):
        self._color_cont = Container(parent=self, align=Align.TOLEFT, width=self._get_height(), clipChildren=True)
        self._color_fill = Fill(parent=self._color_cont, align=Align.TOALL, padding=(1, 1, 0, 1), state=uiconst.UI_NORMAL, color=self._color, ignoreColorBlindMode=self._ignore_color_blind_mode, hint=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/ColorPickerEditColorHint'))
        self._color_fill.OnClick = self._on_color_fill_clicked
        InputUnderlay(parent=self._color_cont, align=Align.TOALL, padRight=-1)
        self._text_field = SingleLineEditText(parent=self, align=Align.TOTOP, setvalue=self._get_color_text(), autoselect=True, OnChange=self._on_change, OnFocusLost=self._on_focus_lost)
        self._text_field.SetHistoryVisibility(False)

    def _get_color_text(self):
        return self._color.hex_rgb.upper()

    def _get_height(self):
        return styling.get_height(self._density)

    def _update_color_fill(self):
        if self._color_fill:
            self._color_fill.SetRGB(*self.color.rgb)

    def _update_field_text(self):
        focused = uicore.registry.GetFocus() == self._text_field
        if not focused:
            self._text_field.SetValue(self._get_color_text())

    def _on_color_fill_clicked(self, *args):
        show_color_picker_popover(owner=self._color_fill, color=self.color, on_color_changed=self._on_popover_picker_color_changed, brightness_range=self._brightness_range, saturation_range=self._saturation_range, ignore_color_blind_mode=self._ignore_color_blind_mode)

    def _on_popover_picker_color_changed(self, picker):
        self.color = picker.color

    def _on_focus_lost(self, input):
        try:
            color = carbonui.Color.from_hex(self._text_field.GetValue().strip())
            color = theme_util.get_with_capped_brightness(color, *self._brightness_range)
        except Exception:
            pass
        else:
            self.color = color

        self._update_field_text()

    def _on_change(self, text):
        try:
            color = carbonui.Color.from_hex(self._text_field.GetValue().strip())
            color = theme_util.get_with_capped_brightness(color, *self._brightness_range)
        except Exception:
            pass
        else:
            self.color = color


class ColorPickerPopoverArguments(object):

    def __init__(self, color, on_color_changed = None, brightness_range = (0.0, 1.0), saturation_range = (0.0, 1.0), ignore_color_blind_mode = False):
        self.brightness_range = brightness_range
        self.saturation_range = saturation_range
        self.color = color
        self.on_color_changed = on_color_changed
        self.ignore_color_blind_mode = ignore_color_blind_mode


def show_color_picker_popover(owner, color, on_color_changed = None, brightness_range = (0.0, 1.0), saturation_range = (0.0, 1.0), ignore_color_blind_mode = False):
    arguments = ColorPickerPopoverArguments(color=color, on_color_changed=on_color_changed, brightness_range=brightness_range, saturation_range=saturation_range, ignore_color_blind_mode=ignore_color_blind_mode)
    return uicore.uilib.tooltipHandler.LoadPersistentTooltip(owner=owner, customTooltipClass=ColorFieldPickerPopover, loadArguments=(arguments,), parent=uicore.layer.hint)


class ColorFieldPickerPopover(TooltipPersistentPanel):
    default_pointerDirection = uiconst.POINT_BOTTOM_2
    default_columns = 1
    default_state = uiconst.UI_NORMAL
    default_margin = 16
    isTopLevelWindow = True
    _picker = None

    def __init__(self, **kwargs):
        self.on_color_changed = signals.Signal()
        super(ColorFieldPickerPopover, self).__init__(**kwargs)
        self.pickState = uiconst.TR2_SPS_ON
        uicore.registry.SetFocus(self)
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self._on_global_mouse_down)

    @property
    def color(self):
        return self._picker.color

    def LoadTooltip(self, arguments):
        ColorPicker(parent=self, align=Align.TOPLEFT, color=arguments.color, on_color_changed=arguments.on_color_changed, brightness_range=arguments.brightness_range, saturation_range=arguments.saturation_range, ignore_color_blind_mode=arguments.ignore_color_blind_mode)

    def _on_global_mouse_down(self, *args):
        if uicore.uilib.mouseOver is self or uicore.uilib.mouseOver.IsUnder(self):
            return True
        else:
            self.Close()
            return False


class ColorPicker(Container):

    def __init__(self, width = 236, height = 200, color = carbonui.Color.from_hsb(h=0.0, s=0.0, b=1.0), on_color_changed = None, brightness_range = (0.0, 1.0), saturation_range = (0.0, 1.0), ignore_color_blind_mode = False, **kwargs):
        self._hue = color.hue
        self._saturation = color.saturation
        self._brightness = color.brightness
        self.on_color_changed = signals.Signal()
        super(ColorPicker, self).__init__(width=width, height=height, **kwargs)
        HueSlider(parent=self, align=Align.TORIGHT, width=20, padLeft=16, hue=self._hue, on_hue_changed=self._on_hue_changed, ignore_color_blind_mode=ignore_color_blind_mode)
        self._picker = Picker2D(parent=self, align=Align.TOALL, position=(self._saturation, 1.0 - self._brightness), on_position_changed=self._on_position_changed, brightness_range=brightness_range, saturation_range=saturation_range, ignore_color_blind_mode=ignore_color_blind_mode)
        self._gradient = ColorSaturationBrightnessGradient(parent=self, align=Align.TOALL, hue=self._hue, ignore_color_blind_mode=ignore_color_blind_mode)
        if on_color_changed is not None:
            self.on_color_changed.connect(on_color_changed)

    @property
    def color(self):
        return carbonui.Color.from_hsb(h=self._hue, s=self._saturation, b=self._brightness)

    @color.setter
    def color(self, value):
        if self.color != value:
            self._hue = value.hue
            self._saturation = value.saturation
            self._brightness = value.brightness
            self._update_color()
            self.on_color_changed(self)

    def _update_color(self):
        self._gradient.hue = self._hue

    def _on_hue_changed(self, picker):
        self._hue = picker.hue
        self._update_color()
        self.on_color_changed(self)

    def _on_position_changed(self, picker):
        x, y = picker.position
        saturation = x
        brightness = 1.0 - y
        if not mathext.is_close(saturation, self._saturation) or not mathext.is_close(brightness, self._brightness):
            self._saturation = saturation
            self._brightness = brightness
            self._update_color()
            self.on_color_changed(self)


class HueSlider(Container):
    _dragging = False
    _on_hue_changed = None
    _STEPS = 10
    _INDICATOR_THICKNESS = 2

    def __init__(self, hue = 0.0, orientation = Axis.VERTICAL, enabled = True, on_hue_changed = None, state = uiconst.UI_NORMAL, ignore_color_blind_mode = False, **kwargs):
        self._enabled = enabled
        self._hue = hue
        self._orientation = orientation
        super(HueSlider, self).__init__(state=state, **kwargs)
        self._indicator = Fill(parent=self, align=Align.TOTOP_NOPUSH if self._orientation == Axis.VERTICAL else Align.TOLEFT_NOPUSH, pos=self._get_indicator_position(), color=carbonui.Color.from_rgba(1.0, 1.0, 1.0, 1.0))
        GradientSprite(parent=self, align=Align.TOALL, state=uiconst.UI_DISABLED, rgbData=[ (float(i) / self._STEPS, carbonui.Color.from_hsb(h=float(i) / self._STEPS, s=1.0, b=1.0).rgb) for i in range(self._STEPS + 1) ], rotation=0.0 if self._orientation == Axis.HORIZONTAL else -math.pi / 2.0, ignoreColorBlindMode=ignore_color_blind_mode)
        if on_hue_changed:
            self.on_hue_changed.connect(on_hue_changed)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if self._enabled != value:
            self._enabled = bool(value)
            if self._dragging:
                self._stop_dragging()

    @property
    def hue(self):
        return self._hue

    @hue.setter
    def hue(self, value):
        value = mathext.clamp(float(value), 0.0, 1.0)
        if not mathext.is_close(self._hue, value):
            self._hue = value
            self._update_indicator_position()
            if self._on_hue_changed is not None:
                self._on_hue_changed(self)

    @property
    def on_hue_changed(self):
        if self._on_hue_changed is None:
            self._on_hue_changed = signals.Signal('{}.on_hue_changed'.format(self.__class__.__name__))
        return self._on_hue_changed

    def _get_indicator_position(self):
        width, height = self.GetCurrentAbsoluteSize()
        if self._orientation == Axis.VERTICAL:
            return (0,
             self._hue * (height - self._INDICATOR_THICKNESS),
             0,
             self._INDICATOR_THICKNESS)
        else:
            return (self._hue * (width - self._INDICATOR_THICKNESS),
             0,
             self._INDICATOR_THICKNESS,
             0)

    def _update_indicator_position(self):
        if self._indicator:
            self._indicator.pos = self._get_indicator_position()

    def _stop_dragging(self):
        if self._dragging:
            self._dragging = False

    def _pick_at_mouse(self):
        left, top = self.GetCurrentAbsolutePosition()
        width, height = self.GetCurrentAbsoluteSize()
        if self._orientation == Axis.HORIZONTAL:
            self.hue = mathext.clamp((uicore.uilib.x - left) / width, 0.0, 1.0)
        else:
            self.hue = mathext.clamp((uicore.uilib.y - top) / height, 0.0, 1.0)

    def OnMouseDown(self, button, *args):
        if not self._dragging and button == uiconst.MOUSELEFT and self.enabled:
            self._dragging = True
            self._pick_at_mouse()

    def OnMouseMove(self, *args):
        if self._dragging:
            self._pick_at_mouse()

    def OnMouseUp(self, button, *args):
        if self._dragging and button == uiconst.MOUSELEFT:
            self._pick_at_mouse()
            self._stop_dragging()

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        result = super(HueSlider, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
        _, _, _, _, size_changed = result
        if size_changed:
            self._update_indicator_position()
        return result


class HatchesSprite(Sprite):
    default_texturePath = 'res:/UI/Texture/Classes/Industry/Output/hatchPattern.png'
    default_tileX = True
    default_tileY = True
    default_state = uiconst.UI_DISABLED
    default_color = eveColor.BLACK
    default_opacity = 0.5


class Picker2D(Container):
    _dragging = False
    _on_position_changed = None

    def __init__(self, position = (0.0, 0.0), indicator = None, indicator_hotspot = (0.5, 0.5), enabled = True, on_position_changed = None, state = uiconst.UI_NORMAL, cursor = uiconst.UICORSOR_FINGER, brightness_range = (0.0, 1.0), saturation_range = (0.0, 1.0), **kwargs):
        self._enabled = enabled
        self._position = position
        self._indicator = indicator
        self._indicator_hotspot = indicator_hotspot
        self._brightness_range = brightness_range
        self._saturation_range = saturation_range
        super(Picker2D, self).__init__(state=state, cursor=cursor, **kwargs)
        if self._indicator is None:
            self._indicator = CircleIndicator()
        self._indicator.align = Align.TOPLEFT
        self._indicator.SetParent(self)
        self._check_construct_limitation_hatches()
        if on_position_changed:
            self.on_position_changed.connect(on_position_changed)

    def _check_construct_limitation_hatches(self):
        x_min, x_max = self._saturation_range
        y_min, y_max = 1.0 - self._brightness_range[1], 1.0 - self._brightness_range[0]
        hatchesCont = Container(name='hatcesCont', parent=self, state=uiconst.UI_DISABLED)
        if x_min != 0:
            HatchesSprite(parent=hatchesCont, align=uiconst.TOLEFT_PROP, width=x_min)
        if x_max != 1.0:
            HatchesSprite(parent=hatchesCont, align=uiconst.TORIGHT_PROP, width=1.0 - x_max)
        if y_min != 0:
            HatchesSprite(parent=hatchesCont, align=uiconst.TOTOP_PROP, height=y_min)
        if y_max != 1.0:
            HatchesSprite(parent=hatchesCont, align=uiconst.TOBOTTOM_PROP, height=1.0 - y_max)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if self._enabled != value:
            self._enabled = value
            if self._dragging:
                self._stop_dragging()

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        if self._position != value:
            self._position = value
            self._update_indicator_position()
            if self._on_position_changed is not None:
                self._on_position_changed(self)

    @property
    def on_position_changed(self):
        if self._on_position_changed is None:
            self._on_position_changed = signals.Signal('{}.on_position_changed'.format(self.__class__.__name__))
        return self._on_position_changed

    def _update_indicator_position(self):
        width, height = self.GetCurrentAbsoluteSize()
        x, y = self._position
        offset_x, offset_y = self._get_indicator_offset()
        self._indicator.left = math.floor(width * x + offset_x)
        self._indicator.top = math.floor(height * y + offset_y)

    def _get_indicator_offset(self):
        width, height = self._indicator.GetCurrentAbsoluteSize()
        hotspot_x, hotspot_y = self._indicator_hotspot
        return (width * -hotspot_x, height * -hotspot_y)

    def _stop_dragging(self):
        if self._dragging:
            self._dragging = False

    def _update_selected_position(self):
        left, top = self.GetCurrentAbsolutePosition()
        width, height = self.GetCurrentAbsoluteSize()
        sat_min, sat_max = self._saturation_range
        bri_min, bri_max = self._brightness_range
        x = mathext.clamp((uicore.uilib.x - left) / width, sat_min, sat_max)
        y = mathext.clamp((uicore.uilib.y - top) / height, 1.0 - bri_max, 1.0 - bri_min)
        self.position = (x, y)

    def OnMouseDown(self, button, *args):
        if not self._dragging and button == uiconst.MOUSELEFT and self.enabled:
            self._dragging = True
            self._update_selected_position()

    def OnMouseMove(self, *args):
        if self._dragging:
            self._update_selected_position()

    def OnMouseUp(self, button, *args):
        if self._dragging and button == uiconst.MOUSELEFT:
            self._update_selected_position()
            self._stop_dragging()

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        result = super(Picker2D, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
        _, _, _, _, size_changed = result
        if size_changed:
            self._update_indicator_position()
        return result


class CircleIndicator(Sprite):

    def __init__(self, width = 15, height = 15, texturePath = 'res:/UI/Texture/classes/ColorPicker/color_selection_indicator.png', state = uiconst.UI_DISABLED, **kwargs):
        super(CircleIndicator, self).__init__(width=width, height=height, texturePath=texturePath, state=state, **kwargs)


class ColorSaturationBrightnessGradient(Container):
    _hue_fill = None

    def __init__(self, hue, ignore_color_blind_mode = False, **kwargs):
        self._hue = hue
        super(ColorSaturationBrightnessGradient, self).__init__(**kwargs)
        GradientSprite(parent=self, align=Align.TOALL, rgbData=[(0.0, (0.0, 0.0, 0.0)), (1.0, (0.0, 0.0, 0.0))], alphaData=[(0.0, 0.0), (1.0, 1.0)], rotation=-math.pi / 2.0)
        GradientSprite(parent=self, align=Align.TOALL, rgbData=[(0.0, (1.0, 1.0, 1.0)), (1.0, (1.0, 1.0, 1.0))], alphaData=[(0.0, 1.0), (1.0, 0.0)])
        self._hue_fill = Fill(parent=self, align=Align.TOALL, color=self._get_color(), ignoreColorBlindMode=ignore_color_blind_mode)

    @property
    def hue(self):
        return self._hue

    @hue.setter
    def hue(self, value):
        self._hue = value
        if self._hue_fill:
            self._hue_fill.color = self._get_color()

    def _get_color(self):
        return carbonui.Color.from_hsb(self._hue, 1.0, 1.0)
