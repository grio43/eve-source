#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\pointerTool\favorites.py
from carbon.common.script.sys.service import ROLE_GML, ROLE_WORLDMOD
from eve.client.script.ui.shared.pointerTool.link import parse_help_pointer_url, SCHEME_HELP_POINTER
from localization import GetByLabel
from menu import MenuLabel
from utillib import KeyVal
import blue
import carbonui.const as uiconst
ROOT_GROUPID = 0
FAVORITES_SETTING_CONFIG_NAME = 'uiHelpPointerFavorites'

def GetFavoriteKeyVal(**kwargs):
    return KeyVal(groupID=kwargs.get('groupID'), groupName=kwargs.get('groupName', ''), subGroups=kwargs.get('subGroups', []), uiElementNames=kwargs.get('uiElementNames', []) or [], subLevel=kwargs.get('subLevel', 0))


def __GetMaxSubGroupID(parentGroup):
    if parentGroup.subGroups:
        return max((x.groupID for x in parentGroup.subGroups))
    return 0


def __AddSubGroup(parentGroup, newGroup):
    parentGroup.subGroups.append(newGroup)


def __RemoveSubGroup(parentGroup, groupID):
    for eachGroup in parentGroup.subGroups:
        if eachGroup.groupID == groupID:
            if eve.Message('AskDeleteFavoritePointerGroup', {'groupName': eachGroup.groupName}, uiconst.YESNO) == uiconst.ID_YES:
                parentGroup.subGroups.remove(eachGroup)
                return True

    return False


def __AddUIElementsWithIdx(parentGroup, uiElements, idx = -1):
    if len(uiElements) == 1 and uiElements[0] in parentGroup.uiElementNames and idx > -1:
        uiElement = uiElements[0]
        currentIdx = parentGroup.uiElementNames.index(uiElement)
        if idx == currentIdx:
            return
        newIdx = idx if currentIdx > idx else idx - 1
        parentGroup.uiElementNames.remove(uiElement)
        parentGroup.uiElementNames.insert(newIdx, uiElement)
        return
    uiElementsToAdd = [ x for x in uiElements if x not in parentGroup.uiElementNames ]
    if not uiElementsToAdd:
        return
    if idx == -1 or idx is None:
        parentGroup.uiElementNames.extend(uiElementsToAdd)
    elif len(uiElements) == 1:
        parentGroup.uiElementNames.insert(idx, uiElementsToAdd[0])
    else:
        newList = parentGroup.uiElementNames[:idx] + uiElements + parentGroup.uiElementNames[idx:]
        parentGroup.uiElementNames = newList


def __RemoveUiElements(parentGroup, uiElements):
    wasRemoved = False
    for element in uiElements:
        if element in parentGroup.uiElementNames:
            parentGroup.uiElementNames.remove(element)
            wasRemoved = True

    return wasRemoved


def AddFavoriteGroup(*args):
    folderNameLabel = GetByLabel('UI/Market/Marketbase/FolderName')
    typeFolderNameLabel = GetByLabel('UI/Market/Marketbase/TypeFolderName')
    from eve.client.script.ui.util.utilWindows import NamePopup
    newName = NamePopup(folderNameLabel, typeFolderNameLabel, maxLength=30)
    if newName is None:
        return
    rootGroup = GetFavoriteRootGroup()
    maxGroupID = __GetMaxSubGroupID(rootGroup)
    newGroup = GetFavoriteKeyVal(groupID=maxGroupID + 1, groupName=newName, subLevel=1)
    __AddSubGroup(rootGroup, newGroup)
    TrySaveGroup(rootGroup)
    sm.ScatterEvent('OnFavoriteGroupChanged')


def RemoveSubGroup(groupID):
    rootGroup = GetFavoriteRootGroup()
    wasRemoved = __RemoveSubGroup(rootGroup, groupID)
    if wasRemoved:
        TrySaveGroup(rootGroup)
        sm.ScatterEvent('OnFavoriteGroupChanged')


def OnDropDataInFavorite(idFromNode, nodes):
    groupID = idFromNode[1]
    AddElementsToGroup(groupID, nodes)


