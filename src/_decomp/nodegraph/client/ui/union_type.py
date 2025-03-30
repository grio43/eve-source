#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\union_type.py
import evetypes
import eveui
import localization
from carbon.common.lib.const import maxBigint
from nodegraph.client.ui.fsd_field import FsdLoaderField, KeyValueFsdLoaderField, DataField
from unionTypes import UnionTypes
_class_map = {}

def get_all_union_type_classes():
    return _class_map


def get_union_type_class(union_type):
    return _class_map.get(union_type, None)


def get_union_type_name(union_type, value):
    union_type_class = get_union_type_class(union_type)
    if union_type_class:
        return union_type_class.get_name(value)
    else:
        return str(value)


class BaseUnionType(object):
    union_type = None
    fsd_editor_url = ''

    @classmethod
    def get_name(cls, entry):
        return entry

    @classmethod
    def get_input_field(cls, **kwargs):
        return None

    @classmethod
    def has_fsd_editor_url(cls):
        return bool(cls.fsd_editor_url)

    @classmethod
    def get_fsd_editor_url(cls, entry):
        return cls.fsd_editor_url.format(entry)

    @classmethod
    def open_fsd_editor_url(cls, entry):
        import webbrowser
        webbrowser.open_new('http://localhost:8000/{}'.format(cls.get_fsd_editor_url(entry)))


class BoolType(BaseUnionType):
    union_type = UnionTypes.boolType

    @classmethod
    def get_name(cls, entry):
        return bool(entry)

    @classmethod
    def get_input_field(cls, value = None, handle_change = None, **kwargs):
        input_field = eveui.Checkbox(checked=bool(value), callback=handle_change)
        input_field.__get_parameter_value__ = lambda : bool(input_field.GetValue())
        return input_field


class FloatType(BaseUnionType):
    union_type = UnionTypes.floatType

    @classmethod
    def get_input_field(cls, value = None, handle_change = None, **kwargs):
        input_field = eveui.SingleLineEditFloat(setvalue=value, OnChange=handle_change)
        input_field.OnMouseWheel = None
        input_field.__get_parameter_value__ = input_field.GetValue
        return input_field


class IntegerType(BaseUnionType):
    union_type = UnionTypes.integerType

    @classmethod
    def get_input_field(cls, value = None, handle_change = None, **kwargs):
        input_field = eveui.SingleLineEditInteger(setvalue=value, OnChange=handle_change, dataType=long, minValue=-maxBigint - 1, maxValue=maxBigint)
        input_field.OnMouseWheel = None
        input_field.__get_parameter_value__ = input_field.GetValue
        return input_field


class StringType(BaseUnionType):
    union_type = UnionTypes.stringType

    @classmethod
    def get_input_field(cls, value = None, handle_change = None, **kwargs):
        input_field = eveui.SingleLineEditText(setvalue=value, OnChange=handle_change)
        input_field.__get_parameter_value__ = input_field.GetValue
        return input_field


class ObjectType(BaseUnionType):
    union_type = UnionTypes.objectType

    @classmethod
    def get_input_field(cls, value = None, handle_change = None, **kwargs):
        input_field = eveui.SingleLineEditText(setvalue=value, OnChange=handle_change)
        input_field.__get_parameter_value__ = input_field.GetValue
        input_field.Disable()
        return input_field


class Vector3Type(BaseUnionType):
    union_type = UnionTypes.vector3Type

    @classmethod
    def get_input_field(cls, **kwargs):
        input_field = _construct_vector_input_field(**kwargs)
        return input_field


class EveTypeIdType(IntegerType):
    union_type = UnionTypes.eveTypeIdType
    fsd_editor_url = 'types/{}/'

    @classmethod
    def get_name(cls, entry):
        if entry is None:
            return
        return _format_name(evetypes.GetName(entry), entry)

    @classmethod
    def get_input_field(cls, **kwargs):
        return _construct_data_field(get_data=evetypes.Iterate, get_data_name=cls.get_name, **kwargs)


class EveTypeGroupIdType(IntegerType):
    union_type = UnionTypes.eveTypeGroupIdType
    fsd_editor_url = 'groups/{}/'

    @classmethod
    def get_name(cls, entry):
        if entry is None:
            return
        return _format_name(evetypes.GetGroupNameByGroup(entry), entry)

    @classmethod
    def get_input_field(cls, **kwargs):
        return _construct_data_field(get_data=evetypes.IterateGroups, get_data_name=cls.get_name, **kwargs)


