#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\contextMenu\menuDataFactory.py
import types
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.contextMenu.menuEntryData import MenuEntryData, BaseMenuEntryData
from eve.client.script.ui import menuUtil
from menu import MenuLabel, NO_ARGUMENTS
DISABLED_ENTRY = [-1]
DISABLED_ENTRY2 = [[-1]]

def CreateMenuDataFromRawTuples(rawTupleDataList):
    if isinstance(rawTupleDataList, MenuData):
        return rawTupleDataList
    rawTupleDataList = _chomplist(rawTupleDataList)
    if not rawTupleDataList:
        return
    menuEntryDataList = []
    for data in rawTupleDataList:
        if data is None:
            menuEntryDataList.append(None)
        elif isinstance(data, BaseMenuEntryData):
            menuEntryDataList.append(data)
        else:
            menuEntryData = _GetEntryTupleFromRawTuple(data)
            menuEntryDataList.append(menuEntryData)

    return CreateMenuDataWithEntries(menuEntryDataList)


def CreateMenuDataWithEntries(menuEntryDataList, iconSize = 16):
    menuData = MenuData(iconSize=iconSize)
    menuEntryDataList = _SortMenuEntries(menuEntryDataList)
    lastMenuEntryData = None
    for menuEntryData in menuEntryDataList:
        if menuEntryData is None:
            menuData.AddSeparator()
            continue
        if lastMenuEntryData and menuEntryData.GetPrimaryMenuGroupID() != lastMenuEntryData.GetPrimaryMenuGroupID():
            menuData.AddSeparator()
        lastMenuEntryData = menuEntryData
        menuData.AppendMenuEntryData(menuEntryData)

    return menuData


def _GetEntryTupleFromRawTuple(each):
    menuGroupID = None
    quantity = None
    menuLabel, value = each[:2]
    if isinstance(menuLabel, MenuLabel):
        text = menuLabel
    else:
        if isinstance(menuLabel, basestring):
            menuGroupID = menuUtil.GetMenuGroup(menuLabel.lower())
        text = menuLabel
    if len(each) > 2 and each[2] != NO_ARGUMENTS:
        args = each[2]
        if args not in (DISABLED_ENTRY, DISABLED_ENTRY2):
            value = lambda f = value, args = args: f(*args)
        else:
            value = None
        if len(args) == 2 and type(args[1]) == list and len(args[1]) > 1:
            quantity = _GetEntryQuantity(args)
    icon = None
    if len(each) > 3:
        icon = each[3]
        if icon is not None:
            if isinstance(icon, types.TupleType):
                icon, _ = icon
    menuClass = None
    if len(each) > 4:
        menuClass = each[4]
    internalName = ''
    if len(each) > 5:
        internalName = each[5]
    typeID = None
    if len(each) > 6:
        typeID = each[6]
    func = None
    subMenuData = None
    if callable(value):
        func = value
    elif isinstance(value, (list, tuple)) and value:
        if value[0] == 'isDynamic':
            _func = value[1]
            args = value[2]
            subMenuData = lambda : _func(*args)
        else:
            subMenuData = value
    elif isinstance(value, basestring) and isinstance(text, basestring):
        text += ' ( %s )' % value
    return MenuEntryData(text=text, func=func, subMenuData=subMenuData, texturePath=icon, menuGroupID=menuGroupID, menuEntryViewClass=menuClass, internalName=internalName, typeID=typeID, quantity=quantity)


def _GetEntryQuantity(args):
    t = 0
    for eacharg in args[1]:
        t1 = None
        if hasattr(eacharg, 'stacksize'):
            t1 = eacharg.stacksize
        if t1 is None and hasattr(eacharg, 'quantity'):
            t1 = eacharg.quantity
        if t1 is not None:
            t += t1
        else:
            t += 1

    return t


def _SortMenuEntries(entryList, *args):
    entryList.sort(cmp=_CompareGroups)
    return entryList


def _CompareGroups(x, y):
    groupX = x.menuGroupID if x else None
    groupY = y.menuGroupID if y else None
    if groupX in menuUtil.menuHierarchy:
        priorityX = menuUtil.menuHierarchy.index(groupX)
    else:
        priorityX = -1
    if groupY in menuUtil.menuHierarchy:
        priorityY = menuUtil.menuHierarchy.index(groupY)
    else:
        priorityY = -1
    if priorityX < priorityY:
        return -1
    elif priorityX == priorityY:
        return 0
    else:
        return 1


def _chomplist(lst):
    if not lst:
        return
    startIdx = 0
    lstLen = len(lst)
    stopIdx = lstLen
    while startIdx < stopIdx:
        if lst[startIdx] is None:
            startIdx += 1
        elif lst[stopIdx - 1] is None:
            stopIdx -= 1
        else:
            break

    if stopIdx <= startIdx:
        return
    if startIdx == 0 and stopIdx == lstLen:
        return lst
    return lst[startIdx:stopIdx]
