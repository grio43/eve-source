#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\goals\client\goalParameter.py
import abc
import eveicon
import evetypes
import eveui
import localization
from carbonui import TextColor, Align, uiconst
from carbonui.control.comboEntryData import ComboEntryData
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.dragdrop import dragdata
from carbonui.control.forms import formValidators, formComponent
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.shared.maps.solarSystemMapIcon import SolarSystemMapIcon, ConstellationMapIcon, RegionMapIcon
from eve.client.script.ui.shared.neocom.corporation.corp_goals.forms.goalFormComponents import MultiValueLocationFormComponent, MultiValueItemFormComponent, MultiValueNpcCorpFormComponent, MultiValuePlayerCorpOrOrgFormComponent, MultiValueShipAndShipTreeFormComponent, MultiValueEnumComponent
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from eveformat.client import solar_system_with_security
from goals.common.goalConst import GoalParameterTypes, ON_BEHALF_OF_CORP, ON_BEHALF_OF_SELF, ON_BEHALF_OF_LABELS
from localization import GetByLabel, GetByMessageID
from npcs.npccorporations import get_corporation_lp_offer_tables, get_corporation_exchange_rates
from shipgroup import get_ship_tree_group_name, get_ship_tree_group_icon
_class_map = {}

def get_goal_parameter(parameter, value):
    parameter_class = _class_map[parameter.parameterType]
    return parameter_class(parameter, value)


class _BaseGoalParameter(object):
    __metaclass__ = abc.ABCMeta
    parameter_id = None
    form_component_class = None
    form_component_class_multiple = None
    entry_height = 48

    def __init__(self, data, value = None):
        self._key = data.parameterKey
        self._title = data.title
        self._icon = data.icon
        self._info = data.info
        self._type = data.parameterType
        self._is_required = data.isRequired
        self._max_entries = data.maxEntries
        self._sort_values(value)
        self._value = value
        self._values = value

    @property
    def title(self):
        return localization.GetByLabel(self._title)

    @property
    def icon(self):
        if self._icon is None:
            return
        return eveicon.get(self._icon, self._icon)

    @property
    def info(self):
        if self._info:
            return localization.GetByLabel(self._info)
        return ''

    @property
    def key(self):
        return self._key

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._value

    @property
    def values(self):
        return self._values

    @property
    def is_required(self):
        return self._is_required

    @property
    def max_entries(self):
        return self._max_entries

    def get_value_text(self):
        if self.value is None:
            return self.get_none_value_text()
        else:
            return self.get_entry_title(self.value)

    def get_none_value_text(self):
        return GetByLabel('UI/Common/Any')

    def get_menu(self):
        return self.get_entry_menu(self.value)

    def get_entry_title(self, value):
        return repr(value)

    def get_entry_subtitle(self, value):
        return ''

    def get_entry_menu(self, value):
        return None

    def get_none_entry_menu(self):
        return None

    def get_entry_drag_data(self, value):
        return None

    def get_entry_height(self):
        return self.entry_height

    def construct_entry_icon(self, value):
        return None

    def get_form_component(self):
        kwargs = self._get_form_component_values()
        if self._should_render_multi_select():
            return self.form_component_class_multiple(**kwargs)
        return self.form_component_class(**kwargs)

    def _get_form_component_values(self):
        is_multivalue = self._should_render_multi_select()
        value = self.value
        values = {'name': self.key,
         'label': self.title,
         'icon': self.icon,
         'hint': self.info,
         'value': value,
         'validators': [formValidators.InputRequired()] if self.is_required else None}
        if self.form_component_class not in [formComponent.Enum, formComponent.Boolean]:
            values['placeholder'] = _get_text_field_placeholder(self.is_required)
        if is_multivalue:
            values['max_entries'] = self.max_entries
        return values

    def _should_render_multi_select(self):
        return self.max_entries is not None and self.max_entries > 1

    def _sort_values(self, values):
        if not isinstance(values, list):
            return
        values.sort(key=lambda value: self._sort_key(value))

    def _sort_key(self, value):
        return value


