#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\theme\edit_window.py
import carbonui
import eveicon
import localization
import signals
import trinity
from carbonui import Align, ButtonVariant, uiconst
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.infoIcon import InfoGlyphIcon
from eve.client.script.ui.shared.colorThemes import ColorTheme
from eve.client.script.ui.shared.systemMenu.theme import theme_const
from eve.client.script.ui.shared.systemMenu.theme.color_picker import ColorField
from eve.client.script.ui.shared.systemMenu.theme.confirm import confirm_discard_unsaved_color_theme_changes
from eve.client.script.ui.shared.systemMenu.theme.model import focus_dark_from_focus
from eve.client.script.ui.shared.systemMenu.theme.share import copy_theme_slug_to_clipboard, format_theme_slug, InvalidThemeSlug, parse_theme_slug

class ThemeEditState(object):

    def __init__(self, theme):
        self._initial_theme = theme
        self._theme_id = theme.id
        self._name = theme.name
        self._focus = theme.focus
        self._accent = theme.accent
        self._alert = theme.alert
        self._tint = theme.tint
        self.on_theme_changed = signals.Signal()
        self.on_name_changed = signals.Signal()
        self.on_focus_color_changed = signals.Signal()
        self.on_focus_dark_color_changed = signals.Signal()
        self.on_accent_color_changed = signals.Signal()
        self.on_tint_color_changed = signals.Signal()
        self.on_alert_color_changed = signals.Signal()
        self.on_theme_slug_changed = signals.Signal()

    @property
    def has_unsaved_changes(self):
        return self._initial_theme != self.theme

    @property
    def theme(self):
        return ColorTheme(theme_id=self._theme_id, name=self._name, focus=self._focus, focus_dark=self.focus_dark_color, accent=self._accent, alert=self._alert, tint=self._tint)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if self._name != value:
            self._name = value
            self.on_name_changed(self)

    @property
    def focus_color(self):
        return self._focus

    @focus_color.setter
    def focus_color(self, value):
        if self._focus != value:
            self._focus = value
            self.on_focus_color_changed(self)
            self.on_focus_dark_color_changed(self)
            self.on_theme_slug_changed(self)
            self.on_theme_changed(self)

    @property
    def focus_dark_color(self):
        return focus_dark_from_focus(self._focus)

    @property
    def accent_color(self):
        return self._accent

    @accent_color.setter
    def accent_color(self, value):
        if self._accent != value:
            self._accent = value
            self.on_accent_color_changed(self)
            self.on_theme_slug_changed(self)
            self.on_theme_changed(self)

    @property
    def tint_color(self):
        return self._tint

    @tint_color.setter
    def tint_color(self, value):
        if self._tint != value:
            self._tint = value
            self.on_tint_color_changed(self)
            self.on_theme_slug_changed(self)
            self.on_theme_changed(self)

    @property
    def alert_color(self):
        return self._alert

    @alert_color.setter
    def alert_color(self, value):
        if self._alert != value:
            self._alert = value
            self.on_alert_color_changed(self)
            self.on_theme_slug_changed(self)
            self.on_theme_changed(self)

    @property
    def theme_slug(self):
        return format_theme_slug(focus=self.focus_color, accent=self.accent_color, tint=self.tint_color, alert=self.alert_color)

    def apply_theme_slug(self, slug):
        focus, accent, tint, alert = parse_theme_slug(slug)
        self.focus_color = focus
        self.accent_color = accent
        self.tint_color = tint
        self.alert_color = alert


