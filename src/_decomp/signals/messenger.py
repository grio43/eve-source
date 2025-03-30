#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\signals\messenger.py
from signals.signal import Signal
import collections

class Messenger(object):

    def __init__(self):
        self.signals = collections.defaultdict(Signal)

    def SendMessage(self, signalName_, *args, **kwargs):
        signal = self.signals.get(signalName_)
        if signal:
            signal(*args, **kwargs)

    def SubscribeToMessage(self, name, handler):
        self.signals[name].connect(handler)

    def UnsubscribeFromMessage(self, name, handler):
        self.signals[name].disconnect(handler)

    def UnsubscribeAllFromMessage(self, name):
        self.signals[name].clear()

    def Clear(self):
        self.signals.clear()
