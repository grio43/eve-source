#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\open_on_startup.py
import uthread2
import gametime
from gametime.downtime import get_last_downtime
from eve.common.script.sys.eveCfg import IsDocked
from storylines.client.airnpe import is_air_npe_focused
from jobboard.client.job_board_settings import open_opportunities_on_startup_setting
from jobboard.client.ui.job_board_window import JobBoardWindow
from jobboard.client.feature_flag import open_job_board_on_startup
from jobboard.client.job_board_signals import on_job_board_open_on_startup_changed

class OpenOpportunitiesOnStartup(object):
    __notifyevents__ = ['OnViewStateChanged', 'OnWindowOpened']

    def __init__(self):
        self._registered = False
        self._has_unregistered = False
        on_job_board_open_on_startup_changed.connect(self._on_job_board_open_on_startup_changed)
        self.register()

    def __del__(self):
        on_job_board_open_on_startup_changed.disconnect(self._on_job_board_open_on_startup_changed)
        self.unregister()

    def _on_job_board_open_on_startup_changed(self, *args, **kwargs):
        if self._has_unregistered:
            return
        if open_job_board_on_startup():
            self.register()
        else:
            self.unregister()

    def register(self):
        if not open_job_board_on_startup():
            return
        if not open_opportunities_on_startup_setting.is_enabled():
            return
        if self._has_opened_after_downtime():
            return
        if self._registered:
            return
        self._registered = True
        sm.RegisterNotify(self)
        if IsDocked():
            self._check_open()

    def unregister(self):
        if not self._registered:
            return
        settings.char.ui.Set('open_opportunities_on_startup_timestamp', gametime.GetWallclockTime())
        sm.UnregisterNotify(self)
        self._registered = False
        self._has_unregistered = True

    def OnViewStateChanged(self, from_view, to_view):
        if to_view == 'hangar':
            self._check_open()

    def OnWindowOpened(self, window):
        if window.windowID == JobBoardWindow.default_windowID:
            self.unregister()

    def _job_board_opened(self, *args, **kwargs):
        self.unregister()

    @uthread2.debounce(1)
    def _check_open(self):
        if not session.charid or not open_opportunities_on_startup_setting.is_enabled() or not IsDocked():
            return
        if is_air_npe_focused():
            return
        self.unregister()
        JobBoardWindow.Open(page_id='home')

    def _has_opened_after_downtime(self):
        last_opened = settings.char.ui.Get('open_opportunities_on_startup_timestamp', None)
        if not last_opened:
            return False
        return last_opened > get_last_downtime()