class EveTypeCategoryIdType(IntegerType):
    union_type = UnionTypes.eveTypeCategoryIdType
    fsd_editor_url = 'categories/{}/'

    @classmethod
    def get_name(cls, entry):
        if entry is None:
            return
        return _format_name(evetypes.GetCategoryNameByCategory(entry), entry)

    @classmethod
    def get_input_field(cls, **kwargs):
        return _construct_data_field(get_data=evetypes.IterateCategories, get_data_name=cls.get_name, **kwargs)


class LocationIdType(IntegerType):
    union_type = UnionTypes.locationIdType

    @classmethod
    def get_name(cls, entry):
        if entry is None:
            return
        return _format_name(cfg.evelocations.Get(entry).locationName, entry)

    @classmethod
    def has_fsd_editor_url(cls):
        return False

    @classmethod
    def get_fsd_editor_url(cls, entry):
        return None


class SolarSystemIdType(LocationIdType):
    union_type = UnionTypes.solarSystemIdType

    @classmethod
    def get_input_field(cls, **kwargs):
        return _construct_data_field(get_data=(lambda : cfg.mapSystemCache), get_data_name=cls.get_name, **kwargs)


class ConstellationIdType(LocationIdType):
    union_type = UnionTypes.constellationIdType

    @classmethod
    def get_input_field(cls, **kwargs):
        return _construct_data_field(get_data=(lambda : cfg.mapConstellationCache), get_data_name=cls.get_name, **kwargs)


class RegionIdType(LocationIdType):
    union_type = UnionTypes.regionIdType

    @classmethod
    def get_input_field(cls, **kwargs):
        return _construct_data_field(get_data=(lambda : cfg.mapRegionCache), get_data_name=cls.get_name, **kwargs)


class StationIdType(LocationIdType):
    union_type = UnionTypes.stationIdType


class DungeonIdType(IntegerType):
    union_type = UnionTypes.dungeonIdType


class CheckPointsIdType(IntegerType):
    union_type = UnionTypes.checkPointsIdType


class PlayerIdType(IntegerType):
    union_type = UnionTypes.playerIdType

    @classmethod
    def get_input_field(cls, value = None, handle_change = None, **kwargs):
        input_field = eveui.SingleLineEditInteger(setvalue=value, OnChange=handle_change, minValue=0)
        input_field.OnMouseWheel = None
        input_field.__get_parameter_value__ = input_field.GetValue
        return input_field


class AgentLevelType(IntegerType):
    union_type = UnionTypes.agentLevelType

    @classmethod
    def get_input_field(cls, value = None, handle_change = None, **kwargs):
        input_field = eveui.SingleLineEditInteger(setvalue=value, OnChange=handle_change, minValue=1, maxValue=5)
        input_field.OnMouseWheel = None
        input_field.__get_parameter_value__ = input_field.GetValue
        return input_field


class SkillLevelType(IntegerType):
    union_type = UnionTypes.skillLevelType

    @classmethod
    def get_input_field(cls, value = None, handle_change = None, **kwargs):
        input_field = eveui.SingleLineEditInteger(setvalue=value, OnChange=handle_change, minValue=0, maxValue=5)
        input_field.OnMouseWheel = None
        input_field.__get_parameter_value__ = input_field.GetValue
        return input_field


class ExternalReferenceType(IntegerType):
    union_type = None
    name_param = 'name'

    @classmethod
    def get_data_loader(cls):
        return None

    @classmethod
    def get_name(cls, entry):
        if entry is None:
            return
        data = cls.get_data_loader().GetData()
        fsd_object = data.get(entry, {})
        name = getattr(fsd_object, cls.name_param, getattr(fsd_object, 'nameID', ''))
        if isinstance(name, int):
            name = localization.GetByMessageID(name)
        return _format_name(name, entry)

    @classmethod
    def get_input_field(cls, **kwargs):
        return _construct_fsd_field(fsd_loader=cls.get_data_loader, name_param=cls.name_param, **kwargs)


class AtomIdType(ExternalReferenceType):
    union_type = UnionTypes.atomIdType
    fsd_editor_url = 'cfsd/projects/atoms/atoms/{}/edit'

    @classmethod
    def get_data_loader(cls):
        from nodegraph.common.atomdata import AtomsLoader
        return AtomsLoader


class CommandSetIdType(ExternalReferenceType):
    union_type = UnionTypes.commandSetIdType
    fsd_editor_url = 'command/set/{}/'

    @classmethod
    def get_data_loader(cls):
        from uihider import CommandSetsData
        return CommandSetsData


class ConversationIdType(ExternalReferenceType):
    union_type = UnionTypes.conversationIdType
    fsd_editor_url = 'conversations/{}/'

    @classmethod
    def get_data_loader(cls):
        from conversations.fsdloaders import ConversationsLoader
        return ConversationsLoader


