#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\ClientLogger.py
import uthread2
from eveexceptions.exceptionEater import ExceptionEater
EVENT_GET_TUTORIAL_TASK = 'get_tutorial_task'

def _log_client_event(event, columns, *args):
    with ExceptionEater('eventLog'):
        uthread2.StartTasklet(sm.ProxySvc('eventLog').LogClientEvent, 'projectdiscovery', columns, event, *args)


def log_tutorial_task_loaded(finished_tutorial, task_id):
    _log_client_event(EVENT_GET_TUTORIAL_TASK, ['task_id', 'finished_tutorial'], task_id, finished_tutorial)
