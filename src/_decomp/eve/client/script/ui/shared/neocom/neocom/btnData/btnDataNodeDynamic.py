#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\btnData\btnDataNodeDynamic.py
import localization
from carbonui.uicore import uicore
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNode import BtnDataNode

class BtnDataNodeDynamic(BtnDataNode):
    __guid__ = 'neocom.BtnDataNodeDynamic'
    persistChildren = False

    def GetDataList(self):
        return []

    def GetNodeFromData(self, data, parent):
        pass

    def _AddChild(self, child, idx = None):
        pass

    def CheckContinueBlinking(self):
        pass

    def _RemoveChild(self, btnData):
        pass

    def GetChildren(self):
        dataList = self.GetDataList()
        return self._GetChildren(dataList, self)

    def GetPanelEntryHeight(self):
        return 25

    def _GetChildren(self, dataList, parent = None):
        children = []
        entryHeight = self.GetPanelEntryHeight()
        maxEntries = uicore.desktop.height / entryHeight - 1
        for data in dataList[:maxEntries]:
            btnData = self.GetNodeFromData(data, parent)
            children.append(btnData)

        overflow = dataList[maxEntries:]
        if overflow:
            overflowBtnData = BtnDataNode(parent=parent, iconPath=neocomConst.ICONPATH_GROUP, label=localization.GetByLabel('UI/Neocom/OverflowButtonsLabel', numButtons=len(overflow)), btnType=neocomConst.BTNTYPE_GROUP, panelEntryHeight=entryHeight, isRemovable=False, isDraggable=False)
            children.append(overflowBtnData)
            self._GetChildren(dataList[maxEntries:], overflowBtnData)
        return children

    children = property(GetChildren)
