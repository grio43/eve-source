#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\live_data\component_instance.py
import math
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from cosmetics.common.ships.skins.static_data.component import ComponentsDataLoader
from cosmetics.common.ships.skins.static_data.pattern_attribute import PatternAttribute
from signals import Signal
DEFAULT_SCALING_RATIO = 0.5
DEFAULT_OFFSET_RATIO = 0.0
DEFAULT_YAW = 0.999
DEFAULT_PITCH = 0.999
DEFAULT_ROLL = 0.0
DEFAULT_MIRRORED = False

class BaseComponentInstance(object):
    VECTOR3_PROTO = None
    VECTOR4_PROTO = None

    def __init__(self, component_id):
        self._component_id = component_id
        self._component_license_to_use = None
        self.on_licence_to_use_changed = Signal('on_licence_to_use_changed')
        self.on_attribute_changed = Signal('on_attribute_changed')

    @property
    def component_id(self):
        return self._component_id

    @property
    def component_license_to_use(self):
        return self._component_license_to_use

    @component_license_to_use.setter
    def component_license_to_use(self, value):
        self._component_license_to_use = value
        self.on_licence_to_use_changed(self.component_id, value)

    def get_component_data(self):
        if not self._component_id:
            return None
        return ComponentsDataLoader.get_component_data(self._component_id)

    def copy_params_from_other(self, other_component, should_copy_components_to_use = False):
        if should_copy_components_to_use:
            self.component_license_to_use = other_component.component_license_to_use

    def build_params_from_proto(self, payload):
        raise NotImplementedError

    def build_proto(self):
        raise NotImplementedError

    def get_component_license(self):
        return self.component_license_to_use

    @property
    def sequence_binder_type_id(self):
        return self.get_component_data().sequence_binder_type_id

    @property
    def category(self):
        return self.get_component_data().category

    @property
    def sequence_binder_amount_required(self):
        if self.component_license_to_use and self.component_license_to_use.license_type == ComponentLicenseType.UNLIMITED:
            return self.get_component_data().sequence_binder_required_amount
        limited_item_type = self.get_component_data().get_item_type(ComponentLicenseType.LIMITED)
        unlimited_item_type = self.get_component_data().get_item_type(ComponentLicenseType.UNLIMITED)
        if unlimited_item_type and not limited_item_type:
            return self.get_component_data().sequence_binder_required_amount
        return 0

    @property
    def sequence_binder_amount_required_if_bound(self):
        return self.get_component_data().sequence_binder_required_amount

    def apply_user_authored_values(self):
        pass

    def _apply_user_authored_values(self):
        pass


