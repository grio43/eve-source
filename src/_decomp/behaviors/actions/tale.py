#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\tale.py
import logging
from behaviors.tasks import Task
from ccpProfile import TimedFunction
logger = logging.getLogger(__name__)

class UpdateTaleContextForPersistedObject(Task):

    @TimedFunction('behaviors::actions::entities::UpdateTaleContextForPersistedObject::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        if self.context.get('myTaleId') is not None:
            return
        taleId = self._GetTaleIdFromTaleManager()
        if not taleId:
            self.SetStatusToFailed()
            logger.debug('Behavior: %s failed getting taleId from the DB', self.context.myItemId)
        self.context.myTaleId = taleId

    def _GetTaleIdFromTaleManager(self):
        taleManager = self._GetTaleManager()
        persistedObject = taleManager.GetTaleForPersistedObject(self.context.myItemId)
        if len(persistedObject):
            return persistedObject[0].taleID

    def _GetTaleManager(self):
        return sm.GetService('taleMgr')
