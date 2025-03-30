#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\common\skipconditions\ship.py
from operations.common.skipconditions.skipconditions import SkipCondition, OPERATOR_STRING_TO_EVALUATION_FUNCTION

class ConditionTargetsLocked(SkipCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('operand has to be an integer value')

        try:
            type_id = condition_parameters.identifier
            if type_id is not None:
                type_id = int(type_id)
        except ValueError:
            raise RuntimeError("'Targets Locked' evaluation requires typeID as an integer identifier")

        count = self.get_num_targets(type_id)
        return operator_func(count, operand)

    def get_num_targets(self, type_id = None):
        targets_by_id = sm.GetService('target').GetTargets()
        num_targets = 0
        for target in targets_by_id.values():
            if type_id and type_id != target.typeID:
                continue
            num_targets += 1

        return num_targets
