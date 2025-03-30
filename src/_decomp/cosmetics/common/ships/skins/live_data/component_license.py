#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\live_data\component_license.py
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from cosmetics.common.ships.skins.static_data.component import ComponentsDataLoader
from cosmetics.common.ships.skins.static_data.component_category import ComponentCategory

class BaseComponentLicense(object):
    LICENSE_KIND_PROTO = None
    COMPONENT_IDENTIFIER_PROTO = None
    COATING_IDENTIFIER_PROTO = None
    PATTERN_IDENTIFIER_PROTO = None

    def __init__(self, owner_character_id, component_id, license_type, remaining_license_uses = None):
        self._owner_character_id = owner_character_id
        self._component_id = component_id
        self._license_type = license_type
        self._remaining_license_uses = remaining_license_uses

    @property
    def owner_character_id(self):
        return self._owner_character_id

    @property
    def component_id(self):
        return self._component_id

    @property
    def license_type(self):
        return self._license_type

    @property
    def name(self):
        return self.get_component_data().name

    @property
    def remaining_license_uses(self):
        if self.license_type == ComponentLicenseType.LIMITED:
            return self._remaining_license_uses

    def set_remaining_license_uses(self, remaining_license_uses):
        self._remaining_license_uses = remaining_license_uses

    def has_enough_remaining_uses(self, num_runs):
        if self.license_type == ComponentLicenseType.UNLIMITED:
            return True
        return self.remaining_license_uses >= num_runs

    def get_required_sequence_binders(self):
        if self.license_type == ComponentLicenseType.LIMITED:
            return
        component_data = self.get_component_data()
        if component_data is not None:
            return (component_data.sequence_binder_type_id, component_data.sequence_binder_required_amount)

    def get_component_data(self):
        return ComponentsDataLoader.get_component_data(self.component_id)

    @classmethod
    def build_from_proto(cls, character_id, payload):
        component_id = cls.get_component_id_from_proto(payload.component)
        license_type = ComponentLicenseType.UNLIMITED if payload.HasField('infinite') else ComponentLicenseType.LIMITED
        remaining_license_uses = int(payload.finite) if payload.HasField('finite') else None
        return cls(character_id, component_id, license_type, remaining_license_uses)

    @classmethod
    def build_from_finite_proto(cls, character_id, component_id, payload):
        license_type = ComponentLicenseType.LIMITED
        remaining_license_uses = payload.capacity
        return cls(character_id, component_id, license_type, remaining_license_uses)

    @classmethod
    def build_from_infinite_proto(cls, character_id, component_id, _payload):
        license_type = ComponentLicenseType.UNLIMITED
        return cls(character_id, component_id, license_type, None)

    @classmethod
    def build_proto_from_component_license(cls, component_license):
        component_data = component_license.get_component_data()
        license_kind = cls.LICENSE_KIND_PROTO()
        license_kind.component.CopyFrom(cls.build_component_id_proto_from_component_id(component_license.component_id, component_data.category))
        if component_license.license_type == ComponentLicenseType.LIMITED:
            license_kind.finite = component_license.remaining_license_uses
        else:
            license_kind.infinite = True
        return license_kind

    @classmethod
    def build_component_id_proto_from_component_id(cls, component_id, component_type):
        component_proto = cls.COMPONENT_IDENTIFIER_PROTO()
        if component_type in [ComponentCategory.METALLIC, ComponentCategory.MATERIAL]:
            component_proto.coating.CopyFrom(cls.COATING_IDENTIFIER_PROTO(sequential=component_id))
        elif component_type in [ComponentCategory.PATTERN]:
            component_proto.pattern.CopyFrom(cls.PATTERN_IDENTIFIER_PROTO(sequential=component_id))
        else:
            raise NotImplementedError('Unknown component type for component id: {component_id}'.format(component_id=component_id))
        return component_proto

    @classmethod
    def get_component_id_from_proto(cls, payload):
        if payload.HasField('coating'):
            return payload.coating.sequential
        if payload.HasField('pattern'):
            return payload.pattern.sequential
        raise NotImplementedError('Unknown component type in component proto: {payload}'.format(payload=payload))

    def __eq__(self, other):
        if other is None:
            return False
        return self.owner_character_id == other.owner_character_id and self.component_id == other.component_id and self.license_type == other.license_type and self.remaining_license_uses == other.remaining_license_uses

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        result = '%s Component License for component %s' % (self.license_type, self.component_id)
        if self.license_type == ComponentLicenseType.LIMITED:
            result += ' (remaining uses: %s)' % self.remaining_license_uses
        return result
