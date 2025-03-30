#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\common\skipconditions\ui.py
from operations.common.skipconditions.skipconditions import SkipCondition, OPERATOR_STRING_TO_EVALUATION_FUNCTION

class ConditionWindowOpen(SkipCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('Window Open condition evaluation requires integer parameter')

        try:
            window_id = condition_parameters.identifier
        except ValueError:
            raise RuntimeError('Window Open condition evaluation requires the windowID as a string identifier')

        return self.is_window_open(window_id, operator_func, operand)

    def is_window_open(self, window_id, operator_func, operand):
        raise NotImplementedError('is_window_open check must be implemented in subclass')


class ConditionWindowOpenWithExactName(ConditionWindowOpen):

    def is_window_open(self, window_id, operator_func, operand):
        from carbonui.control.window import Window
        is_open = Window.IsOpen
        is_already_open = is_open(window_id) or is_open((window_id, None))
        window_count = int(is_already_open)
        return operator_func(window_count, operand)


class ConditionWindowOpenWithNameLike(ConditionWindowOpen):

    def is_window_open(self, window_id, operator_func, operand):
        from carbonui.uicore import uicore
        all_open_windows = [ window_data.name for window_data in uicore.registry.GetWindows() ]
        window_count = len([ window_name for window_name in all_open_windows if window_id in window_name ])
        return operator_func(window_count, operand)


class ConditionAgencyContentGroupOpened(SkipCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = bool(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('Agency content group evaluation requires boolean parameter')

        try:
            content_group_ID = int(condition_parameters.identifier)
        except ValueError:
            raise RuntimeError('Agency content type evaluation requires the content type as an int')

        is_content_group_opened = self.is_content_group_opened(content_group_ID)
        return operator_func(is_content_group_opened, operand)

    def is_content_group_opened(self, content_group_ID):
        return sm.GetService('agencyNew').IsContentGroupOpened(content_group_ID)


class ConditionAgencyCardSelected(SkipCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError("'Agency card selected' evaluation requires integer operand")

        try:
            content_type = int(condition_parameters.identifier)
        except ValueError:
            raise RuntimeError("'Agency card selected' evaluation requires integer identifier")

        count = int(self.is_card_selected(content_type))
        return operator_func(count, operand)

    def is_card_selected(self, content_type):
        return sm.GetService('agencyNew').IsCardSelected(content_type)
