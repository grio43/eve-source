#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\grouprewards\data.py
from eveuniverse.security import get_security_class_text
from eveuniverse.security import securityClassHighSec
from eveuniverse.security import securityClassLowSec
from eveuniverse.security import securityClassZeroSec
from fsdBuiltData.common.base import BuiltDataLoader
from grouprewards import SECURITY_CRITERIA_ALL_SECURITY_BANDS
from grouprewards import SECURITY_CRITERIA_HIGH_SECURITY
from grouprewards import SECURITY_CRITERIA_LOW_SECURITY
from grouprewards import SECURITY_CRITERIA_NULL_SECURITY
try:
    import groupRewardsLoader
except ImportError:
    groupRewardsLoader = None

try:
    import groupRewardTypesLoader
except ImportError:
    groupRewardTypesLoader = None

class GroupRewardTableNotDefinedForSecurityClass(Exception):
    pass


class GroupRewards(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/groupRewards.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/groupRewards.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/groupRewards.fsdbinary'
    __loader__ = groupRewardsLoader


class GroupRewardTypes(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/server/groupRewardTypes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/groupRewardTypes.fsdbinary'
    __loader__ = groupRewardsLoader


def get_group_reward(group_reward_id):
    return get_group_rewards().get(group_reward_id)


def get_group_rewards():
    return GroupRewards.GetData()


def get_group_reward_type(group_reward_type_id):
    return get_group_reward_types().get(group_reward_type_id)


def get_group_reward_types():
    return GroupRewardTypes.GetData()


def get_reward_lp_log_type_name_id(group_reward_id):
    return get_group_reward(group_reward_id).lpLogTypeNameID


def get_delayed_reward_tables(group_reward_id):
    group_reward = get_group_reward(group_reward_id)
    return [ table for table in group_reward.tables if table.delayed ]


def get_immediate_reward_tables(group_reward_id):
    group_reward = get_group_reward(group_reward_id)
    return [ table for table in group_reward.tables if not table.delayed ]


def get_delayed_reward_tables_for_security_class(group_reward_id, security_class):
    delayed_tables = get_delayed_reward_tables(group_reward_id)
    return get_tables_for_security_class(delayed_tables, security_class)


def get_immediate_reward_tables_for_security_class(group_reward_id, security_class):
    delayed_tables = get_immediate_reward_tables(group_reward_id)
    return get_tables_for_security_class(delayed_tables, security_class)


def get_security_criteria(security_class):
    return GET_SECURITY_CRITERIA_CHECK_FROM_SECURITY_CLASS[security_class]


def get_tables_for_security_class(tables, security_class):
    result = []
    security_criteria = get_security_criteria(security_class)
    for table in tables:
        if is_security_criteria_all(table):
            result.append(table)
        elif security_criteria(table):
            result.append(table)

    return result


def is_security_criteria_all(table):
    return table.securityCriteria == SECURITY_CRITERIA_ALL_SECURITY_BANDS


def is_security_criteria_high(table):
    return table.securityCriteria == SECURITY_CRITERIA_HIGH_SECURITY


def is_security_criteria_low(table):
    return table.securityCriteria == SECURITY_CRITERIA_LOW_SECURITY


def is_security_criteria_null(table):
    return table.securityCriteria == SECURITY_CRITERIA_NULL_SECURITY


GET_SECURITY_CRITERIA_CHECK_FROM_SECURITY_CLASS = {securityClassZeroSec: is_security_criteria_null,
 securityClassLowSec: is_security_criteria_low,
 securityClassHighSec: is_security_criteria_high}

def get_group_reward_min_max_player_count_by_security_class(group_reward_id, security_class):
    group_reward = get_group_reward(group_reward_id)
    tables = get_tables_for_security_class(group_reward.tables, security_class)
    if len(tables) == 0:
        raise GroupRewardTableNotDefinedForSecurityClass('Group reward {} has no table for security class {}'.format(group_reward_id, get_security_class_text(security_class)))
    min_player_count = get_min_player_count_from_reward_tables(tables)
    max_player_count = get_max_player_count_from_reward_tables(tables)
    return (min_player_count, max_player_count)


def get_max_player_count_from_reward_tables(tables):
    return max((get_max_rewarded_player_count(table) for table in tables))


def get_min_player_count_from_reward_tables(tables):
    return min((get_min_rewarded_player_count(table) for table in tables))


def get_max_rewarded_player_count(table):
    return max([ entry.playerCount for entry in table.entries if entry.quantity > 0 ])


def get_min_rewarded_player_count(table):
    return min([ entry.playerCount for entry in table.entries if entry.quantity > 0 ])


def get_max_reward_from_tables_with_reward_type(reward_tables, reward_type_id):
    return max((get_max_reward_from_reward_table(table) for table in reward_tables if reward_type_id == table.rewardType))


def get_max_reward_from_reward_table(table):
    return max((entry.quantity for entry in table.entries))


def get_max_reward_value_by_reward_type(group_reward_id, reward_type_id):
    group_reward = get_group_reward(group_reward_id)
    return get_max_reward_from_tables_with_reward_type(group_reward.tables, reward_type_id)


def get_optimal_player_count_for_table(table):
    table_entries = table.entries
    return next(((reward_entry.playerCount, table_entries[i + 1].playerCount - 1) for i, reward_entry in enumerate(table_entries) if table_entries[i + 1].quantity < reward_entry.quantity), 0)


def get_reward_for_player_count(reward_table, player_count):
    quantity = 0
    for entry in reward_table.entries:
        if entry.playerCount <= player_count:
            quantity = entry.quantity
        else:
            break

    return quantity


def get_minimum_reward_contribution(group_reward_id):
    return get_group_reward(group_reward_id).minimumContribution