class _LocationGoalParameter(_BaseGoalParameter):
    form_component_class = formComponent.SolarSystem
    form_component_class_multiple = MultiValueLocationFormComponent

    def get_entry_title(self, value):
        if idCheckers.IsSolarSystem(value):
            return solar_system_with_security(value)
        return cfg.evelocations.Get(value).locationName

    def get_entry_subtitle(self, value):
        if idCheckers.IsSolarSystem(value):
            return localization.GetByLabel('UI/Common/LocationTypes/SolarSystem')
        if idCheckers.IsConstellation(value):
            return localization.GetByLabel('UI/Common/LocationTypes/Constellation')
        if idCheckers.IsRegion(value):
            return localization.GetByLabel('UI/Common/LocationTypes/Region')
        return ''

    def get_entry_menu(self, value):
        return sm.GetService('menu').CelestialMenu(value)

    def get_entry_drag_data(self, value):
        return eveui.dragdata.Location(value)

    def construct_entry_icon(self, value):
        map_icon = None
        type_id = None
        if idCheckers.IsSolarSystem(value):
            map_icon = SolarSystemMapIcon(width=32, height=32, align=Align.CENTER, state=uiconst.UI_NORMAL)
            map_icon.Draw(value, 32)
            type_id = appConst.typeSolarSystem
        elif idCheckers.IsConstellation(value):
            map_icon = ConstellationMapIcon(value, size=32, state=uiconst.UI_NORMAL, align=Align.CENTER, lineColors=[(0.2, 0.75, 0.2, 1), (0.2, 0.2, 0.75, 1), (0.75, 0.2, 0.2, 1)], dotColor=(0.7, 0.7, 0.7), dotSizeMultiplier=0.7)
            type_id = appConst.typeConstellation
        elif idCheckers.IsRegion(value):
            map_icon = RegionMapIcon(value, size=32, state=uiconst.UI_NORMAL, align=Align.CENTER, lineColors=[(0.2, 0.75, 0.2, 1), (0.2, 0.2, 0.75, 1), (0.75, 0.2, 0.2, 1)], dotColor=(0.7, 0.7, 0.7))
            type_id = appConst.typeRegion
        if map_icon:
            map_icon.OnClick = lambda *args, **kwargs: self._show_info(value, type_id)
            return map_icon

    def _show_info(self, location_id, type_id):
        sm.GetService('info').ShowInfo(itemID=location_id, typeID=type_id)

    def _sort_key(self, value):
        if idCheckers.IsSolarSystem(value):
            priority = 1
        elif idCheckers.IsConstellation(value):
            priority = 2
        elif idCheckers.IsRegion(value):
            priority = 3
        else:
            priority = 4
        return (priority, cfg.evelocations.Get(value).locationName.lower())


class _EveOwnerGoalParameter(_BaseGoalParameter):
    parameter_id = None

    def get_entry_title(self, value):
        return cfg.eveowners.Get(value).name

    def get_entry_subtitle(self, value):
        if idCheckers.IsEvePlayerCharacter(value):
            return localization.GetByLabel('UI/Common/Capsuleer')
        if idCheckers.IsCharacter(value):
            return localization.GetByLabel('UI/Common/Character')
        if idCheckers.IsCorporation(value):
            return localization.GetByLabel('UI/Common/Corporation')
        if idCheckers.IsAlliance(value):
            return localization.GetByLabel('UI/Common/Alliance')
        if idCheckers.IsFaction(value):
            return localization.GetByLabel('UI/Common/Faction')
        return ''

    def get_entry_menu(self, value):
        return sm.GetService('menu').GetMenuForOwner(int(value))

    def get_entry_drag_data(self, value):
        return eveui.dragdata.Character(value)

    def construct_entry_icon(self, value):
        return OwnerIcon(ownerID=value, size=32, width=32, height=32)

    def _sort_key(self, value):
        if idCheckers.IsCharacter(value):
            priority = 1
        elif idCheckers.IsCorporation(value):
            priority = 2
        elif idCheckers.IsAlliance(value):
            priority = 3
        elif idCheckers.IsFaction(value):
            priority = 4
        else:
            priority = 5
        return (priority, self.get_entry_title(value).lower())


