#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\client\tutorialOperationsController.py
import carbonui.const as uiconst
from operations.client.operationscontroller import GetOperationsController
from operations.common.const import OPERATION_CATEGORY_TUTORIAL_AIR_NPE
from operations.common.util import get_tutorial_category_id
from uihider import get_ui_hider

class TutorialOperationsController(object):
    __notifyevents__ = ['OnTutorialSkipped', 'OnOperationCategoryCompleted']

    def __init__(self, *args, **kwargs):
        super(TutorialOperationsController, self).__init__(*args, **kwargs)
        self._is_tutorial_complete = None
        self.manager = sm.RemoteSvc('operationsManager')
        self.operationsController = GetOperationsController()
        sm.RegisterNotify(self)

    def is_tutorial_active(self):
        return self.operationsController.get_active_category_id() == get_tutorial_category_id()

    def get_tutorial_state(self):
        return self.manager.get_tutorial_state()

    def terminate_tutorial(self):
        self._is_tutorial_complete = True
        with self.operationsController.state_cache.Lock() as state_cache:
            state_cache.active_category_id = None
            state_cache.active_operation_id = None

    @property
    def is_tutorial_complete(self):
        if self._is_tutorial_complete is None:
            self._is_tutorial_complete = self.operationsController.is_category_complete(get_tutorial_category_id())
        return self._is_tutorial_complete

    def is_main_tutorial_finished(self):
        return self.manager.is_main_tutorial_finished(session.charid)

    def has_skipped_tutorial(self):
        return self.manager.has_skipped_tutorial()

    def OnTutorialSkipped(self):
        self.terminate_tutorial()

    def OnOperationCategoryCompleted(self, categoryID):
        if categoryID == get_tutorial_category_id():
            self.terminate_tutorial()


tutorialOperationsController = None

def GetTutorialOperationsController():
    global tutorialOperationsController
    if tutorialOperationsController is None:
        tutorialOperationsController = TutorialOperationsController()
    return tutorialOperationsController


def ReleaseTutorialOperationsController():
    global tutorialOperationsController
    if tutorialOperationsController is not None:
        del tutorialOperationsController
        tutorialOperationsController = None
