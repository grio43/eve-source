#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\font.py
import enum
from carbonui import fontconst

class FontStyle(str, enum.Enum):
    normal = fontconst.STYLE_DEFAULT
    condensed = fontconst.STYLE_HEADER
    expanded = fontconst.STYLE_SMALLTEXT
