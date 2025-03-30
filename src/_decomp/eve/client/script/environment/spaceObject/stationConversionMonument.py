#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\stationConversionMonument.py
from dogma.const import attributeMonumentAllianceID, attributeMonumentCorporationID
from eve.client.script.environment.spaceObject.LargeCollidableStructure import LargeCollidableStructure

class StationConversionMonument(LargeCollidableStructure):
    __notifyevents__ = ['OnAllianceLogoReady']

    def __init__(self):
        LargeCollidableStructure.__init__(self)
        sm.RegisterNotify(self)

    def LoadModel(self, fileName = None, loadedModel = None):
        LargeCollidableStructure.LoadModel(self)
        self.SetControllerVariable('IsOnline', True)
        self._SetupLogo()

    def OnAllianceLogoReady(self, allianceID, _size):
        if allianceID and allianceID == self._GetAllianceID():
            self._SetupLogo()

    def _SetupLogo(self):
        allianceID = self._GetAllianceID()
        corporationID = self._GetCorporationID()
        if allianceID:
            logoPath = sm.GetService('photo').GetAllianceLogo(allianceID, size=128, callback=True)
        elif corporationID:
            logoPath = sm.GetService('photo').GetCorporationLogo(corporationID, size=128, callback=True)
        else:
            return
        if self.model is not None:
            for param in self.model.externalParameters:
                if param.name == 'AllianceLogoResPath':
                    setattr(param.destinationObject, param.destinationAttribute, logoPath)

    def _GetAllianceID(self):
        return int(self.sm.GetService('godma').GetTypeAttribute(self.GetTypeID(), attributeMonumentAllianceID, 0))

    def _GetCorporationID(self):
        return int(self.sm.GetService('godma').GetTypeAttribute(self.GetTypeID(), attributeMonumentCorporationID, 0))
