#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agentinteraction\npcinteractionview.py
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.uianimations import animations
import agentinteraction.constUI as paddingConst
from agentinteraction.rewardsview import RewardsView
from agentinteraction.textutils import fix_text
from agentinteraction.warningpanel import CollateralPanel, DisclaimerPanel, GrantedItemsPanel, ShipRequirementsPanel
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from localization import GetByMessageID
from carbonui.primitives.collapsibleContainer import CollapsibleContainer
LINE_HEIGHT = 1
TOP_LINE_PADDING_BOTTOM = 8
LORE_HEIGHT = 120
SCROLLBAR_COLOR = Color.GRAY5
LORE_SCROLLBAR_PADDING = 35
BUTTON_PADDING_TOP = 30
BUTTON_PADDING_BOTTOM = 2

class NpcInteractionView(Container):
    default_name = 'NpcInteractionView'

    def __init__(self, npc_character, inner_padding = (0, 0, 0, 0), **kwargs):
        self._inner_padding = inner_padding
        self.npc_character = npc_character
        self.subcontainer_lore = None
        self.lore_autosize = None
        self.lore_text = ''
        self.scroll = None
        self.end_line = None
        super(NpcInteractionView, self).__init__(**kwargs)
        self._build_content()

    @property
    def inner_padding(self):
        return self._inner_padding

    @inner_padding.setter
    def inner_padding(self, value):
        if isinstance(value, (int, float)):
            value = (value,
             value,
             value,
             value)
        if self._inner_padding != value:
            self._inner_padding = value
            self._update_scroll_padding()
            self._update_buttons_padding()

    def _build_content(self):
        self._build_loading_wheel()
        self.content_cont = Container(name='content_cont', parent=self)
        self._build_buttons()
        self._build_end_line()
        self.scroll = ScrollContainer(name='scroll', parent=self.content_cont, align=uiconst.TOALL, scrollBarColor=SCROLLBAR_COLOR, scrollBarPadding=10, innerPadding=(0, 0, 0, 0), padding=self._get_scroll_padding())
        self.scroll.onSizeChangeSignal.connect(self.on_scroll_size_changed)
        self.inner_scroll_cont = ContainerAutoSize(name='inner_scroll_cont', parent=self.scroll, align=uiconst.TOTOP)
        self._build_title_cont()
        self._build_title()
        self._build_top_line()
        self._build_lore()
        self._build_objectives()
        self._build_ship_requirements_warning()
        self._build_disclaimer()
        self._build_granted_items()
        self._build_collateral()
        self._build_rewards()

    def _get_scroll_padding(self):
        pad_left, pad_top, pad_right, _ = self.inner_padding
        return (pad_left,
         pad_top,
         pad_right,
         0)

    def _update_scroll_padding(self):
        if self.scroll:
            self.scroll.padding = self._get_scroll_padding()

    def _build_loading_wheel(self):
        self.loading_wheel = LoadingWheel(name='loading_wheel', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.loading_wheel.display = False

    def _build_buttons(self):
        self.buttonGroup = ButtonGroup(name='container_buttons', parent=self.content_cont, align=uiconst.TOBOTTOM, padding=self._get_buttons_padding(), button_size_mode=ButtonSizeMode.STRETCH)

    def _get_buttons_padding(self):
        pad_left, pad_top, pad_right, pad_bottom = self.inner_padding
        return (pad_left,
         pad_bottom,
         pad_right,
         pad_bottom)

    def _update_buttons_padding(self):
        if self.buttonGroup:
            self.buttonGroup.padding = self._get_buttons_padding()

    def _build_title_cont(self):
        self.container_title = ContainerAutoSize(name='container_title', parent=self.inner_scroll_cont, align=uiconst.TOTOP, padding=(0,
         0,
         0,
         paddingConst.PADDING_XSMALL), alignMode=uiconst.TOTOP)

    def _build_title(self):
        self.title = Label(name='label_title', parent=self.container_title, align=uiconst.TOTOP, fontsize=paddingConst.HEADER_SIZE_BIG, color=Color.WHITE)

    def _build_top_line(self):
        container_top_line = Container(name='container_top_line', parent=self.inner_scroll_cont, align=uiconst.TOTOP, height=LINE_HEIGHT, padding=(0,
         0,
         0,
         TOP_LINE_PADDING_BOTTOM))
        Line(name='top_line', parent=container_top_line, align=uiconst.TOALL, weight=LINE_HEIGHT)

    def _build_lore(self):
        self.container_lore = ContainerAutoSize(name='container_lore', parent=self.inner_scroll_cont, align=uiconst.TOTOP)
        self._build_lore_content()

    def _build_lore_content(self):
        if not self.lore_autosize or self.lore_autosize.destroyed:
            self.lore_autosize = CollapsibleContainer(name='lore_autosize', parent=self.container_lore, align=uiconst.TOTOP, clipChildren=True)
        self.lore_autosize.set_text(self.lore_text)

    def _build_objectives(self):
        self.container_objectives = Container(name='container_objectives', parent=self.inner_scroll_cont, align=uiconst.TOTOP, height=100)

    def _build_ship_requirements_warning(self):
        self.container_ship_requirements_warning = ShipRequirementsPanel(name='container_ship_requirements_warning', parent=self.inner_scroll_cont, align=uiconst.TOTOP)
        self.container_ship_requirements_warning.Hide()

    def _build_disclaimer(self):
        self.container_disclaimer = DisclaimerPanel(name='container_disclaimer', parent=self.inner_scroll_cont, align=uiconst.TOTOP)
        self.container_disclaimer.Hide()

    def _build_granted_items(self):
        self.container_granted_items = GrantedItemsPanel(name='container_granted_items', parent=self.inner_scroll_cont, align=uiconst.TOTOP)
        self.container_granted_items.Hide()

    def _build_collateral(self):
        self.container_collateral = CollateralPanel(name='container_collateral', parent=self.inner_scroll_cont, align=uiconst.TOTOP)
        self.container_collateral.Hide()

    def _build_rewards(self):
        self.container_rewards = RewardsView(name='container_rewards', parent=self.inner_scroll_cont, align=uiconst.TOTOP, padding=(0,
         paddingConst.PADDING_SMALL,
         0,
         0))
        self.container_rewards.Hide()

    def _build_end_line(self):
        self.end_line = Line(parent=self.content_cont, align=uiconst.TOBOTTOM_NOPUSH, top=-1)

    def update_granted_items(self, items):
        self.container_granted_items.update_items(items)
        if items:
            self.container_granted_items.Show()
        else:
            self.container_granted_items.Hide()

    def update_normal_rewards(self, items):
        self.container_rewards.update_normal_rewards(items)
        if items:
            self.container_rewards.Show()
        else:
            self.container_rewards.Hide()

    def update_bonus_rewards(self, items):
        self.container_rewards.update_bonus_rewards(items)
        if items:
            self.container_rewards.Show()
        else:
            self.container_rewards.Hide()

    def clear_rewards(self):
        self.container_rewards.clear_rewards()
        self.container_rewards.Hide()

    def update_collateral(self, items):
        self.container_collateral.update_items(items)
        if items:
            self.container_collateral.Show()
        else:
            self.container_collateral.Hide()

    def update_disclaimer(self, disclaimer):
        if disclaimer:
            self.container_disclaimer.Show()
            self.container_disclaimer.set_text(disclaimer)
        else:
            self.container_disclaimer.Hide()

    def update_ship_requirements(self, should_show):
        if should_show:
            self.container_ship_requirements_warning.Show()
        else:
            self.container_ship_requirements_warning.Hide()

    def update_ship_requirements_info(self, dungeon_id = None):
        self.container_ship_requirements_warning.set_restrictions_info(dungeon_id, in_valid_ship=False, ship_window_header=self.title.text)

    def update_title(self, title):
        if title:
            self.title.SetText(GetByMessageID(title))
            self.container_title.Show()
        else:
            self.container_title.Hide()

    def update_lore(self, lore, show_all = False):
        self.lore_text = fix_text(lore)
        self.lore_autosize.set_text(self.lore_text, show_all)

    def update_buttons(self, actions, controller):
        self.buttonGroup.FlushButtons()
        for label, func, kwargs in reversed(actions):
            self.buttonGroup.AddButton(label, func, **(kwargs or {}))

    def update_loading_state(self, is_loading):
        if is_loading:
            self.loading_wheel.display = True
            self.content_cont.opacity = 0
        else:
            self.loading_wheel.display = False
            animations.FadeIn(self.content_cont)

    def disable_buttons(self):
        for button in self.buttonGroup.buttons:
            button.Disable()

    def enable_buttons(self):
        for button in self.buttonGroup.buttons:
            button.Enable()

    def show_objectives(self):
        self.container_objectives.Show()

    def hide_objectives(self):
        self.container_objectives.Hide()

    def on_scroll_size_changed(self, *args):
        self.update_end_line()

    def update_end_line(self):
        if not self.scroll or not self.end_line:
            return
        if self.scroll.IsVerticalScrollBarVisible():
            self.end_line.Show()
        else:
            self.end_line.Hide()

    def Close(self):
        if self.scroll:
            self.scroll.onSizeChangeSignal.disconnect(self.on_scroll_size_changed)
        super(NpcInteractionView, self).Close()
