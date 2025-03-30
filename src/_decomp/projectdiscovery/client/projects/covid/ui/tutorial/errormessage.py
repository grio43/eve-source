#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\tutorial\errormessage.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import Label
from localization import GetByLabel
BACKGROUND_TEXTURE_PATH = 'res:/UI/Texture/classes/ProjectDiscovery/covid/tutorial/drawing_clear.png'
TEXT_FONTSIZE = 14
TEXT_COLOR = (1.0, 1.0, 1.0, 1.0)
PADDING_TOP = 5
PADDING_BOT = 4
PADDING_H = 21

class ErrorMessage(Container):
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        super(ErrorMessage, self).ApplyAttributes(attributes)
        self._add_label()
        self._add_background()
        self.original_left = self.left

    def _add_label(self):
        self.label = Label(name='text', parent=self, align=uiconst.CENTER, fontsize=TEXT_FONTSIZE, color=TEXT_COLOR)

    def _add_background(self):
        Sprite(name='background', parent=self, align=uiconst.TOALL, texturePath=BACKGROUND_TEXTURE_PATH)

    def rescale(self, left, top):
        self.top = top
        self.original_left = left
        self._correct_size()

    def _correct_size(self):
        self.width = self.label.width + 2 * PADDING_H
        self.height = self.label.height + PADDING_TOP + PADDING_BOT
        self.left = self.original_left - self.width / 2

    def show_errors(self, text_path_list):
        text = ''
        for text_path in text_path_list:
            if text:
                text += '\n'
            text += GetByLabel(text_path)

        self.label.SetText(text)
        self._correct_size()
        self.SetState(uiconst.UI_DISABLED)

    def hide_error(self):
        self.Hide()
