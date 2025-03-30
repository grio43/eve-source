#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\agent.py
from .base import Event

class AgentMissionChanged(Event):
    atom_id = 155
    __notifyevents__ = ['OnAgentMissionChanged']

    def OnAgentMissionChanged(self, mission_state, agent_id):
        self.invoke(agent_id=agent_id, mission_state=mission_state)
