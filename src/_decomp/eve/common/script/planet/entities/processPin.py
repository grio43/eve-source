#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\planet\entities\processPin.py
from eve.common.script.planet.entities.basePin import BasePin
from eve.common.script.planet.entities.basePin import STATE_ACTIVE, STATE_IDLE
import blue
from fsdBuiltData.common.planet import get_schematic

class ProcessPin(BasePin):
    __slots__ = ['schematicID',
     'cycleTime',
     'hasReceivedInputs',
     'receivedInputsLastCycle',
     'demands',
     'products']

    def __init__(self, typeID):
        BasePin.__init__(self, typeID)
        self.schematicID = None
        self.cycleTime = None
        self.hasReceivedInputs = True
        self.receivedInputsLastCycle = True
        self.demands = {}
        self.products = {}

    def CanAccept(self, typeID, quantity):
        if typeID not in self.demands:
            return 0
        if quantity < 0:
            quantity = self.demands[typeID]
        remainingSpace = self.demands[typeID]
        if typeID in self.contents:
            remainingSpace = self.demands[typeID] - self.contents[typeID]
        if remainingSpace < quantity:
            return remainingSpace
        return quantity

    def HasEnoughInputs(self):
        for demandTypeID, demandQty in self.demands.iteritems():
            if demandTypeID not in self.contents:
                return False
            if demandQty > self.contents[demandTypeID]:
                return False

        return True

    def CanActivate(self):
        if self.activityState < STATE_IDLE:
            return False
        if self.schematicID is None:
            return False
        if self.IsActive():
            return True
        if self.hasReceivedInputs or self.receivedInputsLastCycle:
            return True
        if not self.HasEnoughInputs():
            return False
        return True

    def GetNextRunTime(self):
        if not self.IsActive() and self.HasEnoughInputs():
            return None
        else:
            return BasePin.GetNextRunTime(self)

    def CanRun(self, runTime = None):
        if not self.IsActive() and not self.CanActivate():
            return False
        rt = runTime
        if runTime is None:
            rt = blue.os.GetWallclockTime()
        nextRunTime = self.GetNextRunTime()
        if nextRunTime is None or nextRunTime <= rt:
            return True
        return False

    def Run(self, runTime):
        products = {}
        if self.IsActive():
            products = self.products.copy()
        canConsume = True
        for demandTypeID, demandQty in self.demands.iteritems():
            if demandTypeID not in self.contents:
                canConsume = False
                break
            if demandQty > self.contents[demandTypeID]:
                canConsume = False
                break

        if canConsume:
            for demandTypeID, demandQty in self.demands.iteritems():
                self.RemoveCommodity(demandTypeID, demandQty)

            self.SetState(STATE_ACTIVE)
        else:
            self.SetState(STATE_IDLE)
        self.receivedInputsLastCycle = self.hasReceivedInputs
        self.hasReceivedInputs = False
        self.lastRunTime = runTime
        return products

    def InstallSchematic(self, schematicID):
        schematicObj = get_schematic(schematicID)
        if not schematicObj:
            raise RuntimeError('Schematic with schematicID', schematicID, 'does not exist')
        if not schematicObj.pins:
            self.LogError('AUTHORING ERROR :: Schematic ID', schematicID, 'cannot be assigned to any pin types!')
            return
        if not schematicObj.types:
            self.LogError('AUTHORING ERROR :: Schematic ID', schematicID, 'has no inputs or outputs!')
            return
        if self.typeID not in schematicObj.pins:
            raise UserError('CannotAssignSchematicToPinType')
        self.SetSchematic(schematicID, schematicObj)
        self.SetState(STATE_IDLE)

    def SetSchematic(self, schematicID, schematic = None):
        self.demands = {}
        self.products = {}
        if not schematic:
            schematic = get_schematic(schematicID)
        for typeID, commodity in schematic.types.iteritems():
            if commodity.isInput:
                self.demands[typeID] = commodity.quantity
            else:
                self.products[typeID] = commodity.quantity

        self.schematicID = schematicID
        self.cycleTime = schematic.cycleTime * const.SEC
        newContents = {}
        for commodityID, quantity in self.contents.iteritems():
            if commodityID in self.demands:
                newContents[commodityID] = quantity if quantity < self.demands[commodityID] else self.demands[commodityID]

        self.contents = newContents

    def AddCommodity(self, typeID, quantity):
        qtyAdded = self._AddCommodity(typeID, quantity)
        if qtyAdded > 0:
            self.hasReceivedInputs = True
        return qtyAdded

    def IsConsumer(self):
        return True

    def GetConsumables(self):
        return self.demands.copy()

    def IsProducer(self):
        return True

    def IsProcessor(self):
        return True

    def IsNeedingAttention(self):
        return not self.GetProducts()

    def GetCycleTime(self):
        return self.cycleTime

    def GetProducts(self):
        return self.products.copy()

    def GetInputBufferState(self):
        productsRatio = 0
        for typeID, qty in self.demands.iteritems():
            productsRatio += float(self.contents.get(typeID, 0)) / qty

        return 1 - productsRatio / len(self.demands)

    def HasDifferingState(self, otherPin):
        if self.schematicID != getattr(otherPin, 'schematicID', -1):
            return True
        return BasePin.HasDifferingState(self, otherPin)

    def Serialize(self, full = False):
        data = BasePin.Serialize(self, full)
        data.schematicID = self.schematicID
        data.hasReceivedInputs = self.hasReceivedInputs
        data.receivedInputsLastCycle = self.receivedInputsLastCycle
        return data
