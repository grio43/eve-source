#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\assetholding\common\const.py
from itertoolsext.Enum import Enum
ASSET_INFINITE_CAPACITY = -1

@Enum

class UnitType(object):
    ISK = ('ISK_UNIT_TYPE',)
    LOYALTY_POINT = ('LOYALTY_POINT_UNIT_TYPE',)
    SKILL_POINT = 'SKILL_POINT_UNIT_TYPE'
