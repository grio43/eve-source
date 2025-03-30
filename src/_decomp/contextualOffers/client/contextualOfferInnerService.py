#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contextualOffers\client\contextualOfferInnerService.py
from carbon.common.script.util.countdownTimer import CountdownTimer
from contextualOffers.client.contextualOfferClientConst import SCATTER_EVENT_ON_OFFER_AVAILABILITY_CHANGE
from eve.common.script.util.notificationconst import notificationTypeNewOfferAvailable
from gametime import GetWallclockTimeNow, DAY
from notifications.common.formatters.contextualOffers import ContextualOfferNotification
from log import LogError

class ContextualOfferInnerService:

    def __init__(self, scatterService):
        self.scatterSvc = scatterService
        self.InitializeData()

    def InitializeData(self):
        self.availableOffers = {}
        self.purchasedOffers = {}
        self.offerNotifications = []
        self.offerTimers = {}

    def OnOfferReceived(self, offerID, offerObj):
        hadOffers = self.HasOffers()
        self.availableOffers[offerID] = offerObj
        self.AddOfferTimer(offerID, offerObj)
        self._OnAvailabilityChanged(hadOffers)
        self.SendOfferAvailableNotification(offerObj)

    def OnPurchaseSuccessReceived(self, offerID, purchaseObj):
        self.purchasedOffers[offerID] = purchaseObj
        if offerID in self.availableOffers:
            del self.availableOffers[offerID]
        self._NotifyOfAvailabilityChange()

    def SendOfferAvailableNotification(self, offer):
        offerID = offer['offerID']
        subject = offer['notification']['Title']
        body = offer['notification']['Body']
        notificationData = ContextualOfferNotification.MakeData(subject=subject, body=body, url='', offerID=offerID)
        if self.scatterSvc:
            notificationSvc = self.scatterSvc.GetService('notificationSvc')
            notificationSvc.MakeAndScatterNotification(type=notificationTypeNewOfferAvailable, data=notificationData)

    def _OnAvailabilityChanged(self, hadOffers):
        if self.HasOffers() is not hadOffers:
            self._NotifyOfAvailabilityChange()

    def _NotifyOfAvailabilityChange(self):
        if self.scatterSvc:
            self.scatterSvc.ScatterEvent(SCATTER_EVENT_ON_OFFER_AVAILABILITY_CHANGE)

    def GetOfferNotifications(self):
        return list(self.offerNotifications)

    def AddOfferNotification(self, offerID, viewType):
        if (offerID, viewType) not in self.offerNotifications:
            self.offerNotifications.append((offerID, viewType))

    def RemoveOfferNotification(self, offerID, viewType):
        if (offerID, viewType) in self.offerNotifications:
            self.offerNotifications.remove((offerID, viewType))

    def HasOffers(self):
        return len(self.availableOffers) > 0

    def GetOffers(self):
        return self.availableOffers.copy()

    def IsOfferAvailable(self, offerID):
        return offerID in self.availableOffers.keys()

    def GetOfferById(self, offerID):
        return self.availableOffers[offerID]

    def GetPurchasedOffers(self):
        return self.purchasedOffers.copy()

    def IsPurchaseConfirmed(self, offerID):
        return offerID in self.purchasedOffers.keys()

    def GetPurchasedOfferById(self, offerID):
        return self.purchasedOffers[offerID]

    def AddOfferTimer(self, offerID, offerObject):
        expirationDate = offerObject.get('validTo', DAY + GetWallclockTimeNow())
        if offerID in self.offerTimers:
            self.offerTimers[offerID].set_expiration_date(expirationDate)
        else:
            self.offerTimers[offerID] = CountdownTimer(expirationDate)

    def SubscribeToOfferTimer(self, offerID, subscriber, callback):
        if offerID not in self.offerTimers:
            LogError('Failed to subscribe to offer countdown timer. Timer cannot be found.')
            return
        self.offerTimers[offerID].register_subscriber(subscriber, callback)

    def UnsubscribeFromOfferTimer(self, offerID, subscriber):
        if offerID not in self.offerTimers:
            LogError('Failed to unsubscribe from offer countdown timer. Timer cannot be found.')
            return
        self.offerTimers[offerID].unregister_subscriber(subscriber)

    def Debug_ClearOffers(self):
        hadOffers = self.HasOffers()
        self.InitializeData()
        self._OnAvailabilityChanged(hadOffers)
