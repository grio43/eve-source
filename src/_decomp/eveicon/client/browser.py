#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveicon\client\browser.py
import itertools
import blue
import carbonui
import eveformat
import eveicon
import eveui
import signals
import uthread2
from carbonui import TextColor, uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control import eveLabel
from carbonui.control.window import Window

class IconBrowserWindow(Window):
    default_windowID = 'icon_browser'
    default_caption = 'Icons'
    default_minSize = (800, 520)

    def __init__(self, **kwargs):
        self._state = State()
        self._search = None
        self._side_panel = None
        self._scroll = None
        self._flow = None
        super(IconBrowserWindow, self).__init__(**kwargs)
        self.layout()
        self._state.on_selected_icon_change.connect(self._update_selection)
        self._load_icons()

    def layout(self):
        self._side_panel = SidePanel(parent=Container(parent=self.GetMainArea(), align=uiconst.TORIGHT, width=240, padLeft=16), align=uiconst.TOALL, icon=self._state.selected_icon, on_tag_clicked=self._on_tag_clicked)
        self._search = SingleLineEditText(parent=ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, padBottom=16), align=uiconst.TOTOP, hintText='Search', OnChange=self._on_filter_text_change)
        self._search.ShowClearButton(hint='Clear')
        self._scroll = ScrollContainer(parent=self.GetMainArea(), align=uiconst.TOALL)

    def _load_icons(self, filter_text = None):
        self._scroll.Flush()
        icon_groups = itertools.groupby(sorted(eveicon.iter_icons(), key=lambda icon: (icon.group_id, icon.icon_id)), lambda icon: icon.group_id)
        first_icon = None
        for i, (group, icons) in enumerate(icon_groups):
            icons = list(icons)
            group_name = icons[0].group
            total_count = len(icons)
            if filter_text:
                filter_text = filter_text.lower()
                icons = [ icon for icon in icons if filter_text in icon.name.lower() or any((filter_text in tag for tag in icon.tags)) ]
                if len(icons) == 0:
                    continue
            if first_icon is None:
                first_icon = icons[0]
            IconGroup(parent=self._scroll, align=uiconst.TOTOP, top=0 if i == 0 else 32, group_name=group_name, icons=icons, total_count=total_count, state=self._state)

        if self._state.selected_icon is None:
            self._state.select(first_icon)

    @uthread2.debounce(wait=0.25)
    def _on_filter_text_change(self, text):
        self._load_icons(text)

    def _on_tag_clicked(self, tag):
        self._search.SetValue(tag)

    def _update_selection(self):
        self._side_panel.icon = self._state.selected_icon


class IconGroup(ContainerAutoSize):

    def __init__(self, parent, align, top, group_name, icons, total_count, state):
        self._state = state
        super(IconGroup, self).__init__(parent=parent, align=align, alignMode=uiconst.TOTOP, top=top)
        top_cont = ContainerAutoSize(parent=self, align=uiconst.TOTOP)
        grid = LayoutGrid(parent=top_cont, align=uiconst.TOPLEFT, columns=2, cellSpacing=(8, 0))
        eveLabel.EveCaptionSmall(parent=grid, align=uiconst.TOPLEFT, text=group_name)
        eveLabel.EveLabelMedium(parent=grid, align=uiconst.BOTTOMLEFT, text='{} / {} icon{}'.format(len(icons), total_count, 's' if total_count > 1 else '') if total_count != len(icons) else '{} icon{}'.format(len(icons), 's' if len(icons) > 1 else ''), opacity=0.5)
        self._flow = FlowContainer(parent=self, align=uiconst.TOTOP, top=4)
        for icon in icons:
            IconEntry(parent=self._flow, align=uiconst.NOALIGN, icon=icon, selected=self._state.selected_icon == icon, on_click=lambda _icon = icon: self._state.select(_icon))

        self._state.on_selected_icon_change.connect(self._update_selection)

    def _update_selection(self):
        for entry in self._flow.children:
            entry.selected = entry.icon == self._state.selected_icon


class State(object):

    def __init__(self):
        self._selected_icon = None
        self.on_selected_icon_change = signals.Signal()

    @property
    def selected_icon(self):
        return self._selected_icon

    @selected_icon.setter
    def selected_icon(self, value):
        if self._selected_icon != value:
            self._selected_icon = value
            self.on_selected_icon_change()

    def select(self, icon):
        self.selected_icon = icon


