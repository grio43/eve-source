#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\intromovie\ui\introvideo.py
import blue
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import StreamingVideoSprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, Label
from eve.client.script.ui.shared.subtitles import Subtitles, GetSubtitlePathForVideo
import langutils
from localization import GetByLabel
import logging
from math import pi
from uthread2 import call_after_wallclocktime_delay, start_tasklet
logger = logging.getLogger(__name__)
SUBTITLES_HEIGHT_RATIO = 0.1
SKIP_SUGGESTION_HEIGHT_RATIO = 0.07
SUBTITLES_TEXT_COLOR = (0.75, 0.75, 0.75, 1.0)
SKIP_SUGGESTION_OPACITY = 1.0
SKIP_SUGGESTION_COLOR_0 = (0.0, 0.15, 0.16)
SKIP_SUGGESTION_COLOR_1 = (0.0, 0.11, 0.13)
SKIP_SUGGESTION_COLOR_2 = (0.04, 0.08, 0.1)
SKIP_SUGGESTION_TEXT_COLOR = (0.75, 0.75, 0.75, 1.0)
SKIP_SUGGESTION_DURATION_SECONDS = 7.0
SKIP_SUGGESTION_FADE_OUT_SECONDS = 1.0
SKIP_SUGGESTION_TEXT_PATH = 'UI/Intro/SkipSuggestion'
KEYS_THAT_TRIGGER_SKIPPING = [uiconst.VK_SPACE]

