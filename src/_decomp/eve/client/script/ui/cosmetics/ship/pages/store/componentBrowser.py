#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\componentBrowser.py
import eveicon
from carbonui import Align
from carbonui.button.menu import MenuButtonIcon
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from cosmetics.client.ships.ship_skin_signals import on_component_listing_cache_invalidated
from cosmetics.client.ships.skins.live_data.section_controller import StoreNanocoatingComponentsSection, StoreMetallicComponentsSection, StorePatternComponentsSection
from cosmetics.common.ships.skins.static_data.component_category import ComponentCategory
from cosmetics.common.ships.skins.static_data.component_finish import ComponentFinish
from cosmetics.common.ships.skins.util import ComponentListingOrder
from eve.client.script.ui.cosmetics.ship.controls.baseCardSectionContainer import BaseCardSectionContainer
from eve.client.script.ui.cosmetics.ship.pages.cards.componentListingCard import ComponentListingCard
from eve.client.script.ui.cosmetics.ship.pages.store import storeSignals, storeSettings
from eve.client.script.ui.cosmetics.ship.pages.store.storeSettings import components_sort_by_setting
from localization import GetByLabel
MAX_NUM_PER_PAGE = 20

class ComponentBrowser(ScrollContainer):

    def __init__(self, **kw):
        super(ComponentBrowser, self).__init__(**kw)
        self.is_loaded = False

    def LoadPanel(self, category = None):
        self.reconstruct_layout()
        self.Flush()
        if category == ComponentCategory.PATTERN:
            ComponentStoreViewAllSectionContainer(name='materials_section', parent=self, align=Align.TOTOP, padTop=32, section_controller=StorePatternComponentsSection(MAX_NUM_PER_PAGE))
        elif category == ComponentCategory.MATERIAL:
            NanocoatinComponentStoreViewAllSectionContainer(name='materials_section', parent=self, align=Align.TOTOP, padTop=32, section_controller=StoreNanocoatingComponentsSection(MAX_NUM_PER_PAGE))
        elif category == ComponentCategory.METALLIC:
            ComponentStoreViewAllSectionContainer(name='materials_section', parent=self, align=Align.TOTOP, padTop=32, section_controller=StoreMetallicComponentsSection(MAX_NUM_PER_PAGE))
        else:
            self.construct_landing_page()
        self.appear()

    def reconstruct_layout(self):
        self.Flush()

    def construct_landing_page(self):
        ComponentStoreSectionContainer(name='materials_section', parent=self, align=Align.TOTOP, section_controller=StoreNanocoatingComponentsSection(num_per_page=None), single_row=True, padTop=32)
        ComponentStoreSectionContainer(name='metallics_section', parent=self, align=Align.TOTOP, section_controller=StoreMetallicComponentsSection(num_per_page=None), single_row=True, padTop=48, max_entries=5)
        ComponentStoreSectionContainer(name='pattern_section', parent=self, align=Align.TOTOP, section_controller=StorePatternComponentsSection(num_per_page=None), single_row=True, padTop=48, max_entries=5)

    def appear(self):
        animations.FadeTo(self, 0.0, 1.0, duration=0.3)


class ComponentStoreSectionContainer(BaseCardSectionContainer):

    def on_sort_by_setting(self, *args):
        self.reconstruct_cards()

    def connect_signals(self):
        super(ComponentStoreSectionContainer, self).connect_signals()
        components_sort_by_setting.on_change.connect(self.on_sort_by_setting)
        storeSignals.on_component_listing_selected.connect(self.on_skin_license_selected)
        on_component_listing_cache_invalidated.connect(self._on_component_listing_cache_invalidated)

    def disconnect_signals(self):
        super(ComponentStoreSectionContainer, self).disconnect_signals()
        components_sort_by_setting.on_change.disconnect(self.on_sort_by_setting)
        storeSignals.on_component_listing_selected.disconnect(self.on_skin_license_selected)
        on_component_listing_cache_invalidated.disconnect(self._on_component_listing_cache_invalidated)

    def construct_card(self, listing):
        return ComponentListingCard(parent=self.content, listing=listing)

    def on_skin_license_selected(self, listing):
        for card in self.cards:
            if card.listing != listing:
                card.is_selected = False

    def _on_component_listing_cache_invalidated(self, *args):
        self.update()