class EveTypeGoalParameter(_BaseGoalParameter):
    parameter_id = GoalParameterTypes.EVE_TYPE
    form_component_class = formComponent.EveType
    form_component_class_multiple = MultiValueItemFormComponent

    def get_entry_title(self, value):
        if not isinstance(value, tuple):
            return evetypes.GetName(value)
        entry_type, entry_id = value
        if entry_type == 'item_type':
            return evetypes.GetName(entry_id)
        if entry_type == 'item_group':
            return evetypes.GetGroupNameByGroup(entry_id)
        if entry_type == 'item_category':
            return evetypes.GetCategoryNameByCategory(entry_id)
        return ''

    def get_entry_subtitle(self, value):
        if not isinstance(value, tuple):
            return localization.GetByLabel('UI/Common/Type')
        entry_type, entry_id = value
        if entry_type == 'item_type':
            return localization.GetByLabel('UI/Common/Type')
        if entry_type == 'item_group':
            return localization.GetByLabel('UI/Common/Group')
        if entry_type == 'item_category':
            return localization.GetByLabel('UI/Common/Category')
        return ''

    def get_entry_menu(self, value):
        type_id = self._get_type_id(value)
        if type_id:
            return sm.GetService('menu').GetMenuFromItemIDTypeID(None, type_id, includeMarketDetails=True)

    def get_entry_drag_data(self, value):
        type_id = self._get_type_id(value)
        if type_id:
            return dragdata.TypeDragData(type_id)

    def construct_entry_icon(self, value):
        type_id = self._get_type_id(value)
        if type_id:
            return ItemIcon(width=32, height=32, typeID=type_id, showOmegaOverlay=False)

    def _get_type_id(self, value):
        if isinstance(value, tuple):
            entry_type, entry_id = value
            if entry_type == 'item_type':
                return entry_id
            else:
                return None
        else:
            return value

    def _sort_key(self, value):
        entry_type, entry_id = value
        if entry_type == 'item_type':
            priority = 1
            name = evetypes.GetName(entry_id)
        elif entry_type == 'item_group':
            priority = 2
            name = evetypes.GetGroupNameByGroup(entry_id)
        elif entry_type == 'item_category':
            priority = 3
            name = evetypes.GetCategoryNameByCategory(entry_id)
        else:
            priority = 4
            name = entry_id
        return (priority, name.lower())


