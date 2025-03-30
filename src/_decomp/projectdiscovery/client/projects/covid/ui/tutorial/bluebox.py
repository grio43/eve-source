#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\tutorial\bluebox.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame

class BlueBox(Container):
    FRAME_COLOR = (0.06, 0.69, 0.94, 1.0)
    BACKGROUND_COLOR = (0.2, 0.74, 0.95, 0.2)
    default_cursor = uiconst.UICORSOR_FINGER

    def ApplyAttributes(self, attributes):
        super(BlueBox, self).ApplyAttributes(attributes)
        self._add_frame()
        self._add_background()

    def _add_frame(self):
        Frame(name='blue_box_frame', parent=self, align=uiconst.TOALL, color=self.FRAME_COLOR, frameConst=uiconst.FRAME_BORDER1_CORNER0)

    def _add_background(self):
        Fill(name='blue_box_background', parent=self, align=uiconst.TOALL, color=self.BACKGROUND_COLOR)
