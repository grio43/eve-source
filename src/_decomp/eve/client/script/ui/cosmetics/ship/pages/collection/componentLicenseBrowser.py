#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\collection\componentLicenseBrowser.py
import eveicon
from carbonui import Align
from carbonui.button.menu import MenuButtonIcon
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.ships.skins.live_data.section_controller import CollectionNanocoatingComponentsSection, CollectionMetallicComponentsSection, CollectionPatternComponentsSection
from cosmetics.common.ships.skins.static_data.component_category import ComponentCategory
from cosmetics.common.ships.skins.util import SkinListingOrder, ComponentListingOrder
from eve.client.script.ui.cosmetics.ship.controls.baseCardSectionContainer import BaseCardSectionContainer
from eve.client.script.ui.cosmetics.ship.pages.cards.componentLicenseCard import ComponentLicenceCard
from eve.client.script.ui.cosmetics.ship.pages.collection import collectionSignals, collectionSettings
from localization import GetByLabel
MAX_NUM_PER_PAGE = 20

class ComponentLicenseBrowser(ScrollContainer):

    def __init__(self, **kw):
        super(ComponentLicenseBrowser, self).__init__(**kw)
        self.is_loaded = False

    def LoadPanel(self, category = None):
        self.reconstruct_layout()
        if category == ComponentCategory.PATTERN:
            self.construct_view_all_section(CollectionPatternComponentsSection(MAX_NUM_PER_PAGE))
        elif category == ComponentCategory.MATERIAL:
            self.construct_view_all_section(CollectionNanocoatingComponentsSection(MAX_NUM_PER_PAGE))
        elif category == ComponentCategory.METALLIC:
            self.construct_view_all_section(CollectionMetallicComponentsSection(MAX_NUM_PER_PAGE))
        else:
            self.construct_landing_page()
        self.appear()

    def reconstruct_layout(self):
        self.Flush()

    def construct_landing_page(self):
        self.Flush()
        ComponentCollectionSectionContainer(name='materials_section', parent=self, align=Align.TOTOP, section_controller=CollectionNanocoatingComponentsSection(num_per_page=None), single_row=True, padTop=32)
        ComponentCollectionSectionContainer(name='metallics_section', parent=self, align=Align.TOTOP, section_controller=CollectionMetallicComponentsSection(num_per_page=None), single_row=True, padTop=48)
        ComponentCollectionSectionContainer(name='pattern_section', parent=self, align=Align.TOTOP, section_controller=CollectionPatternComponentsSection(num_per_page=None), single_row=True, padTop=48)

    def construct_view_all_section(self, section_controller):
        self.Flush()
        ComponentCollectionViewAllSectionContainer(name='materials_section', parent=self, align=Align.TOTOP, padTop=32, section_controller=section_controller)

    def appear(self):
        animations.FadeTo(self, 0.0, 1.0, duration=0.3)


class ComponentCollectionSectionContainer(BaseCardSectionContainer):

    def __init__(self, section_controller, **kw):
        super(ComponentCollectionSectionContainer, self).__init__(section_controller, **kw)
        collectionSettings.components_sort_by_setting.on_change.connect(self.on_sort_by_setting)

    def on_sort_by_setting(self, *args):
        self.reconstruct_cards()

    def connect_signals(self):
        collectionSignals.on_component_license_selected.connect(self.on_component_license_selected)
        ship_skin_signals.on_component_license_cache_invalidated.connect(self.on_component_license_cache_invalidated)
        ship_skin_signals.on_component_license_granted.connect(self.on_component_license_granted)
        ship_skin_signals.on_skin_sequencing_job_updated.connect(self.on_skin_sequencing_job_updated)
        self.on_size_changed.connect(self._on_size_changed)

    def disconnect_signals(self):
        collectionSignals.on_component_license_selected.disconnect(self.on_component_license_selected)
        ship_skin_signals.on_component_license_cache_invalidated.disconnect(self.on_component_license_cache_invalidated)
        ship_skin_signals.on_component_license_granted.disconnect(self.on_component_license_granted)
        ship_skin_signals.on_skin_sequencing_job_updated.disconnect(self.on_skin_sequencing_job_updated)

    def on_component_license_selected(self, component_license):
        for card in self.cards:
            if card.component_license != component_license:
                card.is_selected = False

    def on_component_license_cache_invalidated(self, *args):
        self.update()

    def on_component_license_granted(self, *args):
        self.update()

    def on_skin_sequencing_job_updated(self, *args):
        self.update()

    def construct_card(self, component_license):
        return ComponentLicenceCard(name='card_{name}'.format(name=component_license.name.encode('utf-8')), parent=self.content, component_license=component_license)


class SortByMenuButtonIcon(MenuButtonIcon):
    hint = GetByLabel('UI/Common/SortBy')
    default_texturePath = eveicon.bars_sort_ascending

    def GetMenu(self):
        m = MenuData()
        m.AddCaption(self.hint)
        m.AddRadioButton(GetByLabel('UI/Common/Name'), (SkinListingOrder.NAME, False), collectionSettings.components_sort_by_setting)
        m.AddRadioButton(GetByLabel('UI/Inventory/NameReversed'), (SkinListingOrder.NAME, True), collectionSettings.components_sort_by_setting)
        m.AddSeparator()
        m.AddRadioButton(GetByLabel('UI/Common/ColorShade'), (ComponentListingOrder.COLOR_SHADE, False), collectionSettings.components_sort_by_setting)
        m.AddRadioButton(GetByLabel('UI/Common/ColorShadeReversed'), (ComponentListingOrder.COLOR_SHADE, True), collectionSettings.components_sort_by_setting)
        return m


class ComponentCollectionViewAllSectionContainer(ComponentCollectionSectionContainer):

    def construct_filter_and_sorting(self):
        SortByMenuButtonIcon(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT)

    def construct_pagination_container(self):
        self.pagination_container = Container(name='pagination_container', parent=self, align=Align.TOTOP, height=32)
