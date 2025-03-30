#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\live_data\skin_design.py
import datetime
from carbon.common.script.sys.serviceConst import ROLE_QA
from collections import defaultdict
from cosmetics.common.ships.skins.static_data.pattern_blend_mode import PatternBlendMode, NO_SECONDARY_COLOR_BLEND_MODES
from cosmetics.common.ships.skins.static_data.slot_configuration import SlotConfigurationsDataLoader
from cosmetics.common.ships.skins.static_data.skin_tier import ShipSkinTierTable
from cosmetics.common.ships.skins.static_data.slot_name import SlotID
from google.protobuf.timestamp_pb2 import Timestamp
from signals import Signal

class BaseSkinDesign(object):
    SLOT_LAYOUT_CLASS = None
    CHARACTER_PROTO = None
    SKIN_ATTRIBUTES_PROTO = None
    SKIN_TIER_PROTO = None

    def __init__(self, creator_character_id = None, tier_table = None):
        self.construct_signals()
        self._ship_type_id = None
        self._slot_layout = None
        self.clear()
        self.creator_character_id = creator_character_id
        self._tier_table = tier_table if tier_table is not None else ShipSkinTierTable()

    def construct_signals(self):
        self.on_name_changed = Signal('on_name_changed')
        self.on_line_name_changed = Signal('on_line_name_changed')
        self.on_slot_fitting_changed = Signal('on_slot_fitting_changed')
        self.on_ship_type_id_changed = Signal('on_ship_type_id_changed')
        self.on_tier_level_changed = Signal('on_tier_level_changed')
        self.on_component_instance_license_to_use_changed = Signal('on_component_instance_license_to_use_changed')
        self.on_pattern_blend_mode_changed = Signal('on_pattern_blend_mode_changed')
        self.on_component_attribute_changed = Signal('on_component_attribute_changed')

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = u'{}'.format(value) if value else ''
        self.on_name_changed(self.name)

    @property
    def full_name(self):
        return self._name

    @property
    def line_name(self):
        return self._line_name

    @line_name.setter
    def line_name(self, value):
        self._line_name = u'{}'.format(value) if value else ''
        self.on_line_name_changed(self.line_name)

    @property
    def creator_character_id(self):
        return self._creator_character_id

    @creator_character_id.setter
    def creator_character_id(self, value):
        self._creator_character_id = value

    @property
    def ship_type_id(self):
        return self._ship_type_id

    @ship_type_id.setter
    def ship_type_id(self, value):
        if self.ship_type_id != value:
            self._ship_type_id = value
            old_layout = None
            if self._slot_layout is not None:
                old_layout = self._slot_layout
            self._initialize_slot_layout()
            if old_layout is not None:
                self._slot_layout.copy_slots_from_other(old_layout)
            self._compute_tier_level()
            self.on_ship_type_id_changed(self.ship_type_id)
        self._connect_component_instance_signals()
        self._apply_type_id_to_components(value)

    def _apply_type_id_to_components(self, value):
        pass

    @property
    def saved_skin_design_id(self):
        return self._saved_skin_design_id

    @saved_skin_design_id.setter
    def saved_skin_design_id(self, value):
        self._saved_skin_design_id = value

    @property
    def design_hex(self):
        return self._design_hex

    @design_hex.setter
    def design_hex(self, value):
        self._design_hex = value

    def copy_ship_type_and_layout(self, ship_type_id, layout):
        self._slot_layout = layout
        self.ship_type_id = ship_type_id

    @property
    def tier_level(self):
        return self._tier_level

    @tier_level.setter
    def tier_level(self, value):
        self._tier_level = value

    @property
    def slot_layout(self):
        if self._slot_layout is None:
            self._initialize_slot_layout()
        return self._slot_layout

    @property
    def sequenced(self):
        return self._sequenced

    @sequenced.setter
    def sequenced(self, value):
        self._sequenced = value

    @property
    def tier_points(self):
        return self.compute_current_points_value()

    @property
    def tier_thresholds(self):
        return self._tier_table.get_thresholds_for_ship_type(self.ship_type_id)

    def compute_current_points_value(self):
        total_points = 0
        for slot_id, component_instance in self.slot_layout.fitted_slots.iteritems():
            if component_instance.get_component_data().points_value:
                if self.slot_layout.pattern_blend_mode in NO_SECONDARY_COLOR_BLEND_MODES and slot_id == SlotID.SECONDARY_PATTERN_MATERIAL:
                    pass
                else:
                    total_points += component_instance.get_component_data().points_value

        if session and session.role & ROLE_QA:
            total_points += self._qa_tier_points
        return total_points

    def get_sequence_binder_amounts_required(self, number_of_runs):
        amount_by_type_id = defaultdict(int)
        for instance in self.slot_layout.fitted_slots.values():
            amount_required = instance.sequence_binder_amount_required
            if amount_required > 0:
                type_id = instance.sequence_binder_type_id
                amount_by_type_id[type_id] += amount_required * number_of_runs

        return amount_by_type_id

    def fit_slot(self, slot_id, component_id, licence = None):
        if component_id:
            component_instance = self.create_component_instance(component_id)
            component_instance.component_license_to_use = licence
            component_instance.on_licence_to_use_changed.connect(self.on_component_instance_license_to_use_changed)
            component_instance.on_attribute_changed.connect(self._on_component_instance_attribute_changed)
        else:
            component_instance = None
        self.slot_layout.fit_slot(slot_id, component_instance)
        return component_instance

    def swap_slots(self, slot_id_1, slot_id_2):
        self.slot_layout.swap_slots(slot_id_1, slot_id_2)

    def unfit_all(self):
        self.slot_layout.unfit_all()

    def _on_component_instance_attribute_changed(self, component_instance, attribute_id, value):
        slot_id = self.slot_layout.get_slot_id(component_instance)
        if slot_id:
            self.on_component_attribute_changed(slot_id, attribute_id, value)

    def get_fitted_component_instance(self, slot_id):
        return self.slot_layout.slots.get(slot_id, None)

    def has_fitted_components(self):
        return bool(self.get_fitted_components())

    def get_fitted_components(self):
        return [ component_instance for component_instance in self.slot_layout.slots.itervalues() if component_instance ]

    def _initialize_slot_layout(self):
        config = SlotConfigurationsDataLoader.get_for_ship(self._ship_type_id)
        if config:
            self._slot_layout = self.SLOT_LAYOUT_CLASS(config)
            self._slot_layout.on_slot_fitting_changed.connect(self._on_slot_fitting_changed)
            self._slot_layout.on_pattern_blend_mode_changed.connect(self._on_pattern_blend_mode_changed)
        else:
            self._slot_layout = None

    def _on_slot_fitting_changed(self, slot_id, component_instance):
        self._compute_tier_level()
        self.on_slot_fitting_changed(slot_id, component_instance)

    def _on_pattern_blend_mode_changed(self, value):
        self._compute_tier_level()
        self.on_pattern_blend_mode_changed(value)

    def clear(self):
        self._name = None
        self._line_name = None
        self._creator_character_id = None
        self._tier_level = 1
        if self.slot_layout:
            for component_instance in self.slot_layout.fitted_slots.values():
                component_instance.on_licence_to_use_changed.disconnect(self.on_component_instance_license_to_use_changed)
                component_instance.on_attribute_changed.disconnect(self._on_component_instance_attribute_changed)

        self._slot_layout = None
        self._sequenced = None
        self._saved_skin_design_id = None
        self._design_hex = None
        self._qa_tier_points = 0

    def _compute_tier_level(self):
        new_tier_level = self._tier_table.get_tier_level_for_design(self)
        if new_tier_level == self.tier_level:
            return
        self.tier_level = new_tier_level
        self.on_tier_level_changed(new_tier_level)

    def __eq__(self, other):
        if other is None:
            return False
        return self.name == other.name and self.line_name == other.line_name and self.creator_character_id == other.creator_character_id and self.ship_type_id == other.ship_type_id and self.slot_layout == other.slot_layout and self.tier_level == other.tier_level

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        design_str = 'Name: {name}\nLine:\n{line}\nCreated by {char_id} for ship type {ship_type}\nTier level {tier}\n'.format(name=self.name.encode('utf-8'), line=self.line_name.encode('utf-8') if self.line_name is not None else 'No line name', char_id=self.creator_character_id, ship_type=self.ship_type_id, tier=self.tier_level)
        design_str += 'Layout:\n %s' % self.slot_layout
        return design_str

    def update_from_other(self, other_design, saved_skin_design_id = None):
        self.clear()
        self.creator_character_id = other_design.creator_character_id
        self._name = other_design.name
        self._line_name = other_design.line_name
        self.slot_layout.copy_slots_from_other(other_design.slot_layout, should_copy_components_to_use=True)
        self.ship_type_id = other_design.ship_type_id
        self.sequenced = other_design.sequenced
        self.saved_skin_design_id = saved_skin_design_id
        self.design_hex = other_design.design_hex
        self._compute_tier_level()

    def clean_up_skin(self):
        if self.slot_layout is None:
            return
        if self.slot_layout.pattern_blend_mode in NO_SECONDARY_COLOR_BLEND_MODES or self.slot_layout.slots[SlotID.SECONDARY_PATTERN] is None:
            self.slot_layout.unfit_slot(SlotID.SECONDARY_PATTERN_MATERIAL, True)

    def _connect_component_instance_signals(self):
        for component_instance in self.slot_layout.fitted_slots.values():
            component_instance.on_licence_to_use_changed.connect(self.on_component_instance_license_to_use_changed)
            component_instance.on_attribute_changed.connect(self._on_component_instance_attribute_changed)

    @classmethod
    def copy_from_other(cls, other_design, new_creator_character_id = None, should_copy_components_to_use = False):
        if other_design is not None:
            if new_creator_character_id is not None:
                design_copy = cls(new_creator_character_id)
            else:
                design_copy = cls(other_design.creator_character_id)
            design_copy.name = other_design.name
            design_copy.line_name = other_design.line_name
            design_copy.ship_type_id = other_design.ship_type_id
            design_copy.slot_layout.copy_slots_from_other(other_design.slot_layout, should_copy_components_to_use=should_copy_components_to_use)
            design_copy.sequenced = other_design.sequenced
            design_copy.saved_skin_design_id = other_design.saved_skin_design_id
            design_copy.design_hex = other_design.design_hex
            design_copy.tier_level = other_design.tier_level
            return design_copy

    @classmethod
    def build_from_proto(cls, payload):
        design = cls(payload.creator.sequential)
        design.name = payload.name
        design.line_name = payload.line_name if len(payload.line_name) > 0 else None
        design.ship_type_id = payload.layout.ship_type.sequential
        design.slot_layout.fit_slots_from_proto(payload.layout)
        design.tier_level = payload.tier.level
        if payload.HasField('first_sequenced'):
            design.sequenced = datetime.datetime.fromtimestamp(payload.first_sequenced.seconds)
        return design

    @classmethod
    def build_proto_from_design(cls, skin_design):
        attributes = cls.SKIN_ATTRIBUTES_PROTO()
        attributes.name = skin_design.name
        attributes.line_name = skin_design.line_name if skin_design.line_name is not None else ''
        attributes.creator.CopyFrom(cls.CHARACTER_PROTO(sequential=skin_design.creator_character_id))
        attributes.layout.CopyFrom(cls.SLOT_LAYOUT_CLASS.build_proto_from_layout(skin_design.ship_type_id, skin_design.slot_layout))
        attributes.tier.CopyFrom(cls.SKIN_TIER_PROTO(level=skin_design.tier_level))
        if skin_design.sequenced is None:
            attributes.not_sequenced = True
        else:
            attributes.sequenced = Timestamp().FromDatetime(skin_design.sequenced)
        return attributes

    def create_component_instance(self, component_id, **kwargs):
        raise NotImplementedError

    @property
    def qa_tier_points(self):
        if session and session.role & ROLE_QA:
            return self._qa_tier_points
        return 0

    def set_qa_tier_points(self, value):
        if session and session.role & ROLE_QA:
            self._qa_tier_points = value
            self._compute_tier_level()
            self.on_tier_level_changed(self.tier_level)
