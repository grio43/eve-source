#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\common\componentmessenger.py
from collections import defaultdict
import logging
import signals
log = logging.getLogger(__name__)

class ComponentMessenger(object):

    def __init__(self):
        self.subscriptions = defaultdict(lambda : defaultdict(signals.Signal))

    def SubscribeToItemMessage(self, itemID, messageName, messageHandler):
        self.subscriptions[itemID][messageName].connect(messageHandler)

    def SendMessageToItem(self, itemID, messageName, *args, **kwargs):
        subscribedMessages = self.subscriptions.get(itemID)
        if subscribedMessages:
            signaler = subscribedMessages.get(messageName)
            if signaler:
                signaler(*args, **kwargs)

    def SendMessageToAllItems(self, messageName, *args, **kwargs):
        for itemID, subscribedMessages in self.subscriptions.iteritems():
            signaler = subscribedMessages.get(messageName)
            if signaler:
                signaler(*args, **kwargs)

    def DeleteSubscriptionsForItem(self, itemID):
        try:
            del self.subscriptions[itemID]
        except KeyError:
            pass

    def UnsubscribeFromItemMessage(self, itemID, messageName, messageHandler):
        try:
            self.subscriptions[itemID][messageName].disconnect(messageHandler)
        except (ValueError, KeyError):
            pass
