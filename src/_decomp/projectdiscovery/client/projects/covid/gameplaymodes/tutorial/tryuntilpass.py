#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\gameplaymodes\tutorial\tryuntilpass.py
import carbonui.const as uiconst
from localization import GetByLabel
from projectdiscovery.client.projects.covid.gameplaymodes.tutorial.tutorialproject import StaticTaskProject
from projectdiscovery.client.projects.covid.ui.resultbanner import ResultType
from projectdiscovery.client.projects.covid.ui.tutorial.pointer import Pointer
NUMBER_OF_STEPS = 6
STEPS_DRAWING = [0, 1]
STEP_PASSED = 2
STEPS_FAILED_INCORRECT_NUMBER_OF_CLUSTERS = [3, 4]
STEP_FAILED_LOW_ACCURACY = 5
STEPS_RESULTS_PASSED = [STEP_PASSED]
STEPS_RESULTS_FAILED = STEPS_FAILED_INCORRECT_NUMBER_OF_CLUSTERS + [STEP_FAILED_LOW_ACCURACY]
STEPS_RESULTS = STEPS_RESULTS_PASSED + STEPS_RESULTS_FAILED
STEPS_RESULTS_WITH_SCORES = [STEP_PASSED, STEP_FAILED_LOW_ACCURACY]
POINTER_SUBMIT_TEXT = 'UI/ProjectDiscovery/Covid/Tutorial/PointerSubmit'
POINTER_SUBMIT_PADDING = 18
STATISTICS_TO_INSTRUCTIONS_PADDING = 42
ERROR_MESSAGE_TOP = 0.79

