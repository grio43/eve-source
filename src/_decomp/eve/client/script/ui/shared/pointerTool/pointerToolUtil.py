#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\pointerTool\pointerToolUtil.py
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.pointerTool.entry import PointerWndEntry, FavoritePointerWndEntry, FavoriteListGroup
import eve.client.script.ui.shared.pointerTool.favorites as fav
from eve.client.script.ui.shared.pointerTool.favorites import GetNormalPointerEntryMenu, GetFavoritePointerEntryMenu
from localization import GetByLabel

def GetFilteredScrollList(filterText, selectedName, sourceLocation):
    scrollList = []
    scrollList += _GetFavoriteGroup(filterText)
    neocomNodes = _GetNeocomNodes(filterText, selectedName, sourceLocation)
    scrollList += _GetSortedEntries(neocomNodes, GetByLabel('UI/Help/PointerWndNeocomHeader'))
    actionNodes = _GetActionNodes(filterText, selectedName, sourceLocation)
    scrollList += _GetSortedEntries(actionNodes, GetByLabel('UI/Help/PointerWndSelectedItemHeader'))
    uiHighlightNodes = _GetUiHighlightNodes(filterText, selectedName, sourceLocation)
    scrollList += _GetSortedEntries(uiHighlightNodes, GetByLabel('UI/Help/PointerWndUiElements'))
    agencytNodes = _GetAgencyNodes(filterText, selectedName, sourceLocation)
    scrollList += _GetSortedEntries(agencytNodes, GetByLabel('UI/Help/PointerAgencyElements'))
    stationServiceNodes = _GetStationServiceNodes(filterText, selectedName, sourceLocation)
    scrollList += _GetSortedEntries(stationServiceNodes, GetByLabel('UI/Help/PointerWndStationServices'))
    skillPlanNodes = _SkillPlanNodes(filterText, selectedName, sourceLocation)
    scrollList += _GetSortedEntries(skillPlanNodes, GetByLabel('UI/Help/PointerWndSkillPlans'))
    return scrollList


def GetFilteredNodes(filterText, sourceLocation = 0):
    filterText = filterText.lower()
    allNodes = []
    allNodes += _GetActionNodes(filterText, None, sourceLocation, useLongName=True)
    allNodes += _GetNeocomNodes(filterText, None, sourceLocation, useLongName=True, openElement=True)
    allNodes += _GetUiHighlightNodes(filterText, None, sourceLocation)
    allNodes += _GetAgencyNodes(filterText, None, sourceLocation)
    allNodes += _GetStationServiceNodes(filterText, None, sourceLocation, useLongName=True, openElement=True)
    allNodes += _SkillPlanNodes(filterText, None, sourceLocation, useLongName=True)
    return allNodes


def _GetUiHighlightNodes(filterText, selectedName, sourceLocation):
    pointerDict = sm.GetService('helpPointer').GetHighlightByElementName()
    uiHighlightsData = _GetEntryNodes(filterText, pointerDict, selectedName, sourceLocation)
    return uiHighlightsData


def _GetAgencyNodes(filterText, selectedName, sourceLocation):
    pointerDict = sm.GetService('helpPointer').GetAgencyLabelByElementName()
    agencyNodes = _GetEntryNodes(filterText, pointerDict, selectedName, sourceLocation)
    return agencyNodes


def _GetNeocomNodes(filterText, selectedName, sourceLocation, useLongName = False, openElement = False):
    pointerDict = sm.GetService('helpPointer').GetNeocomPointersByElementName()
    neocomData = _GetEntryNodes(filterText, pointerDict, selectedName, sourceLocation, openElement, useLongName)
    return neocomData


def _GetActionNodes(filterText, selectedName, sourceLocation, useLongName = False):
    pointerDict = sm.GetService('helpPointer').GetActionLabelPathsByElementName()
    actionData = _GetEntryNodes(filterText, pointerDict, selectedName, sourceLocation, useLongName=useLongName)
    return actionData


def _GetStationServiceNodes(filterText, selectedName, sourceLocation, openElement = False, useLongName = False):
    pointerDict = sm.GetService('helpPointer').GetStationServiceTextByElementName()
    stationServiceData = _GetEntryNodes(filterText, pointerDict, selectedName, sourceLocation, openElement, useLongName)
    return stationServiceData


def _SkillPlanNodes(filterText, selectedName, sourceLocation, useLongName = False):
    pointerDict = sm.GetService('helpPointer').GetSkillPlansByElementName()
    stationServiceData = _GetEntryNodes(filterText, pointerDict, selectedName, sourceLocation, useLongName)
    return stationServiceData


def _GetEntryNodes(filterText, pointerDict, selectedName, sourceLocation, openElement = None, useLongName = None):
    dataList = []
    for uiElementName, pointerObject in pointerDict.iteritems():
        if filterText and pointerObject.labelLower.find(filterText) < 0:
            continue
        entryData = _GetEntryData(pointerObject, selectedName, sourceLocation, openElement, useLongName)
        dataList.append(entryData)

    return dataList


def _GetEntryData(pointerObject, selectedName = '', sourceLocation = 0, openElement = False, useLongName = False, sublevel = 1):
    entryData = {'label': pointerObject.label,
     'uiElementName': pointerObject.uiElementName,
     'texturePath': pointerObject.texturePath,
     'iconData': pointerObject.iconData,
     'longName': pointerObject.labelLong,
     'useLongName': useLongName,
     'pointerObject': pointerObject,
     'pointerObjects': [pointerObject],
     'openElement': openElement,
     'sourceLocation': sourceLocation,
     'sublevel': sublevel,
     'isSelected': pointerObject.uiElementName == selectedName,
     'iconSizes': pointerObject.iconSizes}
    return entryData


