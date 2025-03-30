#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\roles.py
from behaviors.const.behaviorroles import COMBAT_ROLES, ROLE_LOGISTIC
from behaviors.const.blackboardchannels import ROLE_MESSAGE_CHANNEL, COMMANDER_ADDRESS

def get_role_for_member(task, item_id):
    return task.GetMessageChannelForItemId(item_id, ROLE_MESSAGE_CHANNEL).GetLastMessageValue()


def get_group_commander(task):
    return task.GetLastBlackboardValue(COMMANDER_ADDRESS)


def is_commander(task, item_id):
    return item_id == get_group_commander(task)


def has_combat_role(task, item_id):
    role = task.GetMessageChannelForItemId(item_id, ROLE_MESSAGE_CHANNEL).GetLastMessageValue()
    return role in COMBAT_ROLES


def is_logistic_role(task, item_id):
    return get_role_for_member(task, item_id) == ROLE_LOGISTIC
