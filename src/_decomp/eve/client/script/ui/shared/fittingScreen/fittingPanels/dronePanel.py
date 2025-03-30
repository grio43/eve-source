#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingPanels\dronePanel.py
from carbon.common.script.util.format import FmtAmt
from carbonui import ButtonVariant, const as uiconst, Density
from carbonui.primitives.sprite import Sprite
from dogma.attributes.format import GetFormattedAttributeAndValueAllowZero
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.fittingScreen.fittingPanels.basePanel import BaseMenuPanel
from eve.client.script.ui.shared.fittingScreen.fittingUtil import GetColoredText
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
from localization import GetByLabel
from carbonui.uicore import uicore

class DronePanel(BaseMenuPanel):
    default_iconSize = 20
    droneStats = (('bandwidth', 'res:/UI/Texture/classes/Fitting/StatsIcons/bandwidth.png', 'DroneBandwidth'), ('controlRange', 'res:/UI/Texture/classes/Fitting/StatsIcons/controlRange.png', 'DroneControlRange'))

    def ApplyAttributes(self, attributes):
        BaseMenuPanel.ApplyAttributes(self, attributes)

    def LoadPanel(self, initialLoad = False):
        self.Flush()
        self.ResetStatsDicts()
        self.display = True
        parentGrid = self.GetValueParentGrid()
        for configName, texturePath, tooltipName in self.droneStats:
            valueCont = self.GetValueCont(self.iconSize)
            parentGrid.AddCell(cellObject=valueCont)
            icon = Sprite(texturePath=texturePath, parent=valueCont, align=uiconst.CENTERLEFT, pos=(3,
             0,
             self.iconSize,
             self.iconSize), state=uiconst.UI_DISABLED)
            label = EveLabelMedium(text='', parent=valueCont, left=0, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
            SetFittingTooltipInfo(targetObject=valueCont, tooltipName=tooltipName)
            self.statsLabelsByIdentifier[configName] = label
            self.statsIconsByIdentifier[configName] = icon
            self.statsContsByIdentifier[configName] = valueCont

        self.selectedDrones = EveLabelMedium(text='', parent=parentGrid, left=self.iconSize + 7, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        parentGrid.AddCell(cellObject=Button(label=GetByLabel('UI/Fitting/FittingWindow/ManageDrones'), func=self.ManageDrones, align=uiconst.TOPLEFT, variant=ButtonVariant.GHOST, density=Density.COMPACT), cellPadding=4)
        BaseMenuPanel.FinalizePanelLoading(self, initialLoad)

    def ManageDrones(self, *args):
        if self.controller.IsSimulated():
            self.controller.OpenFakeDroneBay()
        else:
            uicore.cmd.GetCommandAndExecute('OpenDroneBayOfActiveShip')

    def UpdateDroneStats(self):
        activeDroneNumInfo, droneBandwidthUsageInfo, droneDpsInfo = self.controller.GetDroneInfo()
        self.SetDroneDpsText(droneDpsInfo)
        if not self.panelLoaded:
            return
        shipBandwidthInfo = self.controller.GetDroneBandwidth()
        text = GetByLabel('UI/Fitting/FittingWindow/NumDronesActive', numDrones=activeDroneNumInfo.value)
        coloredText = GetColoredText(isBetter=activeDroneNumInfo.isBetterThanBefore, text=text)
        self.selectedDrones.text = coloredText
        bandwithUsedText = FmtAmt(droneBandwidthUsageInfo.value)
        bandwithUsedTextColoredText = GetColoredText(isBetter=droneBandwidthUsageInfo.isBetterThanBefore, text=bandwithUsedText)
        shipBandwidthText = GetFormattedAttributeAndValueAllowZero(const.attributeDroneBandwidth, shipBandwidthInfo.value).value
        shipBandwidthColoredText = GetColoredText(isBetter=shipBandwidthInfo.isBetterThanBefore, text=shipBandwidthText)
        bandwidthText = '%s/%s' % (bandwithUsedTextColoredText, shipBandwidthColoredText)
        self.SetLabel('bandwidth', bandwidthText)
        droneControlRange = self.controller.GetDroneControlRange()
        controlRangeText = GetFormattedAttributeAndValueAllowZero(const.attributeDroneControlDistance, droneControlRange.value).value
        droneControlRangeColoredText = GetColoredText(isBetter=droneControlRange.isBetterThanBefore, text=controlRangeText)
        self.SetLabel('controlRange', droneControlRangeColoredText)

    def SetDroneDpsText(self, droneDpsInfo):
        droneText = GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=droneDpsInfo.value)
        droneColoredText = GetColoredText(isBetter=droneDpsInfo.isBetterThanBefore, text=droneText)
        self.SetStatusText(droneColoredText)
