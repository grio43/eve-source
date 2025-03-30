#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\gatekeeper\client\service.py
from carbon.common.script.sys import service
import gatekeeper

class GatekeeperService(service.Service):
    __guid__ = 'svc.gatekeeper'
    __notifyevents__ = ['DoSessionChanging', 'ProcessSessionChange']

    def Run(self, memStream = None):
        if getattr(session, 'userid', None):
            self._InitUser()
        if getattr(session, 'charid', None):
            self._InitCharacter()

    def DoSessionChanging(self, isRemote, session, change):
        if 'userid' in change and gatekeeper.user.IsInitialized():
            gatekeeper.user.Teardown()
        if 'charid' in change and gatekeeper.character.IsInitialized():
            gatekeeper.character.Teardown()

    def ProcessSessionChange(self, isRemote, session, change):
        if 'userid' in change and change['userid'][1] is not None:
            self._InitUser()
        if 'charid' in change and change['charid'][1] is not None:
            self._InitCharacter()

    def _InitUser(self):
        gatekeeper.user.Initialize(lambda args: sm.RemoteSvc('charUnboundMgr').GetCohortsForUser)

    def _InitCharacter(self):
        gatekeeper.character.Initialize(lambda args: sm.RemoteSvc('charMgr').GetCohortsForCharacter)
