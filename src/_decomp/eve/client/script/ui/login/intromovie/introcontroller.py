#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\intromovie\introcontroller.py
from eve.client.script.ui.view.viewStateConst import ViewState
from localization import GetByLabel
from uihider import get_ui_hider

class IntroController(object):

    def __init__(self):
        self.character_id = None
        self.is_game_loaded = False
        self.is_intro_playing = False
        self.is_intro_stopped = False
        self.intro_video = None
        self.black_overlay = None
        sm.RegisterForNotifyEvent(self, 'OnSessionReset')
        self.start_listening_to_startup_events()

    def start_listening_to_startup_events(self):
        sm.RegisterForNotifyEvent(self, 'OnCurrSessionSpaceEnteredFirstTime')
        sm.RegisterForNotifyEvent(self, 'OnViewStateChanged')

    def stop_listening_to_startup_events(self):
        sm.UnregisterForNotifyEvent(self, 'OnCurrSessionSpaceEnteredFirstTime')
        sm.UnregisterForNotifyEvent(self, 'OnViewStateChanged')

    def play_intro(self, character_id, skip_tutorial):
        self.character_id = character_id
        if skip_tutorial:
            self.transition_directly_to_game()
        else:
            get_ui_hider().hide_everything()
            if self._should_play_intro_video():
                self.play_intro_video()
            else:
                self.transition_directly_to_game()

    def stop_intro(self):
        self._clear_intro()
        self._reset_state()

    def on_video_stopped(self):
        self.is_intro_stopped = True
        if self.is_game_loaded:
            self.transition_from_end_of_video_to_game()
        else:
            self.wait_for_game_to_load()

    def OnCurrSessionSpaceEnteredFirstTime(self):
        self.is_game_loaded = True
        if self.is_intro_stopped:
            self.transition_from_middle_of_video_to_game()
        self._notify_if_intro_completed()

    def OnViewStateChanged(self, from_view, to_view):
        if from_view not in (ViewState.CharacterSelector, ViewState.CharacterCreation):
            return
        if to_view in (ViewState.Station,
         ViewState.Hangar,
         ViewState.StarMap,
         ViewState.DockPanel,
         ViewState.SystemMap,
         ViewState.Planet,
         ViewState.ShipTree,
         ViewState.Structure):
            self.is_game_loaded = True
            self._notify_if_intro_completed()

    def OnSessionReset(self):
        self._reset_state()

    def _reset_state(self):
        self.is_intro_playing = False
        self.is_game_loaded = False
        self.is_intro_stopped = False
        self.start_listening_to_startup_events()

    def _notify_intro_started(self):
        sm.ScatterEvent('OnIntroStarted')

    def _notify_if_intro_completed(self):
        if self.is_game_loaded and not self.is_intro_playing:
            sm.ScatterEvent('OnIntroCompleted')
            self.stop_listening_to_startup_events()

    def _should_play_intro_video(self):
        return settings.public.generic.Get('showIntroVideo', 1)

    def _is_ui_available(self, ui_container):
        return ui_container and not ui_container.destroyed

    def play_intro_video(self):
        self.is_intro_playing = True
        self._notify_intro_started()
        from eve.client.script.ui.login.intromovie.ui.blackoverlay import BlackOverlay
        from eve.client.script.ui.login.intromovie.ui.introvideo import IntroVideo
        self.intro_video = IntroVideo(onStopCallback=self.on_video_stopped)
        self.black_overlay = BlackOverlay()

    def transition_from_middle_of_video_to_game(self):
        if self._is_ui_available(self.black_overlay):
            self.black_overlay.fade_in(callback=self._exit_intro)
        self._show_loading_ui()

    def transition_from_end_of_video_to_game(self):
        if self._is_ui_available(self.black_overlay):
            self.black_overlay.fade_in(callback=self._exit_intro)

    def transition_directly_to_game(self):
        self._exit_intro()
        self._show_loading_ui()

    def wait_for_game_to_load(self):
        if self._is_ui_available(self.black_overlay):
            self.black_overlay.fade_in(callback=self._stop_intro_video)
        self._show_loading_ui()

    def _stop_intro_video(self):
        if self.intro_video and not self.intro_video.destroyed:
            self.intro_video.StopMovie()

    def _exit_intro(self):
        self._clear_intro()
        self.is_intro_playing = False
        self._notify_if_intro_completed()

    def _clear_intro(self):
        for ui_container in [self.intro_video, self.black_overlay]:
            if self._is_ui_available(ui_container):
                ui_container.Close()

        self._update_cursor()
        self._hide_loading_ui()

    def _update_cursor(self):
        sm.GetService('ui').ForceCursorUpdate()

    def _show_loading_ui(self):
        sm.GetService('loading').ProgressWnd(title=GetByLabel('UI/CharacterCreation'), strng=GetByLabel('UI/CharacterCreation/EnteringGameAs', player=self.character_id), portion=1, total=2)

    def _hide_loading_ui(self):
        sm.GetService('loading').EndLoading()
