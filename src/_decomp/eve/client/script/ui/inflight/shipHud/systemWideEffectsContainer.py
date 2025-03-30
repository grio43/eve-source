#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipHud\systemWideEffectsContainer.py
from carbonui import const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.inflight.shipHud.systemWideEffectButton import SystemWideEffectSlotParent
from eve.client.script.ui.shared.pointerTool.pointerToolConst import UNIQUE_NAME_SYSTEM_EFFECTS
from uihider import UiHiderMixin

class SystemWideEffectsContainer(UiHiderMixin, ContainerAutoSize):
    __guid__ = 'uicls.SystemWideEffectsContainer'
    default_height = 5
    default_name = 'SystemWideEffectsContainer'
    default_state = uiconst.UI_PICKCHILDREN
    uniqueUiName = UNIQUE_NAME_SYSTEM_EFFECTS
    __notifyevents__ = ['OnSystemWideEffectAdd', 'OnSystemWideEffectRemove', 'OnSystemWideEffectInfoUpdated']

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        UiHiderMixin.ApplyAttributes(self, attributes)
        self.btnParByItemID = {}
        self.Initialize(self.GetSystemWideEffectsInfo())
        sm.RegisterNotify(self)

    def Close(self):
        sm.UnregisterNotify(self)
        ContainerAutoSize.Close(self)

    def CreateButton(self, sourceItemID, sourceTypeID):
        if sourceItemID not in self.btnParByItemID:
            self.btnParByItemID[sourceItemID] = SystemWideEffectSlotParent(parent=self, sourceTypeID=sourceTypeID)

    def RemoveButton(self, sourceItemID):
        if sourceItemID in self.btnParByItemID:
            btn = self.btnParByItemID.pop(sourceItemID)
            btn.Close()

    def OnSystemWideEffectAdd(self, sourceItemID, sourceTypeID):
        self.CreateButton(sourceItemID, sourceTypeID)

    def OnSystemWideEffectRemove(self, sourceItemID):
        self.RemoveButton(sourceItemID)

    def OnSystemWideEffectInfoUpdated(self, systemWideEffectInfo):
        self.Initialize(systemWideEffectInfo)

    def GetSystemWideEffectsInfo(self):
        return sm.GetService('systemWideEffectSvc').GetSystemWideEffectInfo()

    def Initialize(self, systemWideEffectInfo):
        self.Flush()
        self.btnParByItemID = {}
        for itemKey, effects in systemWideEffectInfo.iteritems():
            self.CreateButton(itemKey[0], itemKey[1])
