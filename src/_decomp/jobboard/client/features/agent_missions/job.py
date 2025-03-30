#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\agent_missions\job.py
from agentinteraction.textutils import fix_text
import caching
from carbonui.control.contextMenu.menuData import MenuData
import eveicon
from eve.client.script.ui import eveColor
from eve.client.script.ui.station.agents.agentUtil import GetMissionExpirationText
from evemissions.client.data import get_mission
from eveagent.client.link import AgentMissionLinkDragData
from npcs.divisions import get_division_name
import inventorycommon.const as invConst
import localization
from metadata.common.content_tags import ContentTags
from objectives.client.objective_chain import ObjectiveChain
from objectives.common.objective_context import ObjectivesContext
import threadutils
from jobboard.client.job import BaseJob
from .card import AgentMissionCard
from .list_entry import AgentMissionListEntry
from .page import AgentMissionPage
from .info_panel_entry import AgentMissionInfoPanelEntry

class AgentMissionJob(BaseJob):
    PAGE_CLASS = AgentMissionPage
    CARD_CLASS = AgentMissionCard
    LIST_ENTRY_CLASS = AgentMissionListEntry
    INFO_PANEL_ENTRY_CLASS = AgentMissionInfoPanelEntry

    def __init__(self, job_id, provider, agent_mission):
        self._agent_mission = agent_mission
        self._data = None
        self._is_dirty = True
        self._mission_id = agent_mission.mission_id
        self._character_id = session.charid
        self._travel_to_objective_chain = None
        self._objectives_context = None
        super(AgentMissionJob, self).__init__(job_id, self._mission_id, provider)

    def clear(self):
        super(AgentMissionJob, self).clear()
        self._clear_objectives()

    def update(self, flag_dirty = True, mission_state = None, *args, **kwargs):
        if flag_dirty:
            self._is_dirty = True
        if mission_state is not None:
            self._agent_mission.update_state(mission_state)
        super(AgentMissionJob, self).update()

    @property
    def data(self):
        if not self._data:
            self._data = get_mission(self.content_id)
        return self._data

    @property
    def mission_id(self):
        return self._mission_id

    @property
    def agent_id(self):
        return self._agent_mission.agent_id

    @property
    def agent_level(self):
        return self._agent_mission.level

    @property
    def agent_division_id(self):
        return self._agent_mission.division_id

    @property
    def agent_name(self):
        return cfg.eveowners.Get(self.agent_id).name

    @property
    def agent_corporation_id(self):
        return self._agent_mission.corporation_id

    @property
    def agent_faction_id(self):
        return self._agent_mission.faction_id

    @property
    def expiration_time(self):
        return self._agent_mission.expiration_time or None

    @property
    def is_important_mission(self):
        return self._agent_mission.is_important

    @property
    def content_template_id(self):
        return self.data.contentTemplate

    @caching.lazy_property
    def _epic_arc(self):
        if ContentTags.feature_epic_arcs in self.content_tag_ids:
            for epic_arc in sm.GetService('epicArc').GetEpicArcs():
                active_mission = epic_arc.GetActiveMission()
                if not active_mission:
                    continue
                if active_mission.agentID == self.agent_id and active_mission.missionID == self.mission_id:
                    return epic_arc

    @caching.lazy_property
    def epic_arc_job_id(self):
        from jobboard.client import get_job_id, ProviderType
        if not self._epic_arc:
            return None
        return get_job_id(self._epic_arc.epicArcID, ProviderType.EPIC_ARCS)

    @property
    def state(self):
        return self._agent_mission.state

    @property
    def title(self):
        return localization.GetByMessageID(self.data.nameID)

    @property
    def subtitle(self):
        if self._epic_arc:
            return localization.GetByMessageID(self._epic_arc.nameID)
        return u'%s - %s' % (self.division_name, localization.GetByLabel('UI/Agents/AgentEntry/Level', level=self.agent_level))

    @property
    def division_name(self):
        return get_division_name(self.agent_division_id)

    @property
    def description(self):
        if self._agent_mission.is_offered() and self._agent_mission.get_message_id('messages.mission.offered.agentsays'):
            return self._get_message('messages.mission.offered.agentsays')
        return self._get_message('messages.mission.briefing')

    @property
    def extra_information(self):
        body = self._get_message('messages.mission.extrainfo.body')
        if body:
            header = self._get_message('messages.mission.extrainfo.header')
            return (header, body)
        else:
            return None

    @property
    def objectives(self):
        return self._agent_mission.objectives

    @property
    def objectives_type(self):
        return self._agent_mission.objectives_type

    @property
    def rewards(self):
        return self._agent_mission.normal_rewards

    @property
    def bonus_rewards(self):
        return self._agent_mission.bonus_rewards

    @property
    def granted_items(self):
        return self._agent_mission.granted_items

    @property
    def collateral(self):
        return self._agent_mission.collateral

    @property
    def bookmarks(self):
        active_mission = self.active_mission_controller
        if active_mission:
            return self.active_mission_controller.bookmarks
        return []

    @property
    def accepted_timestamp(self):
        for bookmark in self.bookmarks:
            if 'created' in bookmark:
                return bookmark['created']

    @property
    def objective_chain(self):
        active_mission = self.active_mission_controller
        if active_mission:
            self._stop_travel_objective_chain()
            return self.active_mission_controller.objective_chain
        self._start_travel_objective_chain()
        return self._travel_to_objective_chain

    @property
    def is_dirty(self):
        return self._is_dirty

    @property
    def is_linkable(self):
        return bool(session.fleetid)

    def get_drag_data(self):
        if not self.is_linkable:
            return []
        return [AgentMissionLinkDragData(self.agent_id, self._character_id, self.content_id)]

    @property
    def is_trackable(self):
        return self._agent_mission.is_active() and not self._agent_mission.is_expired()

    @property
    def is_available_in_active(self):
        return self.is_accepted or self.is_tracked

    @property
    def is_available_in_browse(self):
        if not super(AgentMissionJob, self).is_available_in_browse:
            return False
        return self._agent_mission.is_active() and not self._agent_mission.is_expired()

    @property
    def is_accepted(self):
        return self._agent_mission.is_accepted()

    @property
    def is_completed(self):
        return self._agent_mission.is_completed()

    @property
    def is_expired(self):
        return self._agent_mission.is_expired()

    @property
    def is_offered(self):
        return self._agent_mission.is_offered()

    @property
    def are_objectives_complete(self):
        if self.active_mission_controller:
            return self.active_mission_controller.are_objectives_complete
        return False

    @property
    def in_valid_ship(self):
        return self._agent_mission.can_run_in_current_ship()

    @property
    def ship_restrictions(self):
        return self._agent_mission.get_ship_restrictions()

    @property
    def dungeon_id(self):
        return self._agent_mission.dungeon_id

    @property
    def solar_system_id(self):
        return self._agent_mission.agent.solarsystemID

    @property
    def location_id(self):
        return self._agent_mission.agent.stationID or self._agent_mission.agent.solarsystemID

    @property
    def active_mission_controller(self):
        return sm.GetService('missionObjectivesTracker').agentMissions.get(self.agent_id)

    def on_tracked(self):
        self._clear_objectives()
        self._start_travel_objective_chain()

    def on_untracked(self):
        self._clear_objectives()

    def _start_travel_objective_chain(self):
        if not self.active_mission_controller and not self._travel_to_objective_chain:
            self._objectives_context = ObjectivesContext()
            self._objectives_context.set_values(agent_id=self.agent_id)
            objective_chain = ObjectiveChain(content_id=52, context=self._objectives_context)
            objective_chain.start()
            self._travel_to_objective_chain = objective_chain

    def _stop_travel_objective_chain(self):
        active_mission = self.active_mission_controller
        if active_mission:
            if self._travel_to_objective_chain:
                self._travel_to_objective_chain.stop()
                self._travel_to_objective_chain = None

    def _clear_objectives(self):
        if self._travel_to_objective_chain:
            self._travel_to_objective_chain.stop()
            self._travel_to_objective_chain = None
        if self._objectives_context:
            self._objectives_context.clear()
            self._objectives_context = None

    def get_menu(self):
        from evemissions.client import qa_tools
        data = MenuData()
        data.entrylist.extend(qa_tools.get_agent_mission_context_menu(self.content_id, self.agent_id, objective_chain=self._travel_to_objective_chain))
        data.AddEntry(u'{}: {}'.format(localization.GetByLabel('UI/Agents/Agent'), self.agent_name), subMenuData=sm.GetService('menu').GetMenuFromItemIDTypeID(self.agent_id, invConst.typeCharacter))
        data.entrylist.extend(super(AgentMissionJob, self).get_menu().entrylist)
        return data

    def get_cta_buttons(self):
        buttons = [{'icon': eveicon.start_conversation,
          'label': localization.GetByLabel('UI/Chat/StartConversationAgent'),
          'on_click': self._open_agent_window}]
        if self.epic_arc_job_id:
            buttons.append({'icon': eveicon.epic_arc,
             'label': localization.GetByLabel('UI/Opportunities/ViewEpicArc'),
             'on_click': self._open_epic_arc})
        return buttons

    def construct_page(self, *args, **kwargs):
        self.update_objective_info()
        return super(AgentMissionJob, self).construct_page(*args, **kwargs)

    def get_state_info(self):
        if self.is_expired:
            return {'text': localization.GetByLabel('UI/Generic/Expired'),
             'color': eveColor.DANGER_RED,
             'icon': eveicon.hourglass}
        if self.is_offered:
            return {'text': localization.GetByLabel('UI/Journal/JournalWindow/Agents/StateOffered'),
             'color': eveColor.WARNING_ORANGE,
             'icon': eveicon.start_conversation}
        if self.are_objectives_complete:
            return {'text': localization.GetByLabel('UI/Opportunities/ObjectivesComplete'),
             'color': eveColor.SUCCESS_GREEN,
             'icon': eveicon.checkmark}
        return super(AgentMissionJob, self).get_state_info()

    def has_expiration_time(self):
        return self._agent_mission.has_expiration_time()

    def get_expiration_text(self, *args, **kwargs):
        return GetMissionExpirationText(missionState=self.state, expirationTime=self._agent_mission.expiration_time, short=False)

    def _open_agent_window(self, *args, **kwargs):
        sm.GetService('agents').OpenDialogueWindow(agentID=self.agent_id)

    def _open_epic_arc(self, *args, **kwargs):
        if self.epic_arc_job_id:
            self.service.open_job(self.epic_arc_job_id)

    def _get_content_tag_ids(self):
        result = [ContentTags.feature_agent_missions]
        mission_tag_ids = self._agent_mission.content_tag_ids
        if mission_tag_ids:
            result.extend(mission_tag_ids)
        else:
            result.extend(content_tags_by_agent_mission_template.get(self.content_template_id, []))
        return result

    @caching.lazy_property
    def _message_arguments(self):
        agents_service = sm.GetService('agents')
        result = {}
        mission_message_id = (self.agent_id, self.content_id)
        if mission_message_id not in agents_service.missionArgs:
            agents_service.PrimeMessageArguments(self.agent_id, self.content_id)
        result.update(agents_service.missionArgs.get(mission_message_id, {}))
        result.update(agents_service.agentArgs.get(self.agent_id, {}))
        return result

    def update_objective_info(self):
        if not self._is_dirty:
            return
        self._is_dirty = False
        self._update_objective_info()

    @threadutils.threaded
    def _update_objective_info(self):
        objective_info = self._get_objective_info() or {}
        if not self._agent_mission.accept_time and not self._agent_mission.is_offered():
            accepted_timestamp = None
            for bookmark in self.bookmarks:
                if 'created' in bookmark:
                    accepted_timestamp = bookmark['created']
                    break

            self._agent_mission.accept_time = accepted_timestamp
        self._agent_mission.update_objective_info(objective_info)
        self.update(flag_dirty=False)

    def _get_objective_info(self):
        agent = sm.GetService('agents').GetAgentMoniker(self.agent_id)
        return agent.GetMissionObjectiveInfo(ignoreLocateCheck=True)

    def _get_message(self, message_key):
        message_id = self._agent_mission.get_message_id(message_key)
        if not message_id:
            return ''
        return fix_text(localization.GetByMessageID(message_id, **self._message_arguments))

    def _get_relevance_override_weights(self):
        return {ContentTags.feature_epic_arcs: 20 if ContentTags.feature_epic_arcs in self.content_tag_ids else 10}

    def _check_keywords(self, keywords):
        result = super(AgentMissionJob, self)._check_keywords(keywords)
        if not result:
            agent_name = self.agent_name.lower()
            for keyword in keywords:
                if keyword in agent_name:
                    continue
                return False

            return True
        else:
            return True


