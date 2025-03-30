#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\structureFittingController.py
from eve.client.script.ui.shared.fittingScreen.fittingSlotController import ShipFittingSlotController
import carbonui.const as uiconst
from eve.client.script.ui.shared.fittingScreen.slotControllerGhostFittingExtension import UnfitFromSlot
from eve.client.script.util.eveMisc import GetRemoveServiceConfirmationQuestion, GetOfflineServiceConfirmationQuestion
from eve.common.script.sys.eveCfg import IsControllingStructure
from inventorycommon.const import serviceSlotFlags
from localization import GetByLabel

class StructureFittingServiceSlotController(ShipFittingSlotController):

    def UnfitModule(self, *args):
        if self.IsSimulated():
            return UnfitFromSlot(None, self.GetModule())
        module = self.GetModule()
        if module is None:
            return
        parentID = self.GetParentID()
        if parentID is None:
            return
        if IsControllingStructure():
            sm.GetService('structureControl').CheckCanDisableServiceModule(self.GetModule())
            questionPath, params = GetRemoveServiceConfirmationQuestion(self.GetModuleTypeID())
            ret = eve.Message(questionPath, params=params, buttons=uiconst.YESNO)
            if ret != uiconst.ID_YES:
                return
            invCache = sm.GetService('invCache')
            shipInv = invCache.GetInventoryFromId(parentID, locationID=session.structureid)
            shipInv.Add(self.GetModuleID(), parentID, qty=None, flag=const.flagHangar)

    def ToggleOnlineModule(self):
        if not self.IsOnlineable():
            return False
        if self.IsOnline():
            if not self.IsSimulated():
                sm.GetService('structureControl').CheckCanDisableServiceModule(self.GetModule())
                questionPath, params = GetOfflineServiceConfirmationQuestion(self.GetModuleTypeID())
                numOnlineServiceModules = 0
                for module in self.parentController.GetFittedModules():
                    if module.flagID in serviceSlotFlags and module.IsOnline():
                        numOnlineServiceModules += 1

                if numOnlineServiceModules == 1:
                    params['extraWarningText'] = GetByLabel('UI/Structures/OfflineLastServiceModuleWarning') + '<br>'
                else:
                    params['extraWarningText'] = ''
                ret = eve.Message(questionPath, params=params, buttons=uiconst.YESNO)
                if ret != uiconst.ID_YES:
                    return
            self.OfflineModule()
        else:
            self.OnlineModule()
        if self.IsSimulated():
            sm.GetService('ghostFittingSvc').SendFittingSlotsChangedEvent()

    def _ShouldContinueAfterOfflineWarning(self):
        return True
