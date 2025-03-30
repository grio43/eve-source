#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dotWeapons\client\dotInfoPerTarget.py
import gametime
import itertoolsext
from dotWeapons.common.dotConst import DOT_ACTIVE

class DamageInfoPerTarget(object):

    def __init__(self):
        self._ResetState()

    def _ResetState(self):
        self._dmgInfo = set()

    def UpdatedDotWeapons(self, dmgApps):
        self._dmgInfo = dmgApps

    def HasDotApps(self):
        self._ExpireDmgInfo()
        if self._dmgInfo:
            return True

    def _ExpireDmgInfo(self):
        toRemove = []
        for d in self._dmgInfo:
            if d.expiryTime <= gametime.GetSimTime():
                toRemove.append(d)

        for tr in toRemove:
            self._dmgInfo.discard(tr)

    def GetAppliedDamage(self):
        self._ExpireDmgInfo()
        return itertoolsext.first(self._dmgInfo, predicate=lambda x: x.activityState == DOT_ACTIVE)

    def GetAllDmgInfo(self, doExpire = True):
        if doExpire:
            self._ExpireDmgInfo()
        return self._dmgInfo

    def GetLastExpiryTimestamp(self):
        self._ExpireDmgInfo()
        lastPendingExpiryTime = None
        for p in self.GetAllDmgInfo():
            if lastPendingExpiryTime < p.expiryTime:
                lastPendingExpiryTime = p.expiryTime

        return lastPendingExpiryTime

    def GetDamageInfoForAttacker(self, charID, doExpire = True):
        all = self.GetAllDmgInfo(doExpire)
        ret = []
        for dmgInfo in all:
            if dmgInfo.attackerID == charID:
                ret.append(dmgInfo)

        return ret

    def __repr__(self):
        return '<DamageInfoPerTarget %s>, %s' % (self.__dict__, id(self))
