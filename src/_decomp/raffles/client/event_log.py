#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\event_log.py
from eveexceptions import ExceptionEater
import threadutils

def refresh_browse(grab, filters, constraints):
    _log('RefreshBrowse', ['raffleID',
     'typeID',
     'groupID',
     'solarSystemID',
     'minTicketPrice',
     'maxTicketPrice',
     'minTicketCount',
     'maxTicketCount'], ','.join([ raffle.raffle_id for raffle in grab ]), _get_from_dict('type_id', filters), _get_from_dict('group_id', filters), _get_from_dict('solar_system_id', filters), _get_from_dict('min_ticket_price', constraints), _get_from_dict('max_ticket_price', constraints), _get_from_dict('min_ticket_count', constraints), _get_from_dict('max_ticket_count', constraints))


def _get_from_dict(key, dict):
    if dict:
        return dict.get(key)


@threadutils.threaded
def _log(event, columns, *args):
    with ExceptionEater('eventLog'):
        sm.ProxySvc('eventLog').LogClientEvent('raffles', columns, event, *args)
