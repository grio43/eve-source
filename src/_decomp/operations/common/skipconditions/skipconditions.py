#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\common\skipconditions\skipconditions.py
OPERATOR_STRING_TO_EVALUATION_FUNCTION = {'greaterThan': lambda a, b: a > b,
 'lessThan': lambda a, b: a < b,
 'equalTo': lambda a, b: a == b}

class SkipCondition(object):

    def Evaluate(self, character_id, condition_parameters):
        raise NotImplementedError
