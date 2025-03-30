#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\historyCont.py
from carbonui import ButtonVariant, Density
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button
from eve.client.script.ui.control.historyBar import HistoryBar
from localization import GetByLabel

class FittingHistoryCont(Container):
    default_width = 270
    default_height = 50

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        historyController = attributes.historyController
        topCont = Container(name='topCont', parent=self, align=uiconst.TOTOP)
        btn = Button(name='historyBtn', align=uiconst.CENTERRIGHT, parent=topCont, label=GetByLabel('UI/Fitting/FittingWindow/SaveState'), func=sm.GetService('ghostFittingSvc').SaveSnapshot, density=Density.COMPACT, variant=ButtonVariant.GHOST)
        label = eveLabel.EveLabelMedium(parent=topCont, name='historyLabel', align=uiconst.CENTERLEFT)
        topCont.height = max(btn.height, label.height)
        historyBar = HistoryBar(parent=self, align=uiconst.CENTERBOTTOM, isAllowedToLoadFunc=sm.GetService('ghostFittingSvc').IsAllowedToLoadSnapshot, callback=sm.GetService('ghostFittingSvc').LoadSnapshot, historyController=historyController, width=self.width, bitHintFunc=sm.GetService('ghostFittingSvc').GetBitHintFromData)
        label.left = historyBar.leftBtn.width
        btn.left = historyBar.rightBtn.width
        spaceLeft = self.width - (label.left + btn.width + btn.left)
        for labelPath in ['UI/Fitting/FittingWindow/SimulationHistory', 'UI/Fitting/FittingWindow/SimulationHistoryShort']:
            simHistoryText = GetByLabel(labelPath)
            textwidth, _ = eveLabel.EveLabelMedium.MeasureTextSize(simHistoryText)
            if spaceLeft > textwidth:
                label.text = simHistoryText
                break

        self.height = topCont.height + historyBar.height + 4
