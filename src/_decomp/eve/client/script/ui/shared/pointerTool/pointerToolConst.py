#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\pointerTool\pointerToolConst.py
from uihighlighting.uniqueNameConst import *

def SetUniqueUiNamesForTabs(tabs, tabNamesAndPointers):
    try:
        for tabName, pointerName in tabNamesAndPointers:
            tab = tabs.GetPanelByName(tabName)
            if tab:
                tab.uniqueUiName = pointerName

    except:
        pass


def SetUniqueNamesForColumns(scroll, columnNameAndPointersDict):
    try:
        innerScrollHeaders = scroll.sr.innerScrollHeaders
        if innerScrollHeaders:
            for child in innerScrollHeaders.children:
                pointer = columnNameAndPointersDict.get(child.name, None)
                if pointer:
                    child.uniqueUiName = pointer

    except:
        pass


SOURCE_LOCATION_LINK = 1
SOURCE_LOCATION_WINDOW = 2
SOURCE_LOCATION_SEARCH = 3
SOURCE_LOCATION_OVERLAY = 4
