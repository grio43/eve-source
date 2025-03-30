#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\singlelineedits\caret.py
from carbonui import uiconst
from carbonui.primitives.fill import Fill
from eve.client.script.ui import eveThemeColor

class Caret(Fill):
    default_width = 1
    default_color = eveThemeColor.THEME_ACCENT
    default_glowBrightness = 0.3
    default_outputMode = uiconst.OUTPUT_COLOR_AND_GLOW

    def OnColorThemeChanged(self):
        self.rgba = self.default_color
