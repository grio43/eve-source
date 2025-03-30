#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\videowindow.py
import logging
import math
import uthread2
from carbonui import const as uiconst
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import StreamingVideoSprite, Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveCaptionMedium
from carbonui.control.window import Window
from eve.client.script.ui.control.simpleTextTooltip import SimpleTextTooltip
from eve.client.script.ui.shared.subtitles import Subtitles
from eve.common.lib import appConst
from localization import GetByLabel
from localization.formatters import FormatTimeIntervalShort, TIME_CATEGORY_HOUR, TIME_CATEGORY_SECOND
SUBTITLE_BG_COLOR = (0.15,
 0.15,
 0.15,
 0.6)
NANOS_PER_SECOND = 1000000000
logger = logging.getLogger(__name__)

class VideoPlayerWindow(Window):
    default_caption = 'Video'
    default_minSize = (500, 400)
    default_windowID = 'VideoPlayerWnd'
    default_iconNum = 'res:/ui/texture/icons/bigplay_64.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.videoPlayer = VideoPlayer(parent=self.sr.main, padding=appConst.defaultPadding)

    def SetVideoPath(self, path, title = None, subtitles = None):
        self.SetCaption(title if title is not None else self.default_caption)
        self.videoPlayer.SetVideoPath(path, title, subtitles)

    def SetVideoFinishedCallback(self, callback):
        self.videoPlayer.SetVideoFinishedCallback(callback)


