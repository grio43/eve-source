#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\sections\myListings.py
import carbonui
import eveformat
import eveicon
from carbonui import Align, uiconst, TextColor
from carbonui.button.menu import MenuButtonIcon
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.primitives.container import Container
from cosmetics.client.shipSkinTradingSvc import get_ship_skin_trading_svc
from cosmetics.client.ships.ship_skin_signals import on_skin_listing_cache_invalidated
from cosmetics.client.ships.skins.live_data.section_controller import BaseSection
from cosmetics.client.ships.skins.live_data.skin_listing_target import SellerMembershipType, ListingTargetType, ListedTo
from cosmetics.client.ships.skins.static_data.store_section import StoreSection
from cosmetics.common.ships.skins.static_data import trading_const
from cosmetics.common.ships.skins.trading_util import get_maximum_concurrent_skin_listings
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.cosmetics.ship.const import SkinrPage
from eve.client.script.ui.cosmetics.ship.controls.shipFilterMenuButton import ShipFilterMenuButton
from eve.client.script.ui.cosmetics.ship.pages.cards.baseSkinCard import BlankSkinCard
from eve.client.script.ui.cosmetics.ship.pages.store import storeSettings
from eve.client.script.ui.cosmetics.ship.pages.store.sections.baseSkinsSection import _get_skin_listing_sort_key
from eve.client.script.ui.cosmetics.ship.pages.store.sections.baseSkinsSectionContainer import BaseSkinsSectionContainer, SortByMenuButtonIcon, MAX_NUM_PER_PAGE
from eve.client.script.ui.cosmetics.ship.pages.store.storeSettings import skins_sort_by_setting, listed_to_setting
from eve.client.script.ui.shared.shipTree.infoBubble import SkillEntry
from localization import GetByLabel
from skills.client.util import get_skill_service

class StoreSkinsListedByMeSection(BaseSection):
    page_id = SkinrPage.STORE_SKINS
    category = StoreSection.SKINS_MY_LISTINGS
    name = 'UI/Personalization/ShipSkins/SKINR/Store/MyListings'

    def _get_all_card_controllers(self):
        return get_ship_skin_trading_svc().get_owned_listings()

    def _sort_controllers(self, controllers):
        sort_by, ascending = skins_sort_by_setting.get()
        return sorted(controllers, key=lambda l: _get_skin_listing_sort_key(l, sort_by), reverse=not ascending)

    def _on_skin_listing_cache_invalidated(self, *args):
        self.pagination_controller.clear(self._get_card_controllers_filtered_and_sorted(), self.num_per_page)

    @property
    def blank_card_class(self):
        return BlankSkinCard


class ListedByMeSectionContainer(BaseSkinsSectionContainer):
    __notifyevents__ = ['OnSkillsChanged']

    def __init__(self, **kw):
        super(ListedByMeSectionContainer, self).__init__(**kw)
        sm.RegisterNotify(self)

    def _set_section_controller(self, section_controller = None):
        self.section_controller = StoreSkinsListedByMeSection(num_per_page=None, apply_filtering=False)

    def OnSkillsChanged(self, _skills):
        self.update_num_items_label()

    def update_num_items_label(self):
        if not self.is_loaded:
            return
        num_listings = self.section_controller.get_num_entries()
        max_listings = get_maximum_concurrent_skin_listings(get_skill_service().GetMyLevel)
        self.num_items_label.text = u'{}/{}'.format(eveformat.number(num_listings), max_listings)

    def construct_header(self):
        super(ListedByMeSectionContainer, self).construct_header()
        self.header_layout_grid.columns = 3
        MaxListingsSkillsInfoIcon(parent=self.header_layout_grid, align=Align.CENTER)

    def on_skin_license_updated(self, *args):
        super(ListedByMeSectionContainer, self).on_skin_license_updated(*args)
        self.update_num_items_label()

    def _on_skin_listing_cache_invalidated(self, *args):
        super(ListedByMeSectionContainer, self)._on_skin_listing_cache_invalidated(*args)
        self.update_num_items_label()


class ViewAllSkinsListedByMeSection(StoreSkinsListedByMeSection):

    def _get_all_card_controllers(self):
        return get_ship_skin_trading_svc().get_owned_listings(listed_to_setting.get())

    def _filter_controllers(self, controllers):
        ship_type = storeSettings.skins_hull_type_filter_setting.get()
        if ship_type:
            controllers = [ c for c in controllers if c.skin_design.ship_type_id == ship_type ]
        return controllers


class MyListingsSectionFilterMenuButtonIcon(MenuButtonIcon):
    hint = GetByLabel('UI/Common/Filter')
    default_texturePath = eveicon.filter

    def GetMenu(self):
        m = MenuData()
        m.AddCaption(GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ListedTo'))
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ListedToSpecific'), ListedTo.SPECIFIC, listed_to_setting)
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/SellAvailability/MyCorporation'), ListedTo.MY_CORP, listed_to_setting)
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/SellAvailability/MyAlliance'), ListedTo.MY_ALLIANCE, listed_to_setting)
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ListedByAnyone'), ListedTo.PUBLIC, listed_to_setting)
        return m


class ViewAllSkinsListedByMeSectionContainer(ListedByMeSectionContainer):

    def __init__(self, **kw):
        super(ViewAllSkinsListedByMeSectionContainer, self).__init__(**kw)
        storeSettings.skins_hull_type_filter_setting.set(None)
        storeSettings.listed_to_setting.set(ListedTo.PUBLIC)

    def connect_signals(self):
        super(ViewAllSkinsListedByMeSectionContainer, self).connect_signals()
        storeSettings.skins_hull_type_filter_setting.on_change.connect(self.on_skins_hull_type_filter_setting)
        storeSettings.listed_to_setting.on_change.connect(self.on_listed_to_setting)

    def disconnect_signals(self):
        super(ViewAllSkinsListedByMeSectionContainer, self).disconnect_signals()
        storeSettings.skins_hull_type_filter_setting.on_change.disconnect(self.on_skins_hull_type_filter_setting)
        storeSettings.listed_to_setting.on_change.disconnect(self.on_listed_to_setting)

    def on_listed_to_setting(self, *args):
        self.update()

    def on_skins_hull_type_filter_setting(self, *args):
        self.update()

    def _set_section_controller(self, section_controller = None):
        self.section_controller = ViewAllSkinsListedByMeSection(MAX_NUM_PER_PAGE)

    def construct_filter_and_sorting(self):
        MyListingsSectionFilterMenuButtonIcon(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT, left=48)
        ShipFilterMenuButton(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT, left=20, hull_type_setting=storeSettings.skins_hull_type_filter_setting)
        SortByMenuButtonIcon(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT)

    def construct_pagination_container(self):
        self.pagination_container = Container(name='pagination_container', parent=self, align=Align.TOTOP, height=32)


class MaxListingsSkillsInfoIcon(InfoIcon):

    def ConstructTooltipPanel(self):
        return MaxListingsSkillsTooltipPanel()


class MaxListingsSkillsTooltipPanel(TooltipPanel):
    default_columns = 2
    default_state = uiconst.UI_NORMAL

    def __init__(self, **kw):
        super(MaxListingsSkillsTooltipPanel, self).__init__(**kw)
        self.LoadStandardSpacing()
        self.AddCell(carbonui.TextBody(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/MaxListingsTooltip'), width=300, color=TextColor.SECONDARY), colSpan=2)
        for type_id in trading_const.max_concurrent_listings_skills:
            level = get_skill_service().GetMyLevel(type_id)
            self.AddRow(rowClass=SkillEntry, typeID=type_id, level=level, showLevel=False)
