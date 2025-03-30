#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\tutorial\pointer.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import Label
from localization import GetByLabel
from math import pi
TRIANGLE_TEXTURE_PATH = 'res:/UI/Texture/classes/ProjectDiscovery/covid/tutorial/triangle.png'
TRIANGLE_GLOW_TEXTURE_PATH = 'res:/UI/Texture/classes/ProjectDiscovery/covid/tutorial/triangle_glow.png'
TRIANGLE_WIDTH = 8
TRIANGLE_HEIGHT = 7
TRIANGLE_TOP = 2
TRIANGLE_GLOW_WIDTH = 14
TRIANGLE_GLOW_HEIGHT = 13
TRIANGLE_GLOW_OPACITY = 0.6
TEXT_FONTSIZE = 18
TEXT_COLOR = (1.0, 1.0, 1.0, 1.0)
PADDING_TRIANGLE_TO_TEXT = 5

class Pointer(Container):
    default_state = uiconst.UI_DISABLED
    default_should_point_up = True

    def ApplyAttributes(self, attributes):
        super(Pointer, self).ApplyAttributes(attributes)
        self.text = attributes.get('text')
        self.should_point_up = attributes.get('should_point_up', self.default_should_point_up)
        self.add_triangle()
        self.add_text()
        self.correct_size()

    def add_triangle(self):
        triangle_container = Container(name='triangle_container', parent=self, align=uiconst.TOTOP if self.should_point_up else uiconst.TOBOTTOM, height=TRIANGLE_GLOW_HEIGHT)
        Sprite(name='triangle', parent=triangle_container, align=uiconst.CENTER, width=TRIANGLE_WIDTH, height=TRIANGLE_HEIGHT, top=TRIANGLE_TOP, texturePath=TRIANGLE_TEXTURE_PATH, rotation=0 if self.should_point_up else pi)
        Sprite(name='triangle_glow', parent=triangle_container, align=uiconst.CENTER, width=TRIANGLE_GLOW_WIDTH, height=TRIANGLE_GLOW_HEIGHT, texturePath=TRIANGLE_GLOW_TEXTURE_PATH, opacity=TRIANGLE_GLOW_OPACITY, rotation=0 if self.should_point_up else pi)

    def add_text(self):
        self.label = Label(name='text', parent=self, align=uiconst.TOTOP if self.should_point_up else uiconst.TOBOTTOM, fontsize=TEXT_FONTSIZE, bold=True, text=GetByLabel(self.text).upper(), top=PADDING_TRIANGLE_TO_TEXT, color=TEXT_COLOR)

    def correct_size(self):
        _, text_width = self.label.GetWidthToIndex(-1)
        text_height = self.label.height
        self.width = text_width
        self.height = TRIANGLE_GLOW_HEIGHT + PADDING_TRIANGLE_TO_TEXT + text_height
