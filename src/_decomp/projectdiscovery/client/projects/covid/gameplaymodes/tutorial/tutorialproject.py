#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\gameplaymodes\tutorial\tutorialproject.py
import carbonui.const as uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from localization import GetByLabel
from projectdiscovery.client.projects.covid.gameplaymodes.covidproject import CovidProject
from projectdiscovery.client.projects.covid.ui.instructions import Instructions
CONTINUE_BUTTON_WIDTH = 322
CONTINUE_BUTTON_HEIGHT = 64

class TutorialProject(CovidProject):
    default_is_validation_enabled = False

    def ApplyAttributes(self, attributes):
        super(TutorialProject, self).ApplyAttributes(attributes)
        self.go_to_next_sample_tutorial = attributes.get('go_to_next_sample_tutorial')

    def should_play_sample_sounds(self):
        return False

    def should_play_drawing_sounds(self):
        return True

    def set_instructions_text(self, text):
        if self.instructions and not self.instructions.destroyed:
            self.instructions.Close()
        if text:
            self.instructions = Instructions(name='instructions_container', parent=self.main_container, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, text=text)

    def set_continue_button_text(self, text):
        if self.continue_button_container and not self.continue_button_container.destroyed:
            self.continue_button_container.Close()
        if text:
            self.continue_button_container = Container(name='continue_button_container', parent=self.main_container, align=uiconst.TOPRIGHT, width=CONTINUE_BUTTON_WIDTH, height=CONTINUE_BUTTON_HEIGHT, opacity=0.0)
            self.continue_button = Button(parent=self.continue_button_container, align=uiconst.TOPRIGHT, label=GetByLabel(text), func=self.go_to_next_step)


class StaticImageProject(TutorialProject):
    SAMPLE_TEXTURE_PATH = None

    def get_new_task(self):
        return {'assets': {'texturePath': self.SAMPLE_TEXTURE_PATH}}

    def load_sample_image(self):
        if self.sample_image and not self.sample_image.destroyed:
            self.sample_image.Close()
        self.sample_image = Sprite(name='sample_image', parent=self.sample_container, align=uiconst.CENTER, texturePath=self.task['assets']['texturePath'])


class StaticTaskProject(TutorialProject):
    SAMPLE_TASK_ID = None

    def get_new_task(self):
        return self.service.get_new_task(original_code=self.SAMPLE_TASK_ID)