class TryUntilPassTutorial(StaticTaskProject):
    NUMBER_OF_POLYGONS = 0
    GENERIC_LABELS_FOLDER = 'UI/ProjectDiscovery/Covid/Tutorial/TryUntilPass/'
    SPECIAL_LABELS_FOLDER = GENERIC_LABELS_FOLDER

    def ApplyAttributes(self, attributes):
        super(TryUntilPassTutorial, self).ApplyAttributes(attributes)
        self.pointer = None

    def load_drawing_tool(self):
        super(TryUntilPassTutorial, self).load_drawing_tool()
        self.drawing_tool.on_polygon_added.connect(self.on_polygon_completed)

    def has_too_many_polygons(self, number_of_polygons):
        return number_of_polygons > self.NUMBER_OF_POLYGONS

    def has_too_few_polygons(self, number_of_polygons):
        return number_of_polygons < self.NUMBER_OF_POLYGONS

    def has_low_accuracy(self):
        return 'score' in self.result and self.result['score'] <= 0.5

    def on_polygon_completed(self, order):
        if self.step == 0 and order == 3:
            self.go_to_step(1)

    def go_to_next_step(self, *args):
        if self.step in STEPS_DRAWING:
            self.go_to_step(2)
        elif self.step in STEPS_RESULTS_PASSED:
            self.go_to_next_sample_tutorial()
        elif self.step in STEPS_RESULTS_FAILED:
            self.go_to_step(0)

    def go_to_step(self, step):
        self.step = step
        if self.continue_button:
            self.continue_button.Disable()
        self.hide_rewards()
        if self.step not in STEPS_DRAWING:
            self.drawing_tool.Disable()
            self.cells.Disable()
        if self.step == 0:
            self.load_task()
            self.drawing_tool.Enable()
            self.cells.Enable()
        if self.step == STEP_PASSED:
            polygons = self.drawing_tool.get_polygons()
            number_of_polygons = len(polygons) if polygons else 0
            if self.has_too_many_polygons(number_of_polygons):
                self.step = 3
            elif self.has_too_few_polygons(number_of_polygons):
                self.step = 4
            else:
                self.submit_and_show_solution()
                if self.has_low_accuracy():
                    self.step = 5
        self.add_instructions()
        self.add_continue_button()
        self.rescale_instructions()
        self.rescale_continue_button()
        if self.step not in STEPS_RESULTS:
            self.hide_result_banner()
        if self.step not in STEPS_RESULTS_WITH_SCORES:
            self.hide_statistics()
        if self.step == STEP_PASSED:
            self.show_result_banner()
            self.show_statistics(show_labels=False)
        if self.step == STEP_FAILED_LOW_ACCURACY:
            self.show_result_banner(result_type=ResultType.FAILED)
            self.show_statistics(show_labels=False)
        if self.step in STEPS_FAILED_INCORRECT_NUMBER_OF_CLUSTERS:
            self.show_result_banner(result_type=ResultType.FAILED)
        self.update_pointer()
        self.update_error_message()
        self.update_instructions()
        if self.continue_button:
            self.continue_button.Enable()

    def add_instructions(self):
        instructions_by_step = {0: self.SPECIAL_LABELS_FOLDER + 'InstructionsGeneral',
         1: self.SPECIAL_LABELS_FOLDER + 'InstructionsGeneral',
         2: self.SPECIAL_LABELS_FOLDER + 'InstructionsPassed',
         3: self.SPECIAL_LABELS_FOLDER + 'InstructionsFailedTooManyPolygons',
         4: self.SPECIAL_LABELS_FOLDER + 'InstructionsFailedTooFewPolygons',
         5: self.SPECIAL_LABELS_FOLDER + 'InstructionsFailedLowAccuracy'}
        label = instructions_by_step[self.step]
        text = GetByLabel(label, numberOfPolygons=self.NUMBER_OF_POLYGONS)
        self.set_instructions_text(text)

    def add_continue_button(self):
        button_text_by_step = {0: self.GENERIC_LABELS_FOLDER + 'ButtonSubmit',
         1: self.GENERIC_LABELS_FOLDER + 'ButtonSubmit',
         2: self.SPECIAL_LABELS_FOLDER + 'ButtonGoToNext',
         3: self.GENERIC_LABELS_FOLDER + 'ButtonRestart',
         4: self.GENERIC_LABELS_FOLDER + 'ButtonRestart',
         5: self.GENERIC_LABELS_FOLDER + 'ButtonRestart'}
        label = button_text_by_step[self.step]
        self.set_continue_button_text(label)

    def update_error_message(self):
        error_message_text_by_step = {3: self.GENERIC_LABELS_FOLDER + 'ErrorTooManyClustersMarked',
         4: self.GENERIC_LABELS_FOLDER + 'ErrorTooFewClustersMarked',
         5: self.GENERIC_LABELS_FOLDER + 'ErrorLowAccuracy'}
        text_path = error_message_text_by_step.get(self.step, None)
        if text_path:
            self.error_message.show_errors([text_path])
        else:
            self.error_message.hide_error()

    def update_pointer(self):
        if self.pointer and not self.pointer.destroyed:
            self.pointer.Close()
        if self.step == 1:
            left = self.continue_button_container.left + self.continue_button.width / 2
            top = self.continue_button_container.top
            self.pointer = Pointer(name='pointer_%s' % self.step, parent=self, align=uiconst.TOPRIGHT, left=left, top=top, idx=0, should_point_up=False, text=POINTER_SUBMIT_TEXT)
            self.pointer.left -= self.pointer.width / 2
            self.pointer.top -= self.pointer.height + POINTER_SUBMIT_PADDING

    def update_instructions(self):
        if self.step in [STEP_PASSED, STEP_FAILED_LOW_ACCURACY]:
            self.instructions.top += self.statistics.get_gauges_height() + STATISTICS_TO_INSTRUCTIONS_PADDING

    def rescale_content(self):
        super(TryUntilPassTutorial, self).rescale_content()
        self.update_pointer()
        self.update_error_message()
        self.update_instructions()


class HeartShapedTutorial(TryUntilPassTutorial):
    SAMPLE_TASK_ID = 'be362d8b-4ff4-448b-877f-23b8c2cb4fe0'
    NUMBER_OF_POLYGONS = 3
    SPECIAL_LABELS_FOLDER = 'UI/ProjectDiscovery/Covid/Tutorial/TryUntilPass/HeartShaped/'


class ValleyTutorial(TryUntilPassTutorial):
    SAMPLE_TASK_ID = 'eb4c6403-e878-43cf-a009-9c8c566ae90f'
    NUMBER_OF_POLYGONS = 3
    SPECIAL_LABELS_FOLDER = 'UI/ProjectDiscovery/Covid/Tutorial/TryUntilPass/Valley/'


class TailsAndValleysTutorial(TryUntilPassTutorial):
    SAMPLE_TASK_ID = '21cbef0c-684e-4a4c-b1fe-be6e24d894c2'
    NUMBER_OF_POLYGONS = 5
    SPECIAL_LABELS_FOLDER = 'UI/ProjectDiscovery/Covid/Tutorial/TryUntilPass/TailsAndValleys/'


class TailTutorial(TryUntilPassTutorial):
    SAMPLE_TASK_ID = 'ff9f9a21-954b-4c1c-9a54-16b21cf17670'
    NUMBER_OF_POLYGONS = 4
    SPECIAL_LABELS_FOLDER = 'UI/ProjectDiscovery/Covid/Tutorial/TryUntilPass/Tail/'
