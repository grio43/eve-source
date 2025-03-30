#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\collection\skinLicenseBrowser.py
import eveicon
from carbonui import Align
from carbonui.button.menu import MenuButtonIcon
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.ships.skins.live_data.section_controller import CollectionAllActivatedSkinsSection, CollectionAllUnactivatedSkinsSection
from cosmetics.client.ships.skins.static_data.collection_section import CollectionSection
from cosmetics.common.ships.skins.util import SkinListingOrder
from eve.client.script.ui.cosmetics.ship.controls.baseCardSectionContainer import BaseCardSectionContainer
from eve.client.script.ui.cosmetics.ship.controls.shipFilterMenuButton import ShipFilterMenuButton
from eve.client.script.ui.cosmetics.ship.pages.cards.skinLicenseCard import ActivatedSkinLicenseCard, UnactivatedSkinLicenseCard
from eve.client.script.ui.cosmetics.ship.pages.collection import collectionSignals, collectionSettings
from localization import GetByLabel
MAX_NUM_PER_PAGE = 10

class SkinLicenseBrowser(ScrollContainer):

    def __init__(self, **kw):
        super(SkinLicenseBrowser, self).__init__(**kw)
        self.is_loaded = False

    def LoadPanel(self, section_id = None):
        self.reconstruct_layout()
        if section_id == CollectionSection.SKINS_3RD_PARTY_ACTIVATED:
            self.construct_view_all_activated_section()
        elif section_id == CollectionSection.SKINS_3RD_PARTY_UNACTIVATED:
            self.construct_view_all_unactivated_section()
        else:
            self.construct_landing_page()
        self.appear()

    def construct_view_all_unactivated_section(self):
        self.Flush()
        ViewAllUnactivatedSkinsSectionContainer(parent=self, align=Align.TOTOP, padTop=32, section_controller=CollectionAllUnactivatedSkinsSection(num_per_page=MAX_NUM_PER_PAGE))

    def construct_view_all_activated_section(self):
        self.Flush()
        ViewAllActivatedSkinsSectionContainer(parent=self, align=Align.TOTOP, padTop=32, section_controller=CollectionAllActivatedSkinsSection(num_per_page=MAX_NUM_PER_PAGE))

    def reconstruct_layout(self):
        self.Flush()

    def construct_landing_page(self):
        self.Flush()
        ActivatedSkinsSectionContainer(parent=self, align=Align.TOTOP, section_controller=CollectionAllActivatedSkinsSection(num_per_page=None, apply_filtering=False), single_row=True, padTop=32)
        UnactivatedSkinsSectionContainer(parent=self, align=Align.TOTOP, section_controller=CollectionAllUnactivatedSkinsSection(num_per_page=None, apply_filtering=False), single_row=True, padTop=32)

    def appear(self):
        animations.FadeTo(self, 0.0, 1.0, duration=0.3)


class BaseSkinsSectionContainer(BaseCardSectionContainer):

    def on_sort_by_setting(self, *args):
        self.update()

    def connect_signals(self):
        super(BaseSkinsSectionContainer, self).connect_signals()
        collectionSettings.skins_sort_by_setting.on_change.connect(self.on_sort_by_setting)
        collectionSignals.on_activated_skin_license_selected.connect(self.on_activated_skin_license_selected)
        collectionSignals.on_unactivated_skin_license_selected.connect(self.on_unactivated_skin_license_selected)
        ship_skin_signals.on_skin_license_added.connect(self.on_skin_license_added)
        ship_skin_signals.on_skin_license_deleted.connect(self.on_skin_license_deleted)
        ship_skin_signals.on_skin_license_updated.connect(self.on_skin_license_updated)

    def disconnect_signals(self):
        super(BaseSkinsSectionContainer, self).disconnect_signals()
        collectionSettings.skins_sort_by_setting.on_change.disconnect(self.on_sort_by_setting)
        collectionSignals.on_activated_skin_license_selected.connect(self.on_activated_skin_license_selected)
        collectionSignals.on_unactivated_skin_license_selected.connect(self.on_unactivated_skin_license_selected)
        ship_skin_signals.on_skin_license_added.disconnect(self.on_skin_license_added)
        ship_skin_signals.on_skin_license_deleted.disconnect(self.on_skin_license_deleted)
        ship_skin_signals.on_skin_license_updated.disconnect(self.on_skin_license_updated)

    def on_skin_license_added(self, *args):
        self.update()

    def on_skin_license_deleted(self, *args):
        self.update()

    def on_skin_license_updated(self, *args):
        self.update()

    def on_unactivated_skin_license_selected(self, skin_license):
        pass

    def on_activated_skin_license_selected(self, skin_license):
        pass

    def set_selected_license(self, skin_license):
        for card in self.cards:
            if card.skin_license != skin_license:
                card.is_selected = False


