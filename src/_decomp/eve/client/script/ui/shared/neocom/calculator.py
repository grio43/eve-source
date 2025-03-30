#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\calculator.py
import sys
import eveLocalization
import localization
from carbonui import fontconst, uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.uicore import uicore
from carbonui.control.window import Window
from eve.client.script.ui.util import uix
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from menu import MenuLabel
MINWIDTH = 240

class Calculator(Window):
    __guid__ = 'form.Calculator'
    default_windowID = 'calculator'
    default_width = MINWIDTH
    default_height = 160
    default_left = 0
    default_top = 0
    default_captionLabelPath = 'UI/Accessories/Calculator/Calculator'
    default_iconNum = 'res:/ui/Texture/WindowIcons/calculator.png'
    default_scope = uiconst.SCOPE_INGAME

    def ApplyAttributes(self, attributes):
        self.mainCont = None
        self.buttonGrid = None
        self.decimalSign = eveLocalization.GetDecimalSeparator(localization.SYSTEM_LANGUAGE)
        self.digitSign = eveLocalization.GetThousandSeparator(localization.SYSTEM_LANGUAGE)
        self.PopulateKnownKeys()
        super(Calculator, self).ApplyAttributes(attributes)
        self.MakeUnResizeable()
        self.Layout()

    def Layout(self):
        self.mainCont = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, callback=self._OnMainContResized)
        self.sr.inpt = inpt = SingleLineEditText(name='inpt', parent=ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, top=8, padLeft=8, padRight=8), align=uiconst.TOTOP, top=0, height=32, fontsize=fontconst.EVE_LARGE_FONTSIZE)
        inpt.SetHistoryVisibility(0)
        inpt.OnChar = self.OnCharInput
        inpt.Paste = self.OnInputPasted
        self.SetInpt('0')
        hist = settings.public.ui.Get('CalculatorHistory', [])
        if hist:
            ops = [ (v, v) for v in hist ]
        else:
            ops = [('0', '0')]
        inpt.LoadCombo('urlcombo', ops, self.OnComboChange)
        memoryCont = LayoutGrid(parent=ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, top=8, left=8, padRight=8), align=uiconst.CENTER, columns=3, cellSpacing=(8, 8))
        self.buttonGrid = grid = LayoutGrid(parent=ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, top=8, left=8, padRight=8, padBottom=8), align=uiconst.TOPLEFT, columns=7, cellSpacing=(4, 4))
        buttons = [('7', localization.formatters.FormatNumeric(7)),
         ('8', localization.formatters.FormatNumeric(8)),
         ('9', localization.formatters.FormatNumeric(9)),
         ('divide', localization.GetByLabel('UI/Accessories/Calculator/DivideSymbol')),
         ('clear', localization.GetByLabel('UI/Accessories/Calculator/ClearSymbol')),
         ('clearall', localization.GetByLabel('UI/Accessories/Calculator/ClearAllSymbol')),
         ('4', localization.formatters.FormatNumeric(4)),
         ('5', localization.formatters.FormatNumeric(5)),
         ('6', localization.formatters.FormatNumeric(6)),
         ('times', localization.GetByLabel('UI/Accessories/Calculator/MultiplySymbol')),
         ('bo', localization.GetByLabel('UI/Accessories/Calculator/BracketOpenSymbol')),
         ('bc', localization.GetByLabel('UI/Accessories/Calculator/BracketCloseSymbol')),
         ('1', localization.formatters.FormatNumeric(1)),
         ('2', localization.formatters.FormatNumeric(2)),
         ('3', localization.formatters.FormatNumeric(3)),
         ('minus', localization.GetByLabel('UI/Accessories/Calculator/SubtractSymbol')),
         ('percent', localization.GetByLabel('UI/Accessories/Calculator/PercentSymbol')),
         ('square', localization.GetByLabel('UI/Accessories/Calculator/SquareSymbol')),
         ('0', localization.formatters.FormatNumeric(0)),
         ('dot', self.decimalSign),
         ('equal', localization.GetByLabel('UI/Accessories/Calculator/EqualsSymbol')),
         ('plus', localization.GetByLabel('UI/Accessories/Calculator/AddSymbol')),
         ('plusminus', localization.GetByLabel('UI/Accessories/Calculator/PlusMinusSymbol')),
         ('root', u'\u221a\xaf')]
        for i, (arg, label) in enumerate(buttons):
            if i % 6 == 4:
                Container(parent=grid, align=uiconst.TOPLEFT, width=8)
            Button(name=arg, parent=grid, align=uiconst.TOPLEFT, fixedwidth=32, fixedheight=32, label=label, fontsize=fontconst.EVE_MEDIUM_FONTSIZE, func=lambda c = arg: self.OnBtnClick(c), args=())

        for i in xrange(1, 7):
            MemorySlot(parent=memoryCont, align=uiconst.TOPLEFT, index=i, getInputValue=self._GetInputValue, setInputValue=lambda value: self.SetInpt(str(value).replace('.', self.decimalSign), False))

        self.newNumber = True
        self._stack = []
        self.opStack = []
        self.lastOp = 0
        uicore.registry.SetFocus(self.sr.inpt)

    def _GetInputValue(self):
        if self.sr.inpt.GetValue() == '':
            self.SetInpt('0')
        text = self.sr.inpt.GetValue()
        return float(text.replace(self.decimalSign, '.'))

    def _OnMainContResized(self):
        if self.buttonGrid is None:
            return
        windowMain = self.GetMainArea()
        totalHeight = self.header_height + windowMain.padTop + windowMain.padBottom + self.mainCont.height
        totalWidth = windowMain.padLeft + windowMain.padRight + self.buttonGrid.width + self.buttonGrid.parent.left + self.buttonGrid.parent.padRight
        self.SetMinSize(size=(totalWidth, totalHeight), refresh=True)

    def SetInpt(self, value, new = True):
        self.sr.inpt.SetValue(value)
        self.newNumber = new

    def OnComboChange(self, combo, header, value, *args):
        self.SetInpt(value, False)

    def OnInputPasted(self, paste, deleteStart = None, deleteEnd = None, forceFocus = False):
        self.SetInpt('0')
        for char in paste:
            self.OnCharInput(ord(char))

    def OnCharInput(self, char, flag = None):
        _char = char
        text = self.sr.inpt.GetText()
        try:
            _char = unichr(char)
            if len(_char) == 1 and _char in '0123456789':
                if text == '0' or self.newNumber:
                    self.sr.inpt.text = ''
                self.sr.inpt.Insert(char)
                self.newNumber = False
                return True
        except:
            sys.exc_clear()

        if _char in self.knownkeys.keys():
            _char = self.knownkeys[_char]
        if _char == 'dot' or type(char) == int and unichr(char) == u'.':
            if self.decimalSign not in text or self.newNumber:
                if text == '' or self.newNumber:
                    self.sr.inpt.text = '0'
                    self.sr.inpt.Insert(ord(self.decimalSign))
                    self.newNumber = False
                    return True
                self.sr.inpt.Insert(ord(self.decimalSign))
                self.newNumber = False
            else:
                return True
        if _char == 'plusminus':
            if text.startswith('-'):
                text = text[1:]
            else:
                text = '-' + text
            self.SetInpt(text, False)
            return True
        if _char == 'clearall':
            self._stack = []
            self.opStack = []
        if _char in ('\x08', 'clear', 'clearall'):
            self.SetInpt('0')
            return True
        if _char in self.prio.keys():
            self.Operator(_char, text)
            if _char == 'equal':
                hist = settings.public.ui.Get('CalculatorHistory', [])
                hist.insert(0, text)
                if len(hist) > 20:
                    hist.pop()
                settings.public.ui.Set('CalculatorHistory', hist)
                ops = [ (v, v) for v in hist ]
                self.sr.inpt.LoadCombo('urlcombo', ops, self.OnComboChange, setvalue=text)
        return True

    def OnBtnClick(self, arg):
        try:
            arg = ord(arg)
        except Exception:
            sys.exc_clear()

        self.OnCharInput(arg)

    def CheckOperator(self):
        if str(self._stack[-1]) in self.prio.keys():
            return True
        return False

    def Calc(self):
        if len(self._stack) > 0 and self.CheckOperator():
            op = self._stack.pop()
            if op in ('equal', 'bo', 'bc'):
                self.Calc()
            if op == 'plus':
                self.Calc()
                op1 = self._stack.pop()
                self.Calc()
                op2 = self._stack.pop()
                self._stack.append(op2 + op1)
            if op == 'minus':
                self.Calc()
                op1 = self._stack.pop()
                self.Calc()
                op2 = self._stack.pop()
                self._stack.append(op2 - op1)
            if op == 'times':
                self.Calc()
                op1 = self._stack.pop()
                self.Calc()
                op2 = self._stack.pop()
                self._stack.append(op2 * op1)
            if op == 'divide':
                self.Calc()
                op1 = self._stack.pop()
                self.Calc()
                op2 = self._stack.pop()
                try:
                    self._stack.append(op2 / op1)
                except ZeroDivisionError as e:
                    sys.exc_clear()
                    eve.Message('uiwarning03')
                    self._stack.append(0.0)

            if op == 'square':
                self.Calc()
                op1 = self._stack.pop()
                try:
                    self._stack.append(op1 ** 2.0)
                except OverflowError as e:
                    sys.exc_clear()
                    eve.Message('uiwarning03')
                    self._stack.append(0.0)

            if op == 'root':
                self.Calc()
                op1 = self._stack.pop()
                try:
                    self._stack.append(op1 ** 0.5)
                except ValueError as e:
                    sys.exc_clear()
                    eve.Message('uiwarning03')
                    self._stack.append(0.0)

            if op == 'percent':
                self.Calc()
                op1 = self._stack.pop()
                if len(self._stack):
                    op2 = self._stack[-1]
                else:
                    eve.Message('uiwarning03')
                    op2 = 0.0
                self._stack.append(op2 * op1 / 100.0)

    def Operator(self, op, number):
        if not self.newNumber or len(self._stack) == 0:
            self._stack.append(float(number.replace(self.decimalSign, '.')))
        elif self.lastOp in ('plus', 'minus', 'times', 'divide') and op != 'bo':
            self.opStack[-1] = op
            return
        if op != 'bo' and (len(self.opStack) == 0 or self.prio[op] <= self.prio[self.opStack[-1]]):
            while len(self.opStack) > 0 and self.prio[op] <= self.prio[self.opStack[-1]]:
                self._stack.append(self.opStack.pop())

        if op == 'bc':
            while len(self.opStack) > 0 and self.opStack[-1] != 'bo':
                self._stack.append(self.opStack.pop())

            if len(self.opStack):
                self.opStack.pop()
        if op in ('percent', 'root', 'square', 'equal', 'bc'):
            self._stack.append(op)
        else:
            self.opStack.append(op)
        self.Calc()
        number = '%.14G' % self._stack[-1]
        self.SetInpt(number.replace('.', self.decimalSign))
        self.lastOp = op

    def PopulateKnownKeys(self):
        self.knownkeys = {'+': 'plus',
         '-': 'minus',
         '*': 'times',
         '/': 'divide',
         self.decimalSign: 'dot',
         '=': 'equal',
         'r': 'root',
         's': 'square',
         'p': 'percent',
         'm': 'plusminus',
         '(': 'bo',
         ')': 'bc',
         'C': 'clearall',
         '\r': 'equal'}

    prio = {'plus': 3,
     'minus': 3,
     'times': 4,
     'divide': 4,
     'square': 5,
     'root': 5,
     'bo': 1,
     'bc': 6,
     'percent': 4,
     'equal': 0}