def AddElementsToGroup(groupID, nodes, idx = -1):
    groupToAddTo = FindGroupWithGroupID(groupID)
    uiElementsToAdd = FindUIElementsFromNodes(nodes)
    if uiElementsToAdd and groupToAddTo:
        __AddUIElementsWithIdx(groupToAddTo, uiElementsToAdd, idx=idx)
        TrySaveGroup(groupToAddTo)
        sm.ScatterEvent('OnFavoriteGroupChanged')


def FindUIElementsFromNodes(nodes):
    pointerObjects = FindPointerObjectsForNodes(nodes)
    if not pointerObjects:
        return []
    uiElementNames = [ getattr(x, 'uiElementName', None) for x in pointerObjects ]
    uiElementNames = filter(None, uiElementNames)
    return uiElementNames


def RemoveElementFromGroup(groupID, nodes):
    groupToRemoveFrom = FindGroupWithGroupID(groupID)
    uiElementsToRemove = FindUIElementsFromNodes(nodes)
    if uiElementsToRemove and groupToRemoveFrom:
        wasRemoved = __RemoveUiElements(groupToRemoveFrom, uiElementsToRemove)
        if wasRemoved:
            TrySaveGroup(groupToRemoveFrom)
            sm.ScatterEvent('OnFavoriteGroupChanged')


def FindPointerObjectsForNodes(nodes):
    allPointers = sm.GetService('helpPointer').GetAllPointersByElementName()
    pointerObjects = []
    for x in nodes:
        po = getattr(x, 'pointerObjects', [])
        if po:
            pointerObjects += po
        guid = getattr(x, '__guid__', None)
        if guid == 'TextLink' and x.url.startswith(SCHEME_HELP_POINTER):
            uiElementName = parse_help_pointer_url(x.url)
            if uiElementName and uiElementName in allPointers:
                pointerObjects.append(allPointers[uiElementName])

    return pointerObjects


def FindGroupWithGroupID(groupID):
    rootGroup = GetFavoriteRootGroup()
    if groupID == ROOT_GROUPID:
        return rootGroup
    for each in rootGroup.subGroups:
        if each.groupID == groupID:
            return each


def TrySaveGroup(groupKeyVal):
    if groupKeyVal.groupID != ROOT_GROUPID:
        return
    settings.user.ui.Set(FAVORITES_SETTING_CONFIG_NAME, groupKeyVal)


def GetFavoriteGroups():
    rootGroup = GetFavoriteRootGroup()
    return rootGroup.subGroups


def GetFavoriteGroupMenu(node):
    m = []
    m += [(MenuLabel('UI/HelpPointers/Wnd/AddGroup'), AddFavoriteGroup, (ROOT_GROUPID,))]
    return m


def GetFavoriteSubGroupMenu(groupData):
    groupID = groupData['groupID']
    m = [(MenuLabel('UI/HelpPointers/Wnd/DeleteGroup'), RemoveSubGroup, (groupID,))]
    return m


def GetFavoriteRootGroup():
    rootGroup = settings.user.ui.Get(FAVORITES_SETTING_CONFIG_NAME, None)
    if rootGroup is None:
        return GetFavoriteKeyVal(groupID=0)
    return GetFavoriteKeyVal(**rootGroup.__dict__)


def AddToFavoriteGroup(groupID, node):
    AddElementsToGroup(groupID, [node])


def GetNormalPointerEntryMenu(entry):
    menu = []
    node = entry.sr.node
    if session.role & (ROLE_GML | ROLE_WORLDMOD):
        menu += [('GM: Unique UI Name: ' + node.uiElementName, blue.pyos.SetClipboardData, (node.uiElementName,))]
    menu += [(MenuLabel('UI/HelpPointers/Wnd/AddToFavoriteRoot'), AddToFavoriteGroup, (0, node))]
    if GetFavoriteGroups():
        menu += [(MenuLabel('UI/HelpPointers/Wnd/AddToFavoriteSubGroup'), ('isDynamic', ShowFavoriteGroups, (node,)))]
    return menu


def ShowFavoriteGroups(node):
    m = []
    for eachGroup in GetFavoriteGroups():
        m += [(eachGroup.groupName, AddToFavoriteGroup, (eachGroup.groupID, node))]

    return m


def GetFavoritePointerEntryMenu(entry):
    node = entry.sr.node
    parentGroupID = node.parentGroup.groupID
    m = []
    m += [(MenuLabel('UI/HelpPointers/Wnd/RemoveFromGroup'), RemoveElementFromGroup, (parentGroupID, [node]))]
    return m
