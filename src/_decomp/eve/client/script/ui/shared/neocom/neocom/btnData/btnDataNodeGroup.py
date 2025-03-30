#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\btnData\btnDataNodeGroup.py
import localization
import utillib
from carbonui import uiconst
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNode import BtnDataNode
from eve.client.script.ui.shared.neocom.neocom.neocomGroupNamePopup import NeocomGroupNamePopup
from menu import MenuLabel
from signals import Signal

class BtnDataNodeGroup(BtnDataNode):
    __guid__ = 'neocom.BtnDataNodeGroup'

    def __init__(self, parent = None, children = None, iconPath = None, label = None, btnID = None, btnType = None, isRemovable = True, isDraggable = True, isOpen = False, isBlinking = False, labelAbbrev = None, wndCls = None, cmdName = None, **kw):
        self.on_name_changed = Signal('on_name_changed')
        BtnDataNode.__init__(self, parent, children, iconPath, label, btnID, btnType, isRemovable, isDraggable, isOpen, isBlinking, labelAbbrev, wndCls, cmdName, **kw)

    def GetMenu(self):
        if self.GetRootNode() == sm.GetService('neocom').GetEveMenuBtnDataRoot():
            return
        m = []
        if self.IsRemovable():
            m.append((MenuLabel('UI/Neocom/RemoveShortcut'), self.Remove))
            m.append((localization.GetByLabel('UI/Neocom/Edit'), self.EditGroup))
        return m

    def GetRawData(self):
        return utillib.KeyVal(btnType=self.btnType, id=self.id, iconPath=self.iconPath, children=self._GetRawChildren(), label=self.label, labelAbbrev=self.labelAbbrev)

    def EditGroup(self):
        wnd = NeocomGroupNamePopup.Open(groupName=self.label, groupAbbrev=self.labelAbbrev)
        ret = wnd.ShowModal()
        if ret in (uiconst.ID_CLOSE, uiconst.ID_CANCEL):
            return
        self.label = ret.label or localization.GetByLabel('UI/Neocom/ButtonGroup')
        self.labelAbbrev = ret.labelAbbrev
        self.Persist()
        self.on_name_changed()
