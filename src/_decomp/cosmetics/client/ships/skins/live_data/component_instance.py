#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\live_data\component_instance.py
from cosmetics.client.shipSkinComponentSvc import get_ship_skin_component_svc
from cosmetics.client.ships import ship_skin_signals
from cosmetics.common.ships.skins.live_data.component_instance import BaseMaterialComponentInstance, BasePatternComponentInstance
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from cosmetics.common.ships.skins.static_data.component import ComponentsDataLoader
from cosmetics.common.ships.skins.static_data.component_category import ComponentCategory
from cosmetics.common.ships.skins.static_data.pattern_attribute import PatternAttribute
from eve.client.script.ui.cosmetics.ship.pages.studio import patternProjectionUtil
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.slot.slot_pb2 import Configuration as SlotConfiguration
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.coating.coating_pb2 import Configuration as CoatingConfiguration, Identifier as CoatingIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.pattern.pattern_pb2 import Configuration as PatternConfiguration, Identifier as PatternIdentifier
from eveProto.generated.eve_public.math.vector_pb2 import Vector3, Vector4

def create_component_instance(component_id, **kwargs):
    component_data = ComponentsDataLoader.get_component_data(component_id)
    if component_data:
        if component_data.category in (ComponentCategory.MATERIAL, ComponentCategory.METALLIC):
            return MaterialComponentInstance(component_id)
        if component_data.category == ComponentCategory.PATTERN:
            return PatternComponentInstance(component_id, **kwargs)


def build_config_proto_from_component_instance(component_instance):
    config = SlotConfiguration()
    if isinstance(component_instance, MaterialComponentInstance):
        config.coating.CopyFrom(SlotConfiguration.Coating(coating=CoatingIdentifier(sequential=component_instance.component_id), configuration=component_instance.build_proto()))
    elif isinstance(component_instance, PatternComponentInstance):
        config.pattern.CopyFrom(SlotConfiguration.Pattern(pattern=PatternIdentifier(sequential=component_instance.component_id), configuration=component_instance.build_proto()))
    return config


class MaterialComponentInstance(BaseMaterialComponentInstance):
    VECTOR3_PROTO = Vector3
    VECTOR4_PROTO = Vector4
    COATING_CONFIGURATION_PROTO = CoatingConfiguration

    def __init__(self, component_id):
        super(MaterialComponentInstance, self).__init__(component_id)
        ship_skin_signals.on_component_license_granted.connect(self._on_component_license_granted)

    def __del__(self):
        ship_skin_signals.on_component_license_granted.disconnect(self._on_component_license_granted)

    def _on_component_license_granted(self, component_id, license_type, quantity):
        if self.component_license_to_use is None or self.component_license_to_use.license_type == ComponentLicenseType.UNLIMITED:
            return
        if self.component_license_to_use.license_type == license_type and self.component_license_to_use.component_id == component_id:
            self.component_license_to_use = get_ship_skin_component_svc().get_license(component_id, self.category, license_type)


class PatternComponentInstance(BasePatternComponentInstance):
    VECTOR3_PROTO = Vector3
    VECTOR4_PROTO = Vector4
    PATTERN_CONFIGURATION_PROTO = PatternConfiguration

    def __init__(self, component_id, scaling_multiplier = 1.0):
        super(PatternComponentInstance, self).__init__(component_id, scaling_multiplier)
        ship_skin_signals.on_component_license_granted.connect(self._on_component_license_granted)

    def __del__(self):
        ship_skin_signals.on_component_license_granted.disconnect(self._on_component_license_granted)

    def _on_component_license_granted(self, component_id, license_type, quantity):
        if self.component_license_to_use is None or self.component_license_to_use.license_type == ComponentLicenseType.UNLIMITED:
            return
        if self.component_license_to_use.license_type == license_type and self.component_license_to_use.component_id == component_id:
            self.component_license_to_use = get_ship_skin_component_svc().get_license(component_id, self.category, license_type)

    def apply_user_authored_values(self):
        self._apply_user_authored_values()
        self.on_attribute_changed(self, PatternAttribute.POSITION, self._position)
        self.on_attribute_changed(self, PatternAttribute.ROTATION, self._rotation)

    def _apply_user_authored_values(self):
        self._position, self._rotation = patternProjectionUtil.get_pattern_projection_position_and_rotation(self.ellipsoid_center, self.ellipsoid_radii, self.offset_u_ratio, self.offset_v_ratio, self.yaw, self.pitch, self.roll)
