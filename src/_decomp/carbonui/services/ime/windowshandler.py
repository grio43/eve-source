#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\services\ime\windowshandler.py
import uthread
import trinity
from carbonui.services.ime.basehandler import BaseImeHandler
import carbonui.const as uiconst
from carbonui.uicore import uicore
from windowsutilities import windowsEvents
GCS_COMPSTR = 8
GCS_CURSORPOS = 128
GCS_RESULTSTR = 2048
NI_CLOSECANDIDATE = 17
NI_COMPOSITIONSTR = 21
CPS_CANCEL = 4
LANG_KOREAN = 18

class WindowsImeHandler(BaseImeHandler):

    def __init__(self):
        super(WindowsImeHandler, self).__init__()
        self.currentLanguage = None
        self._otherMessageProc = trinity.app.onWindowsMessage
        self._otherFilter = trinity.app.GetWindowsMessageFilter()
        messages = [windowsEvents.WM_ACTIVATEAPP,
         windowsEvents.WM_INPUTLANGCHANGE,
         windowsEvents.WM_IME_SETCONTEXT,
         windowsEvents.WM_IME_STARTCOMPOSITION,
         windowsEvents.WM_IME_COMPOSITION,
         windowsEvents.WM_IME_ENDCOMPOSITION]
        trinity.app.onWindowsMessage = self._OnWindowsMessage
        trinity.app.SetWindowsMessageFilter(self._otherFilter[0], self._otherFilter[1] + messages)
        self.ime.SetHWND(trinity.app.GetHwndAsLong())
        self._SetLanguage(self.ime.GetKeyboardLayout())

    def __del__(self):
        super(WindowsImeHandler, self).__del__()
        trinity.app.onWindowsMessage = self._otherMessageProc
        trinity.app.SetWindowsMessageFilter(*self._otherFilter)

    def _SetImeState(self, enable):
        really_enable = super(WindowsImeHandler, self)._SetImeState(enable)
        self.ime.AssociateContext(really_enable)

    def _OnWindowsMessage(self, msg, wParam, lParam):
        with uthread.BlockTrapSection():
            if msg == windowsEvents.WM_ACTIVATEAPP:
                returnValue = self._OnActivateApp(wParam, lParam)
            elif msg == windowsEvents.WM_INPUTLANGCHANGE:
                returnValue = self._OnLanguageChange(wParam, lParam)
            elif msg == windowsEvents.WM_IME_SETCONTEXT:
                returnValue = self._OnSetContext(wParam, lParam)
            elif msg == windowsEvents.WM_IME_STARTCOMPOSITION:
                returnValue = self._OnStartComposition(wParam, lParam)
            elif msg == windowsEvents.WM_IME_COMPOSITION:
                returnValue = self._OnComposition(wParam, lParam)
            elif msg == windowsEvents.WM_IME_ENDCOMPOSITION:
                returnValue = self._OnEndComposition(wParam, lParam)
            else:
                if self._otherMessageProc:
                    return self._otherMessageProc(msg, wParam, lParam)
                returnValue = None
        if returnValue is None:
            return (0, False)
        else:
            return (returnValue, True)

    def _OnActivateApp(self, wp, lp):
        self._SetImeState(wp)
        return True

    def _OnLanguageChange(self, wp, lp):
        self.ime.SetHWND(trinity.app.GetHwndAsLong())
        self._SetLanguage(lp)
        return True

    def _OnSetContext(self, wp, lp):
        return True

    def _OnStartComposition(self, wp, lp):
        self._ResetCompositionString()
        return True

    def _OnComposition(self, wp, lp):
        if lp & GCS_CURSORPOS != 0:
            self.compositionCaretPosition = max(0, self.ime.GetCursorPos())
        if lp & GCS_RESULTSTR != 0:
            result = self.ime.GetCompositionString(GCS_RESULTSTR)
            self._TruncateCompositionString(len(result))
            self.compositionString = result
            self._SendCompositionString()
            self._ResetCompositionString()
            self._ShowCompositionWindow()
        if lp & GCS_COMPSTR != 0:
            result = self.ime.GetCompositionString(GCS_COMPSTR)
            self._TruncateCompositionString(len(result))
            self.compositionString = result
            if self._CheckFocusWidget() and self.insertOnType:
                self._SendCompositionString()
                nCount = len(self.compositionString) - self.compositionCaretPosition
                _, handler = self.currentFocusWidget.FindEventHandler('OnKeyDown')
                if handler:
                    for i in xrange(nCount):
                        handler(uiconst.VK_LEFT, 0)

            self._ShowCompositionWindow()
        return True

    def _OnEndComposition(self, wp, lp):
        if uicore.uilib.Key(uiconst.VK_RETURN):
            uicore.registry.BlockConfirm()
        self._TruncateCompositionString()
        self._ResetCompositionString()
        self._HideCompositionWindow()
        return True

    def _SplitLangIdentifier(self, code):
        code = code & 2147483647
        if code & 1073676288:
            code = (code & 1073676288) >> 16
        primaryLanguage = code & 1023
        subLanguage = (code & 64512) >> 10
        return (primaryLanguage, subLanguage)

    def _SetLanguage(self, code):
        self.currentLanguage, _ = self._SplitLangIdentifier(code)
        self.insertOnType = self.currentLanguage == LANG_KOREAN

    def _FinalizeCompositionString(self):
        super(WindowsImeHandler, self)._FinalizeCompositionString()
        self._ImmNotifyIME(NI_COMPOSITIONSTR, CPS_CANCEL, 0)
        self._ImmNotifyIME(NI_CLOSECANDIDATE, 0, 0)

    def _ImmNotifyIME(self, action, index, value):
        self.ime.NotifyIME(action, index, value)

    def _SimulateHotKey(self, hotkey):
        return self.ime.SimulateHotKey(hotkey)

    def _GetOpenStatus(self):
        return self.ime.GetOpenStatus()

    def _SetOpenStatus(self, open):
        return self.ime.SetOpenStatus(open)