class ShipTypeGoalParameter(_BaseGoalParameter):
    parameter_id = GoalParameterTypes.SHIP_TYPE
    form_component_class = formComponent.EveType
    form_component_class_multiple = MultiValueShipAndShipTreeFormComponent

    def _get_form_component_values(self):
        values = super(ShipTypeGoalParameter, self)._get_form_component_values()
        if self._should_render_multi_select():
            return values
        values['type_filter'] = lambda type_id: evetypes.GetCategoryID(type_id) == appConst.categoryShip
        return values

    def get_entry_title(self, value):
        if not isinstance(value, tuple):
            return evetypes.GetName(value)
        entry_type, entry_id = value
        if entry_type == 'ship_type':
            return evetypes.GetName(entry_id)
        if entry_type == 'ship_class':
            return get_ship_tree_group_name(entry_id)
        return ''

    def get_entry_subtitle(self, value):
        if not isinstance(value, tuple):
            return localization.GetByLabel('UI/Common/ShipType')
        entry_type, entry_id = value
        if entry_type == 'ship_type':
            return localization.GetByLabel('UI/Common/ShipType')
        if entry_type == 'ship_class':
            return localization.GetByLabel('UI/Common/ShipClass')
        return ''

    def get_entry_menu(self, value):
        type_id = self._get_type_id(value)
        if type_id:
            return sm.GetService('menu').GetMenuFromItemIDTypeID(None, type_id, includeMarketDetails=True)

    def get_entry_drag_data(self, value):
        type_id = self._get_type_id(value)
        if type_id:
            return dragdata.TypeDragData(type_id)

    def construct_entry_icon(self, value):
        type_id = self._get_type_id(value)
        if type_id:
            return ItemIcon(width=32, height=32, typeID=type_id, showOmegaOverlay=False)
        entry_type, entry_id = value
        if entry_type == 'ship_class':
            try:
                class_icon = get_ship_tree_group_icon(entry_id)
                return _render_basic_icon(class_icon, size=24, color=TextColor.SECONDARY)
            except:
                pass

    def _get_type_id(self, value):
        if isinstance(value, tuple):
            entry_type, entry_id = value
            if entry_type == 'ship_type':
                return entry_id
            else:
                return None
        else:
            return value

    def _sort_key(self, value):
        entry_type, entry_id = value
        if entry_type == 'ship_type':
            priority = 1
            name = evetypes.GetName(entry_id)
        elif entry_type == 'ship_class':
            priority = 2
            name = get_ship_tree_group_name(entry_id)
        else:
            priority = 3
            name = entry_id
        return (priority, name.lower())


class InsuranceShipTypeGoalParameter(ShipTypeGoalParameter):
    parameter_id = GoalParameterTypes.INSURANCE_SHIP_TYPE
    form_component_class = formComponent.EveType
    form_component_class_multiple = MultiValueShipAndShipTreeFormComponent

    def __init__(self, data, value = None):
        super(InsuranceShipTypeGoalParameter, self).__init__(data, value)
        self.includes_implants = None

    def get_none_value_text(self):
        if self.includes_implants is None:
            return GetByLabel('UI/Common/Any')
        if self.includes_implants:
            return GetByLabel('UI/Corporations/Goals/SRPAnyWithCapsules')
        return GetByLabel('UI/Corporations/Goals/SRPAnyWithoutCapsules')

    def set_includes_capsules(self, value):
        self.includes_implants = value


class MineableOreGoalParameter(EveTypeGoalParameter):
    parameter_id = GoalParameterTypes.MINEABLE_ORE_TYPE

    def _get_form_component_values(self):
        values = super(MineableOreGoalParameter, self)._get_form_component_values()
        allowed_type_ids = evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_ALL_MINABLE_TYPES)
        values['type_filter'] = lambda type_id: type_id in allowed_type_ids
        if not self._should_render_multi_select():
            return values
        allowed_group_ids = {evetypes.GetGroupID(type_id) for type_id in allowed_type_ids}
        values['group_filter'] = lambda group_id: group_id in allowed_group_ids
        values['include_group'] = True
        values['include_category'] = False
        return values


class ManufacturableItemGoalParameter(EveTypeGoalParameter):
    parameter_id = GoalParameterTypes.MANUFACTURABLE_ITEM_TYPE

    def _get_form_component_values(self):
        from industry.ManufacturableItemsLoader import is_manufacturable_item
        values = super(ManufacturableItemGoalParameter, self)._get_form_component_values()
        values['type_filter'] = lambda type_id: is_manufacturable_item(type_id)
        if not self._should_render_multi_select():
            return values
        values['include_group'] = False
        values['include_category'] = False
        return values


class HarvestableGasGoalParameter(EveTypeGoalParameter):
    parameter_id = GoalParameterTypes.HARVESTABLE_GAS_TYPE

    def _get_form_component_values(self):
        values = super(HarvestableGasGoalParameter, self)._get_form_component_values()
        values['type_filter'] = lambda type_id: evetypes.GetGroupID(type_id) == appConst.groupHarvestableCloud
        if not self._should_render_multi_select():
            return values
        values['include_group'] = False
        values['include_category'] = False
        return values


