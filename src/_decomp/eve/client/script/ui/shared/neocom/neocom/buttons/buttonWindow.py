#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\buttonWindow.py
import uthread
from carbonui import const as uiconst, fontconst
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from eve.client.script.ui.shared.neocom.neocom.buttons.baseNeocomButton import BaseNeocomButton
from menu import MenuLabel

class ButtonWindow(BaseNeocomButton):
    default_name = 'ButtonWindow'

    def ApplyAttributes(self, attributes):
        super(ButtonWindow, self).ApplyAttributes(attributes)
        self.btnData.on_child_removed.connect(self._on_child_removed)

    def Close(self):
        super(ButtonWindow, self).Close()
        self.btnData.on_child_removed.disconnect(self._on_child_removed)

    def _on_child_removed(self, btnData):
        self.UpdateIcon()

    def OnClickCommand(self):
        if self.IsSingleWindow():
            uthread.new(self.GetWindow().ToggleMinimize)
        elif self.btnData.children:
            self.ToggleNeocomPanel()
        else:
            super(ButtonWindow, self).OnClickCommand()

    def IsSingleWindow(self):
        return len(self.btnData.children) == 1

    def GetWindow(self):
        if self.btnData.children:
            btnData = self.btnData.children[0]
            return btnData.wnd

    def GetAllWindows(self):
        wnds = []
        for btnData in self.btnData.children:
            wnds.append(btnData.wnd)

        return wnds

    def GetMenu(self):
        if self.IsSingleWindow():
            wnd = self.GetWindow()
            if wnd and wnd.GetMenu:
                menu = BaseNeocomButton.GetMenu(self)
                return wnd.GetMenu() + menu
        else:
            if self.btnData.children:
                for wnd in self.GetAllWindows():
                    if not wnd.IsKillable():
                        return None

                return [(MenuLabel('/Carbon/UI/Commands/CmdCloseAllWindows'), self.CloseAllWindows)]
            if self.btnData.btnType in neocomConst.COMMAND_BTNTYPES + (neocomConst.BTNTYPE_INVENTORY,):
                return BaseNeocomButton.GetMenu(self)

    def CloseAllWindows(self):
        for wnd in self.GetAllWindows():
            wnd.CloseByUser()

    def OnDragEnter(self, panelEntry, nodes):
        if sm.GetService('neocom').IsValidDropData(nodes):
            BaseNeocomButton.OnDragEnter(self, panelEntry, nodes)
        elif self.btnData.btnType == neocomConst.BTNTYPE_WINDOW:
            self.dropFrame.state = uiconst.UI_DISABLED
            self.OnMouseEnter()
            uthread.new(self.ShowPanelOnMouseHoverThread)

    def OnDragExit(self, *args):
        self.dropFrame.state = uiconst.UI_HIDDEN
        self.OnMouseExit()

    def OnDropData(self, source, nodes):
        if sm.GetService('neocom').IsValidDropData(nodes):
            index = self.btnData.parent.children.index(self.btnData)
            sm.GetService('neocom').OnBtnDataDropped(nodes[0], index)
        elif self.IsSingleWindow():
            wnd = self.GetWindow()
            if hasattr(wnd, 'OnDropData'):
                if wnd.OnDropData(source, nodes):
                    self.BlinkOnDrop()
        elif not self.GetAllWindows():
            wndCls = self.btnData.wndCls
            if wndCls and hasattr(wndCls, 'OnDropDataCls'):
                if wndCls.OnDropDataCls(source, nodes):
                    self.BlinkOnDrop()
        self.dropFrame.state = uiconst.UI_HIDDEN

    def BlinkOnDrop(self):
        self.BlinkOnce()

    def UpdateIcon(self):
        if self.iconLabelCont:
            self.iconLabelCont.Close()
        wnd = self.GetWindow()
        if not wnd:
            iconNum = self.btnData.iconPath
        elif self.IsSingleWindow():
            iconNum = wnd.iconNum
        else:
            iconNum = None
            wnds = self.GetAllWindows()
            for w in wnds:
                iconNum = w.GetNeocomGroupIcon()
                if iconNum is not None:
                    break

            self.ConstructIconLabelCont(wnds)
        self.SetTexturePath(iconNum or neocomConst.ICONPATH_DEFAULT)

    def ConstructIconLabelCont(self, wnds):
        self.iconLabelCont = Container(parent=self, align=uiconst.TOPRIGHT, pos=(1, 1, 13, 13), idx=0, bgColor=Color.GetGrayRGBA(0.7, 0.2))
        eveLabel.EveLabelMedium(parent=self.iconLabelCont, align=uiconst.CENTER, text=len(wnds))
