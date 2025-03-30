#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\nonDiminishingInjectionService.py
import carbon.common.script.sys.service as service

class NonDiminishingInjection(service.Service):
    __guid__ = 'svc.nonDiminishingInjection'
    __servicename__ = 'nonDiminishingInjection'
    __displayname__ = 'Non-Diminishing Injection Service'
    __exportedcalls__ = {'GetRemaining': []}
    __notifyevents__ = ['OnCharacterSessionChanged',
     'OnNonDiminishingInjectionsAdded',
     'OnNonDiminishingInjectionsUsed',
     'OnNonDiminishingInjectionsRemoved']

    def Run(self, memStream = None):
        self.availableInjections = None

    def OnCharacterSessionChanged(self, _oldCharacterID, _newCharacterID):
        self._UpdateAvailableNonDiminishingInjections()

    def OnNonDiminishingInjectionsAdded(self, amount):
        if self.availableInjections is not None:
            self.availableInjections += amount
        sm.ScatterEvent('OnNonDiminishingInjectionsChanged')

    def OnNonDiminishingInjectionsUsed(self, amount):
        if self.availableInjections is not None:
            self.availableInjections -= amount
        sm.ScatterEvent('OnNonDiminishingInjectionsChanged')

    def OnNonDiminishingInjectionsRemoved(self):
        self.availableInjections = 0
        sm.ScatterEvent('OnNonDiminishingInjectionsChanged')

    def GetRemaining(self):
        if self.availableInjections is None:
            self._UpdateAvailableNonDiminishingInjections()
        return self.availableInjections

    def _UpdateAvailableNonDiminishingInjections(self):
        self.availableInjections = sm.RemoteSvc('nonDiminishingInjectionMgr').GetAvailableNonDiminishingInjections()
