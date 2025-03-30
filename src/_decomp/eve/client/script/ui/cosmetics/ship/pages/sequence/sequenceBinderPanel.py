#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\sequence\sequenceBinderPanel.py
import logging
from carbonui import Align, PickState, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uiconst import OutputMode
from cosmetics.client.shipSkinComponentSvc import get_ship_skin_component_svc
from cosmetics.client.shipSkinSequencingSvc import get_ship_skin_sequencing_svc
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.ships.skins.live_data import current_skin_design, current_skin_design_signals
from cosmetics.common.cosmeticsConst import SEQUENCE_BINDER_TYPES
from cosmetics.common.ships.skins.static_data.slot import SlotsDataLoader
from cosmetics.common.ships.skins.static_data.slot_configuration import SlotConfigurationsDataLoader
from cosmetics.common.ships.skins.static_data.slot_name import SlotID, PATTERN_RELATED_SLOT_IDS
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship.pages.sequence import sequence_ui_signals
from eve.client.script.ui.cosmetics.ship.pages.sequence.sequenceBinderEntries import SequenceBinderCostEntryCompact
from eve.client.script.ui.cosmetics.ship.pages.studio.cosmeticSlot import CosmeticSlot
from eve.client.script.ui.cosmetics.ship.pages.studio.licenseSelector import LicenseSelector
from eve.common.lib import appConst
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException
log = logging.getLogger(__name__)
LINE_TEXTURES_BY_SLOT_ID_TYPE_ID = {SlotID.PRIMARY_NANOCOATING: {appConst.typeFermionic: ('res:/UI/Texture/classes/Cosmetics/Ship/sequencing/lines/left_1_ferm.png', (-20, 63, 45, 72)),
                              appConst.typeKerr: ('res:/UI/Texture/classes/Cosmetics/Ship/sequencing/lines/left_1_kerr.png', (-20, 60, 45, 170))},
 SlotID.SECONDARY_NANOCOATING: {appConst.typeFermionic: ('res:/UI/Texture/classes/Cosmetics/Ship/sequencing/lines/left_2_ferm.png', (-20, 21, 45, 44)),
                                appConst.typeKerr: ('res:/UI/Texture/classes/Cosmetics/Ship/sequencing/lines/left_2_kerr.png', (-20, 60, 45, 58))},
 SlotID.TERTIARY_NANOCOATING: {appConst.typeFermionic: ('res:/UI/Texture/classes/Cosmetics/Ship/sequencing/lines/left_3_ferm.png', (-20, -91, 45, 156)),
                               appConst.typeKerr: ('res:/UI/Texture/classes/Cosmetics/Ship/sequencing/lines/left_3_kerr.png', (-20, 4, 45, 58))},
 SlotID.TECH_AREA: {appConst.typeFermionic: ('res:/UI/Texture/classes/Cosmetics/Ship/sequencing/lines/left_4_ferm.png', (-20, -203, 45, 268)),
                    appConst.typeKerr: ('res:/UI/Texture/classes/Cosmetics/Ship/sequencing/lines/left_4_kerr.png', (-20, -108, 45, 170))},
 SlotID.PATTERN_MATERIAL: {appConst.typeFermionic: ('res:/UI/Texture/classes/Cosmetics/Ship/sequencing/lines/right_1_ferm.png', (-20, 90, 57, 17)),
                           appConst.typeKerr: ('res:/UI/Texture/classes/Cosmetics/Ship/sequencing/lines/right_1_kerr.png', (-20, 65, 45, 140))},
 SlotID.SECONDARY_PATTERN_MATERIAL: {appConst.typeFermionic: ('res:/UI/Texture/classes/Cosmetics/Ship/sequencing/lines/right_2_ferm.png', (-20, 19, 53, 28)),
                                     appConst.typeKerr: ('res:/UI/Texture/classes/Cosmetics/Ship/sequencing/lines/right_2_kerr.png', (-20, 90, 57, 31))},
 SlotID.PATTERN: {appConst.typeAlignment: ('res:/UI/Texture/classes/Cosmetics/Ship/sequencing/lines/right_3_align.png', (-20, 87, 56, 26))},
 SlotID.SECONDARY_PATTERN: {appConst.typeAlignment: ('res:/UI/Texture/classes/Cosmetics/Ship/sequencing/lines/right_4_align.png', (-20, 24, 55, 20))}}

