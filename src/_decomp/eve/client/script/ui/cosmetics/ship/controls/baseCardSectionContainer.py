#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\controls\baseCardSectionContainer.py
import logging
import carbonui
import uthread2
from carbonui import Align, TextColor, Density, TextAlign
from carbonui.button.group import ButtonGroup
from carbonui.control.baseScrollContEntry import LazyLoadVerticalMixin
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.services import deviceSignals
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.cosmetics.ship.pages import current_page
from eve.client.script.ui.cosmetics.ship.pages.cards import cardConst
from eve.client.script.ui.cosmetics.ship.pages.store.paginationButtons import PaginationButtons
from localization import GetByLabel
log = logging.getLogger(__name__)

class BaseCardSectionContainer(ContainerAutoSize, LazyLoadVerticalMixin):
    default_height = 290
    default_minHeight = 290
    default_alignMode = Align.TOTOP

    def __init__(self, section_controller = None, single_row = False, **kw):
        super(BaseCardSectionContainer, self).__init__(**kw)
        self._set_section_controller(section_controller)
        self.reconstruct_listings_thread = None
        self.cards = []
        self.emptyCards = []
        self.pagination_buttons = None
        self.single_row = single_row
        self.selected_card = None
        self.connect_signals()

    def _set_section_controller(self, section_controller = None):
        self.section_controller = section_controller

    def lazy_load(self):
        self.construct_layout()
        self.update()

    def connect_signals(self):
        deviceSignals.on_end_change_device.connect(self.on_end_change_device)
        self.on_size_changed.connect(self._on_size_changed)

    def disconnect_signals(self):
        deviceSignals.on_end_change_device.disconnect(self.on_end_change_device)

    def on_end_change_device(self):
        if self.IsVisible():
            self.reconstruct_cards()

    def _on_size_changed(self, width, height):
        if not self.single_row:
            return
        if not self.IsVisible():
            return
        num_per_page = self.get_num_cards_per_row()
        if self.section_controller.num_per_page < num_per_page:
            self.reconstruct_cards()
            return
        allCards = self.cards + self.emptyCards
        for i, card in enumerate(allCards):
            if i < num_per_page:
                card.Show()
            else:
                card.Hide()

    def Close(self):
        try:
            if self.reconstruct_listings_thread:
                self.reconstruct_listings_thread.kill()
            self.disconnect_signals()
        finally:
            super(BaseCardSectionContainer, self).Close()

    def update(self):
        if not self.is_loaded:
            return
        self.reconstruct_cards()
        uthread2.start_tasklet(self.update_values)

    def update_values(self):
        self.header_name_label.text = self.section_controller.get_name()
        self.update_num_items_label()

    def update_num_items_label(self):
        num_listings = self.section_controller.get_num_entries()
        if num_listings:
            self.num_items_label.text = GetByLabel('UI/Personalization/ShipSkins/SKINR/NumItems', num_items=num_listings)

    def construct_layout(self):
        self.top_cont = Container(name='top_cont', parent=self, align=Align.TOTOP, alignMode=Align.CENTERRIGHT, height=32)
        self.construct_top_right_buttons()
        self.construct_top_cont()
        self.construct_loading_indicators()
        self.content_overlay = Container(name='content_overlay', parent=self, padTop=24)
        self.content = FlowContainer(name='content', parent=self, align=Align.TOTOP, height=128, padTop=24, contentSpacing=(16, 16))

    def construct_loading_indicators(self):
        self.loading_cont = Container(name='loading_cont', parent=self, align=Align.TOTOP_NOPUSH, display=False, padding=(8, 0, 8, 0), height=self._get_card_height(), opacity=0.0)
        LoadingWheel(parent=self.loading_cont, align=Align.CENTER)
        self.no_content_caption = carbonui.TextHeader(parent=self.loading_cont, align=Align.CENTER, padding=(0, 8, 0, 8), text=GetByLabel('UI/Common/NothingFound'), textAlign=TextAlign.CENTER, color=TextColor.SECONDARY, display=False)

    def _get_card_height(self):
        return cardConst.card_height

    def construct_top_right_buttons(self):
        self.top_right_cont = ContainerAutoSize(name='top_right_buttons', parent=self.top_cont, align=Align.TORIGHT)
        self.top_right_buttons = ButtonGroup(parent=self.top_right_cont, align=Align.CENTERRIGHT, density=Density.COMPACT)

    def reconstruct_cards(self, page_num = None):
        if not self.is_loaded:
            return
        if self.reconstruct_listings_thread:
            self.reconstruct_listings_thread.kill()
        self.reconstruct_listings_thread = uthread2.start_tasklet(self._reconstruct_cards, page_num)

    def _reconstruct_cards(self, page_num):
        for card in self.cards:
            if card.is_selected:
                self.selected_card = card
                break

        if self.single_row:
            self.section_controller.num_per_page = self.get_num_cards_per_row()
        card_controllers = self._get_controllers_to_show(page_num)
        self.update_pagination_buttons()
        self.content.Flush()
        self.content_overlay.Flush()
        self.cards = []
        self.emptyCards = []
        if card_controllers:
            self.no_content_caption.display = False
            self.construct_cards(card_controllers)
        else:
            self.construct_empty_state()

    def verify_cards(self):
        for card in self.cards:
            if not card.finished_loading:
                card.construct_live_rendered_icon_sprite()

    def get_num_cards_per_row(self):
        width, _ = self.GetAbsoluteSize()
        num_cards = (width + 16) / (cardConst.card_width + 16)
        return max(1, num_cards)

    def update_pagination_buttons(self):
        self._check_construct_pagination_buttons()
        if self.pagination_buttons or not self.section_controller.is_paginated():
            if self.pagination_buttons:
                if self.section_controller.is_paginated():
                    self.pagination_buttons.Show()
                else:
                    self.pagination_buttons.Hide()

    def construct_empty_state(self):
        card_class = self.section_controller.blank_card_class
        self.no_content_caption.display = False
        if card_class:
            for i in range(self.get_num_cards_per_row()):
                emptyCard = card_class(parent=self.content)
                self.emptyCards.append(emptyCard)

    def construct_cards(self, card_controllers):
        for card_controller in card_controllers:
            card = self.construct_card(card_controller)
            self.cards.append(card)
            if self.selected_card and card.name == self.selected_card.name:
                card.is_selected = True

        if not self.section_controller.is_paginated():
            empty_cards_to_add = self.get_num_cards_per_row() - len(card_controllers)
            if empty_cards_to_add > 0:
                for i in range(empty_cards_to_add):
                    emptyCard = self.section_controller.blank_card_class(parent=self.content)
                    self.emptyCards.append(emptyCard)

    def _check_construct_pagination_buttons(self):
        if self.pagination_buttons:
            return
        self.construct_pagination_container()
        self.pagination_buttons = PaginationButtons(parent=self.pagination_container, align=Align.CENTER, pagination_controller=self.section_controller.pagination_controller, density=Density.COMPACT)
        self.pagination_buttons.on_page_selected.connect(self.on_page_selected)

    def construct_pagination_container(self):
        self.pagination_container = ContainerAutoSize(name='pagination_container', parent=self.top_cont, align=Align.TORIGHT)

    def on_page_selected(self, page_num):
        self.reconstruct_cards(page_num)

    def construct_card(self, card_controller):
        pass

    def _get_controllers_to_show(self, page_num = None):
        try:
            self.loading_cont.display = True
            animations.FadeIn(self.loading_cont, duration=0.3, timeOffset=0.1)
            controllers = self.section_controller.get_card_controllers(page_num)
        except Exception as e:
            log.exception(e)
            return
        finally:
            animations.FadeOut(self.loading_cont, duration=0.3, callback=self.loading_cont.Hide)

        return controllers

    def construct_top_cont(self):
        self.construct_header()
        self.construct_top_right_button()
        self.filter_and_sorting_cont = ContainerAutoSize(parent=self.top_cont, align=Align.TORIGHT, padding=(8, 0, 8, 0))
        self.construct_filter_and_sorting()

    def construct_header(self):
        self.construct_header_layout_grid()
        self.construct_header_name_label()
        self.construct_header_num_items_label()

    def construct_header_layout_grid(self):
        self.header_layout_grid = LayoutGrid(parent=self.top_cont, align=Align.CENTERLEFT, cellSpacing=8, columns=2)

    def construct_header_name_label(self):
        self.header_name_label = carbonui.TextHeadline(parent=self.header_layout_grid, align=Align.CENTERLEFT)

    def construct_header_num_items_label(self):
        self.num_items_label = carbonui.TextBody(parent=self.header_layout_grid, align=Align.CENTERLEFT, color=TextColor.SECONDARY)

    def construct_filter_and_sorting(self):
        pass

    def construct_top_right_button(self):
        if self.single_row:
            page_id, page_args = self.section_controller.get_page_id_and_args()
            Button(name='view_more_btn', parent=self.top_right_buttons, label=GetByLabel('UI/Common/ViewMore'), func=lambda *args: current_page.set_page_id(page_id, page_args))
        else:
            Button(name='view_more_btn', parent=self.top_right_buttons, label=GetByLabel('UI/Commands/Back'), func=lambda *args: current_page.go_back())
