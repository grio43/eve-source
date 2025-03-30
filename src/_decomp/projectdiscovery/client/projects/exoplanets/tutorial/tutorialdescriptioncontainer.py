#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\tutorial\tutorialdescriptioncontainer.py
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from carbonui.uianimations import animations
from carbonui.control.button import Button
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import EveLabelLarge, Label
from trinity import TR2_SBM_BLEND
TITLE_OPACITY = 1.0
TEXT_OPACITY = 1.0
TITLE_COLOR = (191 / 255.0,
 214 / 255.0,
 239 / 255.0,
 1.0)
TITLE_LINE_HEIGHT = 1
TITLE_LINE_OPACITY = 0.3
TITLE_LINE_VERTICAL_PADDING = 4
TITLE_LINE_COLOR = (128 / 255.0,
 177 / 255.0,
 222 / 255.0,
 1.0)

class TutorialDescriptionContainer(Container):
    default_align = uiconst.TOLEFT

    def ApplyAttributes(self, attributes):
        super(TutorialDescriptionContainer, self).ApplyAttributes(attributes)
        self._button_func = attributes.get('buttonFunc')
        self._button_text = attributes.get('buttonText')
        self._title = attributes.get('title')
        self._description = attributes.get('description')
        self.setup_layout()
        animations.BlinkIn(self)

    def setup_layout(self):
        self._button_container = Container(name='ButtonContainer', parent=self, align=uiconst.TOBOTTOM, height=18)
        self._button = Button(name='Button', align=uiconst.CENTER, parent=self._button_container, label=self._button_text, func=self._button_func)
        self._title_container = Container(parent=self, align=uiconst.TOTOP, name='pointerTitleContainer', height=18)
        self._title_label = EveLabelLarge(text=self._title, parent=self._title_container, align=uiconst.CENTER, state=uiconst.UI_DISABLED, idx=0, opacity=TITLE_OPACITY, blendMode=TR2_SBM_BLEND, color=TITLE_COLOR)
        self._title_line = Line(name='pointerTitleLine', parent=self, align=uiconst.TOTOP, weight=TITLE_LINE_HEIGHT, opacity=TITLE_LINE_OPACITY, padTop=TITLE_LINE_VERTICAL_PADDING, padBottom=TITLE_LINE_VERTICAL_PADDING, color=TITLE_LINE_COLOR)
        self._scroll_container = ScrollContainer(name='ScrollContainer', parent=self, align=uiconst.TOALL)
        self._description_label = Label(name='Description', parent=self._scroll_container, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, idx=0, opacity=TITLE_OPACITY, blendMode=TR2_SBM_BLEND, color=TITLE_COLOR, text=self._description)
