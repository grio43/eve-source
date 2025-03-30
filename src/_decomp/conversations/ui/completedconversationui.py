#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\conversations\ui\completedconversationui.py
import carbonui.const as uiconst
from carbonui.fontconst import DEFAULT_FONTSIZE
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.util.uix import GetTextWidth
from localization import GetByLabel
from trinity import TR2_SBM_ADD
from carbonui.uicore import uicore
COMPLETED_LABEL = 'UI/Conversations/UI/CompletedConversation'
COMPLETED_LABEL_PADDING = 2
COMPLETED_LABEL_COLOR = (0.42, 0.77, 0.25, 1.5)
COMPLETED_NEXT_BUTTON_LABEL = 'UI/Conversations/UI/NextConversationLine'
COMPLETED_NEXT_BUTTON_LABEL_PADDING = 10
COMPLETED_NEXT_BUTTON_LABEL_COLOR = (1.0, 1.0, 1.0, 1.0)
COMPLETED_NEXT_BUTTON_COLOR = (0.29, 0.5, 0.18, 1.2)
COMPLETED_NEXT_BUTTON_RIGHT_PADDING = 7
COMPLETED_UI_BACKGROUND_FILL_COLOR = (0.42, 0.77, 0.25, 0.0)
COMPLETED_UI_BACKGROUND_FILL_START_OPACITY = 0.5
COMPLETED_UI_BACKGROUND_FILL_END_OPACITY = 0.15
COMPLETED_UI_BACKGROUND_FILL_START_DISPLAY_WIDTH = 0.0
COMPLETED_UI_BACKGROUND_FILL_DURATION = 1.0
COMPLETED_UI_BACKGROUND_FILL_OPACITY_CHANGE_DURATION_SECS = 1.75
COMPLETED_UI_BACKGROUND_FILL_OPACITY_CHANGE_OFFSET_SECS = 0.5
COMPLETED_CHECKBOX_SIZE = 14
COMPLETED_CHECKBOX_PADDING = 2
COMPLETED_CHECKBOX_TEXTURE = 'res:/UI/Texture/Classes/InfoPanels/opportunitiesCheck.png'
COMPLETED_CHECKBOX_COLOR = (0.42, 0.77, 0.25, 1.0)
COMPLETED_CHECKBOX_GLOW_EXPAND_START = 5.0
COMPLETED_CHECKBOX_GLOW_EXPAND_END = 0.0
COMPLETED_CHECKBOX_GLOW_EXPAND_DURATION = 2.0
COMPLETED_CHECKBOX_GLOW_COLOR_START = (0.5, 0.5, 0.5, 0.5)
COMPLETED_CHECKBOX_GLOW_COLOR_END = (0.0, 0.0, 0.0, 0.0)
COMPLETED_CHECKBOX_GLOW_COLOR_DURATION = 2.0
COMPLETED_CHECKBOX_OPACITY = 1.0
CONTENT_PADDING = 4

