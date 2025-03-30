#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\characterEnergySvc.py
from carbon.common.script.sys.service import Service
from characterenergy import CalculateStateAtTime
from gametime import GetWallclockTime

class CharacterEnergySvc(Service):
    __displayname__ = 'Character Energy Client'
    __guid__ = 'svc.characterEnergySvc'
    __startupdependencies__ = []
    __notifyevents__ = ['OnCharacterSessionChanged', 'OnCharacterEnergyChanged']
    _energyState = None

    def OnCharacterSessionChanged(self, oldCharacterID, newCharacterID):
        self._energyState = None

    def OnCharacterEnergyChanged(self, characterID, newEnergyState):
        if characterID != session.charid:
            return
        self._energyState = newEnergyState
        sm.ScatterEvent('OnCharacterEnergyChanged_Local')

    def GetEnergyStateNow(self):
        return CalculateStateAtTime(self._GetEnergyState(), GetWallclockTime())

    def _GetEnergyState(self):
        if self._energyState is None:
            self._energyState = sm.RemoteSvc('characterEnergyMgr').GetMyEnergyState()
        return self._energyState
