#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\systemWideEffectSvc.py
from carbon.common.script.sys.service import Service
from eve.client.script.parklife.systemWideEffects import SystemWideEffects

class SystemWideEffectSvc(Service):
    __guid__ = 'svc.systemWideEffectSvc'
    __notifyevents__ = ['OnSystemWideEffectStart',
     'OnSystemWideEffectStop',
     'OnUpdateSystemWideEffectsInfo',
     'OnSessionReset']

    def __init__(self):
        super(SystemWideEffectSvc, self).__init__()
        self.systemWideEffectsOnShip = SystemWideEffects()

    def OnUpdateSystemWideEffectsInfo(self, systemWideEffectsOnShip):
        self.systemWideEffectsOnShip.OnUpdateSystemWideEffectInfo(systemWideEffectsOnShip)
        sm.ScatterEvent('OnSystemWideEffectInfoUpdated', self.GetSystemWideEffectInfo())

    def OnSystemWideEffectStart(self, effectID, sourceItemID, sourceTypeID):
        if not self.systemWideEffectsOnShip.hasAddedEffect(sourceItemID, sourceTypeID):
            sm.ScatterEvent('OnSystemWideEffectAdd', sourceItemID, sourceTypeID)
        self.systemWideEffectsOnShip.OnSystemWideEffectStart(effectID, sourceItemID, sourceTypeID)

    def OnSystemWideEffectStop(self, effectID, sourceItemID, sourceTypeID):
        self.systemWideEffectsOnShip.OnSystemWideEffectStop(effectID, sourceItemID, sourceTypeID)
        if self.systemWideEffectsOnShip.hasNoEffects(sourceItemID, sourceTypeID):
            sm.ScatterEvent('OnSystemWideEffectRemove', sourceItemID)

    def GetSystemWideEffectInfo(self):
        return self.systemWideEffectsOnShip.GetSystemWideEffectsOnShip()

    def OnSessionReset(self):
        self.systemWideEffectsOnShip.ResetSystemWideEffects()
