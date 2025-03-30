#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\collection\collectionPage.py
from carbonui import Align
from carbonui.control.tabGroup import TabGroup
from carbonui.primitives.container import Container
from cosmetics.client.ships import ship_skin_signals
from eve.client.script.ui.cosmetics.ship.const import SkinrPage
from eve.client.script.ui.cosmetics.ship.pages.collection import collectionSignals
from eve.client.script.ui.cosmetics.ship.pages.collection.componentLicenseBrowser import ComponentLicenseBrowser
from eve.client.script.ui.cosmetics.ship.pages.collection.componentLicenseInfo import ComponentLicenseInfo
from eve.client.script.ui.cosmetics.ship.pages.collection.skinLicenseBrowser import SkinLicenseBrowser
from eve.client.script.ui.cosmetics.ship.pages.collection.skinLicenseInfo import SkinLicenseInfo
from eve.client.script.ui.cosmetics.ship.pages import current_page
from localization import GetByLabel

class CollectionPage(Container):
    default_padding = (32, 96, 32, 32)
    is_loaded = False

    def load_panel(self, page_id = None, page_args = None):
        if not self.is_loaded:
            self.is_loaded = True
            self.construct_layout()
            self.connect_signals()
        self.left_cont.FlagForceUpdateAlignment()
        if SkinrPage.COLLECTION_SKINS in (page_id, page_args):
            self.show_skins(page_args)
        elif SkinrPage.COLLECTION_COMPONENTS in (page_id, page_args):
            self.show_components(page_args)
        else:
            self.tab_group.AutoSelect()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(CollectionPage, self).Close()

    def connect_signals(self):
        self.on_display_changed.connect(self._on_display_changed)
        ship_skin_signals.on_skin_license_updated.connect(self.on_skin_license_updated)

    def disconnect_signals(self):
        self.on_display_changed.disconnect(self._on_display_changed)
        ship_skin_signals.on_skin_license_updated.disconnect(self.on_skin_license_updated)

    def _on_display_changed(self, *args):
        if not self.display:
            self.hide_selection_details()

    def construct_layout(self):
        self.right_cont = Container(name='right_cont', parent=self, align=Align.TORIGHT_PROP, width=0.55, maxWidth=920)
        self.left_cont = Container(name='left_cont', parent=self, padding=(0, 0, 64, 16))
        self.construct_left_cont()
        self.construct_right_cont()

    def construct_left_cont(self):
        self.selected_skin_details = SkinLicenseInfo(name='skin_license_info', parent=self.left_cont, top=80)
        self.selected_component_details = ComponentLicenseInfo(name='component_license_info', parent=self.left_cont, top=80)

    def construct_right_cont(self):
        self.tab_group = TabGroup(parent=self.right_cont, align=Align.TOTOP, show_line=False, callback=self.on_tab_group, settingsID='SKINRStorePageTopLevel')
        self.skin_browser = SkinLicenseBrowser(parent=self.right_cont)
        self.tab_group.AddTab(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/SKINs'), tabID=SkinrPage.COLLECTION_SKINS)
        self.component_browser = ComponentLicenseBrowser(parent=self.right_cont, display=False)
        self.tab_group.AddTab(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/DesignElements'), tabID=SkinrPage.COLLECTION_COMPONENTS)

    def on_tab_group(self, page_id, old_page_id):
        self.hide_selection_details()
        if page_id == SkinrPage.COLLECTION_SKINS:
            self.show_skins()
        elif page_id == SkinrPage.COLLECTION_COMPONENTS:
            self.show_components()

    def hide_selection_details(self):
        self.selected_skin_details.fade_out()
        self.selected_component_details.fade_out()

    def show_skins(self, section_id = None):
        self.component_browser.display = False
        self.skin_browser.display = True
        self.skin_browser.LoadPanel(section_id)
        self.tab_group.SelectByID(SkinrPage.COLLECTION_SKINS, silent=True, useCallback=False)
        if section_id is None:
            current_page.set_sub_page(SkinrPage.COLLECTION, SkinrPage.COLLECTION_SKINS)

    def show_components(self, category = None):
        self.component_browser.display = True
        self.component_browser.LoadPanel(category)
        self.skin_browser.display = False
        self.tab_group.SelectByID(SkinrPage.COLLECTION_COMPONENTS, silent=True, useCallback=False)
        if category is None:
            current_page.set_sub_page(SkinrPage.COLLECTION, SkinrPage.COLLECTION_COMPONENTS)

    def on_skin_license_updated(self, license_id, license_data):
        if self.selected_skin_details.license_id == license_id:
            self.selected_skin_details.fade_out()
            collectionSignals.on_skin_license_details_clear()