class SolarSystemGoalParameter(_LocationGoalParameter):
    parameter_id = GoalParameterTypes.SOLAR_SYSTEM


class NpcFactionGoalParameter(_EveOwnerGoalParameter):
    parameter_id = GoalParameterTypes.NPC_FACTION
    form_component_class = formComponent.Enum
    form_component_class_multiple = MultiValueEnumComponent

    def _get_form_component_values(self):
        values = super(NpcFactionGoalParameter, self)._get_form_component_values()
        values['options'] = self._get_options()
        return values

    def _get_options(self):
        from characterdata.factions import get_factions, get_faction
        from eve.common.script.util.facwarCommon import IsOccupierFWFaction
        FW_FACTION_ICONS = {appConst.factionAmarrEmpire: eveicon.amarr_logo,
         appConst.factionGallenteFederation: eveicon.gallente_logo,
         appConst.factionCaldariState: eveicon.caldari_logo,
         appConst.factionMinmatarRepublic: eveicon.minmatar_logo}
        options = [ ComboEntryData(GetByMessageID(get_faction(factionId).nameID), factionId, icon=FW_FACTION_ICONS[factionId], iconColor=TextColor.SECONDARY) for factionId in get_factions() if IsOccupierFWFaction(factionId) ]
        if not self.is_required and not self._should_render_multi_select():
            options.insert(0, ComboEntryData(GetByLabel('UI/Common/Any'), None, icon=eveicon.flag, iconColor=TextColor.SECONDARY))
        return options


class NpcCorporationGoalParameter(_EveOwnerGoalParameter):
    parameter_id = GoalParameterTypes.NPC_CORPORATION
    form_component_class = formComponent.NPCCorporation
    form_component_class_multiple = MultiValueNpcCorpFormComponent

    def get_entry_title(self, value):
        from npcs.npccorporations import get_npc_corporation_name
        return get_npc_corporation_name(value)


class LpNpcCorporationGoalParameter(NpcCorporationGoalParameter):
    parameter_id = GoalParameterTypes.LP_NPC_CORPORATION

    def _get_form_component_values(self):
        values = super(NpcCorporationGoalParameter, self)._get_form_component_values()

        def is_valid(corp_id):
            if corp_id == appConst.corpHeraldry:
                return False
            if bool(get_corporation_lp_offer_tables(corp_id)):
                return True
            if bool(get_corporation_exchange_rates(corp_id)):
                return True
            return False

        values['filter'] = is_valid
        return values


class OwnerIdentityGoalParameter(_EveOwnerGoalParameter):
    parameter_id = GoalParameterTypes.OWNER_IDENTITY
    form_component_class = formComponent.PlayerOrPlayerOrganization
    form_component_class_multiple = MultiValuePlayerCorpOrOrgFormComponent


class CorpOfficeGoalParameter(_BaseGoalParameter):
    parameter_id = GoalParameterTypes.CORP_OFFICE
    form_component_class = formComponent.Enum
    form_component_class_multiple = MultiValueEnumComponent
    entry_height = 32

    def get_entry_title(self, value):
        station_id = self._get_office_station_id(value)
        if station_id:
            return cfg.evelocations.Get(station_id).locationName
        return '-'

    def get_none_value_text(self):
        return GetByLabel('UI/Corporations/Goals/AnyCorpOffice')

    def _get_form_component_values(self):
        values = super(CorpOfficeGoalParameter, self)._get_form_component_values()
        values['options'] = self._get_options()
        return values

    def _get_options(self):
        options = [ ComboEntryData(cfg.evelocations.Get(o.stationID).locationName, o.officeID) for o in sm.GetService('officeManager').GetMyCorporationsOffices() ]
        if not self.is_required and not self._should_render_multi_select():
            options.insert(0, ComboEntryData(GetByLabel('UI/Common/Any'), None))
        return options

    def get_entry_menu(self, value):
        if value:
            station_id = self._get_office_station_id(value)
            if station_id:
                return sm.GetService('menu').CelestialMenu(station_id)
        else:
            return self.get_none_entry_menu()

    def get_none_entry_menu(self):
        m = MenuData()
        for office in sm.GetService('officeManager').GetMyCorporationsOffices():
            m.AddEntry(cfg.evelocations.Get(office.stationID).locationName, subMenuData=lambda : sm.GetService('menu').CelestialMenu(office.stationID))

        return m

    def get_entry_drag_data(self, value):
        station_id = self._get_office_station_id(value)
        if station_id:
            return eveui.dragdata.Location(station_id)

    def _get_office_station_id(self, value):
        if value:
            office = sm.GetService('officeManager').GetMyCorporationsOffice(value)
            if office:
                return office.stationID


