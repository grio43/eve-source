#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\controllers\structureController.py
import utillib
from eve.client.script.ui.shared.dockedUI.controllers.baseController import BaseStationController
from eve.client.script.ui.shared.inventory.invConst import ContainerType
from eve.common.script.sys.idCheckers import IsNPC

class StructureController(BaseStationController):

    def __init__(self, itemID):
        BaseStationController.__init__(self)
        self.itemID = self.structureID = itemID
        self._structureItem = None

    @property
    def structureItem(self):
        if self._structureItem is None:
            inv = sm.GetService('invCache').GetInventoryFromId(self.structureID)
            self._structureItem = inv.GetItem()
        return self._structureItem

    def ChangeDockedMode(self, viewState):
        if viewState.HasActiveTransition():
            return
        if sm.GetService('viewState').IsPrimaryViewActive('structure'):
            sm.GetService('cmd').CmdEnterHangar()
        else:
            sm.GetService('cmd').CmdEnterStructure()

    def GetServicesInStructure(self):
        candidateServices = sm.GetService('structureServices').GetPossibleStructureServices()
        return self._GetServiceInfoAvailable(candidateServices)

    def GetCurrentStateForService(self, serviceID):
        try:
            hasAccessTo = sm.GetService('structureServices').IsServiceAvailableForCharacter(serviceID)
        except KeyError:
            return utillib.KeyVal(isEnabled=True)

        return utillib.KeyVal(isEnabled=hasAccessTo)

    def GetGuests(self):
        return sm.GetService('structureGuests').GetGuests()

    def GetOwnerID(self):
        return self.structureItem.ownerID

    def _GetShipInventoryType(self):
        return ContainerType.STRUCTURE_SHIP_HANGAR

    def _GetItemInventoryType(self):
        return ContainerType.STRUCTURE_ITEM_HANGAR

    def GetItemID(self):
        return self.structureID

    def HasDockModes(self):
        return True

    def GetDockedModeTextPath(self, viewName = None):
        if sm.GetService('viewState').IsPrimaryViewActive('hangar'):
            return 'UI/Commands/EnterStructure'
        else:
            return 'UI/Commands/EnterHangar'

    def MayTakeControl(self, structureID):
        return sm.GetService('structureControl').MayTakeControl(structureID)

    def IsHqAllowed(self):
        return False

    def IsControlable(self):
        return True

    def TakeControl(self):
        sm.GetService('structureControl').TakeControl(self.GetItemID())

    def GetStructurePilot(self, structureID):
        return sm.GetService('structureControl').GetStructurePilot(structureID)

    def IsNpcControlled(self):
        return IsNPC(self.GetOwnerID())

    def GetTypeID(self):
        return self.structureItem.typeID