class VideoPlayer(Container):
    default_name = 'VideoPlayer'
    default_sendAnalytics = False
    play_texture_path = 'res:/UI/Texture/classes/agency/helpSection/play_Icon.png'
    pause_texture_path = 'res:/UI/Texture/classes/agency/helpSection/pause_Icon.png'
    replay_texture_path = 'res:/UI/Texture/classes/agency/helpSection/replay_Icon.png'
    volume_texture_path = 'res:/UI/Texture/classes/agency/helpSection/volumeIcon.png'
    volume_muted_texture_path = 'res:/UI/Texture/classes/agency/helpSection/muteIcon.png'
    next_texture_path = 'res:/UI/Texture/classes/agency/helpSection/next_Icon.png'

    def ApplyAttributes(self, attributes):
        super(VideoPlayer, self).ApplyAttributes(attributes)
        self._updatePosition = True
        self._onFinish = None
        self._subtitles = None
        self._finished = False
        self._isScrubbing = False
        self.showSubtitles = True
        self.updateThread = None
        self.videoSequence = []
        self.loops = 0
        self.sendAnalytics = attributes.get('sendAnalytics', False)
        self.volume = settings.user.ui.Get('videoPlayerVolume', 100)
        self.ConstructLayout()
        self.layoutAreaParent._OnSizeChange_NoBlock = self.RecalcLayout
        self.UpdateLayoutArea()

    def StartUpdateThread(self):
        self.updateThread = uthread2.StartTasklet(self._UpdatePosition)

    def ConstructLayout(self):
        self.layoutAreaParent = Container(name='layoutAreaParent', parent=self)
        self.layoutArea = Container(name='layoutArea', parent=self.layoutAreaParent, align=uiconst.CENTER, state=uiconst.UI_NORMAL, width=100, height=100)
        self.layoutArea.OnMouseEnter = self.RevealControls
        self.layoutArea.OnMouseExit = self.HideControls
        self.ConstructLargePlayButton()
        self.ConstructControls()
        self.ConstructPausedOverlay()
        self.ConstructSubtitleContainer()
        self.ConstructVideoSprite()

    def ConstructLargePlayButton(self):
        self.largePlayButton = ButtonIcon(name='PlayButtonOverlay', parent=self.layoutArea, align=uiconst.CENTER, iconSize=86, width=86, height=86, texturePath='res:/UI/Texture/classes/agency/helpSection/largePlay_Icon.png', func=self.PlayPauseToggle, state=uiconst.UI_HIDDEN)

    def ConstructPausedOverlay(self):
        self.pausedOverlay = Fill(name='pausedOverlay', parent=self.layoutArea, color=(0, 0, 0, 0.25), state=uiconst.UI_HIDDEN)

    def ConstructSubtitleContainer(self):
        subtitleCont = Container(parent=self.layoutArea, name='subtitleCont', align=uiconst.TOBOTTOM_NOPUSH, state=uiconst.UI_DISABLED, height=100)
        self.subtitleBackground = ContainerAutoSize(name='subtitleBackground', parent=subtitleCont, bgColor=SUBTITLE_BG_COLOR, align=uiconst.CENTER, padding=(-5, 0, -5, 0))
        self.subtitleLabel = EveCaptionMedium(parent=self.subtitleBackground, color=Color.WHITE, align=uiconst.CENTER, bold=False, state=uiconst.UI_DISABLED, maxLines=2)

    def RevealControls(self, *args):
        if self.controlsContainer.GetOpacity() == 1:
            return
        animations.FadeIn(self.controlsContainer, duration=0.225, callback=lambda : self.controlsContainer.SetState(uiconst.UI_NORMAL))

    def HideControls(self, *args):
        if self.video.isPaused:
            return
        animations.FadeOut(self.controlsContainer, duration=0.225, callback=lambda : self.controlsContainer.SetState(uiconst.UI_DISABLED))

    def ConstructVideoSprite(self):
        self.video = StreamingVideoSprite(parent=self.layoutArea, align=uiconst.TOALL, state=uiconst.UI_DISABLED, sendAnalytics=self.sendAnalytics)
        self.video.OnVideoSizeAvailable = self.RecalcLayout
        self.video.OnVideoFinished = self._OnVideoFinished
        self.video.OnVideoDurationAvailable = self.OnVideoDurationAvailable

    def ConstructControls(self):
        self.controlsContainer = ContainerAutoSize(name='controlsContainer', parent=self.layoutArea, align=uiconst.TOBOTTOM_NOPUSH, bgColor=(0.1, 0.1, 0.1, 0.45), opacity=0)
        self.ConstructButtonContainer()
        self.ConstructControlButtons()
        self.ConstructPositionContainer()
        self.ConstructTimeLabelContainer()

    def ConstructButtonContainer(self):
        self.buttonContainer = Container(name='buttonContainer', parent=self.controlsContainer, align=uiconst.TOBOTTOM, height=24)

    def ConstructControlButtons(self):
        if self.videoSequence:
            self.previousButton = ButtonIcon(name='previousVideoButton', parent=self.buttonContainer, func=self.PlayPreviousVideoInSequence, align=uiconst.TOLEFT, texturePath=self.next_texture_path, rotation=math.pi, hint=GetByLabel('UI/VideoPlayer/Previous'))
            self.ConstructPlayPauseButton()
            self.nextButton = ButtonIcon(name='nextVideoButton', parent=self.buttonContainer, func=self.PlayNextVideoInSequence, align=uiconst.TOLEFT, texturePath=self.next_texture_path, hint=GetByLabel('UI/VideoPlayer/Next'))
        else:
            self.ConstructPlayPauseButton()
        self.ConstructVolumeControl()
        self.subtitlesBtn = ButtonIcon(parent=self.buttonContainer, func=self.ToggleSubtitles, align=uiconst.TORIGHT, texturePath='res:/ui/texture/icons/73_16_10.png', hint=GetByLabel('UI/VideoPlayer/ToggleSubtitles'))

    def ConstructVolumeControl(self):
        volumeControlsContainer = ContainerAutoSize(name='volumeControlsContainer', parent=self.buttonContainer, align=uiconst.TOLEFT)
        volumeControlsContainer.OnMouseEnter = self.RevealVolumeSlider
        volumeControlsContainer.OnMouseExit = self.HideVolumeSlider
        self.muteBtn = ButtonIcon(mame='muteBtn', parent=volumeControlsContainer, func=self.Mute, align=uiconst.TOLEFT, texturePath=self.volume_texture_path, iconSize=24, hint=GetByLabel('UI/VideoPlayer/Mute'))
        self.volumeSlider = VideoPlayerVolumeSlider(parent=volumeControlsContainer, width=100, value=self.volume, minValue=0, maxValue=100, startValue=100, showLabel=False, on_dragging=self.SetVolume, align=uiconst.TOLEFT, opacity=0)

    def ConstructPlayPauseButton(self):
        self.playPauseBtn = ButtonIcon(name='PlayPauseButton', parent=self.buttonContainer, func=self.PlayPauseToggle, align=uiconst.TOLEFT, texturePath=self.pause_texture_path, iconSize=24, hint=GetByLabel('UI/VideoPlayer/Pause'))

    def ConstructPositionContainer(self):
        self.positionContainer = Container(name='positionCont', parent=self.controlsContainer, align=uiconst.TOBOTTOM, height=16, padLeft=9, padRight=9)
        self.positionCircle = Sprite(name='positionCircle', parent=self.positionContainer, align=uiconst.TOPLEFT_PROP, height=16, width=16, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/agency/helpSection/timeline_Icon.png')
        self.positionCircle.OnClick = self.ApplyVideoPosition
        self.positionCircle.OnMouseEnter = self.positionCircle.Show
        self.positionCircle.OnMouseDown = self.OnPosContMouseDown
        self.positionCircle.OnMouseUp = self.OnPosContMouseUp
        self.positionCircle.OnMouseMove = self.Scrub
        self.timelineContainer = Container(name='fillContainer', parent=self.positionContainer, height=4, top=4, state=uiconst.UI_NORMAL)
        self.timelineContainer.OnClick = self.ApplyVideoPosition
        self.timelineContainer.OnMouseMove = self.OnTimelineMouseMove
        self.timelineContainer.OnMouseDown = self.OnPosContMouseDown
        self.timelineContainer.OnMouseUp = self.OnPosContMouseUp
        self.timelineContainer.OnMouseEnter = self.OnPosContMouseEnter
        self.timelineContainer.OnMouseExit = self.OnPosContMouseExit
        self.timelineContainer.GetTooltipPosition = self.GetTooltipPosition
        self.timelineContainer.GetTooltipDelay = self.GetTooltipDelay
        self.positionFill = Fill(name='positionFill', parent=self.timelineContainer, align=uiconst.TOPLEFT_PROP, height=8, width=2, state=uiconst.UI_DISABLED, color=Color.WHITE)
        self.progressFill = Fill(parent=Container(parent=self.timelineContainer, state=uiconst.UI_DISABLED), name='progressFill', align=uiconst.TOLEFT_PROP, color=(0.1804, 0.5412, 0.6392, 1))
        self.downloadedFill = Fill(parent=Container(parent=self.timelineContainer, state=uiconst.UI_DISABLED), name='downloadFill', align=uiconst.TOLEFT_PROP, color=(0.4667, 0.7529, 0.8392, 0.45))
        Fill(parent=self.timelineContainer, align=uiconst.TOALL, color=(1.0, 1.0, 1.0, 0.3))

    def ConstructTimeLabelContainer(self):
        timeLabelContainer = Container(name='timeLabelContainer', parent=self.controlsContainer, align=uiconst.TOBOTTOM, height=20, padLeft=9, padRight=9)
        self.currentTimeLabel = EveLabelMedium(name='currentTimeLabel', parent=timeLabelContainer, align=uiconst.CENTERLEFT)
        self.totalDurationLabel = EveLabelMedium(name='totalDurationLabel', parent=timeLabelContainer, align=uiconst.CENTERRIGHT)

    def Reset(self):
        self.progressFill.width = 0
        self.downloadedFill.width = 0
        self.playPauseBtn.SetTexturePath(self.pause_texture_path)
        self.playPauseBtn.SetHint(GetByLabel('UI/VideoPlayer/Pause'))
        self.muteBtn.SetTexturePath(self.volume_texture_path)
        self.muteBtn.SetHint(GetByLabel('UI/VideoPlayer/Mute'))
        self.largePlayButton.SetState(uiconst.UI_HIDDEN)
        self.volumeSlider.SetValue(self.volume)

    def RevealVolumeSlider(self, *args):
        animations.FadeIn(self.volumeSlider, duration=0.225)

    def HideVolumeSlider(self, *args):
        animations.FadeOut(self.volumeSlider, duration=0.225)

    def OnPosContMouseUp(self, *args):
        self._isScrubbing = False

    def OnPosContMouseDown(self, *args):
        self._isScrubbing = True

    def GetTooltipPosition(self):
        x, y = self.timelineContainer.GetAbsolutePosition()
        return (int(uicore.uilib.x * uicore.desktop.dpiScaling),
         y,
         0,
         0)

    def OnPosContMouseEnter(self, *args):
        self.positionCircle.Show()
        self.timelineContainer.tooltipPanelClassInfo = SimpleTextTooltip(text=self.GetFormattedVideoTimeFromMousePosition(), margin=4)

    def OnTimelineMouseMove(self, *args):
        if self.timelineContainer.tooltipPanelClassInfo:
            self.UpdateVideoTimeTooltip()
        self.Scrub()

    def Scrub(self, *args):
        if self._isScrubbing:
            self.ApplyVideoPosition()

    def OnPosContMouseExit(self, *args):
        if self._isScrubbing:
            return
        self.positionCircle.Hide()

    def GetTooltipDelay(self):
        return 0

    def UpdateVideoTimeTooltip(self):
        self.UpdateVideoTimeTooltipPosition()
        self.UpdateVideoTimeTooltipText()

    def UpdateVideoTimeTooltipText(self):
        if not self.timelineContainer.tooltipPanelClassInfo.textLabel:
            return
        currentTime = self.GetFormattedVideoTimeFromMousePosition()
        self.timelineContainer.tooltipPanelClassInfo.textLabel.SetText(currentTime)

    def GetFormattedVideoTimeFromMousePosition(self):
        nanoseconds = self.GetVideoTimeFromMousePosition()
        seconds_in_video = int(nanoseconds / NANOS_PER_SECOND)
        currentTime = FormatTimeIntervalShort(seconds_in_video * appConst.SEC, showFrom=TIME_CATEGORY_HOUR, showTo=TIME_CATEGORY_SECOND)
        return currentTime

    def UpdateVideoTimeTooltipPosition(self):
        if not self.timelineContainer.tooltipPanelClassInfo.tooltipPanel:
            return
        l, t, w, h = self.GetTooltipPosition()
        t -= self.timelineContainer.tooltipPanelClassInfo.tooltipPanel.height + 9
        l -= self.timelineContainer.tooltipPanelClassInfo.tooltipPanel.width / 2
        self.timelineContainer.tooltipPanelClassInfo.tooltipPanel.SetPosition(l, t)

    def GetVideoTimeFromMousePosition(self):
        l, t, w, h = self.timelineContainer.GetAbsolute()
        try:
            x = (uicore.uilib.x - l) / float(w)
        except ZeroDivisionError:
            x = 0.0

        if x >= 1.0:
            return 1.0
        x = max(0.0, x)
        x = int(x * self.video.duration)
        return x

    def ApplyVideoPosition(self):
        nanoseconds = self.GetVideoTimeFromMousePosition()
        self.video.Seek(nanoseconds)

    def SetVideoFinishedCallback(self, callback):
        self._onFinish = callback

    def _OnVideoFinished(self):
        self._finished = True
        self.playPauseBtn.SetTexturePath(self.replay_texture_path)
        self.playPauseBtn.SetHint(GetByLabel('UI/VideoPlayer/Replay'))
        self._updatePosition = False
        if self._onFinish is not None:
            self._onFinish()
        self.updateThread.kill()

    def SetVideoSequence(self, videoPaths):
        if not videoPaths:
            return
        self.videoSequence = list(videoPaths)
        self.buttonContainer.Flush()
        self.ConstructControlButtons()
        self.UpdateNextPreviousButtons()
        self.subtitleLabel.text = ''

    def ClearVideoSequence(self):
        self.videoSequence = []
        self.buttonContainer.Flush()
        self.ConstructControlButtons()
        self.UpdateNextPreviousButtons()
        self.subtitleLabel.text = ''

    def UpdateNextPreviousButtons(self, videoIndexInSequence = None):
        if not self.video.path:
            return
        if not videoIndexInSequence:
            videoIndexInSequence = self.videoSequence.index(self.video.path)
        if videoIndexInSequence == len(self.videoSequence) - 1:
            self.nextButton.Disable()
        elif videoIndexInSequence == 0:
            self.previousButton.Disable()

    def PlayNextVideoInSequence(self):
        try:
            nextIndex = self.videoSequence.index(self.video.path) + 1
        except ValueError:
            logger.warn('Video Player: Unable to play next video in sequence', exc_info=True)
            return

        if nextIndex > len(self.videoSequence) - 1:
            return
        self.SetVideoPath(self.videoSequence[nextIndex], *self._replayArgs[1:])
        self.OnNextButtonClicked()
        if not self.previousButton.enabled:
            self.previousButton.Enable()
        self.UpdateNextPreviousButtons(nextIndex)

    def OnNextButtonClicked(self):
        pass

    def PlayPreviousVideoInSequence(self):
        try:
            prevIndex = self.videoSequence.index(self.video.path) - 1
        except ValueError:
            logger.warn('Video Player: Unable to play previous video in sequence', exc_info=True)
            return

        if prevIndex < 0:
            return
        self.SetVideoPath(self.videoSequence[prevIndex], *self._replayArgs[1:])
        self.OnPreviousButtonClicked()
        if not self.nextButton.enabled:
            self.nextButton.Enable()
        self.UpdateNextPreviousButtons(prevIndex)

    def OnPreviousButtonClicked(self):
        pass

    def SetVideoPath(self, path, title = None, subtitles = None, videoLoop = False):
        if self.video and path == self.video.path:
            return
        self.Reset()
        self.video.SetVideoPath(path, videoLoop=videoLoop)
        self.video.SetVolume(float(self.volume) / 100.0)
        self._finished = False
        self._replayArgs = (path,
         title,
         subtitles,
         videoLoop)
        subtitleText = None
        if subtitles is None:
            self._subtitles = None
        else:
            self._subtitles = Subtitles()
            subtitleText = self._subtitles.LoadSubtitleFile(subtitles)
        if not subtitleText:
            self.subtitleBackground.Hide()
            self._subtitles = None
        else:
            self._subtitles.PrepareSubtitles(subtitleText)
            self.subtitleBackground.Show()
        self.StartUpdateThread()

    def OnVideoDurationAvailable(self):
        self.UpdateDurationLabel()

    def UpdateDurationLabel(self):
        if not self.video or not self.video.duration:
            return
        seconds_in_video = self.video.duration / NANOS_PER_SECOND
        totalDuration = FormatTimeIntervalShort(seconds_in_video * appConst.SEC, showFrom=TIME_CATEGORY_HOUR, showTo=TIME_CATEGORY_SECOND)
        self.totalDurationLabel.SetText(totalDuration)

    def UpdateCurrentTimeLabel(self):
        if not self.video or not self.video.mediaTime:
            return
        currentTime = self.GetVideoCurrentTime()
        self.currentTimeLabel.SetText(currentTime)

    def GetVideoCurrentTime(self):
        seconds_in_video = self.video.mediaTime % self.video.duration / NANOS_PER_SECOND
        currentTime = FormatTimeIntervalShort(seconds_in_video * appConst.SEC, showFrom=TIME_CATEGORY_HOUR, showTo=TIME_CATEGORY_SECOND)
        return currentTime

    def Close(self, *args, **kwds):
        self._updatePosition = False
        self.video = None
        if self.updateThread:
            self.updateThread.kill()
        super(VideoPlayer, self).Close()

    def _UpdatePosition(self):
        while self._updatePosition:
            if self.video:
                mediaTime = self.video.GetPositionRatioInVideo()
                self.UpdateCurrentTimeLabel()
                if mediaTime == 0:
                    self.progressFill.Hide()
                else:
                    self.progressFill.Show()
                    self.progressFill.width = mediaTime
                    self.positionCircle.left = mediaTime
                    self.positionFill.left = mediaTime
                duration = float((self.video.duration or 1) / 1000000)
                if duration == 0:
                    duration = 1
                downloadedTime = min(float((self.video.downloadedTime or 0) / 1000000) / duration, 1)
                if downloadedTime == 0:
                    self.downloadedFill.Hide()
                else:
                    self.downloadedFill.Show()
                    self.downloadedFill.width = downloadedTime
                self._UpdateSubtitles()
            uthread2.Sleep(0.1)

    def _UpdateSubtitles(self):
        if self._subtitles is None or not self.showSubtitles:
            return
        currentTime = self.video.mediaTime or 0
        currentTime /= 1000000
        text = self._subtitles.GetSubtitle(currentTime)
        self.subtitleLabel.maxWidth = self.displayWidth - 50
        if text:
            self.subtitleLabel.SetText(text)

    def UpdateLayoutArea(self):
        size = self.video.GetVideoSize()
        if not size:
            return
        areaWidth, areaHeight = self.layoutAreaParent.GetAbsoluteSize()
        xFitScale = areaWidth / float(size[0])
        yFitScale = areaHeight / float(size[1])
        scaling = min(xFitScale, yFitScale)
        self.layoutArea.width = int(size[0] * scaling)
        self.layoutArea.height = int(size[1] * scaling)

    def RecalcLayout(self, *args):
        self.UpdateLayoutArea()

    def PlayPauseToggle(self, *args):
        if self._finished:
            self.Replay()
        elif self.video.isPaused:
            self.Play()
        else:
            self.Pause()

    def Play(self):
        self.video.Play()
        self.controlsContainer.SetOpacity(1.0)
        self.largePlayButton.SetState(uiconst.UI_HIDDEN)
        self.playPauseBtn.SetTexturePath(self.pause_texture_path)
        self.playPauseBtn.SetHint(GetByLabel('UI/VideoPlayer/Pause'))
        self.pausedOverlay.SetState(uiconst.UI_HIDDEN)

    def Pause(self):
        self.video.Pause()
        self.largePlayButton.SetState(uiconst.UI_NORMAL)
        self.playPauseBtn.SetTexturePath(self.play_texture_path)
        self.playPauseBtn.SetHint(GetByLabel('UI/VideoPlayer/Play'))
        self.pausedOverlay.SetState(uiconst.UI_NORMAL)

    def Replay(self):
        self._finished = False
        self.SetVideoPath(*self._replayArgs)
        self.Play()

    def Mute(self, *args):
        if self.video.isMuted:
            self.video.UnmuteAudio()
            self.volumeSlider.SetValue(self.volume)
            self.muteBtn.SetTexturePath(self.volume_texture_path)
            self.muteBtn.SetHint(GetByLabel('UI/VideoPlayer/Mute'))
        else:
            self.video.MuteAudio()
            self.volumeSlider.SetValue(0)
            self.muteBtn.SetTexturePath(self.volume_muted_texture_path)
            self.muteBtn.SetHint(GetByLabel('UI/VideoPlayer/Unmute'))

    def SetVolume(self, slider):
        self.video.SetVolume(float(slider.value) / 100.0)
        self.volume = slider.value
        settings.user.ui.Set('videoPlayerVolume', self.volume)
        if self.volume:
            self.muteBtn.SetTexturePath(self.volume_texture_path)
            self.muteBtn.SetHint(GetByLabel('UI/VideoPlayer/Mute'))

    def ToggleSubtitles(self):
        self.showSubtitles = not self.showSubtitles
        if self.showSubtitles:
            self.subtitlesBtn.opacity = 1.0
            self.subtitleLabel.Show()
            self.subtitleBackground.Show()
        else:
            self.subtitlesBtn.opacity = 0.2
            self.subtitleLabel.Hide()
            self.subtitleBackground.Hide()


class VideoPlayerVolumeSlider(Slider):
    default_name = 'VideoPlayerVolumeSlider'

    def ApplyAttributes(self, attributes):
        super(VideoPlayerVolumeSlider, self).ApplyAttributes(attributes)
        self.callback.connect(self.UpdateFillWidth)
        self.on_dragging.connect(self.UpdateFillWidth)
        self.UpdateFillWidth()

    def _ConstructHandle(self):
        super(VideoPlayerVolumeSlider, self)._ConstructHandle()

    def _ConstructBackground(self):
        volumeFillContainer = Container(parent=self, align=uiconst.CENTER, height=self.barHeight / 2, width=self.width)
        Fill(name='backgroundFill', bgParent=volumeFillContainer, color=Color.GRAY5, opacity=0.25)
        self.volumeFill = Fill(parent=volumeFillContainer, align=uiconst.TOLEFT_PROP, width=0.0, color=Color.WHITE)

    def _ConstructBarCont(self):
        self.barCont = Container(parent=self, name='barCont', align=uiconst.CENTER, state=uiconst.UI_NORMAL, height=self.barHeight + 10, width=self.width)
        self.barCont.OnClick = self.OnSliderClicked
        self.barCont.OnMouseMove = self.OnSliderMouseMove
        self.barCont.OnMouseExit = self.OnMouseBarExit
        self.barCont.OnMouseWheel = self.OnMouseWheel
        self.barCont.GetHint = self.GetHint

    def UpdateFillWidth(self, *args):
        self.volumeFill.width = self.value / 100

    def OnHandleMouseEnter(self, *args):
        pass

    def OnHandleMouseExit(self, *args):
        pass
