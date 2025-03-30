#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\sovereigntyClaimMarker.py
import uthread
from eve.client.script.environment.spaceObject.LargeCollidableStructure import LargeCollidableStructure
from evegraphics.logoLoader import LogoLoader

class SovereigntyClaimMarker(LargeCollidableStructure):
    __notifyevents__ = ['OnAllianceLogoReady']

    def __init__(self):
        LargeCollidableStructure.__init__(self)
        self.logoLoader = LogoLoader((LogoLoader.ALLIANCE,))
        sm.RegisterNotify(self)

    def LoadModel(self, fileName = None, loadedModel = None):
        LargeCollidableStructure.LoadModel(self)
        self.SetControllerVariable('IsOnline', bool(self._GetAllianceID()))
        self.logoLoader.Load(self.model, self.typeData['slimItem'])

    def OnSlimItemUpdated(self, slimItem):
        uthread.new(self.logoLoader.Load, self.model, slimItem)
        oldAllianceID = self._GetAllianceID()
        self.typeData['slimItem'] = slimItem
        newAllianceID = self._GetAllianceID()
        if oldAllianceID != newAllianceID:
            self.SetControllerVariable('IsOnline', bool(self._GetAllianceID()))

    def OnAllianceLogoReady(self, allianceID, _size):
        if self.logoLoader.HasID(allianceID):
            self.logoLoader.Update(self.model)

    def _GetAllianceID(self):
        slimItem = self.typeData['slimItem']
        return getattr(slimItem, 'allianceID', None)
