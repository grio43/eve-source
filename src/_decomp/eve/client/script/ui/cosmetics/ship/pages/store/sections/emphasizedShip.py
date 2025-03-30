#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\sections\emphasizedShip.py
import evetypes
from carbonui import Align
from carbonui.primitives.container import Container
from cosmetics.client.ships.skins.live_data import current_skin_design
from cosmetics.client.ships.skins.static_data.store_section import StoreSection
from eve.client.script.ui.cosmetics.ship.const import SkinrPage
from eve.client.script.ui.cosmetics.ship.pages.store import storeSettings
from eve.client.script.ui.cosmetics.ship.pages.store.sections.baseSkinsSection import BaseSkinsSection
from eve.client.script.ui.cosmetics.ship.pages.store.sections.baseSkinsSectionContainer import BaseSkinsSectionContainer, SortByMenuButtonIcon, MAX_NUM_PER_PAGE
from localization import GetByLabel

class EmphasizedShipSkinsSection(BaseSkinsSection):
    page_id = SkinrPage.STORE_SKINS
    category = StoreSection.SKINS_EMPHASIZED_SHIP
    name = 'UI/Personalization/ShipSkins/SKINR/Studio/ActiveShipSKINs'

    def get_type_filter(self):
        if self.apply_filtering:
            return [storeSettings.emphasized_ship_type_id.get()]
        else:
            return []

    def get_name(self):
        return GetByLabel(self.name, shipName=evetypes.GetName(storeSettings.emphasized_ship_type_id.get()))


class EmphasizedShipSectionContainer(BaseSkinsSectionContainer):

    def _set_section_controller(self, section_controller = None):
        self.section_controller = EmphasizedShipSkinsSection(num_per_page=None)


class ViewAllSkinsEmphasizedShipSectionContainer(BaseSkinsSectionContainer):

    def _set_section_controller(self, section_controller = None):
        self.section_controller = EmphasizedShipSkinsSection(MAX_NUM_PER_PAGE)

    def construct_filter_and_sorting(self):
        SortByMenuButtonIcon(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT, show_name_option=False)

    def construct_pagination_container(self):
        self.pagination_container = Container(name='pagination_container', parent=self, align=Align.TOTOP, height=32)
