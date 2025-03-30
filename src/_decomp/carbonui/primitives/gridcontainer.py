#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\gridcontainer.py
import math
from carbonui import uiconst
from carbonui.uicore import uicore
from carbonui.primitives.container import Container
from carbonui.primitives.base import Base

class GridContainer(Container):
    __guid__ = 'uicls.GridContainer'
    default_name = 'gridContainer'
    default_columns = 0
    default_lines = 0
    default_contentSpacing = (0, 0)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.columns = attributes.get('columns', self.default_columns)
        self.lines = attributes.get('lines', self.default_lines)
        self.contentSpacing = attributes.get('contentSpacing', self.default_contentSpacing)

    @property
    def lines(self):
        return self._lines

    @lines.setter
    def lines(self, value):
        self._lines = value
        self.FlagMyChildrenAlignmentDirty()

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, value):
        self._columns = value
        self.FlagMyChildrenAlignmentDirty()

    def FlagMyChildrenAlignmentDirty(self):
        self.FlagAlignmentDirty()
        for each in self.children:
            each._alignmentDirty = True

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        if self.destroyed:
            return (budgetLeft,
             budgetTop,
             budgetWidth,
             budgetHeight,
             False)
        forceUpdate = self._forceUpdateAlignment
        if updateChildrenOnly:
            childrenDirty = True
            sizeChange = False
        else:
            budgetLeft, budgetTop, budgetWidth, budgetHeight, sizeChange = Base.UpdateAlignment(self, budgetLeft, budgetTop, budgetWidth, budgetHeight)
            childrenDirty = self._childrenAlignmentDirty
        self._childrenAlignmentDirty = False
        numChildren = len(self.children)
        if numChildren and (childrenDirty or forceUpdate or sizeChange):
            numColumns, numLines = self._GetNumColumnsAndLines(numChildren)
            cellWidth = self.displayWidth / float(numColumns) if numColumns else 0
            cellHeight = self.displayHeight / float(numLines) if numLines else 0
            spacingX = uicore.ScaleDpi(self.contentSpacing[0])
            spacingY = uicore.ScaleDpi(self.contentSpacing[1])
            cellTop = 0
            for line in xrange(numLines):
                cellLeft = 0
                cellBottom = int(cellHeight * (line + 1))
                for column in xrange(numColumns):
                    ix = line * numColumns + column
                    if ix < numChildren:
                        cellRigth = min(self.displayWidth, int(cellWidth * (column + 1)))
                        padTop = spacingY if line > 0 and line < numLines else 0
                        padLeft = spacingX if column > 0 and column < numColumns else 0
                        budget = (cellLeft + padLeft,
                         cellTop + padTop,
                         cellRigth - cellLeft - padLeft,
                         cellBottom - cellTop - padTop)
                        child = self.children[ix]
                        child._alignmentDirty = True
                        if forceUpdate:
                            child._forceUpdateAlignment = True
                        child.UpdateAlignment(*budget)
                        cellLeft = cellRigth

                cellTop = min(self.displayHeight, cellBottom)

        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight,
         sizeChange)

    def _GetNumColumnsAndLines(self, numChildren):
        numColumns = self.columns
        numLines = self.lines
        if numColumns < 1:
            numColumns = self._GetAutoNumColumns(numChildren, numColumns, numLines)
        if numLines < 1:
            if numColumns < 1:
                numColumns, numLines = self._GetAutoNumLinesAndColumns(numChildren, numLines)
            else:
                numLines = self._GetAutoNumLines(numChildren, numColumns, numLines)
        return (numColumns, numLines)

    def _GetAutoNumLines(self, numChildren, numColumns, numLines):
        numLines = int(float(numChildren) / float(numColumns) + 0.5)
        if numColumns * numLines < numChildren:
            numLines += 1
        return numLines

    def _GetAutoNumLinesAndColumns(self, numChildren, numLines):
        aspectRatio = float(self.displayWidth) / float(self.displayHeight)
        numColumns = int(math.sqrt(numChildren) * aspectRatio + 0.5)
        numLines = self._GetAutoNumLines(numChildren, numColumns, numLines)
        if self.displayWidth > self.displayHeight:
            while numColumns * numLines > numChildren:
                numColumns -= 1

            if numColumns * numLines < numChildren:
                numColumns += 1
        else:
            while numColumns * numLines > numChildren:
                numLines -= 1

            if numColumns * numLines < numChildren:
                numLines += 1
        return (numColumns, numLines)

    def _GetAutoNumColumns(self, numChildren, numColumns, numLines):
        if numLines > 0:
            numColumns = int(float(numChildren) / float(numLines) + 0.5)
            if numColumns * numLines < numChildren:
                numColumns += 1
        return numColumns
