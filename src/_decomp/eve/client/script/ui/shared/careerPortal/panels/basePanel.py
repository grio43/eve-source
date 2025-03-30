#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\panels\basePanel.py
from carbonui import uiconst
from carbonui.control.section import SectionAutoSize
from carbonui.primitives.line import Line

class BasePanel(SectionAutoSize):
    default_name = 'BasePanel'
    default_mirrored = True
    default_inside_padding = (24, 24, 24, 24)
    default_opacity = 0
    default_align = uiconst.TOTOP
    default_alignMode = uiconst.TOTOP
    default_state = uiconst.UI_DISABLED

    def _ConstructHeader(self):
        Line(parent=self, align=uiconst.TOTOP, color=self.color, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW)

    def SetText(self, text):
        pass