class CorpOfficeLocationGoalParameter(_LocationGoalParameter):
    parameter_id = GoalParameterTypes.CORP_OFFICE_LOCATION
    form_component_class = formComponent.Enum
    form_component_class_multiple = MultiValueEnumComponent
    entry_height = 32

    def _get_form_component_values(self):
        values = super(CorpOfficeLocationGoalParameter, self)._get_form_component_values()
        values['options'] = self._get_options()
        return values

    def _get_options(self):
        options = [ ComboEntryData(cfg.evelocations.Get(o.stationID).locationName, o.stationID) for o in sm.GetService('officeManager').GetMyCorporationsOffices() ]
        if not self.is_required and not self._should_render_multi_select():
            options.insert(0, ComboEntryData(GetByLabel('UI/Common/Any'), None))
        return options


class FactionalWarfareComplexGoalParameter(_BaseGoalParameter):
    parameter_id = GoalParameterTypes.FACTIONAL_WARFARE_COMPLEX_TYPE
    form_component_class = formComponent.Enum
    form_component_class_multiple = MultiValueEnumComponent
    entry_height = 32

    def get_entry_title(self, value):
        return self._get_option_text(value)

    def _get_form_component_values(self):
        values = super(FactionalWarfareComplexGoalParameter, self)._get_form_component_values()
        values['options'] = self._get_options()
        return values

    def _get_options(self):
        FW_COMPLEX_TYPES = (appConst.dunArchetypeFactionalWarfareComplexNovice,
         appConst.dunArchetypeFactionalWarfareComplexSmall,
         appConst.dunArchetypeFactionalWarfareComplexMedium,
         appConst.dunArchetypeFactionalWarfareComplexLarge)
        options = [ ComboEntryData(label=self._get_option_text(complex_type), returnValue=complex_type) for complex_type in FW_COMPLEX_TYPES ]
        if not self._should_render_multi_select():
            options.insert(0, ComboEntryData(GetByLabel('UI/Common/Any'), None))
        return options

    def _get_option_text(self, value):
        from evearchetypes import GetArchetypeTitle
        return GetByMessageID(GetArchetypeTitle(value))


class OnBehalfOfGoalParameter(_BaseGoalParameter):
    parameter_id = GoalParameterTypes.ON_BEHALF_OF
    form_component_class = formComponent.Enum
    form_component_class_multiple = MultiValueEnumComponent
    entry_height = 32

    def get_entry_title(self, value):
        return self._get_option_text(value)

    def _get_form_component_values(self):
        values = super(OnBehalfOfGoalParameter, self)._get_form_component_values()
        values['options'] = self._get_options()
        return values

    def _get_options(self):
        return [ComboEntryData(self._get_option_text(ON_BEHALF_OF_SELF), ON_BEHALF_OF_SELF), ComboEntryData(self._get_option_text(ON_BEHALF_OF_CORP), ON_BEHALF_OF_CORP)]

    def _get_option_text(self, value):
        return GetByLabel(ON_BEHALF_OF_LABELS[value])


