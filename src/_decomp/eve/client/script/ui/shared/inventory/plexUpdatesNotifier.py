#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\inventory\plexUpdatesNotifier.py
from carbon.common.script.util.timerstuff import AutoTimer
from collections import deque
STOP_TRACKING_AFTER_MS = 10000

class PlexUpdate(object):

    def __init__(self, is_user_move, on_expiry_callback):
        self.is_user_move = is_user_move
        self.on_expiry_callback = on_expiry_callback
        self.start_tracking()

    def start_tracking(self):
        self.expiry_timer = AutoTimer(STOP_TRACKING_AFTER_MS, self.on_expiry_callback)

    def stop_tracking(self):
        self.expiry_timer.KillTimer()


class PlexUpdatesNotifier(object):
    __notifyevents__ = ['OnPlexVaultDepositStarted', 'OnAurumChangeFromVgs']

    def __init__(self, callback):
        self.callback = callback
        self.tracked_updates = deque()
        sm.RegisterNotify(self)

    def on_plex_update_expired(self):
        self.tracked_updates.popleft()

    def OnPlexVaultDepositStarted(self, is_user_move):
        plex_update = PlexUpdate(is_user_move, self.on_plex_update_expired)
        self.tracked_updates.append(plex_update)

    def OnAurumChangeFromVgs(self, change_data):
        balance = int(change_data['balance'])
        if self.tracked_updates:
            next_update = self.tracked_updates.popleft()
            next_update.stop_tracking()
            self.callback(balance, next_update.is_user_move)
