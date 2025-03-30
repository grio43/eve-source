#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingPanels\fuelPanel.py
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.fittingScreen.fittingPanels.attributePanel import AttributePanel
from eve.client.script.ui.shared.fittingScreen.fittingUtil import GetColoredText
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
from localization import GetByLabel
import carbonui.const as uiconst
ICON_SIZE = 20

class FuelPanel(AttributePanel):
    fuelInfo = ('fuel', 'res:/UI/Texture/classes/Fitting/StatsIcons/fuel.png', 'FuelUsage')

    def LoadPanel(self, initialLoad = False):
        AttributePanel.LoadPanel(self, initialLoad)
        parentGrid = self.GetValueParentGrid()
        self.AddFuelUsage(parentGrid)
        AttributePanel.FinalizePanelLoading(self, initialLoad)

    def AddFuelUsage(self, parentGrid):
        alignID, texturePath, tooltipName = self.fuelInfo
        c = self.GetValueCont(ICON_SIZE)
        parentGrid.AddCell(cellObject=c)
        icon = Sprite(texturePath=texturePath, parent=c, align=uiconst.CENTERLEFT, pos=(0,
         0,
         ICON_SIZE,
         ICON_SIZE), state=uiconst.UI_DISABLED)
        SetFittingTooltipInfo(targetObject=c, tooltipName=tooltipName)
        label = EveLabelMedium(text='', parent=c, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        self.statsLabelsByIdentifier[alignID] = label
        self.statsIconsByIdentifier[alignID] = icon
        self.statsContsByIdentifier[alignID] = c

    def UpdateFuelPanel(self):
        self.SetFuelUsageText()

    def SetFuelUsageText(self):
        fuelPerDay = self.controller.GetFuelUsage()
        text = GetByLabel('UI/Fitting/FittingWindow/FuelPerDay', unitsPerDay=fuelPerDay.value)
        coloredText = GetColoredText(isBetter=fuelPerDay.isBetterThanBefore, text=text)
        self.SetLabel(self.fuelInfo[0], coloredText)
