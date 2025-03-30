#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\goals\client\contributionMethods.py
import eveicon
import evetypes
import localization
from dogma.units import get_display_name
from goals.client.contributionMethodTypeLoader import get_contribution_method_authored_data
from goals.client.goalParameter import get_goal_parameter
from goals.common.errors import ContributionMethodTypeNotSupported
from goals.common.goalConst import ContributionMethodTypes
from localization import GetByMessageID, GetByLabel
from metadata.common.content_tags.const import CONTENT_TAG_TO_CAREER_PATH
_class_map = {}

def get_all_contribution_methods():
    return [ get_contribution_method(method_type) for method_type in _class_map.keys() ]


def get_contribution_method(method_id, data = None):
    if method_id not in _class_map:
        raise ContributionMethodTypeNotSupported(u'Method type {} not supported'.format(method_id))
    return _class_map.get(method_id)(data or {})


class _BaseContributionMethod(object):
    method_id = None
    __notifyevents__ = ['OnLanguageChanged']

    def __init__(self, parameter_values):
        self._title_id = None
        self._descriptionID = None
        self._icon = None
        self._unit = None
        self._param = None
        self._parameter_values = parameter_values
        self._load_authored_data()
        sm.RegisterNotify(self)

    def _load_authored_data(self):
        data = get_contribution_method_authored_data(self.method_id)
        if not data:
            return
        self._title_id = data.titleID
        self._descriptionID = data.descriptionID
        self._icon = data.icon
        self._target_value_description = data.targetValueDescriptionID if data.targetValueDescriptionID else None
        self._rewarding_description = data.rewardingDescriptionID if data.rewardingDescriptionID else None
        self._progress_description = data.progressDescriptionID if data.progressDescriptionID else None
        if data.unit:
            self._unit = get_display_name(data.unit)
        self._construct_parameters(data)
        self._content_tags = [ t for t in data.contentTags or [] ]

    def _construct_parameters(self, data):
        self._param = {param.parameterKey:get_goal_parameter(param, getattr(self, param.parameterKey)) for param in data.parameters}

    @property
    def title_id(self):
        return self._title_id

    @property
    def title(self):
        return localization.GetByMessageID(self._title_id)

    @property
    def info(self):
        return localization.GetByMessageID(self._descriptionID)

    @property
    def target_value_description(self):
        if self._target_value_description:
            return GetByMessageID(self._target_value_description)
        else:
            return GetByLabel('UI/Corporations/Goals/TargetValue')

    @property
    def rewarding_description(self):
        if self._rewarding_description:
            return GetByMessageID(self._rewarding_description)
        else:
            return GetByLabel('UI/Corporations/Goals/ISKPerUnitOfProgress')

    @property
    def progress_description(self):
        if self._progress_description:
            return GetByMessageID(self._progress_description)
        return ''

    @property
    def full_description(self):
        return self.title

    @property
    def icon(self):
        if self._icon:
            return eveicon.get(self._icon)

    @property
    def unit(self):
        return self._unit

    @property
    def parameters(self):
        return self._param.values()

    def keys(self):
        return self.__dict__.keys()

    @property
    def content_tags(self):
        return self._content_tags

    @property
    def career_path(self):
        if self.content_tags:
            return CONTENT_TAG_TO_CAREER_PATH.get(self.content_tags[0], None)

    @property
    def solar_system(self):
        return None

    @property
    def location(self):
        return self.solar_system

    def get_parameter(self, key):
        if key in self._param.keys():
            return self._param[key]

    def OnLanguageChanged(self, _language_id):
        self._load_authored_data()


class _ShipContributionMethod(_BaseContributionMethod):
    method_id = None

    @property
    def solar_system(self):
        return self._parameter_values.get('solar_system', None)

    @property
    def ship(self):
        return self._parameter_values.get('ship', None)

    @property
    def organization(self):
        return self._parameter_values.get('organization', None)


class Manual(_BaseContributionMethod):
    method_id = ContributionMethodTypes.MANUAL


class DamageShip(_ShipContributionMethod):
    method_id = ContributionMethodTypes.DAMAGE_SHIP


class DeliverItem(_BaseContributionMethod):
    method_id = ContributionMethodTypes.DELIVER_ITEM

    @property
    def item_type(self):
        return self._parameter_values.get('item_type', None)

    @property
    def office(self):
        return self._parameter_values.get('office', None)

    @property
    def solar_system(self):
        office = sm.GetService('officeManager').GetMyCorporationsOffice(self.office)
        if office:
            return office.solarsystemID

    @property
    def location(self):
        office = sm.GetService('officeManager').GetMyCorporationsOffice(self.office)
        if office:
            return office.stationID

    @property
    def full_description(self):
        return u'{} ({})'.format(self.title, evetypes.GetName(self.item_type))


