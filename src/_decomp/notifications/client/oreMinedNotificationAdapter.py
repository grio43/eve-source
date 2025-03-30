#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\oreMinedNotificationAdapter.py


class OreMinedNotificationAdapter(object):
    __notifyevents__ = ['OnOreMined', 'OnHaulerQuantityChangedInClient']

    def __init__(self, loggerService):
        self.loggerService = loggerService

    def OnOreMined(self, dataDict):
        oreType = dataDict['oreType']
        amount = dataDict['amount']
        hasRewards = dataDict['hasRewards']
        amountWasted = dataDict['amountWasted']
        self.loggerService.AddMiningMessage(oreType, amount, hasRewards, amountWasted)

    def OnHaulerQuantityChangedInClient(self, haulerID, quantity, totalQuantity, ownerID, oreType):
        self.loggerService.AddOreDepositedMessage(oreType, quantity, ownerID)
