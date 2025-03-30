#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihighlighting\ui\retrouipointer.py
import carbonui.const as uiconst
from carbonui.uicore import uicore
from uihighlighting.ui.uipointer import BaseUiPointer

class RetroUiPointer(BaseUiPointer):
    MAX_WIDTH = 200
    MARGIN = (12, 15, 12, 15)

    def ApplyAttributes(self, attributes):
        self.pointDirections = attributes.get('pointDirections', (0, 0, 0))
        self.text = attributes.basicData.uiPointerText or ''
        self.tooltip = None
        super(RetroUiPointer, self).ApplyAttributes(attributes)

    def GetTooltipDirection(self):
        pointUp, pointDown, pointLeft = self.pointDirections
        if pointUp:
            return uiconst.POINT_TOP_2
        if pointDown:
            return uiconst.POINT_BOTTOM_2
        if pointLeft:
            return uiconst.POINT_LEFT_2
        return uiconst.POINT_RIGHT_2

    def ConstructContent(self):
        self.tooltip = uicore.uilib.tooltipHandler.LoadPersistentTooltip(owner=self.pointToElement, customPointDirection=self.GetTooltipDirection())
        if not self.tooltip:
            return
        self.tooltip.state = uiconst.UI_NORMAL
        self.tooltip.LoadGeneric1ColumnTemplate()
        self.tooltip.margin = self.MARGIN
        self.tooltip.AddLabelMedium(name='RetroUiPointerLabel', text=self.text, align=uiconst.CENTER, bold=True, wrapWidth=self.MAX_WIDTH)
        self.width = self.tooltip.width
        self.height = self.tooltip.height

    def SetPosition(self, left, top):
        previousLeft = self.left
        previousTop = self.top
        super(RetroUiPointer, self).SetPosition(left, top)
        if self.tooltip:
            leftChange = self.left - previousLeft
            topChange = self.top - previousTop
            previousTooltipLeft = self.tooltip.left
            previousTooltipTop = self.tooltip.top
            newTooltipLeft = previousTooltipLeft + leftChange
            newTooltipTop = previousTooltipTop + topChange
            self.tooltip.SetPosition(newTooltipLeft, newTooltipTop)

    def UpdatePointToElement(self, pointToElement):
        super(RetroUiPointer, self).UpdatePointToElement(pointToElement)
        if self.tooltip and not self.tooltip.destroyed:
            self.tooltip.Close()
        self.ConstructContent()

    def Close(self):
        if self.tooltip:
            self.tooltip.CloseWithFade()
        super(RetroUiPointer, self).Close()

    def Show(self, *args):
        if self.tooltip:
            self.tooltip.Show()
        super(RetroUiPointer, self).Show()

    def Hide(self, *args):
        super(RetroUiPointer, self).Hide()
        if self.tooltip:
            self.tooltip.Hide()
