#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evemissions\client\ui\agentview.py
from caching import Memoize
from agentinteraction.npccharacterview import NpcCharacterView
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.station.agents.agentDialogueUtil import LocationWrapper
from evemissions.client.ui.standingcont import StandingCont

class AgentView(NpcCharacterView):
    default_name = 'AgentView'
    PORTRAITS_FOLDER_2D = 'res:/UI/Texture/classes/Agents'
    PORTRAITS_FOLDER_VIDEO = 'res:/video/agents'
    HEIGHT_STANDINGS = 42
    HEIGHT_STANDINGS_BAR = 10
    PADDING_STANDINGS_BOTTOM = 15
    V_PADDING_ABOVE_STANDINGS = 60
    PADDING_IMPORTANT_MISSION_TOP = 44
    PADDING_IMPORTANT_MISSION_LEFT = 45
    PADDING_IMPORTANT_MISSION_BETWEEN = 9
    IMPORTANT_MISSION_ICON_WIDTH = 32
    IMPORTANT_MISSION_ICON_HEIGHT = 28
    IMPORTANT_MISSION_FONTSIZE = 14

    def ApplyAttributes(self, attributes):
        super(AgentView, self).ApplyAttributes(attributes)
        self.npc_character_id = self.npc_character.get_id()
        self._agent = sm.GetService('agents').GetAgentMoniker(self.npc_character_id)
        self.standings_container = None
        self.standing_gain = 0.0
        self.standing_effective = 0.0
        self.show_standings = False

    def _build_npc_character_text(self):
        super(AgentView, self)._build_npc_character_text()
        self._build_standings()

    def _build_standings(self):
        if self.standings_container and not self.standings_container.destroyed:
            self.standings_container.Close()
        self.standings_container = StandingCont(name='standings_container', parent=self.inner_cont, align=uiconst.TOBOTTOM_NOPUSH, padding=(self.H_PADDING_CONTENT,
         self.V_PADDING_ABOVE_STANDINGS,
         self.H_PADDING_CONTENT,
         0), idx=0, top=self.V_PADDING_TEXT_TO_BOTTOM, npc_character_id=self.npc_character_id)
        self.standings_container.Hide()

    def _build_important_mission(self):
        self.important_mission_container = Container(name='important_mission_container', parent=self.inner_cont, align=uiconst.TOTOP_NOPUSH, height=self.IMPORTANT_MISSION_ICON_HEIGHT, padding=(self.PADDING_IMPORTANT_MISSION_LEFT,
         self.PADDING_IMPORTANT_MISSION_TOP,
         0,
         0), idx=0)
        self.important_mission_container.Hide()
        sprite_container = Container(name='important_mission_sprite_container', parent=self.important_mission_container, align=uiconst.TOLEFT, width=self.IMPORTANT_MISSION_ICON_WIDTH, padRight=self.PADDING_IMPORTANT_MISSION_BETWEEN)
        Sprite(name='important_mission_sprite', parent=sprite_container, align=uiconst.TOTOP, height=self.IMPORTANT_MISSION_ICON_HEIGHT, texturePath='res:/UI/Texture/Classes/AgentInteraction/ImportantMission.png')
        label_container = Container(name='important_mission_label_container', parent=self.important_mission_container, align=uiconst.TOTOP, height=self.IMPORTANT_MISSION_ICON_HEIGHT)
        Label(name='important_mission_label', parent=label_container, align=uiconst.CENTERLEFT, text='Important mission', fontsize=self.IMPORTANT_MISSION_FONTSIZE, color=Color.WHITE)

    def _get_location_text(self):
        location = _get_agent_location_wrap(self._agent)
        return LocationWrapper(location)

    def update_standings(self, standing_gain, show_standings):
        self.standing_gain = float(standing_gain) if standing_gain > 0.05 else 0.0
        self.standing_effective, _ = sm.GetService('standing').GetEffectiveStandingWithAgent(self.npc_character_id)
        self.show_standings = show_standings
        self._update_standing_numbers()

    def _update_standing_numbers(self):
        self.standings_container.update_with_standings(self.standing_effective, value_with_gains=self.standing_gain)
        text_top = self.standings_container.height + self.standings_container.top
        if self.show_standings:
            self.standings_container.Show()
            text_top += self.V_PADDING_BETWEEN_AGENT_INFO_AND_STANDINGS
        else:
            self.standings_container.Hide()
        if self.container_npc_character_text:
            self.container_npc_character_text.top = text_top

    def _OnResize(self, *args):
        super(AgentView, self)._OnResize(*args)
        self._build_standings()
        self._update_standing_numbers()


@Memoize(60)
def _get_agent_location_wrap(agent):
    location = agent.GetAgentLocationWrap()
    return location
