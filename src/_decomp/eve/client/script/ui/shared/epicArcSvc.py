#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\epicArcSvc.py
from carbon.common.script.sys.service import Service
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.epicArcs.epicArcController import EpicArcController

class EpicArcSvc(Service):
    __guid__ = 'svc.epicArc'
    __startupdependencies__ = []
    __notifyevents__ = ['OnEpicJournalChange', 'OnCharacterSelected', 'OnSessionReset']

    def OnCharacterSelected(self):
        self.Initialize()

    def OnSessionReset(self):
        self.Initialize()

    def Initialize(self):
        self._missionStatusesByEpicArcID = None
        self.controller = None

    def ReconstructController(self):
        self._missionStatusesByEpicArcID = sm.RemoteSvc('agentMgr').GetMyEpicArcStatus()
        self.controller = EpicArcController(missionStatusesByEpicArcID=self._missionStatusesByEpicArcID)
        sm.GetService('agencyNew').GetContentProvider(contentGroupConst.contentGroupEpicArcs).InvalidateContentPieces()

    def GetEpicArcs(self):
        self.CheckConstructController()
        return self.controller.GetEpicArcs().values()

    def GetEpicArcFactionIDs(self):
        return set([ arc.GetFactionID() for arc in self.GetEpicArcs() ])

    def CheckConstructController(self):
        if not self.controller:
            self.ReconstructController()

    def OnEpicJournalChange(self):
        self.ReconstructController()
        sm.ScatterEvent('OnEpicArcDataChanged')
