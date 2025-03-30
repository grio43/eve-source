#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\singleLineEditMarketPrice.py
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from marketutil import ticks
from marketutil.const import MAX_ORDER_PRICE
from qtyTooltip.qtyConst import EDIT_INPUT_TYPE_ISK

class SingleLineEditMarketPrice(SingleLineEditFloat):
    default_inputType = EDIT_INPUT_TYPE_ISK
    default_setvalue = ticks.ISK_MINIMUM_DIVISION
    default_minValue = ticks.ISK_MINIMUM_DIVISION
    default_maxValue = MAX_ORDER_PRICE
    default_decimalPlaces = 2
    default_isBuy = False
    _isTickActivated = True

    def ApplyAttributes(self, attributes):
        self._isBuy = attributes.get('isBuy', self.default_isBuy)
        self._isTickActivated = attributes.get('isTickActivated', True)
        super(SingleLineEditMarketPrice, self).ApplyAttributes(attributes)

    def DeactivateTickAlignment(self):
        self._isTickActivated = False

    def ActivateTickAlignment(self):
        self._isTickActivated = True
        self._RoundToTick()

    def _RoundToTick(self):
        if not self._isTickActivated:
            return
        currentValue = self.GetValue()
        if currentValue <= ticks.ISK_MINIMUM_DIVISION:
            self.SetValue(ticks.ISK_MINIMUM_DIVISION)
        elif not ticks.is_tick(currentValue):
            if self._isBuy:
                newValue = ticks.decrement_to_next_tick(currentValue)
            else:
                newValue = ticks.increment_to_next_tick(currentValue)
            self.SetValue(newValue)

    def OnKillFocus(self, *args):
        self._RoundToTick()
        super(SingleLineEditMarketPrice, self).OnKillFocus(*args)

    def ChangeNumericValue(self, val):
        if self._isTickActivated:
            if val > 0:
                currentValue = self.GetValue()
                newValue = ticks.increment_to_next_tick(currentValue)
                self.SetValue(newValue)
            elif val < 0:
                currentValue = self.GetValue()
                if currentValue > ticks.ISK_MINIMUM_DIVISION:
                    newValue = ticks.decrement_to_next_tick(currentValue)
                    self.SetValue(newValue)
        else:
            super(SingleLineEditMarketPrice, self).ChangeNumericValue(val)