class SignatureTypeGoalParameter(_BaseGoalParameter):
    parameter_id = GoalParameterTypes.SIGNATURE_TYPE
    form_component_class = formComponent.Enum
    form_component_class_multiple = MultiValueEnumComponent
    entry_height = 32

    def get_entry_title(self, value):
        from probescanning.explorationSites import get_signature_type_label
        return GetByLabel(get_signature_type_label(value))

    def _get_form_component_values(self):
        values = super(SignatureTypeGoalParameter, self)._get_form_component_values()
        values['options'] = self._get_options()
        return values

    def _get_options(self):
        from probescanning.explorationSites import get_all_signature_types, siteTypeOre
        options = [ ComboEntryData(label=self.get_entry_title(signature_type), returnValue=signature_type) for signature_type in get_all_signature_types() if signature_type is not siteTypeOre ]
        if not self._should_render_multi_select():
            options.insert(0, ComboEntryData(GetByLabel('UI/Common/Any'), None))
        return options


class HackingContainerTypeGoalParameter(_BaseGoalParameter):
    parameter_id = GoalParameterTypes.HACKING_CONTAINER_TYPE
    form_component_class = formComponent.Enum
    entry_height = 32
    HACKING_CONTAINER_TYPE_LABELS = {'data': 'UI/GameGoalConfig/Parameters/DataHackingContainerType',
     'relic': 'UI/GameGoalConfig/Parameters/RelicHackingContainerType'}

    def get_entry_title(self, value):
        return GetByLabel(self.HACKING_CONTAINER_TYPE_LABELS[value])

    def _get_form_component_values(self):
        values = super(HackingContainerTypeGoalParameter, self)._get_form_component_values()
        values['options'] = self._get_options()
        return values

    def _get_options(self):
        options = [ComboEntryData(self.get_entry_title('data'), 'data'), ComboEntryData(self.get_entry_title('relic'), 'relic')]
        options.insert(0, ComboEntryData(GetByLabel('UI/Common/Any'), None))
        return options


class BooleanTypeGoalParameter(_BaseGoalParameter):
    parameter_id = GoalParameterTypes.BOOLEAN_TYPE
    form_component_class = formComponent.Boolean

    @property
    def values(self):
        return bool(self._value)

    def get_none_value_text(self):
        return GetByLabel('UI/Generic/No')

    def get_entry_title(self, value):
        if value:
            return GetByLabel('UI/Generic/No')
        else:
            return GetByLabel('UI/Generic/Yes')


class CapsuleerInvolvementParameter(BooleanTypeGoalParameter):
    parameter_id = GoalParameterTypes.CAPSULEER_INVOLVEMENT
    entry_height = 32

    @property
    def values(self):
        return bool(self._value)

    def get_none_value_text(self):
        return GetByLabel('UI/Corporations/Goals/AnyLossesCovered')

    def get_entry_title(self, value):
        if value:
            return GetByLabel('UI/Corporations/Goals/OnlyCoverLossesCausedByCapsuleers')
        else:
            return GetByLabel('UI/Corporations/Goals/AnyLossesCovered')


def _get_text_field_placeholder(is_required):
    if is_required:
        return GetByLabel('UI/Corporations/Goals/TypeInName')
    else:
        return u'{} ({})'.format(GetByLabel('UI/Corporations/Goals/TypeInName'), GetByLabel('UI/Corporations/Goals/Optional'))


def _render_basic_icon(icon, size = 32, color = TextColor.NORMAL):
    return Sprite(texturePath=icon, align=Align.CENTER, height=size, width=size, color=color)


def _map_classes(local_scope):
    for name, value in local_scope.items():
        if '__' in name:
            continue
        if isinstance(value, type) and issubclass(value, _BaseGoalParameter) and value.parameter_id is not None:
            _class_map[value.parameter_id] = value


_map_classes(locals())
