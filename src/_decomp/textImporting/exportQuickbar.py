#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\textImporting\exportQuickbar.py
from collections import defaultdict
from textImporting import GetNameFunc, SUBLEVEL_FOLDER, SUBLEVEL_TYPE, EXTRA_TEXT_SYMBOL_OPEN, EXTRA_TEXT_SYMBOL_CLOSE
LINEBREAK = '\r\n'

class QuickbarExporter(object):

    def __init__(self):
        self.nameFunc = GetNameFunc(True)

    def ExportQuickbarToClipboard(self, quickbar, isLocalized = True):
        self.nameFunc = GetNameFunc(isLocalized)
        myExportList = []
        childrenByParentID = defaultdict(list)
        for entryID, eachEntry in quickbar.iteritems():
            childrenByParentID[eachEntry.parent].append(eachEntry)

        def AddEntriesToList(listOfEntries, sublevel = 0):
            for eachEntry in listOfEntries:
                eachName = self.GetName(eachEntry)
                isType = isinstance(eachEntry.label, int)
                extraText = getattr(eachEntry, 'extraText', None)
                myExportList.append((eachName,
                 sublevel,
                 isType,
                 extraText))
                entryID = eachEntry.id
                children = childrenByParentID.get(entryID, [])
                if children:
                    childrenSublevel = sublevel + 1
                    sortedChildren = sorted(children, key=self.GetSortValue)
                    AddEntriesToList(sortedChildren, childrenSublevel)

        rootChildren = childrenByParentID.get(0, [])
        sortedRootChildren = sorted(rootChildren, key=self.GetSortValue)
        AddEntriesToList(sortedRootChildren)
        exportList = []
        for name, sublevel, isType, extraText in myExportList:
            text = name
            subLevelToUse = sublevel
            if not isType:
                subLevelToUse += 1
            if subLevelToUse:
                if isType:
                    subLevelSymbol = SUBLEVEL_TYPE
                else:
                    subLevelSymbol = SUBLEVEL_FOLDER
                text = subLevelSymbol * subLevelToUse + ' %s' % text
            if extraText:
                text += ' %s%s%s' % (EXTRA_TEXT_SYMBOL_OPEN, extraText, EXTRA_TEXT_SYMBOL_CLOSE)
            exportList.append(text)

        exportText = LINEBREAK.join(exportList)
        return exportText

    def GetSortValue(self, entry):
        return self.GetName(entry, isSortValue=True)

    def GetName(self, eachEntry, isSortValue = False):
        if eachEntry.label is None:
            return
        else:
            if isinstance(eachEntry.label, int):
                typeID = eachEntry.label
                typeName = self.nameFunc(typeID)
                if isSortValue:
                    return typeName.lower()
                else:
                    return typeName
            if isSortValue:
                return ' %s' % eachEntry.label.lower()
            return eachEntry.label
