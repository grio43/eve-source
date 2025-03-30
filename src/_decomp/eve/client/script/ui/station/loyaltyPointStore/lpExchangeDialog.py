#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\loyaltyPointStore\lpExchangeDialog.py
import math
import localization
from carbon.common.script.util.format import FmtAmt
from carbonui import Density, uiconst
from carbonui.button.const import HEIGHT_COMPACT
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveLabel
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.station.loyaltyPointStore.lpLabels import LPStoreEntryLabel
from eve.common.lib import appConst as const
ENTRY_HEIGHT = HEIGHT_COMPACT

class LPExhangeDialog(Window):
    __guid__ = 'form.LPExhangeDialog'
    __notifyevents__ = ['OnLPStoreFilterChange', 'OnLPStoreCurrentPresetChange', 'OnLPStorePresetsChange']
    default_fixedWidth = 300
    default_fixedHeight = 225
    default_isMinimizable = False
    default_isCollapseable = False
    default_scope = uiconst.SCOPE_STATION
    default_captionLabelPath = 'UI/LPStore/LPExchangeDialogTitle'
    default_iconNum = 'res:/ui/Texture/WindowIcons/lpstore.png'

    def ApplyAttributes(self, attributes):
        super(LPExhangeDialog, self).ApplyAttributes(attributes)
        self.lpSvc = sm.GetService('lpstore')
        self.toCorpID = attributes.Get('toCorpID')
        self.toCorpName = cfg.eveowners.Get(self.toCorpID).ownerName
        self.fromCorpName = cfg.eveowners.Get(attributes.get('fromCorpID', const.ownerCONCORD)).ownerName
        self.currentFromCorpLPs = attributes.get('currentFromCorpLPs')
        self.currentToCorpLPs = attributes.get('currentToCorpLPs')
        self.exchangeRate = attributes.get('exchangeRate')
        self.maxCorporationLPs = int(self.currentFromCorpLPs * self.exchangeRate)
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self.sr.main, align=uiconst.TOTOP, callback=self.OnMainContResized)
        eveLabel.EveLabelMedium(parent=self.mainCont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/LPStore/ConvertLPMsg', toCorpName=self.toCorpName, exchangeRate=self.exchangeRate, fromCorpName=self.fromCorpName))
        eveLabel.EveCaptionSmall(parent=self.mainCont, text=self.toCorpName, padTop=16, align=uiconst.TOTOP)
        cont = Container(name='toCorpLPAmountContainer', parent=self.mainCont, align=uiconst.TOTOP, height=ENTRY_HEIGHT, state=uiconst.UI_PICKCHILDREN, padTop=4)
        eveLabel.EveLabelMedium(parent=cont, text=localization.GetByLabel('UI/LPStore/ExchangePurchaseAmount'), align=uiconst.CENTERLEFT)
        eveLabel.EveLabelMedium(parent=cont, text=localization.GetByLabel('UI/LPStore/LP'), align=uiconst.TORIGHT)
        self.amountEdit = SingleLineEditInteger(name='lpAmountEdit', parent=cont, pos=(17, 0, 80, 0), maxValue=self.maxCorporationLPs, align=uiconst.TOPRIGHT, OnChange=self.OnChangeEdit, density=Density.COMPACT)
        zeroLP = 0.0
        cont = Container(name='toCorpCurrentLPContainer', parent=self.mainCont, align=uiconst.TOTOP, height=ENTRY_HEIGHT, padTop=4)
        eveLabel.EveLabelMedium(parent=cont, text=localization.GetByLabel('UI/Common/Current'), align=uiconst.CENTERLEFT)
        self.toCorpCurrentLP = eveLabel.EveLabelMedium(parent=cont, text=localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(FmtAmt(zeroLP))), align=uiconst.CENTERRIGHT)
        cont = Container(name='toCorpTotalLPContainer', parent=self.mainCont, align=uiconst.TOTOP, height=ENTRY_HEIGHT, padTop=4)
        eveLabel.EveLabelMedium(parent=cont, text=localization.GetByLabel('UI/Common/Total'), align=uiconst.CENTERLEFT)
        self.toCorpTotalLP = eveLabel.EveLabelMedium(parent=cont, text=localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(FmtAmt(zeroLP))), align=uiconst.CENTERRIGHT)
        eveLabel.EveCaptionSmall(parent=self.mainCont, text=self.fromCorpName, padTop=16, align=uiconst.TOTOP)
        cont = Container(name='fromCorpCostLPContainer', parent=self.mainCont, align=uiconst.TOTOP, height=ENTRY_HEIGHT, padTop=4)
        eveLabel.EveLabelMedium(parent=cont, text=localization.GetByLabel('UI/Common/Cost'), align=uiconst.CENTERLEFT)
        self.fromCorpCostLP = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(FmtAmt(zeroLP))), align=uiconst.CENTERRIGHT)
        cont = Container(name='fromCorpFinalLPContainer', parent=self.mainCont, align=uiconst.TOTOP, height=ENTRY_HEIGHT, padTop=4)
        eveLabel.EveLabelMedium(parent=cont, text=localization.GetByLabel('UI/Common/Remaining'), align=uiconst.CENTERLEFT)
        self.fromCorpFinalLP = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(FmtAmt(zeroLP))), align=uiconst.CENTERRIGHT)
        self.ConstructButtonGroup()
        self.SetDetails(1)

    def OnMainContResized(self):
        _, height = self.GetWindowSizeForContentSize(height=self.mainCont.height)
        self.SetFixedHeight(height)

    def ConstructButtonGroup(self):
        self.buttons = ButtonGroup(parent=self.mainCont, align=uiconst.TOTOP, padTop=16)
        self.buttons.AddButton(localization.GetByLabel('UI/Common/Buttons/OK'), self.OnOK)
        self.buttons.AddButton(localization.GetByLabel('UI/Common/Buttons/Cancel'), self.OnCancel)

    def SetDetails(self, lpToExchange):
        concordLPCost = int(math.ceil(lpToExchange / self.exchangeRate))
        concordLPAfter = self.currentFromCorpLPs - concordLPCost
        corporationLPAfter = self.currentToCorpLPs + lpToExchange
        self.fromCorpCostLP.SetText(localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(FmtAmt(concordLPCost))))
        self.fromCorpFinalLP.SetText(localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(FmtAmt(concordLPAfter))))
        self.toCorpTotalLP.SetText(localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(FmtAmt(corporationLPAfter))))
        self.toCorpCurrentLP.SetText(localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(FmtAmt(self.currentToCorpLPs))))

    def OnChangeEdit(self, *args):
        self.SetDetails(self.amountEdit.GetValue())

    def OnOK(self, *args):
        try:
            amount = self.amountEdit.GetValue()
            if amount:
                self.lpSvc.ConvertConcordLP(self.toCorpID, int(self.amountEdit.GetValue()))
        finally:
            self.EnableButton()
            self.Close()

    def _OnClose(self, *args):
        self.EnableButton()

    def OnCancel(self, *args):
        self.Close()

    def EnableButton(self):
        from eve.client.script.ui.station.loyaltyPointStore.lpStoreWindow import LPStoreWindow
        wnd = LPStoreWindow.GetIfOpen()
        if wnd:
            wnd.Refresh()
