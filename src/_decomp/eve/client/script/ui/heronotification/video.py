#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\heronotification\video.py
import abc
import math
import eveui
import gametime
import signals
import trinity
import uthread2
from carbonui import uiconst
from carbonui.primitives.sprite import StreamingVideoSprite
from carbonui.uianimations import animations
from eve.client.script.ui.heronotification.cancel import Cancelled
from stacklesslib.locks import NLCondition

class LoopPolicy(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def should_stop(self):
        pass

    def on_start_looping(self):
        pass

    def on_loop_finished(self):
        pass

    def dispose(self):
        pass


class LoopCountPolicy(LoopPolicy):

    def __init__(self, loop_count):
        self._loop_count = loop_count
        self._finished_loops = 0

    def should_stop(self):
        return self._finished_loops >= self._loop_count

    def on_loop_finished(self):
        self._finished_loops += 1


class LoopTimerPolicy(LoopPolicy):

    def __init__(self, duration):
        self._duration = duration
        self._loop_start = None

    def should_stop(self):
        return self._loop_start is not None and gametime.now() - self._loop_start >= self._duration

    def on_start_looping(self):
        self._loop_start = gametime.now()


class SegmentedVideoHeroNotification(object):

    def __init__(self, video_width, video_height, video_intro_path, video_loop_path, video_outro_path, loop_policy, allow_cancel_intro = False, allow_cancel_loop = False):
        self._allow_cancel_intro = allow_cancel_intro
        self._allow_cancel_loop = allow_cancel_loop
        self._cancellation_token = None
        self._loop_policy = loop_policy
        self._state = State.INIT
        self._video_height = video_height
        self._video_intro_path = video_intro_path
        self._video_loop_path = video_loop_path
        self._video_outro_path = video_outro_path
        self._video_sprite_intro = None
        self._video_sprite_loop = None
        self._video_sprite_outro = None
        self._video_width = video_width
        self.on_intro_start = signals.Signal()
        self.on_loop_start = signals.Signal()
        self.on_outro_start = signals.Signal()
        self._on_intro_start_condition = NLCondition()
        self._on_loop_start_condition = NLCondition()
        self._on_outro_start_condition = NLCondition()

    def play(self, parent, cancellation_token):
        if self._state != State.INIT:
            raise RuntimeError('The video is already playing')
        self._cancellation_token = cancellation_token
        try:
            self._setup(parent)
            self._wait_for_intro()
        except Cancelled:
            self._hard_outro()
        else:
            self._wait_for_loops()
            self._play_outro()
            self._wait_for_outro()
        finally:
            self._cleanup()

    def wait_for_intro_start(self):
        if self._state < State.INTRO:
            self._on_intro_start_condition.wait()

    def wait_for_loop_start(self):
        if self._state < State.LOOP:
            self._on_loop_start_condition.wait()

    def wait_for_outro_start(self):
        if self._state < State.OUTRO:
            self._on_outro_start_condition.wait()

    def _setup(self, parent):
        self._state = State.SETUP
        self._video_sprite_intro = self._create_video_sprite(parent=parent, video_path=self._video_intro_path, auto_play=True, on_finished=self._on_intro_finished)
        self._video_sprite_loop = self._create_video_sprite(parent=parent, video_path=self._video_loop_path, loop=True, display=False)
        self._video_sprite_outro = self._create_video_sprite(parent=parent, video_path=self._video_outro_path, display=False)
        self._state = State.INTRO
        self.on_intro_start()
        self._on_intro_start_condition.notify_all()

    def _create_video_sprite(self, parent, video_path, loop = False, auto_play = False, on_finished = None, display = True):
        sprite = StreamingVideoSprite(parent=parent, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=self._video_width, height=self._video_height, videoPath=video_path, disableAudio=True, videoLoop=loop, videoAutoPlay=auto_play, blendMode=trinity.TR2_SBM_ADD, spriteEffect=trinity.TR2_SFX_COPY)
        sprite.display = display
        if on_finished is not None:
            sprite.OnVideoFinished = on_finished
        return sprite

    def _on_intro_finished(self):
        if self._state == State.INTRO:
            self._play_loop()

    def _wait_for_intro(self):
        while self._state == State.INTRO:
            self._wait_for_next_frame()
            if self._allow_cancel_intro:
                self._cancellation_token.check_cancelled()

    def _play_loop(self):
        self._state = State.LOOP
        self._video_sprite_loop.display = True
        self._video_sprite_intro.display = False
        self._video_sprite_loop.Play()
        self._loop_policy.on_start_looping()
        self.on_loop_start()
        self._on_loop_start_condition.notify_all()

    def _wait_for_loops(self):
        last_loop = self._get_video_loops()
        while not self._loop_policy.should_stop():
            if self._allow_cancel_loop and self._cancellation_token.cancelled:
                while self._get_video_loops() == last_loop:
                    self._wait_for_next_frame()
                    return

            self._wait_for_next_frame()
            loop = self._get_video_loops()
            while last_loop < loop:
                last_loop += 1
                self._loop_policy.on_loop_finished()

    def _get_video_loops(self):
        if not self._video_sprite_loop.duration:
            return 0
        return int(math.floor(self._video_sprite_loop.mediaTime / float(self._video_sprite_loop.duration)))

    def _play_outro(self):
        self._state = State.OUTRO
        self._video_sprite_outro.display = True
        self._video_sprite_loop.display = False
        self._video_sprite_loop.Pause()
        self._video_sprite_outro.Play()
        self.on_outro_start()
        self._on_outro_start_condition.notify_all()

    def _wait_for_outro(self):
        while self._state == State.OUTRO:
            if self._video_sprite_outro.isFinished:
                break
            self._wait_for_next_frame()

    def _hard_outro(self):
        for sprite in (self._video_sprite_intro, self._video_sprite_loop, self._video_sprite_outro):
            if sprite is not None and not sprite.destroyed:
                animations.FadeOut(sprite, duration=0.5)

        uthread2.sleep(0.5)
        self._state = State.FINISHED

    def _wait_for_next_frame(self):
        eveui.wait_for_next_frame()
        self._check_destroyed()

    def _check_destroyed(self):
        for element in (self._video_sprite_intro, self._video_sprite_loop, self._video_sprite_outro):
            if element is None or element.destroyed:
                raise HeroNotificationDestroyed()

    def _cleanup(self):
        self._loop_policy.dispose()
        for element in (self._video_sprite_intro, self._video_sprite_loop, self._video_sprite_outro):
            if element is not None:
                element.Close()

        self._video_sprite_intro = None
        self._video_sprite_loop = None
        self._video_sprite_outro = None
        self._cancellation_token = None
        self._state = State.FINISHED
        self._on_intro_start_condition.notify_all()
        self._on_loop_start_condition.notify_all()
        self._on_outro_start_condition.notify_all()

    def __call__(self, parent, cancellation_token):
        self.play(parent, cancellation_token)


class State(object):
    INIT = 1
    SETUP = 2
    INTRO = 3
    LOOP = 4
    OUTRO = 5
    FINISHED = 6


class HeroNotificationDestroyed(Exception):
    pass
