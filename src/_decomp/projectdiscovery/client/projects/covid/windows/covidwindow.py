#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\windows\covidwindow.py
import carbonui.const as uiconst
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from projectdiscovery.client.projects.covid.gameplaymodes.covidflowcytometerintro import CovidFlowCytometerIntro
from projectdiscovery.client.projects.covid.gameplaymodes.covidintro import CovidIntro
from projectdiscovery.client.projects.covid.gameplaymodes.covidproject import CovidProject
from projectdiscovery.client.projects.covid.gameplaymodes.covidretraining import OfferRetraining
from projectdiscovery.client.projects.covid.gameplaymodes.covidtransition import CovidTransition
from projectdiscovery.client.projects.covid.gameplaymodes.tutorial.tryuntilpass import HeartShapedTutorial, TailsAndValleysTutorial, TailTutorial, ValleyTutorial
from projectdiscovery.client.projects.covid.gameplaymodes.tutorial.onegate import OneGateTutorial
from projectdiscovery.client.projects.covid.gameplaymodes.tutorial.twogates import TwoGatesTutorial
from projectdiscovery.client.projects.covid.sounds import Sounds
from projectdiscovery.client.projects.covid.ui.dialog import DialogPopup
from projectdiscovery.client.ui.projectdiscoverywindow import BaseProjectDiscoveryWindow
PADDING_TOP = 20
SAMPLE_TUTORIAL = [OneGateTutorial,
 TwoGatesTutorial,
 HeartShapedTutorial,
 ValleyTutorial,
 TailsAndValleysTutorial,
 TailTutorial]
TUTORIAL_LABEL_PATHS_FOLDER = 'UI/ProjectDiscovery/Covid/Tutorial/'
ERROR_LABEL_PATHS_FOLDER = 'UI/ProjectDiscovery/Covid/Errors/'
DOCTOR_IMAGE_TEXTURE_PATH = 'res:/UI/Texture/classes/ProjectDiscovery/covid/intro/doctor_cossarizza.png'
ERROR_IMAGE_TEXTURE_PATH = 'res:/UI/Texture/classes/ProjectDiscovery/covid/error_message_image.png'

