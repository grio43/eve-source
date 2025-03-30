#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\sideNavigation.py
import carbonui
import eveicon
import eveui
import signals
import uthread2
from carbonui import Align, TextColor, uiconst, PickState
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.decorative.blurredSceneUnderlay import BlurredSceneUnderlay
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.decorative.selectionIndicatorLine import SelectionIndicatorLine
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.split_view import SplitView, PanelMode
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveThemeColor

class SideNavigationSplitView(SplitView):

    def __init__(self, is_always_expanded_setting, compact_panel_width = 58, panel_mode = PanelMode.COMPACT_OVERLAY, static_panel_inner_width = False, force_compact = False, **kwargs):
        super(SideNavigationSplitView, self).__init__(compact_panel_width=compact_panel_width, panel_mode=panel_mode, static_panel_inner_width=static_panel_inner_width, **kwargs)
        self._minimized = False
        self._force_compact = force_compact
        self.original_compact_panel_width = compact_panel_width
        self.is_always_expanded_setting = is_always_expanded_setting
        self.panel.pickState = PickState.ON
        self.panel.OnMouseEnter = self._panel_mouse_enter
        self.panel.OnMouseExit = self._panel_mouse_exit
        self.is_always_expanded_setting.on_change.connect(self._apply_always_expanded_setting)
        self._apply_always_expanded_setting()
        self._expand_button = Button(parent=self.content, align=Align.TOPLEFT, padTop=8, texturePath=eveicon.list_view, func=self._on_expand_button)
        self._expand_button.Hide()

    def _apply_always_expanded_setting(self, *args, **kwargs):
        if self.is_always_expanded_setting.is_enabled():
            self._enable_always_expanded()
        else:
            self._disable_always_expanded()

    def _disable_always_expanded(self):
        self.panel_mode = PanelMode.COMPACT_OVERLAY
        self.content.padLeft = self.compact_panel_width
        self.collapse(animate=False)

    def _enable_always_expanded(self):
        self.panel_mode = PanelMode.INLINE
        self.content.padLeft = 0
        self.expand(animate=False)

    def _panel_mouse_enter(self, *args, **kwargs):
        self.expand_panel(True)

    def _panel_mouse_exit(self, *args, **kwargs):
        self.expand_panel(False)

    def expand_panel(self, expanded):
        if self.is_always_expanded_setting.is_enabled():
            return
        if self._force_compact:
            return
        self.expanded = expanded

    def _on_expand_button(self, *args):
        self.expand(True)

    def set_content_padLeft(self, padLeft):
        self.content.padLeft = padLeft

    def set_minimized(self, minimized):
        if minimized and not self._minimized:
            self.compact_panel_width = 0
            self.set_content_padLeft(0)
            self.panel_mode = PanelMode.OVERLAY
            self._expand_button.Show()
        elif not minimized and self._minimized:
            self.compact_panel_width = self.original_compact_panel_width
            self.set_content_padLeft(self.original_compact_panel_width)
            self.panel_mode = PanelMode.COMPACT_OVERLAY
            self._expand_button.Hide()
        self._minimized = minimized

    def set_force_compact(self, force_compact):
        if force_compact:
            self.expanded = False
        self._force_compact = force_compact


