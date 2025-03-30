#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\shipSKINRWindow.py
import math
import eveicon
import evetypes
from carbonui import Align, Density, PickState, ButtonVariant
from carbonui.control.button import Button
from carbonui.control.dragdrop.dragdata import TypeDragData
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.ships.feature_flag import is_ship_skinr_feature_enabled
from cosmetics.client.ships.ship_skin_signals import on_skin_sequencing_job_failed
from cosmetics.client.ships.skins.errors import SEQUENCING_ERROR_TEXT_BY_CODE, SEQUENCE_FAILURE_REASON_TO_ERROR
from cosmetics.client.ships.skins.live_data import current_skin_design
from cosmetics.client.ships.qa.menus import is_qa, add_qa_context_menu
from cosmetics.common.ships.skins.static_data.slot_configuration import is_skinnable_ship
from eve.client.script.ui.control.floatingToggleButtonGroup import FloatingToggleButtonGroup
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship.const import SkinrPage, ANIM_DURATION_LONG, PARENT_PAGE_BY_CHILD_PAGE, CHILD_PAGES_BY_PARENT_PAGE
from eve.client.script.ui.cosmetics.ship.pages.store import storeSettings
from eve.client.script.ui.cosmetics.ship.pages.store.storePage import StorePage
from eve.client.script.ui.cosmetics.ship.pages.collection.collectionPage import CollectionPage
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSignals
from eve.client.script.ui.cosmetics.ship.pages import current_page
from eve.client.script.ui.cosmetics.ship.pages.studio.studioPageContainer import StudioPageContainer
from eve.client.script.ui.cosmetics.ship.pages.studio.skinrBackgroundContainer import SKINRBackgroundContainer
from eve.client.script.ui.shared.mapView.dockPanel import DockablePanel, BUTTON_FULLSCREEN, BUTTON_FLOAT
from eve.client.script.ui.view.viewStateConst import ViewState
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
from localization import GetByLabel
from logging import getLogger
CAMERA_PITCH = 4 * math.pi / 10
logger = getLogger(__name__)

