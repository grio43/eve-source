#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\singlelineedits\baseSingleLineEditNumber.py
import blue
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.control.singlelineedits.baseSingleLineEdit import BaseSingleLineEdit
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from carbonui.control.buttonIcon import ButtonIcon
import eveLocalization
from localization import SYSTEM_LANGUAGE
from localization.formatters.numericFormatters import FormatNumeric
from menu import MenuLabel
import platform
import sys
import trinity
from uthread2 import start_tasklet

class BaseSingleLineEditNumbers(BaseSingleLineEdit):
    default_name = 'BaseSingleLineEditNumbers'
    default_minValue = None
    default_maxValue = None
    default_legalCharacters = ''
    default_dataType = None
    default_arrowIconColor = ButtonIcon.default_iconColor
    default_arrowIconClass = None
    default_arrowIconBlendMode = trinity.TR2_SBM_ADD
    default_arrowIconGlowColor = None
    default_arrowUseThemeColor = True
    default_showNumericControls = True
    HYPHEN = u'-'

    def ApplyAttributes(self, attributes):
        self.numericControlsCont = None
        minValue = attributes.get('minValue', self.default_minValue)
        maxValue = attributes.get('maxValue', self.default_maxValue)
        self.dataType = attributes.get('dataType', self.default_dataType)
        self.legalCharacters = attributes.get('legalCharacters', self.default_legalCharacters)
        self.arrowIconColor = attributes.get('arrowIconColor', self.default_arrowIconColor)
        self.arrowIconClass = attributes.get('arrowIconClass', self.default_arrowIconClass)
        self.arrowIconBlendMode = attributes.get('arrowIconBlendMode', self.default_arrowIconBlendMode)
        self.arrowIconGlowColor = attributes.get('arrowIconGlowColor', self.default_arrowIconGlowColor)
        self.arrowUseThemeColor = attributes.get('arrowUseThemeColor', self.default_arrowUseThemeColor)
        if minValue is None:
            minValue = self.default_minValue
        if maxValue is None:
            maxValue = self.default_maxValue
        self.SetMaxValue(maxValue)
        self.SetMinValue(minValue)
        super(BaseSingleLineEditNumbers, self).ApplyAttributes(attributes)
        showNumericControls = attributes.get('showNumericControls', self.default_showNumericControls)
        if showNumericControls:
            self.ShowNumericControls()

    def Insert(self, text):
        if self.readonly or not text:
            return
        if not isinstance(text, basestring):
            text = unichr(text)
        text = text.replace(u'\r', u' ').replace(u'\n', u'')
        text = self.FilterIllegalChars(text)
        if not text:
            return
        if text == self.HYPHEN and self.minValue >= 0:
            return
        if self.GetSelectionBounds() != (None, None):
            self.DeleteSelected(inserting=True)
        caretIndex = self.caretIndex[0]
        numSeparators = self.CountThousandSeparators()
        caretIndex -= numSeparators
        try:
            self.ValidateNegativeInput(text, caretIndex)
        except ValueError:
            return

        before = self.text[:caretIndex]
        after = self.text[caretIndex:]
        become = before + text + after
        become = self.ValidateNewText(become)
        if not become:
            return
        become, caretIndex = self.CheckForZeroInput(become, caretIndex)
        self.autoselect = False
        ret = self.CheckBounds(become, allowEmpty=bool(self.hintText), returnNoneIfOK=True)
        if ret is not None:
            if ret >= self.maxValue:
                become = repr(ret)
        self.SetText(become)
        newCaretIndex = min(caretIndex + max(len(text), 1), len(become))
        newNumSeparators = self.CountThousandSeparators(newCaretIndex + numSeparators)
        newCaretIndex += newNumSeparators
        if ret is not None:
            newCaretIndex = -1
        self.caretIndex = self.GetCursorFromIndex(newCaretIndex)
        self.OnTextChange()

    def ValidateNewText(self, newText):
        return newText

    def CheckBounds(self, quantity, allowEmpty = True, returnNoneIfOK = False):
        if allowEmpty and not quantity:
            return quantity
        if quantity == self.HYPHEN or not quantity:
            quantity = 0
        quantity = self.FilterIllegalChars(repr(quantity))
        minusIndex = repr(quantity).find(self.HYPHEN)
        if minusIndex > 1:
            return self.minValue
        quantity = self.dataType(quantity)
        if quantity > self.maxValue:
            quantity = self.maxValue
        elif quantity < self.minValue:
            quantity = self.minValue
        elif returnNoneIfOK:
            return None
        return quantity

    def SetMaxValue(self, newMaxValue):
        self.maxValue = self.dataType(min(newMaxValue, sys.maxsize))

    def SetMinValue(self, newMinValue):
        self.minValue = self.dataType(max(newMinValue, -sys.maxsize))

    def FilterIllegalChars(self, text):
        return filter(lambda x: x in self.legalCharacters, text)

    def Copy(self, selectStart = None, selectEnd = None):
        text = self.GetText()
        if selectStart is not None and selectEnd is not None:
            blue.pyos.SetClipboardData(text[selectStart:selectEnd])
        else:
            start, end = self.GetSelectionBounds()
            if not start and not end:
                blue.pyos.SetClipboardData(text)
            else:
                numSeparators = self.CountThousandSeparators(startIndex=start[0], endIndex=end[0])
                blue.pyos.SetClipboardData(text[start[0]:end[0] - numSeparators])

    def CountThousandSeparators(self, endIndex = 0, startIndex = 0):
        endIndex = endIndex if endIndex else self.caretIndex[0]
        displayText = self.textLabel.GetText()
        endIndex = min(endIndex, len(displayText))
        displayTextFromStartIndexToEndIndex = displayText[startIndex:endIndex]
        return displayTextFromStartIndexToEndIndex.count(self.GetLocalizedThousandSeparator())

    def CheckForZeroInput(self, become, caretIndex):
        allLettersAreZero = all((letter == '0' for letter in become))
        if allLettersAreZero:
            become = '0'
            caretIndex = 0
        return (become, caretIndex)

    def GetLocalizedThousandSeparator(self):
        return eveLocalization.GetThousandSeparator(SYSTEM_LANGUAGE)

    def OnUpKeyPressed(self):
        self.ChangeNumericValue(1)

    def OnDownKeyPressed(self):
        super(BaseSingleLineEditNumbers, self).OnDownKeyPressed()
        self.ChangeNumericValue(-1)

    def Delete(self, direction = True):
        if self.readonly:
            return
        oldCaretIndex = self.caretIndex[0]
        indexWithoutSeparators = max(oldCaretIndex - self.CountThousandSeparators(endIndex=oldCaretIndex), 0)
        if direction:
            begin = indexWithoutSeparators
            end = min(indexWithoutSeparators + 1, len(self.textLabel.text))
            newIndexWithoutSeparators = indexWithoutSeparators
        else:
            begin = max(indexWithoutSeparators - 1, 0)
            end = indexWithoutSeparators
            newIndexWithoutSeparators = max(indexWithoutSeparators - 1, 0)
        newText = self.text[:begin] + self.text[end:]
        self.SetText(newText)
        numSeparators = self.CountThousandSeparators(endIndex=indexWithoutSeparators)
        self.caretIndex = self.GetCursorFromIndex(newIndexWithoutSeparators + numSeparators)
        self.OnTextChange()

    def StripLeadingZeroesIfNecessary(self, newText):
        if not newText or newText.startswith('0.') or newText.startswith('0L') or newText == '0':
            return newText
        stripped = newText.lstrip('0')
        if stripped == 'L' or stripped == '':
            return '0'
        return stripped

    def DeleteSelected(self, inserting = False):
        if self.readonly:
            return
        start, end = self.GetSelectionBounds()
        self.selFrom = self.selTo = None
        self.RefreshSelectionDisplay()
        separatorsTilStart = 0
        if start[0]:
            separatorsTilStart = self.CountThousandSeparators(endIndex=start[0])
        separatorsBetweenSelection = self.CountThousandSeparators(startIndex=start[0], endIndex=end[0])
        deleteFromIndex = max(start[0] - separatorsTilStart, 0)
        deleteUntilIndex = min(end[0] - separatorsTilStart - separatorsBetweenSelection, len(self.text))
        newText = self.text[:deleteFromIndex] + self.text[deleteUntilIndex:]
        self.SetText(newText, format=not inserting)
        newSeparatorsTilStart = self.CountThousandSeparators(endIndex=deleteFromIndex)
        newCaretIndex = start[0] - separatorsTilStart + newSeparatorsTilStart
        self.caretIndex = self.GetCursorFromIndex(newCaretIndex)
        self.OnTextChange()

    def SetText(self, newText, format = True):
        return super(BaseSingleLineEditNumbers, self).SetText(newText)

    def FormatNumeric(self, otext, useGrouping = True, decimalPlaces = 0, leadingZeroes = 0):
        if not otext:
            return ''
        else:
            try:
                number = self.dataType(otext or 0)
            except ValueError:
                return otext

            return FormatNumeric(number, useGrouping=useGrouping, decimalPlaces=decimalPlaces, leadingZeroes=leadingZeroes)

    def SetValue(self, text, docallback = 1):
        if text == self.HYPHEN:
            text = self.minValue
        text = self.dataType(text) if text else text
        text = self.CheckBounds(text, allowEmpty=bool(self.hintText))
        super(BaseSingleLineEditNumbers, self).SetValue(text, docallback)

    def ShowNumericControls(self):
        if self.numericControlsCont:
            return
        self.numericControlsCont = Container(name='numericControlsCont', parent=self, align=uiconst.TORIGHT, idx=0, width=10, padding=(0, 1, 8, 1), opacity=0.75, state=uiconst.UI_HIDDEN if self.readonly else uiconst.UI_NORMAL)
        self.upButton = ButtonIcon(name='upButton', parent=self.numericControlsCont, align=uiconst.CENTER, pos=(0, -4, 9, 9), iconSize=7, texturePath='res:/UI/Texture/Shared/up.png', soundClick=uiconst.SOUND_VALUECHANGE_TICK, iconColor=self.arrowIconColor, glowColor=self.arrowIconGlowColor, iconClass=self.arrowIconClass, useThemeColor=self.arrowUseThemeColor, iconBlendMode=self.arrowIconBlendMode)
        self.upButton.OnMouseDown = self.OnNumericUpButtonMouseDown
        self.upButton.OnMouseUp = self.OnNumericUpButtonMouseUp
        self.downButton = ButtonIcon(name='downButton', parent=self.numericControlsCont, align=uiconst.CENTER, pos=(0, 4, 9, 9), iconSize=7, texturePath='res:/UI/Texture/Shared/down.png', soundClick=uiconst.SOUND_VALUECHANGE_TICK, iconColor=self.arrowIconColor, glowColor=self.arrowIconGlowColor, iconClass=self.arrowIconClass, useThemeColor=self.arrowUseThemeColor, iconBlendMode=self.arrowIconBlendMode)
        self.downButton.OnMouseDown = self.OnNumericDownButtonMouseDown
        self.downButton.OnMouseUp = self.OnNumericDownButtonMouseUp

    def OnNumericUpButtonMouseDown(self, *args):
        ButtonIcon.OnMouseDown(self.upButton, *args)
        self.updateNumericInputThread = start_tasklet(self.UpdateNumericInputThread, 1)

    def OnNumericDownButtonMouseDown(self, *args):
        ButtonIcon.OnMouseDown(self.downButton, *args)
        self.updateNumericInputThread = start_tasklet(self.UpdateNumericInputThread, -1)

    def KillNumericInputThread(self):
        if self.updateNumericInputThread:
            self.updateNumericInputThread.kill()
            self.updateNumericInputThread = None

    def OnNumericUpButtonMouseUp(self, *args):
        ButtonIcon.OnMouseUp(self.upButton, *args)
        self.KillNumericInputThread()

    def OnNumericDownButtonMouseUp(self, *args):
        ButtonIcon.OnMouseUp(self.downButton, *args)
        self.KillNumericInputThread()

    def UpdateNumericInputThread(self, diff):
        sleepTime = 500
        while uicore.uilib.leftbtn:
            self.ChangeNumericValue(diff)
            blue.synchro.SleepWallclock(sleepTime)
            sleepTime -= 0.5 * sleepTime
            sleepTime = max(10, sleepTime)

    def OnMouseWheel(self, *args):
        if self.readonly:
            return
        PlaySound(uiconst.SOUND_VALUECHANGE_TICK)
        if platform.system() == 'Darwin':
            self.ChangeNumericValue(uicore.uilib.dz / 120.0)
        else:
            self.ChangeNumericValue((uicore.uilib.dz / 120) ** 3)

    def ChangeNumericValue(self, val):
        self.BlinkButtons(val)
        self.ClampMinMaxValue(val)

    def GetValue(self, *args, **kwargs):
        if not self.text:
            return self.minValue or 0
        elif self.text == self.HYPHEN:
            return 0
        else:
            try:
                value = self.dataType(self.text)
            except ValueError:
                return 0

            return value

    def ValidateNegativeInput(self, text, caretIndex):
        newvalue = self.text[:caretIndex] + text + self.text[caretIndex:]
        if text == self.HYPHEN:
            if newvalue != self.HYPHEN:
                newvalue = self.FilterIllegalChars(newvalue)
                try:
                    self.dataType(newvalue)
                except ValueError:
                    sys.exc_clear()
                    raise ValueError

        elif abs(self.dataType(newvalue)) >= sys.maxsize:
            raise ValueError

    def BlinkButtons(self, val):
        if not self.numericControlsCont:
            return
        if val > 0:
            self.upButton.Blink(0.2)
        else:
            self.downButton.Blink(0.2)

    def ClampMinMaxValue(self, change = 0):
        current = 0
        try:
            current = self.dataType(self.text)
        except ValueError:
            sys.exc_clear()

        newText = repr(current + change)
        text = self.CheckBounds(newText)
        self.SetText(text)
        self.SendCaretToEnd()
        self.ClearSelection()
        self.OnTextChange()

    def GetMenu(self):
        m = super(BaseSingleLineEditNumbers, self).GetMenu()
        if self.displayHistory:
            m += [(MenuLabel('/Carbon/UI/Controls/Common/ClearHistory'), self.ClearHistory, (None,))]
        return m

    def OnKillFocus(self, *args):
        ret = self.CheckBounds(self.text, allowEmpty=bool(self.hintText), returnNoneIfOK=True)
        if ret is not None:
            if ret <= self.minValue:
                self.SetValue(self.minValue)
        super(BaseSingleLineEditNumbers, self).OnKillFocus(*args)
