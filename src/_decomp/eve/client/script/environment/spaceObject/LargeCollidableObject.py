#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\LargeCollidableObject.py
import evetypes
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from eveSpaceObject import spaceobjaudio
from globalConfig.getFunctions import BillboardTakeoverEnabled
from inventorycommon.const import groupBillboard

class LargeCollidableObject(SpaceObject):
    __notifyevents__ = ['OnAudioDeactivated']

    def __init__(self):
        super(LargeCollidableObject, self).__init__()
        if self.IsBillboard():
            sm.RegisterNotify(self)

    def GetDNA(self):
        dna = SpaceObject.GetDNA(self)
        if dna and ':class?' not in dna:
            dna += ':class?stationary'
        return dna

    def Assemble(self):
        self.SetStaticRotation()
        if getattr(self.model, 'ChainAnimationEx', None) is not None:
            self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        self.SetupSharedAmbientAudio()
        self.SetupBillboard()
        self.TriggerStateObject('default')

    def SetupAmbientAudio(self, defaultSoundUrl = None, model = None):
        super(LargeCollidableObject, self).SetupAmbientAudio(defaultSoundUrl, model)
        self.SetupBillboard()

    def IsBillboard(self):
        return evetypes.GetGroupID(self.GetTypeID()) == groupBillboard

    def OnAudioDeactivated(self):
        self.SetupBillboard()

    def SetupBillboard(self):
        if self.IsBillboard():
            machoNet = sm.GetService('machoNet')
            if BillboardTakeoverEnabled(machoNet):
                audioEnabled = sm.GetService('audio').IsActivated()
                spaceobjaudio.SetBillboardAudio(self.model, audioEnabled)
                if hasattr(self.model, 'observers') and audioEnabled:
                    for observer in self.model.observers:
                        spaceobjaudio.PlayBillboardAudio(observer.observer, self.id)

    def Release(self, origin = None):
        if self.IsBillboard():
            spaceobjaudio.StopBillboardAudio(self.id)
        super(LargeCollidableObject, self).Release(origin)