class ThemeEditWindow(Window):
    default_windowID = 'theme_edit_window'
    default_isLightBackgroundConfigurable = False
    default_isLockable = False
    default_isMinimizable = False
    default_isOverlayable = False
    default_isCollapseable = False
    default_captionLabelPath = 'UI/SystemMenu/GeneralSettings/ColorTheme/ThemeEditWindowCaption'
    default_iconNum = 'res:/UI/Texture/WindowIcons/color_picker.png'
    _content_wrap = None
    _theme_slug_input = None

    def __init__(self, theme, on_theme_changed = None, **kwargs):
        self.on_theme_changed = signals.Signal()
        self._theme_edit_state = ThemeEditState(theme)
        super(ThemeEditWindow, self).__init__(**kwargs)
        self.MakeUnResizeable()
        self._layout()
        self._theme_edit_state.on_focus_color_changed.connect(self._on_focus_color_changed)
        self._theme_edit_state.on_accent_color_changed.connect(self._on_accent_color_changed)
        self._theme_edit_state.on_tint_color_changed.connect(self._on_tint_color_changed)
        self._theme_edit_state.on_alert_color_changed.connect(self._on_alert_color_changed)
        self._theme_edit_state.on_theme_changed.connect(self._on_theme_changed)
        self._theme_edit_state.on_theme_slug_changed.connect(self._on_theme_slug_changed)
        if on_theme_changed is not None:
            self.on_theme_changed.connect(on_theme_changed)

    @property
    def theme(self):
        return self._theme_edit_state.theme

    def _on_theme_changed(self, theme_edit_state):
        self.on_theme_changed(self)

    def _layout(self):
        self._content_wrap = ContainerAutoSize(parent=self.content, callback=self._on_content_wrap_size_changed, only_use_callback_when_size_changes=True)
        self._content_wrap.DisableAutoSize()
        grid = LayoutGrid(parent=self._content_wrap, align=Align.TOPLEFT, columns=2, cellSpacing=(16, 16))
        name_cont = ContainerAutoSize(align=Align.TOTOP)
        grid.AddCell(name_cont, colSpan=2)
        eveLabel.EveLabelMedium(parent=name_cont, align=Align.TOTOP, text=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/ThemeNameFieldLabel'))
        SingleLineEditText(parent=name_cont, align=Align.TOTOP, top=4, maxLength=64, setvalue=self._theme_edit_state.name, OnChange=self._on_name_input_changed)
        primary_grid = LayoutGrid(parent=grid, align=Align.TOPLEFT, columns=1, cellSpacing=(0, 4))
        eveLabel.EveLabelMedium(parent=primary_grid, align=Align.TOPLEFT, text=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/PrimaryColorFieldLabel'))
        self._focus_color_picker = ColorField(parent=primary_grid, align=Align.TOPLEFT, color=self._theme_edit_state.focus_color, on_color_changed=self._on_focus_color_picked, brightness_range=(theme_const.FOREGROUND_MIN_BRIGHTNESS, 1.0))
        accent_grid = LayoutGrid(parent=grid, align=Align.TOPLEFT, columns=1, cellSpacing=(0, 4))
        eveLabel.EveLabelMedium(parent=accent_grid, align=Align.TOPLEFT, text=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/AccentColorFieldLabel'))
        self._accent_color_picker = ColorField(parent=accent_grid, align=Align.TOPLEFT, color=self._theme_edit_state.accent_color, on_color_changed=self._on_accent_color_picked, brightness_range=(theme_const.FOREGROUND_MIN_BRIGHTNESS, 1.0))
        tint_grid = LayoutGrid(parent=grid, align=Align.TOPLEFT, columns=1, cellSpacing=(0, 4))
        eveLabel.EveLabelMedium(parent=tint_grid, align=Align.TOPLEFT, text=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/TintColorFieldLabel'))
        self._tint_color_picker = ColorField(parent=tint_grid, align=Align.TOPLEFT, color=self._theme_edit_state.tint_color, on_color_changed=self._on_tint_color_picked, brightness_range=(0.0, theme_const.BACKGROUND_MAX_BRIGHTNESS), ignore_color_blind_mode=True)
        alert_grid = LayoutGrid(parent=grid, align=Align.TOPLEFT, columns=1, cellSpacing=(0, 4))
        eveLabel.EveLabelMedium(parent=alert_grid, align=Align.TOPLEFT, text=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/AlertColorFieldLabel'))
        self._alert_color_picker = ColorField(parent=alert_grid, align=Align.TOPLEFT, color=self._theme_edit_state.alert_color, on_color_changed=self._on_alert_color_picked, brightness_range=(theme_const.FOREGROUND_MIN_BRIGHTNESS, 1.0))
        share_cont = ContainerAutoSize(align=Align.TOTOP, alignMode=Align.TOTOP, top=16)
        grid.AddCell(share_cont, colSpan=2)
        Button(parent=ContainerAutoSize(parent=share_cont, align=Align.TORIGHT, padLeft=8), align=Align.TOPLEFT, hint=localization.GetByLabel('UI/Common/Copy'), texturePath=eveicon.copy, func=self._on_copy_theme_slug, args=())
        self._theme_slug_input = SingleLineEditText(parent=share_cont, align=Align.TOTOP, setvalue=self._theme_edit_state.theme_slug, autoselect=True, OnChange=self._on_theme_slug_edited, OnFocusLost=self._on_theme_slug_focus_lost)
        self._theme_slug_input.SetHistoryVisibility(False)
        InfoGlyphIcon(parent=ContainerAutoSize(parent=self._theme_slug_input, align=Align.TORIGHT, left=8, idx=0), align=Align.CENTER, state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/ShareHint'))
        group = ButtonGroup(align=Align.TOTOP, button_size_mode=ButtonSizeMode.STRETCH, top=16)
        grid.AddCell(group, colSpan=2)
        Button(parent=group, label=localization.GetByLabel('UI/Common/Buttons/Apply'), func=self._on_apply, args=(), variant=ButtonVariant.PRIMARY)
        Button(parent=group, label=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/Save'), func=self._on_save, args=())
        Button(parent=group, label=localization.GetByLabel('UI/Common/Cancel'), func=self._on_cancel, args=())
        self._content_wrap.EnableAutoSize()

    def _on_apply(self):
        self.SetModalResult(uiconst.ID_APPLY)

    def _on_save(self):
        self.SetModalResult(uiconst.ID_OK)

    def _on_cancel(self):
        if self._confirm_discard_changes_if_any():
            self.SetModalResult(uiconst.ID_CANCEL)

    def _on_copy_theme_slug(self):
        copy_theme_slug_to_clipboard(self._theme_edit_state.theme_slug)

    def CloseByUser(self, *args):
        if self._confirm_discard_changes_if_any():
            super(ThemeEditWindow, self).CloseByUser()

    def DeactivateUnderlay(self):
        pass

    def OnWindowAboveSetInactive(self):
        pass

    def _confirm_discard_changes_if_any(self):
        if self._theme_edit_state.has_unsaved_changes:
            return confirm_discard_unsaved_color_theme_changes()
        else:
            return True

    def _on_name_input_changed(self, text):
        self._theme_edit_state.name = text

    def _on_focus_color_changed(self, theme_edit_state):
        self._focus_color_picker.color = theme_edit_state.focus_color

    def _on_focus_color_picked(self, color_picker):
        self._theme_edit_state.focus_color = color_picker.color

    def _on_accent_color_changed(self, theme_edit_state):
        self._accent_color_picker.color = theme_edit_state.accent_color

    def _on_accent_color_picked(self, color_picker):
        self._theme_edit_state.accent_color = color_picker.color

    def _on_tint_color_changed(self, theme_edit_state):
        self._tint_color_picker.color = theme_edit_state.tint_color

    def _on_tint_color_picked(self, color_picker):
        self._theme_edit_state.tint_color = color_picker.color

    def _on_alert_color_changed(self, theme_edit_state):
        self._alert_color_picker.color = theme_edit_state.alert_color

    def _on_alert_color_picked(self, color_picker):
        self._theme_edit_state.alert_color = color_picker.color

    def _on_theme_slug_changed(self, theme_edit_state):
        focused = uicore.registry.GetFocus() == self._theme_slug_input
        if not focused:
            self._theme_slug_input.SetText(theme_edit_state.theme_slug)

    def _on_theme_slug_edited(self, text):
        try:
            self._theme_edit_state.apply_theme_slug(text)
        except InvalidThemeSlug:
            pass

    def _on_theme_slug_focus_lost(self, input):
        try:
            self._theme_edit_state.apply_theme_slug(input.GetValue())
        except InvalidThemeSlug:
            pass

        self._theme_slug_input.SetText(self._theme_edit_state.theme_slug)

    def _on_content_wrap_size_changed(self):
        self.width, self.height = self.GetWindowSizeForContentSize(width=self._content_wrap.width, height=self._content_wrap.height)

    def _create_modal_layer(self, name, close_when_clicked = False):
        return ModalLayer(name=name, parent=uicore.layer.modal)


def edit_custom_color_theme(theme, ui_color_service):
    if theme.is_preset:
        raise ValueError("Can't edit preset themes")

    def on_theme_changed(theme_edit_window):
        ui_color_service.SetThemeOverride(theme_edit_window.theme)

    ui_color_service.SetThemeOverride(theme)
    try:
        window = ThemeEditWindow.Open(theme=theme, on_theme_changed=on_theme_changed)
        result = window.ShowDialog(modal=True, fillOpacity=0.0, sceneSaturation=1.0)
        if result == uiconst.ID_APPLY:
            ui_color_service.SaveCustomTheme(window.theme)
            ui_color_service.SetThemeID(window.theme.id)
        elif result == uiconst.ID_OK:
            ui_color_service.SaveCustomTheme(window.theme)
    finally:
        ui_color_service.ClearThemeOverride()


class ModalLayer(Container):
    _frame = None
    _header = None
    _hatch = None
    HATCH_SIZE = 264
    HATCH_SIZE_HALF = HATCH_SIZE / 2.0

    def __init__(self, name, parent):
        super(ModalLayer, self).__init__(name=name, parent=parent, align=Align.TOALL, state=uiconst.UI_NORMAL, idx=0)
        self._frame = Frame(parent=self, align=Align.TOALL, frameConst=uiconst.FRAME_BORDER2_CORNER0, color=eveColor.WARNING_ORANGE)
        self._header = carbonui.TextHeadline(parent=self, align=Align.CENTERTOP, top=16, text=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/ColorThemePreviewModeCaption'), color=eveColor.WARNING_ORANGE)
        self._hatch = Sprite(parent=self, align=Align.TOPLEFT, state=uiconst.UI_DISABLED, width=264, height=264, texturePath='res:/UI/Texture/classes/ColorPicker/hatch.png', textureSecondaryPath='res:/UI/Texture/classes/ColorPicker/hatch_mask.png', spriteEffect=trinity.TR2_SFX_MODULATE, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, color=eveColor.WARNING_ORANGE, opacity=0.15, glowBrightness=0.1)
        self._update_hatch_position()
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self._on_global_mouse_move)

    def _on_global_mouse_move(self, *args):
        if not self.destroyed and self._hatch:
            self._update_hatch_position()
            return True
        else:
            return False

    def _update_hatch_position(self):
        self._hatch.left = uicore.uilib.x - self.HATCH_SIZE_HALF
        self._hatch.top = uicore.uilib.y - self.HATCH_SIZE_HALF
        self._hatch.translationPrimary = (uicore.uilib.x % 11 / float(self.HATCH_SIZE), uicore.uilib.y % 11 / float(self.HATCH_SIZE))

    def _AppendChildRO(self, child):
        super(ModalLayer, self)._AppendChildRO(child)
        if self._hatch and child is not self._hatch:
            self._hatch.SetOrder(-1)

    def _InsertChildRO(self, idx, child):
        super(ModalLayer, self)._InsertChildRO(idx, child)
        if self._hatch and child is not self._hatch:
            self._hatch.SetOrder(-1)

    def OnMouseDown(self, *args):
        for element in (self._frame, self._header):
            if element:
                animations.SpColorMorphTo(element, startColor=eveColor.WARNING_ORANGE, endColor=eveColor.WHITE, duration=0.4, loops=3, curveType=uiconst.ANIM_WAVE)

        if self._hatch:
            animations.FadeTo(self._hatch, startVal=0.3, endVal=0.15, duration=0.3)
