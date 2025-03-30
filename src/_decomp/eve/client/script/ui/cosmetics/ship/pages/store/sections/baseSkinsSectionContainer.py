#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\sections\baseSkinsSectionContainer.py
import eveicon
from carbonui.button.menu import MenuButtonIcon
from carbonui.control.contextMenu.menuData import MenuData
from cosmetics.client.ships import ship_skin_signals
from cosmetics.common.ships.skins.util import SkinListingOrder
from eve.client.script.ui.cosmetics.ship.controls.baseCardSectionContainer import BaseCardSectionContainer
from eve.client.script.ui.cosmetics.ship.pages.cards.skinListingCard import SkinListingCard
from eve.client.script.ui.cosmetics.ship.pages.store import storeSignals
from eve.client.script.ui.cosmetics.ship.pages.store.storeSettings import skins_sort_by_setting
from localization import GetByLabel
MAX_NUM_PER_PAGE = 12

class BaseSkinsSectionContainer(BaseCardSectionContainer):
    default_height = 306
    default_minHeight = 306

    def connect_signals(self):
        super(BaseSkinsSectionContainer, self).connect_signals()
        storeSignals.on_skin_listing_selected.connect(self.on_skin_listing_selected)
        ship_skin_signals.on_skin_license_added.connect(self.on_skin_license_added)
        ship_skin_signals.on_skin_license_deleted.connect(self.on_skin_license_deleted)
        ship_skin_signals.on_skin_license_updated.connect(self.on_skin_license_updated)
        ship_skin_signals.on_skin_listing_cache_invalidated.connect(self._on_skin_listing_cache_invalidated)
        skins_sort_by_setting.on_change.connect(self.on_sort_by_setting)

    def disconnect_signals(self):
        super(BaseSkinsSectionContainer, self).disconnect_signals()
        storeSignals.on_skin_listing_selected.disconnect(self.on_skin_listing_selected)
        ship_skin_signals.on_skin_license_added.disconnect(self.on_skin_license_added)
        ship_skin_signals.on_skin_license_deleted.disconnect(self.on_skin_license_deleted)
        ship_skin_signals.on_skin_license_updated.disconnect(self.on_skin_license_updated)
        ship_skin_signals.on_skin_listing_cache_invalidated.disconnect(self._on_skin_listing_cache_invalidated)
        skins_sort_by_setting.on_change.disconnect(self.on_sort_by_setting)

    def on_skin_license_added(self, *args):
        self.update()

    def on_skin_license_deleted(self, *args):
        self.update()

    def on_skin_license_updated(self, *args):
        self.update()

    def on_skin_listing_selected(self, listing, selected_card):
        for card in self.cards:
            if card.listing != listing:
                card.is_selected = False
            else:
                card.is_selected = card == selected_card

    def _on_skin_listing_cache_invalidated(self, *args):
        self.update()

    def on_sort_by_setting(self, *args):
        self.update()

    def construct_card(self, listing):
        return SkinListingCard(parent=self.content, listing=listing)


class SortByMenuButtonIcon(MenuButtonIcon):
    hint = GetByLabel('UI/Common/SortBy')
    default_texturePath = eveicon.bars_sort_ascending

    def __init__(self, show_name_option = True, **kw):
        super(SortByMenuButtonIcon, self).__init__(**kw)
        self.show_name_option = show_name_option

    def GetMenu(self):
        m = MenuData()
        m.AddCaption(self.hint)
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/TimeLeft'), (SkinListingOrder.EXPIRES_AT, True), skins_sort_by_setting)
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/TimeLeftReversed'), (SkinListingOrder.EXPIRES_AT, False), skins_sort_by_setting)
        if self.show_name_option:
            m.AddSeparator()
            m.AddRadioButton(GetByLabel('UI/Common/Name'), (SkinListingOrder.NAME, True), skins_sort_by_setting)
            m.AddRadioButton(GetByLabel('UI/Inventory/NameReversed'), (SkinListingOrder.NAME, False), skins_sort_by_setting)
        return m
