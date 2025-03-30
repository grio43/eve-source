#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\loggers\message_bus\windowMessenger.py
import carbonui.const as uiconst
from eveProto.generated.eve_public.app.eveonline.generic_ui.window.analytics_pb2 import Closed as WindowClosed
from eveProto.generated.eve_public.app.eveonline.generic_ui.window.analytics_pb2 import Focused as WindowFocused
from eveProto.generated.eve_public.app.eveonline.generic_ui.window.analytics_pb2 import Opened as WindowOpened
from eveProto.generated.eve_public.app.eveonline.generic_ui.window.analytics_pb2 import Unfocused as WindowUnfocused
from eveProto.generated.eve_public.app.eveonline.generic_ui.window.window_pb2 import DOCKINGMODE_FULLSCREEN, DOCKINGMODE_FLOATING, DOCKINGMODE_LEFT, DOCKINGMODE_RIGHT
from logging import getLogger
DEFAULT_DOCKING_MODE = DOCKINGMODE_FLOATING
DOCKING_MODES_CONVERSION = {uiconst.TOALL: DOCKINGMODE_FULLSCREEN,
 uiconst.TOLEFT: DOCKINGMODE_LEFT,
 uiconst.TORIGHT: DOCKINGMODE_RIGHT,
 uiconst.TOPLEFT: DOCKINGMODE_FLOATING}
logger = getLogger(__name__)

class WindowMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def window_closed(self, window_id, seconds_opened, nanoseconds_opened):
        event = WindowClosed()
        event.window.unique_name = window_id
        event.duration_opened.seconds = seconds_opened
        event.duration_opened.nanos = nanoseconds_opened
        self.public_gateway.publish_event_payload(event)
        self._log_window_event(event, window_id, event_name='CLOSED')

    def window_focused(self, window_id):
        event = WindowFocused()
        event.window.unique_name = window_id
        self.public_gateway.publish_event_payload(event)
        self._log_window_event(event, window_id, event_name='FOCUSED')

    def window_opened(self, window_id, docking_mode = DEFAULT_DOCKING_MODE):
        event = WindowOpened()
        event.window.unique_name = window_id
        event.docking = docking_mode
        self.public_gateway.publish_event_payload(event)
        self._log_window_event(event, window_id, event_name='OPENED')

    def window_unfocused(self, window_id, seconds_focused, nanoseconds_focused):
        event = WindowUnfocused()
        event.window.unique_name = window_id
        event.duration_focused.seconds = seconds_focused
        event.duration_focused.nanos = nanoseconds_focused
        self.public_gateway.publish_event_payload(event)
        self._log_window_event(event, window_id, event_name='UNFOCUSED')

    def _log_window_event(self, event, window_id, event_name):
        logger.info('WINDOW {event_name}: {window_id} ({event_class}). Protobuf:\n {event}'.format(event_class=type(event), window_id=window_id, event=event, event_name=event_name))
