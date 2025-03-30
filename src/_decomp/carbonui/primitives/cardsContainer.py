#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\cardsContainer.py
from carbonui import uiconst
from carbonui.uicore import uicore
from carbonui.primitives.container import Container
from carbonui.primitives.base import Base
import math

class _CardGroup(Container):
    default_fill_always = False
    default_contentSpacing = (0, 0)

    def ApplyAttributes(self, attributes):
        super(_CardGroup, self).ApplyAttributes(attributes)
        self.fill_always = attributes.get('fill_always', self.default_fill_always)
        self.contentSpacing = attributes.get('contentSpacing', self.default_contentSpacing)

    def get_num_children(self):
        return len(self.children)

    def _AppendChildRO(self, child):
        child.align = uiconst.TOALL
        child.pos = (0, 0, 0, 0)
        super(_CardGroup, self)._AppendChildRO(child)

    def _InsertChildRO(self, idx, child):
        child.align = uiconst.TOALL
        child.pos = (0, 0, 0, 0)
        super(_CardGroup, self)._InsertChildRO(idx, child)

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        if self.destroyed:
            return (budgetLeft,
             budgetTop,
             budgetWidth,
             budgetHeight,
             False)
        budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly = super(_CardGroup, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
        columnCount = len(self.children)
        spacingX = self.contentSpacing[0]
        step = (self.displayWidth - spacingX * (columnCount - 1)) / float(columnCount) if columnCount else 0
        for idx, child in enumerate(self.children):
            cellLeft = step * idx
            cellRight = step * (idx + 1)
            padLeft = spacingX if 0 < idx < columnCount else 0
            budget = (cellLeft + padLeft * idx,
             0,
             cellRight - cellLeft,
             self.displayHeight)
            child._alignmentDirty = True
            child.UpdateAlignment(*budget)

        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight,
         updateChildrenOnly)


class CardsContainer(Container):
    default_cardHeight = 100
    default_cardMaxWidth = 350
    default_contentSpacing = (0, 0)
    default_maxColumnCount = None
    default_allow_stretch = False

    def ApplyAttributes(self, attributes):
        super(CardsContainer, self).ApplyAttributes(attributes)
        self._cardHeight = attributes.get('cardHeight', self.default_cardHeight)
        self._cardMaxWidth = attributes.get('cardMaxWidth', self.default_cardMaxWidth)
        self._contentSpacing = attributes.get('contentSpacing', self.default_contentSpacing)
        self.maxColumnCount = attributes.get('maxColumnCount', self.default_maxColumnCount)
        self.allow_stretch = attributes.get('allow_stretch', self.default_allow_stretch)

    @property
    def cardMaxWidth(self):
        return self._cardMaxWidth

    @cardMaxWidth.setter
    def cardMaxWidth(self, value):
        self._cardMaxWidth = value
        self.FlagAlignmentDirty()

    @property
    def cardHeight(self):
        return self._cardHeight

    @cardHeight.setter
    def cardHeight(self, value):
        self._cardHeight = value
        self.FlagAlignmentDirty()

    @property
    def contentSpacing(self):
        return self._contentSpacing

    @contentSpacing.setter
    def contentSpacing(self, value):
        self._contentSpacing = value
        self.FlagAlignmentDirty()

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        if self.destroyed:
            return (budgetLeft,
             budgetTop,
             budgetWidth,
             budgetHeight,
             False)
        numColumns = self._GetNumColumns()
        lines = self._GetLines(numColumns)
        numLines = len(lines)
        self.height = numLines * self.cardHeight + (numLines - 1) * self.contentSpacing[1]
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
            cellHeight = uicore.ScaleDpi(self.cardHeight)
            spacingX = uicore.ScaleDpi(self.contentSpacing[0])
            spacingY = uicore.ScaleDpi(self.contentSpacing[1])
            cellTop = 0
            padTop = 0
            for line in lines:
                cellTop += padTop
                cellLeft = 0
                cellBottom = cellTop + cellHeight
                lineColumns = 0
                for group in line:
                    lineColumns += self._GetColCount(group)

                if not self.allow_stretch and not self._GetLineFill(line):
                    lineColumns = max(lineColumns, numColumns)
                cellWidth = (self.displayWidth - spacingX * (lineColumns - 1)) / float(lineColumns) if lineColumns else 0
                lineIdx = 0
                for group in line:
                    colCount = self._GetColCount(group)
                    cellRight = min(self.displayWidth, int(cellWidth * (lineIdx + colCount)))
                    if colCount > 1:
                        cellRight += spacingX * (colCount - 1)
                    padLeft = spacingX if 0 < lineIdx < lineColumns else 0
                    budget = (cellLeft + padLeft * lineIdx,
                     cellTop,
                     cellRight - cellLeft,
                     cellBottom - cellTop)
                    group._alignmentDirty = True
                    if forceUpdate:
                        group._forceUpdateAlignment = True
                    group.UpdateAlignment(*budget)
                    cellLeft = cellRight
                    lineIdx += colCount

                cellTop = min(self.displayHeight, cellBottom)
                padTop = spacingY

        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight,
         sizeChange)

    def _GetNumColumns(self):
        numColumns = int(math.ceil(max(0, uicore.ReverseScaleDpi(self.displayWidth)) / self.cardMaxWidth + 0.5))
        if self.maxColumnCount is not None:
            numColumns = min(numColumns, self.maxColumnCount)
        return numColumns

    def _GetLines(self, numColumns):
        lines = []
        currentLine = []
        currentColumnCount = 0
        for group in self.children:
            if self._GetFill(group):
                if len(currentLine) > 0:
                    lines.append(currentLine)
                    currentLine = []
                currentLine.append(group)
                lines.append(currentLine)
                currentLine = []
                currentColumnCount = 0
                continue
            groupColCount = self._GetColCount(group)
            if groupColCount + currentColumnCount > numColumns and currentColumnCount:
                lines.append(currentLine)
                currentLine = [group]
                currentColumnCount = groupColCount
            else:
                currentLine.append(group)
                currentColumnCount += groupColCount

        if len(currentLine) > 0:
            lines.append(currentLine)
        return lines

    def _GetColCount(self, item):
        if isinstance(item, _CardGroup):
            return item.get_num_children()
        return 1

    def _GetFill(self, item):
        if isinstance(item, _CardGroup):
            return item.fill_always
        return False

    def _GetLineFill(self, line):
        for item in line:
            if self._GetFill(item):
                return True

        return False

    def _AppendChildRO(self, child):
        child.align = uiconst.TOALL
        child.pos = (0, 0, 0, 0)
        super(CardsContainer, self)._AppendChildRO(child)

    def _InsertChildRO(self, idx, child):
        child.align = uiconst.TOALL
        child.pos = (0, 0, 0, 0)
        super(CardsContainer, self)._InsertChildRO(idx, child)

    def CreateGroup(self, fill_always = False):
        return _CardGroup(parent=self, fill_always=fill_always, contentSpacing=self.contentSpacing)
