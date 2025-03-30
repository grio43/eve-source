#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\neocomWalletUpdater.py
from carbon.client.script.environment.AudioUtil import PlaySound
from eve.client.script.ui.control.tooltips import TooltipPersistentPanel, COLOR_NUMBERVALUE_POSITIVE, COLOR_NUMBERVALUE_NEGATIVE, COLOR_NUMBERVALUE
import uthread
import blue
import eve.client.script.ui.control.pointerPanel as pointerPanel
import carbonui.const as uiconst
from carbonui.uicore import uicore
from neocom2.transaction import IskTransaction

class WalletUpdater(object):

    def __init__(self, transactions, finishedCallBack = None):
        self.transactions = transactions
        self.initialDelay = 1000
        self.showTime = 5000
        self.tooltipPanel = None
        self.finishedCallback = finishedCallBack
        self._ResetLabelsAndValues()

    def _ResetLabelsAndValues(self):
        self.debitsAndCreditsLabel = None
        self.debitsAndCreditsValue = None
        self.balanceValues = []

    def _FindWalletButton(self, neocom):
        for button in neocom.buttonCont.children:
            if button.name is 'wallet':
                return button
        else:
            return neocom.charSheetBtn

    def _ShouldPlayFavorableSound(self):
        for transaction in self.transactions:
            if isinstance(transaction, IskTransaction):
                return transaction.get_value() > 0

        return sum([ transaction.get_value() for transaction in self.transactions ]) > 0

    def _GetValueColor(self, value):
        if value > 0:
            return COLOR_NUMBERVALUE_POSITIVE
        else:
            return COLOR_NUMBERVALUE_NEGATIVE

    def ShowBalanceChange(self, neocom):
        if not self.transactions:
            return
        button = self._FindWalletButton(neocom)
        if button:
            parent = uicore.layer.menu
            self.tooltipPanel = TooltipPersistentPanel(parent=parent, owner=button, idx=0, width=220)
            self._LoadTooltipPanel(self.tooltipPanel)
            uthread.new(self._AnimationChain)
            if self._ShouldPlayFavorableSound():
                PlaySound(uiconst.SOUND_ISK_RECEIVED)
            else:
                PlaySound(uiconst.SOUND_ISK_PAID)

    def _AnimationChain(self):
        uicore.animations.FadeIn(self.tooltipPanel, duration=0.2)
        if self.debitsAndCreditsValue:
            uicore.animations.FadeTo(self.debitsAndCreditsValue, duration=0.2)
            uicore.animations.MoveInFromRight(self.debitsAndCreditsValue)
        uthread.new(self._AnimateTransaction)
        uthread.new(self._WaitAndClose)

    def _LoadDebitOrCredit(self, tooltipPanel):
        self.debitsAndCreditsLabel, self.debitsAndCreditsValue = tooltipPanel.AddLabelValue(label='', value='')

    def _LoadSpacer(self, tooltipPanel):
        spacer = tooltipPanel.AddSpacer(width=180, height=1, colSpan=2, rowSpan=1)
        spacer.color = (0.5, 0.5, 0.5, 1.0)

    def _LoadBalances(self, tooltipPanel):
        for transaction in self.transactions:
            label = transaction.get_balance_label()
            formattedValue = transaction.get_formatted_start_balance_value()
            color = COLOR_NUMBERVALUE
            _, balanceValue = tooltipPanel.AddLabelValue(label=label, value=formattedValue, valueColor=color)
            self.balanceValues.append(balanceValue)

    def _LoadTooltipPanel(self, tooltipPanel):
        self._ResetLabelsAndValues()
        tooltipPanel.LoadGeneric2ColumnTemplate()
        self._LoadDebitOrCredit(tooltipPanel)
        self._LoadSpacer(tooltipPanel)
        self._LoadBalances(tooltipPanel)

    def _AnimateTransaction(self):
        for order, transaction in enumerate(self.transactions):
            iteration = 0
            totalIterations = 20
            label = transaction.get_transaction_label()
            formattedValue = transaction.get_formatted_value()
            value = transaction.get_value()
            color = self._GetValueColor(value)
            self.debitsAndCreditsLabel.SetText(label)
            self.debitsAndCreditsValue.SetText(formattedValue)
            self.debitsAndCreditsValue.SetTextColor(color)
            if not order:
                blue.synchro.Sleep(self.initialDelay)
            originalBalance = transaction.get_start_balance_value()
            difference = value
            while iteration < totalIterations:
                increment = (iteration + 1) / (1.0 * totalIterations)
                label = self.balanceValues[order]
                value = originalBalance + difference * increment
                formattedValue = transaction.format_amount(value)
                label.SetText(formattedValue)
                iteration += 1
                blue.synchro.Sleep(25)

    def _WaitAndClose(self):
        blue.synchro.Sleep(self.showTime)
        pointerPanel.FadeOutPanelAndClose(self.tooltipPanel)
        if self.finishedCallback:
            self.finishedCallback()
