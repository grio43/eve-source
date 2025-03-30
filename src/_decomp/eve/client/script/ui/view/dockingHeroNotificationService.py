#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\dockingHeroNotificationService.py
import datetime
import gametime
import langutils
import localization
import uthread2
import weakref
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import fontconst, TextColor, uiconst
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.heronotification.animation import garble_reveal_label
from eve.client.script.ui.heronotification.golden import GoldenPositionContainerAutoSize
from eve.client.script.ui.heronotification.video import LoopPolicy, SegmentedVideoHeroNotification
from eve.client.script.ui.view.viewStateConst import ViewState
DOCKING_HERO_NOTIFICATION_PRIORITY = 100

class DockingHeroNotificationService(Service):
    __guid__ = 'svc.dockingHeroNotification'
    __servicename__ = 'dockingHeroNotification'
    __startupdependencies__ = ('heroNotification',)
    __notifyevents__ = ('OnDockingAccepted', 'OnUndockingAborted', 'OnUndockingStarted', 'OnViewLoaded')

    def __init__(self):
        self._active_notification_cancellation_tokens = weakref.WeakSet()
        super(DockingHeroNotificationService, self).__init__()

    def GetHeroNotificationPriority(self):
        return DOCKING_HERO_NOTIFICATION_PRIORITY

    def OnDockingAccepted(self, location_id):
        self._show_docking_hero_notification()

    def OnUndockingAborted(self, location_id):
        self._cancel_active_and_pending_hero_notifications()

    def OnUndockingStarted(self, location_id):
        self._show_undocking_hero_notification()

    def OnViewLoaded(self, from_view, to_view):
        if to_view.name != from_view.name:
            self._cancel_active_and_pending_hero_notifications()

    def _show_docking_hero_notification(self):
        cancellation_token = self.heroNotification.play(create_animation(text=localization.GetByLabel('UI/Inflight/Messages/Docking'), letter_space=get_docking_letter_space(), loop_policy=DockingLoopPolicy()), priority=DOCKING_HERO_NOTIFICATION_PRIORITY)
        self._active_notification_cancellation_tokens.add(cancellation_token)

    def _show_undocking_hero_notification(self):
        cancellation_token = self.heroNotification.play(create_animation(text=localization.GetByLabel('UI/Station/Undocking'), letter_space=get_undocking_letter_space(), loop_policy=UndockingLoopPolicy()), priority=DOCKING_HERO_NOTIFICATION_PRIORITY)
        self._active_notification_cancellation_tokens.add(cancellation_token)

    def _cancel_active_and_pending_hero_notifications(self):
        while self._active_notification_cancellation_tokens:
            self._active_notification_cancellation_tokens.pop().cancel()


LETTER_SPACE_DEFAULT = 10
DOCKING_LETTER_SPACE_BY_LANGUAGE_ID = {langutils.LANG_FR: 6,
 langutils.LANG_RU: 4}

def get_docking_letter_space():
    return DOCKING_LETTER_SPACE_BY_LANGUAGE_ID.get(langutils.get_session_language(), LETTER_SPACE_DEFAULT)


UNDOCKING_LETTER_SPACE_BY_LANGUAGE_ID = {langutils.LANG_DE: 4,
 langutils.LANG_ES: 4,
 langutils.LANG_FR: 8,
 langutils.LANG_RU: 4}

def get_undocking_letter_space():
    return UNDOCKING_LETTER_SPACE_BY_LANGUAGE_ID.get(langutils.get_session_language(), LETTER_SPACE_DEFAULT)


class DockingLoopPolicy(LoopPolicy):
    __notifyevents__ = ('OnDockingFinished', 'OnViewLoaded')
    SCENE_LOADING_TIMEOUT = datetime.timedelta(seconds=30)
    LOOPING_TIMEOUT = datetime.timedelta(minutes=1)

    def __init__(self):
        self._view_loaded = False
        self._docking_finished = False
        self._docking_finished_at = None
        self._looping_started_at = None
        super(DockingLoopPolicy, self).__init__()
        ServiceManager.Instance().RegisterNotify(self)

    def should_stop(self):
        now = gametime.now()
        return self._view_loaded or self._docking_finished and now - self._docking_finished_at > self.SCENE_LOADING_TIMEOUT or self._looping_started_at is not None and now - self._looping_started_at > self.LOOPING_TIMEOUT

    def on_start_looping(self):
        self._looping_started_at = gametime.now()
        view_state_service = ServiceManager.Instance().GetService('viewState')
        active_view = view_state_service.GetPrimaryView().name
        if active_view in (ViewState.Hangar, ViewState.Structure):
            self._view_loaded = True

    def dispose(self):
        ServiceManager.Instance().UnregisterNotify(self)

    def OnDockingFinished(self, location_id):
        self._docking_finished = True
        self._docking_finished_at = gametime.now()

    def OnViewLoaded(self, from_view, to_view):
        if to_view.name in (ViewState.Hangar, ViewState.Structure):
            self._view_loaded = True


