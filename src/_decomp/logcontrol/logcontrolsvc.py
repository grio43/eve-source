#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\logcontrol\logcontrolsvc.py
import blue
import log
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLEMASK_ELEVATEDPLAYER

class LogControlSvc(Service):
    __guid__ = 'svc.LogControl'
    __notifyevents__ = ['OnSessionChanged']

    def OnSessionChanged(self, isRemote, sess, change):
        if 'role' not in change:
            return
        if session and session.role & ROLEMASK_ELEVATEDPLAYER == 0:
            log.LogInfo('Insufficient karma, proceeding quietly...')
            blue.LogControl.LogtypeInfoIsPrivilegedOnly = True
        else:
            blue.LogControl.LogtypeInfoIsPrivilegedOnly = False
