#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\menuMerge.py
import log
import uthread
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from eve.client.script.ui.services.menuSvcExtras import invItemFunctions
from menu import MenuList, MenuLabel, NO_ARGUMENTS, CaptionIsInMultiFunctions

def MergeMenus(menus):
    if not menus:
        return MenuList()
    allLabels, allReasons = _GetAllLabelsAndReasons(menus)
    menus = filter(None, [ filter(None, each) for each in menus ])
    ret = MenuList()
    ret.reasonsWhyNotAvailable = allReasons
    for menuLabel in allLabels:
        if menuLabel is None:
            ret.append(None)
        else:
            menuEntry = _GetMergedMenuEntry(menuLabel, menus)
            if menuEntry:
                ret.append(menuEntry)

    return ret


def _GetMergedMenuEntry(menuLabel, menus):
    if isinstance(menuLabel, MenuLabel):
        caption = menuLabel[0]
        keywords = menuLabel[1]
    else:
        caption = menuLabel
        keywords = {}
    lst = []
    isList = None
    icon = None
    menuClass = None
    internalName = ''
    typeID = None
    menuEntryDataLst = []
    for menu in menus:
        for entry in menu:
            if isinstance(entry, MenuEntryData):
                entryCaption = entry.GetLabelPath() or entry.GetText()
                if caption == entryCaption:
                    menuEntryDataLst.append(entry)
            elif _IsSame(caption, keywords, entry, menuLabel):
                if type(entry[1]) in (str, unicode):
                    return (menuLabel, entry[1])
                if type(entry[1]) == tuple and entry[1][0] == 'isDynamic' and len(entry) == 2:
                    return (menuLabel, entry[1])
                if len(entry) > 3:
                    icon = entry[3]
                if isList is None:
                    isList = isinstance(entry[1], list)
                if isList != isinstance(entry[1], list):
                    return
                if isList:
                    lst.append(entry[1])
                    internalName = entry[5] if len(entry) > 5 else ''
                    typeID = entry[6] if len(entry) > 6 else None
                elif len(entry) > 2:
                    func = entry[1]
                    arguments = entry[2]
                    lst.append([func, arguments])
                    menuClass = entry[4] if len(entry) > 4 else None
                    internalName = entry[5] if len(entry) > 5 else ''
                    typeID = entry[6] if len(entry) > 6 else None
                else:
                    lst.append(entry[1:])
                break

    if menuEntryDataLst:
        if len(menuEntryDataLst) > 1:
            return _MergeMenuEntryDataList(menuEntryDataLst)
        else:
            return menuEntryDataLst[0]
    extraArgsTuple = (icon,
     menuClass,
     internalName,
     typeID)
    if isList:
        menuEntryArgs = (menuLabel, MergeMenus(lst), NO_ARGUMENTS) + extraArgsTuple
        return menuEntryArgs
    elif CaptionIsInMultiFunctions(caption) or _IsDeliverToCorpHangarFolderEntry(lst):
        return _GetMergedMenuEntryArgs(caption, extraArgsTuple, lst, menuLabel)
    else:
        return (menuLabel, _ExecMulti, lst) + extraArgsTuple


def _MergeMenuEntryDataList(menuEntryDataLst):
    menuEntryData = menuEntryDataLst[0]
    if CaptionIsInMultiFunctions(menuEntryData.GetActionID()):
        functions = [ m.func for m in menuEntryDataLst ]
        menuEntryData.func = lambda : _CallMultipleFunctions(functions)
        menuEntryData.quantity = len(functions)
    return menuEntryData


def _CallMultipleFunctions(functions):
    for func in functions:
        func()


def _GetMergedMenuEntryArgs(caption, extraArgsTuple, lst, menuLabel):
    mergedArgs = []
    rest = []
    for entry in lst:
        args = entry[1]
        rest = entry[2:]
        if isinstance(args, list):
            mergedArgs += args
        else:
            log.LogWarn('unsupported format of arguments for MergeMenu, function label: ', caption)

    if isinstance(rest, tuple):
        rest = list(rest)
    extraArgs = rest or extraArgsTuple
    if isinstance(extraArgs, tuple):
        extraArgs = list(extraArgs)
    if mergedArgs:
        if type(lst[0][0]) == tuple and lst[0][0][0] == 'isDynamic':
            return [menuLabel, ('isDynamic', lst[0][0][1], lst[0][0][2] + (mergedArgs,))] + rest
        else:
            return [menuLabel, _CheckLocked, (lst[0][0], mergedArgs)] + extraArgs


def _IsSame(caption, keywords, entry, menuLabel):
    if isinstance(menuLabel, MenuLabel):
        entryCaption = entry[0][0]
        entryKeywords = entry[0][1]
    else:
        entryCaption = entry[0]
        entryKeywords = {}
    return entryCaption == caption and entryKeywords == keywords


def _GetAllLabelsAndReasons(menus):
    allCaptionsAndKeywords = []
    allLabels = []
    allReasons = {}
    for menu in menus:
        i = 0
        if getattr(menu, 'reasonsWhyNotAvailable', {}):
            allReasons.update(menu.reasonsWhyNotAvailable)
        for each in menu:
            if each is None:
                if len(allLabels) <= i:
                    allLabels.append(None)
                else:
                    while allLabels[i] is not None:
                        i += 1
                        if i == len(allLabels):
                            allLabels.append(None)
                            break

            else:
                if isinstance(each, MenuEntryData):
                    label = each.GetMenuLabel()
                    labelPath = each.GetLabelPath()
                    labelKeywords = each.GetLabelKeywords()
                else:
                    label = each[0]
                    if isinstance(label, MenuLabel):
                        labelPath = label[0]
                        labelKeywords = label[1]
                    else:
                        labelPath = label
                        labelKeywords = {}
                if (labelPath, labelKeywords) not in allCaptionsAndKeywords:
                    allLabels.insert(i, label)
                    allCaptionsAndKeywords.append((labelPath, labelKeywords))
            i += 1

    return (allLabels, allReasons)


def _IsDeliverToCorpHangarFolderEntry(lst):
    try:
        return len(lst) and len(lst[0]) and lst[0][0] is invItemFunctions.DeliverToCorpHangarFolder
    except TypeError:
        return False


def _ExecAction(action):
    apply(*action)


def _ExecMulti(*actions):
    for each in actions:
        uthread.new(_ExecAction, each)


def _CheckLocked(func, invItemsOrIDs):
    return invItemFunctions.CheckLocked(func, invItemsOrIDs, sm.GetService('invCache'))
