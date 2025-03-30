#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\__init__.py
from .blinker import BlinkerType
from .reference import UiReference
from .reference.element import ElementReference
from .reference.path import UiPathReference, find_element_by_path
from uiblinker.reference.validation import Severity, ValidationError
from .reference.util import iter_element_tree
from .service import get_service

def start(reference, blinker_type, group = None):
    return get_service().start_blinker(reference, blinker_type, group)


def start_box(reference, group = None):
    return start(reference, blinker_type=BlinkerType.box, group=group)


def start_ring(reference, group = None):
    return start(reference, blinker_type=BlinkerType.ring, group=group)


def stop_all_in_group(group):
    get_service().stop_all_blinkers_in_group(group)