class IntroVideo(Container):
    __notifyevents__ = ['OnSetDevice']
    default_align = uiconst.TOALL
    default_idx = 0
    default_name = 'introVideo'
    default_parent = uicore.layer.videoOverlay
    default_state = uiconst.UI_NORMAL
    default_bgColor = Color.BLACK

    def ApplyAttributes(self, attributes):
        self.onStop = attributes.onStopCallback
        self.movie = None
        self.moviePath = None
        self.subtitles = Subtitles()
        self.skipSuggestionContainer = None
        self.skipSuggestionFadeOut = None
        self._isStopping = False
        self.keyUpCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.OnGeneralKeyUp)
        super(IntroVideo, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        start_tasklet(self._LoadContent)

    def Close(self):
        uicore.event.UnregisterForTriuiEvents(self.keyUpCookie)
        super(IntroVideo, self).Close()

    def _IsMovieAvailable(self):
        return blue.paths.FileExistsLocally(self.moviePath)

    def _LoadContent(self, **kwargs):
        self.language = langutils.get_client_language()
        self.moviePath = langutils.get_intro_movie_file(self.language)
        self.useSubtitles = langutils.get_use_intro_subtitles(self.language)
        if not self._IsMovieAvailable():
            self.moviePath = langutils.langconst.INTRO_MOVIE_FILE_DEFAULT
            self.useSubtitles = langutils.langconst.USE_INTRO_SUBTITLE_DEFAULT
        if self._IsMovieAvailable():
            self._LoadMovie()
            self._LoadSubtitles()
            self._LoadSkipSuggestion()
            start_tasklet(self._PlayMovie)
        else:
            self.StopIntro()
        self._isStopping = False

    def _LoadMovie(self):
        self.sr.movieCont = Container(parent=self, name='movieCont', idx=1, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        x, y, contWidth, contHeight = self.sr.movieCont.GetAbsolute()
        dimWidth, dimHeight = self._GetVideoDimensions(contWidth, contHeight, 1280, 720)
        self.movie = StreamingVideoSprite(parent=self.sr.movieCont, width=dimWidth, height=dimHeight, align=uiconst.CENTER, videoPath=self.moviePath, state=uiconst.UI_DISABLED, sendAnalytics=True)

    def _GetSubtitlesHeight(self):
        x, y, contWidth, contHeight = self.sr.movieCont.GetAbsolute()
        return int(float(contHeight) * SUBTITLES_HEIGHT_RATIO)

    def _LoadSubtitles(self):
        if not self.useSubtitles:
            return
        try:
            subtitlePath = GetSubtitlePathForVideo(self.moviePath, self.language)
            subtitleText = ''
            if not subtitlePath:
                defaultLanguage = langutils.langconst.DEFAULT_CLIENT_LANGUAGE
                subtitlePath = GetSubtitlePathForVideo(self.moviePath, defaultLanguage)
            if subtitlePath:
                subtitleText = self.subtitles.LoadSubtitleFile(subtitlePath)
            if not subtitleText:
                self.useSubtitles = False
                return
        except Exception as exc:
            logger.exception('Failed to load subtitles for intro video (language: %s): %s', self.language, exc)
            self.useSubtitles = False
            return

        self.subtitles.PrepareSubtitles(subtitleText)
        self.sr.subtitleCont = Container(parent=self.sr.movieCont, name='subtitleCont', idx=0, align=uiconst.TOBOTTOM, state=uiconst.UI_DISABLED, height=self._GetSubtitlesHeight())
        self._FlushSubtitles()

    def _UpdateSubtitles(self):
        if self.useSubtitles:
            currentTime = self._GetCurrentMovieTime()
            text = self.subtitles.GetSubtitle(currentTime)
            self._FlushSubtitles()
            if text:
                EveCaptionLarge(text='<center>%s' % text, parent=self.sr.subtitleCont, color=SUBTITLES_TEXT_COLOR, align=uiconst.TOALL, bold=False, state=uiconst.UI_DISABLED)

    def _FlushSubtitles(self):
        if self.sr.subtitleCont and not self.sr.subtitleCont.destroyed:
            self.sr.subtitleCont.Flush()

    def _GetSkipSuggestionHeight(self):
        x, y, contWidth, contHeight = self.sr.movieCont.GetAbsolute()
        return int(float(contHeight) * SKIP_SUGGESTION_HEIGHT_RATIO)

    def _LoadSkipSuggestion(self):
        height = self._GetSkipSuggestionHeight()
        self.skipSuggestionContainer = Container(parent=self, name='skipSuggestionContainer', idx=0, height=height, align=uiconst.TOTOP_NOPUSH, state=uiconst.UI_DISABLED, opacity=SKIP_SUGGESTION_OPACITY)
        Label(name='skipSuggestionText', text=GetByLabel(SKIP_SUGGESTION_TEXT_PATH), parent=self.skipSuggestionContainer, idx=0, color=SKIP_SUGGESTION_TEXT_COLOR, align=uiconst.CENTERLEFT, padLeft=50, state=uiconst.UI_DISABLED, fontsize=20)
        GradientSprite(parent=self.skipSuggestionContainer, name='skipSuggestionBackground', idx=1, align=uiconst.TOALL, rgbData=[(0, SKIP_SUGGESTION_COLOR_0), (0.5, SKIP_SUGGESTION_COLOR_1), (1.0, SKIP_SUGGESTION_COLOR_2)], alphaData=[(0.0, 1.0), (1.0, 1.0)], rotation=-pi / 2)
        self.skipSuggestionFadeOut = call_after_wallclocktime_delay(tasklet_func=self._FadeOutSkipSuggestion, delay=SKIP_SUGGESTION_DURATION_SECONDS)

    def _FadeOutSkipSuggestion(self):
        if self.skipSuggestionContainer:
            animations.FadeOut(obj=self.skipSuggestionContainer, duration=SKIP_SUGGESTION_FADE_OUT_SECONDS)

    def _CloseSkipSuggestion(self):
        if self.skipSuggestionFadeOut:
            self.skipSuggestionFadeOut.kill()
            self.skipSuggestionFadeOut = None
        if self.skipSuggestionContainer and not self.skipSuggestionContainer.destroyed:
            uicore.animations.StopAllAnimations(self.skipSuggestionContainer)
            self.skipSuggestionContainer.Close()

    def _PlayMovie(self):
        self.movie.Play()
        self._KeepWatchingMovie()

    def _GetCurrentMovieTime(self):
        return (self.movie.mediaTime or 0) / 1000000

    def _KeepWatchingMovie(self):
        while not self.destroyed:
            if getattr(self, 'movie', None):
                if self.movie.isFinished:
                    self.StopIntro()
                    return
                self._UpdateSubtitles()
            else:
                return
            blue.pyos.synchro.SleepWallclock(20)

    def _GetVideoDimensions(self, contWidth, contHeight, vidResWidth, vidResHeight):
        dimWidth = vidResWidth
        dimHeight = vidResHeight
        contFactor = float(contWidth) / float(contHeight)
        vidResFactor = float(vidResWidth) / float(vidResHeight)
        if vidResFactor > contFactor:
            widthFactor = float(contWidth) / float(vidResWidth)
            dimWidth *= widthFactor
            dimHeight *= widthFactor
        elif vidResFactor < contFactor:
            heightFactor = float(contHeight) / float(vidResHeight)
            dimWidth *= heightFactor
            dimHeight *= heightFactor
        else:
            dimWidth = contWidth
            dimHeight = contHeight
        return (int(dimWidth), int(dimHeight))

    def _ResizeVideo(self):
        dimWidth, dimHeight = self._GetVideoDimensions(uicore.desktop.width, uicore.desktop.height, 1280, 720)
        self.movie.width = dimWidth
        self.movie.height = dimHeight

    def OnSetDevice(self):
        self._ResizeVideo()

    def OnGeneralKeyUp(self, _window, _event_id, key_data, *args):
        key, _ = key_data
        if key in KEYS_THAT_TRIGGER_SKIPPING and not self._isStopping:
            self._isStopping = True
            self.StopIntro()
        return True

    def StopIntro(self):
        self._CloseSkipSuggestion()
        self._FlushSubtitles()
        if callable(self.onStop):
            self.onStop()

    def StopMovie(self):
        if self.movie:
            self.movie.Pause()
        self.movie = None
