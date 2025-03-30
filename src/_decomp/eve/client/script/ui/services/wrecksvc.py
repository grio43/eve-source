#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\wrecksvc.py
import sys
import blue
import log
from carbon.common.script.sys.service import Service
from eve.client.script.parklife import states as state

class WreckService(Service):
    __guid__ = 'svc.wreck'
    __dependencies__ = ['stateSvc', 'gameui']
    __notifyevents__ = ['OnCharacterSessionChanged', 'OnSessionReset']
    __startupdependencies__ = ['settings']

    def Run(self, *args):
        super(WreckService, self).Run(*args)
        self.viewedWrecks = {}
        self.viewdWrecksLoaded = False
        self.LoadViewedWrecks()

    def OnCharacterSessionChanged(self, _oldCharacterID, newCharacterID):
        if newCharacterID is not None:
            self.LoadViewedWrecks()

    def OnSessionReset(self):
        self.viewedWrecks = {}
        self.viewdWrecksLoaded = False

    def LoadViewedWrecks(self):
        if not session.charid or self.viewdWrecksLoaded:
            return
        self.viewdWrecksLoaded = True
        expire_hours, expire_mins = (2, 5)
        expire_ms = 1000 * (3600 * expire_hours + 60 * expire_mins)
        for itemID, time in settings.char.ui.Get('viewedWrecks', {}).iteritems():
            try:
                if blue.os.TimeDiffInMs(time, blue.os.GetWallclockTime()) < expire_ms:
                    self.viewedWrecks[itemID] = time
            except blue.error:
                sys.exc_clear()

        try:
            self._PersistSettings()
        except:
            log.LogException()
            sys.exc_clear()

    def MarkViewed(self, itemID, isViewed, playSound = False):
        if self.IsMarkedViewed(itemID) == isViewed:
            return
        self._SetViewed(itemID, isViewed)
        self._MarkVisually(itemID, isViewed)
        self._PersistSettings()
        if isViewed and playSound:
            sm.GetService('audio').SendUIEvent('ui_sfx_open_wreck_play')

    def IsMarkedViewed(self, itemID):
        return self.stateSvc.GetStates(itemID, (state.flagWreckAlreadyOpened,))[0]

    def IsViewedWreck(self, itemID):
        return itemID in self.viewedWrecks

    def _MarkVisually(self, itemID, isViewed):
        self.stateSvc.SetState(itemID, state.flagWreckAlreadyOpened, isViewed)

    def _SetViewed(self, itemID, isViewed):
        if isViewed and itemID not in self.viewedWrecks:
            self.viewedWrecks[itemID] = blue.os.GetWallclockTime()
        elif not isViewed and itemID in self.viewedWrecks:
            del self.viewedWrecks[itemID]

    def _PersistSettings(self):
        settings.char.ui.Set('viewedWrecks', self.viewedWrecks)
