#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\subtitles\format.py
import re
from nodegraph.subtitles import get_entity_name_getter
ENTITY_NAMES_PATTERN = re.compile('\\{(\\w+):(\\w+)\\}')
PARAMS_PATTERN = re.compile('\\{(\\w+)\\}')
PARAMS_WITH_FALLBACK_PATTERN = re.compile('\\{(.+\\?.+)\\}')

def format(fmt_string, **kwargs):
    try:
        string_result = str(fmt_string)
        string_result = _format_entity_names(string_result, **kwargs)
        string_result = _format_params(string_result, **kwargs)
        return string_result
    except Exception:
        pass

    return fmt_string


def _format_entity_names(fmt_string, **kwargs):
    names_by_pattern = {}
    for m in ENTITY_NAMES_PATTERN.finditer(fmt_string):
        _process_entity_match(m, names_by_pattern, **kwargs)

    for pattern, name in names_by_pattern.iteritems():
        fmt_string = re.sub(pattern, name, fmt_string)

    return fmt_string


def _format_params(fmt_string, **kwargs):
    fmt_string = _format_fallback_expressions(fmt_string, **kwargs)
    params = set()
    for m in PARAMS_PATTERN.finditer(fmt_string):
        params.add(m.group(1))

    for param in params:
        if param in kwargs:
            pattern = '\\{{{}\\}}'.format(param)
            fmt_string = re.sub(pattern, str(kwargs[param]), fmt_string)

    return fmt_string


def _format_fallback_expressions(fmt_string, **kwargs):
    expressions = set()
    for m in PARAMS_WITH_FALLBACK_PATTERN.finditer(fmt_string):
        expressions.add(m.group(1))

    for expression in expressions:
        first, fallback = expression.split('?')
        pattern = '\\{{{}\\?{}\\}}'.format(first, fallback)
        if first in kwargs:
            fmt_string = re.sub(pattern, str(kwargs[first]), fmt_string)
        else:
            fmt_string = re.sub(pattern, fallback, fmt_string)

    return fmt_string


def _process_entity_match(m, names_by_pattern, **kwargs):
    entity = m.group(1)
    param = m.group(2)
    getter = get_entity_name_getter(entity)
    if getter and param in kwargs:
        name = getter(kwargs[param])
        if name:
            pattern = '\\{{{}:{}\\}}'.format(entity, param)
            names_by_pattern[pattern] = name
