#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\dogma\clientDogmaIM.py
import uthread
from carbon.common.script.sys.service import Service
from clientDogmaLocation import DogmaLocation
from carbon.common.lib.const import ixLocationID

class ClientDogmaInstanceManager(Service):
    __guid__ = 'svc.clientDogmaIM'
    __startupdependencies__ = ['clientEffectCompiler',
     'invCache',
     'godma',
     'michelle']
    __notifyevents__ = ['ProcessSessionChange', 'OnSessionReset']

    def Run(self, *args):
        Service.Run(self, *args)
        self.dogmaLocation = None
        self.fittingDogmaLocation = None

    def GetDogmaLocation(self, charBrain = None, *args):
        uthread.Lock('GetDogmaLocation')
        try:
            if self.dogmaLocation is None:
                self.dogmaLocation = DogmaLocation(self, charBrain)
                self.LogInfo('Created client dogmaLocation', id(self.dogmaLocation))
        finally:
            uthread.UnLock('GetDogmaLocation')

        return self.dogmaLocation

    def GetFittingDogmaLocation(self, force = False, *args):
        uthread.Lock('GetFittingDogmaLocation')
        try:
            if self.fittingDogmaLocation is None or force:
                from eve.client.script.ui.shared.fittingScreen.fittingDogmaLocation import FittingDogmaLocation
                charBrain = self._GetBrainForGhostFitting()
                self.fittingDogmaLocation = FittingDogmaLocation(self, charBrain=charBrain)
                self.LogInfo('Created client fittingDogmaLocation', id(self.fittingDogmaLocation))
        finally:
            uthread.UnLock('GetFittingDogmaLocation')

        return self.fittingDogmaLocation

    def _GetBrainForGhostFitting(self):
        if self.dogmaLocation:
            return self.dogmaLocation.GetBrainData(session.charid)
        dogmaLM = sm.GetService('godma').GetDogmaLM()
        allInfo = dogmaLM.GetAllInfo(session.charid, None, None)
        charBrain = allInfo.charInfo or ()
        return charBrain

    def GodmaItemChanged(self, item, change, location):
        if item.itemID == session.charid:
            return
        if self.dogmaLocation is not None:
            shipID = self.dogmaLocation.GetCurrentShipID()
            if item.locationID == shipID:
                self.dogmaLocation.OnItemChange(item, change, location)
            elif change.get(ixLocationID, None) == shipID:
                self.dogmaLocation.OnItemChange(item, change, location)

    def ProcessSessionChange(self, isRemote, session, change):
        if self.dogmaLocation is None:
            return
        if 'stationid' in change or 'solarsystemid' in change:
            self.dogmaLocation.UpdateRemoteDogmaLocation()

    def OnSessionReset(self):
        self.dogmaLocation = None
        if self.fittingDogmaLocation:
            sm.UnregisterNotify(self.fittingDogmaLocation)
            self.fittingDogmaLocation = None

    def GetCapacityForItem(self, itemID, attributeID):
        if self.dogmaLocation is None:
            return
        if not self.dogmaLocation.IsItemLoaded(itemID):
            return
        return self.dogmaLocation.GetAttributeValue(itemID, attributeID)
