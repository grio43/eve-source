#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\jumpQueue.py
import sys
import blue
import localization
import log
import uthread
import utillib
from ballparkCommon.jumpdelay import GetStargateJumpDelayBlueTime
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_SERVICE, SERVICE_RUNNING
from eve.common.lib import appConst as const

class JumpQueue(Service):
    __guid__ = 'svc.jumpQueue'
    __exportedcalls__ = {'IsJumpQueued': [ROLE_SERVICE]}
    __dependencies__ = ['machoNet']
    __notifyevents__ = ['OnJumpQueueUpdate', 'DoSessionChanging']

    def Run(self, ms):
        Service.Run(self, ms)
        self.jumpQueue = None
        self.queueCharID = None
        uthread.worker('jumpQueue::Timer', self.__Timer)

    def PrepareQueueForCharID(self, charID):
        self.jumpQueue = None
        self.queueCharID = charID

    def GetPreparedQueueCharID(self):
        return self.queueCharID

    def DoSessionChanging(self, isRemote, session, change):
        if 'solarsystemid2' in change:
            self.LogInfo('Jump Queue:  DoSessionChanging is cleaning jump queue info')
            self.jumpQueue = None

    def __Timer(self):
        while self.state == SERVICE_RUNNING:
            if self.jumpQueue is None:
                blue.pyos.synchro.SleepWallclock(500)
            else:
                try:
                    if self._ShouldShowNotification():
                        if eve.session.solarsystemid2 and eve.session.solarsystemid2 == self.jumpQueue.solarsystemID:
                            self.jumpQueue = None
                        elif self.queueCharID in self.jumpQueue.jumpKeys:
                            expires = self.jumpQueue.jumpKeys[self.queueCharID] + const.SEC * self.jumpQueue.keyLife
                            if blue.os.GetWallclockTime() > expires:
                                sm.ScatterEvent('OnJumpQueueMessage', localization.GetByLabel('UI/JumpQueue/KeyExpired', system=self.jumpQueue.solarsystemID), False)
                                self.jumpQueue = None
                            else:
                                sm.ScatterEvent('OnJumpQueueMessage', localization.GetByLabel('UI/JumpQueue/KeyIssued', system=self.jumpQueue.solarsystemID, expiration=expires - blue.os.GetWallclockTime()), True)
                        else:
                            try:
                                idx = 1 + self.jumpQueue.queue.index(self.queueCharID)
                                position = max(1, idx - self.jumpQueue.space)
                                sm.ScatterEvent('OnJumpQueueMessage', localization.GetByLabel('UI/JumpQueue/Waiting', system=self.jumpQueue.solarsystemID, pos=position), False)
                            except ValueError:
                                sys.exc_clear()

                except:
                    log.LogException()
                    sys.exc_clear()

                blue.pyos.synchro.SleepWallclock(4500)

    def _ShouldShowNotification(self):
        if self.jumpQueue is None or not eve.session.IsItSafe():
            return False
        if eve.session.nextSessionChange is None or eve.session.solarsystemid2 is None:
            return True
        startNotificationsTime = eve.session.nextSessionChange + GetStargateJumpDelayBlueTime(self.jumpQueue.solarsystemID) - 5 * const.SEC
        return blue.os.GetSimTime() > startNotificationsTime

    def IsJumpQueued(self):
        if self.jumpQueue is None:
            return False
        if self.queueCharID in self.jumpQueue.jumpKeys:
            if blue.os.GetWallclockTime() - self.jumpQueue.jumpKeys[self.queueCharID] < const.SEC * self.jumpQueue.keyLife:
                self.jumpQueue = None
            else:
                return False
        self.LogInfo('Jump Queued, queue=', self.jumpQueue)
        return True

    def OnJumpQueueUpdate(self, solarsystemID, space, queue, jumpKeys, keyLife):
        if self.jumpQueue is None:
            self.LogInfo('Jump Queue:  Entering Queue for ', solarsystemID, ', space=', space, ', queue=', queue)
            self.jumpQueue = utillib.KeyVal(solarsystemID=solarsystemID, space=space, queue=queue, jumpKeys=jumpKeys, keyLife=keyLife)
        elif self.queueCharID in queue:
            self.LogInfo('Jump Queue:  Queue update for ', solarsystemID, ', space=', space, ', queue=', queue, ', keys=', jumpKeys)
            self.jumpQueue.space = space
            self.jumpQueue.queue = queue
            self.jumpQueue.jumpKeys = jumpKeys
            self.jumpQueue.keyLife = keyLife
        else:
            self.LogInfo('Jump Queue:  ', self.queueCharID, ' is leaving queue for ', solarsystemID)
            self.jumpQueue = None
