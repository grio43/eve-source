#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\ui\link_with_ship\__init__.py
from inventorycommon.const import typeSkyhookReagentSilo

def GetLinkButtonLabelPath(typeID):
    if typeID == typeSkyhookReagentSilo:
        return 'UI/Inflight/SpaceComponents/LinkWithShip/BeginLinkSkyhook'
    return 'UI/Inflight/SpaceComponents/LinkWithShip/BeginLink'
