#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\deathzone\__init__.py
import evetypes
from deathzone.const import DEATHZONE_DAMAGE_ELIGIBILITY_TYPELIST

def DeathzoneAppliesToType(typeID):
    return typeID in evetypes.GetTypeIDsByListID(DEATHZONE_DAMAGE_ELIGIBILITY_TYPELIST)
