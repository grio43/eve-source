#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureSettings\__init__.py
import structures
import ownergroups.client

def AreGroupNodes(dragData):
    if not dragData:
        return False
    firstNode = dragData[0]
    if getattr(firstNode, 'nodeType', None) == 'AccessGroupEntry':
        return True
    if getattr(firstNode, '__guid__', None) != 'TextLink':
        return False
    url = getattr(firstNode, 'url', '')
    try:
        ownergroups.client.parse_access_group_url(url)
        return True
    except Exception:
        pass

    return False


def GetGroupIDFromNode(node):
    if not AreGroupNodes([node]):
        return
    if getattr(node, 'nodeType', None) == 'AccessGroupEntry':
        return node.groupID
    if getattr(node, '__guid__', None) == 'TextLink':
        return ownergroups.client.parse_access_group_url(node.url)


def CanHaveGroups(settingID):
    return settingID in structures.SETTINGS_VALUE_HAS_GROUPS
