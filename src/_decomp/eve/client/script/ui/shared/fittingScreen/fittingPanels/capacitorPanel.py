#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingPanels\capacitorPanel.py
import math
import dogma.data as dogma_data
import eveformat
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.util.color import Color
from dogma import const as dogmaConst
from dogma.attributes.format import GetFormatAndValue
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.fittingScreen.fittingUtil import GetColoredText
from eve.client.script.ui.shared.fittingScreen.fittingPanels.basePanel import BaseMenuPanel
from localization import GetByLabel
import trinity
BAD_COLOR = (70 / 256.0, 26 / 256.0, 13.0 / 256.0)
GOOD_COLOR = (240 / 256.0, 90 / 256.0, 50.0 / 256.0)
EMPTY_COLOR = (0.25, 0.25, 0.25, 0.75)

class CapacitorPanel(BaseMenuPanel):

    def ApplyAttributes(self, attributes):
        BaseMenuPanel.ApplyAttributes(self, attributes)
        self.capCapacityAttribute = dogma_data.get_attribute(dogmaConst.attributeCapacitorCapacity)
        self.rechargeRateAttribute = dogma_data.get_attribute(dogmaConst.attributeRechargeRate)
        self.maxcap = None

    def LoadPanel(self, initialLoad = False):
        self.Flush()
        self.display = True
        self.DrawPowerCoreCont()
        self.AddLabels()
        BaseMenuPanel.FinalizePanelLoading(self, initialLoad)

    def DrawPowerCoreCont(self):
        self.powerCoreCont = Container(parent=self, name='powercore', pos=(5, 5, 30, 30), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)

    def AddLabels(self):
        textCont = ContainerAutoSize(parent=self, align=uiconst.CENTERLEFT, left=45, width=200, idx=0)
        self.capAndRechargeLabel = EveLabelMedium(text='', parent=textCont, state=uiconst.UI_NORMAL, align=uiconst.TOTOP)
        self.capAndRechargeLabel.hint = GetByLabel('UI/Fitting/FittingWindow/CapacityAndRechargeRate')
        self.delteLabel = EveLabelMedium(text='', parent=textCont, state=uiconst.UI_NORMAL, align=uiconst.TOTOP)
        self.delteLabel.hint = GetByLabel('UI/Fitting/FittingWindow/ExcessCapacitor')

    def UpdateCapacitorPanel(self):
        deltaInfo, deltaPercentageInfo, loadBalanceInfo, ttlInfo = self.controller.GetCapSimulatorInfos()
        self.SetHeaderText(ttlInfo.value, loadBalanceInfo.value)
        if not self.panelLoaded or self.powerCoreCont.destroyed:
            return
        self.SetRechargeText()
        self.SetDeltaText(deltaInfo, deltaPercentageInfo)
        self.RedrawPowercore()
        self.ColorPowerCore(self.powerUnits, loadBalanceInfo.value, ttlInfo.value)

    def SetHeaderText(self, TTL, loadBalance):
        if loadBalance > 0:
            sustainableText = eveformat.color(GetByLabel('UI/Fitting/FittingWindow/Stable'), color=eveColor.SUCCESS_GREEN)
            capHint = GetByLabel('UI/Fitting/FittingWindow/ModulesSustainable')
        else:
            sustainableText = eveformat.color(GetByLabel('UI/Fitting/FittingWindow/CapacitorNotStable', time=long(TTL)), color=eveColor.DANGER_RED)
            capHint = GetByLabel('UI/Fitting/FittingWindow/ModulesNotSustainable')
        self.SetStatusText(text=sustainableText, hintText=capHint)

    def SetRechargeText(self):
        maxCapInfo = self.controller.GetCapacitorCapacity()
        maxCapFormattedValue = GetFormatAndValue(self.capCapacityAttribute, int(maxCapInfo.value))
        maxCapText = GetColoredText(isBetter=maxCapInfo.isBetterThanBefore, text=maxCapFormattedValue)
        rechargeRate = self.controller.GetCapRechargeRate()
        rechargeFormattedValue = GetFormatAndValue(self.rechargeRateAttribute, int(rechargeRate.value))
        rechargeRateText = GetColoredText(isBetter=rechargeRate.isBetterThanBefore, text=rechargeFormattedValue)
        capText = GetByLabel('UI/Fitting/FittingWindow/CapacitorCapAndRechargeTime', capacitorCapacity=maxCapText, capacitorRechargeTime=rechargeRateText, startColorTag1='', startColorTag2='', endColorTag='')
        self.capAndRechargeLabel.text = capText

    def SetDeltaText(self, deltaInfo, deltaPercentageInfo):
        deltaText = GetByLabel('UI/Fitting/FittingWindow/CapacitorDelta', delta=deltaInfo.value, percentage=deltaPercentageInfo.value)
        deltaText = GetColoredText(isBetter=deltaInfo.isBetterThanBefore, text=deltaText)
        self.delteLabel.text = deltaText

    def RedrawPowercore(self):
        self.powerCoreCont.Flush()
        maxCapInfo = self.controller.GetCapacitorCapacity()
        numcol = min(10, int(maxCapInfo.value / 50))
        rotStep = 360.0 / max(1, numcol)
        colWidth = max(12, min(16, numcol and int(192 / numcol)))
        colHeight = self.powerCoreCont.height
        self.powerUnits = []
        for colIdx in xrange(numcol):
            powerColumn = self.AddPowerColumn(self.powerCoreCont, colIdx, rotStep, colWidth, colHeight)
            for cellIdx in xrange(3):
                newCell = self.AddCell(powerColumn, cellIdx)
                self.powerUnits.insert(0, newCell)

        self.maxcap = maxCapInfo.value

    def AddPowerColumn(self, parent, colIdx, rotStep, colWidth, colHeight):
        rotation = math.radians(colIdx * -rotStep)
        powerColumn = Transform(parent=parent, name='powerColumn', pos=(0,
         0,
         colWidth,
         colHeight), align=uiconst.CENTER, state=uiconst.UI_DISABLED, rotation=rotation, idx=0)
        return powerColumn

    def AddCell(self, parent, cellIdx):
        newcell = Sprite(parent=parent, name='pmark', pos=(0,
         cellIdx * 4,
         8 - cellIdx * 2,
         4), align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/capacitorCell.png', color=(0.94, 0.35, 0.19, 1.0), idx=0, blendMode=trinity.TR2_SBM_ADD)
        return newcell

    def ScaleColor(self, colorTuple, scale):
        return Color(colorTuple[0] * scale, colorTuple[1] * scale, colorTuple[2] * scale)

    def ColorPowerCore(self, powerUnits, loadBalance, TTL):
        badColor = self.ScaleColor(BAD_COLOR, 1.0 - loadBalance)
        goodColor = self.ScaleColor(GOOD_COLOR, loadBalance)
        visible = max(0, min(len(powerUnits), int(loadBalance * len(powerUnits))))
        for cellIdx, each in enumerate(powerUnits):
            if cellIdx >= visible:
                each.SetRGBA(*EMPTY_COLOR)
            else:
                r = badColor.r + goodColor.r
                g = badColor.g + goodColor.g
                b = badColor.b + goodColor.b
                each.SetRGBA(r, g, b, 1.0)

        if loadBalance == 0:
            hint = GetByLabel('UI/Fitting/FittingWindow/CapRunsOutBy', ttl=long(TTL))
        else:
            hint = GetByLabel('UI/Fitting/FittingWindow/CapSustainableBy', balance=loadBalance * 100)
        self.hint = hint