class MemorySlot(LayoutGrid):

    def __init__(self, index, getInputValue, setInputValue, parent = None, align = uiconst.TOPLEFT):
        self._index = index
        self._getInputValue = getInputValue
        self._setInputValue = setInputValue
        super(MemorySlot, self).__init__(parent=parent, align=align, colums=2)
        button = Button(parent=self, align=uiconst.TOPLEFT, label=localization.GetByLabel('UI/Accessories/Calculator/AbbreviatedMemory', index=self._index), func=self._OnButtonClick, args=())
        button.GetHint = self._GetButtonHint
        menu = ButtonIcon(parent=self, align=uiconst.CENTER, width=16, height=16, texturePath='res:/UI/Texture/Icons/38_16_190.png', iconSize=16)
        menu.expandOnLeft = True
        menu.GetMenu = self._GetMenuOptions

    def _OnButtonClick(self):
        stored = GetMemoryAt(self._index)
        if stored is not None:
            self._setInputValue(stored)

    def _GetButtonHint(self):
        stored = GetMemoryAt(self._index)
        if stored is not None:
            return '%s:<br>%.14G' % (GetMemoryNameAt(self._index), stored)
        else:
            return localization.GetByLabel('UI/Accessories/Calculator/EmptyBank', label=GetMemoryNameAt(self._index), empty=localization.GetByLabel('UI/Accessories/Calculator/Empty'))

    def _GetMenuOptions(self):
        m = []
        m.append((MenuLabel('UI/Accessories/Calculator/Set'), self._Set))
        stored = GetMemoryAt(self._index)
        if stored is not None:
            m.extend([(MenuLabel('UI/Accessories/Calculator/Add'), self._Add), (MenuLabel('UI/Accessories/Calculator/Subtract'), self._Sub), (MenuLabel('UI/Accessories/Calculator/Clear'), self._Clear)])
        m.append((MenuLabel('UI/Accessories/Calculator/Annotate'), self._Rename))
        return m

    def _Set(self):
        SetMemoryAt(self._index, self._getInputValue())

    def _Add(self):
        current = GetMemoryAt(self._index, default=0.0)
        value = self._getInputValue()
        SetMemoryAt(self._index, current + value)

    def _Sub(self):
        current = GetMemoryAt(self._index, default=0.0)
        value = self._getInputValue()
        SetMemoryAt(self._index, current - value)

    def _Clear(self):
        SetMemoryAt(self._index, None)

    def _Rename(self):
        retval = uix.HybridWnd(caption=localization.GetByLabel('UI/Accessories/Calculator/Annotate'), windowID='calculatorAnnotate', icon=uiconst.QUESTION, minW=300, minH=100, format=[{'type': 'edit',
          'setvalue': GetMemoryNameAt(self._index),
          'labelwidth': 48,
          'label': localization.GetByLabel('UI/Accessories/Calculator/Name'),
          'key': 'name',
          'maxlength': 16,
          'setfocus': 1}])
        if retval:
            SetMemoryNameAt(self._index, retval['name'])


def GetMemoryAt(index, default = None):
    return settings.public.ui.Get('CalculatorMem%s' % index, default)


def SetMemoryAt(index, value):
    settings.public.ui.Set('CalculatorMem%s' % index, value)


def GetMemoryNameAt(index):
    return settings.public.ui.Get('CalculatorMem%sName' % index, localization.GetByLabel('UI/Accessories/Calculator/Memory', index=index))


def SetMemoryNameAt(index, name):
    settings.public.ui.Set('CalculatorMem%sName' % index, name)
