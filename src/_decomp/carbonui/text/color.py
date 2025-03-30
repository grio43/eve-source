#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\text\color.py
from chroma import Color
from eve.client.script.ui import eveColor

class TextColor(object):
    NORMAL = Color(1.0, 1.0, 1.0, 0.75)
    HIGHLIGHT = Color(1.0, 1.0, 1.0, 0.9)
    SECONDARY = Color(1.0, 1.0, 1.0, 0.5)
    DISABLED = Color(1.0, 1.0, 1.0, 0.3)
    WARNING = Color.from_rgba(*eveColor.WARNING_ORANGE)
    DANGER = Color.from_rgba(*eveColor.DANGER_RED)
    SUCCESS = Color.from_rgba(*eveColor.SUCCESS_GREEN)
    AURA = Color.from_rgba(*eveColor.AURA_PURPLE)