class SideNavigation(Container):
    default_state = uiconst.UI_NORMAL

    def __init__(self, is_expanded_func, expand_func = None, is_always_expanded_setting = None, force_compact = False, **kwargs):
        super(SideNavigation, self).__init__(**kwargs)
        self._entries = {}
        self._force_compact = force_compact
        self.is_expanded_func = is_expanded_func
        self.expand_func = expand_func
        self.is_always_expanded_setting = is_always_expanded_setting
        self._on_expand_signal = signals.Signal('on_expand_signal')
        self._layout()
        self.on_expanded_changed(self.is_expanded_func(), animate=False)

    def on_expanded_changed(self, expanded, animate = True):
        if expanded:
            if self._body.scrollbarsDisabled:
                eveui.Sound.expand.play()
            self._body.EnableScrollbars()
        else:
            if not self._body.scrollbarsDisabled:
                eveui.Sound.collapse.play()
            self._body.DisableScrollbars()
        self._on_expand_signal(expanded, animate)

    def set_force_compact(self, force_compact):
        self._force_compact = force_compact
        for entry in self._body.mainCont.children:
            if isinstance(entry, SideNavigationEntryInterface):
                entry.set_force_compact(force_compact)

    def set_entry_selected(self, entry_id):
        for _entry_id, entry in self._entries.items():
            entry.selected = _entry_id == entry_id

        if self.is_expanded_func() and self.expand_func is not None:
            self.expand_func(False)

    def _layout(self):
        main = Container(name='main', parent=self, padding=(8, 8, 0, 8))
        self._layout_header(main)
        self._layout_footer(main)
        self._body = ScrollContainer(name='body', parent=main)
        self._body.DisableScrollbars()
        self._construct_header()
        self._construct_footer()
        self._construct_body()
        self._construct_background()

    def _layout_header(self, main):
        self._header = ContainerAutoSize(name='header', parent=main, align=Align.TOTOP, alignMode=Align.TOTOP)

    def _layout_footer(self, main):
        self._footer = ContainerAutoSize(name='footer', parent=main, align=Align.TOBOTTOM, alignMode=Align.TOTOP)

    def Flush(self):
        self._body.Flush()

    def _construct_background(self):
        PanelUnderlay(bgParent=self)
        BlurredSceneUnderlay(bgParent=self)

    def _construct_header(self):
        pass

    def _construct_body(self):
        pass

    def _construct_footer(self):
        if self.is_always_expanded_setting:
            entry = SideNavigationSettingsEntry(parent=self._footer, padTop=8, is_always_expanded_setting=self.is_always_expanded_setting, on_hover=self._on_entry_hover)
            self._connect_to_expand(entry)

    def _connect_to_expand(self, entry):
        self._on_expand_signal.connect(entry.on_expanded_changed)

    def add_entry(self, entry_id, text, on_click, icon, hide_empty = False, force_hidden = False, entry_cls = None, **kwargs):
        entry_cls = entry_cls or SideNavigationEntry
        entry = entry_cls(name='{}_entry'.format(entry_id), parent=self._body, icon=icon, text=text, hide_empty=hide_empty, force_hidden=force_hidden, force_compact=self._force_compact, on_click=on_click, entry_id=entry_id, on_hover=self._on_entry_hover, **kwargs)
        entry.on_expanded_changed(self.is_expanded_func(), animate=False)
        self._entries[entry_id] = entry
        self._connect_to_expand(entry)

    def add_header(self, label, **kwargs):
        padTop = 12 if not len(self._body.mainCont.children) else 16
        entry = SideNavigationHeaderEntry(parent=self._body, text=label, **kwargs)
        entry.padTop = padTop
        entry.on_expanded_changed(self.is_expanded_func(), animate=False)
        self._connect_to_expand(entry)

    def _on_entry_hover(self, entry):
        if not self.is_expanded_func() and self.expand_func is not None:
            self.expand_func(True)


class SideNavigationEntryInterface(object):

    def on_expanded_changed(self, expanded, animate = True):
        raise NotImplementedError

    def set_expanded(self, animate = True):
        raise NotImplementedError

    def set_collapsed(self, animate = True):
        raise NotImplementedError

    def set_force_compact(self, force_compact):
        raise NotImplementedError


