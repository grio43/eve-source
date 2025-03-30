#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\agents.py
import localization
import logging
import threadutils
from eve.client.script.ui.shared.userentry import AgentEntry
from eve.common.lib.appConst import agentMissionStateAllocated, agentMissionStateOffered, agentTypeAura, agentTypeBasicAgent, agentTypeCareerAgent, agentTypeEpicArcAgent, agentTypeEventMissionAgent, agentTypeFactionalWarfareAgent, agentTypeGenericStorylineMissionAgent, agentTypeHeraldry, agentTypeResearchAgent, agentTypeStorylineMissionAgent, rookieAgentList
from carbonui import uiconst
from carbonui.control.scroll import Scroll
from carbonui.primitives.container import Container
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.util import GetFromClass
logger = logging.getLogger(__name__)
ON_GOING_MISSION = {agentMissionStateAllocated, agentMissionStateOffered}
NORMAL_AGENTS = {agentTypeResearchAgent,
 agentTypeBasicAgent,
 agentTypeEventMissionAgent,
 agentTypeCareerAgent,
 agentTypeFactionalWarfareAgent,
 agentTypeHeraldry}
SPECIAL_AGENTS = {agentTypeGenericStorylineMissionAgent,
 agentTypeStorylineMissionAgent,
 agentTypeEventMissionAgent,
 agentTypeCareerAgent,
 agentTypeEpicArcAgent}
STORYLINE_AGENTS = {agentTypeGenericStorylineMissionAgent, agentTypeStorylineMissionAgent}

class LoadState(object):
    UNLOADED = 1
    LOAD_PENDING = 2
    LOADING = 3
    LOADED = 4


class AgentsPanel(Container):
    __notifyevents__ = ('OnAgentMissionChanged', 'OnStandingSet')
    _initialized = False
    _load_state = LoadState.UNLOADED
    _scroll = None

    def _layout(self):
        self._scroll = Scroll(parent=self, align=uiconst.TOALL)

    @threadutils.threaded
    def _load(self):
        if not self._initialized:
            self._initialized = True
            self._layout()
            sm.RegisterNotify(self)
        is_already_loading = self._load_state in {LoadState.LOADING, LoadState.LOAD_PENDING}
        self._load_state = LoadState.LOAD_PENDING
        if is_already_loading:
            return
        self._scroll.ShowLoading()
        try:
            entries = []
            while self._load_state == LoadState.LOAD_PENDING:
                self._load_state = LoadState.LOADING
                entries = []
                relevant_agents = []
                mission_state_by_agent = {}
                agent_missions = sm.GetService('journal').GetMyAgentJournalDetails()[:1][0]
                for each in agent_missions:
                    mission_state, important_mission, mission_type, mission_name, agent_id, expiration_time, bookmarks, remote_offerable, remote_completable, content_id = each
                    agent = sm.GetService('agents').GetAgentByID(agent_id)
                    mission_state_by_agent[agent_id] = mission_state
                    if mission_state not in ON_GOING_MISSION or agent.agentTypeID in SPECIAL_AGENTS:
                        relevant_agents.append(agent_id)

                agents_in_station = get_agents_in_current_station()
                local_relevant_agents = []
                for agent in agents_in_station:
                    if agent.agentID in relevant_agents:
                        local_relevant_agents.append(agent.agentID)

                if self.destroyed:
                    return
                available, unavailable = find_available_and_unavailable_agents(agents_in_station, local_relevant_agents, relevant_agents)
                relevant_here = list(set().union(available, unavailable))
                timers = sm.GetService('agents').GetAgentTimers(relevant_here)
                agents_to_move = [ agent_id for agent_id in available if timers.get(agent_id, None) ]
                for agent_id in agents_to_move:
                    available.remove(agent_id)
                    unavailable.append(agent_id)

                relevant_nearby = [ agent_id for agent_id in relevant_agents if agent_id not in local_relevant_agents ]
                agents_of_interest = []
                for agent_id in relevant_nearby:
                    agents_of_interest.append(get_agent_entry_with_sort_value(agent_id, mission_state_by_agent.get(agent_id)))

                if agents_of_interest:
                    entries.append(GetFromClass(Header, {'label': localization.GetByLabel('UI/Station/Lobby/AgentsOfInterest')}))
                    entries += SortListOfTuples(agents_of_interest)
                sections = [('UI/Station/Lobby/AvailableToYou', available), ('UI/Station/Lobby/NotAvailableToYou', unavailable)]
                for section_label_path, agents in sections:
                    if agents:
                        text = localization.GetByLabel(section_label_path)
                        entries.append(GetFromClass(Header, {'label': text}))
                        section_entries = []
                        for agent_id in agents:
                            timer = timers.get(agent_id, None)
                            section_entries.append(get_agent_entry_with_sort_value(agent_id, mission_state_by_agent.get(agent_id), timer))

                        entries += SortListOfTuples(section_entries)

            if self.destroyed:
                return
            self._scroll.Load(fixedEntryHeight=40, contentList=entries)
            self._load_state = LoadState.LOADED
        except Exception:
            logger.exception('Failed to load the Agents tab in the lobby window')
        finally:
            if not self._scroll.destroyed:
                self._scroll.HideLoading()

    def LoadPanel(self):
        self._load()

    def OnAgentMissionChanged(self, actionID, agentID):
        if self._load_state != LoadState.UNLOADED:
            self._load()

    def OnStandingSet(self, fromID, toID, rank):
        if self._load_state != LoadState.UNLOADED:
            self._load()


