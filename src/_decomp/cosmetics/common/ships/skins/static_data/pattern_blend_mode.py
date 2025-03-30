#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\static_data\pattern_blend_mode.py
from itertoolsext.Enum import Enum

@Enum

class PatternBlendMode:
    UNSPECIFIED = 0
    OVERLAY = 1
    SUBTRACT = 2
    EXCLUSION = 3
    NESTED = 4
    NESTED_INVERTED = 5


NO_SECONDARY_COLOR_BLEND_MODES = (PatternBlendMode.SUBTRACT, PatternBlendMode.EXCLUSION)