class SideNavigationSettingsEntry(Container, SideNavigationEntryInterface):
    default_align = Align.TOTOP
    default_height = 32
    default_padLeft = 8
    default_padRight = 8

    def __init__(self, is_always_expanded_setting, on_hover = None, **kwargs):
        super(SideNavigationSettingsEntry, self).__init__(**kwargs)
        self._on_hover = on_hover
        self.is_always_expanded_setting = is_always_expanded_setting
        self._layout()
        self._update_expand_icon()

    def _layout(self):
        self._expand_button = ButtonIcon(parent=self, align=Align.TORIGHT, func=self._expand_clicked, opacity=0)

    def on_expanded_changed(self, expanded, animate = True):
        if expanded:
            self.set_expanded(animate)
        else:
            self.set_collapsed(animate)

    def set_expanded(self, animate = True):
        if animate:
            eveui.animation.fade_in(self._expand_button, end_value=TextColor.NORMAL.opacity, duration=0.2, time_offset=0.3)
        else:
            self._expand_button.opacity = TextColor.NORMAL.opacity

    def set_collapsed(self, animate = True):
        if animate:
            eveui.animation.fade_out(self._expand_button, duration=0.2)
        else:
            self._expand_button.opacity = 0.0

    def _expand_clicked(self):
        self.is_always_expanded_setting.toggle()
        self._update_expand_icon()

    def _update_expand_icon(self):
        self._expand_button.SetTexturePath(eveicon.chevron_left if self.is_always_expanded_setting.is_enabled() else eveicon.chevron_right)

    def set_force_compact(self, force_compact):
        pass

    def OnMouseEnter(self, *args):
        super(SideNavigationSettingsEntry, self).OnMouseEnter(*args)
        if self._on_hover:
            self._on_hover(self)


class SideNavigationHeaderEntry(ContainerAutoSize, SideNavigationEntryInterface):
    default_align = Align.TOTOP
    default_alignMode = Align.TOPLEFT
    default_padding = (8, 16, 8, 4)

    def __init__(self, text, **kwargs):
        super(SideNavigationHeaderEntry, self).__init__(**kwargs)
        self._text = text
        self._text_label = carbonui.TextDetail(parent=self, align=Align.TOPLEFT, text=text, opacity=0)
        self._text_label.autoFadeSides = 12

    def on_expanded_changed(self, expanded, animate = True):
        if expanded:
            self.set_expanded(animate)
        else:
            self.set_collapsed(animate)

    def set_collapsed(self, animate = True):
        if animate:
            eveui.animation.fade_out(self._text_label, duration=0.2)
        else:
            self._text_label.opacity = 0.0

    def set_expanded(self, animate = True):
        if animate:
            eveui.animation.fade_in(self._text_label, end_value=TextColor.SECONDARY.opacity, duration=0.2)
        else:
            self._text_label.opacity = TextColor.SECONDARY.opacity

    def set_force_compact(self, force_compact):
        pass


