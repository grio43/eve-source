#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\reference\ui_name.py
import logging
import textwrap
from uiblinker import UiReference, iter_element_tree, Severity, ValidationError
from uiblinker.reference.validation import SURROUNDING_WHITESPACE, EMPTY_PATH, LEADING_SLASH, TRAILING_SLASH
from uihighlighting.uniqueNameChains import FindChainForUniqueName
logger = logging.getLogger(__name__)

class UniqueNameReference(UiReference):

    def __init__(self, unique_name, chain_blinks = False):
        self._unique_name = unique_name
        self._chain_blinks = chain_blinks
        self._validate_path(unique_name)

    def resolve(self, root):
        chain_elements = find_element_by_name(root, self._unique_name, self._chain_blinks)
        return chain_elements

    def __str__(self):
        return 'UniqueNameReference(path={!r})'.format(self._unique_name)

    @staticmethod
    def validate_path(name):
        return get_name_validation(name)

    @staticmethod
    def _validate_path(name):
        validation = get_name_validation(name)
        warnings = filter(lambda v: v.severity == Severity.warning, validation)
        if warnings:
            template = '{count} validation warning(s) for name "{name}":\n\n{warnings}'
            warning_messages = '\n\n'.join([ textwrap.fill(w.message, width=80) for w in warnings ])
            logger.warning(template.format(count=len(warnings), name=name, warnings=warning_messages))
        errors = filter(lambda v: v.severity == Severity.error, validation)
        if errors:
            raise ValidationError(name, errors)


def get_name_validation(name):
    validation = set()
    if len(name) != len(name.strip()):
        validation.add(SURROUNDING_WHITESPACE)
        name = name.strip()
    if len(name) == 0:
        validation.add(EMPTY_PATH)
        return validation
    if name.startswith('/'):
        validation.add(LEADING_SLASH)
        name = name[1:]
    if name.endswith('/'):
        validation.add(TRAILING_SLASH)
        name = name[:-1]
    return validation


def find_element_by_name(root, unique_name, chain_blinks):
    if chain_blinks:
        chain = FindChainForUniqueName(unique_name)
    else:
        chain = [unique_name]
    chain_elements = find_element_by_chain(root, chain, False)
    return chain_elements


def find_element_by_chain(root, chain_list, should_exclude_invisible = False):
    found_elements = []
    for eachName in chain_list:
        for eachChild in iter_element_tree(root):
            if getattr(eachChild, 'uniqueUiName', None) == eachName:
                if getattr(eachChild, 'display', False) or not should_exclude_invisible:
                    found_elements.append(eachChild)
                    break

    return found_elements
