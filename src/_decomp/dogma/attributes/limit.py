#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\attributes\limit.py
import collections
LIMIT_WINDOW_LENGTH = 20

def LimitAttributeOnItem(item, timestamp, limiting_attribute_id, value):
    discarded_value = 0
    if item is None:
        return (value, discarded_value)
    limit_per_second = item.GetValue(limiting_attribute_id)
    if not limit_per_second:
        return (value, discarded_value)
    history = _GetHistory(item, limiting_attribute_id)
    return _AccumulateValueWithinRollingLimit(history, timestamp, limit_per_second, value)


def GetAccumulatedAttributeOnItem(item, timestamp, limiting_attribute_id):
    if item:
        history = _GetHistory(item, limiting_attribute_id)
        return _GetAccumulatedValue(history, timestamp)


def _GetHistory(item, limiting_attribute_id):
    try:
        return item.rollingHistory[limiting_attribute_id]
    except AttributeError:
        item.rollingHistory = collections.defaultdict(collections.OrderedDict)
        return item.rollingHistory[limiting_attribute_id]


def _AccumulateValueWithinRollingLimit(history, timestamp, limit_per_second, value):
    discarded_value = 0
    if not limit_per_second or not value:
        return (value, discarded_value)
    current_accumulated_value = _GetAccumulatedValue(history, timestamp)
    max_allowed_accumulated_value = limit_per_second * LIMIT_WINDOW_LENGTH
    value_to_add = min(value, max(max_allowed_accumulated_value - current_accumulated_value, 0))
    discarded_value = max(0, value - value_to_add)
    if value_to_add == 0:
        return (0, discarded_value)
    history[int(timestamp)] = value_to_add + history.get(int(timestamp), 0)
    return (value_to_add, discarded_value)


def _GetAccumulatedValue(history, timestamp):
    oldest = int(timestamp) - LIMIT_WINDOW_LENGTH
    for key in history.keys():
        if key < oldest:
            del history[key]
        else:
            break

    return sum(history.itervalues())
