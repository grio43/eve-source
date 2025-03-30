#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\util\observerNotifier.py


class ObserverNotifier(object):

    def __init__(self):
        self.subscribers = {}

    def get_value(self):
        raise NotImplementedError('Must implement ObserverNotifier::get_value in derived class')

    def start_updates(self):
        raise NotImplementedError('Must implement ObserverNotifier::start_updates in derived class')

    def stop_updates(self):
        raise NotImplementedError('Must implement ObserverNotifier::stop_updates in derived class')

    def register_subscriber(self, subscriber, callback):
        if subscriber not in self.subscribers:
            self.subscribers[subscriber] = callback
            self._notify_subscriber(subscriber, self.get_value())
            self.start_updates()

    def unregister_subscriber(self, subscriber):
        if subscriber in self.subscribers:
            del self.subscribers[subscriber]
        if not self.subscribers:
            self.stop_updates()

    def _notify_subscribers(self, update):
        all_subscribers = self.subscribers.copy()
        for subscriber in all_subscribers:
            self._notify_subscriber(subscriber, update)

    def _notify_subscriber(self, subscriber, update):
        if not subscriber or getattr(subscriber, 'destroyed', False):
            self.unregister_subscriber(subscriber)
        elif subscriber in self.subscribers:
            self.subscribers[subscriber](update)
