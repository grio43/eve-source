#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fastcheckout\client\eventlogging\eventLoggers.py
from eveexceptions.exceptionEater import ExceptionEater
from fastcheckout.client.eventlogging.events import BaseEventLogger, Event
from journey.tracker import get_journey_id
from uthread2 import StartTasklet

class EventLogsLogger(BaseEventLogger):
    PARAMETER_ORDER = ['commodity',
     'amount',
     'offerID',
     'offerIDs',
     'context',
     'purchase_trace_id',
     'journey_id',
     'has_fast_checkout',
     'error']

    def _get_category(self, event):
        if event == Event.BUY_PLEX_CLICKED:
            return 'monetization'
        return 'fastcheckout'

    def _get_parameters(self, data):
        data['commodity'] = 'plex'
        data['purchase_trace_id'] = sm.GetService('fastCheckoutClientService').get_purchase_trace_id()
        data['journey_id'] = get_journey_id()
        return sorted(zip(data.keys(), data.values()), key=lambda x: self.PARAMETER_ORDER.index(x[0]))

    def _log_event(self, event, data, *args):
        with ExceptionEater('eventLog'):
            event_category = self._get_category(event)
            parameters = self._get_parameters(data)
            columns = [ column for column, value in parameters ]
            values = [ value for column, value in parameters ]
            StartTasklet(sm.ProxySvc('eventLog').LogClientEvent, event_category, columns, event, *values)


class ExternalQueueLogger(BaseEventLogger):
    SUPPORTED_EVENTS = [Event.BUY_PLEX_CLICKED,
     Event.BUY_PLEX_IN_GAME_STARTED,
     Event.BUY_PLEX_IN_WEB_STARTED,
     Event.OFFERS_RECEIVED,
     Event.OFFERS_RETRIEVAL_FAILED,
     Event.OFFER_SELECTED,
     Event.PASSWORD_ENTER_CANCELLED,
     Event.PASSWORD_RESET_REQUESTED,
     Event.PASSWORD_ENTERED,
     Event.PURCHASE_CONFIRMED,
     Event.PURCHASE_NEEDS_WEB_CONFIRMATION,
     Event.PURCHASE_ERROR]
    PARAMETER_ORDER = ['user_id',
     'character_id',
     'purchase_trace_id',
     'context',
     'offerIDs',
     'offerID',
     'amount',
     'has_fast_checkout',
     'error']

    def _get_parameters(self, data):
        data['user_id'] = session.userid
        data['character_id'] = session.charid
        data['purchase_trace_id'] = sm.GetService('fastCheckoutClientService').get_purchase_trace_id()
        return sorted(zip(data.keys(), data.values()), key=lambda x: self.PARAMETER_ORDER.index(x[0]))

    def _log_event(self, event, data, *args):
        with ExceptionEater('externalQueueLog'):
            if event not in self.SUPPORTED_EVENTS:
                return
            parameters = self._get_parameters(data)
            values = [ value for column, value in parameters ]


class MultiEventLogger(BaseEventLogger):

    def __init__(self):
        self.loggers = [EventLogsLogger(), ExternalQueueLogger()]

    def __getattribute__(self, name):
        if name == 'loggers':
            return super(MultiEventLogger, self).__getattribute__(name)

        def apply_on_all_loggers(*args, **kwargs):
            for logger in self.loggers:
                getattr(logger, name)(*args, **kwargs)

        return apply_on_all_loggers


event_logger = MultiEventLogger()
