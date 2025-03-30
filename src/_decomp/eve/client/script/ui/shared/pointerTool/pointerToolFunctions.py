#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\pointerTool\pointerToolFunctions.py
from eve.client.script.ui.shared.pointerTool.pointerToolConst import NEOCOM_PANEL_PREFIX
from carbonui.uicore import uicore

def DigToFindUniqueName(mouseOver):
    downUniqueElements = []
    CrawlDown(mouseOver, 'uniqueUiName', downUniqueElements)
    upUniqueElements = []
    CrawlUp(mouseOver, 'uniqueUiName', upUniqueElements)
    returnDict = [ (x.uniqueUiName.replace(NEOCOM_PANEL_PREFIX, ''), x) for x in downUniqueElements ]
    returnDict += [ (x.uniqueUiName.replace(NEOCOM_PANEL_PREFIX, ''), x) for x in upUniqueElements ]
    return returnDict


def DigToFindName(mouseOver):
    downNameElements = []
    CrawlDown(mouseOver, 'name', downNameElements)
    upNameElements = []
    CrawlUp(mouseOver, 'name', upNameElements)
    returnList = [ (x.name, x) for x in downNameElements ]
    returnList += [ (x.name, x) for x in upNameElements ]
    return returnList


def CrawlDown(element, nameAttribute, listOfFoundElements):
    elementName = getattr(element, nameAttribute, None)
    if elementName:
        listOfFoundElements.append(element)
    children = getattr(element, 'children', None)
    if not children:
        return
    for child in children:
        CrawlDown(child, nameAttribute, listOfFoundElements)


def CrawlUp(element, nameAttribute, listOfFoundElements):
    parent = getattr(element, 'parent', None)
    if not parent:
        return
    parentName = getattr(parent, nameAttribute, None)
    if parentName:
        listOfFoundElements.append(parent)
    CrawlUp(parent, nameAttribute, listOfFoundElements)


def FindDictForUniquelyNamedElements(element, namesToFind, foundDict):
    if getattr(element, 'uniqueUiName', None) in namesToFind and element.IsVisible():
        foundDict[element.uniqueUiName] = element
    children = getattr(element, 'children', None)
    if not children:
        return
    if getattr(element, 'name', None) == 'l_bracket':
        return
    for child in children:
        FindDictForUniquelyNamedElements(child, namesToFind, foundDict)


def GetScreenElementsByUniqueName(elementNames):
    dictOfMissingElements = {}
    FindDictForUniquelyNamedElements(uicore.desktop, elementNames, dictOfMissingElements)
    return dictOfMissingElements


def FindElementUnderMouse(mouseOver, mouseX = None, mouseY = None):
    relativesWithUniqueNames = DigToFindUniqueName(mouseOver)
    mouseX = uicore.uilib.x if mouseX is None else mouseX
    mouseY = uicore.uilib.y if mouseY is None else mouseY
    uiElementName, uiElement = FindUiElementNamesFromRelatives(relativesWithUniqueNames, mouseX, mouseY)
    if uiElementName is None:
        relativesWithNames = DigToFindName(mouseOver)
        uiElementName, uiElement = FindUiElementNamesFromRelatives(relativesWithNames, mouseX, mouseY)
    return (uiElementName, uiElement)


def FindUiElementNamesFromRelatives(relatives, x, y):
    if not relatives:
        return (None, None)
    allPointers = sm.GetService('helpPointer').GetAllPointersByElementName()
    relativeNames = {x[0] for x in relatives}
    uiElementNames = {x for x in allPointers.iterkeys() if x in relativeNames}
    backup = []
    for eachRelativeName, eachRelative in relatives:
        if eachRelativeName in uiElementNames:
            if _IsMouseOutsideElement(eachRelative, x, y):
                backup.append((eachRelativeName, eachRelative))
                continue
            return (eachRelativeName, eachRelative)

    if backup:
        return backup[0]
    return (None, None)


def _IsMouseOutsideElement(uiElement, x, y):
    if x < uiElement.absoluteLeft:
        return True
    if x > uiElement.absoluteRight:
        return True
    if y < uiElement.absoluteTop:
        return True
    if y > uiElement.absoluteBottom:
        return True
    return False


def GetInfoOnElementUnderMouse(mouseOver, mouseX, mouseY):
    uiElementName, _ = FindElementUnderMouse(mouseOver, mouseX, mouseY)
    if not uiElementName:
        return
    allPointers = sm.GetService('helpPointer').GetAllPointersByElementName()
    for eachUiElementName, eachPointerObj in allPointers.iteritems():
        if eachUiElementName == uiElementName:
            return eachPointerObj
