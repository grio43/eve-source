#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\tooltips\tooltipUtil.py
from eve.client.script.ui.control.pointerPanel import FadeOutPanelAndClose
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipHeaderDescriptionWrapper, TooltipDescriptionWrapper
from carbonui.uicore import uicore

def RefreshTooltipForOwner(owner):
    if not uicore.uilib.tooltipHandler:
        return
    tooltipHandler = uicore.uilib.tooltipHandler
    doUpdate = uicore.uilib.mouseOver is owner
    if tooltipHandler.tooltipPanel and not (tooltipHandler.tooltipPanel.destroyed or tooltipHandler.tooltipPanel.beingDestroyed):
        if tooltipHandler.tooltipPanel.owner is owner and not tooltipHandler.tooltipPanel.owner.destroyed:
            FadeOutPanelAndClose(tooltipHandler.tooltipPanel, duration=0.1)
            tooltipHandler.tooltipPanel = None
            doUpdate = True
    if tooltipHandler.tooltipHint and not (tooltipHandler.tooltipHint.destroyed or tooltipHandler.tooltipHint.beingDestroyed):
        if tooltipHandler.tooltipHint.owner is owner and not tooltipHandler.tooltipHint.owner.destroyed:
            FadeOutPanelAndClose(tooltipHandler.tooltipHint, duration=0.1)
            tooltipHandler.tooltipHint = None
            doUpdate = True
    if doUpdate:
        tooltipHandler.lastMouseOver = None
        tooltipHandler.UpdateTooltip()


def SetTooltipHeaderAndDescription(targetObject, headerText, descriptionText):
    targetObject.tooltipPanelClassInfo = TooltipHeaderDescriptionWrapper(header=headerText, description=descriptionText)


def SetTooltipDescription(targetObject, descriptionText):
    targetObject.tooltipPanelClassInfo = TooltipDescriptionWrapper(description=descriptionText)
