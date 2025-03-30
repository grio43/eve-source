#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcosmetics\common\const.py
from itertoolsext.Enum import Enum

@Enum

class CosmeticsType(object):
    NONE = 0
    CORPORATION_LOGO = 1
    ALLIANCE_LOGO = 2
    SKIN = 3


def GetSupportedCosmeticsTypes():
    return [CosmeticsType.ALLIANCE_LOGO, CosmeticsType.CORPORATION_LOGO]


REMOVE_EMBLEMS_LP_COST_FLAG = 'remove-emblems-lp-cost'
REMOVE_EMBLEMS_LP_COST_FLAG_DEFAULT = False
ENABLE_LP_HERALDRY_PURCHASES_FLAG = 'lp-store-heraldry-purchases'
ENABLE_LP_HERALDRY_PURCHASES_FLAG_DEFAULT = True
DISABLE_ALL_SHIP_EMBLEMS_FLAG = 'disable-all-ship-emblems'
DISABLE_ALL_SHIP_EMBLEMS_FLAG_DEFAULT = False
