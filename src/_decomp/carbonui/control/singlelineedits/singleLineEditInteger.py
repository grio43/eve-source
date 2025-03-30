#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\singlelineedits\singleLineEditInteger.py
from carbon.common.script.util.commonutils import StripTags
from carbonui import uiconst
from carbonui.control.singlelineedits.baseSingleLineEditNumber import BaseSingleLineEditNumbers
from carbonui.uicore import uicore
from eve.common.lib import appConst
from qtyTooltip.qtyConst import EDIT_INPUT_TYPE_INT
from qtyTooltip.tooltip import LoadTooltipForNumber

class SingleLineEditInteger(BaseSingleLineEditNumbers):
    default_name = 'SingleLineEditInteger'
    default_minValue = 0
    default_maxValue = appConst.maxInt
    default_legalCharacters = '-0123456789'
    default_dataType = int

    def SetText(self, text, format = True):
        if not isinstance(text, basestring):
            text = repr(self.dataType(text))
        if text.lower() == 'l':
            text = ''
        text = StripTags(text, stripOnly=['localized'])
        displayText = text
        if format:
            displayText = self.FormatNumeric(text)
            text = self.StripLeadingZeroesIfNecessary(text)
        displayText = self.SanitizeText(displayText)
        self.textLabel.SetText(displayText)
        self.text = text

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if not self.text or self.text == '-':
            return
        return LoadTooltipForNumber(tooltipPanel, self.hint, self.dataType(self.text), EDIT_INPUT_TYPE_INT)

    def ChangeNumericValue(self, val):
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            val *= 10
        if val > 0:
            val = max(1, self.dataType(val))
        else:
            val = min(-1, self.dataType(val))
        super(SingleLineEditInteger, self).ChangeNumericValue(val)

    def Paste(self, paste, deleteStart = None, deleteEnd = None, forceFocus = False):
        if '.' in paste:
            paste = self.dataType(round(float(paste.replace(self.GetLocalizedThousandSeparator(), ''))))
        super(SingleLineEditInteger, self).Paste(str(paste), deleteStart, deleteEnd, forceFocus)

    def SetMaxValue(self, newMaxValue):
        if type(newMaxValue) == long:
            self.dataType = long
        super(SingleLineEditInteger, self).SetMaxValue(newMaxValue)