class ActivatedSkinsSectionContainer(BaseSkinsSectionContainer):

    def construct_card(self, skin_license):
        return ActivatedSkinLicenseCard(name='card_{name}'.format(name=skin_license.skin_hex), parent=self.content, skin_license=skin_license)

    def on_unactivated_skin_license_selected(self, skin_license):
        self.set_selected_license(None)

    def on_activated_skin_license_selected(self, skin_license):
        self.set_selected_license(skin_license)


class UnactivatedSkinsSectionContainer(BaseSkinsSectionContainer):

    def construct_card(self, skin_license):
        return UnactivatedSkinLicenseCard(name='card_{name}'.format(name=skin_license.skin_hex), parent=self.content, skin_license=skin_license)

    def on_unactivated_skin_license_selected(self, skin_license):
        self.set_selected_license(skin_license)

    def on_activated_skin_license_selected(self, skin_license):
        self.set_selected_license(None)


class SortByMenuButtonIcon(MenuButtonIcon):
    hint = GetByLabel('UI/Common/SortBy')
    default_texturePath = eveicon.bars_sort_ascending

    def GetMenu(self):
        m = MenuData()
        m.AddCaption(self.hint)
        m.AddRadioButton(GetByLabel('UI/Common/Name'), (SkinListingOrder.NAME, False), collectionSettings.skins_sort_by_setting)
        m.AddRadioButton(GetByLabel('UI/Inventory/NameReversed'), (SkinListingOrder.NAME, True), collectionSettings.skins_sort_by_setting)
        return m


class BaseViewAllSkinsSectionContainer(BaseSkinsSectionContainer):

    def __init__(self, section_controller, max_entries = None, **kw):
        super(BaseViewAllSkinsSectionContainer, self).__init__(section_controller, max_entries, **kw)
        collectionSettings.skins_hull_type_filter_setting.set(None)

    def connect_signals(self):
        super(BaseViewAllSkinsSectionContainer, self).connect_signals()
        collectionSettings.skins_hull_type_filter_setting.on_change.connect(self.skins_hull_type_filter_setting)

    def disconnect_signals(self):
        super(BaseViewAllSkinsSectionContainer, self).disconnect_signals()
        collectionSettings.skins_hull_type_filter_setting.on_change.disconnect(self.skins_hull_type_filter_setting)

    def skins_hull_type_filter_setting(self, type_id):
        self.update()

    def construct_filter_and_sorting(self):
        ShipFilterMenuButton(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT, left=20, hull_type_setting=collectionSettings.skins_hull_type_filter_setting)
        SortByMenuButtonIcon(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT)

    def construct_pagination_container(self):
        self.pagination_container = Container(name='pagination_container', parent=self, align=Align.TOTOP, height=32)


class ViewAllActivatedSkinsSectionContainer(BaseViewAllSkinsSectionContainer):

    def construct_card(self, skin_license):
        return ActivatedSkinLicenseCard(name='card_{name}'.format(name=skin_license.skin_hex), parent=self.content, skin_license=skin_license)

    def on_unactivated_skin_license_selected(self, skin_license):
        self.set_selected_license(None)

    def on_activated_skin_license_selected(self, skin_license):
        self.set_selected_license(skin_license)


class ViewAllUnactivatedSkinsSectionContainer(BaseViewAllSkinsSectionContainer):

    def construct_card(self, skin_license):
        return UnactivatedSkinLicenseCard(name='card_{name}'.format(name=skin_license.skin_hex), parent=self.content, skin_license=skin_license)

    def on_unactivated_skin_license_selected(self, skin_license):
        self.set_selected_license(skin_license)

    def on_activated_skin_license_selected(self, skin_license):
        self.set_selected_license(None)
