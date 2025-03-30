#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\agencyFilters.py
from copy import copy
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyEventLog
from signals import Signal
import logging
_filters = None
logger = logging.getLogger(__name__)
onFilterChanged = Signal(signalName='onFilterChanged')

def _CheckInitFilters():
    global _filters
    if _filters is None:
        _InitFilters()


def _InitFilters():
    global _filters
    _filters = settings.char.ui.Get('agencyFiltersByContentGroupID', {})


def SetFilterValue(contentGroupID, filterType, value, log = True):
    if GetFilterValue(contentGroupID, filterType) == value:
        return
    _SetFilterValue(contentGroupID, filterType, value, log)
    onFilterChanged(contentGroupID, filterType, value)


def SetFilterValueWithoutEvent(contentGroupID, filterType, value, log = False):
    _SetFilterValue(contentGroupID, filterType, value, log)


def _SetFilterValue(contentGroupID, filterType, value, log):
    _CheckInitFilters()
    _CheckContentGroupExists(contentGroupID)
    _filters[contentGroupID][filterType] = copy(value)
    _PersistFilters()
    if log:
        agencyEventLog.LogEventFilterChanged(contentGroupID, filterType, value)


def _PersistFilters():
    settings.char.ui.Set('agencyFiltersByContentGroupID', _filters)


def GetFilterValue(contentGroupID, filterType):
    _CheckInitFilters()
    if contentGroupID not in _filters:
        _filters[contentGroupID] = {}
    try:
        return copy(_filters[contentGroupID].get(filterType, agencyConst.FILTER_DEFAULTS.get(filterType, None)))
    except KeyError:
        _InitFilters()
        raise


def ResetFilter(contentGroupID, filterType):
    _CheckInitFilters()
    _CheckContentGroupExists(contentGroupID)
    if filterType not in _filters[contentGroupID]:
        return
    SetFilterValue(contentGroupID, filterType, agencyConst.FILTER_DEFAULTS[filterType])


def _CheckContentGroupExists(contentGroupID):
    if contentGroupID not in _filters:
        _filters[contentGroupID] = {}