def _GetSortedEntries(dataNodes, headerText):
    if dataNodes:
        forceOpen = any((x for x in dataNodes if x.get('isSelected', None)))
        data = GetBoilerplateData()
        data.update({'GetSubContent': _GetEntriesSubContent,
         'label': headerText,
         'id': ('uiPointerGroups', headerText),
         'groupItems': dataNodes,
         'sublevel': 0,
         'forceOpen': forceOpen})
        return [GetFromClass(ListGroup, data)]
    return []


def _GetEntriesSubContent(nodedata, *args):
    scrollList = []
    for eachNode in nodedata.groupItems:
        eachNode['OnGetMenu'] = GetNormalPointerEntryMenu
        entry = GetFromClass(PointerWndEntry, eachNode)
        scrollList.append((eachNode['label'], entry))

    scrollList = SortListOfTuples(scrollList)
    return scrollList


def GetBoilerplateData():
    return {'state': 'locked',
     'BlockOpenWindow': 1,
     'showicon': 'hide',
     'showlen': 0,
     'updateOnToggle': 0}


def _GetFavoriteGroup(filterText):
    rootGroupID = 0
    rootGroup = fav.GetFavoriteRootGroup()
    if filterText:
        elementNamesinFavorite = rootGroup.uiElementNames[:]
        groupWithName = False
        for g in fav.GetFavoriteGroups():
            elementNamesinFavorite += g.uiElementNames
            if g.groupName.lower().find(filterText) >= 0:
                groupWithName = True
                break

        if not groupWithName:
            filteredPointers = _FindValidPointersAfterFilter(filterText, elementNamesinFavorite)
            if not filteredPointers:
                return []
    data = GetBoilerplateData()
    data.update({'GetSubContent': _GetFavoriteSubGroups,
     'label': GetByLabel('UI/HelpPointers/Wnd/FavoriteGroup'),
     'id': ('uiPointerFavorites', rootGroupID),
     'groupKeyVal': rootGroup,
     'sublevel': 0,
     'groupID': rootGroupID,
     'MenuFunction': fav.GetFavoriteGroupMenu,
     'DropData': fav.OnDropDataInFavorite,
     'filterText': filterText})
    return [GetFromClass(FavoriteListGroup, data)]


def _GetFavoriteSubGroups(nodedata, *args):
    groupKeyVal = nodedata.groupKeyVal
    filterText = nodedata.filterText
    uiElements = groupKeyVal.uiElementNames
    allPointers = sm.GetService('helpPointer').GetAllPointersByElementName()
    pointerList = [ allPointers.get(x) for x in uiElements if x in allPointers ]
    scrollList = []
    parentSubLevel = nodedata.sublevel
    for pointerObject in pointerList:
        if filterText and pointerObject.labelLower.find(filterText) < 0:
            continue
        entryData = _GetEntryData(pointerObject, sublevel=parentSubLevel + 1)
        entryData['OnGetMenu'] = GetFavoritePointerEntryMenu
        entryData['parentGroup'] = groupKeyVal
        entry = GetFromClass(FavoritePointerWndEntry, entryData)
        scrollList.append(entry)

    subGroups = nodedata.groupKeyVal.get('subGroups', [])
    for eahcSubGroup in subGroups:
        groupName = eahcSubGroup.get('groupName', GetByLabel('UI/HelpPointers/Wnd/UnknownGroupName'))
        if filterText and groupName.lower().find(filterText) < 0:
            filteredPointers = _FindValidPointersAfterFilter(filterText, eahcSubGroup.uiElementNames, allPointers)
            if not filteredPointers:
                continue
        groupID = eahcSubGroup.groupID
        data = GetBoilerplateData()
        data.update({'GetSubContent': _GetFavoriteSubGroups,
         'label': groupName,
         'id': ('uiPointerFavorites', groupID),
         'groupKeyVal': eahcSubGroup,
         'sublevel': eahcSubGroup.subLevel,
         'MenuFunction': fav.GetFavoriteSubGroupMenu,
         'groupID': groupID,
         'DropData': fav.OnDropDataInFavorite,
         'filterText': filterText})
        scrollList += [GetFromClass(FavoriteListGroup, data)]

    return scrollList


def _FindValidPointersAfterFilter(filterText, uiElementNames, allPointers = None):
    if allPointers is None:
        allPointers = sm.GetService('helpPointer').GetAllPointersByElementName()
    pointersInSubGroup = [ allPointers.get(x) for x in uiElementNames if x in allPointers ]
    filteredPointers = [ x for x in pointersInSubGroup if x.labelLower.find(filterText) >= 0 ]
    return filteredPointers


class TextAndTexture(object):
    indentAmount = 10

    def __init__(self, text, texturePath = None, iconSizes = None, indentChar = '-', iconData = None):
        self.text = text
        self.texturePath = texturePath
        self.iconSizes = iconSizes
        self.indentChar = indentChar
        self.iconData = iconData

    def GetText(self):
        return self.text

    def GetTexturePath(self):
        return self.texturePath

    def GetIconData(self):
        return self.iconData

    def GetIconSizes(self):
        return self.iconSizes

    def GetIndentChar(self):
        return self.indentChar

    def GetMaxWidth(self, lineNum, defaultIconSize):
        totalWidth = lineNum * self.indentAmount
        if self.indentChar:
            textWidth, _ = EveLabelMedium.MeasureTextSize(self.indentChar)
            if textWidth:
                totalWidth += textWidth
        if self.texturePath:
            if self.iconSizes:
                iconWidth = self.iconSizes[0]
            else:
                iconWidth = defaultIconSize
            totalWidth += iconWidth
        textWidth, _ = EveLabelMedium.MeasureTextSize(self.text, bold=True)
        totalWidth += textWidth
        return totalWidth
