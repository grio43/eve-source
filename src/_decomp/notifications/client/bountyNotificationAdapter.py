#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\bountyNotificationAdapter.py


class BountyNotificationAdapter(object):
    __notifyevents__ = ['OnBountyAddedToPayout']

    def __init__(self, loggerService):
        self.loggerService = loggerService

    def OnBountyAddedToPayout(self, dataDict):
        amount = dataDict['amount']
        payoutTimestamp = dataDict['payoutTime']
        enemyTypeID = dataDict['enemyTypeID']
        isModified = dataDict['isModified']
        self.loggerService.AddBountyMessage(amount, payoutTimestamp, enemyTypeID, isModified)
