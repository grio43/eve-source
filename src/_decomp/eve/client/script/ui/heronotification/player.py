#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\heronotification\player.py
import uthread
from stacklesslib.locks import NLCondition

class HeroNotificationPlayer(object):

    class _State(object):
        INIT = 1
        PLAYING = 2
        DONE = 3

    def __init__(self, hero_notification, container, cancellation_token):
        self._hero_notification = hero_notification
        self._container = container
        self._state = self._State.INIT
        self._tasklet = None
        self._cancellation_token = cancellation_token
        self._done_condition = NLCondition()

    @property
    def done(self):
        return self._state == self._State.DONE

    def start(self):
        if self._state == self._State.INIT:
            if self._cancellation_token.cancelled:
                self._to_done()
            else:
                self._state = self._State.PLAYING
                self._tasklet = uthread.new(self._play_hero_notification)

    def cancel(self):
        self._cancellation_token.cancel()

    def wait(self, timeout = None):
        if not self.done:
            self._done_condition.wait(timeout)

    def _play_hero_notification(self):
        try:
            self._hero_notification(self._container, self._cancellation_token)
        finally:
            self._to_done()
            self._tasklet = None
            self._container.Close()
            self._container = None

    def _to_done(self):
        self._state = self._State.DONE
        self._done_condition.notify_all()