class BaseMaterialComponentInstance(BaseComponentInstance):
    COATING_CONFIGURATION_PROTO = None

    def __init__(self, component_id):
        super(BaseMaterialComponentInstance, self).__init__(component_id)
        self._diffuse_color = [0,
         0,
         0,
         0]
        self._dust_diffuse_color = [0,
         0,
         0,
         0]
        self._fresnel_color = [0,
         0,
         0,
         0]
        self._gloss = [0,
         0,
         0,
         0]

    @property
    def diffuse_color(self):
        return self._diffuse_color

    @diffuse_color.setter
    def diffuse_color(self, value):
        self._diffuse_color = value

    @property
    def dust_diffuse_color(self):
        return self._dust_diffuse_color

    @dust_diffuse_color.setter
    def dust_diffuse_color(self, value):
        self._dust_diffuse_color = value

    @property
    def fresnel_color(self):
        return self._fresnel_color

    @fresnel_color.setter
    def fresnel_color(self, value):
        self._fresnel_color = value

    @property
    def gloss(self):
        return self._gloss

    @gloss.setter
    def gloss(self, value):
        self._gloss = value

    def copy_params_from_other(self, other_component, should_copy_components_to_use = False):
        self.diffuse_color = other_component.diffuse_color
        self.dust_diffuse_color = other_component.dust_diffuse_color
        self.fresnel_color = other_component.fresnel_color
        self.gloss = other_component.gloss
        super(BaseMaterialComponentInstance, self).copy_params_from_other(other_component, should_copy_components_to_use)

    def build_params_from_proto(self, payload):
        self.diffuse_color = [payload.diffuse_color.x,
         payload.diffuse_color.y,
         payload.diffuse_color.z,
         payload.diffuse_color.w]
        self.dust_diffuse_color = [payload.dust_diffuse_color.x,
         payload.dust_diffuse_color.y,
         payload.dust_diffuse_color.z,
         payload.dust_diffuse_color.w]
        self.fresnel_color = [payload.fresnel_color.x,
         payload.fresnel_color.y,
         payload.fresnel_color.z,
         payload.fresnel_color.w]
        self.gloss = [payload.gloss.x,
         payload.gloss.y,
         payload.gloss.z,
         payload.gloss.w]

    def build_proto(self):
        config = self.COATING_CONFIGURATION_PROTO()
        config.diffuse_color.CopyFrom(self.VECTOR4_PROTO(x=self._diffuse_color[0], y=self._diffuse_color[1], z=self._diffuse_color[2], w=self._diffuse_color[3]))
        config.dust_diffuse_color.CopyFrom(self.VECTOR4_PROTO(x=self._dust_diffuse_color[0], y=self._dust_diffuse_color[1], z=self._dust_diffuse_color[2], w=self._dust_diffuse_color[3]))
        config.fresnel_color.CopyFrom(self.VECTOR4_PROTO(x=self._fresnel_color[0], y=self._fresnel_color[1], z=self._fresnel_color[2], w=self._fresnel_color[3]))
        config.gloss.CopyFrom(self.VECTOR4_PROTO(x=self._gloss[0], y=self._gloss[1], z=self._gloss[2], w=self._gloss[3]))
        return config

    def __eq__(self, other):
        if other is None:
            return False
        return self.component_id == other.component_id and self.diffuse_color == other.diffuse_color and self.dust_diffuse_color == other.dust_diffuse_color and self.fresnel_color == other.fresnel_color and self.gloss == other.gloss

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        result = ''
        result += 'component id: %s\n' % self.component_id
        result += 'params: \n'
        result += 'diffuse color: %s %s %s %s\n' % (self.diffuse_color[0],
         self.diffuse_color[1],
         self.diffuse_color[2],
         self.diffuse_color[3])
        result += 'dust diffuse color: %s %s %s %s\n' % (self.dust_diffuse_color[0],
         self.dust_diffuse_color[1],
         self.dust_diffuse_color[2],
         self.dust_diffuse_color[3])
        result += 'fresnel color: %s %s %s %s\n' % (self.fresnel_color[0],
         self.fresnel_color[1],
         self.fresnel_color[2],
         self.fresnel_color[3])
        result += 'gloss: %s %s %s %s' % (self.gloss[0],
         self.gloss[1],
         self.gloss[2],
         self.gloss[3])
        return result


K_MIN_SCALE = 0.1
K_MAX_SCALE = 3.6

def ratio_to_scale(ratio, scaling_multiplier):
    return scaling_multiplier * (K_MIN_SCALE + ratio ** 2 * K_MAX_SCALE)


def scale_to_ratio(scale, scaling_multiplier):
    return math.sqrt(max(0, (scale / scaling_multiplier - K_MIN_SCALE) / K_MAX_SCALE))


default_scaling_ratio = 0.5

