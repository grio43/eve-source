#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\btnData\btnDataNodeRoot.py
import localization
import uthread
from carbonui import uiconst
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNode import BtnDataNode
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNodeGroup import BtnDataNodeGroup
from eve.client.script.ui.shared.neocom.neocom.neocomConst import NOTPERSISTED_BTNTYPES
from eve.client.script.ui.shared.neocom.neocom.neocomGroupNamePopup import NeocomGroupNamePopup

class BtnDataNodeRoot(BtnDataNode):
    __guid__ = 'neocom.BtnDataNodeRoot'

    def __init__(self, parent = None, children = None, iconPath = None, label = None, btnID = None, btnType = None, isRemovable = True, isDraggable = True, isOpen = False, isBlinking = False, labelAbbrev = None, wndCls = None, cmdName = None, isTopLevel = True, **kw):
        self._persistThread = None
        self.isTopLevel = isTopLevel
        BtnDataNode.__init__(self, parent, children, iconPath, label, btnID, btnType, isRemovable, isDraggable, isOpen, isBlinking, labelAbbrev, wndCls, cmdName, **kw)

    def __repr__(self):
        return '<BtnDataNodeRoot: %s children>' % len(self._children)

    def Persist(self):
        if not self.IsPersistant():
            return
        if not self._persistThread:
            self._persistThread = uthread.new(self._Persist)

    def _Persist(self):
        if self.persistChildren:
            savedData = []
            for btnData in self._children:
                if btnData.btnType not in NOTPERSISTED_BTNTYPES:
                    savedData.append(btnData.GetRawData())

            settingsKey = '%sButtonRawData' % self.id
            settings.char.ui.Set(settingsKey, savedData)
        self._persistThread = None

    def IsTopLevel(self):
        return self.isTopLevel

    def GetRootNode(self):
        return self

    def IsDescendantOf(self, btnData):
        return False

    def _IsDescendantOf(self, btnData):
        return btnData == self

    def AddNewGroup(self):
        wnd = NeocomGroupNamePopup.Open()
        ret = wnd.ShowModal()
        if ret in (uiconst.ID_CLOSE, uiconst.ID_CANCEL):
            return
        BtnDataNodeGroup(parent=self, children=[], iconPath=neocomConst.ICONPATH_GROUP, label=ret.label or localization.GetByLabel('UI/Neocom/ButtonGroup'), btnID='group_%s' % ret.label, btnType=neocomConst.BTNTYPE_GROUP, labelAbbrev=ret.labelAbbrev)

    def IsValidDropData(self, btnData):
        if not isinstance(btnData, BtnDataNode):
            try:
                btnData = btnData[0]
                if not isinstance(btnData, BtnDataNode):
                    return False
            except Exception:
                return False

        if btnData.GetRootNode() != self:
            if btnData.btnType == neocomConst.BTNTYPE_GROUP:
                if self.GetBtnDataByTypeAndID(btnData.id, neocomConst.BTNTYPE_GROUP, recursive=True):
                    return False
            else:
                foundBtnData = self.GetBtnDataByWndCls(btnData.wndCls, recursive=True)
                if foundBtnData and foundBtnData.btnType != neocomConst.BTNTYPE_WINDOW:
                    return False
        return True
