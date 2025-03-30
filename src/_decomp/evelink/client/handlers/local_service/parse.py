#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evelink\client\handlers\local_service\parse.py
import functools
import sys
import typeutils

def parse(kwargs, **data_types):
    return {k:parse_value(v, get_eval_func(data_types[k])) for k, v in kwargs.iteritems()}


def parse_value(value, eval_func):
    if value is None or value == 'None':
        return
    try:
        if isinstance(value, list):
            return map(eval_func, value)
        return eval_func(value)
    except ValueError:
        raise
    except Exception:
        message = "Failed to parse value '{}'".format(value)
        raise ValueError(message), None, sys.exc_info()[2]


def get_eval_func(data_type):
    return data_type_to_eval_func.get(data_type, data_type)


def fail_on_none(value, eval_func):
    parsed_value = eval_func(value, default=None)
    if parsed_value is None:
        raise ValueError("Failed to parse value '{}'".format(value))
    return parsed_value


data_type_to_eval_func = {int: functools.partial(fail_on_none, eval_func=typeutils.int_eval),
 float: functools.partial(fail_on_none, eval_func=typeutils.float_eval),
 bool: typeutils.bool_eval}

def pre_parse_none(eval_func, value):
    if value is None or value == 'None':
        return
    return eval_func(value)


int_optional = functools.partial(pre_parse_none, data_type_to_eval_func[int])
float_optional = functools.partial(pre_parse_none, data_type_to_eval_func[float])
bool_optional = functools.partial(pre_parse_none, data_type_to_eval_func[bool])
str_optional = functools.partial(pre_parse_none, str)
unicode_optional = functools.partial(pre_parse_none, unicode)