class ConversationAgentIdType(ExternalReferenceType):
    union_type = UnionTypes.conversationAgentIdType
    fsd_editor_url = 'conversations/{}/'

    @classmethod
    def get_data_loader(cls):
        from conversations.fsdloaders import ConversationAgentsLoader
        return ConversationAgentsLoader


class DogmaAttributeIdType(ExternalReferenceType):
    union_type = UnionTypes.dogmaAttributeIdType
    fsd_editor_url = 'dogma/attributes/{}/edit/'

    @classmethod
    def get_data_loader(cls):
        from dogma.data import DogmaAttributes
        return DogmaAttributes


class EveTypeListIdType(ExternalReferenceType):
    union_type = UnionTypes.eveTypeListIdType
    fsd_editor_url = 'evetypelists/{}/edit/'

    @classmethod
    def get_data_loader(cls):
        from evetypes.data import TypeListLoader
        return TypeListLoader


class GraphicIdType(ExternalReferenceType):
    union_type = UnionTypes.graphicIdType
    fsd_editor_url = 'graphics/graphicIDs/{}'
    name_param = 'graphic_id'

    @classmethod
    def get_data_loader(cls):
        from fsdBuiltData.common.graphicIDs import GraphicIDs
        return GraphicIDs


class MenuHighlightIdType(ExternalReferenceType):
    union_type = UnionTypes.menuHighlightIdType
    fsd_editor_url = 'uiHighlights/menuHighlights/{}/'

    @classmethod
    def get_data_loader(cls):
        from uihighlighting.fsdloaders import MenuHighlightsLoader
        return MenuHighlightsLoader


class MusicTriggerIdType(ExternalReferenceType):
    union_type = UnionTypes.musicTriggerIdType
    fsd_editor_url = 'audio/musicTriggers/{}'
    name_param = 'trigger'

    @classmethod
    def get_data_loader(cls):
        from fsdBuiltData.client.musicTriggers import MusicTriggers
        return MusicTriggers


class NodeGraphIdType(ExternalReferenceType):
    union_type = UnionTypes.nodeGraphIdType
    fsd_editor_url = 'nodegraphs/{}/'

    @classmethod
    def get_data_loader(cls):
        from nodegraph.common.nodedata import NodeGraphLoader
        return NodeGraphLoader


class NodeTypeIdType(ExternalReferenceType):
    union_type = UnionTypes.nodeTypeIdType
    fsd_editor_url = 'cfsd/projects/nodegraphs/nodetypes/{}/edit'

    @classmethod
    def get_data_loader(cls):
        from nodegraph.common.nodedata import NodeTypesLoader
        return NodeTypesLoader


class NpcCharacterIdType(ExternalReferenceType):
    union_type = UnionTypes.npcCharacterIdType
    fsd_editor_url = 'npccharacters/{}/'

    @classmethod
    def get_data_loader(cls):
        from characterdata.npccharacters import NpcCharactersLoader
        return NpcCharactersLoader


class NpcCorporationIdType(ExternalReferenceType):
    union_type = UnionTypes.npcCorporationIdType
    fsd_editor_url = 'corporation/npccorporations/{}/'

    @classmethod
    def get_data_loader(cls):
        from npcs.npccorporations import NpcCorporationsLoader
        return NpcCorporationsLoader


class NpcFactionIdType(ExternalReferenceType):
    union_type = UnionTypes.npcFactionIdType
    fsd_editor_url = 'character/factions/{}/'

    @classmethod
    def get_data_loader(cls):
        from characterdata.factions import FactionsLoader
        return FactionsLoader


class UiHidingTemplateIdType(ExternalReferenceType):
    union_type = UnionTypes.uiHidingTemplateIdType
    fsd_editor_url = 'ui/uihidingtemplates/edit/{}/'

    @classmethod
    def get_data_loader(cls):
        from uihider.fsd_loader import UiHidingTemplatesData
        return UiHidingTemplatesData


class UiHighlightIdType(ExternalReferenceType):
    union_type = UnionTypes.uiHighlightIdType
    fsd_editor_url = 'uiHighlights/uiHighlights/{}/'

    @classmethod
    def get_data_loader(cls):
        from uihighlighting.fsdloaders import UIHighlightsLoader
        return UIHighlightsLoader


class SoundIdType(ExternalReferenceType):
    union_type = UnionTypes.soundIdType
    fsd_editor_url = 'audio/soundIDs/{}/'
    name_param = 'wwiseEvent'

    @classmethod
    def get_data_loader(cls):
        from fsdBuiltData.common.soundIDs import SoundIDs
        return SoundIDs


