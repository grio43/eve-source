#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\attributes\utils.py
from dogma.attributes.format import GetAttribute, GetDisplayName

def GetDisplayNamesForAttributeList(attributeList):
    attributeNames = []
    for attribute in attributeList:
        name = GetDisplayName(attribute)
        attributeNames.append(name)

    return attributeNames


def GetModifyingItemIDs(dogmaItem, attributeID):
    try:
        attrib = dogmaItem.attributes[attributeID]
    except KeyError:
        return []

    ret = []
    for operator, modifyingAttrib in attrib.GetIncomingModifiers():
        if modifyingAttrib.item is not None:
            ret.append(modifyingAttrib.item.itemID)

    return ret
