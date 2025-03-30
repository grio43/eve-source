#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\singlelineedits\singleLineEditFloat.py
import eveLocalization
import localization
from carbon.common.script.util.commonutils import StripTags
from carbonui import uiconst
from carbonui.control.singlelineedits.baseSingleLineEditNumber import BaseSingleLineEditNumbers
from carbonui.uicore import uicore
from eveprefs import prefs
from qtyTooltip.qtyConst import EDIT_INPUT_TYPE_FLOAT
from qtyTooltip.tooltip import LoadTooltipForNumber

class SingleLineEditFloat(BaseSingleLineEditNumbers):
    default_name = 'SingleLineEditFloat'
    default_minValue = 0.0
    default_maxValue = 922337203685477.0
    default_decimalPlaces = 1
    default_dataType = float
    default_legalCharacters = '-0123456789e.'
    DECIMAL = '.'

    def ApplyAttributes(self, attributes):
        self.decimalPlaces = attributes.get('decimalPlaces', self.default_decimalPlaces)
        super(SingleLineEditFloat, self).ApplyAttributes(attributes)

    def ValidateNewText(self, newText):
        if newText == self.DECIMAL:
            return False
        if newText.count(self.DECIMAL) > 1:
            uicore.Message('uiwarning03')
            return False
        significand, decimalPoint, decimals = newText.partition(self.DECIMAL)
        hasTooManyDecimals = len(decimals) > self.decimalPlaces
        if hasTooManyDecimals:
            numDecimalsToCut = len(decimals) - self.decimalPlaces
            return newText[:-numDecimalsToCut]
        return newText

    def SetText(self, text, format = True):
        if not isinstance(text, basestring):
            text = '%.*f' % (self.decimalPlaces, self.dataType(text))
        text = StripTags(text, stripOnly=['localized'])
        decimalPlaces = 0
        if self.DECIMAL in text:
            significand, decimalPoint, decimals = text.partition(self.DECIMAL)
            decimalPlaces = min(len(decimals), self.decimalPlaces)
            if decimalPlaces:
                text = significand + decimalPoint + decimals[:decimalPlaces]
        displayText = text
        if format:
            displayText = self.FormatNumeric(text, decimalPlaces=decimalPlaces)
            text = self.StripLeadingZeroesIfNecessary(text)
        displayText = self.SanitizeText(displayText)
        shouldAddHyphen = self.HYPHEN in text and self.HYPHEN not in displayText
        if shouldAddHyphen:
            displayText = self.HYPHEN + displayText
        shouldAddDecimal = decimalPlaces == 0 and self.DECIMAL in text
        if shouldAddDecimal:
            displayText += self.GetLocalizedDecimal()
        self.textLabel.SetText(displayText)
        self.text = text

    def GetLocalizedDecimal(self):
        if session:
            localizedDecimal = eveLocalization.GetDecimalSeparator(localization.SYSTEM_LANGUAGE)
        else:
            localizedDecimal = prefs.GetValue('decimal', '.')
        return localizedDecimal

    def SetValue(self, text, docallback = 1):
        isString = isinstance(text, basestring)
        if isString:
            text = StripTags(text, stripOnly=['localized'])
            text = self.PrepareFloatString(text)
        return super(SingleLineEditFloat, self).SetValue(text, docallback)

    def Paste(self, paste, deleteStart = None, deleteEnd = None, forceFocus = False):
        paste = self.FilterIllegalChars(paste)
        for char in paste:
            if char not in self.legalCharacters:
                uicore.Message('uiwarning03')
                return

        paste = self.PrepareFloatString(paste)
        super(SingleLineEditFloat, self).Paste(paste, deleteStart, deleteEnd, forceFocus)

    def OnChar(self, char, flag):
        if unichr(char) in ',.':
            return False
        return super(SingleLineEditFloat, self).OnChar(char, flag)

    def OnKeyDown(self, vkey, flag):
        if vkey in (uiconst.VK_DECIMAL, uiconst.VK_OEM_PERIOD, uiconst.VK_OEM_COMMA):
            self.Insert(self.DECIMAL)
            return
        super(SingleLineEditFloat, self).OnKeyDown(vkey, flag)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if not self.text or self.text == '-':
            return
        return LoadTooltipForNumber(tooltipPanel, self.hint, self.dataType(self.text), EDIT_INPUT_TYPE_FLOAT)

    def ChangeNumericValue(self, val):
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            val *= 10
        val *= 1 / float(10 ** self.decimalPlaces)
        super(SingleLineEditFloat, self).ChangeNumericValue(val)

    @staticmethod
    def PrepareFloatString(numberString):
        commasInString = numberString.count(',')
        periodsInString = numberString.count('.')
        if commasInString and periodsInString:
            haveDecimal = False
            stripped = u''
            for each in reversed(unicode(numberString)):
                if each in '-0123456789e.':
                    if each in u',.':
                        if haveDecimal:
                            continue
                        haveDecimal = True
                        stripped = '.' + stripped
                    else:
                        stripped = each + stripped

            return stripped
        if commasInString >= 2:
            numberString = filter(lambda x: x in '-0123456789e.', numberString)
            return numberString
        if periodsInString >= 2:
            numberString = filter(lambda x: x in '-0123456789e,', numberString)
            numberString = numberString.replace(',', '.')
            return numberString
        numberString = filter(lambda x: x in '-0123456789e,.', numberString)
        numberString = numberString.replace(',', '.')
        return numberString
