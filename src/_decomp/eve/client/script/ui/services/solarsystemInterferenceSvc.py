#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\solarsystemInterferenceSvc.py
from carbon.common.script.sys.service import Service
from gametime import GetWallclockTime
from solarsysteminterference import CalculateStateAtTime
from solarsysteminterference.const import INTERFERENCE_BAND_NONE

class SolarsystemInterferenceSvc(Service):
    __displayname__ = 'Solarsystem Interference Client'
    __guid__ = 'svc.solarsystemInterferenceSvc'
    __startupdependencies__ = []
    __notifyevents__ = ['OnSessionChanged', 'OnSolarsystemInterferenceChanged']
    _localInterferenceState = None

    def OnSessionChanged(self, isremote, session, change):
        if 'solarsystemid2' in change:
            self._localInterferenceState = None

    def OnSolarsystemInterferenceChanged(self, solarsystemID, newInterferenceState):
        if solarsystemID != session.solarsystemid2:
            return
        self._localInterferenceState = newInterferenceState
        sm.ScatterEvent('OnSolarsystemInterferenceChanged_Local')

    def GetLocalInterferenceStateNow(self):
        interferenceState = self._GetLocalInterferenceState()
        if interferenceState is not None:
            return CalculateStateAtTime(interferenceState, GetWallclockTime())

    def _GetLocalInterferenceState(self):
        if self._localInterferenceState is None:
            self._localInterferenceState = sm.RemoteSvc('solarsystemInterferenceMgr').GetLocalInterferenceState()
        return self._localInterferenceState

    def GetAllInterferenceBands(self):
        return sm.RemoteSvc('solarsystemInterferenceMgr').GetAllInterferenceBands()

    def GetSolarSystemInterferenceBand(self, solarsystemID):
        if session.solarsystemid2 == solarsystemID:
            localInterferenceState = self.GetLocalInterferenceStateNow()
            if localInterferenceState is not None:
                return localInterferenceState.interferenceBand
        else:
            interferenceBands = self.GetAllInterferenceBands()
            if solarsystemID in interferenceBands:
                return interferenceBands[solarsystemID]
        return INTERFERENCE_BAND_NONE
