#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\intro\flowcytometer.py
import carbonui.const as uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import Label
from localization import GetByLabel
from math import pi
from projectdiscovery.client.projects.covid.sounds import Sounds
import trinity
from uthread2 import call_after_wallclocktime_delay

class FlowStep(object):
    FLUIDICS = 0
    LASER = 1
    OPTICS_1 = 2
    OPTICS_2 = 3


DECORATION_TEXTURE_PATH = 'res:/UI/Texture/classes/ProjectDiscovery/footerBG.png'
CORNER_TEXTURE_PATH = 'res:/UI/Texture/classes/ProjectDiscovery/covid/corner_decoration.png'
VIDEOS_FOLDER = 'res:/video/projectdiscovery/'
VIDEO_BY_STEP = {FlowStep.FLUIDICS: VIDEOS_FOLDER + 'fluidics.webm',
 FlowStep.LASER: VIDEOS_FOLDER + 'laser.webm',
 FlowStep.OPTICS_1: VIDEOS_FOLDER + 'optics1.webm',
 FlowStep.OPTICS_2: VIDEOS_FOLDER + 'optics2.webm'}
LOOP_VIDEO_BY_STEP = {FlowStep.FLUIDICS: VIDEOS_FOLDER + 'fluidics_loop.webm',
 FlowStep.LASER: VIDEOS_FOLDER + 'laser_loop.webm',
 FlowStep.OPTICS_1: VIDEOS_FOLDER + 'optics1_loop.webm',
 FlowStep.OPTICS_2: VIDEOS_FOLDER + 'optics2_loop.webm'}
LABELS_FOLDER = 'UI/ProjectDiscovery/Covid/Intro/'
TEXT_BY_STEP = {FlowStep.FLUIDICS: LABELS_FOLDER + 'FluidicsText',
 FlowStep.LASER: LABELS_FOLDER + 'LaserText',
 FlowStep.OPTICS_1: LABELS_FOLDER + 'Optics1Text',
 FlowStep.OPTICS_2: LABELS_FOLDER + 'Optics2Text'}
BUTTON_TEXT_BY_STEP = {FlowStep.FLUIDICS: LABELS_FOLDER + 'FluidicsButton',
 FlowStep.LASER: LABELS_FOLDER + 'LaserButton',
 FlowStep.OPTICS_1: LABELS_FOLDER + 'Optics1Button',
 FlowStep.OPTICS_2: LABELS_FOLDER + 'Optics2Button'}
TEXT_DELAY_BY_STEP = {FlowStep.FLUIDICS: 0.1,
 FlowStep.LASER: 0.1,
 FlowStep.OPTICS_1: 0.1,
 FlowStep.OPTICS_2: 3.0}
INTRO_AUDIO_BY_STEP = {FlowStep.FLUIDICS: Sounds.FLOW_CYTOMETER_1_INTRO,
 FlowStep.LASER: Sounds.FLOW_CYTOMETER_2_INTRO,
 FlowStep.OPTICS_1: Sounds.FLOW_CYTOMETER_3_INTRO,
 FlowStep.OPTICS_2: Sounds.FLOW_CYTOMETER_4_INTRO}
INTRO_STOP_AUDIO_BY_STEP = {FlowStep.FLUIDICS: Sounds.FLOW_CYTOMETER_1_INTRO_STOP,
 FlowStep.LASER: Sounds.FLOW_CYTOMETER_2_INTRO_STOP,
 FlowStep.OPTICS_1: Sounds.FLOW_CYTOMETER_3_INTRO_STOP,
 FlowStep.OPTICS_2: Sounds.FLOW_CYTOMETER_4_INTRO_STOP}
TEXT_WIDTH = 296
TEXT_TOP = 80
TEXT_LEFT = 48
TEXT_FONTSIZE = 14
CONTINUE_BUTTON_WIDTH = 242
CONTINUE_BUTTON_HEIGHT = 64
CONTINUE_BUTTON_TOP = 66
CONTINUE_BUTTON_LEFT = 48
DECORATION_WIDTH = 355
DECORATION_HEIGHT = 53
CORNER_SIZE = 6
CORNER_PADDING = 20
VIDEO_ASPECT_RATIO = 0.77

