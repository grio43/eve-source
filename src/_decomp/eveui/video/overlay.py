#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\video\overlay.py
from carbon.common.script.util.mathCommon import FloatCloseEnough
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import StreamingVideoSprite
from carbonui.uianimations import animations
import carbonui.uiconst as uiconst
from carbonui.uicore import uicore
import trinity
from uthread2 import call_after_wallclocktime_delay
import uthread
from eveui.layout.aspect_ratio import AspectRatioContainer

class VideoOverlay(object):
    BLACK_BACKGROUND_OPACITY_START = 0.1
    BLACK_BACKGROUND_OPACITY_MAX = 1.0
    BLACK_BACKGROUND_OPACITY_END = 0.1
    ANIMATION_DURATION_SECONDS_DEFAULT = 8.0
    ANIMATION_DELAY_SECONDS = 0.1

    def __init__(self, resource_file_path, show_background, audio_ui_event):
        self.resource_file_path = resource_file_path
        self.show_background = show_background
        self.audio_ui_event = audio_ui_event
        self.main_container = None
        self.black_background = None
        self.video = None

    def _load(self):
        self._construct_container()
        self._construct_black_background()
        self._construct_video()

    def _is_ui_element_available(self, ui_element):
        return ui_element and not ui_element.destroyed

    def _clear_ui_element(self, ui_element):
        if self._is_ui_element_available(ui_element):
            ui_element.Close()

    def _construct_container(self):
        self._clear_ui_element(self.main_container)
        self.main_container = Container(name='video_animation_{resource_file_path}'.format(resource_file_path=self.resource_file_path), parent=uicore.layer.videoOverlay, align=uiconst.TOALL, state=uiconst.UI_DISABLED)

    def _construct_black_background(self):
        self._clear_ui_element(self.black_background)
        if self.show_background:
            self.black_background = Fill(name='black_background', parent=self.main_container, align=uiconst.TOALL, idx=1, state=uiconst.UI_DISABLED, color=(0.0,
             0.0,
             0.0,
             self.BLACK_BACKGROUND_OPACITY_START))

    def _construct_video(self):
        self._clear_ui_element(self.video)
        video_parent = AspectRatioContainer(parent=self.main_container, contain=False)
        self.video = StreamingVideoSprite(name='video_{resource_file_path}'.format(resource_file_path=self.resource_file_path), parent=video_parent, videoPath=self.resource_file_path, videoLoop=False, align=uiconst.TOALL, idx=0, state=uiconst.UI_DISABLED, spriteEffect=trinity.TR2_SFX_COPY, disableAudio=True)
        self.video.OnVideoFinished = self.stop

    def start(self):
        if not self._is_ui_element_available(self.video):
            self._load()
        self.video.Play()
        self._play_audio()
        self._animate_black_background()

    def _play_audio(self):
        if self.audio_ui_event:
            sm.GetService('audio').SendUIEvent(self.audio_ui_event)

    def stop(self):
        uthread.new(self._stop)

    def _stop(self):
        if self._is_ui_element_available(self.video):
            self.video.Pause()
        self._clear_ui_element(self.main_container)
        sm.GetService('sceneManager').Saturate(duration=0.1, saturateLevel=1.0)

    def _get_duration_in_seconds(self):
        try:
            if not FloatCloseEnough(self.video.duration, 0.0):
                return self.video.duration / 1000000000.0 - self.ANIMATION_DELAY_SECONDS
        except AttributeError:
            return self.ANIMATION_DURATION_SECONDS_DEFAULT

        return self.ANIMATION_DURATION_SECONDS_DEFAULT

    def _animate_black_background(self):
        if self.black_background:
            call_after_wallclocktime_delay(self._fade_in_black_background, delay=self.ANIMATION_DELAY_SECONDS)

    def _fade_in_black_background(self):
        duration = self._get_duration_in_seconds() / 2.0
        sm.GetService('sceneManager').Saturate(duration, saturateLevel=0.0)
        animations.FadeTo(obj=self.black_background, startVal=self.black_background.opacity, endVal=self.BLACK_BACKGROUND_OPACITY_MAX, duration=duration, callback=self._fade_out_black_background)

    def _fade_out_black_background(self):
        duration = self._get_duration_in_seconds() / 2.0
        sm.GetService('sceneManager').Saturate(duration, saturateLevel=1.0)
        animations.FadeTo(obj=self.black_background, startVal=self.black_background.opacity, endVal=self.BLACK_BACKGROUND_OPACITY_END, duration=duration)
