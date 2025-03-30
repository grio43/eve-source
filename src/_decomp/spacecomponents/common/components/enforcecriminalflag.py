#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\common\components\enforcecriminalflag.py
from spacecomponents.common.componentConst import ENFORCE_CRIMINAL_FLAG_CLASS
from spacecomponents.common.data import get_space_component_for_type
from spacecomponents.common.helper import HasEnforceCriminalFlagComponent

def has_enforce_suspect_or_criminal_flag(type_id):
    if not HasEnforceCriminalFlagComponent(type_id):
        return False
    return has_enforce_suspect_flag(type_id) or has_enforce_criminal_flag(type_id)


def has_enforce_suspect_flag(type_id):
    return get_space_component_for_type(type_id, ENFORCE_CRIMINAL_FLAG_CLASS).enforceSuspectFlag


def has_enforce_criminal_flag(type_id):
    return get_space_component_for_type(type_id, ENFORCE_CRIMINAL_FLAG_CLASS).enforceCriminalFlag
