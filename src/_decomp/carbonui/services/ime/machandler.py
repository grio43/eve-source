#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\services\ime\machandler.py
from carbonui.services.ime.basehandler import BaseImeHandler
import trinity
NS_NOT_FOUND = 9223372036854775807L
EMPTY_RANGE = (NS_NOT_FOUND, 0)

class MacImeHandler(BaseImeHandler):

    def __init__(self):
        super(MacImeHandler, self).__init__()
        self._markedRange = EMPTY_RANGE
        self._selectedRange = EMPTY_RANGE
        trinity.app.onInsertTextIME_MacOS = self._onInsertTextIME_MacOS
        trinity.app.onSetMarkedTextIME_MacOS = self._onSetMarkedTextIME_MacOS
        trinity.app.onKeyboardLayoutChange_MacOS = self._onKeyboardLayoutChange_MacOS
        self.currentLanguageMac = self.ime.GetKeyboardLayout()

    def __del__(self):
        super(MacImeHandler, self).__del__()
        trinity.app.onInsertTextIME_MacOS = None
        trinity.app.onSetMarkedTextIME_MacOS = None
        trinity.app.onKeyboardLayoutChange_MacOS = None
        self._HideCompositionWindow()

    def _IsCurrentLayoutKorean(self):
        return self.currentLanguageMac.startswith('com.apple.inputmethod.Korean')

    def _onKeyboardLayoutChange_MacOS(self, *args):
        layout = self.ime.GetKeyboardLayout()
        if self.currentLanguageMac != layout:
            self.currentLanguageMac = layout
            if self._IsCurrentLayoutKorean():
                self.insertOnType = True
            else:
                self.insertOnType = False
            self._ResetCompositionString()
            if trinity.app.imeState_MacOS != trinity.Tr2ImeState_MacOS.DISABLED:
                trinity.app.imeState_MacOS = trinity.Tr2ImeState_MacOS.READY

    def _SetImeState(self, enable):
        enable = super(MacImeHandler, self)._SetImeState(enable)
        trinity.app.imeState_MacOS = trinity.Tr2ImeState_MacOS.READY if enable else trinity.Tr2ImeState_MacOS.DISABLED

    def _onInsertTextIME_MacOS(self, string):
        if trinity.app.imeState_MacOS == trinity.Tr2ImeState_MacOS.DISABLED:
            return
        if trinity.app.imeState_MacOS == trinity.Tr2ImeState_MacOS.BLOCKING:
            trinity.app.imeState_MacOS = trinity.Tr2ImeState_MacOS.READY
        self._TruncateCompositionString(len(self.compositionString))
        self.compositionString = string
        self._SendCompositionString()
        self._HideCompositionWindow()
        self._ResetCompositionString()

    def _onSetMarkedTextIME_MacOS(self, string, selectedLocation, selectedLength):
        if trinity.app.imeState_MacOS == trinity.Tr2ImeState_MacOS.DISABLED:
            return
        self._TruncateCompositionString(len(string))
        self.compositionCaretPosition = selectedLocation
        self.compositionCaretWidth = selectedLength
        if len(string) == 0:
            trinity.app.imeState_MacOS = trinity.Tr2ImeState_MacOS.READY
            self._HideCompositionWindow()
        else:
            trinity.app.imeState_MacOS = trinity.Tr2ImeState_MacOS.BLOCKING
            self.compositionString = string
            if self._CheckFocusWidget() and self.insertOnType:
                self._SendCompositionString()
            self._ShowCompositionWindow()
        if trinity.mainWindow.onChar:
            trinity.mainWindow.onChar(0, 0, True)

    def _SendCompositionString(self):
        if trinity.mainWindow.onChar:
            for char in self.compositionString:
                trinity.mainWindow.onChar(ord(char), 0, False)
