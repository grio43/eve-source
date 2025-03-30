#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\collection\componentLicenseInfo.py
from carbonui import Align, AxisAlignment, Density, uiconst
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from eve.client.script.ui.cosmetics.ship.const import SkinrPage
from eve.client.script.ui.cosmetics.ship.controls.componentInfo import ComponentInfo
from eve.client.script.ui.cosmetics.ship.pages.collection.baseLicenseInfo import LicenseInfo
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSignals
from localization import GetByLabel

class ComponentLicenseInfo(LicenseInfo):

    def __init__(self, *args, **kwargs):
        self.component_license = None
        super(ComponentLicenseInfo, self).__init__(*args, **kwargs)

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(ComponentLicenseInfo, self).Close()

    def connect_signals(self):
        super(ComponentLicenseInfo, self).connect_signals()
        studioSignals.on_page_opened.connect(self.on_page_opened)

    def disconnect_signals(self):
        super(ComponentLicenseInfo, self).disconnect_signals()
        studioSignals.on_page_opened.disconnect(self.on_page_opened)

    def construct_layout(self):
        self.right_cont = ContainerAutoSize(name='right_cont', parent=self, align=Align.TORIGHT)
        self.left_cont = Container(name='component_info_container', parent=self, clipChildren=True, align=Align.TOALL)
        self.construct_button_group()

    def construct_button_group(self):
        self.button_group = ButtonGroup(parent=self.right_cont, align=Align.BOTTOMRIGHT, button_alignment=AxisAlignment.END, density=Density.EXPANDED, button_size_mode=ButtonSizeMode.DYNAMIC, padTop=64)

    def update(self):
        self.update_component_info()
        self.update_buttons()

    def update_component_info(self):
        self.left_cont.Flush()
        if not self.component_license:
            return
        ComponentInfo(name='component_info', parent=self.left_cont, align=Align.TOBOTTOM, component_data=self.component_license.get_component_data(), license_type=self.component_license.license_type, runs_remaining=self.component_license.remaining_license_uses)

    def update_buttons(self):
        self.button_group.Flush()
        if not self.component_license:
            return
        if self.component_license.license_type == ComponentLicenseType.UNLIMITED:
            return
        if not self.get_market_type_id():
            return
        self.button_group.add_button(Button(label=GetByLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'), func=self.on_market_button))

    def on_market_button(self, *args):
        sm.GetService('marketutils').ShowMarketDetails(self.get_market_type_id())

    def get_market_type_id(self):
        if not self.component_license:
            return None
        for item_data in self.component_license.get_component_data().component_item_data_by_type_id.values():
            if item_data.license_type != self.component_license.license_type:
                continue
            if item_data.type_id:
                return item_data.type_id

    def on_first_party_skin_selected(self, *args):
        self.fade_out()

    def on_unactivated_skin_license_selected(self, skin_license):
        self.fade_out()

    def on_activated_skin_license_selected(self, skin_license):
        self.fade_out()

    def on_page_opened(self, page_id, page_args, last_page_id, animate = True):
        any_collection_page = [SkinrPage.COLLECTION, SkinrPage.COLLECTION_COMPONENTS, SkinrPage.COLLECTION_SKINS]
        if page_id in any_collection_page and last_page_id in any_collection_page:
            self.fade_out()

    def on_component_license_selected(self, component_license):
        self.component_license = component_license
        if component_license:
            self.fade_out(callback=self.on_fade_out_complete)
        else:
            self.fade_out()

    def fade_out(self, callback = None):
        self.state = uiconst.UI_DISABLED
        animations.FadeTo(self, self.opacity, 0.0, uiconst.TIME_EXIT, callback=callback)

    def on_fade_out_complete(self):
        self.update()
        self.fade_in()

    def fade_in(self):
        self.state = uiconst.UI_PICKCHILDREN
        animations.FadeTo(self, self.opacity, 1.0, 0.5)
