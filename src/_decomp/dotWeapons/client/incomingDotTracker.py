#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dotWeapons\client\incomingDotTracker.py
from collections import defaultdict
import signals
from carbon.common.script.util.timerstuff import AutoTimer
from dotWeapons.client.dotInfoPerTarget import DamageInfoPerTarget
from uthread2 import BufferedCall

class IncomingDotTracker(object):
    __notifyevents__ = ['OnSessionChanged']
    _appliedDmgApp = None
    _pending = None
    signalOnDotWeaponUpdate = None

    def __init__(self):
        self._expireThread = None
        self._infoByTargetID = defaultdict(DamageInfoPerTarget)
        self._isAttackBtnVisible = False
        sm.RegisterNotify(self)
        self.signalOnDotWeaponUpdate = signals.Signal(signalName='signalOnDotWeaponUpdate')
        self._ResetState()

    def _ResetState(self):
        self._infoByTargetID.clear()
        self.signalOnDotWeaponUpdate()

    def OnSessionChanged(self, isRemote, sess, change):
        if 'shipid' in change or 'locationid' in change or 'structureid' in change:
            self._ResetState()

    def OnDotWeaponsUpdated(self, targetID, dmgAppsInfo):
        self._infoByTargetID[targetID].UpdatedDotWeapons(dmgAppsInfo)
        if not self._expireThread:
            self._expireThread = AutoTimer(1000, self.ExpireThread)
        self.signalOnDotWeaponUpdate()

    def CurrentShipHasIncomingDotApps(self):
        shipID = session.shipid
        if shipID in self._infoByTargetID:
            return self._infoByTargetID[shipID].HasDotApps()
        return False

    def GetDmgInfoForShipID(self, shipID):
        if shipID in self._infoByTargetID:
            return self._infoByTargetID[shipID].GetAllDmgInfo()
        return set()

    def GetLastExpiryTimestampForCurrentShip(self):
        shipID = session.shipid
        if shipID in self._infoByTargetID:
            return self._infoByTargetID[shipID].GetLastExpiryTimestamp()

    def GetOnGridDamageInfosForAttacker(self, charID, doExpire = True):
        ret = []
        ballpark = sm.GetService('michelle').GetBallpark()
        for targetID, info in self._infoByTargetID.iteritems():
            if not ballpark.GetInvItem(targetID):
                continue
            ret += info.GetDamageInfoForAttacker(charID, doExpire)

        return ret

    def HasAttackingDotApps(self, doExpire = True):
        return bool(self.GetOnGridDamageInfosForAttacker(session.charid, doExpire))

    def ShouldShowAttackingBtn(self):
        self._isAttackBtnVisible = self.HasAttackingDotApps()
        return self._isAttackBtnVisible

    def ExpireThread(self):
        if not self._infoByTargetID:
            self._expireThread = None
            return
        btnVisibleBefore = self._isAttackBtnVisible
        toRemove = set()
        for targetID, info in self._infoByTargetID.iteritems():
            if not info.HasDotApps():
                toRemove.add(targetID)

        for targetID in toRemove:
            self._infoByTargetID.pop(targetID, None)

        btnVisibleAfter = self.ShouldShowAttackingBtn()
        if session.shipid in toRemove:
            self.TriggerUpdate()
        elif btnVisibleBefore != btnVisibleAfter:
            self.TriggerUpdate()

    @BufferedCall(50)
    def TriggerUpdate(self):
        self.signalOnDotWeaponUpdate()