class SortByMenuButtonIcon(MenuButtonIcon):
    hint = GetByLabel('UI/Common/SortBy')
    default_texturePath = eveicon.bars_sort_ascending

    def GetMenu(self):
        m = MenuData()
        m.AddCaption(self.hint)
        m.AddRadioButton(GetByLabel('UI/Common/Name'), (ComponentListingOrder.NAME, False), components_sort_by_setting)
        m.AddRadioButton(GetByLabel('UI/Inventory/NameReversed'), (ComponentListingOrder.NAME, True), components_sort_by_setting)
        m.AddSeparator()
        m.AddRadioButton(GetByLabel('UI/Market/Marketbase/Price'), (ComponentListingOrder.PRICE, False), components_sort_by_setting)
        m.AddRadioButton(GetByLabel('UI/Market/Marketbase/PriceReversed'), (ComponentListingOrder.PRICE, True), components_sort_by_setting)
        m.AddSeparator()
        m.AddRadioButton(GetByLabel('UI/Common/ColorShade'), (ComponentListingOrder.COLOR_SHADE, False), components_sort_by_setting)
        m.AddRadioButton(GetByLabel('UI/Common/ColorShadeReversed'), (ComponentListingOrder.COLOR_SHADE, True), components_sort_by_setting)
        return m


class ComponentStoreViewAllSectionContainer(ComponentStoreSectionContainer):

    def construct_filter_and_sorting(self):
        SortByMenuButtonIcon(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT)

    def construct_pagination_container(self):
        self.pagination_container = Container(name='pagination_container', parent=self, align=Align.TOTOP, height=32)


class NanocoatingFilterMenuButton(MenuButtonIcon):
    hint = GetByLabel('UI/Common/Filter')
    default_texturePath = eveicon.filter

    def GetMenu(self):
        m = MenuData()
        m.AddCaption(GetByLabel('UI/Personalization/ShipSkins/Finish'))
        m.AddRadioButton(GetByLabel('UI/Common/Any'), None, storeSettings.nanocoating_finish_filter_setting)
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/FinishMatte'), ComponentFinish.MATTE, storeSettings.nanocoating_finish_filter_setting)
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/FinishSatin'), ComponentFinish.SATIN, storeSettings.nanocoating_finish_filter_setting)
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/FinishGloss'), ComponentFinish.GLOSS, storeSettings.nanocoating_finish_filter_setting)
        return m


class NanocoatinComponentStoreViewAllSectionContainer(ComponentStoreViewAllSectionContainer):

    def __init__(self, section_controller, single_row = False, **kw):
        super(NanocoatinComponentStoreViewAllSectionContainer, self).__init__(section_controller, single_row, **kw)
        storeSettings.nanocoating_finish_filter_setting.set(None)

    def __del__(self):
        storeSettings.nanocoating_finish_filter_setting.set(None)

    def connect_signals(self):
        super(NanocoatinComponentStoreViewAllSectionContainer, self).connect_signals()
        storeSettings.nanocoating_finish_filter_setting.on_change.connect(self.on_finish_setting_changed)

    def disconnect_signals(self):
        super(NanocoatinComponentStoreViewAllSectionContainer, self).disconnect_signals()
        storeSettings.nanocoating_finish_filter_setting.on_change.disconnect(self.on_finish_setting_changed)

    def on_finish_setting_changed(self, finish):
        self.update()

    def construct_filter_and_sorting(self):
        super(NanocoatinComponentStoreViewAllSectionContainer, self).construct_filter_and_sorting()
        NanocoatingFilterMenuButton(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT, left=20)
