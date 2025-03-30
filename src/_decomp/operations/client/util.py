#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\client\util.py
from evetypes import GetName
import operations.common.util as commonUtil
CHECK_MODULE_REQUIREMENTS_ON_UNDOCK = True
MISSING_REQUIREMENTS_DIALOG_ID = 'UndockingWithoutOperationModuleRequirements'

def are_operations_active():
    return commonUtil.is_character_eligible_for_operation(session.charid)


def can_undock(module_requirements):
    if not CHECK_MODULE_REQUIREMENTS_ON_UNDOCK or not module_requirements:
        return True
    missing_modules = get_module_requirements_string(module_requirements)
    if not missing_modules:
        return True
    if prompt(MISSING_REQUIREMENTS_DIALOG_ID, {'missingRequirements': missing_modules}):
        return True
    return False


def prompt(dialog_id, dialog_args):
    from carbonui.const import YESNO, ID_YES
    return eve.Message(dialog_id, dialog_args, YESNO, suppress=ID_YES) == ID_YES


def get_module_requirements_string(module_requirements):
    missing_modules_string = ''
    missing_modules = get_missing_modules(module_requirements)
    for module in missing_modules:
        if missing_modules_string:
            missing_modules_string += '<br>'
        module_name = GetName(module)
        missing_modules_string += '- ' + module_name

    return missing_modules_string


def get_missing_modules(module_requirements):
    fitting_svc = sm.GetService('fittingSvc')
    missing_modules = []
    for module_requirement in module_requirements:
        if not fitting_svc.IsTypeFittedInActiveShip(module_requirement):
            missing_modules.append(module_requirement)

    return missing_modules
