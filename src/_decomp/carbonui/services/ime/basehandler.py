#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\services\ime\basehandler.py
import uthread
import blue
import inputmethod
from carbonui.control.singlelineedits.baseSingleLineEdit import BaseSingleLineEdit
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.control.editPlainText import EditPlainTextCore
from carbonui.control.label import LabelCore
import carbonui.const as uiconst
from carbonui.uicore import uicore

class BaseImeHandler(object):

    def __init__(self):
        self.insertOnType = False
        self.currentLanguageMac = None
        self.compositionWindow = None
        self.compositionWindowParent = None
        self.currentFocusWidget = None
        self.allowedWidgetTypes = (EditPlainTextCore, BaseSingleLineEdit)
        self.ime = inputmethod.Ime()
        self._ResetCompositionString()
        uthread.new(self._PositionWindowTasklet)

    def __del__(self):
        self._HideCompositionWindow()

    def IsVisible(self):
        return self.compositionWindow and self.compositionWindow.state != uiconst.UI_HIDDEN

    def SetFocus(self, widget):
        if self.currentFocusWidget:
            self.KillFocus(self.currentFocusWidget)
        self.currentFocusWidget = widget if self._IsImeWidget(widget) else None
        self._SetImeState(True)

    def KillFocus(self, widget):
        if self.currentFocusWidget is not widget:
            return
        self._FinalizeCompositionString()
        self._HideCompositionWindow()
        self.currentFocusWidget = None
        self._SetImeState(False)

    def _SetImeState(self, enable):
        enable = enable is True and self.currentFocusWidget is not None
        return enable

    def _IsImeWidget(self, widget):
        return isinstance(widget, self.allowedWidgetTypes)

    def _TruncateCompositionString(self, iNewStrLen = 0):
        if not self._CheckFocusWidget() or not self.insertOnType:
            return
        cc = len(self.compositionString)
        if iNewStrLen != 0 and iNewStrLen < cc:
            return
        _, char_handler = self.currentFocusWidget.FindEventHandler('OnChar')
        _, key_down_handler = self.currentFocusWidget.FindEventHandler('OnKeyDown')
        for i in xrange(cc - self.compositionCaretPosition):
            if key_down_handler:
                key_down_handler(uiconst.VK_RIGHT, 0)

        for i in xrange(cc):
            if char_handler:
                char_handler(uiconst.VK_BACK, 0)
            if key_down_handler:
                key_down_handler(uiconst.VK_BACK, 0)

    def _ResetCompositionString(self):
        self.compositionCaretPosition = 0
        self.compositionCaretWidth = 0
        self.compositionString = ''

    def _FinalizeCompositionString(self):
        if not self.insertOnType:
            self._SendCompositionString()
        self._ResetCompositionString()

    def _SendCompositionString(self):
        if not self._CheckFocusWidget():
            return
        _, handler = self.currentFocusWidget.FindEventHandler('OnChar')
        if handler:
            for char in self.compositionString:
                handler(ord(char), 0)

    def _ShowCompositionWindow(self):
        if not self._CheckFocusWidget():
            return
        fontsize = 14
        if hasattr(self.currentFocusWidget, 'GetFontParams'):
            fontsize = max(fontsize, self.currentFocusWidget.GetFontParams().fontsize)
        if not self.compositionWindow:
            self.compositionWindow = Container(name='IME', parent=uicore.desktop, align=uiconst.TOPLEFT, idx=0)
            if self.compositionCaretWidth == 0:
                self.compositionWindowCursor = Fill(parent=self.compositionWindow, align=uiconst.TOPLEFT, width=1, top=2, color=(1.0, 1.0, 1.0, 0.75))
            self.compositionWindowText = LabelCore(parent=self.compositionWindow, fontsize=fontsize, state=uiconst.UI_DISABLED, left=3, top=1)
            Frame(parent=self.compositionWindow, color=(1, 1, 1, 0.3))
            Fill(parent=self.compositionWindow, color=(0.0, 0.0, 0.0, 1.0))
        self.compositionWindowText.fontsize = fontsize
        self.compositionWindowText.text = self.compositionString
        self.compositionWindow.state = uiconst.UI_HIDDEN if self.insertOnType else uiconst.UI_DISABLED
        self.compositionWindow.width = self.compositionWindowText.textwidth + self.compositionWindowText.left * 2
        self.compositionWindow.height = self.compositionWindowText.textheight + self.compositionWindowText.top * 2
        if self.compositionCaretWidth == 0:
            self.compositionWindowCursor.height = self.compositionWindow.height - self.compositionWindowCursor.top * 2
            self.compositionWindowCursor.width = 1
            self.compositionWindowCursor.align = uiconst.TOPLEFT
        else:
            self.compositionWindowCursor.height = 2
            self.compositionWindowCursor.align = uiconst.BOTTOMLEFT
            self.compositionWindowCursor.width = self._GetCompositionCursorPosition(self.compositionCaretWidth)
        self.compositionWindowParent = self.currentFocusWidget
        self.compositionWindowCursor.left = self.compositionWindowText.left + self._GetCompositionCursorPosition(self.compositionCaretPosition)
        self._PositionCompositionWindow()

    def _CheckFocusWidget(self):
        if not self.currentFocusWidget or self.currentFocusWidget.destroyed:
            self._HideCompositionWindow()
            return False
        return True

    def _PositionWindowTasklet(self):
        while getattr(uicore, 'uilib', None):
            sleeptime = 5 if uicore.uilib.leftbtn else 250
            if self.compositionWindow and self.compositionWindow.state == uiconst.UI_DISABLED:
                self._PositionCompositionWindow()
            blue.pyos.synchro.SleepWallclock(sleeptime)

    def _PositionCompositionWindow(self):
        edit = self.compositionWindowParent
        if not edit or edit.destroyed:
            return
        if isinstance(edit, (EditPlainTextCore,)):
            entry = edit.GetActiveNode()
            if not entry.panel:
                return
            panel = entry.panel
            y = panel.absoluteTop - self.compositionWindow.height + 2
            x = panel.absoluteLeft + panel.GetCursorOffset() - 1
        elif isinstance(edit, BaseSingleLineEdit):
            x, y = edit.get_absolute_caret_position()
            y -= self.compositionWindow.height
        elif hasattr(edit, 'get_ime_position'):
            x, y = edit.get_ime_position(self.compositionWindow.height, self.compositionWindow.width)
        else:
            return
        self.compositionWindow.left = min(uicore.desktop.width - self.compositionWindow.width - 6, x)
        self.compositionWindow.top = y

    def _HideCompositionWindow(self):
        if self.compositionWindow:
            self.compositionWindow.state = uiconst.UI_HIDDEN
            self._ResetCompositionString()

    def _GetCompositionCursorPosition(self, pos):
        if not pos or not self.compositionString:
            return 0
        if getattr(self, 'compositionWindowText', None):
            textWidth, textHeight = self.compositionWindowText.MeasureTextSize(self.compositionString[:pos], fontsize=self.compositionWindowText.fontsize)
        else:
            textWidth, textHeight = LabelCore.MeasureTextSize(self.compositionString[:pos])
        return textWidth
