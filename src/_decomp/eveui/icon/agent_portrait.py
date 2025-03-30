#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\icon\agent_portrait.py
import math
import localization
from eve.common.lib import appConst
from eveagent.data import get_agent
from npcs.divisions import get_division_name
from npcs.npccorporations import get_npc_corporation_name
from characterdata.npccharacters import get_npc_character, get_npc_character_name
from eveui import Container
from eveui.icon.character_portrait import CharacterPortrait
from eveui.constants import State, Align
from eveui.primitive.sprite import Sprite
import eveformat.client

class AgentPortrait(Container):
    default_name = 'AgentPortrait'
    default_state = State.pick_children

    def __init__(self, agent_id = None, size = 64, **kwargs):
        kwargs.setdefault('height', size)
        kwargs.setdefault('width', size)
        super(AgentPortrait, self).__init__(**kwargs)
        self._content = Container(parent=self, align=Align.center, width=size, height=size)
        self._construct_locator_icon()
        self._construct_division_icon()
        self._character_portrait = CharacterPortrait(parent=self._content, align=Align.center, size=size)
        self._character_portrait.LoadTooltipPanel = self._LoadTooltipPanel
        self.agent_id = agent_id

    @property
    def agent_id(self):
        return self._character_portrait.character_id

    @agent_id.setter
    def agent_id(self, agent_id):
        if self._character_portrait.character_id == agent_id:
            return
        self._character_portrait.character_id = agent_id
        agent_info = get_agent(agent_id)
        if agent_info:
            if agent_info.agentLocateCharacter:
                self._locator.state = State.disabled
            else:
                self._locator.state = State.hidden
            self._division_icon.texturePath = get_agent_badge(agent_info.agentType, agent_info.agentDivisionID)

    def _construct_locator_icon(self):
        self._locator = Sprite(parent=self._content, state=State.hidden, align=Align.bottom_left, width=37, height=37, rotation=math.pi, texturePath='res:/UI/Texture/classes/agency/ActivityBadges/badge_agentsLocator.png')

    def _construct_division_icon(self):
        self._division_icon = Sprite(parent=self._content, align=Align.top_right, width=37, height=37)

    def _LoadTooltipPanel(self, tooltip_panel, *args):
        if not self.agent_id:
            return
        character_info = get_npc_character(self.agent_id)
        agent_info = character_info.agent
        tooltip_panel.LoadGeneric1ColumnTemplate()
        tooltip_panel.margin = (12, 8, 12, 8)
        tooltip_panel.AddLabelMedium(text=get_npc_character_name(self.agent_id), bold=True)
        tooltip_panel.AddLabelSmall(text=u'{} - {}'.format(get_division_name(agent_info.agentDivisionID), localization.GetByLabel('UI/Agents/AgentEntry/Level', level=agent_info.agentLevel)))
        tooltip_panel.AddLabelSmall(text=get_npc_corporation_name(character_info.corporationID))
        station = cfg.evelocations.Get(character_info.stationID)
        tooltip_panel.AddLabelSmall(text=eveformat.solar_system_with_security_and_jumps(station.solarSystemID))


def get_agent_badge(agent_type, agent_division):
    if agent_type in (appConst.agentTypeStorylineMissionAgent, appConst.agentTypeGenericStorylineMissionAgent):
        return 'res:/UI/Texture/classes/agency/ActivityBadges/badge_storylineMissions.png'
    if agent_type == appConst.agentTypeCareerAgent:
        return 'res:/UI/Texture/classes/agency/ActivityBadges/badge_careerAgents.png'
    if agent_type == appConst.agentTypeResearchAgent:
        return 'res:/UI/Texture/classes/agency/ActivityBadges/badge_agentsResearch.png'
    if agent_division == appConst.corpDivisionSecurity:
        return 'res:/UI/Texture/classes/agency/ActivityBadges/badge_agentsSecurity.png'
    if agent_division == appConst.corpDivisionMining:
        return 'res:/UI/Texture/classes/agency/ActivityBadges/badge_agentsMining.png'
    if agent_division == appConst.corpDivisionDistribution:
        return 'res:/UI/Texture/classes/agency/ActivityBadges/badge_agentsDistribution.png'
