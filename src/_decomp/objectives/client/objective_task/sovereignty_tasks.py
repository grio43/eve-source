#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\sovereignty_tasks.py
import eveicon
import uuid
from ballparkCommon.parkhelpers.warpSubjects import WarpSubjects
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToItem, Approach
from eve.common.script.sys.eveCfg import InShipInSpace
from localization import GetByLabel
from menucheckers import CelestialChecker, SessionChecker
from objectives.client.objective_task.base import ObjectiveTask
from objectives.client.ui.objective_task_widget import ObjectiveTaskWidget
from objectives.client.ui.objective_task_widget.button import ButtonTaskWidget
from sovereignty.mercenaryden.client.checkers import is_mercenary_den_close_enough_to_configure
from sovereignty.mercenaryden.client.mercenary_den_signals import on_activity_started_notice
from sovereignty.mercenaryden.client.repository import get_mercenary_den_repository
from sovereignty.mercenaryden.common.errors import UnknownActivity, ActivityValidationFailed, ActivityAlreadyStarted
import logging
logger = logging.getLogger('mercenary_den')

class StartMTOActivity(ObjectiveTask):
    objective_task_content_id = 46
    BUTTON_WIDGET = ButtonTaskWidget
    WIDGET = ObjectiveTaskWidget

    def __init__(self, activity_id = None, den_id = None, **kwargs):
        super(StartMTOActivity, self).__init__(**kwargs)
        self._repository = get_mercenary_den_repository()
        self._activity_id = uuid.UUID(hex=activity_id)
        self._den_id = den_id
        on_activity_started_notice.connect(self._activity_started)

    def __del__(self):
        on_activity_started_notice.disconnect(self._activity_started)

    def _start(self):
        super(StartMTOActivity, self)._start()

    def _update(self):
        activity = self._repository.get_mercenary_den_activity_for_character(self._activity_id)
        self.completed = activity is not None and activity.is_started

    def _activity_started(self, activity):
        if activity.id == self._activity_id:
            self.completed = True

    @property
    def completed(self):
        return self._completed

    @completed.setter
    def completed(self, value):
        self._completed = bool(value)
        self._update_highlight_state()
        self.on_state_changed(objective_task=self, reason='on_complete' if value else 'on_incomplete')

    @property
    def button_label(self):
        return GetByLabel('UI/Sovereignty/MercenaryDen/StartOperation')

    @property
    def title(self):
        return GetByLabel('UI/Sovereignty/MercenaryDen/StartMTOAtMercDen')

    @property
    def button_icon(self):
        return eveicon.mercenary_den

    @property
    def icon(self):
        return eveicon.mercenary_den

    def double_click(self):
        activity = self._repository.get_mercenary_den_activity_for_character(self._activity_id)
        if not InShipInSpace() or session.solarsystemid2 != activity.solar_system_id:
            eve.Message('MercenaryDen_MustBeInShipInSolarsystem')
            return
        try:
            activity = self._repository.start_activity(self._activity_id)
        except ActivityValidationFailed:
            eve.Message('MercenaryDen_MustBeInShipInSolarsystem')
            return
        except ActivityAlreadyStarted:
            self.completed = True
            return
        except UnknownActivity:
            eve.Message('MercenaryDen_OperationInvalid')
            return

        eve.Message('MercenaryDen_MTOStartedSuccessfully')
        self.completed = activity.is_started
