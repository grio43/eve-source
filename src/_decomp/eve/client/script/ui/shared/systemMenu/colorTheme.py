#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\colorTheme.py
import eveicon
import localization
import signals
import threadutils
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst, TextColor, Align, AxisAlignment, ButtonVariant
from carbonui.button.group import ButtonGroup
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.decorative.divider_line import DividerLine
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.uiconst import PickState
from carbonui.uicore import uicore
from clonegrade import const as cloneGradeConst
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.services import uiColorSettings
from eve.client.script.ui.shared import colorThemes
from eve.client.script.ui.shared.cloneGrade import cloneStateUtil
from eve.client.script.ui.shared.systemMenu.theme.confirm import confirm_remove_custom_color_theme
from eve.client.script.ui.shared.systemMenu.theme.edit_window import edit_custom_color_theme
from eve.client.script.ui.shared.systemMenu.theme.feature_flag import is_custom_color_themes_enabled
from eve.client.script.ui.shared.systemMenu.theme.model import generate_theme_id
from eve.client.script.ui.shared.systemMenu.theme.share import copy_theme_slug_to_clipboard, format_theme_slug
from eve.client.script.ui.shared.systemMenu.theme.storage import custom_color_themes
from signals import Signal

class ColorThemeContainer(ContainerAutoSize):

    def __init__(self, ui_color_service, **kwargs):
        self._loading = False
        self._reload_pending = False
        self._ui_color_service = ui_color_service
        super(ColorThemeContainer, self).__init__(**kwargs)
        self._update_enabled()
        self.entry_cont = ContainerAutoSize(name='entry_cont', parent=self, align=Align.TOTOP)
        if is_custom_color_themes_enabled():
            self._construct_buttons()
        self._load()
        if is_custom_color_themes_enabled():
            custom_color_themes.on_change.connect(self._on_custom_color_themes_changed)
        self.on_omega_button_clicked = Signal('on_omega_button_clicked')

    def _construct_buttons(self):
        buttonGroup = ButtonGroup(parent=self, align=uiconst.TOTOP, padTop=8, button_alignment=AxisAlignment.START)
        isOmega = cloneStateUtil.IsOmega()
        createButton = buttonGroup.AddButton(label=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/CreateNewTheme'), variant=ButtonVariant.GHOST, func=create_custom_theme)
        if not isOmega:
            createButton.Disable()

    def _construct_theme_list(self, header, themes):
        eveLabel.EveHeaderMedium(parent=self.entry_cont, align=uiconst.TOTOP, top=12, text=header, color=TextColor.DISABLED)
        for theme in themes:
            ColorSettingEntry(parent=self.entry_cont, theme=theme, on_edit=self._on_edit_theme, on_remove=self._on_remove_theme, on_share=self._on_share_theme)

    def _construct_omega_theme_list(self, header, themes, tooltip = None):
        labelCont = Container(parent=self.entry_cont, align=uiconst.TOTOP, top=10, height=24)
        ButtonIcon(parent=labelCont, align=uiconst.TOLEFT, iconSize=24, width=24, left=0, texturePath=cloneGradeConst.TEXTUREPATH_OMEGA_24, func=self._on_omega_button_click, hint=tooltip)
        eveLabel.EveHeaderMedium(parent=labelCont, align=uiconst.TOLEFT, top=2, left=6, text=header, color=TextColor.DISABLED)
        for theme in themes:
            ColorSettingEntry(parent=self.entry_cont, theme=theme, pickState=PickState.OFF)

    def _update_enabled(self):
        if uiColorSettings.color_theme_by_ship_faction_setting.is_enabled():
            self.state = uiconst.UI_DISABLED
            self.opacity = 0.3
        else:
            self.state = uiconst.UI_PICKCHILDREN
            self.opacity = 1.0

    @threadutils.threaded
    def _load(self):
        if self._loading:
            self._reload_pending = True
            return
        self._loading = True
        try:
            themes = self._ui_color_service.GetAvailableThemes()
            isOmega = cloneStateUtil.IsOmega()
            omega_themes = []
            preset_themes = []
            custom_themes = []
            for theme in themes:
                if theme.id in colorThemes.COLOR_THEME_PRESET_BY_ID:
                    if theme.omega_only and not isOmega:
                        omega_themes.append(theme)
                    else:
                        preset_themes.append(theme)
                elif is_custom_color_themes_enabled():
                    custom_themes.append(theme)

            preset_themes = localization.util.Sort(preset_themes, key=lambda t: t.name)
            omega_themes = localization.util.Sort(omega_themes, key=lambda t: t.name)
            custom_themes = localization.util.Sort(custom_themes, key=lambda t: t.name)
            self._construct_theme_list(localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/Presets'), preset_themes)
            if len(omega_themes) > 0:
                self._construct_omega_theme_list(localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/OmegaPresets'), omega_themes, localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/OmegaPresetsTooltip'))
            if isOmega:
                self._construct_theme_list(localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/CustomThemes'), custom_themes)
            else:
                self._construct_omega_theme_list(localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/CustomThemes'), custom_themes, localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/OmegaCustomThemesTooltip'))
        finally:
            self._loading = False

        if self._reload_pending:
            self._reload()

    def _reload(self):
        self._reload_pending = False
        self.entry_cont.Flush()
        self._load()

    def _on_custom_color_themes_changed(self, value):
        self._reload()

    def _on_edit_theme(self, theme):
        edit_custom_theme(theme, system_menu=uicore.layer.systemmenu, ui_color_service=self._ui_color_service)

    def _on_remove_theme(self, theme):
        remove_custom_theme(theme, ui_color_service=self._ui_color_service)

    def _on_share_theme(self, theme):
        copy_theme_slug_to_clipboard(format_theme_slug(focus=theme.focus, accent=theme.accent, tint=theme.tint, alert=theme.alert))

    def _on_omega_button_click(self, *args):
        uicore.cmd.OpenCloneUpgradeWindow()
        self.on_omega_button_clicked()

    def Close(self, *args):
        if is_custom_color_themes_enabled():
            custom_color_themes.on_change.disconnect(self._on_custom_color_themes_changed)
        super(ColorThemeContainer, self).Close(*args)


def create_custom_theme(*args):
    default_theme = colorThemes.COLOR_THEME_PRESET_BY_ID[colorThemes.DEFAULT_COLORTHEMEID]
    theme = default_theme.copy_with(theme_id=generate_theme_id(), name=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/CustomThemeDefaultName'))
    edit_custom_theme(theme=theme, system_menu=uicore.layer.systemmenu, ui_color_service=sm.GetService('uiColor'))


def edit_custom_theme(theme, system_menu, ui_color_service):
    if not is_custom_color_themes_enabled():
        return
    if theme.is_preset:
        theme = theme.copy_with(theme_id=generate_theme_id(), name=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/CustomizedPresetThemeDefaultName', theme_name=theme.name))
    system_menu.suppress(show_ui=True)
    try:
        edit_custom_color_theme(theme, ui_color_service)
    finally:
        system_menu.unsuppress()


def remove_custom_theme(theme, ui_color_service):
    if confirm_remove_custom_color_theme(theme):
        ui_color_service.DeleteCustomTheme(theme)


class ColorSettingEntry(Container):
    default_name = 'ColorSettingEntry'
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_height = 32
    __notifyevents__ = ['OnUIColorsChanged']
    _action_cont = None

    def __init__(self, theme, on_edit = None, on_remove = None, on_share = None, deactivated = False, **kwargs):
        self.theme = theme
        self.on_edit = signals.Signal()
        self.on_remove = signals.Signal()
        self.on_share = signals.Signal()
        self._deactivated = deactivated
        super(ColorSettingEntry, self).__init__(**kwargs)
        self._layout()
        sm.RegisterNotify(self)
        if on_edit:
            self.on_edit.connect(on_edit)
        if on_remove:
            self.on_remove.connect(on_remove)
        if on_share:
            self.on_share.connect(on_share)

    def _layout(self):
        ThemePreview(parent=ContainerAutoSize(parent=self, align=uiconst.TOLEFT, padding=(2, 8, 0, 8)), align=uiconst.CENTER, theme=self.theme)
        self._action_cont = ContainerAutoSize(parent=self, align=uiconst.TORIGHT)
        self._action_cont.display = False
        if cloneStateUtil.IsOmega():
            if self.theme.is_preset:
                ButtonIcon(parent=ContainerAutoSize(parent=self._action_cont, align=uiconst.TOLEFT), align=uiconst.CENTER, width=24, height=24, texturePath=eveicon.copy, hint=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/Duplicate'), func=lambda : self.on_edit(self.theme))
            else:
                ButtonIcon(parent=ContainerAutoSize(parent=self._action_cont, align=uiconst.TOLEFT), align=uiconst.CENTER, width=24, height=24, texturePath=eveicon.edit, hint=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/Edit'), func=lambda : self.on_edit(self.theme))
                ButtonIcon(parent=ContainerAutoSize(parent=self._action_cont, align=uiconst.TOLEFT), align=uiconst.CENTER, width=24, height=24, texturePath=eveicon.export, hint=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/Share'), func=lambda : self.on_share(self.theme))
                DividerLine(parent=ContainerAutoSize(parent=self._action_cont, align=uiconst.TOLEFT, padding=(4, 0, 4, 0)), align=uiconst.CENTER, height=16)
                ButtonIcon(parent=ContainerAutoSize(parent=self._action_cont, align=uiconst.TOLEFT), align=uiconst.CENTER, width=24, height=24, texturePath=eveicon.trashcan, hint=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/Delete'), func=lambda : self.on_remove(self.theme))
        eveLabel.EveLabelMedium(parent=Container(parent=self, align=uiconst.TOALL, clipChildren=True), align=uiconst.CENTERLEFT, left=4, text=self.theme.name, autoFadeSides=8, color=TextColor.DISABLED if self._deactivated else TextColor.NORMAL)
        self.underlay = ListEntryUnderlay(bgParent=self)
        self.UpdateSelected()

    def UpdateSelected(self):
        if self.IsSelected():
            self.underlay.Select()
        else:
            self.underlay.Deselect()

    def IsSelected(self):
        return self.theme.id == sm.GetService('uiColor').GetActiveThemeID()

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        self.underlay.hovered = True
        if self._action_cont:
            self._action_cont.display = True

    def OnMouseExit(self, *args):
        self.underlay.hovered = False
        if self._action_cont:
            self._action_cont.display = False

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_ENTRY_SELECT)
        sm.GetService('uiColor').SetThemeID(self.theme.id)

    def OnUIColorsChanged(self):
        self.UpdateSelected()


class ThemePreview(ContainerAutoSize):
    TILE_SIZE_LARGE = 16
    TILE_PADDING = 2
    TILE_SIZE_SMALL = int((TILE_SIZE_LARGE - TILE_PADDING) / 2)

    def __init__(self, theme, **kwargs):
        self._theme = theme
        super(ThemePreview, self).__init__(height=self.TILE_SIZE_LARGE, **kwargs)
        self._layout()

    def _layout(self):
        if is_custom_color_themes_enabled():
            Fill(parent=self, align=uiconst.TOLEFT, color=self._theme.focus, width=self.TILE_SIZE_LARGE)
            Fill(parent=self, align=uiconst.TOLEFT, color=self._theme.accent, left=self.TILE_PADDING, width=self.TILE_SIZE_LARGE)
            Fill(parent=self, align=uiconst.TOLEFT, color=self._theme.tint, left=self.TILE_PADDING, width=self.TILE_SIZE_LARGE)
            Fill(parent=self, align=uiconst.TOLEFT, color=self._theme.alert, left=self.TILE_PADDING, width=self.TILE_SIZE_LARGE)
        else:
            Fill(parent=self, align=uiconst.TOPLEFT, color=self._theme.focus, width=self.TILE_SIZE_LARGE, height=self.TILE_SIZE_LARGE, ignoreColorBlindMode=True)
            Fill(parent=self, align=uiconst.TOPLEFT, color=self._theme.focus_dark, left=self.TILE_SIZE_LARGE + self.TILE_PADDING, width=self.TILE_SIZE_LARGE, height=self.TILE_SIZE_LARGE, ignoreColorBlindMode=True)
            Fill(parent=self, align=uiconst.TOPLEFT, color=self._theme.accent, left=2 * (self.TILE_SIZE_LARGE + self.TILE_PADDING), width=self.TILE_SIZE_LARGE, height=self.TILE_SIZE_LARGE, ignoreColorBlindMode=True)
            Fill(parent=self, align=uiconst.TOPLEFT, color=self._theme.alert, left=3 * (self.TILE_SIZE_LARGE + self.TILE_PADDING), width=self.TILE_SIZE_LARGE, height=self.TILE_SIZE_LARGE, ignoreColorBlindMode=True)
