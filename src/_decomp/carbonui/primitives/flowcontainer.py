#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\flowcontainer.py
from carbonui import uiconst
from carbonui.primitives.base import Base
from carbonui.primitives.container import Container
from carbonui.uiconst import AxisAlignment
from carbonui.uicore import uicore
import uthread
import uthread2
import blue
ALLOWED_AUTO_HEIGHT_ALIGNMENTS = (uiconst.BOTTOMLEFT,
 uiconst.BOTTOMRIGHT,
 uiconst.CENTER,
 uiconst.CENTERBOTTOM,
 uiconst.CENTERLEFT,
 uiconst.CENTERRIGHT,
 uiconst.CENTERTOP,
 uiconst.TOBOTTOM,
 uiconst.TOBOTTOM_NOPUSH,
 uiconst.TOPLEFT,
 uiconst.TOPRIGHT,
 uiconst.TOTOP,
 uiconst.TOTOP_NOPUSH)

class FlowContainer(Container):
    default_name = 'flowContainer'

    def __init__(self, contentSpacing = (0, 0), centerContent = False, contentAlignment = AxisAlignment.START, crossAxisAlignment = AxisAlignment.START, autoHeight = True, **kwargs):
        self.contentSpacing = contentSpacing
        if centerContent:
            self._contentAlignment = AxisAlignment.CENTER
        else:
            self._contentAlignment = contentAlignment
        self._crossAxisAlignment = crossAxisAlignment
        self._autoHeight = autoHeight
        super(FlowContainer, self).__init__(**kwargs)

    @property
    def contentAlignment(self):
        return self._contentAlignment

    @contentAlignment.setter
    def contentAlignment(self, value):
        if self._contentAlignment != value:
            self._contentAlignment = value
            self._ForceAlignmentDirty()

    @property
    def crossAxisAlignment(self):
        return self._crossAxisAlignment

    @crossAxisAlignment.setter
    def crossAxisAlignment(self, value):
        if self._crossAxisAlignment != value:
            self._crossAxisAlignment = value
            self._ForceAlignmentDirty()

    @property
    def autoHeight(self):
        return self._autoHeight

    @autoHeight.setter
    def autoHeight(self, value):
        if self._autoHeight != value:
            self._autoHeight = value
            self._ForceAlignmentDirty()

    def _ForceAlignmentDirty(self):
        self.FlagAlignmentDirty()
        self._childrenAlignmentDirty = True

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
            retBudgetLeft, retBudgetTop, retBudgetWidth, retBudgetHeight = (budgetLeft,
             budgetTop,
             budgetWidth,
             budgetHeight)
        else:
            retBudgetLeft, retBudgetTop, retBudgetWidth, retBudgetHeight, sizeChange = Base.UpdateAlignment(self, budgetLeft, budgetTop, budgetWidth, budgetHeight)
            childrenDirty = self._childrenAlignmentDirty
        self._childrenAlignmentDirty = False
        if childrenDirty or forceUpdate or sizeChange:

            def AdjustRow(rowObjects, width, height, rowY):
                if self.contentAlignment == AxisAlignment.CENTER:
                    xOffset = (self.displayWidth - width) / 2
                elif self.contentAlignment == AxisAlignment.END:
                    xOffset = self.displayWidth - width
                else:
                    xOffset = 0
                for item in rowObjects:
                    yOffset = 0
                    if self.crossAxisAlignment != AxisAlignment.START and item.displayHeight != height:
                        if self.crossAxisAlignment == AxisAlignment.CENTER:
                            yOffset = (height - item.displayHeight) / 2
                        elif self.crossAxisAlignment == AxisAlignment.END:
                            yOffset = height - item.displayHeight
                    item.displayY = rowY + yOffset
                    item.displayX += xOffset

            x = 0
            y = 0
            rowItems = []
            rowHeight = 0
            rowWidth = 0
            spacingX = uicore.ScaleDpi(self.contentSpacing[0])
            spacingY = uicore.ScaleDpi(self.contentSpacing[1])
            for each in self.children:
                if each.align != uiconst.NOALIGN:
                    continue
                if each.display:
                    scaledWidth = uicore.ScaleDpi(each.width)
                    scaledHeight = uicore.ScaleDpi(each.height)
                    if scaledWidth != each.displayWidth or scaledHeight != each.displayHeight or forceUpdate:
                        if forceUpdate:
                            each._forceUpdateAlignment = True
                        each._alignmentDirty = True
                        each.UpdateAlignment()
                    if x + scaledWidth > self.displayWidth:
                        AdjustRow(rowItems, rowWidth - spacingX, rowHeight, y)
                        x = 0
                        y += rowHeight + spacingY
                        rowWidth = 0
                        rowHeight = 0
                        rowItems = []
                    rowItems.append(each)
                    rowHeight = max(rowHeight, scaledHeight)
                    rowWidth += scaledWidth + spacingX
                    each.displayX = x
                    x += scaledWidth + spacingX

            AdjustRow(rowItems, rowWidth - spacingX, rowHeight, y)
            if self.autoHeight and self.align in ALLOWED_AUTO_HEIGHT_ALIGNMENTS:
                newHeight = uicore.ReverseScaleDpi(y + rowHeight)
                if newHeight != self.height:
                    self.height = newHeight
                    retBudgetLeft, retBudgetTop, retBudgetWidth, retBudgetHeight, sizeChange = Base.UpdateAlignment(self, budgetLeft, budgetTop, budgetWidth, budgetHeight)
        return (retBudgetLeft,
         retBudgetTop,
         retBudgetWidth,
         retBudgetHeight,
         sizeChange)

    def UnifyContentSize(self):
        maxWidth = 0
        maxHeight = 0
        for each in self.children:
            maxWidth = max(maxWidth, each.width)
            maxHeight = max(maxHeight, each.height)

        for each in self.children:
            each.width = maxWidth
            each.height = maxHeight

    def _AppendChildRO(self, child):
        child.align = uiconst.NOALIGN
        Container._AppendChildRO(self, child)

    def _InsertChildRO(self, idx, child):
        child.align = uiconst.NOALIGN
        Container._InsertChildRO(self, idx, child)

    def _RemoveChildRO(self, child):
        Container._RemoveChildRO(self, child)
        if not self.destroyed:
            self._childrenAlignmentDirty = True
            self.FlagAlignmentDirty()
