#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\textImporting\importQuickbar.py
import itertools
from brennivin.itertoolsext import Bundle
from textImporting import GetLines, EXTRA_TEXT_SYMBOL_OPEN, EXTRA_TEXT_SYMBOL_CLOSE, SUBLEVEL_FOLDER, SUBLEVEL_TYPE

class QuickbarImporter(object):

    def __init__(self, typeIDFinder):
        self.typeIDFinder = typeIDFinder

    def ImportText(self, text, firstIdx = 1):
        bundleLDict = {}
        if not text:
            return bundleLDict
        allLines = GetLines(text)
        lastFolderIdBySublevel = {}
        for i, eachLine in enumerate(allLines):
            lineID = i + firstIdx
            extraText = ''
            if eachLine.startswith('+'):
                numSymbols = sum([ 1 for _ in itertools.takewhile(lambda x: x == SUBLEVEL_FOLDER, eachLine) ])
                subLevel = numSymbols - 1
                text = eachLine.replace(SUBLEVEL_FOLDER * numSymbols, '')
                label = text.strip()
                parentID = lastFolderIdBySublevel.get(subLevel - 1, 0)
                lastFolderIdBySublevel[subLevel] = lineID
            else:
                subLevel = sum([ 1 for _ in itertools.takewhile(lambda x: x == SUBLEVEL_TYPE, eachLine) ])
                text = eachLine.replace(SUBLEVEL_TYPE * subLevel, '', 1)
                text = text.strip()
                typeID, nameFound = self.FindTypeID(text)
                if not typeID:
                    continue
                label = typeID
                extraText = self.FindExtraText(text)
                parentID = lastFolderIdBySublevel.get(subLevel - 1, 0)
            bundleLDict[lineID] = Bundle(parent=parentID, id=lineID, extraText=extraText, label=label)

        return bundleLDict

    def FindTypeID(self, text):
        text = text.lower()
        parts = text.split()
        numParts = len(parts)
        for x in xrange(numParts, 0, -1):
            potentialName = ' '.join(parts[:x])
            potentialName = potentialName.lower()
            typeID = self.typeIDFinder.GetTypeIDFromEitherLangage(potentialName)
            if typeID:
                return (typeID, potentialName)

        return (None, None)

    def FindExtraText(self, text):
        extraText = ''
        parts = text.split()
        if len(parts) < 2:
            return extraText
        lastPart = parts[-1]
        if lastPart.startswith(EXTRA_TEXT_SYMBOL_OPEN) and lastPart.endswith(EXTRA_TEXT_SYMBOL_CLOSE):
            extraText = lastPart.replace(EXTRA_TEXT_SYMBOL_OPEN, '', 1).replace(EXTRA_TEXT_SYMBOL_CLOSE, '', 1)
            try:
                return int(extraText)
            except ValueError:
                return extraText

        return extraText