class CompletedConversationUi(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        next_function = attributes.Get('nextFunction', None)
        self.load_text()
        self.add_background()
        self.add_content()
        self.activate_next_button(next_function=next_function)

    def load_text(self):
        self.completed_label_text = GetByLabel(COMPLETED_LABEL)
        self.completed_label_text_width = GetTextWidth(strng=self.completed_label_text, fontsize=DEFAULT_FONTSIZE) + 2 * COMPLETED_LABEL_PADDING
        self.next_button_label_text = GetByLabel(COMPLETED_NEXT_BUTTON_LABEL)
        self.next_button_label_text_width = GetTextWidth(strng=self.next_button_label_text, fontsize=DEFAULT_FONTSIZE) + 2 * COMPLETED_NEXT_BUTTON_LABEL_PADDING

    def add_content(self):
        self.content_container = Container(name='completed_ui_content_container', align=uiconst.TOLEFT, parent=self, width=self.width, height=self.height, padding=CONTENT_PADDING)
        self.add_completed_tag()
        self.add_next_button()

    def add_background(self):
        completed_fill = Fill(bgParent=self, color=COMPLETED_UI_BACKGROUND_FILL_COLOR)
        completed_fill.displayWidth = COMPLETED_UI_BACKGROUND_FILL_START_DISPLAY_WIDTH
        completed_fill.opacity = COMPLETED_UI_BACKGROUND_FILL_START_OPACITY
        uicore.animations.MorphScalar(completed_fill, 'displayWidth', completed_fill.displayWidth, self.width, duration=COMPLETED_UI_BACKGROUND_FILL_DURATION)
        uicore.animations.FadeTo(completed_fill, startVal=COMPLETED_UI_BACKGROUND_FILL_START_OPACITY, endVal=COMPLETED_UI_BACKGROUND_FILL_END_OPACITY, duration=COMPLETED_UI_BACKGROUND_FILL_OPACITY_CHANGE_DURATION_SECS, timeOffset=COMPLETED_UI_BACKGROUND_FILL_OPACITY_CHANGE_OFFSET_SECS)

    def add_completed_tag(self):
        completed_tag_container = Container(name='completed_tag_container', align=uiconst.TOLEFT, parent=self.content_container, width=COMPLETED_CHECKBOX_SIZE + 2 * COMPLETED_CHECKBOX_PADDING + self.completed_label_text_width, height=self.content_container.height)
        self.add_completed_checkbox(completed_tag_container)
        self.add_completed_label(completed_tag_container)

    def add_completed_checkbox(self, parent):
        completed_checkbox_container = Container(name='completed_checkbox_container', align=uiconst.TOLEFT, parent=parent, width=COMPLETED_CHECKBOX_SIZE, height=parent.height, padRight=COMPLETED_CHECKBOX_PADDING, padLeft=COMPLETED_CHECKBOX_PADDING)
        completed_checkbox = Sprite(name='completed_checkbox', parent=completed_checkbox_container, align=uiconst.CENTER, width=COMPLETED_CHECKBOX_SIZE, height=COMPLETED_CHECKBOX_SIZE, texturePath=COMPLETED_CHECKBOX_TEXTURE, color=COMPLETED_CHECKBOX_COLOR, blendMode=TR2_SBM_ADD)
        uicore.animations.MorphScalar(completed_checkbox, 'glowExpand', startVal=COMPLETED_CHECKBOX_GLOW_EXPAND_START, endVal=COMPLETED_CHECKBOX_GLOW_EXPAND_END, duration=COMPLETED_CHECKBOX_GLOW_EXPAND_DURATION)
        uicore.animations.SpColorMorphTo(completed_checkbox, startColor=COMPLETED_CHECKBOX_GLOW_COLOR_START, endColor=COMPLETED_CHECKBOX_GLOW_COLOR_END, attrName='glowColor', duration=COMPLETED_CHECKBOX_GLOW_COLOR_DURATION)
        uicore.animations.FadeTo(completed_checkbox, startVal=completed_checkbox.opacity, endVal=COMPLETED_CHECKBOX_OPACITY)

    def add_completed_label(self, parent):
        completed_label_container = Container(name='completed_label_container', align=uiconst.TOLEFT, parent=parent, width=self.completed_label_text_width, height=parent.height)
        EveLabelMedium(name='completed_label', parent=completed_label_container, text=self.completed_label_text, align=uiconst.CENTER, color=COMPLETED_LABEL_COLOR, blendMode=TR2_SBM_ADD)

    def add_next_button(self):
        completed_next_button_container = Container(name='completed_next_button_container', align=uiconst.TORIGHT, parent=self.content_container, width=self.next_button_label_text_width, height=self.content_container.height, padRight=COMPLETED_NEXT_BUTTON_RIGHT_PADDING)
        self.completed_next_button = Button(name='completed_next_button', align=uiconst.NOALIGN, parent=completed_next_button_container, label=self.next_button_label_text, color=COMPLETED_NEXT_BUTTON_COLOR)
        self.completed_next_button.SetColor(COMPLETED_NEXT_BUTTON_COLOR)
        self.completed_next_button.SetLabelColor(COMPLETED_NEXT_BUTTON_LABEL_COLOR)
        self.completed_next_button.SetActiveFrameColor(COMPLETED_NEXT_BUTTON_LABEL_COLOR)

    def activate_next_button(self, next_function):
        self.completed_next_button.OnClick = next_function

    def deactivate_next_button(self):
        self.completed_next_button.state = uiconst.UI_DISABLED
        self.completed_next_button.OnClick = None
