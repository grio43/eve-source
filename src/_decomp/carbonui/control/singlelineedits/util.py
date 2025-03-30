#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\singlelineedits\util.py
from eve.client.script.ui.control.allUserEntries import AllUserEntries
from eve.common.lib import appConst
from eve.common.script.sys.idCheckers import IsCharacter, IsCorporation, IsAlliance
from eve.client.script.ui.util.linkUtil import GetItemIDFromTextLink, GetCharIDFromTextLink
from utillib import KeyVal

def GetDroppedCharCorpOrAllianceName(node):
    validTypeIDs = appConst.characterTypes + [appConst.typeCorporation, appConst.typeAlliance]
    return GetDroppedOwnerNameForValidTypeIDs(node, validTypeIDs)


def GetDroppedCorpOrAllianceName(node):
    validTypeIDs = [appConst.typeCorporation, appConst.typeAlliance]
    return GetDroppedOwnerNameForValidTypeIDs(node, validTypeIDs)


def GetDroppedOwnerNameForValidTypeIDs(node, validTypeIDs):
    if not IsUserNode(node):
        return
    itemID = GetItemIDFromTextLink(node, validTypeIDs)
    if itemID is None:
        itemID = node.itemID
    if IsCharacter(itemID) or IsCorporation(itemID) or IsAlliance(itemID):
        itemName = cfg.eveowners.Get(itemID).name
        return KeyVal(itemName=itemName, itemID=itemID)


def GetDroppedCharInfo(node):
    if not IsUserNode(node):
        return
    charID = GetCharIDFromTextLink(node)
    if charID is None:
        charID = node.charID
    if IsCharacter(charID):
        charName = cfg.eveowners.Get(charID).name
        return KeyVal(charName=charName, charID=charID)


def IsUserNode(node):
    isUserNode = getattr(node, '__guid__', None) in AllUserEntries() + ['TextLink']
    return isUserNode
