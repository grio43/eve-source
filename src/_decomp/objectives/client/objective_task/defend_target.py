#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\defend_target.py
from objectives.client.objective_task.destroy_target import DestroyTargetTask, DestroyTargetsTask, DestroyTargetTaskGroup
from objectives.client.ui.objective_task_widget import FriendlyTargetWidget

class DefendTargetTask(DestroyTargetTask):
    WIDGET = FriendlyTargetWidget

    def _update_complete_state(self):
        pass


class DefendTargetsTask(DestroyTargetsTask):
    objective_task_content_id = 53
    TASK = DefendTargetTask


class DefendTargetTaskGroup(DestroyTargetTaskGroup):
    objective_task_content_id = 6
    TASK = DefendTargetTask
