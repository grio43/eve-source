#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\rwPirateKilledNotificationAdapter.py


class PirateKilledNotificationAdapter(object):
    __notifyevents__ = ['OnRwPirateKilledByCharacter', 'OnRwPirateKilledByNpc']

    def __init__(self, loggerService):
        self.loggerService = loggerService

    def OnRwPirateKilledByCharacter(self, killerID, killedShipItem):
        self.loggerService.AddRwPirateKilledByCharacterMessage(killerID, killedShipItem)

    def OnRwPirateKilledByNpc(self, killerShipItem, killedShipItem):
        self.loggerService.AddRwPirateKilledByNpcMessage(killerShipItem, killedShipItem)
