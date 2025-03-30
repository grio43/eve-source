#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\gameplaymodes\tutorial\onegate.py
import carbonui.const as uiconst
from localization import GetByLabel
from projectdiscovery.client.projects.covid.gameplaymodes.tutorial.tutorialproject import StaticImageProject
from projectdiscovery.client.projects.covid.ui.tutorial.bluebox import BlueBox
from projectdiscovery.client.projects.covid.ui.tutorial.pointer import Pointer
NUMBER_OF_STEPS_ALL = 14
NUMBER_OF_STEPS_NORMAL_FLOW = 13
BLUE_BOX_POSITION_BY_STEP = {1: (0.73, 0.27),
 2: (0.55, 0.46),
 3: (0.44, 0.68),
 4: (0.29, 0.66),
 5: (0.22, 0.43),
 6: (0.09, 0.32),
 7: (0.15, 0.14),
 8: (0.39, 0.06),
 9: (0.68, 0.09),
 10: (0.73, 0.27),
 13: (0.73, 0.27)}
for step in xrange(0, NUMBER_OF_STEPS_ALL + 1):
    if step not in BLUE_BOX_POSITION_BY_STEP.keys():
        BLUE_BOX_POSITION_BY_STEP[step] = None

VERTEX_POSITION_IN_BLUE_BOX = 0.04
POINTER_FIRST_STEP_PADDING = 7
POINTER_SUBMIT_PADDING = 18
DRAWING_CLEAR_TOP = 0.79
BLUE_BOX_SIZE = 48

