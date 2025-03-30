#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\intro\doctorpresentation.py
import carbonui.const as uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import Label
from carbonui.fontconst import STYLE_SMALLTEXT
from localization import GetByLabel
from projectdiscovery.client.projects.covid.sounds import Sounds
from projectdiscovery.client.projects.covid.ui.instructions import Instructions
import trinity
from uthread2 import call_after_wallclocktime_delay
LABELS_FOLDER = 'UI/ProjectDiscovery/Covid/Intro/'
DOCTOR_NAME_LABEL_PATH = LABELS_FOLDER + 'DoctorName'
DOCTOR_TITLE_LABEL_PATH = LABELS_FOLDER + 'DoctorTitle'
TEXTURE_FOLDER = 'res:/UI/Texture/classes/ProjectDiscovery/covid/intro/'
DOCTOR_IMAGE_TEXTURE_PATH = TEXTURE_FOLDER + 'doctor_cossarizza.png'
DOCTOR_TITLE_BACKGROUND_TEXTURE_PATH = TEXTURE_FOLDER + 'label_background.png'
DOCTOR_IMAGE_DECORATION_TEXTURE_PATH = TEXTURE_FOLDER + 'decoration_frame.png'
DOCTOR_IMAGE_WIDTH = 477
DOCTOR_IMAGE_HEIGHT = 563
DOCTOR_IMAGE_TOP = 87
DOCTOR_IMAGE_LEFT = 55
DOCTOR_IMAGE_DECORATION_WIDTH = 240
DOCTOR_IMAGE_DECORATION_HEIGHT = 13
DOCTOR_IMAGE_DECORATION_TOP = -3
DOCTOR_TITLE_BACKGROUND_WIDTH = 368
DOCTOR_TITLE_BACKGROUND_HEIGHT = 83
DOCTOR_TITLE_BACKGROUND_TOP = DOCTOR_IMAGE_TOP + 420
DOCTOR_TITLE_BACKGROUND_LEFT = DOCTOR_IMAGE_LEFT + 1
DOCTOR_NAME_FONTSIZE = 24
DOCTOR_TITLE_FONTSIZE = 14
DOCTOR_NAME_COLOR = (0.06, 0.69, 0.94, 1.0)
CELL_IMAGES_TOP = 87
CELL_IMAGES_LEFT = DOCTOR_IMAGE_LEFT + DOCTOR_IMAGE_WIDTH + 18
CELL_IMAGE_SIZE = 126
CELL_IMAGE_PADDING = 20
CELL_IMAGE_SQUARE_SIZE = 10
CELL_IMAGE_SQUARE_COLOR = (0.584, 0.584, 0.584, 1.0)
TEXT_TOP = 87
TEXT_WIDTH = 505
TEXT_LEFT = 55
BUTTON_WIDTH = 243
BUTTON_HEIGHT = 64
BUTTON_TOP = 588
PADDING_BETWEEN_BUTTONS = 19

