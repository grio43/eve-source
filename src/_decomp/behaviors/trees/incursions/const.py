#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\incursions\const.py
from eve.common.lib.appConst import factionDrifters
from inventorycommon.const import ownerUnknown, categoryShip, categoryDrone, categoryEntity, ownerAmarrNavy, groupStargate, groupStation, categoryFighter
DRIFTER_OWNERS = {factionDrifters, ownerUnknown}
AMARR_NAVY_OWNERS = {ownerAmarrNavy}
VALID_HOSTILE_CATEGORIES = [categoryShip,
 categoryDrone,
 categoryEntity,
 categoryFighter]
ROAMING_SITE_GROUP_IDS = [groupStargate, groupStation]
