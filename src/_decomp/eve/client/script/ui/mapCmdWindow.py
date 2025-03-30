#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\mapCmdWindow.py
import localization
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button
from carbonui.control.window import Window

class MapCmdWindow(Window):
    __guid__ = 'form.MapCmdWindow'
    default_fixedWidth = 320
    default_state = uiconst.UI_NORMAL
    default_windowID = 'MapCmdWindow'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        cmdname = attributes.cmdname
        self.SetCaption(uicore.cmd.FuncToDesc(cmdname))
        self.MakeUnResizeable()
        self.mouseCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUp)
        self.keyCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.OnGlobalKeyUp)
        currShortcut = uicore.cmd.GetShortcutStringByFuncName(cmdname) or localization.GetByLabel('UI/Common/None')
        self._content = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, callback=self._OnContentResized)
        eveLabel.EveLabelMedium(parent=self._content, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, text=localization.GetByLabel('UI/Commands/EnterNewShortcutPrompt', currShortcut=currShortcut))
        Button(parent=ContainerAutoSize(parent=self._content, align=uiconst.TOTOP, padTop=16), align=uiconst.CENTER, label=localization.GetByLabel('UI/Common/Cancel'), func=self.Close, args=None)

    def _OnContentResized(self):
        content_height = self._content.height + self._content.padTop + self._content.padBottom
        _, self.height = self.GetWindowSizeForContentSize(height=content_height)

    def OnGlobalMouseUp(self, window, msgID, param):
        btnNum, type = param
        btnMap = {uiconst.MOUSEMIDDLE: uiconst.VK_MBUTTON,
         uiconst.MOUSEXBUTTON1: uiconst.VK_XBUTTON1,
         uiconst.MOUSEXBUTTON2: uiconst.VK_XBUTTON2}
        if btnNum in btnMap:
            self.Apply(btnMap[btnNum])

    def OnGlobalKeyUp(self, window, msgID, param):
        vkey, type = param
        self.Apply(vkey)

    def Confirm(self, *args):
        pass

    def Apply(self, vkey):
        shortcut = []
        for modKey in uiconst.MODKEYS:
            if uicore.uilib.Key(modKey) and modKey != vkey:
                shortcut.append(modKey)

        shortcut.append(vkey)
        self.result = {'shortcut': tuple(shortcut)}
        self.SetModalResult(1)

    def _OnClose(self, *args):
        uicore.event.UnregisterForTriuiEvents(self.mouseCookie)
        uicore.event.UnregisterForTriuiEvents(self.keyCookie)
