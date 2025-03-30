#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\live_data\slot_layout.py
import logging
from collections import defaultdict
from cosmetics.common.ships.skins.errors import SlotConfigurationUnavailable, ComponentsUnavailable, SlotDataUnavailable, ComponentDataUnavailable, ComponentNotAllowedInSlot, SlotDisallowedForComponent, InvalidBlendMode, UnusedComponentsFitted, MissingPatternColor
from cosmetics.common.ships.skins.live_data.component_instance import BasePatternComponentInstance
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from cosmetics.common.ships.skins.sequencing_util import build_component_licenses_per_type_dict
from cosmetics.common.ships.skins.static_data.pattern_blend_mode import PatternBlendMode, NO_SECONDARY_COLOR_BLEND_MODES
from cosmetics.common.ships.skins.static_data.slot import SlotsDataLoader
from cosmetics.common.ships.skins.static_data.slot_configuration import SlotConfiguration, SlotConfigurationsDataLoader
from cosmetics.common.ships.skins.static_data.slot_name import SlotID
from signals import Signal
log = logging.getLogger(__name__)
DEFAULT_BLEND_MODE = PatternBlendMode.OVERLAY

class BaseSlotLayout(object):
    LAYOUT_PROTO = None
    SLOT_IDENTIFIER_PROTO = None
    SHIP_TYPE_PROTO = None

    def __init__(self, slot_config):
        self._slot_config = slot_config
        self._slots = {}
        self._pattern_blend_mode = DEFAULT_BLEND_MODE
        self._init_slots()
        self.on_slot_fitting_changed = Signal('on_slot_fitting_changed')
        self.on_pattern_blend_mode_changed = Signal('on_pattern_blend_mode_changed')

    def _init_slots(self):
        for slot_id in self._slot_config.slots:
            self._slots[slot_id] = None

    @property
    def slot_config(self):
        return self._slot_config

    @property
    def slots(self):
        return self._slots

    @property
    def pattern_blend_mode(self):
        return self._pattern_blend_mode

    @pattern_blend_mode.setter
    def pattern_blend_mode(self, value):
        if value == PatternBlendMode.UNSPECIFIED:
            value = DEFAULT_BLEND_MODE
        self._pattern_blend_mode = value
        self.on_pattern_blend_mode_changed(value)

    def get_component(self, slot_id):
        return self.slots[slot_id]

    def get_slot_id(self, component_instance):
        for slot_id, _component in self._slots.items():
            if component_instance == _component:
                return slot_id

    @property
    def fitted_slots(self):
        return {slot_id:instance for slot_id, instance in self.slots.items() if instance}

    def fit_slot(self, slot_id, component_instance = None, notify = True):
        self._fit_slot(slot_id, component_instance, notify)
        if component_instance:
            component_instance.apply_user_authored_values()

    def _fit_slot(self, slot_id, component_instance = None, notify = True):
        if slot_id not in self._slots:
            return
        if component_instance is None:
            self.unfit_slot(slot_id, notify)
        elif self._validate(slot_id, component_instance):
            previous_component = self._slots[slot_id]
            if previous_component is not None:
                component_instance.copy_params_from_other(previous_component)
            self._slots[slot_id] = component_instance
            self._check_select_default_component_instance_license(component_instance)
            if notify:
                self.on_slot_fitting_changed(slot_id, component_instance)

    def swap_slots(self, slot_id_1, slot_id_2):
        instance_1 = self._slots[slot_id_1]
        instance_2 = self._slots[slot_id_2]
        self._slots[slot_id_1] = instance_2
        self._slots[slot_id_2] = instance_1
        self.on_slot_fitting_changed(slot_id_1, instance_2)
        self.on_slot_fitting_changed(slot_id_2, instance_1)

    def unfit_slot(self, slot_id, notify = True):
        self._slots[slot_id] = None
        if notify:
            self.on_slot_fitting_changed(slot_id, None)
        if slot_id == SlotID.PATTERN:
            self.unfit_slot(SlotID.PATTERN_MATERIAL, notify)
            self.unfit_slot(SlotID.SECONDARY_PATTERN, notify)
            self.pattern_blend_mode = DEFAULT_BLEND_MODE
        elif slot_id == SlotID.SECONDARY_PATTERN:
            self.unfit_slot(SlotID.SECONDARY_PATTERN_MATERIAL, notify)
            self.pattern_blend_mode = DEFAULT_BLEND_MODE

    def unfit_all(self):
        for slot_id in self._slots.keys():
            self.unfit_slot(slot_id)

    def _check_select_default_component_instance_license(self, component_instance):
        if not component_instance.component_license_to_use:
            component_type = component_instance.get_component_data().category
            license = self.get_component_license(component_instance.component_id, component_type)
            if license:
                component_instance.component_license_to_use = license

    def copy_slots_from_other(self, other_layout, should_copy_components_to_use = False):
        for slot_id, component_instance in other_layout.slots.items():
            if component_instance:
                component_instance_copy = self.create_component_instance(component_instance.component_id)
                component_instance_copy.copy_params_from_other(component_instance, should_copy_components_to_use)
                self._fit_slot(slot_id, component_instance_copy, notify=False)
            else:
                self._fit_slot(slot_id, None, notify=False)

        self.pattern_blend_mode = other_layout.pattern_blend_mode

    def _validate(self, slot_id, component_instance):
        slot_data = SlotsDataLoader.get_slot_data(slot_id)
        if not slot_data:
            raise SlotDataUnavailable()
        component_data = component_instance.get_component_data()
        if not component_data:
            raise ComponentDataUnavailable()
        if component_data.category not in slot_data.allowed_component_categories:
            raise ComponentNotAllowedInSlot()
        if slot_id in component_data.disallowed_slot_ids:
            raise SlotDisallowedForComponent()
        return True

    def validate_layout(self):
        try:
            for slot_id, component_instance in self.fitted_slots.items():
                self._validate(slot_id, component_instance)

        except (SlotDataUnavailable,
         ComponentDataUnavailable,
         ComponentNotAllowedInSlot,
         SlotDisallowedForComponent) as e:
            log.exception(e)
            return False

        try:
            self.validate_patterns()
        except (MissingPatternColor, InvalidBlendMode, UnusedComponentsFitted) as e:
            log.exception(e)
            return False

        return True

    def validate_patterns(self):
        nb_patterns = len([ x for x, y in self.fitted_slots.iteritems() if isinstance(y, BasePatternComponentInstance) ])
        if nb_patterns > 1 and self.pattern_blend_mode == PatternBlendMode.UNSPECIFIED:
            raise InvalidBlendMode()
        if self.pattern_blend_mode in NO_SECONDARY_COLOR_BLEND_MODES:
            secondary_color = self.get_component(SlotID.SECONDARY_PATTERN_MATERIAL)
            if secondary_color is not None:
                raise UnusedComponentsFitted()
        else:
            nb_pattern_colors = len([ x for x, y in self.fitted_slots.iteritems() if x in [SlotID.SECONDARY_PATTERN_MATERIAL, SlotID.PATTERN_MATERIAL] ])
            if nb_pattern_colors != nb_patterns:
                raise MissingPatternColor()

    def validate_licenses(self, number_of_runs, licenses, exact_match = False):
        if any([ x is None for x in licenses ]):
            return False
        licenses_available = build_component_licenses_per_type_dict(licenses)
        component_required_amounts = defaultdict(int)
        for component_instance in self.fitted_slots.values():
            component_required_amounts[component_instance.component_id] += number_of_runs

        for component_id, nb_required in component_required_amounts.iteritems():
            if component_id not in licenses_available:
                return False
            if ComponentLicenseType.LIMITED in licenses_available[component_id]:
                if exact_match:
                    if nb_required < licenses_available[component_id][ComponentLicenseType.LIMITED].remaining_license_uses:
                        return False
                    if nb_required != licenses_available[component_id][ComponentLicenseType.LIMITED].remaining_license_uses:
                        if ComponentLicenseType.UNLIMITED not in licenses_available[component_id]:
                            return False
                    elif ComponentLicenseType.UNLIMITED in licenses_available[component_id]:
                        return False
                elif nb_required > licenses_available[component_id][ComponentLicenseType.LIMITED].remaining_license_uses:
                    if ComponentLicenseType.UNLIMITED not in licenses_available[component_id]:
                        return False
            elif ComponentLicenseType.UNLIMITED not in licenses_available[component_id]:
                return False

        return True

    def get_amount_of_components_with_license_type(self, component_id, license_type = None):
        component_amount = 0
        for component_instance in self.fitted_slots.values():
            if component_instance.component_id == component_id:
                license = component_instance.component_license_to_use
                if license_type is None or license is None:
                    component_amount += 1
                elif license.license_type == license_type:
                    component_amount += 1

        return component_amount

    def __eq__(self, other):
        if other is None:
            return False
        if len(self.slots) != len(other.slots):
            return False
        for slot_id, slot_data in self.slots.items():
            if slot_id not in other.slots:
                return False
            if slot_data != other.slots[slot_id]:
                return False

        if self.pattern_blend_mode != other.pattern_blend_mode:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        result = ''
        for slot_id, slot_data in self._slots.iteritems():
            result += 'slot %s: %s\n' % (slot_id, slot_data)

        result += 'blend mode: %s' % self.pattern_blend_mode
        return result

    @classmethod
    def copy_from_other(cls, other_layout):
        layout_copy = cls(other_layout.slot_config)
        layout_copy.copy_from_other(other_layout)
        return layout_copy

    @classmethod
    def build_from_proto(cls, payload):
        ship_type_id = payload.ship_type.sequential
        slot_config = SlotConfigurationsDataLoader.get_for_ship(ship_type_id)
        if not slot_config:
            raise SlotConfigurationUnavailable()
        slot_layout = cls(slot_config)
        slot_layout.fit_slots_from_proto(payload)
        slot_layout.pattern_blend_mode = payload.pattern_blend_mode
        return slot_layout

    def fit_slots_from_proto(self, payload):
        for slot in payload.slots:
            component_id = None
            if slot.configuration.HasField('coating'):
                component_id = slot.configuration.coating.coating.sequential
            elif slot.configuration.HasField('pattern'):
                component_id = slot.configuration.pattern.pattern.sequential
            if component_id is not None:
                component_instance = self.create_component_instance(component_id)
                if not component_instance:
                    log.error('unable to find component id %s, skipping it from layout %s' % (component_id, payload))
                    continue
                if slot.configuration.HasField('coating'):
                    component_instance.build_params_from_proto(slot.configuration.coating.configuration)
                elif slot.configuration.HasField('pattern'):
                    component_instance.build_params_from_proto(slot.configuration.pattern.configuration)
                self._fit_slot(slot.id.sequential, component_instance)

        self.pattern_blend_mode = payload.pattern_blend_mode

    @classmethod
    def build_proto_from_layout(cls, ship_type_id, layout):
        proto_layout = cls.LAYOUT_PROTO()
        slot_list = []
        for slot_id, slot_data in layout.slots.iteritems():
            if slot_data is not None:
                slot_list.append(cls.LAYOUT_PROTO.Slot(id=cls.SLOT_IDENTIFIER_PROTO(sequential=slot_id), configuration=cls.build_config_proto_from_component_instance(slot_data)))

        proto_layout.slots.extend(slot_list)
        proto_layout.ship_type.CopyFrom(cls.SHIP_TYPE_PROTO(sequential=ship_type_id))
        proto_layout.pattern_blend_mode = layout.pattern_blend_mode
        return proto_layout

    def create_component_instance(self, component_id):
        raise NotImplementedError

    @classmethod
    def build_config_proto_from_component_instance(cls, component_instance):
        raise NotImplementedError

    def get_component_license(self, component_id, component_type):
        raise NotImplementedError