class FleetMembersAgentMissionJob(AgentMissionJob):

    def __init__(self, job_id, provider, agent_mission, character_id):
        super(FleetMembersAgentMissionJob, self).__init__(job_id, provider, agent_mission)
        self._character_id = character_id

    @property
    def is_trackable(self):
        return False

    @property
    def is_available_in_active(self):
        return False

    @property
    def is_available_in_browse(self):
        return False

    @caching.lazy_property
    def _message_arguments(self):
        result = super(FleetMembersAgentMissionJob, self)._message_arguments
        result['player'] = self._character_id
        return result

    def get_cta_buttons(self):
        return []

    def get_state_info(self):
        return {'text': localization.GetByLabel('UI/Opportunities/OtherCharactersOpportunity', characterID=self._character_id),
         'color': eveColor.WARNING_ORANGE,
         'icon': eveicon.person}

    def _get_objective_info(self):
        agent = sm.GetService('agents').GetAgentMoniker(self.agent_id)
        return agent.GetMissionObjectiveInfo(charID=self._character_id, ignoreLocateCheck=True)


content_tags_by_agent_mission_template = {'agent.missionTemplatizedContent_BasicCourierMission': [ContentTags.career_path_industrialist, ContentTags.activity_hauling],
 'agent.missionTemplatizedContent_StorylineCourierMission': [ContentTags.career_path_industrialist, ContentTags.activity_hauling],
 'agent.missionTemplatizedContent_GenericStorylineCourierMission': [ContentTags.career_path_industrialist, ContentTags.activity_hauling],
 'agent.missionTemplatizedContent_ResearchCourierMission': [ContentTags.career_path_industrialist, ContentTags.activity_hauling],
 'agent.missionTemplatizedContent_BasicTradeMission': [ContentTags.career_path_industrialist, ContentTags.activity_trading, ContentTags.activity_hauling],
 'agent.missionTemplatizedContent_StorylineTradeMission': [ContentTags.career_path_industrialist, ContentTags.activity_trading, ContentTags.activity_hauling],
 'agent.missionTemplatizedContent_GenericStorylineTradeMission': [ContentTags.career_path_industrialist, ContentTags.activity_trading, ContentTags.activity_hauling],
 'agent.missionTemplatizedContent_ResearchTradeMission': [ContentTags.career_path_industrialist, ContentTags.activity_trading, ContentTags.activity_hauling],
 'agent.missionTemplatizedContent_BasicKillMission': [ContentTags.career_path_enforcer, ContentTags.activity_combat],
 'agent.missionTemplatizedContent_StorylineKillMission': [ContentTags.career_path_enforcer, ContentTags.activity_combat],
 'agent.missionTemplatizedContent_GenericStorylineKillMission': [ContentTags.career_path_enforcer, ContentTags.activity_combat],
 'agent.missionTemplatizedContent_ResearchKillMission': [ContentTags.career_path_enforcer, ContentTags.activity_combat],
 'agent.missionTemplatizedContent_BasicMiningMission': [ContentTags.career_path_industrialist,
                                                        ContentTags.career_path_enforcer,
                                                        ContentTags.activity_mining,
                                                        ContentTags.activity_combat],
 'agent.missionTemplatizedContent_StorylineAgentInteractionMission': [ContentTags.career_path_enforcer,
                                                                      ContentTags.career_path_explorer,
                                                                      ContentTags.career_path_industrialist,
                                                                      ContentTags.activity_travel],
 'agent.missionTemplatizedContent_EpicArcKillMission': [ContentTags.feature_epic_arcs, ContentTags.career_path_enforcer, ContentTags.activity_combat],
 'agent.missionTemplatizedContent_EpicArcAgentInteractionMission': [ContentTags.feature_epic_arcs,
                                                                    ContentTags.career_path_enforcer,
                                                                    ContentTags.career_path_explorer,
                                                                    ContentTags.career_path_industrialist,
                                                                    ContentTags.activity_travel],
 'agent.missionTemplatizedContent_EpicArcTalkToAgentMission': [ContentTags.feature_epic_arcs,
                                                               ContentTags.career_path_enforcer,
                                                               ContentTags.career_path_explorer,
                                                               ContentTags.career_path_industrialist,
                                                               ContentTags.activity_travel],
 'agent.missionTemplatizedContent_EpicArcCourierMission': [ContentTags.feature_epic_arcs, ContentTags.career_path_industrialist, ContentTags.activity_hauling],
 'agent.missionTemplatizedContent_EpicArcTradeMission': [ContentTags.feature_epic_arcs,
                                                         ContentTags.career_path_industrialist,
                                                         ContentTags.activity_trading,
                                                         ContentTags.activity_hauling],
 'agent.missionTemplatizedContent_HeraldryMission': [ContentTags.career_path_industrialist,
                                                     ContentTags.feature_paragon_missions,
                                                     ContentTags.activity_trading,
                                                     ContentTags.activity_hauling]}
