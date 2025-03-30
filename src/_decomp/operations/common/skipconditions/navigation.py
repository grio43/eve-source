#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\common\skipconditions\navigation.py
from eve.common.lib import appConst
try:
    from eve.common.script.sys.eveCfg import IsDockedInStructure
except ImportError:
    IsDockedInStructure = None

from operations.common.skipconditions.skipconditions import SkipCondition, OPERATOR_STRING_TO_EVALUATION_FUNCTION

class LocationGroupCondition(SkipCondition):
    location_group_id = None

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        location_id, location_group_id = sm.GetService('charMgr').GetLocation(character_id)
        character_is_located_in_location_group = location_group_id == self.location_group_id
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('{classname} requires an integer parameter'.format(classname=self.__class__.__name__))

        return operator_func(character_is_located_in_location_group, operand)


class ConditionInSpace(LocationGroupCondition):
    location_group_id = appConst.groupSolarSystem


class ConditionInStation(LocationGroupCondition):
    location_group_id = appConst.groupStation


class ConditionInStructure(SkipCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('InStructure condition evaluation requires integer parameter')

        is_in_structure = IsDockedInStructure()
        in_structure_count = int(is_in_structure)
        return operator_func(in_structure_count, operand)


class ShipCondition(SkipCondition):

    def __init__(self):
        self.godma = None

    def get_ship_item(self):
        if bool(session.shipid):
            if self.godma is None:
                self.godma = sm.GetService('godma')
            return self.godma.GetItem(session.shipid)


class ShipGroupExclusionCondition(ShipCondition):
    excluded_ship_group_ids = []

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('Ship boarded condition requires integer parameter')

        is_ship_boarded = self.is_ship_group_boarded()
        ship_boarded_count = int(is_ship_boarded)
        return operator_func(ship_boarded_count, operand)

    def is_ship_group_boarded(self):
        ship_item = self.get_ship_item()
        if ship_item:
            return ship_item.groupID not in self.excluded_ship_group_ids
        return False


class ConditionShipBoarded(ShipGroupExclusionCondition):
    excluded_ship_group_ids = [appConst.groupCapsule]


class ConditionIsInCareerAgentStation(SkipCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('Career agent station evaluation requires integer parameter')

        count = int(self.is_in_career_agent_station())
        return operator_func(count, operand)

    def is_in_career_agent_station(self):
        return sm.GetService('agents').IsCareerAgentStation(session.stationid)


class ConditionIsInCareerAgentSystem(SkipCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('Career agent system evaluation requires integer parameter')

        count = int(self.is_in_career_agent_system())
        return operator_func(count, operand)

    def is_in_career_agent_system(self):
        return sm.GetService('agents').IsCareerAgentSystem(session.solarsystemid2)


class ConditionIsInRwSite(SkipCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('Is in RW site evaluation requires integer parameter')

        count = int(self.is_in_rw_site())
        return operator_func(count, operand)

    def is_in_rw_site(self):
        return sm.GetService('rwService').is_in_rw_dungeon_or_lobby()


class ConditionInProximity(SkipCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            radius = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError("'In Proximity' evaluation requires radius as an integer operand")

        try:
            type_id = int(condition_parameters.identifier)
        except ValueError:
            raise RuntimeError("'In Proximity' evaluation requires typeID as an integer identifier")

        return self.is_type_in_proximity(type_id, radius, operator_func)

    def is_type_in_proximity(self, type_id, radius, operator):
        return sm.GetService('michelle').GetBallpark().IsTypeInRange(type_id, radius, operator)


class ConditionDestinationSetToCareerAgent(SkipCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('operand has to be an integer value')

        count = int(self.is_destination_set_to_career_agent())
        return operator_func(count, operand)

    def is_destination_set_to_career_agent(self):
        waypoints = sm.GetService('starmap').GetWaypoints()
        if not waypoints:
            return False
        for location_id in waypoints:
            return sm.GetService('agents').IsCareerAgentStation(location_id)

        return False
