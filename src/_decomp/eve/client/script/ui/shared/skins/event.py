#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\skins\event.py
from eveexceptions.exceptionEater import ExceptionEater
import uthread
CONTEXT_UNKNOWN = 'Unknown'

def LogBuySkinAur(shipTypeID, materialID, context = None):
    context = context or CONTEXT_UNKNOWN
    _LogEvent(['shipTypeID', 'materialID', 'context'], 'BuySkinAur', shipTypeID, materialID, context)


def LogBuySkinIsk(shipTypeID, materialID, context = None):
    context = context or CONTEXT_UNKNOWN
    _LogEvent(['shipTypeID', 'materialID', 'context'], 'BuySkinIsk', shipTypeID, materialID, context)


def _LogEvent(columnNames, eventName, *args):
    with ExceptionEater('eventLog'):
        uthread.new(sm.ProxySvc('eventLog').LogClientEvent, 'shipskins', columnNames, eventName, *args)
