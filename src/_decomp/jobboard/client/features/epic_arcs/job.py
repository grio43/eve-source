#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\epic_arcs\job.py
from carbonui.control.contextMenu.menuData import MenuData
import eveicon
import localization
from eve.client.script.ui.shared.epicArcs import epicArcConst
from eve.client.script.ui import eveColor
from metadata import ContentTags
import inventorycommon.const as invConst
import gametime
from evemissions.common.epic_arcs_data import get_epic_arc_restart_interval
from jobboard.client.job import BaseJob
from .card import EpicArcCard, EpicArcListEntry
from .page import EpicArcPage
from jobboard.client import job_board_signals

class EpicArcJob(BaseJob):
    PAGE_CLASS = EpicArcPage
    CARD_CLASS = EpicArcCard
    LIST_ENTRY_CLASS = EpicArcListEntry

    def __init__(self, job_id, provider, epic_arc):
        self._epic_arc = epic_arc
        self._agent = epic_arc.GetActiveAgent()
        content_id = epic_arc.epicArcID
        self._state = epic_arc.GetState()
        super(EpicArcJob, self).__init__(job_id, content_id, provider)

    def update(self, epic_arc = None):
        if epic_arc:
            self._epic_arc = epic_arc
            self._agent = epic_arc.GetActiveAgent()
            if self._state != epic_arc.GetState():
                self._state = epic_arc.GetState()
                job_board_signals.on_job_state_changed(self)
                if self.is_completed:
                    job_board_signals.on_job_completed(self)
        super(EpicArcJob, self).update()

    @property
    def epic_arc_id(self):
        return self.content_id

    @property
    def chapter_ids(self):
        return self._epic_arc.GetChapterIDs()

    @property
    def faction_id(self):
        return self._epic_arc.GetFactionID()

    @property
    def title(self):
        return localization.GetByMessageID(self._epic_arc.nameID)

    @property
    def subtitle(self):
        faction_id = self.faction_id
        if faction_id:
            return cfg.eveowners.Get(faction_id).name
        return ''

    @property
    def tag_line(self):
        return localization.GetByLabel(epicArcConst.FLAVORLINES_BY_EPICARCID[self._epic_arc.epicArcID])

    @property
    def background_image(self):
        return epicArcConst.BACKGROUND_BY_EPICARCID[self._epic_arc.epicArcID]

    @property
    def faction_logo(self):
        return epicArcConst.FACTION_LOGO_BY_EPICARCID[self._epic_arc.epicArcID]

    @property
    def solar_system_id(self):
        return self._agent.solarsystemID

    @property
    def current_progress(self):
        return self._epic_arc.GetNumMissionsCompleted()

    @property
    def target_progress(self):
        return self._epic_arc.GetNumMissions()

    @property
    def progress_percentage(self):
        return self._epic_arc.GetProgressRatio()

    @property
    def complete_time(self):
        return self._epic_arc.GetCompleteTime()

    @property
    def is_replayable(self):
        if self._state != epicArcConst.ARC_COMPLETE:
            return False
        time_since_completion = gametime.GetSecondsSinceWallclockTime(self.complete_time)
        return time_since_completion >= get_epic_arc_restart_interval(self.epic_arc_id) * 60

    @property
    def is_offered(self):
        if self._state == epicArcConst.ARC_AVAILABLE or self.is_replayable:
            return True
        return False

    @property
    def is_active(self):
        return self._state == epicArcConst.ARC_STARTED

    @property
    def is_unavailable(self):
        return self._state == epicArcConst.ARC_UNAVAILABLE

    @property
    def is_completed(self):
        return self._state == epicArcConst.ARC_COMPLETE

    @property
    def agent_id(self):
        return self._agent.agentID

    @property
    def agent_name(self):
        return cfg.eveowners.Get(self.agent_id).name

    @property
    def agent_level(self):
        return self._agent.level

    @property
    def agent_division_id(self):
        return self._agent.divisionID

    @property
    def is_available_in_browse(self):
        if not super(EpicArcJob, self).is_available_in_browse:
            return False
        return self._state in (epicArcConst.ARC_AVAILABLE, epicArcConst.ARC_STARTED) or self.is_replayable

    @property
    def is_available_in_active(self):
        return self.is_active

    @property
    def is_trackable(self):
        return False

    @property
    def is_linkable(self):
        return True

    def get_menu(self):
        data = MenuData()
        data.AddEntry(u'{}: {}'.format(localization.GetByLabel('UI/Agents/Agent'), self.agent_name), subMenuData=sm.GetService('menu').GetMenuFromItemIDTypeID(self.agent_id, invConst.typeCharacter))
        data.entrylist.extend(super(EpicArcJob, self).get_menu().entrylist)
        return data

    def get_buttons(self):
        return [{'icon': eveicon.open_window,
          'on_click': self._open_agency_page,
          'hint': localization.GetByLabel('UI/Opportunities/OpenAgency')}]

    def get_cta_buttons(self):
        if self.is_available_in_active:
            return [{'icon': eveicon.agent_mission,
              'label': localization.GetByLabel('UI/Opportunities/ViewActiveEpicArcMission'),
              'on_click': self._open_active_mission}, {'icon': eveicon.start_conversation,
              'label': localization.GetByLabel('UI/Chat/StartConversationAgent'),
              'on_click': self._open_agent_window}]
        else:
            return [{'icon': eveicon.start_conversation,
              'label': localization.GetByLabel('UI/Chat/StartConversationAgent'),
              'on_click': self._open_agent_window}]

    def get_state_info(self):
        if self.is_offered:
            return {'text': localization.GetByLabel('UI/Agency/EpicArcAvailable'),
             'color': eveColor.WARNING_ORANGE,
             'icon': eveicon.start_conversation}
        if self.is_unavailable:
            return {'text': localization.GetByLabel('UI/Menusvc/MenuHints/Unavailable'),
             'color': eveColor.WARNING_ORANGE,
             'icon': eveicon.close}
        if self.is_completed:
            return {'text': localization.GetByLabel('UI/Agency/EpicArcComplete', completeTime=self.complete_time),
             'color': eveColor.SUCCESS_GREEN,
             'icon': eveicon.checkmark}
        return super(EpicArcJob, self).get_state_info()

    def _get_content_tag_ids(self):
        return [ContentTags.feature_epic_arcs]

    def _open_agency_page(self, *args, **kwargs):
        from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
        from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupEpicArcs
        AgencyWndNew.OpenAndShowContentGroup(contentGroupID=contentGroupEpicArcs)

    def _open_active_mission(self, *args, **kwargs):
        from jobboard.client import open_mission
        active_mission = self._epic_arc.GetActiveMission()
        if active_mission:
            open_mission(active_mission.agentID)

    def _open_agent_window(self, *args, **kwargs):
        sm.GetService('agents').OpenDialogueWindow(agentID=self.agent_id)
