#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\fwVictoryPointSvc.py
from carbon.common.script.sys.service import Service
from carbonui.uicore import uicore
from eveexceptions import UE_OWNERID
STATE_UNKNOWN = 'STATE_UNKNOWN'

class FwVictoryPointSvc(Service):
    __guid__ = 'svc.fwVictoryPointSvc'
    __displayname__ = 'FW Victory Point client service'
    __startupdependencies__ = ['machoNet']
    __notifyevents__ = ['OnSessionChanged',
     'OnVictoryPointStateUpdated',
     'OnFacWarBunkerVulnerable',
     'OnFacWarBunkerNonVulnerable']
    _localVictoryPointState = STATE_UNKNOWN

    def _VictoryPointStateLock(self):
        return self.LockedService('VictoryPointState')

    def OnSessionChanged(self, isremote, session, change):
        if 'solarsystemid2' in change:
            self._localVictoryPointState = STATE_UNKNOWN

    def GetLocalVictoryPointState(self):
        if self._localVictoryPointState is STATE_UNKNOWN:
            with self._VictoryPointStateLock():
                if self._localVictoryPointState is STATE_UNKNOWN:
                    self.LogInfo('GetLocalVictoryPointState - _localVictoryPointState is unknown - asking the server')
                    solarsystemID, victoryPointState = sm.RemoteSvc('fwVictoryPointMgr').GetLocalVictoryPointState()
                    if solarsystemID != session.solarsystemid2:
                        solarsystemID, victoryPointState = sm.RemoteSvc('fwVictoryPointMgr').GetLocalVictoryPointState()
                    if solarsystemID == session.solarsystemid2:
                        self._localVictoryPointState = victoryPointState
        return self._localVictoryPointState

    def GetVictoryPointState(self, solarsystemID):
        if solarsystemID == session.solarsystemid2:
            return self.GetLocalVictoryPointState()
        victoryPointStateBySolarsystemID = sm.RemoteSvc('fwVictoryPointMgr').GetAllVictoryPointStates()
        return victoryPointStateBySolarsystemID.get(solarsystemID, None)

    def OnVictoryPointStateUpdated(self, solarsystemID, newVictoryPointState):
        self.LogInfo('fwVictoryPointSvc.OnVictoryPointStateUpdated', solarsystemID, newVictoryPointState)
        with self._VictoryPointStateLock():
            if solarsystemID != session.solarsystemid2:
                return
            if newVictoryPointState == self._localVictoryPointState:
                return
            self._localVictoryPointState = newVictoryPointState
        sm.ScatterEvent('OnVictoryPointStateUpdated_Local')
        sm.GetService('infoPanel').UpdateFactionalWarfarePanel()
        sm.ScatterEvent('OnSystemStatusChanged')

    def OnFacWarBunkerVulnerable(self, attackerID):
        uicore.Message('FacWarBunkerVulnerable', {'faction': (UE_OWNERID, attackerID)})

    def OnFacWarBunkerNonVulnerable(self, attackerID):
        uicore.Message('FacWarBunkerNonVulnerable', {'faction': (UE_OWNERID, attackerID)})