class SideNavigationEntry(Container, SideNavigationEntryInterface):
    default_state = uiconst.UI_NORMAL
    default_align = Align.TOTOP
    default_height = 32
    default_bgColor = eveThemeColor.THEME_FOCUSDARK

    def __init__(self, icon, text, on_click, hide_empty = False, value = '', force_hidden = False, force_compact = False, entry_id = None, icon_size = 16, icon_color = TextColor.NORMAL, on_hover = None, **kwargs):
        super(SideNavigationEntry, self).__init__(**kwargs)
        self._on_click = on_click
        self._on_hover = on_hover
        self._selected = False
        self._value = value
        self.entry_id = entry_id
        self._hide_empty = hide_empty
        self._force_hidden = force_hidden
        self._force_compact = force_compact
        self.bgFill.opacity = 0
        self._icon_size = icon_size
        self._icon_color = icon_color
        self._text = text
        self._selected_fill = Fill(bgParent=self, color=eveThemeColor.THEME_FOCUSDARK, opacity=0)
        self.selection_indicator = SelectionIndicatorLine(parent=self, align=Align.TOLEFT_NOPUSH, selected=False)
        content = Container(parent=self, pickState=PickState.OFF, padding=(8, 4, 16, 4))
        self._icon_container = Container(parent=content, align=Align.TOLEFT, width=24)
        self._icon = Sprite(parent=self._icon_container, align=Align.CENTER, height=self._icon_size, width=self._icon_size, texturePath=icon, color=TextColor.NORMAL)
        if not icon:
            self._icon_container.Hide()
        self._value_container = ContainerAutoSize(parent=content, align=Align.TORIGHT, opacity=0)
        self._value_label = carbonui.TextBody(parent=self._value_container, align=Align.CENTERLEFT, color=TextColor.SECONDARY)
        self._text_container = Container(parent=content, padLeft=8, padRight=8, clipChildren=True, opacity=0)
        self._text_label = carbonui.TextBody(parent=self._text_container, align=Align.CENTERLEFT, text=text, maxLines=1)
        self._text_label.autoFadeSides = 16
        self.set_value(value)

    def on_expanded_changed(self, expanded, animate = True):
        if expanded:
            self.set_expanded(animate)
        else:
            self.set_collapsed(animate)

    def set_expanded(self, animate = True):
        if animate:
            eveui.animation.fade_in(self._value_container, duration=0.2)
            eveui.animation.fade_in(self._text_container, duration=0.2)
        else:
            self._value_container.opacity = 1.0
            self._text_container.opacity = 1.0

    def set_collapsed(self, animate = True):
        if animate:
            eveui.animation.fade_out(self._value_container, duration=0.1)
            eveui.animation.fade_out(self._text_container, duration=0.2)
        else:
            self._value_container.opacity = 0.0
            self._text_container.opacity = 0.0

    def set_value(self, value):
        self._value = value
        self._update_display_state()
        self._value_label.text = unicode(value) if value else ''
        self._update_colors()

    def force_hidden(self, hidden):
        self._force_hidden = hidden
        self._update_display_state()

    def set_force_compact(self, force_compact):
        self._force_compact = force_compact

    def OnColorThemeChanged(self):
        super(SideNavigationEntry, self).OnColorThemeChanged()
        self.bgFill.rgb = eveThemeColor.THEME_FOCUSDARK[:3]
        self._selected_fill.rgb = eveThemeColor.THEME_FOCUSDARK[:3]

    def OnMouseEnter(self, *args):
        super(SideNavigationEntry, self).OnMouseEnter(*args)
        eveui.Sound.button_hover.play()
        eveui.animation.fade_in(self.bgFill, end_value=0.15, duration=0.05)
        if self._on_hover:
            self._on_hover(self)

    def OnMouseExit(self, *args):
        super(SideNavigationEntry, self).OnMouseExit(*args)
        eveui.animation.fade_out(self.bgFill, duration=0.2)

    def OnClick(self, *args):
        eveui.Sound.button_click.play()
        self._on_click(self)

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        if self._selected == value:
            return
        self._selected = value
        self._update_display_state()
        self._update_colors()
        if self.selected:
            eveui.fade_in(self._selected_fill, end_value=0.2, duration=0.2)
            self.selection_indicator.Select()
        else:
            eveui.fade_out(self._selected_fill, duration=0.2)
            self.selection_indicator.Deselect()

    def _update_colors(self):
        if self._value == 0:
            color = TextColor.DISABLED
            self._text_label.rgba = color
            self._icon.rgba = color
            self._value_label.rgba = color
        elif self._selected:
            color = TextColor.HIGHLIGHT
            self._icon.rgba = color
            self._text_label.rgba = color
            self._value_label.rgba = color
        else:
            self._text_label.rgba = TextColor.NORMAL
            self._icon.rgba = self._icon_color
            self._value_label.rgba = TextColor.SECONDARY

    def _update_display_state(self):
        display = True
        if not self.selected:
            if self._force_hidden:
                display = False
            elif self._hide_empty:
                display = bool(self._value)
        self.display = display

    def GetHint(self):
        if self._force_compact:
            hint = self.hint
            if hint:
                return u'<b>{}</b>\n{}'.format(self._text, self.hint)
            else:
                return self._text
        return self.hint

    def GetTooltipDelay(self):
        if self._force_compact:
            return 0

    def GetTooltipPointer(self):
        return uiconst.POINT_RIGHT_2
