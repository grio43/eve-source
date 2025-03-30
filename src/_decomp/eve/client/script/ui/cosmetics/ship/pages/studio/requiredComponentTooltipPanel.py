#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\requiredComponentTooltipPanel.py
import eveicon
from carbonui import PickState, Align, ButtonVariant
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from cosmetics.client.shipSkinComponentTradingSvc import get_ship_skin_component_trading_svc
from cosmetics.client.shipSkinSequencingSvc import get_ship_skin_sequencing_svc
from cosmetics.client.ships.skins.live_data import current_skin_design
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.cosmetics.ship.pages.store.buyComponentDialogue import BuyComponentDialogue
from localization import GetByLabel

class RequiredComponentTooltipPanel(TooltipPanel):
    default_columns = 1

    def __init__(self, component_instance, title = None, text = None, show_warning = False, **kw):
        super(RequiredComponentTooltipPanel, self).__init__(**kw)
        self.component_instance = component_instance
        self.LoadStandardSpacing()
        self.AddMediumHeader(text=title)
        if text:
            self.AddLabelMedium(text=text, wrapWidth=300)
        if show_warning and self.component_instance:
            warning_text = self.get_warning_text()
            if warning_text:
                self.AddLabelMedium(text=warning_text, wrapWidth=300, color=eveColor.DANGER_RED, padTop=8)
        if self.component_instance and show_warning:
            self.pickState = PickState.ON
            self.construct_buy_buttons()

    def construct_buy_buttons(self):
        listings = get_ship_skin_component_trading_svc().get_component_listings(self.component_instance.component_id)
        if listings:
            button_group = ButtonGroup(parent=self, align=Align.TOTOP, button_size_mode=ButtonSizeMode.DYNAMIC, padTop=8)
            Button(parent=button_group, hint=GetByLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'), func=self.on_view_on_market_button, texturePath=eveicon.market_details, variant=ButtonVariant.GHOST)
            Button(parent=button_group, label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/BuyElement'), func=lambda *args: self.on_buy_component_button(listings[0]), variant=ButtonVariant.PRIMARY)
        else:
            Button(parent=self, align=Align.CENTERBOTTOM, label=GetByLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'), func=self.on_view_on_market_button, texturePath=eveicon.market_details, variant=ButtonVariant.GHOST, padTop=8)

    def get_warning_text(self):
        component_data = self.component_instance.get_component_data()
        if component_data.get_item_type(ComponentLicenseType.LIMITED):
            layout = current_skin_design.get().slot_layout
            number_of_runs = get_ship_skin_sequencing_svc().get_num_runs()
            num_required = number_of_runs * layout.get_amount_of_components_with_license_type(self.component_instance.component_id)
            return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/NotEnoughLimitedDesignElements', num_required=num_required)
        if component_data.get_item_type(ComponentLicenseType.UNLIMITED):
            return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/NotEnoughUnlimitedDesignElements')

    def on_view_on_market_button(self, *args):
        component_data = self.component_instance.get_component_data()
        item_type_id = component_data.get_item_type(ComponentLicenseType.LIMITED)
        if not item_type_id:
            item_type_id = component_data.get_item_type(ComponentLicenseType.UNLIMITED)
        if item_type_id:
            sm.GetService('marketutils').ShowMarketDetails(item_type_id)

    def on_buy_component_button(self, listing):
        dialogue = BuyComponentDialogue(listing=listing)
        dialogue.ShowModal()
