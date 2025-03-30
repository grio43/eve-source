#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\heronotification\service.py
import collections
import uthread2
from carbon.common.script.sys.service import Service
from carbonui.uianimations import animations
from eve.client.script.ui.heronotification.cancel import CancellationToken
from eve.client.script.ui.heronotification.layer import HeroNotificationLayer
from eve.client.script.ui.heronotification.player import HeroNotificationPlayer

class HeroNotificationService(Service):
    __guid__ = 'svc.heroNotification'
    __servicename__ = 'heroNotification'

    def __init__(self):
        self._active = None
        self._active_priority = 0
        self._layer = None
        self._queue = []
        self._queue_monitor_tasklet = None
        self._visible = True
        super(HeroNotificationService, self).__init__()

    def play(self, hero_notification, priority = 0):
        self._prepare_layer()
        cancellation_token = CancellationToken()
        if self._active is not None and not self._active.done:
            self._add_to_queue(hero_notification, priority, cancellation_token)
        else:
            self._play_hero_notification(hero_notification, priority, cancellation_token)
        return cancellation_token

    def show_notifications(self, animate = True):
        if not self._visible:
            self._visible = True
            self._update_layer_opacity(animate)

    def hide_notifications(self, animate = True):
        if self._visible:
            self._visible = False
            self._update_layer_opacity(animate)

    def _add_to_queue(self, hero_notification, priority, cancellation_token):
        if self._active is not None and self._active_priority < priority:
            self._active.cancel()
        self._queue.append(QueueEntry(priority, hero_notification, cancellation_token))
        self._start_queue_monitor_maybe()
        return cancellation_token

    def _start_queue_monitor_maybe(self):
        if self._queue_monitor_tasklet is None:
            self._queue_monitor_tasklet = uthread2.start_tasklet(self._monitor_queue)

    def _monitor_queue(self):
        try:
            while len(self._queue) > 0:
                if self._active is not None:
                    self._active.wait()
                self._queue = sorted(self._queue, key=lambda e: e.priority or 0)
                entry = self._queue.pop(-1)
                if entry.cancellation_token.cancelled:
                    continue
                self._play_hero_notification(hero_notification=entry.hero_notification, priority=entry.priority, cancellation_token=entry.cancellation_token)

        finally:
            self._queue_monitor_tasklet = None

    def _play_hero_notification(self, hero_notification, priority, cancellation_token):
        self._layer.cleanup()
        self._active_priority = priority
        self._active = HeroNotificationPlayer(hero_notification, container=self._layer.create_hero_notification_container(), cancellation_token=cancellation_token)
        self._active.start()

    def _get_layer_opacity(self):
        if self._visible:
            return 1.0
        return 0.0

    def _prepare_layer(self):
        if self._layer is not None and self._layer.destroyed:
            self._layer = None
        if self._layer is None:
            self._layer = HeroNotificationLayer(opacity=self._get_layer_opacity())

    def _update_layer_opacity(self, animate = True):
        if self._layer is not None:
            if animate:
                animations.FadeTo(self._layer, startVal=self._layer.opacity, endVal=self._get_layer_opacity(), duration=0.5)
            else:
                self._layer.opacity = self._get_layer_opacity()


QueueEntry = collections.namedtuple('QueueEntry', ['priority', 'hero_notification', 'cancellation_token'])
