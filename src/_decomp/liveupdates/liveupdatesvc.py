#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\liveupdates\liveupdatesvc.py
import carbon.common.script.sys.service as service
from . import LiveUpdaterClientMixin
from eveprefs import prefs

class LiveUpdateSvc(service.Service):
    __guid__ = 'svc.LiveUpdateSvc'
    __notifyevents__ = ['OnLiveClientUpdate']

    def __init__(self):
        self.liveUpdater = LiveUpdaterClientMixin()
        service.Service.__init__(self)

    def Enabled(self):
        return False

    def OnLiveClientUpdate(self, payload):
        if self.Enabled():
            self.liveUpdater.HandlePayload(payload)
