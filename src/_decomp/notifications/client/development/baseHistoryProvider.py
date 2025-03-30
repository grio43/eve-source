#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\development\baseHistoryProvider.py


class BaseHistoryProvider(object):

    def __init__(self, scatterDebug = False, onlyShowAfterDate = None):
        self.scatterDebug = scatterDebug
        self.onlyShowAfterDate = onlyShowAfterDate

    def IsNotificationTooOld(self, notificationDate):
        if self.onlyShowAfterDate and notificationDate <= self.onlyShowAfterDate:
            return True
        return False