def get_agents_in_current_station():
    if session.stationid:
        return sm.GetService('agents').GetAgentsByStationID()[session.stationid]
    else:
        return []


def get_agent_entry_with_sort_value(agent_id, mission_state, timer = None):
    sort_value = cfg.eveowners.Get(agent_id).name
    entry = GetFromClass(AgentEntry, {'charID': agent_id,
     'missionState': mission_state,
     'timer': timer})
    return (sort_value, entry)


def find_available_and_unavailable_agents(agents_in_station, local_relevant_agents, relevant_agents):
    epic_arc_status_service = sm.RemoteSvc('epicArcStatus')
    standing_service = sm.GetService('standing')
    unavailable_agents = []
    available_agents = []
    for agent in agents_in_station:
        agent_id = agent.agentID
        agent_type_id = agent.agentTypeID
        if agent_id in rookieAgentList:
            continue
        is_limited_to_fac_war = is_limited_to_factional_warfare(agent_type_id, agent.corporationID)
        if agent_type_id in NORMAL_AGENTS:
            standing_is_valid = check_can_use_agent(agent, standing_service)
            have_mission_from_agent = agent_id in relevant_agents
            if not is_limited_to_fac_war and (standing_is_valid or have_mission_from_agent):
                available_agents.append(agent_id)
            else:
                unavailable_agents.append(agent_id)
        elif agent_type_id == agentTypeEpicArcAgent:
            standing_is_valid = check_can_use_agent(agent, standing_service)
            have_mission_from_agent = agent_id in relevant_agents
            epic_agent_available = False
            if have_mission_from_agent:
                epic_agent_available = True
            elif standing_is_valid:
                if agent_id in relevant_agents or epic_arc_status_service.AgentHasEpicMissionsForCharacter(agent_id):
                    epic_agent_available = True
            if epic_agent_available:
                available_agents.append(agent_id)
            else:
                unavailable_agents.append(agent_id)
        if agent_type_id == agentTypeAura:
            continue
        elif agent_type_id in STORYLINE_AGENTS:
            if agent_id in local_relevant_agents:
                available_agents.append(agent_id)
            else:
                unavailable_agents.append(agent_id)

    return (available_agents, unavailable_agents)


def is_limited_to_factional_warfare(agent_type_id, agent_corporation_id):
    if agent_type_id != agentTypeFactionalWarfareAgent:
        return False
    war_faction_id = sm.GetService('facwar').GetCorporationWarFactionID(agent_corporation_id)
    return war_faction_id != session.warfactionid


def check_can_use_agent(agent, standing_service):
    return standing_service.CanUseAgent(agent.factionID, agent.corporationID, agent.agentID, agent.level, agent.agentTypeID)
