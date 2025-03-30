#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\corpStructureFilters.py
from eve.client.script.ui.cosmetics.structure.paintToolSignals import on_structure_filters_changed
STRUCTURE_TYPE_FILTER = None
STRUCTURE_TEXT_FILTER = ''

def set_structure_type_filter(value, notify = True):
    global STRUCTURE_TYPE_FILTER
    if value != STRUCTURE_TYPE_FILTER:
        STRUCTURE_TYPE_FILTER = value
        if notify:
            on_structure_filters_changed()


def set_structure_text_filter(value, notify = True):
    global STRUCTURE_TEXT_FILTER
    if value != STRUCTURE_TEXT_FILTER:
        STRUCTURE_TEXT_FILTER = value
        if notify:
            on_structure_filters_changed()


def get_filters():
    return (STRUCTURE_TYPE_FILTER, STRUCTURE_TEXT_FILTER)
