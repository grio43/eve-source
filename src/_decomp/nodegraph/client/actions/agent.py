#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\agent.py
from .base import Action
from characterdata.npccharacters import get_npc_character_name

class StartAgentConversation(Action):
    atom_id = 475

    def __init__(self, agent_id = None, **kwargs):
        super(StartAgentConversation, self).__init__(**kwargs)
        self.agent_id = agent_id

    def start(self, **kwargs):
        super(StartAgentConversation, self).start(**kwargs)
        if self.agent_id:
            sm.GetService('agents').OpenDialogueWindow(self.agent_id)

    @classmethod
    def get_subtitle(cls, agent_id = None, **kwargs):
        if agent_id:
            return get_npc_character_name(agent_id, language_id='en')
        return ''
