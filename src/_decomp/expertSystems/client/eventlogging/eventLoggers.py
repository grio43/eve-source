#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\eventlogging\eventLoggers.py
from eveexceptions.exceptionEater import ExceptionEater
from expertSystems.client.eventlogging.events import BaseEventLogger, Event
from uthread2 import StartTasklet
from journey.tracker import get_journey_id

class EventLogsLogger(BaseEventLogger):
    PARAMETER_ORDER = ['journeyID']

    def _get_parameters(self, data):
        data['journeyID'] = get_journey_id()
        return sorted(zip(data.keys(), data.values()), key=lambda x: self.PARAMETER_ORDER.index(x[0]))

    def _log_event(self, event, data):
        with ExceptionEater('eventLog'):
            event_category = 'expertSystems'
            parameters = self._get_parameters(data)
            columns = [ column for column, value in parameters ]
            values = [ value for column, value in parameters ]
            StartTasklet(sm.ProxySvc('eventLog').LogClientEvent, event_category, columns, event, *values)


class ExternalQueueLogger(BaseEventLogger):
    SUPPORTED_EVENTS = [Event.STORE_BUTTON_CLICKED]
    PARAMETER_ORDER = ['user_id', 'character_id']

    def _get_parameters(self, data):
        data['user_id'] = session.userid
        data['character_id'] = session.charid
        return sorted(zip(data.keys(), data.values()), key=lambda x: self.PARAMETER_ORDER.index(x[0]))

    def _log_event(self, event, data):
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
