#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\sections\allListings.py
from carbonui import Align
from carbonui.primitives.container import Container
from cosmetics.client.ships.skins.static_data.store_section import StoreSection
from eve.client.script.ui.cosmetics.ship.const import SkinrPage
from eve.client.script.ui.cosmetics.ship.controls.shipFilterMenuButton import ShipFilterMenuButton
from eve.client.script.ui.cosmetics.ship.pages.store import storeSettings
from eve.client.script.ui.cosmetics.ship.pages.store.sections.baseSkinsSection import BaseSkinsSection
from eve.client.script.ui.cosmetics.ship.pages.store.sections.baseSkinsSectionContainer import BaseSkinsSectionContainer, SortByMenuButtonIcon, MAX_NUM_PER_PAGE

class AllSkinsSection(BaseSkinsSection):
    page_id = SkinrPage.STORE_SKINS
    category = StoreSection.SKINS_ALL
    name = 'UI/Personalization/ShipSkins/SKINR/Studio/AllSKINs'

    def get_type_filter(self):
        if self.apply_filtering:
            ship_type = storeSettings.skins_hull_type_filter_setting.get()
            if ship_type:
                return [ship_type]
            return []
        else:
            return []


class AllSkinsSectionContainer(BaseSkinsSectionContainer):

    def _set_section_controller(self, section_controller = None):
        self.section_controller = AllSkinsSection(num_per_page=None, apply_filtering=False)


class ViewAllSkinsSectionContainer(BaseSkinsSectionContainer):

    def __init__(self, **kw):
        super(ViewAllSkinsSectionContainer, self).__init__(**kw)
        storeSettings.skins_hull_type_filter_setting.set(None)

    def _set_section_controller(self, section_controller = None):
        self.section_controller = AllSkinsSection(MAX_NUM_PER_PAGE)

    def connect_signals(self):
        super(ViewAllSkinsSectionContainer, self).connect_signals()
        storeSettings.skins_hull_type_filter_setting.on_change.connect(self.skins_hull_type_filter_setting)

    def disconnect_signals(self):
        super(ViewAllSkinsSectionContainer, self).disconnect_signals()
        storeSettings.skins_hull_type_filter_setting.on_change.disconnect(self.skins_hull_type_filter_setting)

    def skins_hull_type_filter_setting(self, type_id):
        self.reconstruct_cards()

    def construct_filter_and_sorting(self):
        ShipFilterMenuButton(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT, left=20, hull_type_setting=storeSettings.skins_hull_type_filter_setting)
        SortByMenuButtonIcon(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT, show_name_option=False)

    def construct_pagination_container(self):
        self.pagination_container = Container(name='pagination_container', parent=self, align=Align.TOTOP, height=32)


class ViewLinkedListingAndAllSkinsSectionContainer(ViewAllSkinsSectionContainer):

    def __init__(self, linked_listing = None, **kw):
        super(ViewLinkedListingAndAllSkinsSectionContainer, self).__init__(**kw)
        self.linked_listing = linked_listing
        storeSettings.skins_hull_type_filter_setting.set(None)

    def _set_section_controller(self, section_controller = None):
        self.section_controller = AllSkinsSection(MAX_NUM_PER_PAGE)

    def construct_cards(self, card_controllers):
        if self.linked_listing:
            linked_card = self.construct_card(self.linked_listing)
            linked_card.is_selected = True
            self.cards.append(linked_card)
            card_controllers = [ controller for controller in card_controllers if controller.identifier != self.linked_listing.identifier ]
            self.linked_listing = None
        super(ViewLinkedListingAndAllSkinsSectionContainer, self).construct_cards(card_controllers)