class CovidWindow(BaseProjectDiscoveryWindow):
    default_windowID = 'CovidWindow'
    default_minSize = (1268, 726)
    default_width = 1268
    default_height = 726
    default_opacity = 0.8
    default_showHelpInTutorial = True

    def ApplyAttributes(self, attributes):
        self.service = sm.GetService('projectDiscoveryClient')
        self.audio = sm.GetService('audio')
        self.is_in_sample_tutorial = False
        super(CovidWindow, self).ApplyAttributes(attributes)

    def Close(self, *args, **kwargs):
        self.audio.SendUIEvent(Sounds.TUTORIAL_END)
        super(CovidWindow, self).Close(*args, **kwargs)

    def OnEndMaximize_(self, *args):
        if hasattr(self._project_container, 'OnMinimize'):
            self._project_container.OnMaximize()

    def OnEndMinimize_(self, *args):
        if hasattr(self._project_container, 'OnMaximize'):
            self._project_container.OnMinimize()

    def on_connection_error(self):
        self.Close()
        self.show_connection_error_dialogue()

    def show_connection_error_dialogue(self):
        DialogPopup.Open(caption=ERROR_LABEL_PATHS_FOLDER + 'ConnectionErrorTitle', text=ERROR_LABEL_PATHS_FOLDER + 'ConnectionErrorText', image=DOCTOR_IMAGE_TEXTURE_PATH, imageWidth=238, imageHeight=281)

    def show_task_retrieval_error(self):
        DialogPopup.Open(caption=ERROR_LABEL_PATHS_FOLDER + 'TaskRetrievalFailedTitle', text=ERROR_LABEL_PATHS_FOLDER + 'TaskRetrievalFailedText', image=ERROR_IMAGE_TEXTURE_PATH, imageWidth=178, imageHeight=168)

    def show_classification_error(self):
        DialogPopup.Open(caption=ERROR_LABEL_PATHS_FOLDER + 'ClassificationErrorTitle', text=ERROR_LABEL_PATHS_FOLDER + 'ClassificationErrorMishap', image=DOCTOR_IMAGE_TEXTURE_PATH, imageWidth=238, imageHeight=281)

    def set_project(self):
        self._project_container = CovidProject(name='covid_project', parent=self.project_container, align=uiconst.TOALL, bottomContainer=self._bottom_container, clipChildren=False, opacity=0, padTop=PADDING_TOP, scale=self.get_scale(), window=self)
        self.is_in_sample_tutorial = False
        self.stop_tutorial_audio()

    def set_tutorial(self):
        self._project_container = CovidIntro(name='covid_intro', parent=self.project_container, align=uiconst.TOALL, bottomContainer=self._bottom_container, clipChildren=False, opacity=0, padTop=PADDING_TOP, scale=self.get_scale(), window=self, go_to_flow_cytometer_intro=self.go_to_flow_cytometer_intro, go_to_transition=self.go_to_transition)
        self.is_in_sample_tutorial = False
        self.stop_tutorial_audio()

    def set_flow_cytometer_intro(self):
        self._project_container = CovidFlowCytometerIntro(name='covid_flow_cytometer_intro', parent=self.project_container, window=self, align=uiconst.CENTER, width=self.width, height=self.height, bottomContainer=self._bottom_container, clipChildren=False, opacity=0, scale=self.get_scale(), go_to_transition=self.go_to_transition)
        self.is_in_sample_tutorial = False
        self.stop_tutorial_audio()

    def set_transition(self):
        self._project_container = CovidTransition(name='covid_transition', parent=self.project_container, align=uiconst.TOALL, bottomContainer=self._bottom_container, clipChildren=False, opacity=0, padTop=PADDING_TOP, scale=self.get_scale(), window=self, go_to_sample_tutorial=self.go_to_next_sample_tutorial, go_to_game=self.go_to_game)
        self.is_in_sample_tutorial = False
        self.stop_tutorial_audio()

    def set_sample_tutorial(self):
        self.start_tutorial_audio()
        sample_tutorial_step = max(0, self.service.get_sample_tutorial_step())
        tutorial_class = SAMPLE_TUTORIAL[sample_tutorial_step]
        self._project_container = tutorial_class(name='covid_sample_tutorial_%s' % sample_tutorial_step, parent=self.project_container, align=uiconst.TOALL, bottomContainer=self._bottom_container, clipChildren=False, opacity=0, padTop=PADDING_TOP, scale=self.get_scale(), window=self, playerStatistics=self.player_statistics if 'message' not in self.player_statistics else None, playerState=self.player_exp_state, go_to_next_sample_tutorial=self.go_to_next_sample_tutorial)
        self.is_in_sample_tutorial = True

    def set_retraining_offer(self):
        self._project_container = OfferRetraining(name='offer_retraining', parent=self.project_container, align=uiconst.TOALL, bottomContainer=self._bottom_container, clipChildren=False, opacity=0, padTop=PADDING_TOP, scale=self.get_scale(), window=self, go_to_sample_tutorial=self.go_to_tutorial_sample_3, go_to_game=self.go_to_game)
        self.is_in_sample_tutorial = False
        self.stop_tutorial_audio()

    def start_tutorial_audio(self):
        if not self.is_in_sample_tutorial:
            self.audio.SendUIEvent(Sounds.TUTORIAL_START)

    def stop_tutorial_audio(self):
        self.audio.SendUIEvent(Sounds.TUTORIAL_END)

    def go_to_tutorial_start(self):
        self.service.restart_all()
        self._setup_tutorial()

    def go_to_tutorial_sample_3(self):
        self.service.go_to_sample_3_tutorial()
        self._setup_sample_tutorial()

    def go_to_flow_cytometer_intro(self):
        self.service.complete_intro()
        self._setup_flow_cytometer_intro()

    def go_to_transition(self):
        self.service.complete_flow_cytometer_intro()
        self._setup_transition()

    def go_to_next_sample_tutorial(self):
        self.service.complete_transition()
        self.service.go_to_next_sample_tutorial_step()
        self._setup_sample_tutorial()

    def go_to_game(self):
        self.service.complete_tutorial()
        self.audio.SendUIEvent(Sounds.TUTORIAL_END)
        self._setup_actual_project()

    def on_help_button_clicked(self):
        DialogPopup.Open(caption=TUTORIAL_LABEL_PATHS_FOLDER + 'RestartCaption', text=TUTORIAL_LABEL_PATHS_FOLDER + 'RestartText', image=DOCTOR_IMAGE_TEXTURE_PATH, imageWidth=238, imageHeight=281, confirmFunction=self.go_to_tutorial_start, confirmText=TUTORIAL_LABEL_PATHS_FOLDER + 'ButtonRestartOk', cancelText=TUTORIAL_LABEL_PATHS_FOLDER + 'ButtonRestartCancel', showConfirm=True, showCancel=True)

    def set_background(self):
        self._background_scene = None

    def setup_side_panels(self):
        pass

    def set_background_fill(self):
        Fill(name='projectDiscovery_backgroundFill', align=uiconst.TOALL, parent=self.sr.main, padTop=-20, color=(0.0, 0.0, 0.0, 1.0))

    def _setup_flow_cytometer_intro(self):
        self._clean()
        self.set_flow_cytometer_intro()
        animations.FadeIn(self._project_container)

    def _setup_transition(self):
        self._clean()
        self.set_transition()
        animations.FadeIn(self._project_container)

    def _setup_sample_tutorial(self):
        self._clean()
        try:
            self.set_sample_tutorial()
            animations.FadeIn(self._project_container)
        except IndexError:
            self.go_to_game()

    def _setup_retraining_offer(self):
        self._clean()
        self.set_retraining_offer()
        animations.FadeIn(self._project_container)

    def _setup_project_type(self):
        if self.service.should_offer_retraining():
            self._setup_retraining_offer()
            self.service.disable_retraining_offer()
        elif self.service.is_tutorial_complete():
            self._setup_actual_project()
        elif not self.service.is_intro_complete():
            self._setup_tutorial()
        elif not self.service.is_flow_cytometer_intro_complete():
            self._setup_flow_cytometer_intro()
        elif not self.service.is_transition_complete():
            self._setup_transition()
        else:
            self._setup_sample_tutorial()
