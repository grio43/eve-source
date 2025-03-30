#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\agent_missions\info_panel_entry.py
import carbonui
import eveui
from eve.client.script.ui.shared.infoPanels.infoPanelAgentMissions import InfoPanelAgentMissionData
from objectives.client.ui.objective_chain import ObjectiveChainEntry
from objectives.client.ui.objective import CompletedLine
from jobboard.client.ui.info_panel_entry import JobInfoPanelEntry
from eve.client.script.ui.control.statefulButton import StatefulButton
import uthread2

class AgentMissionInfoPanelEntry(JobInfoPanelEntry):
    __notifyevents__ = ['OnClientEvent_WarpFinished', 'OnBallparkSetState', 'OnSessionChanged']

    def __init__(self, job, on_click, *args, **kwargs):
        self._subscribed_to_active_mission = False
        super(AgentMissionInfoPanelEntry, self).__init__(job, on_click, *args, **kwargs)

    def _register(self):
        super(AgentMissionInfoPanelEntry, self)._register()
        self._register_to_active_mission()
        sm.RegisterNotify(self)

    def _unregister(self):
        super(AgentMissionInfoPanelEntry, self)._unregister()
        self._unregister_from_active_mission()
        sm.UnregisterNotify(self)

    def _register_to_active_mission(self):
        if not self._subscribed_to_active_mission and self.job:
            active_mission_controller = self.job.active_mission_controller
            if active_mission_controller and not active_mission_controller.objective_chain:
                self._subscribed_to_active_mission = True
                active_mission_controller.on_objective_changed.connect(self._refresh)

    def _unregister_from_active_mission(self):
        if self.job and self._subscribed_to_active_mission:
            active_mission_controller = self.job.active_mission_controller
            if active_mission_controller and not active_mission_controller.objective_chain:
                active_mission_controller.on_objective_changed.disconnect(self._refresh)
            self._subscribed_to_active_mission = False

    def _on_job_updated(self):
        if self._subscribed_to_active_mission:
            self._update_state_info_line()
        else:
            self._register_to_active_mission()
            self._refresh()

    def OnClientEvent_WarpFinished(self, *args, **kwargs):
        self._refresh()

    def OnSessionChanged(self, is_remote, session, change):
        if 'locationid' in change:
            self._refresh()

    def OnBallparkSetState(self, *args, **kwargs):
        self._refresh()

    @uthread2.debounce(0.5)
    def _refresh(self, *args, **kwargs):
        if self.destroyed or not self.job:
            return
        if self._expanded:
            self._reconstruct_body()

    @eveui.skip_if_destroyed
    def _construct_body(self):
        if self._objective_chain_entry:
            self._objective_chain_entry.Close()
            self._objective_chain_entry = None
        active_mission_controller = self.job.active_mission_controller
        objective_chain = self.job.objective_chain
        if active_mission_controller and not active_mission_controller.objective_chain:
            mission_data = InfoPanelAgentMissionData(self.job.title, self.job.agent_id, self.job.content_id, self.job.bookmarks, objective_chain)
            for objectiveIndex, objective in enumerate(mission_data.objectives):
                if not objective.IsActive() and not objective.GetHeaderText():
                    continue
                OldStyleAgentMissionObjectiveEntry(parent=self._content_container, objective=objective, padTop=4)

        elif objective_chain:
            self._objective_chain_entry = ObjectiveChainEntry(parent=self._content_container, objective_chain=objective_chain)


class OldStyleAgentMissionObjectiveEntry(eveui.ContainerAutoSize):
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top
    default_state = eveui.State.normal
    default_bgColor = (0, 0, 0, 0.25)

    def __init__(self, objective, *args, **kwargs):
        super(OldStyleAgentMissionObjectiveEntry, self).__init__(*args, **kwargs)
        self._objective = objective
        self._layout()

    def _layout(self):
        container = eveui.ContainerAutoSize(name='wrapper', parent=self, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, padding=8)
        header_container = eveui.ContainerAutoSize(name='header', parent=container, align=eveui.Align.to_top, alignMode=eveui.Align.to_top)
        if not self._objective.IsActive():
            CompletedLine(parent=header_container, left=-8)
        eveui.EveLabelLarge(name='title', parent=header_container, align=eveui.Align.to_top, text=self._objective.GetHeaderText(), maxLines=2)
        if not self._objective.IsActive():
            return
        task_container = eveui.ContainerAutoSize(name='task_container', parent=container, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, padTop=4, opacity=0)
        if self._objective.HasText():
            if self._objective.HasIcon():
                icon_size = self._objective.GetObjectiveIconSize()
                icon_container = eveui.Container(parent=task_container, align=eveui.Align.to_left, width=icon_size, left=2, top=2)
                self._objective.BuildIcon(name='mission_objective_icon', parent=icon_container, align=eveui.Align.center, state=eveui.State.normal, opacity=0.7, width=icon_size, height=icon_size)
            title_container = eveui.ContainerAutoSize(parent=task_container, align=eveui.Align.to_top, padLeft=8)
            eveui.EveLabelMedium(parent=title_container, align=eveui.Align.to_top, state=eveui.State.normal, text=self._objective.GetText(), linkStyle=carbonui.uiconst.LINKSTYLE_SUBTLE)
        buttons_container = eveui.ContainerAutoSize(name='buttons_container', parent=task_container, align=eveui.Align.to_top, alignMode=eveui.Align.to_top)
        StatefulButton(name=self._objective.GetLocationButtonName(), parent=buttons_container, align=eveui.Align.to_top, controller=self._objective, state=eveui.State.hidden, density=carbonui.Density.COMPACT, frame_type=carbonui.ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT, padTop=4)
        eveui.fade_in(task_container, duration=0.5)
