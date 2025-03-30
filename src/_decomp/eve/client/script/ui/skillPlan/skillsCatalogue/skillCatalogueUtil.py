#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillsCatalogue\skillCatalogueUtil.py
import math

def GetOrderedByColumn(values, numColumns):
    numLines = int(math.ceil(len(values) / float(numColumns)))
    reorderedGroupIDs = []
    for rowIdx in xrange(numLines):
        groupIDsInRow = values[rowIdx::numLines]
        reorderedGroupIDs += groupIDsInRow

    return reorderedGroupIDs
