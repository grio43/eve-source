#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\agent.py
from characterdata.npccharacters import get_npc_character_name
import eveicon
import localization
from objectives.client.objective_task.base import ObjectiveTask
from objectives.client.ui.objective_task_widget import ButtonTaskWidget

class TalkToAgentTask(ObjectiveTask):
    objective_task_content_id = 8
    BUTTON_WIDGET = ButtonTaskWidget

    def __init__(self, agent_id = None, **kwargs):
        super(TalkToAgentTask, self).__init__(**kwargs)
        self._agent_id = None
        self.agent_id = agent_id

    @property
    def agent_id(self):
        return self._agent_id

    @agent_id.setter
    def agent_id(self, value):
        if self._agent_id == value:
            return
        self._agent_id = value
        self._title = get_npc_character_name(self._agent_id)
        self.update()

    @property
    def button_label(self):
        return localization.GetByLabel('UI/Chat/StartConversationAgent')

    @property
    def button_icon(self):
        return eveicon.start_conversation

    def double_click(self):
        sm.GetService('agents').OpenDialogueWindow(self.agent_id)

    def get_context_menu(self):
        return sm.GetService('menu').CharacterMenu(self.agent_id)