class OneGateTutorial(StaticImageProject):
    SAMPLE_TEXTURE_PATH = 'res:/UI/Texture/classes/ProjectDiscovery/covid/tutorial/onegate.png'
    LABELS_FOLDER = 'UI/ProjectDiscovery/Covid/Tutorial/OneGate/'
    POINTER_FIRST_STEP_TEXT = LABELS_FOLDER + 'PointerStartHere'
    POINTER_SUBMIT_TEXT = 'UI/ProjectDiscovery/Covid/Tutorial/PointerSubmit'
    DRAWING_CLEAR_TEXT = LABELS_FOLDER + 'DrawingCleared'

    def ApplyAttributes(self, attributes):
        super(OneGateTutorial, self).ApplyAttributes(attributes)
        self.blue_box = None
        self.pointer = None

    def load_drawing_tool(self):
        super(OneGateTutorial, self).load_drawing_tool()
        self.drawing_tool.Disable()
        self.drawing_tool.enable_markers()
        self.drawing_tool.on_wip_polygon_cleared.connect(self.on_wip_polygon_cleared)

    def add_instructions(self):
        instructions_by_step = {0: self.LABELS_FOLDER + 'InstructionsWelcome',
         1: self.LABELS_FOLDER + 'InstructionsFirstStep',
         10: self.LABELS_FOLDER + 'InstructionsFinalStep',
         11: self.LABELS_FOLDER + 'InstructionsSubmit',
         12: self.LABELS_FOLDER + 'InstructionsResults',
         13: self.LABELS_FOLDER + 'InstructionsDrawingCleared'}
        default_instructions = self.LABELS_FOLDER + 'InstructionsMiddleSteps'
        label = instructions_by_step.get(self.step, default_instructions)
        text = GetByLabel(label)
        self.set_instructions_text(text)

    def add_continue_button(self):
        button_text_by_step = {0: self.LABELS_FOLDER + 'ButtonWelcome',
         11: self.LABELS_FOLDER + 'ButtonSubmit',
         12: self.LABELS_FOLDER + 'ButtonResults'}
        label = button_text_by_step.get(self.step, None)
        self.set_continue_button_text(label)

    def go_to_next_step(self, *args):
        if self.step == NUMBER_OF_STEPS_NORMAL_FLOW - 1:
            self.go_to_next_sample_tutorial()
            return
        next_step = self.step + 1
        if next_step > NUMBER_OF_STEPS_NORMAL_FLOW:
            next_step = 2
        self.go_to_step(next_step)

    def go_to_step(self, step):
        if self.continue_button:
            self.continue_button.Disable()
        self.step = step
        self.add_instructions()
        self.add_continue_button()
        self.rescale_instructions()
        self.rescale_continue_button()
        self.update_drawing()
        self.update_blue_box()
        self.update_pointer()
        self.update_banner()
        self.update_error_message()
        if self.continue_button:
            self.continue_button.Enable()

    def on_wip_polygon_cleared(self):
        self.go_to_step(13)

    def update_drawing(self):
        if self.step > 11 and self.step != 13:
            self.drawing_tool.disable_markers()
        if self.step < 2 or self.step > 11:
            return
        box_position = BLUE_BOX_POSITION_BY_STEP[self.step - 1]
        if box_position:
            image_proportion_width, image_proportion_height = box_position
            x = (image_proportion_width + VERTEX_POSITION_IN_BLUE_BOX) * self.sample_image.width
            y = (image_proportion_height + VERTEX_POSITION_IN_BLUE_BOX) * self.sample_image.height
            self.drawing_tool.inject_click(x, y)

    def update_blue_box(self):
        if self.blue_box and not self.blue_box.destroyed:
            self.blue_box.Close()
        position = BLUE_BOX_POSITION_BY_STEP[self.step]
        if position:
            image_proportion_width, image_proportion_height = position
            sample_padding = self.get_sample_padding()
            left = self.sample_container.left + sample_padding / 2 + image_proportion_width * self.sample_image.width
            top = self.sample_container.top + sample_padding / 2 + image_proportion_height * self.sample_image.height
            self.blue_box = BlueBox(name='blue_box_%s' % self.step, parent=self, align=uiconst.TOPLEFT, idx=0, state=uiconst.UI_NORMAL, width=BLUE_BOX_SIZE, height=BLUE_BOX_SIZE, left=left, top=top)
            self.blue_box.OnClick = self.go_to_next_step

    def update_pointer(self):
        if self.pointer and not self.pointer.destroyed:
            self.pointer.Close()
        if self.step in (1, 13):
            image_proportion_width, image_proportion_height = BLUE_BOX_POSITION_BY_STEP[1]
            sample_padding = self.get_sample_padding()
            left = self.sample_container.left + sample_padding / 2 + image_proportion_width * self.sample_image.width
            top = self.sample_container.top + sample_padding / 2 + image_proportion_height * self.sample_image.height
            self.pointer = Pointer(name='pointer_%s' % self.step, parent=self, align=uiconst.TOPLEFT, idx=0, text=self.POINTER_FIRST_STEP_TEXT, left=left - BLUE_BOX_SIZE / 2, top=top + BLUE_BOX_SIZE + POINTER_FIRST_STEP_PADDING)
        elif self.step == 11:
            left = self.continue_button_container.left + self.continue_button.width / 2
            top = self.continue_button_container.top
            self.pointer = Pointer(name='pointer_%s' % self.step, parent=self, align=uiconst.TOPRIGHT, left=left, top=top, idx=0, should_point_up=False, text=self.POINTER_SUBMIT_TEXT)
            self.pointer.left -= self.pointer.width / 2
            self.pointer.top -= self.pointer.height + POINTER_SUBMIT_PADDING

    def update_banner(self):
        if self.step == 12:
            self.result_banner.load_result(result={'isSolved': False})
        else:
            self.result_banner.Hide()

    def update_error_message(self):
        if self.step == 13:
            self.error_message.show_errors([self.DRAWING_CLEAR_TEXT])
        else:
            self.error_message.hide_error()

    def rescale_content(self):
        super(OneGateTutorial, self).rescale_content()
        self.update_blue_box()
        self.update_pointer()
        self.update_error_message()
