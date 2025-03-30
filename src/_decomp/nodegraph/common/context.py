#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\context.py
from collections import OrderedDict
import signals
import threadutils

class Blackboard(object):

    def __init__(self):
        self._values = OrderedDict()
        self._messenger = signals.Messenger()

    @property
    def values(self):
        return self._values

    def get_value(self, key, default = None):
        return self._values.get(key, default)

    def set_values(self, **kwargs):
        for key in kwargs:
            self.update(key, kwargs[key])

    def set_default_values(self, **kwargs):
        for key in kwargs:
            if self._values.get(key, None) is None:
                self.update(key, kwargs[key])

    def __contains__(self, key):
        return key in self._values

    def update(self, key, value = None, force_update = False):
        old_value = self._values.get(key, None)
        if not force_update and key in self._values and old_value == value:
            return
        self._values[key] = value
        self._send_message(key, value, old_value)

    @threadutils.threaded
    def _send_message(self, key, value, old_value):
        self._messenger.SendMessage('all', key=key, value=value, old_value=old_value)
        self._messenger.SendMessage(key, key=key, value=value, old_value=old_value)

    def remove(self, key):
        self.update(key, value=None)
        self._values.pop(key)

    def subscribe(self, key, callback):
        self._messenger.SubscribeToMessage(key, callback)

    def unsubscribe(self, key, callback):
        self._messenger.UnsubscribeFromMessage(key, callback)

    def subscribe_to_all(self, callback):
        self._messenger.SubscribeToMessage('all', callback)

    def unsubscribe_from_all(self, callback):
        self._messenger.UnsubscribeFromMessage('all', callback)

    def clear(self):
        self._messenger.Clear()
        self._values.clear()


class NodeGraphContext(object):

    def __init__(self, blackboard = None, messenger = None):
        self._blackboard = blackboard or Blackboard()
        self._messenger = messenger or signals.Messenger()

    @property
    def values(self):
        return self._blackboard.values

    def get_value(self, key, default = None):
        return self._blackboard.get_value(key, default)

    def set_values(self, **kwargs):
        self._blackboard.set_values(**kwargs)

    def set_default_values(self, **kwargs):
        self._blackboard.set_default_values(**kwargs)

    def update_value(self, key, value = None, force_update = False):
        self._blackboard.update(key, value, force_update)

    def subscribe_to_value(self, key, handler):
        self._blackboard.subscribe(key, handler)

    def unsubscribe_from_value(self, key, handler):
        self._blackboard.unsubscribe(key, handler)

    def subscribe_to_all_values(self, handler):
        self._blackboard.subscribe_to_all(handler)

    def unsubscribe_from_all_values(self, handler):
        self._blackboard.unsubscribe_from_all(handler)

    def send_message(self, key, value = None, **kwargs):
        self._messenger.SendMessage(key, key=key, value=value, **kwargs)

    def subscribe_to_message(self, key, handler):
        self._messenger.SubscribeToMessage(key, handler)

    def unsubscribe_from_message(self, key, handler):
        self._messenger.UnsubscribeFromMessage(key, handler)

    def add_message_handlers(self, message_handlers):
        for message_name, handler in message_handlers.iteritems():
            self._messenger.SubscribeToMessage(message_name, handler)

    def clear(self):
        self._messenger.Clear()
        self._blackboard.clear()
