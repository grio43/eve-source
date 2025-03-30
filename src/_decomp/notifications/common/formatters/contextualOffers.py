#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\contextualOffers.py
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

def OnNotificationClick(offerID):
    sm.GetService('contextualOfferSvc').DisplayOfferWindowIfActive(offerID)


class ContextualOfferNotification(BaseNotificationFormatter):

    def Format(self, notification):
        data = notification.data
        notification.subject = data['notificationSubject']
        notification.subtext = data['notificationBody']
        notification.Activate = lambda : OnNotificationClick(offerID=data['offerID'])

    def GetMessageFromData(self, data):
        return data.get('message', '')

    @staticmethod
    def MakeData(subject, body, url, offerID):
        data = {'notificationSubject': subject,
         'notificationBody': body,
         'url': url,
         'offerID': offerID}
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        print 'SampleData'
        return ContextualOfferNotification.MakeData(subject='SpecialOffer For you', body='Like right now dude', url='http://google.com', offerID=2)

    @staticmethod
    def OnNotificationClick(notification):
        pass
