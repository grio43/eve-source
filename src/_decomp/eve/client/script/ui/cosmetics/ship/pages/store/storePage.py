#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\storePage.py
from carbonui import Align
from carbonui.control.tabGroup import TabGroup
from carbonui.primitives.container import Container
from cosmetics.client.ships.ship_skin_signals import on_component_listing_cache_invalidated, on_skin_listing_cache_invalidated
from cosmetics.client.ships.skins.live_data import current_skin_design
from cosmetics.client.ships.skins.static_data.store_section import StoreSection
from eve.client.script.ui.cosmetics.ship import shipUtil
from eve.client.script.ui.cosmetics.ship.const import SkinrPage
from eve.client.script.ui.cosmetics.ship.pages.store import storeSignals
from eve.client.script.ui.cosmetics.ship.pages.store.componentBrowser import ComponentBrowser
from eve.client.script.ui.cosmetics.ship.pages.store.componentListingDetailsContainer import ComponentListingDetailsContainer
from eve.client.script.ui.cosmetics.ship.pages.store.skinBrowser import SkinBrowser
from eve.client.script.ui.cosmetics.ship.pages.store.skinListingDetailsContainer import SkinListingDetailsContainer
from localization import GetByLabel
from eve.client.script.ui.cosmetics.ship.pages import current_page

class StorePage(Container):
    default_padding = (32, 96, 32, 32)
    is_loaded = False

    def load_panel(self, page_id = None, page_args = None):
        if not self.is_loaded:
            self.is_loaded = True
            self.construct_layout()
            self.connect_signals()
        self.left_cont.Flush()
        self.left_cont.FlagForceUpdateAlignment()
        self.details_cont = None
        self.selected_listing = None
        if SkinrPage.STORE_SKINS in (page_id, page_args):
            self.show_skins(page_args)
        elif SkinrPage.STORE_COMPONENTS in (page_id, page_args):
            self.show_components(page_args)
        else:
            self.tab_group.AutoSelect()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(StorePage, self).Close()

    def connect_signals(self):
        storeSignals.on_component_listing_selected.connect(self.on_component_listing_selected)
        storeSignals.on_skin_listing_selected.connect(self.on_skin_listing_selected)
        on_component_listing_cache_invalidated.connect(self._on_component_listing_cache_invalidated)
        on_skin_listing_cache_invalidated.connect(self._on_skin_listing_cache_invalidated)

    def disconnect_signals(self):
        storeSignals.on_component_listing_selected.disconnect(self.on_component_listing_selected)
        storeSignals.on_skin_listing_selected.disconnect(self.on_skin_listing_selected)
        on_component_listing_cache_invalidated.disconnect(self._on_component_listing_cache_invalidated)
        on_skin_listing_cache_invalidated.disconnect(self._on_skin_listing_cache_invalidated)

    def on_skin_listing_selected(self, listing, *args):
        self.show_skin_listing_details(listing)

    def on_component_listing_selected(self, listing):
        self.show_component_listing_details(listing)

    def _on_component_listing_cache_invalidated(self, *args):
        if isinstance(self.details_cont, ComponentListingDetailsContainer):
            self.show_component_listing_details(listing=None)

    def _on_skin_listing_cache_invalidated(self, *args):
        if isinstance(self.details_cont, SkinListingDetailsContainer):
            self.show_skin_listing_details(listing=None)

    def show_component_listing_details(self, listing):
        self.left_cont.Flush()
        if listing:
            self.details_cont = ComponentListingDetailsContainer(parent=self.left_cont, listing=listing, top=80)
            self.details_cont.appear()
        else:
            self.hide_listing_details()

    def show_skin_listing_details(self, listing):
        if self.selected_listing == listing:
            return
        self.left_cont.Flush()
        if listing:
            self.details_cont = SkinListingDetailsContainer(parent=self.left_cont, listing=listing, top=80)
            self.selected_listing = listing
            self.details_cont.appear()
        else:
            self.hide_listing_details()

    def hide_listing_details(self):
        if self.details_cont:
            current_skin_design.create_blank_design(shipUtil.get_active_ship_type_id())
            self.details_cont.disappear()
            self.selected_listing = None

    def show_skin(self, skin_listing):
        self.show_skins(StoreSection.SKINS_LINKED_LISTING_AND_ALL, skin_listing)
        storeSignals.on_skin_listing_selected(skin_listing, self)

    def show_skins(self, section_id = None, linked_listing = None):
        self.component_browser.display = False
        self.skin_browser.display = True
        self.skin_browser.LoadPanel(section_id, linked_listing)
        self.tab_group.SelectByID(SkinrPage.STORE_SKINS, silent=True, useCallback=False)
        if section_id is None:
            current_page.set_sub_page(SkinrPage.STORE, SkinrPage.STORE_SKINS)

    def show_components(self, category = None):
        self.component_browser.display = True
        self.component_browser.LoadPanel(category)
        self.skin_browser.display = False
        self.tab_group.SelectByID(SkinrPage.STORE_COMPONENTS, silent=True, useCallback=False)
        if category is None:
            current_page.set_sub_page(SkinrPage.STORE, SkinrPage.STORE_COMPONENTS)

    def construct_layout(self):
        self.right_cont = Container(name='right_cont', parent=self, align=Align.TORIGHT_PROP, width=0.55, maxWidth=752)
        self.left_cont = Container(name='left_cont', parent=self, padding=(0, 0, 64, 16))
        self.construct_right_cont()

    def construct_right_cont(self):
        self.tab_group = TabGroup(parent=self.right_cont, align=Align.TOTOP, show_line=False, callback=self.on_tab_group, settingsID='SKINRStorePageTopLevel2')
        self.skin_browser = SkinBrowser(parent=self.right_cont)
        self.tab_group.AddTab(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/SKINs'), tabID=SkinrPage.STORE_SKINS)
        self.component_browser = ComponentBrowser(parent=self.right_cont)
        self.tab_group.AddTab(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/DesignElements'), tabID=SkinrPage.STORE_COMPONENTS)

    def on_tab_group(self, page_id, old_page_id):
        storeSignals.on_skin_listing_selected(None, None)
        if page_id == SkinrPage.STORE_SKINS:
            self.show_skins()
        elif page_id == SkinrPage.STORE_COMPONENTS:
            self.show_components()