class BasePatternComponentInstance(BaseComponentInstance):
    PATTERN_CONFIGURATION_PROTO = None

    def __init__(self, component_id, scaling_multiplier = 1.0):
        super(BasePatternComponentInstance, self).__init__(component_id)
        component_data = self.get_component_data()
        self._projection_area1 = True
        self._projection_area2 = True
        self._projection_area3 = True
        self._projection_area4 = True
        self._projection_type_u = component_data.projection_type_uv[0] if component_data else 0
        self._projection_type_v = component_data.projection_type_uv[1] if component_data else 0
        self._position = [0, 0, 0]
        self._rotation = [0,
         0,
         0,
         0]
        self._ellipsoid_center = [0, 0, 0]
        self._ellipsoid_radii = [1.0, 1.0, 1.0]
        default_scaling_ratio = DEFAULT_SCALING_RATIO
        s = ratio_to_scale(default_scaling_ratio, scaling_multiplier)
        self._scaling = [s, s, s]
        self._scaling_ratio = default_scaling_ratio
        self._scaling_multiplier = scaling_multiplier
        self._offset_u_ratio = DEFAULT_OFFSET_RATIO
        self._offset_v_ratio = DEFAULT_OFFSET_RATIO
        self._yaw = DEFAULT_YAW
        self._pitch = DEFAULT_PITCH
        self._roll = DEFAULT_ROLL
        self._mirrored = DEFAULT_MIRRORED
        self.is_built_from_proto = False

    @property
    def projection_area1(self):
        return self._projection_area1

    @projection_area1.setter
    def projection_area1(self, value):
        self._projection_area1 = value
        self.on_attribute_changed(self, PatternAttribute.PROJECT_TO_AREA_1, value)

    @property
    def projection_area2(self):
        return self._projection_area2

    @projection_area2.setter
    def projection_area2(self, value):
        self._projection_area2 = value
        self.on_attribute_changed(self, PatternAttribute.PROJECT_TO_AREA_2, value)

    @property
    def projection_area3(self):
        return self._projection_area3

    @projection_area3.setter
    def projection_area3(self, value):
        self._projection_area3 = value
        self.on_attribute_changed(self, PatternAttribute.PROJECT_TO_AREA_3, value)

    @property
    def projection_area4(self):
        return self._projection_area4

    @projection_area4.setter
    def projection_area4(self, value):
        self._projection_area4 = value
        self.on_attribute_changed(self, PatternAttribute.PROJECT_TO_AREA_4, value)

    def get_projection_areas(self):
        return [self.projection_area1,
         self.projection_area2,
         self.projection_area3,
         self.projection_area4]

    @property
    def projection_type_u(self):
        return self._projection_type_u or 0

    @property
    def projection_type_v(self):
        return self._projection_type_v or 0

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = list(value)
        self.on_attribute_changed(self, PatternAttribute.POSITION, value)

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = list(value)
        self.on_attribute_changed(self, PatternAttribute.ROTATION, value)

    @property
    def ellipsoid_center(self):
        return self._ellipsoid_center

    @ellipsoid_center.setter
    def ellipsoid_center(self, value):
        self._ellipsoid_center = value

    @property
    def ellipsoid_radii(self):
        return self._ellipsoid_radii

    @ellipsoid_radii.setter
    def ellipsoid_radii(self, value):
        if 0 in value:
            raise ValueError('Zero value passed in as ellipsoid radius')
        self._ellipsoid_radii = value

    @property
    def offset_u_ratio(self):
        return self._offset_u_ratio

    @offset_u_ratio.setter
    def offset_u_ratio(self, value):
        value = max(-1.0, min(value, 1.0))
        self._offset_u_ratio = value
        self.apply_user_authored_values()
        self.on_attribute_changed(self, PatternAttribute.OFFSET_U_RATIO, value)

    @property
    def offset_v_ratio(self):
        return self._offset_v_ratio

    @offset_v_ratio.setter
    def offset_v_ratio(self, value):
        value = max(-1.0, min(value, 1.0))
        self._offset_v_ratio = value
        self.apply_user_authored_values()
        self.on_attribute_changed(self, PatternAttribute.OFFSET_V_RATIO, value)

    @property
    def yaw(self):
        return self._yaw

    @yaw.setter
    def yaw(self, value):
        if value >= 1.0:
            value -= 2.0
        elif value < -1.0:
            value += 2.0
        self._yaw = value
        self.apply_user_authored_values()
        self.on_attribute_changed(self, PatternAttribute.YAW_RATIO, value)

    @property
    def pitch(self):
        return self._pitch

    @pitch.setter
    def pitch(self, value):
        value = max(-0.999, min(value, 0.999))
        self._pitch = value
        self.apply_user_authored_values()
        self.on_attribute_changed(self, PatternAttribute.PITCH_RATIO, value)

    @property
    def roll(self):
        return self._roll

    @roll.setter
    def roll(self, value):
        if value > 1.0:
            value -= 2.0
        elif value < -1.0:
            value += 2.0
        self._roll = value
        self.apply_user_authored_values()
        self.on_attribute_changed(self, PatternAttribute.ROLL_RATIO, value)

    @property
    def scaling(self):
        return self._scaling

    @scaling.setter
    def scaling(self, value):
        self._scaling = list(value)
        self.on_attribute_changed(self, PatternAttribute.SCALE, value)

    @property
    def scaling_ratio(self):
        return scale_to_ratio(self.scaling[0], self.scaling_multiplier)

    @scaling_ratio.setter
    def scaling_ratio(self, value):
        value = max(0.0, min(value, 1.0))
        self._scaling_ratio = value
        scale = ratio_to_scale(value, self.scaling_multiplier)
        self.scaling = (scale, scale, scale)

    @property
    def scaling_multiplier(self):
        return self._scaling_multiplier

    @scaling_multiplier.setter
    def scaling_multiplier(self, value):
        self._scaling_multiplier = value
        self.scaling_ratio = self.scaling_ratio

    @property
    def mirrored(self):
        return self._mirrored

    @mirrored.setter
    def mirrored(self, value):
        self._mirrored = value
        self.on_attribute_changed(self, PatternAttribute.MIRROR, value)

    def reset_rotation_scale_and_offset(self):
        self.yaw = DEFAULT_YAW
        self.pitch = DEFAULT_PITCH
        self.roll = DEFAULT_ROLL
        self.offset_u_ratio = DEFAULT_OFFSET_RATIO
        self.offset_v_ratio = DEFAULT_OFFSET_RATIO
        self.scaling_ratio = DEFAULT_SCALING_RATIO

    def copy_params_from_other(self, other_component, should_copy_components_to_use = False):
        self._projection_area1 = other_component.projection_area1
        self._projection_area2 = other_component.projection_area2
        self._projection_area3 = other_component.projection_area3
        self._projection_area4 = other_component.projection_area4
        self._position = other_component._position
        self._rotation = other_component._rotation
        self._scaling = other_component._scaling
        self._mirrored = other_component.mirrored
        self._yaw = other_component.yaw
        self._pitch = other_component.pitch
        self._roll = other_component.roll
        self._offset_u_ratio = other_component.offset_u_ratio
        self._offset_v_ratio = other_component.offset_v_ratio
        self._ellipsoid_radii = other_component.ellipsoid_radii
        self._ellipsoid_center = other_component.ellipsoid_center
        self.is_built_from_proto = other_component.is_built_from_proto
        if not other_component.is_built_from_proto:
            self._apply_user_authored_values()
        super(BasePatternComponentInstance, self).copy_params_from_other(other_component, should_copy_components_to_use)

    def build_params_from_proto(self, payload):
        self._projection_area1 = payload.projection.area1
        self._projection_area2 = payload.projection.area2
        self._projection_area3 = payload.projection.area3
        self._projection_area4 = payload.projection.area4
        self._projection_type_u = payload.projection.projection_type_u
        self._projection_type_v = payload.projection.projection_type_v
        self._position = [payload.transform.position.x, payload.transform.position.y, payload.transform.position.z]
        self._rotation = [payload.transform.rotation.x,
         payload.transform.rotation.y,
         payload.transform.rotation.z,
         payload.transform.rotation.w]
        self._scaling = [payload.transform.scaling.x, payload.transform.scaling.y, payload.transform.scaling.z]
        self._mirrored = payload.mirrored
        self.is_built_from_proto = True

    def build_proto(self):
        config = self.PATTERN_CONFIGURATION_PROTO()
        config.projection.area1 = self._projection_area1
        config.projection.area2 = self._projection_area2
        config.projection.area3 = self._projection_area3
        config.projection.area4 = self._projection_area4
        config.projection.projection_type_u = self._projection_type_u
        config.projection.projection_type_v = self._projection_type_v
        config.transform.position.CopyFrom(self.VECTOR3_PROTO(x=self._position[0], y=self._position[1], z=self._position[2]))
        config.transform.rotation.CopyFrom(self.VECTOR4_PROTO(x=self._rotation[0], y=self._rotation[1], z=self._rotation[2], w=self._rotation[3]))
        config.transform.scaling.CopyFrom(self.VECTOR3_PROTO(x=self._scaling[0], y=self._scaling[1], z=self._scaling[2]))
        config.mirrored = self.mirrored
        return config

    def __eq__(self, other):
        if other is None:
            return False
        return self.component_id == other.component_id and self.position == other.position and self.rotation == other.rotation and self.scaling == other.scaling and self.projection_area1 == other.projection_area1 and self.projection_area2 == other.projection_area2 and self.projection_area3 == other.projection_area3 and self.projection_area4 == other.projection_area4 and self.projection_type_u == other.projection_type_u and self.projection_type_v == other.projection_type_v and self.mirrored == other.mirrored

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        result = ''
        result += 'component id: %s\n' % self.component_id
        result += 'params: \n'
        result += 'projection areas: %s %s %s %s\n' % (self.projection_area1,
         self.projection_area2,
         self.projection_area3,
         self.projection_area4)
        result += 'projection type u: %s v: %s\n' % (self.projection_type_u, self.projection_type_v)
        result += 'position: %s\n' % self.position
        result += 'rotation: %s\n' % self.rotation
        result += 'scaling: %s\n' % self.scaling
        result += 'mirrored: %s\n' % self.mirrored
        result += 'ellipsoid_radii: %s\n' % repr(self.ellipsoid_radii)
        result += 'ellipsoid_center: %s\n' % repr(self.ellipsoid_center)
        return result
