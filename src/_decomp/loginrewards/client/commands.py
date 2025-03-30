#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\loginrewards\client\commands.py
from eve.client.script.ui.shared.pointerTool.pointerToolConst import GetUniqueNeocomPointerName
from neocom2.btnIDs import LOGIN_REWARDS_ID
from uthread2 import call_after_wallclocktime_delay
BLINKER_DURATION_SECONDS = 10

class BlinkLoginRewardWindowOnDock(object):
    __notifyevents__ = ['OnViewStateChanged', 'OnLoginRewardWindowOpened']

    def __init__(self):
        self.is_enabled = False
        self.blinker = None

    def enable(self):
        if self.is_enabled:
            return
        sm.RegisterNotify(self)
        self.is_enabled = True

    def disable(self):
        if not self.is_enabled:
            return
        sm.UnregisterNotify(self)
        self._stop_blinker()
        self.is_enabled = False

    def OnViewStateChanged(self, from_view, to_view):
        if to_view == 'hangar':
            self._start_blinker()

    def OnLoginRewardWindowOpened(self):
        self.disable()

    def _start_blinker(self):
        if self.blinker:
            return
        neocom_button_name = GetUniqueNeocomPointerName(LOGIN_REWARDS_ID)
        self.blinker = sm.GetService('ui_blinker').start_unique_name_blinker(neocom_button_name)
        call_after_wallclocktime_delay(tasklet_func=self.disable, delay=BLINKER_DURATION_SECONDS)

    def _stop_blinker(self):
        if self.blinker:
            self.blinker.stop()
            self.blinker = None
