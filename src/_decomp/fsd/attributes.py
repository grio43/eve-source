#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsd\attributes.py
NO_DEFAULT = 'NO_DEFAULT_VALUE'

class DataAttribute(object):

    def __init__(self, is_optional = False, index = 999999, default = NO_DEFAULT, field_kwargs = None, description = None, **kwargs):
        self.is_optional = is_optional
        self.index = index
        self.default = default
        self.field_kwargs = field_kwargs or {}
        if description:
            self.field_kwargs['description'] = description

    def convert_fsd_to_attribute(self, value):
        return value

    def convert_attribute_to_fsd(self, value):
        return value

    def get_default_as_fsd(self):
        return self.convert_attribute_to_fsd(self.default)


class BooleanAttribute(DataAttribute):
    pass


class FloatAttribute(DataAttribute):
    pass


class IntegerAttribute(DataAttribute):
    pass


class StringAttribute(DataAttribute):
    pass


class DictionaryAttribute(DataAttribute):
    pass


class BlackboardAddressAttribute(DataAttribute):

    def convert_fsd_to_attribute(self, value):
        return (value['scopeType'], value['messageName'])

    def convert_attribute_to_fsd(self, value):
        return {'scopeType': value[0],
         'messageName': value[1]}


class DogmaAttributeAttribute(DataAttribute):
    pass


class DogmaEffectIdAttribute(DataAttribute):
    pass


class DogmaEffectIdSetAttribute(DataAttribute):
    pass


class DungeonSelectAttribute(DataAttribute):
    pass


class DungeonArchetypeListAttribute(DataAttribute):
    pass


class DungeonListAttribute(DataAttribute):
    pass


class GraphicEffectNameAttribute(DataAttribute):
    pass


class InventoryTypeAttribute(DataAttribute):
    pass


class InventoryCategorySetAttribute(DataAttribute):
    pass


class InventoryGroupAttribute(DataAttribute):
    pass


class InventoryGroupSetAttribute(DataAttribute):
    pass


class InventoryTypeSetAttribute(DataAttribute):
    pass


class InventoryTypeSelectAttribute(DataAttribute):
    pass


class OwnerIdAttribute(DataAttribute):
    pass


class OwnerIdSetAddressAttribute(DataAttribute):
    pass


class OwnerListAttribute(DataAttribute):
    pass


class TargetEvaluatorAttribute(DataAttribute):
    pass


class EntitiesAndQuantitiesAttribute(DataAttribute):
    pass


class Vector3dAttributes(DataAttribute):
    pass


class StringToLiteralDictionaryAttribute(DataAttribute):
    pass


class OwnerIdToSpawnlistIdDictionaryAttribute(DataAttribute):

    def convert_fsd_to_attribute(self, value):
        return {int(k):v for k, v in value.iteritems()}


class StringSetAttribute(DataAttribute):
    pass


class CombatRoleAttribute(DataAttribute):
    pass


class CombatRoleSetAttribute(DataAttribute):
    pass


class StandingsClassAttribute(DataAttribute):
    pass


class BehaviorTreeAttribute(DataAttribute):
    pass


class BehaviorItemTreeAttribute(DataAttribute):
    pass


class BehaviorGroupTreeAttribute(DataAttribute):
    pass


class SubtreeParametersAttribute(DataAttribute):
    pass


class BlackboardAddressListAttribute(DataAttribute):

    def convert_fsd_to_attribute(self, value):
        return [ (address['scopeType'], address['messageName']) for address in value ]


class NpcSpawnTableIdAttribute(DataAttribute):
    pass


class EveTypeListSelectAttribute(DataAttribute):
    pass


class BlackboardAddressByFleetTypeAttribute(DataAttribute):

    def convert_fsd_to_attribute(self, value):
        return {int(key):(address['scopeType'], address['messageName']) for key, address in value.iteritems()}


class FleetTypeAttribute(DataAttribute):

    def convert_fsd_to_attribute(self, value):
        return int(value)


class NpcTagListAttribute(DataAttribute):
    pass


class TargetEvaluatorSetAttribute(DataAttribute):
    pass


class ItemIdSetByFleetTypeAttribute(DataAttribute):

    def convert_fsd_to_attribute(self, value):
        return {int(key):(address['scopeType'], address['messageName']) for key, address in value.iteritems()}


class FloatListAttribute(DataAttribute):
    pass


class MessageSelectAttribute(DataAttribute):
    pass


class DungeonTriggerSelectAttribute(DataAttribute):
    pass


class DungeonTriggerEventSelectAttribute(DataAttribute):
    pass


class NpcRewardSelectAttribute(DataAttribute):
    pass


class OwnerIdToSpawnTableIdDictionaryAttribute(DataAttribute):

    def convert_fsd_to_attribute(self, value):
        return {int(k):int(v) for k, v in value.iteritems()}


class NpcCorporationSelectAttribute(DataAttribute):
    pass


class NpcFleetCounterAttribute(DataAttribute):
    pass


class RegionSpawnListSelectAttribute(DataAttribute):
    pass


class SolarSystemSpawnListSelectAttribute(DataAttribute):
    pass


class DungeonSpawnListSelectAttribute(DataAttribute):
    pass


class EntitySpawnListSelectAttribute(DataAttribute):
    pass


class GroupSpawnListSelectAttribute(DataAttribute):
    pass


class TaleDistributionSpawnListSelectAttribute(DataAttribute):
    pass


class SceneTypeSelectAttribute(DataAttribute):
    pass


class DirectorCommandSelectAttribute(DataAttribute):
    pass


class LootTableSelectAttribute(DataAttribute):
    pass


class LocalizationIDAttribute(DataAttribute):
    pass


class IntegerListAttribute(DataAttribute):
    pass


class TaleTemplateSelectAttribute(DataAttribute):
    pass


class FloatIntegerAttribute(DataAttribute):
    pass


class DungeonSpawnLocationAttribute(DataAttribute):
    pass


class DungeonScanStrengthAttribute(DataAttribute):
    pass


class TriggeredSceneAttribute(DataAttribute):
    pass


class TriggeredSceneLocationAttribute(DataAttribute):
    pass


class DummyParameterAttribute(DataAttribute):
    pass


class SystemInfluenceTriggerDirectionAttribute(DataAttribute):
    pass


class SolarSystemSelectAttribute(DataAttribute):
    pass


class NpcFactionSpawnListSelectAttribute(DataAttribute):
    pass


class VisualEffectAttribute(DataAttribute):
    pass


class OperationSiteAttribute(DataAttribute):
    pass


class BlackboardScopeTypeAttribute(DataAttribute):
    pass


class FleetFormationTypeAttribute(DataAttribute):
    pass


class FwAttackMethodAttribute(DataAttribute):
    pass
