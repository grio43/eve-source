#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\gameplaymodes\covidintro.py
import carbonui.const as uiconst
from projectdiscovery.client.projects.covid.gameplaymodes.covidproject import CovidProject
from projectdiscovery.client.projects.covid.ui.intro.doctorpresentation import DoctorPresentation
from projectdiscovery.client.projects.covid.ui.intro.welcome import Welcome

class FlowStep(object):
    WELCOME = 0
    DOCTOR_PRESENTATION = 1


LABELS_FOLDER = 'UI/ProjectDiscovery/Covid/Intro/'
SKIP_BUTTON_LABEL_PATH = LABELS_FOLDER + 'ButtonSkip'
CONTINUE_BUTTON_LABEL_PATH = LABELS_FOLDER + 'ButtonContinue'
DOCTOR_PRESENTATION_LABEL_PATH = LABELS_FOLDER + 'DoctorPresentation'

class CovidIntro(CovidProject):

    def ApplyAttributes(self, attributes):
        self.go_to_flow_cytometer_intro = attributes.get('go_to_flow_cytometer_intro')
        self.go_to_transition = attributes.get('go_to_transition')
        self.page_welcome = None
        self.page_doctor_presentation = None
        super(CovidIntro, self).ApplyAttributes(attributes)

    def should_play_sample_sounds(self):
        return False

    def should_play_drawing_sounds(self):
        return False

    def setup_content(self):
        self.add_page_welcome()
        self.add_page_doctor_presentation()

    def initialize(self):
        self.step = FlowStep.WELCOME
        self.hide_page_doctor_presentation()
        self.show_page_welcome()

    def go_to_doctor_presentation(self):
        self.step = FlowStep.DOCTOR_PRESENTATION
        self.hide_page_welcome()
        self.show_page_doctor_presentation()

    def add_page_welcome(self):
        self.page_welcome = Welcome(name='page_welcome', parent=self.main_container, align=uiconst.TOALL, opacity=0.0, go_to_doctor_presentation=self.go_to_doctor_presentation)

    def add_page_doctor_presentation(self):
        self.page_doctor_presentation = DoctorPresentation(name='page_doctor_presentation', parent=self.main_container, align=uiconst.TOALL, opacity=0.0, leftButtonFunction=self.go_to_transition, rightButtonFunction=self.go_to_flow_cytometer_intro, leftButtonText=SKIP_BUTTON_LABEL_PATH, rightButtonText=CONTINUE_BUTTON_LABEL_PATH, text=DOCTOR_PRESENTATION_LABEL_PATH)

    def show_page_welcome(self):
        if self.page_welcome:
            self.page_welcome.fade_in()

    def show_page_doctor_presentation(self):
        if self.page_doctor_presentation:
            self.page_doctor_presentation.fade_in()

    def hide_page_welcome(self):
        if self.page_welcome:
            self.page_welcome.opacity = 0.0

    def hide_page_doctor_presentation(self):
        if self.page_doctor_presentation:
            self.page_doctor_presentation.opacity = 0.0

    def rescale_content(self):
        pass
