#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingPanels\fighterPanel.py
from carbonui import const as uiconst, ButtonVariant
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.fittingScreen.fittingPanels.basePanel import BaseMenuPanel
from eve.client.script.ui.shared.fittingScreen.fittingUtil import GetColoredText
from localization import GetByLabel
from carbonui.uicore import uicore

class FighterPanel(BaseMenuPanel):
    default_iconSize = 20
    droneStats = (('bandwidth', 'res:/UI/Texture/classes/Fitting/StatsIcons/bandwidth.png', 'DroneBandwidth'), ('controlRange', 'res:/UI/Texture/classes/Fitting/StatsIcons/controlRange.png', 'DroneControlRange'))

    def ApplyAttributes(self, attributes):
        BaseMenuPanel.ApplyAttributes(self, attributes)

    def LoadPanel(self, initialLoad = False):
        self.Flush()
        self.ResetStatsDicts()
        self.display = True
        parentGrid = self.GetValueParentGrid(columns=1)
        self.fullSquadrons = EveLabelMedium(text='', parent=parentGrid, left=7, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, top=4)
        self.partialSquadrons = EveLabelMedium(text='', parent=parentGrid, left=7, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, top=0)
        btn = Button(parent=self, label=GetByLabel('UI/Fitting/FittingWindow/ManageFighters'), func=self.ManageDrones, align=uiconst.CENTERRIGHT, left=10, variant=ButtonVariant.GHOST)
        BaseMenuPanel.FinalizePanelLoading(self, initialLoad)

    def ManageDrones(self, *args):
        if self.controller.IsSimulated():
            self.controller.OpenFakeFighterBay()
        else:
            uicore.cmd.OpenFighterBayOfActiveShip()

    def UpdateFighterStats(self):
        self.SetFighterDpsText()
        if not self.panelLoaded:
            return
        full, partial = self.controller.GetFullAndPartialSquadrons()
        fullText = GetByLabel('UI/Fitting/FittingWindow/NumFullSquadrons', numSquadrons=int(full.value))
        fullColoredText = GetColoredText(isBetter=full.isBetterThanBefore, text=fullText)
        self.fullSquadrons.text = fullColoredText
        partialText = GetByLabel('UI/Fitting/FittingWindow/NumPartialSquadrons', numSquadrons=int(partial.value))
        partialColoredText = GetColoredText(isBetter=partial.isBetterThanBefore, text=partialText)
        self.partialSquadrons.text = partialColoredText

    def SetFighterDpsText(self):
        totalFighterDpsInfo = self.controller.GetFighterDps()
        fighterText = GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=totalFighterDpsInfo.value)
        fighterColoredText = GetColoredText(isBetter=totalFighterDpsInfo.isBetterThanBefore, text=fighterText)
        self.SetStatusText(fighterColoredText)
