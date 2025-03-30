#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithconfig\mcget.py
import datetime as py_datetime
import decimal as py_decimal
import json as py_json
import typeutils
import datetimeutils
import monolithconfig
import logging
log = logging.getLogger(__name__)
_NOT_SUPPLIED = object()

def _groupsplit(key):
    parts = key.split('.', 1)
    if len(parts) == 1:
        return (parts[0], None)
    else:
        return (parts[1], parts[0])


def string(group_and_key, default = u''):
    val = monolithconfig.get_value(*_groupsplit(group_and_key))
    if val is None:
        return default
    return val


def integer(group_and_key, default = 0):
    val = monolithconfig.get_value(*_groupsplit(group_and_key))
    if val is None:
        return default
    return typeutils.int_eval(val, default)


def floating(group_and_key, default = 0.0):
    val = monolithconfig.get_value(*_groupsplit(group_and_key))
    if val is None:
        return default
    return typeutils.float_eval(val, default)


def boolean(group_and_key):
    return typeutils.bool_eval(monolithconfig.get_value(*_groupsplit(group_and_key)))


def datetime(group_and_key, default = None, utc = True):
    val = monolithconfig.get_value(*_groupsplit(group_and_key))
    if val is None:
        return default
    val2 = datetimeutils.any_to_datetime(val, None, utc=utc)
    if val2 is None:
        log.warning(u'parse error in %s: not a valid datetime=%r', group_and_key, val)
        return default
    return val2


def date(group_and_key, default = None, utc = True):
    val = monolithconfig.get_value(*_groupsplit(group_and_key))
    if val is None:
        return default
    val2 = datetimeutils.any_to_datetime(val, None, utc=utc)
    if val2 is None:
        log.warning(u'parse error in %s: not a valid date=%r', group_and_key, val)
        return default
    return val2.date()


def time(group_and_key, default = None, utc = True):
    val = monolithconfig.get_value(*_groupsplit(group_and_key))
    if val is None:
        return default
    val2 = datetimeutils.any_to_datetime(val, None, utc=utc)
    if val2 is None:
        log.warning(u'parse error in %s: not a valid time=%r', group_and_key, val)
        return default
    return val2.time()


def timedelta(group_and_key, default = _NOT_SUPPLIED):
    if default == _NOT_SUPPLIED:
        default = py_datetime.timedelta()
    val = monolithconfig.get_value(*_groupsplit(group_and_key))
    if val is None:
        return default
    val2 = datetimeutils.str_to_timedelta(val, None)
    if val2 is None:
        log.warning(u'parse error in %s: not a valid timedelta=%r', group_and_key, val)
        return default
    return val2


def decimal(group_and_key, default = _NOT_SUPPLIED):
    if default == _NOT_SUPPLIED:
        default = py_decimal.Decimal()
    val = monolithconfig.get_value(*_groupsplit(group_and_key))
    if val is None:
        return default
    try:
        return py_decimal.Decimal(val)
    except Exception as ex:
        log.warning(u'parse error in %s: not a valid decimal=%r', group_and_key, ex)
        return default


def jsondict(group_and_key, default = _NOT_SUPPLIED):
    if default == _NOT_SUPPLIED:
        default = {}
    val = monolithconfig.get_value(*_groupsplit(group_and_key))
    if val is None:
        return default
    try:
        data = py_json.loads(val)
        if not isinstance(data, dict):
            log.warning(u'value error in %s: not a dict=%r', group_and_key, data)
            return default
        return data
    except Exception as ex:
        log.warning(u'json parse error in %s: %r', group_and_key, ex)
        return default


def jsonlist(group_and_key, default = _NOT_SUPPLIED):
    if default == _NOT_SUPPLIED:
        default = []
    val = monolithconfig.get_value(*_groupsplit(group_and_key))
    if val is None:
        return default
    try:
        data = py_json.loads(val)
        if not isinstance(data, list):
            log.warning(u'value error in %s: not a list=%r', group_and_key, data)
            return default
        return data
    except Exception as ex:
        log.warning(u'json parse error in %s: %r', group_and_key, ex)
        return default
