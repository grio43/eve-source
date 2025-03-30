#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\blackboards.py
from npcs.server.components.responsethresholdoverrides import EntityResponseThresholds

def update_blackboard_set_if_changed(task, detected_ids, object_address):
    id_set = task.GetLastBlackboardValue(object_address)
    if id_set is None:
        if not detected_ids:
            return False
        id_set = detected_ids
    elif detected_ids.issubset(id_set):
        return False
    id_set.update(detected_ids)
    task.SendBlackboardValue(object_address, id_set)
    return True


def get_response_thresholds(task):
    return EntityResponseThresholds(None, None, task)
