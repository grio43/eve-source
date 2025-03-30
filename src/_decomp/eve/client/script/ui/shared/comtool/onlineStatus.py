#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\comtool\onlineStatus.py
import blue
import uthread
from carbon.common.script.sys.service import Service
from eve.common.script.sys import idCheckers

class OnlineStatus(Service):
    __guid__ = 'svc.onlineStatus'
    __displayname__ = 'Online Status Service'
    __exportedcalls__ = {'GetOnlineStatus': [],
     'Prime': []}
    __notifyevents__ = ['OnContactLoggedOn',
     'OnContactLoggedOff',
     'OnSessionChanged',
     'OnClientContactChange',
     'OnSessionReset']

    def Run(self, memStream = None):
        self.semaphore = uthread.Semaphore()
        self.onlineStatus = None

    def OnContactLoggedOn(self, charID):
        self.Prime()
        self.onlineStatus[charID] = blue.DBRow(self.onlineStatus.header, [charID, True])

    def OnContactLoggedOff(self, charID):
        self.Prime()
        self.onlineStatus[charID] = blue.DBRow(self.onlineStatus.header, [charID, False])

    def OnClientContactChange(self, charID, online):
        if online:
            self.OnContactLoggedOn(charID)
        else:
            self.OnContactLoggedOff(charID)

    def OnSessionChanged(self, isRemote, sess, change):
        if 'charid' in change and change['charid'][1]:
            self.Prime()

    def GetOnlineStatus(self, charID, fetch = True):
        if idCheckers.IsNPC(charID):
            return False
        if fetch:
            self.Prime()
        if charID not in (self.onlineStatus or {}):
            if fetch:
                self.onlineStatus[charID] = blue.DBRow(self.onlineStatus.header, [charID, sm.RemoteSvc('onlineStatus').GetOnlineStatus(charID)])
            else:
                raise IndexError('GetOnlineStatus', charID)
        if charID in self.onlineStatus:
            return self.onlineStatus[charID].online
        else:
            return None

    def ClearOnlineStatus(self, charID):
        if charID in self.onlineStatus:
            del self.onlineStatus[charID]
            sm.ScatterEvent('OnContactNoLongerContact', charID)

    def OnSessionReset(self):
        self.onlineStatus = None

    def Prime(self):
        if self.onlineStatus is None:
            self.semaphore.acquire()
            try:
                if self.onlineStatus is None:
                    self.onlineStatus = sm.RemoteSvc('onlineStatus').GetInitialState().Index('contactID')
            finally:
                self.semaphore.release()
