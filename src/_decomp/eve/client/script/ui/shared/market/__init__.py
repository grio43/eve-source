#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\__init__.py
from eve.client.script.ui.util.linkUtil import GetTypeIDFromTextLink

def GetTypeIDFromDragItem(node):
    try:
        typeID = node.typeID
        if typeID:
            return typeID
    except AttributeError:
        pass

    nodeGuid = getattr(node, '__guid__', None)
    if nodeGuid in INVENTORY_GUIDS:
        return node.item.typeID
    typeID = GetTypeIDFromTextLink(node)
    return typeID


INVENTORY_GUIDS = ('xtriui.InvItem', 'listentry.InvItem')
