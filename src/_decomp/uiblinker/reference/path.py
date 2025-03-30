#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\reference\path.py
import logging
import textwrap
from uiblinker.reference import UiReference
from uiblinker.reference.validation import Severity, Validation, ValidationError, SURROUNDING_WHITESPACE, EMPTY_PATH, LEADING_SLASH, TRAILING_SLASH
logger = logging.getLogger(__name__)

class UiPathReference(UiReference):

    def __init__(self, path):
        self._path = path
        self._validate_path(path)

    @staticmethod
    def validate_path(path):
        return get_path_validation(path)

    def resolve(self, root):
        element = find_element_by_path(root, self._path)
        if element is not None:
            return [element]
        else:
            return []

    @staticmethod
    def _validate_path(path):
        validation = get_path_validation(path)
        warnings = filter(lambda v: v.severity == Severity.warning, validation)
        if warnings:
            template = '{count} validation warning(s) for path "{path}":\n\n{warnings}'
            warning_messages = '\n\n'.join([ textwrap.fill(w.message, width=80) for w in warnings ])
            logger.warning(template.format(count=len(warnings), path=path, warnings=warning_messages))
        errors = filter(lambda v: v.severity == Severity.error, validation)
        if errors:
            raise ValidationError(path, errors)

    def __str__(self):
        return 'UiPathReference(path={!r})'.format(self._path)


TRAILING_WILDCARD_MSG = 'Ending a path with a wildcard is not a good idea, it will match all elements in the UI tree below the preceding path segment. You should remove the trailing "**" and replace it with a more specific path.'
LEADING_WILDCARD_MSG = 'Redundant wildcard found at the start of the path. All paths have an implicit wildcard at the start, so you don\'t need to add one explicitly. You should remove the leading "**" from the path.'
ADJACENT_WILDCARDS_MSG = 'Multiple wildcards next to each other in the path are redundant and will be effectively merged into a single wildcard. You should replace any instance of "**/**" with "**".'
AGGRESSIVE_WILDCARD_MSG = 'A path that only consists of a wildcard is not a good idea since it will match the entire UI tree. You should define a more specific path.'
TRAILING_WILDCARD = Validation(Severity.warning, 2, TRAILING_WILDCARD_MSG)
LEADING_WILDCARD = Validation(Severity.warning, 3, LEADING_WILDCARD_MSG)
ADJACENT_WILDCARDS = Validation(Severity.warning, 4, ADJACENT_WILDCARDS_MSG)
AGGRESSIVE_WILDCARD = Validation(Severity.warning, 5, AGGRESSIVE_WILDCARD_MSG)
EMPTY_PATH_SEGMENT = Validation(Severity.error, 2, "The path contains an empty segment (i.e. double slashes '//').")
WILDCARD = '**'

def get_path_validation(path):
    validation = set()
    if len(path) != len(path.strip()):
        validation.add(SURROUNDING_WHITESPACE)
        path = path.strip()
    if len(path) == 0:
        validation.add(EMPTY_PATH)
        return validation
    if path.startswith('/'):
        validation.add(LEADING_SLASH)
        path = path[1:]
    if path.endswith('/'):
        validation.add(TRAILING_SLASH)
        path = path[:-1]
    parts = path.split('/')
    if len(parts) == 1 and parts[0].strip() == '':
        validation.add(EMPTY_PATH)
        return validation
    if all((part == WILDCARD for part in parts)):
        validation.add(AGGRESSIVE_WILDCARD)
    elif parts[0] == WILDCARD:
        validation.add(LEADING_WILDCARD)
    elif parts[-1] == WILDCARD:
        validation.add(TRAILING_WILDCARD)
    last_was_wildcard = False
    for part in parts:
        if len(part.strip()) == 0:
            validation.add(EMPTY_PATH_SEGMENT)
        if part == WILDCARD:
            if last_was_wildcard:
                validation.add(ADJACENT_WILDCARDS)
            last_was_wildcard = True
        else:
            last_was_wildcard = False

    return validation


def find_element_by_path(root, ui_element_path):
    return _find_element_by_wildcard_path_list(['**'] + ui_element_path.split('/'), root)


def _find_element_in_children(wildcard_path_list, ui_parent, wildcard_depth):
    for child in getattr(ui_parent, 'children', []):
        find_in_child = _find_element_by_wildcard_path_list(wildcard_path_list, child, wildcard_depth)
        if find_in_child is not None:
            return find_in_child


def _find_element_by_wildcard_path_list(wildcard_path_list, ui_element, wildcard_depth = 0):
    if ui_element is None or wildcard_depth >= len(wildcard_path_list):
        return
    wildcard_sub_path = wildcard_path_list[wildcard_depth]
    if '**' == wildcard_sub_path:
        find_in_child = _find_element_in_children(wildcard_path_list, ui_element, wildcard_depth + 1)
        if find_in_child is not None:
            return find_in_child
        find_in_child = _find_element_in_children(wildcard_path_list, ui_element, wildcard_depth)
        if find_in_child is not None:
            return find_in_child
    elif wildcard_sub_path == unicode(getattr(ui_element, 'name', '')):
        if wildcard_depth == len(wildcard_path_list) - 1:
            return ui_element
        find_in_child = _find_element_in_children(wildcard_path_list, ui_element, wildcard_depth + 1)
        if find_in_child is not None:
            return find_in_child
