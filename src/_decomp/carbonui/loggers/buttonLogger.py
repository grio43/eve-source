#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\loggers\buttonLogger.py
from eveexceptions.exceptionEater import EatsExceptions
from carbonui.loggers.message_bus.buttonMessenger import ButtonMessenger
import logging
logLite = logging.getLogger(__name__)

def collect_context(ui_object):
    context_parts = []
    parent = ui_object.parent
    while parent is not None:
        context = getattr(parent, 'analyticID', None)
        if context:
            context_parts.append(context)
        parent = parent.parent

    return '.'.join(reversed(context_parts))


@EatsExceptions('protoClientLogs')
def log_button_clicked(button_object):
    if not button_object.analyticID:
        return False
    unique_name = getattr(button_object, 'analyticID', None)
    hierarchy_path = collect_context(button_object)
    if not hierarchy_path:
        raise ValueError('hierarchy path is empty, resulting in an invalid message.')
    message_bus = ButtonMessenger(sm.GetService('publicGatewaySvc'))
    message_bus.button_clicked(hierarchy_path, unique_name)
    logLite.info('Tracked button pressed; analyticID: %s' % unique_name)