class SequenceBinderPanel(ContainerAutoSize):
    is_loaded = False

    def __init__(self, **kw):
        super(SequenceBinderPanel, self).__init__(**kw)
        self.cost_entries = []

    def load_panel(self):
        if not self.is_loaded:
            self.is_loaded = True
            self.construct_layout()
            self.connect_signals()
        self.reconstruct_slots()
        self.update_values()
        self.anim_entry()

    def anim_entry(self):
        self.opacity = 0.0
        animations.MorphScalar(self, 'left', -200, 0, duration=0.6)
        animations.FadeTo(self, 0.0, 1.0, duration=0.3, timeOffset=0.6)

    def connect_signals(self):
        sequence_ui_signals.on_num_skins_changed.connect(self.on_num_skins_changed)
        current_skin_design_signals.on_component_instance_license_to_use_changed.connect(self.on_component_instance_license_to_use_changed)
        current_skin_design_signals.on_slot_fitting_changed.connect(self.on_slot_fitting_changed)
        ship_skin_signals.on_component_license_granted.connect(self.on_component_license_granted)

    def disconnect_signals(self):
        sequence_ui_signals.on_num_skins_changed.disconnect(self.on_num_skins_changed)
        current_skin_design_signals.on_component_instance_license_to_use_changed.disconnect(self.on_component_instance_license_to_use_changed)
        current_skin_design_signals.on_slot_fitting_changed.disconnect(self.on_slot_fitting_changed)
        ship_skin_signals.on_component_license_granted.disconnect(self.on_component_license_granted)

    def on_slot_fitting_changed(self, *args):
        self.reconstruct_slots()
        self.update_values()

    def on_component_instance_license_to_use_changed(self, component_id, license):
        self.update_values()

    def on_component_license_granted(self, *args):
        self.reconstruct_slots()
        self.update_values()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(SequenceBinderPanel, self).Close()

    def on_num_skins_changed(self, num_skins):
        self.update_values()

    def update_values(self):
        num_runs = get_ship_skin_sequencing_svc().get_num_runs()
        amount_by_type = current_skin_design.get().get_sequence_binder_amounts_required(num_runs)
        for entry in self.cost_entries:
            entry.update(amount_by_type[entry.type_id])

    def construct_layout(self):
        self.content = ContainerAutoSize(name='content', parent=self, align=Align.CENTERLEFT, height=512, top=64)
        self.left_cont = ContainerAutoSize(name='left_cont', parent=self.content, align=Align.TOLEFT)
        self.center_cont = Container(name='center_cont', parent=self.content, align=Align.TOLEFT, pickState=PickState.ON, width=100, top=64)
        self.right_cont = ContainerAutoSize(name='right_cont', parent=self.content, align=Align.TOLEFT)
        self.construct_center_cont()

    def reconstruct_slots(self):
        self.left_cont.Flush()
        self.right_cont.Flush()
        slot_config = SlotConfigurationsDataLoader.get_for_ship(current_skin_design.get().ship_type_id)
        y_offset_left = 118
        k_offset_right = 34
        y_offset_right = 94
        for slot_id in slot_config.slots:
            if slot_id == SlotID.PRIMARY_NANOCOATING:
                SlotCostEntry(parent=self.left_cont, slot_id=slot_id, top=0, align=Align.TOPRIGHT, alignMode=Align.CENTERRIGHT)
            elif slot_id == SlotID.SECONDARY_NANOCOATING:
                SlotCostEntry(parent=self.left_cont, slot_id=slot_id, top=y_offset_left, align=Align.TOPRIGHT, alignMode=Align.CENTERRIGHT)
            elif slot_id == SlotID.TERTIARY_NANOCOATING:
                SlotCostEntry(parent=self.left_cont, slot_id=slot_id, align=Align.TOPRIGHT, top=2 * y_offset_left, alignMode=Align.CENTERRIGHT)
            elif slot_id == SlotID.TECH_AREA:
                SlotCostEntry(parent=self.left_cont, slot_id=slot_id, align=Align.TOPRIGHT, top=3 * y_offset_left, alignMode=Align.CENTERRIGHT)
            elif slot_id == SlotID.PATTERN_MATERIAL:
                SlotCostEntry(parent=self.right_cont, slot_id=slot_id, align=Align.TOPLEFT, top=k_offset_right, alignMode=Align.CENTERLEFT)
            elif slot_id == SlotID.SECONDARY_PATTERN_MATERIAL:
                SlotCostEntry(parent=self.right_cont, slot_id=slot_id, align=Align.TOPLEFT, top=k_offset_right + y_offset_right, alignMode=Align.CENTERLEFT)
            elif slot_id == SlotID.PATTERN:
                SlotCostEntry(parent=self.right_cont, slot_id=slot_id, align=Align.TOPLEFT, top=k_offset_right + 2 * y_offset_right, alignMode=Align.CENTERLEFT)
            elif slot_id == SlotID.SECONDARY_PATTERN:
                SlotCostEntry(parent=self.right_cont, slot_id=slot_id, align=Align.TOPLEFT, top=k_offset_right + 3 * y_offset_right, alignMode=Align.CENTERLEFT)

    def construct_center_cont(self):
        for i, type_id in enumerate(SEQUENCE_BINDER_TYPES):
            cost_entry = SequenceBinderCostEntryCompact(parent=self.center_cont, type_id=type_id, align=Align.CENTERTOP, pickState=PickState.ON, top=45 + i * 97)
            self.cost_entries.append(cost_entry)


