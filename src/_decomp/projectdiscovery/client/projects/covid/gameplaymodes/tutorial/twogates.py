#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\gameplaymodes\tutorial\twogates.py
import carbonui.const as uiconst
from localization import GetByLabel
from projectdiscovery.client.projects.covid.gameplaymodes.tutorial.tutorialproject import StaticTaskProject
from projectdiscovery.client.projects.covid.ui.resultbanner import ResultType
from projectdiscovery.client.projects.covid.ui.tutorial.pointer import Pointer
NUMBER_OF_STEPS = 7
DRAWING_STEPS = [0,
 1,
 2,
 3,
 4]
SUBMITTED_STEP = 5
RESULTS_STEP = 6
POINTER_SUBMIT_TEXT = 'UI/ProjectDiscovery/Covid/Tutorial/PointerSubmit'
POINTER_SUBMIT_PADDING = 18
STATISTICS_TO_INSTRUCTIONS_PADDING = 42

class TwoGatesTutorial(StaticTaskProject):
    SAMPLE_TASK_ID = 'ed134308-e080-49bc-be56-169a5f839c96'
    LABELS_FOLDER = 'UI/ProjectDiscovery/Covid/Tutorial/TwoGates/'

    def ApplyAttributes(self, attributes):
        super(TwoGatesTutorial, self).ApplyAttributes(attributes)
        self.pointer = None

    def add_instructions(self):
        instructions_by_step = {0: self.LABELS_FOLDER + 'InstructionsWelcome',
         1: self.LABELS_FOLDER + 'InstructionsFirstGate',
         2: self.LABELS_FOLDER + 'InstructionsSecondGateStart',
         3: self.LABELS_FOLDER + 'InstructionsSecondGate',
         4: self.LABELS_FOLDER + 'InstructionsSubmit',
         5: self.LABELS_FOLDER + 'InstructionsSubmitted',
         6: self.LABELS_FOLDER + 'InstructionsResults'}
        label = instructions_by_step[self.step]
        text = GetByLabel(label)
        self.set_instructions_text(text)

    def add_continue_button(self):
        button_text_by_step = {4: self.LABELS_FOLDER + 'ButtonSubmit',
         5: self.LABELS_FOLDER + 'ButtonSubmitted',
         6: self.LABELS_FOLDER + 'ButtonResults'}
        label = button_text_by_step.get(self.step, None)
        self.set_continue_button_text(label)

    def load_drawing_tool(self):
        super(TwoGatesTutorial, self).load_drawing_tool()
        self.drawing_tool.on_polygon_added.connect(self.on_polygon_completed)
        self.drawing_tool.on_polygon_started.connect(self.on_polygon_started)

    def on_polygon_started(self):
        if self.step in (0, 2):
            self.go_to_next_step()

    def on_polygon_completed(self, order):
        if self.step == 1 and order == 0:
            self.go_to_next_step()
        if self.step == 3 and order == 1:
            self.go_to_next_step()

    def go_to_next_step(self, *args):
        if self.step + 1 >= NUMBER_OF_STEPS:
            self.go_to_next_sample_tutorial()
            return
        self.go_to_step(self.step + 1)

    def go_to_step(self, step):
        if self.continue_button:
            self.continue_button.Disable()
        self.step = step
        self.add_instructions()
        self.add_continue_button()
        self.rescale_instructions()
        self.rescale_continue_button()
        self.hide_rewards()
        if self.step not in DRAWING_STEPS:
            self.drawing_tool.Disable()
            self.cells.Disable()
        if self.step != SUBMITTED_STEP:
            self.hide_result_banner()
        if self.step != RESULTS_STEP:
            self.hide_statistics()
        if self.step == 0:
            self.load_task()
            self.drawing_tool.Enable()
            self.cells.Enable()
        if self.step == SUBMITTED_STEP:
            self.submit_and_show_solution()
            self.show_result_banner(result_type=ResultType.UNKNOWN)
        if self.step == RESULTS_STEP:
            self.show_statistics(show_labels=False)
        self.update_pointer()
        self.update_instructions()
        if self.continue_button:
            self.continue_button.Enable()

    def update_pointer(self):
        if self.pointer and not self.pointer.destroyed:
            self.pointer.Close()
        if self.step == 4:
            left = self.continue_button_container.left + self.continue_button.width / 2
            top = self.continue_button_container.top
            self.pointer = Pointer(name='pointer_%s' % self.step, parent=self, align=uiconst.TOPRIGHT, left=left, top=top, idx=0, should_point_up=False, text=POINTER_SUBMIT_TEXT)
            self.pointer.left -= self.pointer.width / 2
            self.pointer.top -= self.pointer.height + POINTER_SUBMIT_PADDING

    def update_instructions(self):
        if self.step == RESULTS_STEP:
            self.instructions.top += self.statistics.get_gauges_height() + STATISTICS_TO_INSTRUCTIONS_PADDING

    def rescale_content(self):
        super(TwoGatesTutorial, self).rescale_content()
        self.update_pointer()
        self.update_instructions()