class UndockingLoopPolicy(LoopPolicy):
    __notifyevents__ = ('OnUndockingAborted', 'OnUndockingCompleted', 'OnUndockingStarted', 'OnViewLoaded')
    SCENE_LOADING_TIMEOUT = datetime.timedelta(seconds=30)
    LOOPING_TIMEOUT = datetime.timedelta(minutes=1)

    def __init__(self):
        self._aborted = False
        self._undocking_completed = False
        self._undocking_completed_at = None
        self._in_space_scene_loaded = False
        self._looping_started_at = None
        self._looping_finished = False
        ServiceManager.Instance().RegisterNotify(self)

    def dispose(self):
        ServiceManager.Instance().UnregisterNotify(self)

    def should_stop(self):
        now = gametime.now()
        return self._aborted or self._in_space_scene_loaded or self._undocking_completed and now - self._undocking_completed_at > self.SCENE_LOADING_TIMEOUT or self._looping_started_at is not None and now - self._looping_started_at > self.LOOPING_TIMEOUT

    def on_start_looping(self):
        self._looping_started_at = gametime.now()
        view_state_service = ServiceManager.Instance().GetService('viewState')
        active_view = view_state_service.GetPrimaryView().name
        if active_view == ViewState.Space:
            self._in_space_scene_loaded = True

    def on_loop_finished(self):
        self._looping_finished = True

    def OnUndockingAborted(self, location_id):
        self._aborted = True

    def OnUndockingCompleted(self, location_id):
        self._undocking_completed = True
        self._undocking_completed_at = gametime.now()

    def OnUndockingStarted(self, location_id):
        if not self._looping_finished:
            self._aborted = False

    def OnViewLoaded(self, from_view, to_view):
        if to_view.name == ViewState.Space:
            self._in_space_scene_loaded = True


def play_intro_sound():
    PlaySound('docking_overlay_start_play')


def play_loop_sound():
    PlaySound('docking_overlay_waiting_play')


def play_outro_sound():
    PlaySound('docking_overlay_waiting_stop')
    PlaySound('docking_overlay_end_play')
    PlaySound('docking_overlay_outro_play')


def create_animation(text, letter_space, loop_policy):

    def animation(parent, cancellation_token):
        container = GoldenPositionContainerAutoSize(parent=parent, alignMode=uiconst.CENTER)
        video = SegmentedVideoHeroNotification(video_intro_path='res:/UI/Texture/classes/Docking/intro.webm', video_loop_path='res:/UI/Texture/classes/Docking/loop.webm', video_outro_path='res:/UI/Texture/classes/Docking/outro.webm', video_width=860, video_height=220, loop_policy=loop_policy)
        video_tasklet = uthread2.start_tasklet(video.play, container, cancellation_token)
        video.on_intro_start.connect(play_intro_sound)
        video.on_loop_start.connect(play_loop_sound)
        video.on_outro_start.connect(play_outro_sound)

        def show_main_label():
            main_label = Label(parent=container, align=uiconst.CENTER, top=-4, left=letter_space / 2.0, fontsize=18, fontStyle=fontconst.STYLE_HEADER, uppercase=True, letterspace=letter_space, maxLines=1, shadowOffset=(0, 0), color=TextColor.HIGHLIGHT, opacity=0.0)
            video.wait_for_intro_start()
            garble_reveal_label(label=main_label, text=text, step_duration=datetime.timedelta(milliseconds=50), time_offset=datetime.timedelta(milliseconds=500), opacity=TextColor.HIGHLIGHT.opacity)
            video.wait_for_outro_start()
            animations.FadeOut(main_label, duration=0.5, timeOffset=0.5)

        main_label_tasklet = uthread2.start_tasklet(show_main_label)
        main_label_tasklet.get()
        video_tasklet.get()

    return animation
