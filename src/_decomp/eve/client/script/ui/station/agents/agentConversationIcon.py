#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\agents\agentConversationIcon.py
import eveicon
from eve.client.script.ui import eveColor
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.station.agents.agentUtil import IsAgentAvailable, GetAgentStartConversationHint
from uthread2 import StartTasklet
COLOR_UNAVAILABLE = eveColor.DANGER_RED

class AgentConversationIcon(ButtonIcon):
    default_name = 'AgentConversationIcon'
    default_texturePath = eveicon.chat_bubble
    default_width = 24
    default_height = 24

    def ApplyAttributes(self, attributes):
        ButtonIcon.ApplyAttributes(self, attributes)
        agentID = attributes.agentID
        self.func = self.InteractWithAgent
        self.SetAgentID(agentID)

    def SetAgentID(self, agentID):
        self.agentID = agentID
        StartTasklet(self._SetColorForAgent, agentID)

    def _SetColorForAgent(self, agentID):
        color = self.default_iconColor if IsAgentAvailable(agentID) else COLOR_UNAVAILABLE
        self.SetIconColor(color)

    def InteractWithAgent(self):
        return sm.GetService('agents').OpenDialogueWindow(self.agentID)

    def GetHint(self):
        return GetAgentStartConversationHint(self.agentID)