class SpaceObjectHighlightIdType(ExternalReferenceType):
    union_type = UnionTypes.spaceObjectHighlightIdType
    fsd_editor_url = 'uiHighlights/spaceObjectHighlights/{}/'

    @classmethod
    def get_data_loader(cls):
        from uihighlighting.fsdloaders import SpaceObjectHighlightsLoader
        return SpaceObjectHighlightsLoader


class MissionIdType(ExternalReferenceType):
    union_type = UnionTypes.missionIdType
    fsd_editor_url = 'missions/missions/{}/edit/'

    @classmethod
    def get_data_loader(cls):
        from evemissions.client.data import ClientMissionsLoader
        return ClientMissionsLoader


class RaceIdType(ExternalReferenceType):
    union_type = UnionTypes.raceIdType
    fsd_editor_url = 'character/races/{}/'

    @classmethod
    def get_data_loader(cls):
        from characterdata.races import RacesLoader
        return RacesLoader


class NpcCorporationDivisionIdType(ExternalReferenceType):
    union_type = UnionTypes.npcCorporationDivisionIdType

    @classmethod
    def get_data_loader(cls):
        from npcs.divisions import NpcCorporationDivisionsLoader
        return NpcCorporationDivisionsLoader


class AgentTypeIdType(BaseUnionType):
    union_type = UnionTypes.agentTypeIdType

    @classmethod
    def get_data_loader(cls):
        from eveagent.data import AgentTypes
        return AgentTypes

    @classmethod
    def get_input_field(cls, **kwargs):
        return _construct_key_value_fsd_field(fsd_loader=cls.get_data_loader, **kwargs)


class SkillPlanIdType(ExternalReferenceType):
    union_type = UnionTypes.skillPlanIdType

    @classmethod
    def get_data_loader(cls):
        from skills.skillplan.skillPlanFSDLoader import SkillPlanLoader
        return SkillPlanLoader


class CareerPathIdType(ExternalReferenceType):
    union_type = UnionTypes.careerPathIdType

    @classmethod
    def get_data_loader(cls):
        from characterdata.careerpath import CareerPathLoader
        return CareerPathLoader


class CrimewatchTimerType(StringType):
    union_type = UnionTypes.crimewatchTimerType

    @classmethod
    def get_input_field(cls, **kwargs):
        from eve.client.script.ui.crimewatch.crimewatchTimers import TimerType
        return _construct_enum_field(options=TimerType, **kwargs)


class FittingWindowTabType(StringType):
    union_type = UnionTypes.fittingWindowTabType

    @classmethod
    def get_input_field(cls, **kwargs):
        options = ['equipment', 'personalization']
        return _construct_combo_input_field(options=options, **kwargs)


class IndustryActivityType(StringType):
    union_type = UnionTypes.industryActivityType

    @classmethod
    def get_input_field(cls, **kwargs):
        from industry.const import ACTIVITY_NAMES
        options = ['any'] + ACTIVITY_NAMES.values()
        return _construct_combo_input_field(options=options, **kwargs)


class IndustryJobErrorType(StringType):
    union_type = UnionTypes.industryJobErrorType

    @classmethod
    def get_input_field(cls, **kwargs):
        options = ['any',
         'INVALID_OWNER',
         'MISSING_MATERIAL',
         'ACCOUNT_FUNDS']
        return _construct_combo_input_field(options=options, **kwargs)


class IndustryJobStatusType(StringType):
    union_type = UnionTypes.industryJobStatusType

    @classmethod
    def get_input_field(cls, **kwargs):
        options = ['any',
         'installed',
         'ready',
         'paused']
        return _construct_combo_input_field(options=options, **kwargs)


class UiBlinkType(StringType):
    union_type = UnionTypes.uiBlinkType

    @classmethod
    def get_input_field(cls, **kwargs):
        options = ['box', 'ring']
        return _construct_combo_input_field(options=options, **kwargs)


class OperatorType(StringType):
    union_type = UnionTypes.operatorType

    @classmethod
    def get_input_field(cls, **kwargs):
        from nodegraph.common.util import operator_functions
        return _construct_combo_input_field(options=operator_functions, **kwargs)


class SettingsGroupType(StringType):
    union_type = UnionTypes.settingsGroupType

    @classmethod
    def get_input_field(cls, **kwargs):
        options = ['ui',
         'windows',
         'tabgroups',
         'cmd',
         'suppress',
         'localization',
         'audio',
         'device',
         'generic']
        return _construct_combo_input_field(options=options, **kwargs)