class SlotCostEntry(ContainerAutoSize):
    default_state = uiconst.UI_PICKCHILDREN

    def __init__(self, slot_id, **kw):
        super(SlotCostEntry, self).__init__(**kw)
        self.slot_id = slot_id
        self.line = None
        self.component = current_skin_design.get().slot_layout.get_component(self.slot_id)
        if self.component:
            svc = get_ship_skin_component_svc()
            component_data = self.component.get_component_data()
            try:
                self.bound_license = svc.get_bound_license(self.component.component_id, component_data.category)
                self.unbound_license = svc.get_unbound_license(self.component.component_id, component_data.category)
            except (GenericException, TimeoutException):
                ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
                self.bound_license = self.unbound_license = None

        else:
            self.opacity = 0.35
            self.bound_license = self.unbound_license = None
        self.construct_layout()
        self.connect_signals()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(SlotCostEntry, self).Close()

    def connect_signals(self):
        current_skin_design_signals.on_component_instance_license_to_use_changed.connect(self.on_component_instance_license_to_use_changed)
        sequence_ui_signals.on_component_license_selection_changed.connect(self.on_component_license_selection_changed)

    def disconnect_signals(self):
        current_skin_design_signals.on_component_instance_license_to_use_changed.disconnect(self.on_component_instance_license_to_use_changed)
        sequence_ui_signals.on_component_license_selection_changed.disconnect(self.on_component_license_selection_changed)

    def on_component_license_selection_changed(self):
        self.reconstruct_line()

    def on_component_instance_license_to_use_changed(self, component_id, license):
        if self.component and self.component.component_id == component_id:
            self.reconstruct_line()

    def construct_layout(self):
        slot_data = SlotsDataLoader.get_slot_data(self.slot_id)
        self.slot = SequenceStepCosmeticSlot(name='slot_{name}'.format(name=slot_data.internal_name), parent=self, slot_data=slot_data, component=self.component, align=self.alignMode, selectable=False)
        LicenseSelector(name='license_selector', parent=self, align=self.alignMode, component_instance=self.component, left=108)
        if self.component:
            self.reconstruct_line()

    def reconstruct_line(self):
        if self.line:
            self.line.Close()
        if not self.component or not self.component.sequence_binder_amount_required:
            return
        pos, texturePath = self._get_line_texture_path_and_position()
        align = Align.TOPLEFT if self.slot_id in PATTERN_RELATED_SLOT_IDS else Align.TOPRIGHT
        self.line = Sprite(name='line', parent=self, align=align, pos=pos, texturePath=texturePath, outputMode=OutputMode.COLOR_AND_GLOW, glowBrightness=0.75, color=eveThemeColor.THEME_ACCENT, pickState=PickState.ON)

    def _get_line_texture_path_and_position(self):
        try:
            texturePath, pos = LINE_TEXTURES_BY_SLOT_ID_TYPE_ID[self.slot_id][self.component.sequence_binder_type_id]
        except KeyError:
            log.exception('Line texture not found: slot_id: {}, component_id: {}, sequence_binder_type_id: {}'.format(self.slot_id, self.component.component_id, self.component.sequence_binder_type_id))
            texturePath = None
            pos = (0, 0, 0, 0)

        return (pos, texturePath)


class SequenceStepCosmeticSlot(CosmeticSlot):
    default_height = 128
    default_width = 128

    def _update_state_side_frame(self, animate):
        self.side_frame.display = False

    def construct_license_selector(self):
        self.license_selector = None
