#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\counterBox.py
from carbonui import fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from eve.client.script.ui.control.eveLabel import Label
import carbonui.const as uiconst

class CounterBox(Container):
    _number = 0

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.label = Label(parent=self, align=uiconst.CENTER, fontPath='res:/UI/Fonts/EveSansNeue-Expanded.otf', fontsize=fontconst.EVE_SMALL_FONTSIZE)
        Frame(bgParent=self, texturePath='res:/UI/Texture/Shared/counterFrame.png', cornerSize=8, offset=-1, color=(0.2, 0.2, 0.2, 1))
        if 'text' in attributes:
            self.text = attributes.text
        else:
            self.display = False

    @apply
    def text():

        def fget(self):
            return self._number

        def fset(self, value):
            self._number = value
            self.label.text = value
            self.width = max(14, self.label.textwidth + 8)
            self.height = max(14, self.label.textheight)
            if self.label.text:
                self.display = True
            else:
                self.display = False

        return property(**locals())
