#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\shipTree\shipTreeUtil.py
import evetypes
from eve.common.lib import appConst as const

def GetTagIconForType(typeID):
    techLevel = evetypes.GetTechLevel(typeID)
    if techLevel == 2:
        return 'res:/UI/Texture/classes/ShipTree/tech/tech2.png'
    if techLevel == 3:
        return 'res:/UI/Texture/classes/ShipTree/tech/tech3.png'
    metaGroupID = evetypes.GetMetaGroupID(typeID)
    if metaGroupID == const.metaGroupFaction:
        return 'res:/UI/Texture/classes/ShipTree/tech/navy.png'
