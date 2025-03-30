#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\gameplaymodes\covidtransition.py
import carbonui.const as uiconst
from projectdiscovery.client.projects.covid.gameplaymodes.covidproject import CovidProject
from projectdiscovery.client.projects.covid.ui.intro.doctorpresentation import DoctorPresentation

class CovidTransition(CovidProject):
    LABELS_FOLDER = 'UI/ProjectDiscovery/Covid/Intro/'
    TRANSITION_SKIP_BUTTON_LABEL_PATH = LABELS_FOLDER + 'TransitionButtonSkip'
    TRANSITION_CONTINUE_BUTTON_LABEL_PATH = LABELS_FOLDER + 'TransitionButtonContinue'
    TRANSITION_TEXT_LABEL_PATH = LABELS_FOLDER + 'TransitionText'

    def ApplyAttributes(self, attributes):
        self.go_to_sample_tutorial = attributes.get('go_to_sample_tutorial')
        self.go_to_game = attributes.get('go_to_game')
        super(CovidTransition, self).ApplyAttributes(attributes)

    def should_play_sample_sounds(self):
        return False

    def should_play_drawing_sounds(self):
        return False

    def setup_content(self):
        self.panel = None

    def initialize(self):
        if self.panel and not self.panel.destroyed:
            self.panel.Close()
        self.panel = DoctorPresentation(name='transition_step_%s' % self.step, parent=self.main_container, align=uiconst.TOALL, opacity=0.0, leftButtonFunction=self.go_to_game, rightButtonFunction=self.go_to_sample_tutorial, leftButtonText=self.TRANSITION_SKIP_BUTTON_LABEL_PATH, rightButtonText=self.TRANSITION_CONTINUE_BUTTON_LABEL_PATH, text=self.TRANSITION_TEXT_LABEL_PATH)
        self.panel.fade_in()

    def rescale_content(self):
        pass
