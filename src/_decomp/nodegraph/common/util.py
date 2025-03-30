#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\util.py
from ast import literal_eval
from logging import getLogger
logger = getLogger(__name__)
operator_functions = {'greaterThan': lambda a, b: a > b,
 'lessThan': lambda a, b: a < b,
 'equalTo': lambda a, b: a == b,
 'notEqualTo': lambda a, b: a != b,
 'in': lambda a, b: a in (b or []),
 'notIn': lambda a, b: a not in (b or []),
 'greaterThanOrEqual': lambda a, b: a >= b,
 'lessThanOrEqual': lambda a, b: a <= b}

def get_operator_function(operator):
    return operator_functions[operator or 'equalTo']


def _get_evaluated_value(value):
    try:
        evaluated_value = literal_eval(value)
    except (SyntaxError, ValueError):
        try:
            evaluated_value = literal_eval(str(value))
        except (SyntaxError, ValueError) as exc:
            if isinstance(value, str):
                return value
            raise exc

    if isinstance(evaluated_value, list):
        return [ _get_evaluated_value(element) for element in evaluated_value ]
    if isinstance(evaluated_value, dict):
        return {_get_evaluated_value(k):_get_evaluated_value(v) for k, v in evaluated_value.items()}
    return evaluated_value


def _try_to_cast_to_iterable(value):
    is_string = isinstance(value, (str, unicode))
    is_string_list = is_string and value.startswith('[') and value.endswith(']')
    is_string_dict = is_string and value.startswith('{') and value.endswith('}')
    if is_string_list or is_string_dict:
        try:
            return literal_eval(value)
        except:
            pass

    return value


def _cast_to_the_other_type_if_possible(value, other_value):
    if isinstance(other_value, bool):
        return bool(value)
    if isinstance(other_value, unicode):
        return unicode(value)
    return value


def _correct_for_special_types(value_a, value_b):
    value_a = None if value_a == 'None' else value_a
    value_b = None if value_b == 'None' else value_b
    trues = [1,
     '1',
     'True',
     True]
    falses = [0,
     '0',
     'False',
     False]
    bools = trues + falses
    if value_a in bools and value_b in bools:
        value_a = value_a in trues
        value_b = value_b in trues
    return (value_a, value_b)


def _cast_to_unicode(value):
    if isinstance(value, list):
        return [ unicode(element) for element in value ]
    if isinstance(value, dict):
        return {unicode(k):unicode(v) for k, v in value.items()}
    return unicode(value)


def compare_values(value_a = None, value_b = None, operator = None, flipped = False):
    value_a, value_b = _correct_for_special_types(value_a, value_b)
    if None not in (value_a, value_b):
        value_a = _try_to_cast_to_iterable(value_a)
        value_b = _try_to_cast_to_iterable(value_b)
        value_a = _cast_to_the_other_type_if_possible(value_a, value_b)
        value_b = _cast_to_the_other_type_if_possible(value_b, value_a)
        if type(value_a) != type(value_b):
            value_a_eval = _get_evaluated_value(value_a)
            value_a_type = type(value_a_eval)
            try:
                value_a = value_a_type(value_a)
                value_b = value_a_type(value_b)
            except (TypeError, ValueError):
                value_a = value_a_eval
                value_b = _get_evaluated_value(value_b)

    try:
        if flipped:
            value_a, value_b = value_b, value_a
        operator_func = get_operator_function(operator)
        return operator_func(value_a, value_b)
    except Exception as e:
        logger.exception(u'Compare values failed to validate, returning False.\n\n            value_a={value_a} ({type_a}), value_b={value_b} ({type_b}), operator={operator}\n\n            ERROR: {e}'.format(value_a=value_a, type_a=type(value_a), value_b=value_b, type_b=type(value_b), operator=operator, e=e))
        return False


def get_object_predicate(key, value):

    def predicate(item):
        return getattr(item, key, None) == value

    return predicate


def get_object_in_list_predicate(key, value_list):

    def predicate(item):
        return getattr(item, key, None) in value_list

    return predicate


def get_object_value_by_path(object, path, default_value = None):
    if isinstance(path, basestring):
        if len(path):
            keys = path.split('.')
        else:
            keys = []
    elif isinstance(path, (list, tuple)):
        keys = path
    else:
        keys = [path]
    result = object
    for key in keys:
        try:
            if isinstance(result, dict):
                result = result.get(key, default_value)
            elif isinstance(result, (list, tuple)):
                result = result[int(key)]
            else:
                result = getattr(result, key, default_value)
        except:
            return default_value

    return result


def set_object_value_by_path(object, path, value):
    if isinstance(path, basestring):
        if len(path):
            keys = path.split('.')
        else:
            keys = []
    elif isinstance(path, (list, tuple)):
        keys = path
    else:
        keys = [path]
    result = object
    if result is None:
        result = {}
    current_object = result
    for key in keys[:-1]:
        try:
            key = int(key)
        except:
            pass

        if key not in current_object:
            current_object[key] = {}
        current_object = current_object[key]

    last_key = keys[-1]
    try:
        last_key = int(last_key)
    except:
        pass

    current_object[last_key] = value
    return result
