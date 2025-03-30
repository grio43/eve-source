#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\item_modules.py
from behaviors.utility.dogmatic import get_dogma_lm
import evetypes

def get_fitted_modules(task, item_id):
    return get_dogma_lm(task).GetItemIdTypeIdAndFlagIdForOnlineFittedModules(item_id)


def is_type_id_in_type_list(type_list_id, type_id):
    return type_id in evetypes.GetTypeIDsByListID(type_list_id)


def has_fitted_from_type_list(task, item_id, type_list_id):
    for item_id, type_id, flag_id in get_fitted_modules(task, item_id):
        if is_type_id_in_type_list(type_list_id, type_id):
            return True

    return False
