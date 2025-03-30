#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\live_data\skin_design.py
from cosmetics.client.ships.skins.live_data.component_instance import create_component_instance
from cosmetics.client.ships.skins.live_data.slot_layout import SlotLayout
from cosmetics.client.ships.skins.static_data import hull_type_projections
from cosmetics.common.ships.skins.live_data.skin_design import BaseSkinDesign
from cosmetics.common.ships.skins.static_data.slot_name import PATTERN_SLOT_IDS
from eveProto.generated.eve_public.character.character_pb2 import Identifier as CharacterIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.thirdparty_pb2 import Attributes, Tier
from eveProto.generated.eve_public.ship.ship_type_pb2 import Identifier as ShipTypeIdentifier

class SkinDesign(BaseSkinDesign):
    SLOT_LAYOUT_CLASS = SlotLayout
    CHARACTER_PROTO = CharacterIdentifier
    TYPE_PROTO = ShipTypeIdentifier
    SKIN_ATTRIBUTES_PROTO = Attributes
    SKIN_TIER_PROTO = Tier

    def create_component_instance(self, component_id, **kwargs):
        scaling_multiplier = hull_type_projections.get_default_scaling_for_type(self.ship_type_id)
        return create_component_instance(component_id, scaling_multiplier=scaling_multiplier)

    def validate_licenses(self, number_of_runs):
        licenses = []
        for component_instance in self.get_fitted_components():
            if component_instance.component_license_to_use is not None:
                component_id = component_instance.component_id
                component_type = component_instance.category
                license_type = component_instance.component_license_to_use.license_type
                license = self.slot_layout.get_component_license_of_type(component_id, component_type, license_type)
                licenses.append(license)

        return self.slot_layout.validate_licenses(number_of_runs, licenses)

    def validate_layout(self):
        return self.slot_layout.validate_layout()

    def _apply_type_id_to_components(self, value):
        for slot_id in PATTERN_SLOT_IDS:
            component_instance = self.get_fitted_component_instance(slot_id)
            if component_instance is not None:
                component_instance.scaling_multiplier = hull_type_projections.get_default_scaling_for_type(value)