class DoctorPresentation(Container):

    def ApplyAttributes(self, attributes):
        super(DoctorPresentation, self).ApplyAttributes(attributes)
        self.audio = sm.GetService('audio')
        self.left_button_function = attributes.get('leftButtonFunction', None)
        self.left_button_text = attributes.get('leftButtonText', '')
        self.right_button_function = attributes.get('rightButtonFunction', None)
        self.right_button_text = attributes.get('rightButtonText', '')
        label_path = attributes.get('text', '')
        self.text = GetByLabel(label_path) if label_path else ''
        self.add_doctor_title()
        self.add_doctor_image()
        self.add_cells()
        self.add_text()
        self.add_buttons()

    def Close(self):
        super(DoctorPresentation, self).Close()
        self.audio.SendUIEvent(Sounds.DOCTOR_END)

    def add_doctor_title(self):
        self.doctor_title = Container(name='doctor_title', parent=self, align=uiconst.TOALL)
        doctor_name = Label(name='doctor_name', parent=self.doctor_title, align=uiconst.TOPLEFT, top=DOCTOR_TITLE_BACKGROUND_TOP + 7, left=DOCTOR_TITLE_BACKGROUND_LEFT + 24, fontsize=DOCTOR_NAME_FONTSIZE, text=GetByLabel(DOCTOR_NAME_LABEL_PATH), color=DOCTOR_NAME_COLOR, bold=True, letterspace=1, fontStyle=STYLE_SMALLTEXT)
        name_width = doctor_name.width
        name_left = doctor_name.left - DOCTOR_TITLE_BACKGROUND_LEFT
        title_background_width = max(DOCTOR_TITLE_BACKGROUND_WIDTH, name_width + 2 * name_left)
        Label(name='doctor_title', parent=self.doctor_title, align=uiconst.TOPLEFT, top=DOCTOR_TITLE_BACKGROUND_TOP + 38, left=DOCTOR_TITLE_BACKGROUND_LEFT + 24, fontsize=DOCTOR_TITLE_FONTSIZE, text=GetByLabel(DOCTOR_TITLE_LABEL_PATH), letterspace=1)
        Sprite(name='doctor_title_background', parent=self.doctor_title, align=uiconst.TOPLEFT, width=title_background_width, height=DOCTOR_TITLE_BACKGROUND_HEIGHT, top=DOCTOR_TITLE_BACKGROUND_TOP, left=DOCTOR_TITLE_BACKGROUND_LEFT, texturePath=DOCTOR_TITLE_BACKGROUND_TEXTURE_PATH, blendMode=trinity.TR2_SBM_NONE)
        self.doctor_title.Hide()

    def add_doctor_image(self):
        Sprite(name='doctor_image_decoration', parent=self, align=uiconst.TOPLEFT, width=DOCTOR_IMAGE_DECORATION_WIDTH, height=DOCTOR_IMAGE_DECORATION_HEIGHT, top=DOCTOR_IMAGE_TOP + DOCTOR_IMAGE_DECORATION_TOP, left=DOCTOR_IMAGE_LEFT + (DOCTOR_IMAGE_WIDTH - DOCTOR_IMAGE_DECORATION_WIDTH) / 2, texturePath=DOCTOR_IMAGE_DECORATION_TEXTURE_PATH)
        Sprite(name='doctor_image', parent=self, align=uiconst.TOPLEFT, width=DOCTOR_IMAGE_WIDTH, height=DOCTOR_IMAGE_HEIGHT, top=DOCTOR_IMAGE_TOP, left=DOCTOR_IMAGE_LEFT, texturePath=DOCTOR_IMAGE_TEXTURE_PATH)

    def add_cells(self):
        cells_container = Container(name='cells_container', parent=self, align=uiconst.TOPLEFT, width=CELL_IMAGE_SIZE, height=CELL_IMAGE_SIZE * 4 + CELL_IMAGE_PADDING * 3, top=CELL_IMAGES_TOP, left=CELL_IMAGES_LEFT)
        top = 0
        for index in xrange(1, 5):
            cell_container = Container(name='cell_container', parent=cells_container, align=uiconst.TOTOP, height=CELL_IMAGE_SIZE, top=top)
            Fill(name='cell_%s_decoration' % index, parent=cell_container, align=uiconst.BOTTOMRIGHT, width=CELL_IMAGE_SQUARE_SIZE, height=CELL_IMAGE_SQUARE_SIZE, color=CELL_IMAGE_SQUARE_COLOR, left=1, top=1)
            Sprite(name='cell_%s' % index, parent=cell_container, align=uiconst.TOALL, texturePath=TEXTURE_FOLDER + 'cell%s.png' % index)
            top = CELL_IMAGE_PADDING

    def add_text(self):
        presentation = Instructions(name='presentation', parent=self, align=uiconst.TOPRIGHT, width=TEXT_WIDTH, top=TEXT_TOP, left=TEXT_LEFT, text=self.text)
        presentation.height = presentation.get_content_height()

    def add_buttons(self):
        if self.right_button_function and self.right_button_text:
            Button(name='button_right', parent=self, align=uiconst.TOPRIGHT, top=BUTTON_TOP, left=TEXT_LEFT, label=GetByLabel(self.right_button_text), func=lambda *args: self.right_button_function())
        if self.left_button_function and self.left_button_text:
            Button(name='button_left', parent=self, align=uiconst.TOPRIGHT, top=BUTTON_TOP, left=TEXT_LEFT + BUTTON_WIDTH + PADDING_BETWEEN_BUTTONS, label=GetByLabel(self.left_button_text), func=lambda *args: self.left_button_function())

    def fade_in(self):
        self.audio.SendUIEvent(Sounds.DOCTOR_START)
        animations.FadeIn(self, duration=0.3)
        call_after_wallclocktime_delay(self.doctor_title.Show, delay=0.1)

    def on_right_button_clicked(self):
        self.audio.SendUIEvent(Sounds.DOCTOR_END)
        self.right_button_function()

    def on_left_button_clicked(self):
        self.audio.SendUIEvent(Sounds.DOCTOR_END)
        self.left_button_function()
