#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\careerControllerUI.py
from carbonui.uicore import uicore
import eve.client.script.ui.shared.careerPortal.careerConst as careerConst
import eve.client.script.ui.shared.careerPortal.uiSettings as careerSettings
from careergoals.client.feature_flag import is_air_career_program_enabled
from careergoals.client.signal import on_air_career_program_availability_changed
from eve.client.script.ui.shared.careerPortal.cpSignals import on_cp_goal_tracking_added, on_cp_goal_tracking_removed
from careergoals.client.career_goal_svc import get_career_goals_svc
from eve.client.script.ui.shared.subtitles import GetSubtitlePathForVideo
from eve.client.script.ui.shared.videowindow import VideoPlayerWindow
_instance = None

def get_career_portal_controller_svc():
    global _instance
    if _instance is None:
        _instance = _CareerControllerUI()
    return _instance


class _CareerControllerUI(object):
    __notifyevents__ = ['OnCharacterSessionChanged', 'OnSessionReset']

    def __init__(self):
        self._reset_for_character()
        on_air_career_program_availability_changed.connect(self._on_air_career_program_availability_changed)
        sm.RegisterNotify(self)

    def __del__(self):
        on_air_career_program_availability_changed.disconnect(self._on_air_career_program_availability_changed)

    def OnCharacterSessionChanged(self, _oldCharacterID, _newCharacterID):
        if _newCharacterID is not None:
            self._reset_for_character()

    def OnSessionReset(self):
        self._reset_for_character()

    def _reset_for_character(self):
        self._tracked_goal_ids = careerSettings.GetTrackedGoalsFromSettings(set())

    def select_career(self, career_path_id, goal_id):
        careerConst.SELECTED_CAREER_PATH_SETTING.set(career_path_id)
        careerConst.CAREER_WINDOW_STATE_SETTING.set(careerConst.CareerWindowState.ACTIVITIES_VIEW)
        get_career_goals_svc().emit_career_selected(goal_id)

    def select_activity(self, activity_id, activity_name, career_path_id):
        careerConst.SELECTED_ACTIVITY_SETTING.set(activity_id)
        careerConst.CAREER_WINDOW_STATE_SETTING.set(careerConst.CareerWindowState.GOALS_VIEW)
        get_career_goals_svc().emit_group_selected(activity_name, careerConst.GetCareerPathName(career_path_id))

    def select_goal(self, goal_id):
        careerConst.SELECTED_GOAL_SETTING.set(goal_id)
        if goal_id:
            get_career_goals_svc().emit_goal_selected(goal_id)

    def is_goal_tracked(self, goal_id):
        return goal_id in self._tracked_goal_ids

    def track_goal(self, goal_id):
        self._tracked_goal_ids.clear()
        self._tracked_goal_ids.add(goal_id)
        careerSettings.StoreTrackedGoalsInSettings(self._tracked_goal_ids)
        get_career_goals_svc().emit_goal_tracked(goal_id)
        on_cp_goal_tracking_added(goal_id)

    def untrack_goal(self, goal_id):
        self._tracked_goal_ids.clear()
        self._tracked_goal_ids.discard(goal_id)
        careerSettings.StoreTrackedGoalsInSettings(self._tracked_goal_ids)
        on_cp_goal_tracking_removed(goal_id)

    def get_tracked_goals(self):
        return self._tracked_goal_ids

    def _on_air_career_program_availability_changed(self, *args):
        if not is_air_career_program_enabled():
            tracked_goals = [ g for g in self._tracked_goal_ids ]
            for g in tracked_goals:
                self.untrack_goal(g)

    def play_video(self, video_path):
        if not video_path:
            return
        self._video_wnd = VideoPlayerWindow.Open(isMinimizable=False)
        self._video_wnd.SetSize(uicore.desktop.width / 2, uicore.desktop.height / 2)
        self._video_wnd.SetVideoPath(video_path, subtitles=GetSubtitlePathForVideo(video_path, session.languageID))
        self._video_wnd.SetVideoFinishedCallback(self._on_video_finished)
        self._video_wnd.ShowModal()

    def _on_video_finished(self):
        if self._video_wnd:
            self._video_wnd.Close()