class ShipSKINRWindow(DockablePanel):
    default_apply_content_padding = False
    default_captionLabelPath = 'UI/Personalization/ShipSkins/SKINR/Title'
    default_descriptionLabelPath = 'UI/Personalization/ShipSkins/SKINR/Description'
    default_iconNum = 'res:/UI/Texture/WindowIcons/paint_tool.png'
    default_minSize = (1024, 700)
    default_windowID = 'ShipSKINRWindow'
    default_analyticID = 'ship_skinr'
    dock_options = (BUTTON_FULLSCREEN, BUTTON_FLOAT)
    panelID = default_windowID
    viewState = ViewState.ShipSKINR
    __notifyevents__ = DockablePanel.__notifyevents__ + ['OnHideUI', 'OnShowUI']

    def __init__(self, page_id = SkinrPage.STUDIO, page_args = None, saved_skin_design_id = None, **kwargs):
        super(ShipSKINRWindow, self).__init__(**kwargs)
        self.is_closing = False
        self.scene_preview_panel = None
        self.initialize_skin_design(saved_skin_design_id)
        self.construct_layout()
        self.connect_signals()
        self.select_initial_tab(page_id)
        current_page.set_page_id(page_id, page_args=page_args, animate=False)

    @classmethod
    def open_external_design(cls, character_id, design_id):
        if design_id is not None:
            window = ShipSKINRWindow.Open()
            if window.IsMinimized():
                window.Maximize()
            window.select_initial_tab(SkinrPage.STUDIO)
            current_page_id = current_page.get_page_id()
            if current_page_id is not None and current_page_id == SkinrPage.STUDIO_DESIGNER and current_skin_design.get().saved_skin_design_id == design_id:
                return
            can_leave_current_page = current_page.set_page_id(SkinrPage.STUDIO)
            if can_leave_current_page:
                current_skin_design.open_existing_saved_design(design_id)
                current_page.set_page_id(SkinrPage.STUDIO_DESIGNER, page_args=design_id)

    @classmethod
    def open_external_skin_listing(cls, skin_listing = None):
        if skin_listing is None:
            ShowQuickMessage(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/ListingNotFound'))
            return
        window = ShipSKINRWindow.Open()
        if window.IsMinimized():
            window.Maximize()
        current = current_page.get_page_id()
        if current != SkinrPage.STORE_SKINS:
            if not current_page.set_page_id(SkinrPage.STORE_SKINS):
                return
        window.select_initial_tab(SkinrPage.STORE_SKINS)
        window.store_page.show_skin(skin_listing)

    @classmethod
    def open_on_paragon_hub(cls, ship_type_id = None):
        if ship_type_id:
            storeSettings.emphasized_ship_type_id.set(ship_type_id)
        wnd = cls.GetIfOpen()
        if wnd:
            current_page.set_page_id(page_id=SkinrPage.STORE_SKINS)
            wnd.Maximize()
        else:
            cls.Open(page_id=SkinrPage.STORE_SKINS)

    @classmethod
    def Open(cls, *args, **kwds):
        if not is_ship_skinr_feature_enabled():
            ShowQuickMessage(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ShipSKINRUnavailable'))
            return
        else:
            return super(ShipSKINRWindow, cls).Open(*args, **kwds)

    def initialize_skin_design(self, saved_skin_design_id):
        current_page.reset_history()
        if saved_skin_design_id:
            current_skin_design.open_existing_saved_design(saved_skin_design_id)
        else:
            current_skin_design.create_blank_design()
            active_ship_type_id = current_skin_design.get_active_ship_type_id()
            if not is_skinnable_ship(active_ship_type_id):
                ShowQuickMessage(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ActiveShipDoesNotSupportSKINs', shipName=evetypes.GetName(active_ship_type_id)))

    def connect_signals(self):
        if self.scene_preview_panel:
            self.scene_preview_panel.sceneNavigation.on_drop_data.connect(self.on_scene_preview_panel_drop_data)
        self.on_size_changed.connect(self._on_size_changed)
        studioSignals.on_page_opened.connect(self.on_page_opened)
        on_skin_sequencing_job_failed.connect(self._on_skin_sequencing_job_failed)
        ship_skin_signals.on_ship_skinr_feature_availability_changed.connect(self.on_ship_skinr_feature_availability_changed)

    def disconnect_signals(self):
        if self.scene_preview_panel:
            self.scene_preview_panel.sceneNavigation.on_drop_data.disconnect(self.on_scene_preview_panel_drop_data)
        self.on_size_changed.disconnect(self._on_size_changed)
        studioSignals.on_page_opened.disconnect(self.on_page_opened)
        on_skin_sequencing_job_failed.disconnect(self._on_skin_sequencing_job_failed)
        ship_skin_signals.on_ship_skinr_feature_availability_changed.disconnect(self.on_ship_skinr_feature_availability_changed)

    def on_ship_skinr_feature_availability_changed(self, *args):
        if not is_ship_skinr_feature_enabled():
            ShowQuickMessage(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ShipSKINRUnavailable'))
            self.Close()

    def on_page_opened(self, page_id, page_args, last_page_id, animate = True):
        self.load_page(page_id, page_args)
        self.update_camera_offset(animate)
        self.update_camera_yaw_and_pitch(page_id)
        self.back_btn.display = current_page.is_back_enabled()

    def update_camera_yaw_and_pitch(self, page_id):
        if self.scene_preview_panel:
            self.scene_preview_panel.turn_camera(yaw=current_page.get_camera_yaw(), pitch=CAMERA_PITCH, duration=ANIM_DURATION_LONG)

    def _on_size_changed(self, width, height):
        self.update_camera_offset(animate=False)

    def on_scene_preview_panel_drop_data(self, drag_source, drag_data):
        if isinstance(drag_data[0], TypeDragData):
            type_id = drag_data[0].typeID
            if is_skinnable_ship(type_id):
                current_skin_design.get().ship_type_id = type_id
                drag_source.data.GetRootNode().DeselectAll()
                drag_source.SetSelected()

    def update_camera_offset(self, animate = True):
        if not self.scene_preview_panel:
            return
        offset = current_page.get_camera_offset()
        if animate:
            if self.scene_preview_panel.camera_offset is not None:
                animations.MorphScalar(self.scene_preview_panel, 'camera_offset', self.scene_preview_panel.camera_offset, offset, duration=ANIM_DURATION_LONG)
        else:
            self.scene_preview_panel.camera_offset = offset

    def construct_layout(self):
        self.construct_logo()
        self.construct_tab_group()
        self.construct_back_btn()
        self.construct_pages()
        self.construct_scene()

    def construct_back_btn(self):
        self.back_btn = Button(name='back_btn', parent=self.content, align=Align.TOPLEFT, pos=(32, 128, 0, 0), texturePath=eveicon.caret_left, func=self.on_back_btn, label=GetByLabel('UI/Commands/Back'), density=Density.EXPANDED, display=False, pickState=PickState.ON, variant=ButtonVariant.GHOST)

    def on_back_btn(self, *args):
        current_page.go_back()

    def Close(self, setClosed = False, *args, **kwds):
        try:
            self.disconnect_signals()
            storeSettings.emphasized_ship_type_id.set(0)
        finally:
            return super(ShipSKINRWindow, self).Close(setClosed, *args, **kwds)

    def construct_logo(self):
        Sprite(name='paragon_logo', parent=self.content, align=Align.TOPRIGHT, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/paragon_logo.png', pos=(20,
         self.toolbarContainer.height + 20,
         90,
         71))

    def construct_tab_group(self):
        self.toggle_btn_group = FloatingToggleButtonGroup(name='toggle_btn_group', parent=self.content, padTop=self.toolbarContainer.height, padLeft=16, align=Align.TOPLEFT, padding=0, pos=(32, 64, 460, 32), callback=self.on_toggle_btn_group)

    def on_toggle_btn_group(self, page_id, old_panel_id):
        if not current_page.set_page_id(page_id):
            self.toggle_btn_group.SetSelected(old_panel_id, animate=False)

    def select_initial_tab(self, page_id):
        page_id = PARENT_PAGE_BY_CHILD_PAGE.get(page_id, page_id)
        self.toggle_btn_group.SetSelected(page_id, animate=False)

    def load_page(self, page_id, page_args = None, **kwargs):
        if page_id == SkinrPage.STUDIO or page_id in CHILD_PAGES_BY_PARENT_PAGE[SkinrPage.STUDIO]:
            self.load_studio_page(page_id, page_args, **kwargs)
        elif page_id == SkinrPage.COLLECTION or page_id in CHILD_PAGES_BY_PARENT_PAGE[SkinrPage.COLLECTION]:
            self.load_collection_page(page_id, page_args, **kwargs)
        elif page_id == SkinrPage.STORE or page_id in CHILD_PAGES_BY_PARENT_PAGE[SkinrPage.STORE]:
            self.load_store_page(page_id, page_args, **kwargs)

    def load_studio_page(self, page_id, page_args = None, **kwargs):
        self.store_page.display = self.collection_page.display = False
        self.studio_page.display = True
        self.studio_page.load_panel(page_id, page_args)
        self.toggle_btn_group.SetSelected(SkinrPage.STUDIO)

    def load_store_page(self, page_id, page_args = None, **kwargs):
        self.collection_page.display = self.studio_page.display = False
        self.store_page.display = True
        self.store_page.load_panel(page_id, page_args)
        self.toggle_btn_group.SetSelected(SkinrPage.STORE)

    def load_collection_page(self, page_id, page_args, **kwargs):
        self.store_page.display = self.studio_page.display = False
        self.collection_page.display = True
        self.collection_page.load_panel(page_id, page_args)
        self.toggle_btn_group.SetSelected(SkinrPage.COLLECTION)

    def construct_pages(self):
        self.page_container = Container(name='page_container', parent=self.content, clipChildren=True)
        self.construct_studio_page(parent=self.page_container)
        self.construct_store_page(parent=self.page_container)
        self.construct_collection_page(parent=self.page_container)

    def construct_scene(self):
        try:
            self.scene_preview_panel = SKINRBackgroundContainer(name='preview_panel', parent=self.content)
        except Exception as exc:
            logger.exception('Failed to construct scene preview panel in SKINR: %s', exc)

    def construct_studio_page(self, parent):
        self.studio_page = StudioPageContainer(name='studio_page', parent=parent)
        self.toggle_btn_group.AddButton(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Title'), btnID=SkinrPage.STUDIO, uniqueUiName=pConst.UNIQUE_NAME_SKINR_STUDIO)

    def construct_store_page(self, parent):
        self.store_page = StorePage(name='store_page', parent=parent)
        self.toggle_btn_group.AddButton(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/Title'), btnID=SkinrPage.STORE, uniqueUiName=pConst.UNIQUE_NAME_SKINR_PARAGON_HUB)

    def construct_collection_page(self, parent):
        self.collection_page = CollectionPage(name='collection_page', parent=parent)
        self.toggle_btn_group.AddButton(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/Title'), btnID=SkinrPage.COLLECTION, uniqueUiName=pConst.UNIQUE_NAME_SKINR_COLLECTION)

    def OnBack(self):
        current_page.go_back()

    def OnForward(self):
        current_page.go_forward()

    def GetMenu(self):
        menu = super(ShipSKINRWindow, self).GetMenu()
        if is_qa():
            add_qa_context_menu(menu)
        return menu

    def OnHideUI(self):
        self.page_container.display = False

    def OnShowUI(self):
        self.page_container.display = True

    def CloseByUser(self, *args):
        try:
            if self.is_closing:
                return
            self.is_closing = True
            if current_page.can_leave_current_page():
                super(ShipSKINRWindow, self).CloseByUser(*args)
            else:
                self.is_closing = False
        except:
            super(ShipSKINRWindow, self).CloseByUser(*args)
            raise

    def _on_skin_sequencing_job_failed(self, _job_id, reason):
        if reason in SEQUENCE_FAILURE_REASON_TO_ERROR:
            error = SEQUENCE_FAILURE_REASON_TO_ERROR[reason]
            if error in SEQUENCING_ERROR_TEXT_BY_CODE:
                label = SEQUENCING_ERROR_TEXT_BY_CODE[error]
                ShowQuickMessage(GetByLabel(label))
