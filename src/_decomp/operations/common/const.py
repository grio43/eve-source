#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\common\const.py
from eve.common.lib.appConst import DUNGEON_ORIGIN_TUTORIAL

class OperationState:
    LOCKED = 0
    ACTIVE = 1
    AVAILABLE = 2
    COMPLETE = 3
    REACTIVATED = 4


class TaskState:
    LOCKED = 10
    ACTIVE = 11
    COMPLETE = 12
    BLOCKED = 13
    SKIPPED = 14


class CategoryState:
    LOCKED = 20
    ACTIVE = 21
    COMPLETE = 22
    SKIPPED_BY_PLAYER = 23
    SKIPPED_BY_INCEPTION = 24
    SKIPPED_BY_ACHIEVEMENTS = 25
    SKIPPED_BY_AGE = 26
    SKIPPED_BY_BNNPE_TERMINATION = 27


TASK_DELAY_BEFORE_DEFAULT = 1.5
OPERATION_CATEGORY_TUTORIAL_AIR_NPE = 2122
OPERATION_CATEGORY_TUTORIAL_BNNPE_START = 2113
OPERATION_CATEGORY_TUTORIAL_BNNPE_COMBAT = 2115
OPERATION_CATEGORY_TUTORIAL_BNNPE_SHIP_DEATH = 31
OPERATION_CATEGORY_TUTORIAL_BNNPE_POD_DEATH = 32
BNNPE_CATEGORIES = [OPERATION_CATEGORY_TUTORIAL_BNNPE_START,
 OPERATION_CATEGORY_TUTORIAL_BNNPE_COMBAT,
 OPERATION_CATEGORY_TUTORIAL_BNNPE_SHIP_DEATH,
 OPERATION_CATEGORY_TUTORIAL_BNNPE_POD_DEATH]
OPERATION_CATEGORY_SHIP_DEATH = None
OPERATION_CATEGORY_CAPSULE_DEATH = None
OPERATION_CATEGORY_RECOMMENDATIONS = 2126
UNLOCKED_CATEGORIES = [OPERATION_CATEGORY_TUTORIAL_AIR_NPE,
 OPERATION_CATEGORY_RECOMMENDATIONS,
 OPERATION_CATEGORY_TUTORIAL_BNNPE_START,
 OPERATION_CATEGORY_TUTORIAL_BNNPE_COMBAT,
 OPERATION_CATEGORY_TUTORIAL_BNNPE_SHIP_DEATH,
 OPERATION_CATEGORY_TUTORIAL_BNNPE_POD_DEATH]
DUNGEON_ORIGIN_BY_OPERATION_CATEGORY = {OPERATION_CATEGORY_TUTORIAL_AIR_NPE: DUNGEON_ORIGIN_TUTORIAL,
 OPERATION_CATEGORY_TUTORIAL_BNNPE_COMBAT: DUNGEON_ORIGIN_TUTORIAL}
OPERATIONS_RESTRICTED_TO_HIGH_SEC = {110,
 111,
 114,
 122,
 123,
 124,
 139,
 140,
 141,
 142,
 143,
 144,
 145,
 146,
 148,
 149}

def generate_int_to_string_dict_for_enum_class(cls):
    return {cls.__dict__[i]:i for i in cls.__dict__.keys() if not i.startswith('__')}


OPERATION_STATE_TO_STRING = generate_int_to_string_dict_for_enum_class(OperationState)
TASK_STATE_TO_STRING = generate_int_to_string_dict_for_enum_class(TaskState)

class ResetToSiteReason:
    INTERNAL = 1
    BY_GM = 2
    BY_PLAYER = 3


class RewardSituation(object):
    ON_OPERATION_UNLOCKED = 1
    ON_OPERATION_COMPLETED = 2
    ON_TASK_COMPLETED = 3


SITUATION_NAME = {RewardSituation.ON_OPERATION_UNLOCKED: 'on operation unlocked',
 RewardSituation.ON_OPERATION_COMPLETED: 'on operation completed',
 RewardSituation.ON_TASK_COMPLETED: 'on task completed'}

class RewardToken(object):

    def __init__(self, typeID, quantity, rewardedTimestamp, claimedTimestamp, claimer):
        self.typeID = typeID
        self.quantity = quantity
        self.rewardedTimestamp = rewardedTimestamp
        self.claimedTimestamp = claimedTimestamp
        self.claimer = claimer


class SkillRewardToken(object):

    def __init__(self, skillTypeID, level, sp, rewardedTimestamp):
        self.skillTypeID = skillTypeID
        self.level = level
        self.sp = sp
        self.rewardedTimestamp = rewardedTimestamp


class SiteSpawningType(object):
    IN_SCHOOL_STARTING_SYSTEM = 'schoolStartingSystem'
    IN_NEIGHBORING_SOLAR_SYSTEM = 'solarSystemInRange'
    IN_NEIGHBORING_SOLAR_SYSTEM_EXCLUDE_SAME = 'solarSystemInRangeExcludeSame'
    IN_SAME_SOLAR_SYSTEM = 'sameSolarSystem'
    IN_SAME_GRID = 'sameGrid'
