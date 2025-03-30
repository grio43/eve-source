#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\abyss.py
from eve.common.script.sys.idCheckers import IsAbyssalSpaceSystem
from inventorycommon.const import groupWarpGate
from objectives.client.objective_task.target import TargetTask

class JumpThroughAbyssGate(TargetTask):
    objective_task_content_id = 56
    __notifyevents__ = ['OnClientEvent_JumpStarted']

    def _start(self):
        super(JumpThroughAbyssGate, self)._start()
        self._update_target()

    def _stop(self):
        self.target = None
        super(JumpThroughAbyssGate, self)._stop()

    def _update_target(self):
        self.target = None
        self.completed = False
        if self.is_active and IsAbyssalSpaceSystem(session.solarsystemid2):
            self.target = {'group_id': groupWarpGate}

    def OnClientEvent_JumpStarted(self, gate_id, destination_id):
        if gate_id == self.item_id:
            self.completed = True
