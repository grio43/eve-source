#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\scrollUtil.py
import itertools
from carbonui.uicore import uicore

class TabFinder(object):

    def GetTabStops(self, nodes, headertabs, entryClass, idx = None):
        maxContentWidths = self.GetMaxContentWidths(nodes, entryClass, idx)
        headerWidths = uicore.font.GetTabstopsAsWidth(uicore.font.MeasureTabstops(headertabs))
        return self.GetMaxTabStops(maxContentWidths, headerWidths)

    def GetMaxContentWidths(self, nodes, entryClass, idx):
        columnWidthsInNodes = [ entryClass.GetColWidths(node, idx) for node in nodes ]
        columnWidthsInNodes = filter(None, columnWidthsInNodes)
        maxContentWidths = [ max(x) for x in zip(*columnWidthsInNodes) ]
        return maxContentWidths

    def GetMaxTabStops(self, maxContentWidth, headerWidths):
        maxColWidth = [ max(z) for z in itertools.izip_longest(*[maxContentWidth, headerWidths]) ]
        newTabStops = self._FindMaxTabstopsFromWidths(maxColWidth)
        return newTabStops

    def _FindMaxTabstopsFromWidths(self, maxColWidth):
        newTabStops = []
        currentLeft = 0
        for eachColWidth in maxColWidth:
            currentLeft += eachColWidth
            newTabStops.append(currentLeft)

        return newTabStops
