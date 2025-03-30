#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\textImporting\importMultibuy.py
from collections import defaultdict, OrderedDict
from textImporting import GetLines, CleanText
QTY_NOT_FOUND = -1

class ImportMultibuy(object):

    def __init__(self, marketImporter, decimalSymbol, digitSymbol):
        self.marketImporter = marketImporter
        self.decimalSymbol = decimalSymbol
        self.digitSymbol = digitSymbol

    def GetTypesAndQty(self, text):
        if not text:
            return ({}, [''])
        lines = GetLines(text)
        foundTypeIDs = OrderedDict()
        failedLines = []
        for eachLine in lines:
            typeID, qty = self.ParseLine(eachLine)
            if typeID:
                if typeID in foundTypeIDs:
                    foundTypeIDs[typeID] += qty
                else:
                    foundTypeIDs[typeID] = qty
            else:
                failedLines.append(eachLine)

        foundTypeIDsList = [ (t, q) for t, q in foundTypeIDs.iteritems() ]
        foundTypeIDsList.reverse()
        foundTypeIDsReversed = OrderedDict(foundTypeIDsList)
        return (foundTypeIDsReversed, failedLines)

    def ParseLine(self, line):
        typeID = None
        foundTypeName = ''
        line = CleanText(line)
        allParts = line.lower().split()
        qty = self._FindQty(allParts)
        if qty != QTY_NOT_FOUND:
            if len(allParts) < 1:
                return
            parts = allParts[1:]
            typeID, foundTypeName = self.FindTypeID(parts)
        if typeID is None:
            typeID, foundTypeName = self.FindTypeID(allParts)
            qty = QTY_NOT_FOUND
        if typeID and qty == QTY_NOT_FOUND:
            restOfLine = line.lower().replace(foundTypeName, '', 1).strip()
            parts = restOfLine.split()
            qty = self._FindQty(parts)
        if qty == QTY_NOT_FOUND:
            qty = 1
        return (typeID, qty)

    def _FindQty(self, parts):
        try:
            part = parts[0]
            part = part.strip('x')
            part = part.replace(self.digitSymbol, '')
            if self.decimalSymbol in part:
                part = part.replace(self.decimalSymbol, '.')
                part = float(part)
            qty = int(part)
        except (KeyError,
         TypeError,
         IndexError,
         ValueError):
            qty = QTY_NOT_FOUND

        return qty

    def FindTypeID(self, parts):
        if parts and parts[0] == 'x':
            parts = parts[1:]
        numParts = len(parts)
        for x in xrange(numParts, 0, -1):
            potentialName = ' '.join(parts[:x])
            potentialName = potentialName.lower()
            typeID = self.marketImporter.GetTypeIDFromEitherLangage(potentialName)
            if typeID:
                return (typeID, potentialName)

        return (None, None)
