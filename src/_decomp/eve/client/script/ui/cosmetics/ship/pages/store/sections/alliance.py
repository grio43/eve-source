#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\sections\alliance.py
import eveicon
from carbonui import uiconst, Align
from carbonui.button.menu import MenuButtonIcon
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.primitives.container import Container
from cosmetics.client.ships.skins.live_data.skin_listing_target import ListingTargetType, SellerMembershipType
from cosmetics.client.ships.skins.static_data.store_section import StoreSection
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from eve.client.script.ui.cosmetics.ship.const import SkinrPage
from eve.client.script.ui.cosmetics.ship.controls.shipFilterMenuButton import ShipFilterMenuButton
from eve.client.script.ui.cosmetics.ship.pages.store import storeSettings
from eve.client.script.ui.cosmetics.ship.pages.store.sections.baseSkinsSection import BaseSkinsSection
from eve.client.script.ui.cosmetics.ship.pages.store.sections.baseSkinsSectionContainer import BaseSkinsSectionContainer, SortByMenuButtonIcon, MAX_NUM_PER_PAGE
from eve.client.script.ui.cosmetics.ship.pages.store.storeSettings import listed_by_setting
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from inventorycommon import const as invconst
from localization import GetByLabel

class AllianceListingsSection(BaseSkinsSection):
    page_id = SkinrPage.STORE_SKINS
    category = StoreSection.SKINS_ALLIANCE
    name = 'UI/Personalization/ShipSkins/SKINR/Store/AllianceSkins'

    def reset_pagination_controller(self, order_by, ascending):
        self.pagination_controller.reset(self.get_type_filter(), order_by, ascending, self.num_per_page, ListingTargetType.ALLIANCE, SellerMembershipType.UNSPECIFIED)


class AllianceListingsSectionContainer(BaseSkinsSectionContainer):

    def _set_section_controller(self, section_controller = None):
        self.section_controller = AllianceListingsSection(num_per_page=None, apply_filtering=False)

    def construct_header(self):
        self.construct_header_layout_grid()
        self.header_layout_grid.columns = 3
        self.alliance_icon = GetLogoIcon(name='alliance_icon', parent=self.header_layout_grid, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, itemID=session.allianceid, pos=(0, 0, 48, 48))
        self.alliance_icon.OnClick = self.on_alliance_logo_click
        self.construct_header_name_label()
        self.construct_header_num_items_label()

    def on_alliance_logo_click(self, *args):
        sm.GetService('info').ShowInfo(typeID=invconst.typeAlliance, itemID=session.allianceid)

    def construct_cards(self, card_controllers):
        if card_controllers and len(card_controllers) > 0:
            super(AllianceListingsSectionContainer, self).construct_cards(card_controllers)


class AllianceSectionFilterMenuButtonIcon(MenuButtonIcon):
    hint = GetByLabel('UI/Common/Filter')
    default_texturePath = eveicon.filter

    def GetMenu(self):
        m = MenuData()
        m.AddCaption(GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ListedBy'))
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ListedByAnyBrandManager'), SellerMembershipType.BRAND_MANAGER, listed_by_setting)
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ListedByAllianceMember'), SellerMembershipType.MEMBER, listed_by_setting)
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ListedByAnyone'), SellerMembershipType.UNSPECIFIED, listed_by_setting)
        return m


class ViewAllAllianceListingsSection(AllianceListingsSection):

    def get_type_filter(self):
        if self.apply_filtering:
            ship_type = storeSettings.skins_hull_type_filter_setting.get()
            if ship_type:
                return [ship_type]
            return []
        else:
            return []

    def reset_pagination_controller(self, order_by, ascending):
        self.pagination_controller.reset(self.get_type_filter(), order_by, ascending, self.num_per_page, listing_target_type=ListingTargetType.ALLIANCE, seller_membership_type=listed_by_setting.get())


class ViewAllAllianceSkinsSectionContainer(BaseSkinsSectionContainer):

    def __init__(self, **kw):
        storeSettings.skins_hull_type_filter_setting.set(None)
        storeSettings.listed_by_setting.set(SellerMembershipType.UNSPECIFIED)
        super(ViewAllAllianceSkinsSectionContainer, self).__init__(**kw)

    def _set_section_controller(self, section_controller = None):
        self.section_controller = ViewAllAllianceListingsSection(MAX_NUM_PER_PAGE)

    def connect_signals(self):
        super(ViewAllAllianceSkinsSectionContainer, self).connect_signals()
        storeSettings.skins_hull_type_filter_setting.on_change.connect(self.skins_hull_type_filter_setting)
        storeSettings.listed_by_setting.on_change.connect(self.on_listed_by_setting)

    def disconnect_signals(self):
        super(ViewAllAllianceSkinsSectionContainer, self).disconnect_signals()
        storeSettings.skins_hull_type_filter_setting.on_change.disconnect(self.skins_hull_type_filter_setting)
        storeSettings.listed_by_setting.on_change.disconnect(self.on_listed_by_setting)

    def on_listed_by_setting(self, *args):
        self.reconstruct_cards()

    def construct_header(self):
        self.construct_header_layout_grid()
        self.header_layout_grid.columns = 3
        self.alliance_icon = GetLogoIcon(name='alliance_icon', parent=self.header_layout_grid, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, itemID=session.allianceid, pos=(0, 0, 48, 48))
        self.alliance_icon.OnClick = self.on_alliance_logo_click
        self.construct_header_name_label()
        self.construct_header_num_items_label()

    def on_alliance_logo_click(self, *args):
        sm.GetService('info').ShowInfo(typeID=invconst.typeAlliance, itemID=session.allianceid)

    def skins_hull_type_filter_setting(self, type_id):
        self.reconstruct_cards()

    def construct_filter_and_sorting(self):
        AllianceSectionFilterMenuButtonIcon(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT, left=48)
        ShipFilterMenuButton(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT, left=20, hull_type_setting=storeSettings.skins_hull_type_filter_setting)
        SortByMenuButtonIcon(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT, show_name_option=False)

    def construct_pagination_container(self):
        self.pagination_container = Container(name='pagination_container', parent=self, align=Align.TOTOP, height=32)
