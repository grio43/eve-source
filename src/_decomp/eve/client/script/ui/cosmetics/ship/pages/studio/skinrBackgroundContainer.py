#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\skinrBackgroundContainer.py
from logging import getLogger
import trinity
import uthread2
from carbonui import const as uiconst
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.primitives.container import Container
from carbonui.ui3d import InSceneContainer
from cosmetics.client.ships.skins.live_data import current_skin_design_signals, current_skin_design
from cosmetics.client.ships.skins.live_data.skin_design import SkinDesign
from cosmetics.common.ships.skins.errors import SlotDisallowedForComponent
from cosmetics.common.ships.skins.static_data.component_category import ComponentCategory
from cosmetics.common.ships.skins.static_data.slot_name import SlotID
from eve.client.script.ui.control.scenecontainer import SceneContainerBaseNavigation
from eve.client.script.ui.cosmetics.ship.const import SkinrPage, CHILD_PAGES_BY_PARENT_PAGE
from eve.client.script.ui.cosmetics.ship.pages import current_page
from eve.client.script.ui.cosmetics.ship.pages.collection import collectionSignals
from eve.client.script.ui.cosmetics.ship.pages.store import storeSignals, storeSettings
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSignals
from eve.client.script.ui.cosmetics.ship.pages.studio.shipSKINRSceneContainer import ShipSKINRSceneContainer
from eve.client.script.ui.cosmetics.ship.pages.studio.skinrInSceneContainer import SkinrInSceneContainer
from eve.client.script.ui.cosmetics.ship.pages.studio.studioUtil import is_green_screen_enabled
from localization import GetByLabel
from signals import Signal
log = getLogger(__name__)
MINIMUM_ZOOM_DISTANCE_DEFAULT = 5000
MAXIMUM_PROJECTION_ANGLE_ADJUSTMENT = 0.3
DEFAULT_PATTERN_SHOWCASE_MATERIAL_ID = 220