class KillNPC(_BaseContributionMethod):
    method_id = ContributionMethodTypes.KILL_NPC

    @property
    def solar_system(self):
        return self._parameter_values.get('solar_system', None)


class MineOre(_BaseContributionMethod):
    method_id = ContributionMethodTypes.MINE_ORE

    @property
    def solar_system(self):
        return self._parameter_values.get('solar_system', None)

    @property
    def ore(self):
        return self._parameter_values.get('ore', None)


class HarvestGas(_BaseContributionMethod):
    method_id = ContributionMethodTypes.HARVEST_GAS

    @property
    def solar_system(self):
        return self._parameter_values.get('solar_system', None)

    @property
    def ore_type(self):
        return self._parameter_values.get('ore_type', None)


class ManufactureItem(_BaseContributionMethod):
    method_id = ContributionMethodTypes.MANUFACTURE_ITEM

    @property
    def item_type(self):
        return self._parameter_values.get('item_type', None)

    @property
    def facility_location(self):
        return self._parameter_values.get('facility_location', None)

    @property
    def owner(self):
        return self._parameter_values.get('owner', None)

    @property
    def full_description(self):
        return u'{} ({})'.format(self.title, evetypes.GetName(self.item_type))


class DestroyPlayerShip(_ShipContributionMethod):
    method_id = ContributionMethodTypes.DESTROY_PLAYER_SHIP


class DefendFacWarComplex(_BaseContributionMethod):
    method_id = ContributionMethodTypes.DEFEND_FACWAR_COMPLEX

    @property
    def solar_system(self):
        return self._parameter_values.get('solar_system', None)

    @property
    def faction(self):
        return self._parameter_values.get('faction', None)

    @property
    def complex_type(self):
        return self._parameter_values.get('complex_type', None)


class CaptureFacWarComplex(_BaseContributionMethod):
    method_id = ContributionMethodTypes.CAPTURE_FACWAR_COMPLEX

    @property
    def solar_system(self):
        return self._parameter_values.get('solar_system', None)

    @property
    def faction(self):
        return self._parameter_values.get('faction', None)

    @property
    def complex_type(self):
        return self._parameter_values.get('complex_type', None)


class RemoteRepairArmor(_ShipContributionMethod):
    method_id = ContributionMethodTypes.REMOTE_REPAIR_ARMOR


class RemoteRepairShield(_ShipContributionMethod):
    method_id = ContributionMethodTypes.REMOTE_REPAIR_SHIELD


class WarpScramble(_ShipContributionMethod):
    method_id = ContributionMethodTypes.WARP_SCRAMBLE


class ShipLostPVP(_ShipContributionMethod):
    method_id = ContributionMethodTypes.SHIP_LOSS


class ScanSignature(_BaseContributionMethod):
    method_id = ContributionMethodTypes.SCAN_SIGNATURE

    @property
    def signature_type(self):
        return self._parameter_values.get('signature_type', None)

    @property
    def solar_system(self):
        return self._parameter_values.get('solar_system', None)


class SalvageWreck(_BaseContributionMethod):
    method_id = ContributionMethodTypes.SALVAGE_WRECK

    @property
    def solar_system(self):
        return self._parameter_values.get('solar_system', None)


class EarnLoyaltyPoints(_BaseContributionMethod):
    method_id = ContributionMethodTypes.EARN_LOYALTY_POINTS

    @property
    def corporation_id(self):
        return self._parameter_values.get('corporation_id', None)


class EarnEverMarks(_BaseContributionMethod):
    method_id = ContributionMethodTypes.EARN_EVER_MARKS


class CompleteGoal(_BaseContributionMethod):
    method_id = ContributionMethodTypes.COMPLETE_GOAL

    @property
    def goal_id(self):
        return self._parameter_values.get('daily_goal', None)


class HackContainer(_BaseContributionMethod):
    method_id = ContributionMethodTypes.HACK_CONTAINER

    @property
    def hacking_container_type(self):
        return self._parameter_values.get('hacking_container_type', None)

    @property
    def solar_system(self):
        return self._parameter_values.get('solar_system', None)


class ShipInsurance(_ShipContributionMethod):
    method_id = ContributionMethodTypes.SHIP_INSURANCE

    @property
    def conflict_type(self):
        return self._parameter_values.get('conflict_type', None)

    @property
    def cover_implants(self):
        return self._parameter_values.get('cover_implants', True)


class SpaceJump(_BaseContributionMethod):
    method_id = ContributionMethodTypes.SPACE_JUMP


def _map_classes(local_scope):
    for name, value in local_scope.items():
        if '__' in name:
            continue
        if isinstance(value, type) and issubclass(value, _BaseContributionMethod) and value.method_id is not None:
            _class_map[value.method_id] = value


_map_classes(locals())