class SidePanel(Container):
    _content = None

    def __init__(self, parent, align, icon = None, on_tag_clicked = None):
        self._icon = icon
        self._on_tag_clicked = on_tag_clicked
        super(SidePanel, self).__init__(parent=parent, align=align)
        self._layout()
        self._update()

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        if self._icon != value:
            self._icon = value
            self._update()

    def _layout(self):
        self._content = Container(parent=self, align=uiconst.TOALL, padding=16)
        Fill(parent=self, align=uiconst.TOALL, color=(1.0, 1.0, 1.0, 0.05))

    def _update(self):
        self._content.Flush()
        if self._icon is None:
            return
        eveLabel.EveCaptionSmall(parent=self._content, align=uiconst.TOTOP, text=self._icon.name)
        eveLabel.EveLabelMedium(parent=self._content, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=self._icon.icon_id, color=TextColor.SECONDARY)
        eveLabel.EveLabelLarge(parent=self._content, align=uiconst.TOTOP, top=16, padding=(0, 0, 0, 4), text='Available sizes')
        size_grid = LayoutGrid(parent=ContainerAutoSize(parent=self._content, align=uiconst.TOTOP), align=uiconst.TOPLEFT, columns=2, cellSpacing=(4, 4))
        for size in reversed(self._icon.sizes):
            Sprite(parent=size_grid, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=self._icon, width=size, height=size)
            eveLabel.EveLabelSmall(parent=size_grid, align=uiconst.CENTERLEFT, text='{}px'.format(size))

        eveLabel.EveLabelLarge(parent=self._content, align=uiconst.TOTOP, top=16, padding=(0, 0, 0, 4), text='Usage')
        Usage(parent=self._content, align=uiconst.TOTOP, icon=self._icon)
        eveLabel.EveLabelLarge(parent=self._content, align=uiconst.TOTOP, top=16, padding=(0, 0, 0, 4), text='Tags')
        tag_flow = FlowContainer(parent=self._content, align=uiconst.TOTOP, contentSpacing=(4, 4))
        for tag in sorted(self._icon.tags):
            Tag(parent=tag_flow, align=uiconst.NOALIGN, tag=tag, on_click=lambda _tag = tag: self._on_tag_clicked(_tag))


class Tag(ContainerAutoSize):
    COLOR_IDLE = (1.0, 1.0, 1.0, 0.1)
    COLOR_HOVER = (1.0, 1.0, 1.0, 0.4)

    def __init__(self, parent, align, tag, on_click):
        self._on_click = on_click
        super(Tag, self).__init__(parent=parent, align=align, alignMode=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        eveLabel.EveLabelMedium(parent=self, align=uiconst.TOPLEFT, padding=(8, 4, 8, 4), text=tag)
        self._fill = Fill(parent=self, align=uiconst.TOALL, color=self.COLOR_IDLE)

    def OnClick(self, *args):
        self._on_click()

    def OnMouseEnter(self, *args):
        eveui.animate(self._fill, 'color', end_value=self.COLOR_HOVER, duration=0.1)

    def OnMouseExit(self, *args):
        eveui.animate(self._fill, 'color', end_value=self.COLOR_IDLE, duration=0.3)


class Usage(ContainerAutoSize):

    def __init__(self, parent, align, icon):
        super(Usage, self).__init__(parent=parent, align=align, alignMode=uiconst.TOPLEFT)
        icon_path = 'eveicon.{}'.format(icon.icon_id)
        eveLabel.EveLabelMedium(parent=self, align=uiconst.TOPLEFT, padding=8, text=icon_path)
        ButtonIcon(parent=self, align=uiconst.CENTERRIGHT, left=4, width=24, height=24, texturePath=eveicon.copy, iconSize=16, hint='Copy', func=lambda *args: blue.pyos.SetClipboardData(icon_path))
        Fill(parent=self, align=uiconst.TOALL, color=(0.0, 0.0, 0.0, 0.5))


class IconEntry(Container):
    FILL_OPACITY_IDLE = 0.0
    FILL_OPACITY_HOVERED = 0.04
    FILL_OPACITY_SELECTED = 0.1

    def __init__(self, parent, align, icon, selected = False, on_click = None):
        self._icon = icon
        self._selected = selected
        self._on_click = on_click
        self._hovered = False
        self._fill = None
        super(IconEntry, self).__init__(parent=parent, align=align, width=112, height=128, state=uiconst.UI_PICKCHILDREN if on_click is None else uiconst.UI_NORMAL)
        max_size = 64
        icon_size = reduce(lambda a, b: max(min(max_size, a), min(max_size, b)), self._icon.sizes)
        Sprite(parent=Container(parent=self, align=uiconst.TOTOP, height=80), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=icon.resolve(icon_size), width=icon_size, height=icon_size)
        carbonui.TextDetail(parent=Container(parent=self, align=uiconst.TOALL, padding=(8, 0, 8, 8)), align=uiconst.TOTOP, text=eveformat.center(icon.name), color=TextColor.DISABLED)
        self._update_fill()

    @property
    def icon(self):
        return self._icon

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        if self._selected != value:
            self._selected = value
            self._update_fill()

    def _update_fill(self):
        opacity = 0.0
        if self._selected:
            opacity = self.FILL_OPACITY_SELECTED
        elif self._hovered:
            opacity = self.FILL_OPACITY_HOVERED
        if opacity > 0.0:
            self._prepare_fill()
        if self._fill is not None:
            eveui.fade(self._fill, end_value=opacity, duration=0.2)

    def _prepare_fill(self):
        if self._fill is None:
            self._fill = Fill(bgParent=self, align=uiconst.TOALL, color=(1.0, 1.0, 1.0), opacity=0.0)

    def OnClick(self):
        if self._on_click:
            self._on_click()

    def OnMouseEnter(self):
        if self._on_click:
            self._hovered = True
            self._update_fill()

    def OnMouseExit(self):
        if self._on_click:
            self._hovered = False
            self._update_fill()
