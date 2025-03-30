#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\util\qtyTooltipUtil.py
from eve.client.script.ui.tooltips.tooltipUtil import RefreshTooltipForOwner
from qtyTooltip.tooltip import LoadQtyTooltipPanel

def AssignQtyTooltipFunc(uiElement, value, inputType, tooltipPointer = None):
    uiElement.LoadTooltipPanel = lambda tooltipPanel, *args: LoadQtyTooltipPanel(tooltipPanel, value, inputType=inputType)
    if tooltipPointer:
        uiElement.tooltipPointer = tooltipPointer
    RefreshTooltipForOwner(uiElement)