class FlowCytometer(Container):

    def ApplyAttributes(self, attributes):
        self.is_in_intro_video = None
        self.audio = sm.GetService('audio')
        self.step = attributes.get('step')
        self.go_to_next = attributes.get('go_to_next')
        super(FlowCytometer, self).ApplyAttributes(attributes)
        self.opacity = 0.0
        self._add_text()
        self._add_corners()
        self._add_continue_button()
        self._add_bottom_decoration()
        self._add_video()

    def _add_text(self):
        self.text = Label(name='text_flow_cytometer_%s' % self.step, parent=self, align=uiconst.TOPRIGHT, top=TEXT_TOP, left=TEXT_LEFT, fontsize=TEXT_FONTSIZE, maxWidth=TEXT_WIDTH, text=GetByLabel(TEXT_BY_STEP[self.step]), opacity=0.0)

    def _add_corners(self):
        Sprite(parent=self, name='corner_top_flow_cytometer_%s' % self.step, texturePath=CORNER_TEXTURE_PATH, align=uiconst.TOPRIGHT, width=CORNER_SIZE, height=CORNER_SIZE, top=TEXT_TOP - CORNER_PADDING, left=TEXT_LEFT, state=uiconst.UI_DISABLED)
        Sprite(parent=self, name='corner_bot_flow_cytometer_%s' % self.step, texturePath=CORNER_TEXTURE_PATH, align=uiconst.TOPRIGHT, width=CORNER_SIZE, height=CORNER_SIZE, top=TEXT_TOP + self.text.height + CORNER_PADDING, left=TEXT_LEFT + TEXT_WIDTH - CORNER_SIZE, state=uiconst.UI_DISABLED, rotation=pi)

    def _add_continue_button(self):
        Button(name='continue_button_flow_cytometer_%s' % self.step, parent=self, align=uiconst.BOTTOMRIGHT, top=CONTINUE_BUTTON_TOP, left=CONTINUE_BUTTON_LEFT, label=GetByLabel(BUTTON_TEXT_BY_STEP[self.step]), func=lambda *args: self.go_to_next())

    def _add_bottom_decoration(self):
        Sprite(parent=self, name='bottom_decoration_flow_cytometer_%s' % self.step, texturePath=DECORATION_TEXTURE_PATH, align=uiconst.CENTERBOTTOM, width=DECORATION_WIDTH, height=DECORATION_HEIGHT, state=uiconst.UI_DISABLED)

    def _add_video(self):
        width, height = self.get_video_dimensions()
        self.video = StreamingVideoSprite(parent=self, name='video_flow_cytometer_%s' % self.step, videoPath=VIDEO_BY_STEP[self.step], videoLoop=False, align=uiconst.CENTER, width=width, height=height, state=uiconst.UI_DISABLED, spriteEffect=trinity.TR2_SFX_COPY, disableAudio=True, opacity=0.0)
        self.video.Pause()
        self.video_loop = StreamingVideoSprite(parent=self, name='video_flow_cytometer_loop_%s' % self.step, videoPath=LOOP_VIDEO_BY_STEP[self.step], videoLoop=True, align=uiconst.CENTER, width=width, height=height, state=uiconst.UI_DISABLED, spriteEffect=trinity.TR2_SFX_COPY, disableAudio=True, opacity=0.0)
        self.video_loop.Pause()
        self.video.OnVideoFinished = self.play_video_loop

    def show(self):
        self.opacity = 1.0
        self.play_video()

    def fade_in(self):
        animations.FadeIn(self, callback=self.play_video)

    def fade_in_text(self):
        animations.FadeIn(self.text)

    def get_video_dimensions(self):
        return (self.width, self.width * VIDEO_ASPECT_RATIO)

    def _play_video(self, video):
        video.Play()
        video.opacity = 1.0

    def _pause_video(self, video):
        video.Pause()
        video.opacity = 0.0

    def _play_intro_sound(self):
        self.audio.SendUIEvent(INTRO_AUDIO_BY_STEP[self.step])

    def _stop_intro_sound(self):
        self.audio.SendUIEvent(INTRO_STOP_AUDIO_BY_STEP[self.step])

    def play_video(self):
        self.is_in_intro_video = True
        self._pause_video(self.video_loop)
        self._play_video(self.video)
        self._play_intro_sound()
        call_after_wallclocktime_delay(self.fade_in_text, TEXT_DELAY_BY_STEP[self.step])

    def play_video_loop(self):
        self.is_in_intro_video = False
        self._pause_video(self.video)
        self._stop_intro_sound()
        self._play_video(self.video_loop)

    def Close(self):
        self._pause_video(self.video)
        self._pause_video(self.video_loop)
        if self.is_in_intro_video:
            self._stop_intro_sound()
        super(FlowCytometer, self).Close()

    def _OnResize(self, *args):
        width, height = self.get_video_dimensions()
        self.video.SetSize(width, height)
        self.video_loop.SetSize(width, height)
