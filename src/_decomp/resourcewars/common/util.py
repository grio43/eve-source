#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\resourcewars\common\util.py
from resourcewars.common.const import RW_HAULER_WRECK_TYPES, RW_CORPORATIONS

def is_rw_hauler_wreck(wreckTypeID, ownerID):
    return wreckTypeID in RW_HAULER_WRECK_TYPES and ownerID in RW_CORPORATIONS
