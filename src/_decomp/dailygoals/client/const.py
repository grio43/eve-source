#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dailygoals\client\const.py
from itertoolsext.Enum import Enum
import eveicon
from characterdata import careerpathconst
from inventorycommon.const import typeKredits, typeLoyaltyPointsHeraldry, typePlex

@Enum

class DailyGoalCategory(object):
    CATEGORY_UNSPECIFIED = 0
    CATEGORY_DAILY = 1
    CATEGORY_DAILY_BONUS = 2
    CATEGORY_MONTHLY_BONUS = 3


@Enum

class RewardType(object):
    ISK = 'ISK'
    LOYALTY_POINTS = 'LOYALTY_POINTS'
    SKILL_POINTS = 'SKILL_POINTS'
    ITEM = 'ITEM'
    PLEX = 'PLEX'


BATCH_SIZE = 25
TRACK_SIZE = 12
ICON_BY_REWARD_TYPE = {RewardType.ISK: eveicon.isk,
 RewardType.LOYALTY_POINTS: eveicon.evermark,
 RewardType.PLEX: eveicon.plex}
OVER_WRITE_ITEM_ICON = {83639: 'res:/UI/Texture/Icons/Inventory/nanocoating_64.png'}
REWARD_SORT_ORDER = {RewardType.ISK: 0,
 RewardType.LOYALTY_POINTS: 1,
 RewardType.SKILL_POINTS: 2}
SPECIFIC_ITEM_TYPE_TEXT = {83679: 722238,
 83639: 722238}
CAREER_PATH_SORT_ORDER = {careerpathconst.career_path_enforcer: 0,
 careerpathconst.career_path_explorer: 1,
 careerpathconst.career_path_industrialist: 2,
 careerpathconst.career_path_soldier_of_fortune: 3,
 careerpathconst.career_path_none: 4}
REWARD_TYPE_TO_TYPE_ID = {RewardType.ISK: typeKredits,
 RewardType.LOYALTY_POINTS: typeLoyaltyPointsHeraldry,
 RewardType.PLEX: typePlex}
PRICE_FIRST_COMPLETION = 2500
PRICE_SECOND_COMPLETION = 4500