class SettingsSectionType(StringType):
    union_type = UnionTypes.settingsSectionType

    @classmethod
    def get_input_field(cls, **kwargs):
        options = ['char', 'user', 'public']
        return _construct_combo_input_field(options=options, **kwargs)


class LanguageType(StringType):
    union_type = UnionTypes.languageType

    @classmethod
    def get_input_field(cls, **kwargs):
        from langutils.langconst import VALID_CLIENT_LANGUAGE_CODES
        return _construct_combo_input_field(options=VALID_CLIENT_LANGUAGE_CODES, **kwargs)


class TargetGroupKeyType(StringType):
    union_type = UnionTypes.targetGroupKeyType

    @classmethod
    def get_input_field(cls, **kwargs):
        options = ['AmarrPlexIntro1',
         'AmarrPlexIntro2',
         'AmarrPlexIntro3',
         'CaldariPlexIntro1',
         'CaldariPlexIntro2',
         'CaldariPlexIntro3',
         'GallentePlexIntro1',
         'GallentePlexIntro2',
         'GallentePlexIntro3',
         'MinmatarPlexIntro1',
         'MinmatarPlexIntro2',
         'MinmatarPlexIntro3']
        return _construct_combo_input_field(options=options, **kwargs)


class GoalType(ExternalReferenceType):
    union_type = UnionTypes.goalIdType
    fsd_editor_url = 'objective/goals/{}/'

    @classmethod
    def get_data_loader(cls):
        from storylines.client.objectives.loader import GoalsData
        return GoalsData


class ObjectiveType(ExternalReferenceType):
    union_type = UnionTypes.objectiveIdType
    fsd_editor_url = 'objective/objectives/{}/'

    @classmethod
    def get_data_loader(cls):
        from storylines.client.objectives.loader import ObjectivesData
        return ObjectivesData


def _construct_fsd_field(fsd_loader, name_param = 'name', value = None, handle_change = None, **kwargs):
    input_field = FsdLoaderField(fsd_loader=fsd_loader, name_param=name_param, data_id=value, **kwargs)
    if handle_change:
        input_field.bind(completed_suggestion=handle_change)
    input_field.__get_parameter_value__ = input_field.get_value
    return input_field


def _construct_key_value_fsd_field(fsd_loader, value = None, handle_change = None, **kwargs):
    input_field = KeyValueFsdLoaderField(fsd_loader=fsd_loader, data_id=value, **kwargs)
    if handle_change:
        input_field.bind(completed_suggestion=handle_change)
    input_field.__get_parameter_value__ = input_field.get_value
    return input_field


def _construct_data_field(get_data, get_data_name, value = None, handle_change = None, **kwargs):
    input_field = DataField(data_id=value, get_data=get_data, get_data_name=get_data_name, **kwargs)
    if handle_change:
        input_field.bind(completed_suggestion=handle_change)
    input_field.__get_parameter_value__ = input_field.get_value
    return input_field


def _construct_vector_input_field(value = None, handle_change = None, **kwargs):
    if value is None:
        value = [0.0, 0.0, 0.0]
    input_field = eveui.GridContainer(name='vectorTypeField', height=26, state=eveui.State.pick_children, lines=1, columns=len(value))
    fields = []
    for _value in value:
        _input_field = eveui.SingleLineEditFloat(setvalue=_value, OnChange=handle_change, minValue=(-922337203685477.0), decimalPlaces=2, parent=input_field, align=eveui.Align.to_all, width=0, padRight=4, **kwargs)
        fields.append(_input_field)

    def get_vector3_value():
        return tuple([ field.GetValue() for field in fields ])

    input_field.OnMouseWheel = None
    input_field.__get_parameter_value__ = get_vector3_value
    return input_field


def _construct_combo_input_field(options, value = None, handle_change = None, **kwargs):
    options = [ (str(i), i) for i in options ]
    input_field = eveui.Combo(options=options, select=value, callback=handle_change, **kwargs)
    input_field.__get_parameter_value__ = input_field.GetValue
    return input_field


def _construct_enum_field(options, value = None, handle_change = None, **kwargs):
    options = [ (u'{} ({})'.format(i.name, i.value), i.name) for i in options ]
    input_field = eveui.Combo(options=options, select=value, callback=handle_change, **kwargs)
    input_field.__get_parameter_value__ = input_field.GetValue
    return input_field


def _format_name(name, key):
    if name:
        return u'{} ({})'.format(name, key)
    return u'{}'.format(key)


def _map_classes(local_scope):
    for name, value in local_scope.items():
        if '__' in name:
            continue
        if isinstance(value, type) and issubclass(value, BaseUnionType) and value.union_type is not None:
            _class_map[value.union_type] = value


_map_classes(locals())
