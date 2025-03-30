#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\common\skipconditions\skills.py
from operations.common.skipconditions.skipconditions import SkipCondition, OPERATOR_STRING_TO_EVALUATION_FUNCTION

class ServerSkillCondition(SkipCondition):

    def __init__(self):
        self.skillMgr = None

    def GetSkillHandler(self, character_id):
        if self.skillMgr is None:
            self.skillMgr = sm.GetService('skillMgr2')
        return self.skillMgr.GetSkillHandler(character_id)


class ConditionSkillPointsTotal(ServerSkillCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('Total skill point evaluation requires integer parameter')

        handler = self.GetSkillHandler(character_id)
        total_skill_points = handler.GetEstimatedSkillPoints()
        return operator_func(total_skill_points, operand)


class ConditionSkillLevel(ServerSkillCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('Skill level evaluation requires integer parameter')

        try:
            skill_type_id = int(condition_parameters.identifier)
        except ValueError:
            raise RuntimeError('Skill level evaluation requires the skill typeID as an integer identifier')

        handler = self.GetSkillHandler(character_id)
        skill_level = handler.GetSkillLevel(skill_type_id)
        return operator_func(skill_level, operand)


class ConditionFreeSkillPoints(ServerSkillCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('Free skill point evaluation requires integer parameter')

        handler = self.GetSkillHandler(character_id)
        free_skill_points = handler.GetFreeSkillPoints()
        return operator_func(free_skill_points, operand)


class ClientSkillCondition(SkipCondition):

    def __init__(self):
        self.skillSvc = None

    def GetSkillQueue(self):
        if self.skillSvc is None:
            self.skillSvc = sm.GetService('skillqueue')
        return self.skillSvc


class ConditionSkillInQueue(ClientSkillCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('Skill in queue evaluation requires integer parameter')

        try:
            skill_type_id = int(condition_parameters.identifier)
        except ValueError:
            raise RuntimeError('Skill in queue evaluation requires the skill typeID as an integer identifier')

        max_skill_level = self.GetSkillQueue().FindHighestLevelInQueue(skill_type_id)
        if max_skill_level is None:
            return False
        return operator_func(max_skill_level, operand)
