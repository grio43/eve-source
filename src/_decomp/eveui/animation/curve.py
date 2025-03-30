#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\animation\curve.py
from carbonui import uiconst
import enum

class CurveType(enum.IntEnum):
    linear = uiconst.ANIM_LINEAR
    smooth = uiconst.ANIM_SMOOTH
    overshot = uiconst.ANIM_OVERSHOT
    overshot2 = uiconst.ANIM_OVERSHOT2
    overshot3 = uiconst.ANIM_OVERSHOT3
    overshot4 = uiconst.ANIM_OVERSHOT4
    overshot5 = uiconst.ANIM_OVERSHOT5
    wave = uiconst.ANIM_WAVE
    random = uiconst.ANIM_RANDOM
    bounce = uiconst.ANIM_BOUNCE
    repeat = uiconst.ANIM_REPEAT
