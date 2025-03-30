#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective\scanning.py
from objectives.client.objective.base import Objective

class ScanSignatureObjective(Objective):
    objective_content_id = 14

    def _task_state_changed(self, objective_task, reason):
        if objective_task.task_id == 'scan_signature' and reason == 'on_complete':
            self.update_value('scan_result', objective_task.scan_result)
        super(ScanSignatureObjective, self)._task_state_changed(objective_task, reason)
