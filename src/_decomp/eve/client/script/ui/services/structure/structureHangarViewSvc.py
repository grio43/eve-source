#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\structure\structureHangarViewSvc.py
from carbon.common.script.sys.service import Service

class StructureHangarViewSvc(Service):
    __guid__ = 'svc.structureHangarViewSvc'
    __notifyevents__ = ['DoSessionChanging', 'OnHangarViewStateUpdated']
    _hangarViewState = None

    def DoSessionChanging(self, isRemote, session, change):
        if 'structureid' in change:
            self._hangarViewState = None

    def GetStructureHangarState(self):
        if session.structureid is None:
            raise NotDockedInStructureError('GetStructureHangarState cannot be called when session is not docked in a structure')
        self._UpdateStructureHangarInfo()
        return self._hangarViewState

    def _UpdateStructureHangarInfo(self):
        if session.structureid is not None and self._hangarViewState is None:
            self._hangarViewState = sm.RemoteSvc('structureHangarViewMgr').GetMyHangarViewState()

    def OnHangarViewStateUpdated(self, structureID, hangarViewState):
        if structureID != session.structureid:
            return
        self._hangarViewState = hangarViewState
        sm.ScatterEvent('OnHangarViewStateUpdated_Local', structureID, hangarViewState)


class NotDockedInStructureError(RuntimeError):
    pass