class SKINRBackgroundContainer(Container):

    def __init__(self, **kw):
        log.info('SKIN PREVIEW - PreviewPanel: Start constructing')
        super(SKINRBackgroundContainer, self).__init__(**kw)
        self.on_drop_data = Signal('on_drop_data')
        self.sceneNavigation = None
        self.in_scene_bg_container = None
        self._construct_layout()
        self.connect_signals()
        self.preview_type(current_skin_design.get().ship_type_id)
        log.info('SKIN PREVIEW - PreviewPanel: Finish constructing')

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(SKINRBackgroundContainer, self).Close()

    def connect_signals(self):
        studioSignals.on_page_opened.connect(self.on_page_opened)
        studioSignals.on_sequencing_job_selected.connect(self.on_sequencing_job_selected)
        collectionSignals.on_component_license_selected.connect(self.on_component_license_selected)
        collectionSignals.on_first_party_skin_applied.connect(self.on_first_party_skin_applied)
        collectionSignals.on_first_party_skin_selected.connect(self.on_first_party_skin_selected)
        collectionSignals.on_activated_skin_license_selected.connect(self.on_collection_skin_license_selected)
        collectionSignals.on_unactivated_skin_license_selected.connect(self.on_collection_skin_license_selected)
        collectionSignals.on_skin_license_details_clear.connect(self.on_collection_skin_license_details_clear)
        current_skin_design_signals.on_ship_type_id_changed.connect(self.on_ship_type_id_changed)
        current_skin_design_signals.on_design_reset.connect(self.on_new_design_initialized)
        current_skin_design_signals.on_existing_design_loaded.connect(self.on_existing_design_loaded)
        storeSignals.on_component_listing_selected.connect(self.on_store_component_listing_selected)
        storeSignals.on_skin_listing_selected.connect(self.on_store_skin_listing_selected)
        if self.sceneNavigation:
            self.sceneNavigation.on_drop_data.connect(self.on_drop_data)

    def disconnect_signals(self):
        studioSignals.on_page_opened.disconnect(self.on_page_opened)
        studioSignals.on_sequencing_job_selected.disconnect(self.on_sequencing_job_selected)
        collectionSignals.on_component_license_selected.disconnect(self.on_component_license_selected)
        collectionSignals.on_first_party_skin_applied.disconnect(self.on_first_party_skin_applied)
        collectionSignals.on_first_party_skin_selected.disconnect(self.on_first_party_skin_selected)
        collectionSignals.on_activated_skin_license_selected.disconnect(self.on_collection_skin_license_selected)
        collectionSignals.on_unactivated_skin_license_selected.disconnect(self.on_collection_skin_license_selected)
        collectionSignals.on_skin_license_details_clear.disconnect(self.on_collection_skin_license_details_clear)
        current_skin_design_signals.on_ship_type_id_changed.disconnect(self.on_ship_type_id_changed)
        current_skin_design_signals.on_design_reset.disconnect(self.on_new_design_initialized)
        current_skin_design_signals.on_existing_design_loaded.disconnect(self.on_existing_design_loaded)
        storeSignals.on_component_listing_selected.disconnect(self.on_store_component_listing_selected)
        storeSignals.on_skin_listing_selected.disconnect(self.on_store_skin_listing_selected)
        if self.sceneNavigation:
            self.sceneNavigation.on_drop_data.disconnect(self.on_drop_data)

    def on_collection_skin_license_selected(self, skin_license):
        current_skin_design.open_existing_design(skin_license.skin_hex)

    def on_collection_skin_license_details_clear(self):
        current_skin_design.reset_design()

    def on_component_license_selected(self, component_licence):
        category = component_licence.get_component_data().category
        self.apply_component(category, component_licence.component_id)

    def on_sequencing_job_selected(self, sequencing_job):
        if not sequencing_job:
            return
        current_skin_design.open_existing_design(sequencing_job.skin_hex)

    def on_store_skin_listing_selected(self, skin_listing, *args):
        if skin_listing:
            if current_skin_design.get() != skin_listing.skin_design:
                current_skin_design.update_from_other(skin_listing.skin_design)

    def on_store_component_listing_selected(self, component_listing):
        if component_listing:
            category = component_listing.get_component_data().category
            component_id = component_listing.component_id
            self.apply_component(category, component_id)

    def apply_component(self, category, component_id):
        skin_design = SkinDesign()
        skin_design.ship_type_id = current_skin_design.get_default_ship_type_id()
        if category == ComponentCategory.MATERIAL:
            for slot_id in (SlotID.PRIMARY_NANOCOATING,
             SlotID.SECONDARY_NANOCOATING,
             SlotID.TERTIARY_NANOCOATING,
             SlotID.TECH_AREA):
                skin_design.fit_slot(slot_id, component_id)

        if category == ComponentCategory.METALLIC:
            for slot_id in (SlotID.PRIMARY_NANOCOATING,
             SlotID.SECONDARY_NANOCOATING,
             SlotID.TERTIARY_NANOCOATING,
             SlotID.TECH_AREA):
                try:
                    skin_design.fit_slot(slot_id, component_id)
                except SlotDisallowedForComponent:
                    continue

        elif category == ComponentCategory.PATTERN:
            skin_design.fit_slot(SlotID.PATTERN, component_id)
            skin_design.fit_slot(SlotID.PATTERN_MATERIAL, DEFAULT_PATTERN_SHOWCASE_MATERIAL_ID)
        current_skin_design.update_from_other(skin_design)

    def on_page_opened(self, page_id, page_args, last_page_id, animate = True):
        if page_id == SkinrPage.STUDIO_DESIGNER and last_page_id == SkinrPage.STUDIO:
            if page_args and page_args == current_skin_design.get().saved_skin_design_id:
                pass
            else:
                log.info('SKIN PREVIEW - PreviewPanel: Reset when creating a new design')
                current_skin_design.reset_design()
        elif page_id == SkinrPage.STUDIO and last_page_id == SkinrPage.STUDIO_DESIGNER:
            log.info('SKIN PREVIEW - PreviewPanel: Reset when going from studio design to studio homepage')
            current_skin_design.reset_design()
        elif page_id == SkinrPage.STUDIO or page_id in CHILD_PAGES_BY_PARENT_PAGE[SkinrPage.STUDIO]:
            if last_page_id not in CHILD_PAGES_BY_PARENT_PAGE[SkinrPage.STUDIO]:
                log.info('SKIN PREVIEW - PreviewPanel: Reset when going to studio homepage or subpage except from studio subpages')
                current_skin_design.reset_design()
        elif page_id == SkinrPage.STORE or page_id in CHILD_PAGES_BY_PARENT_PAGE[SkinrPage.STORE]:
            log.info('SKIN PREVIEW - PreviewPanel: Reset when going to store or subpage')
            current_skin_design.reset_design(ship_type_id=storeSettings.emphasized_ship_type_id.get())
        elif page_id == SkinrPage.COLLECTION or page_id in CHILD_PAGES_BY_PARENT_PAGE[SkinrPage.COLLECTION]:
            log.info('SKIN PREVIEW - PreviewPanel: Reset when going to collection or subpage')
            current_skin_design.reset_design()
        if page_id != SkinrPage.STUDIO_DESIGNER:
            current_skin_design.set_selected_slot_id(None)

    def on_new_design_initialized(self, current_design, saved_skin_design_id):
        self.apply_new_design(current_design)

    def on_existing_design_loaded(self, skin_design, animate):
        self.apply_new_design(skin_design, animate)

    def on_first_party_skin_applied(self, item_id, first_party_skin):
        self.preview_type(first_party_skin.types[0])

    def apply_new_design(self, skin_design, animate = True):
        self.preview_type(skin_design.ship_type_id, skinDesign=skin_design, animate=animate)

    def on_first_party_skin_selected(self, skin_id, first_party_skin):
        self.preview_type(first_party_skin.types[0])

    def _construct_layout(self):
        log.info('SKIN PREVIEW - PreviewPanel Layout: Start constructing')
        self.preview_container = Container(name='preview_container', parent=self, align=uiconst.TOALL)
        self.scene_container = ShipSKINRSceneContainer(parent=self.preview_container, align=uiconst.TOALL)
        log.info('SKIN PREVIEW - PreviewPanel Layout: PaintPreviewSceneContainer constructed')
        self.sceneNavigation = SceneContainerBaseNavigation(name='preview_navigation', parent=self.preview_container, align=uiconst.TOALL, pos=(0, 0, 0, 0), idx=0, state=uiconst.UI_NORMAL, pickRadius=0)
        log.info('SKIN PREVIEW - PreviewPanel Layout: SceneContainerBaseNavigation constructed')
        self.sceneNavigation.Startup(self.scene_container)
        self.sceneNavigation.GetMenu = self.GetMenu
        log.info('SKIN PREVIEW - PreviewPanel Layout: SceneContainerBaseNavigation started up')
        if not is_green_screen_enabled():
            uthread2.start_tasklet(self.create_in_scene_cont)
        log.info('SKIN PREVIEW - PreviewPanel Layout: Finish constructing')

    def GetMenu(self):
        m = MenuData()
        if current_page.get_page_id() == SkinrPage.STUDIO_DESIGNER:
            m.AddEntry(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ResetAllSlots'), self.reset_all)
        return m

    def reset_all(self):
        current_skin_design.get().unfit_all()
        current_skin_design.add_to_undo_history()

    def create_in_scene_cont(self):
        trinity.WaitForResourceLoads()
        if self.scene_container.scene and self.scene_container.camera:
            log.info('SKIN PREVIEW - PreviewPanel Layout: SkinrInSceneContainer started constructing')
            self.in_scene_bg_container = SkinrInSceneContainer(parent=self, scene=self.scene_container.scene, camera=self.scene_container.camera, name='ScneeCont', clearBackground=True, backgroundColor=(0, 0, 0, 0), trackType=InSceneContainer.TRACKTYPE_TRANSFORM)
            self.sceneNavigation.on_mouse_up.connect(self.in_scene_bg_container.on_mouse_up)
            log.info('SKIN PREVIEW - PreviewPanel Layout: SkinrInSceneContainer finished constructing')

    def on_ship_type_id_changed(self, type_id):
        self.preview_type(type_id, current_skin_design.get())

    def _on_slot_mouse_enter(self, slot_id):
        pass

    def _on_slot_mouse_exit(self):
        pass

    def preview_type(self, type_id, skinDesign = None, animate = True):
        self.scene_container.preview_type(type_id, skinDesign=skinDesign, animate=animate)
        if self.in_scene_bg_container:
            self.in_scene_bg_container.update()

    @property
    def camera_offset(self):
        if not self.scene_container.camera:
            return None
        return self.scene_container.camera.centerOffset

    @camera_offset.setter
    def camera_offset(self, value):
        if self.scene_container.camera:
            self.scene_container.camera.centerOffset = value

    def turn_camera(self, yaw, pitch, duration):
        if self.scene_container.camera:
            self.scene_container.turn_camera(yaw, pitch, duration)
