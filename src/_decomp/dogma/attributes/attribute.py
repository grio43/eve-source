#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\attributes\attribute.py
import dogma
import dogma.data as dogma_data
import gametime
from dogma.attributes import AttributeInterface
import pytelemetry.zoning as zoning
import itertools
import dogma.const as const
import weakref
from dogma.dogmaLogging import GetCategoryNameFromID
from dogma.dogmaLogging import GetGroupNameFromID
from dogma.dogmaLogging import GetTypeNameFromID
from dogma.dogmaLogging import LogError
from dogma.dogmaLogging import LogException
from dogma.dogmaLogging import WrappedMethod

def Seq(sequenceOrNone):
    if sequenceOrNone is None:
        return []
    return sequenceOrNone


class Attribute(AttributeInterface):
    __slots__ = ['category',
     'currentValue',
     'baseValue',
     'typeValue',
     'invItem',
     'incomingModifiers',
     '_outgoingModifiers',
     'capAttrib',
     'item',
     'dirty',
     'highIsGood',
     'dogmaLM',
     'attribID',
     '_onChangeCallbacks',
     'nonModifyingDependants',
     'clientSideValue',
     'floorAttrib']

    def __str__(self):
        return self.performantStr()

    def performantStr(self):
        try:
            itemID = self.item.itemID
            itemClass = self.item.__class__.__name__
            itemAddress = id(self.item)
        except ReferenceError:
            itemID = self.invItem.itemID
            itemClass = 'UNLOADED-ITEM'
            itemAddress = '[GONE]'

        attribID = self.attribID
        attributeClass = self.__class__.__name__
        invItemCategoryID = self.invItem.categoryID
        invItemGroupID = self.invItem.groupID
        invItemTypeID = self.invItem.typeID
        return "'{attribID}' ({attributeClass}) on '{invItemCategoryID} / {invItemTypeID}' ({itemClass} {itemID}) ".format(**locals())

    def friendlyStr(self):
        try:
            itemID = self.item.itemID
            itemClass = self.item.__class__.__name__
            itemAddress = id(self.item)
        except ReferenceError:
            itemID = self.invItem.itemID
            itemClass = 'UNLOADED-ITEM'
            itemAddress = '[GONE]'

        attribID = self.attribID
        attributeName = dogma_data.get_attribute_name(attribID)
        attributeClass = self.__class__.__name__
        invItemCategoryName = GetCategoryNameFromID(self.invItem.categoryID)
        invItemGroupName = GetGroupNameFromID(self.invItem.groupID)
        invItemTypeName = GetTypeNameFromID(self.invItem.typeID)
        numIncoming = self.CountIncomingModifiers()
        numOutgoing = self.CountOutgoingModifiers()
        return "'{attributeName}' ({attributeClass}) on '{invItemCategoryName} / {invItemTypeName}' ({itemClass} {itemID}) [i{numIncoming}:o{numOutgoing}] ".format(**locals())

    def printInvItemDetails(self, itemClass):
        print 'START INV ITEM DETAILS:'
        print
        try:
            i = self.invItem
            print 'invItem:', i
            print 'type:', type(i)
            print 'columns:', i.__columns__
            print
            for a in ['itemID',
             'typeID',
             'ownerID',
             'locationID',
             'flagID',
             'quantity',
             'groupID',
             'categoryID',
             'customInfo',
             'stacksize',
             'singleton']:
                print a, getattr(i, a)

            print
            print 'Underlying item:', self.item
            print
            print 'class:', itemClass
        except:
            print "*** OUCH. THAT DIDN'T WORK! ***"

        print
        print 'END INV ITEM DETAILS'
        print

    def __init__(self, attribID, baseValue, dogmaItem, dogmaLM, staticAttr):
        self.attribID = attribID
        self.item = dogmaItem
        self.dogmaLM = dogmaLM
        self.invItem = dogmaItem.invItem
        if attribID is not None:
            self.typeValue = dogma_data.get_type_attribute_or_default(dogmaItem.invItem.typeID, attribID)
        else:
            self.typeValue = baseValue
        if baseValue is None:
            baseValue = self.typeValue
        self.baseValue = baseValue
        self.incomingModifiers = None
        self._outgoingModifiers = None
        self.nonModifyingDependants = None
        self._onChangeCallbacks = None
        self.highIsGood = staticAttr.highIsGood
        self.category = staticAttr.dataType
        self.currentValue = self.baseValue
        self.dirty = False
        if getattr(staticAttr, 'maxAttributeID', False):
            self.capAttrib = weakref.proxy(dogmaItem.attributes[staticAttr.maxAttributeID])
            self.capAttrib.AddNonModifyingDependant(self)
        else:
            self.capAttrib = None
        if getattr(staticAttr, 'minAttributeID', False):
            self.floorAttrib = weakref.proxy(dogmaItem.attributes[staticAttr.minAttributeID])
            self.floorAttrib.AddNonModifyingDependant(self)
        else:
            self.floorAttrib = None
        self._PickUpInitialModifiers(dogmaItem)

    def IsAnOrphan(self):
        try:
            testWhetherItemIsStillValid = self.item.invItem
            return False
        except ReferenceError:
            return True

    def _PickUpInitialModifiers(self, dogmaItem):
        location = dogmaItem.GetLocation()
        if location:
            location._PickUpInitialModifiersFromLocationTo(self)
        pilotID = dogmaItem.GetPilot()
        ownerItem = self.dogmaLM.dogmaItems.get(pilotID, None)
        if ownerItem and self.item.IsOwnerModifiable():
            ownerItem._PickUpInitialModifiersFromOwnerTo(self)

    def Update(self):
        prevValue = self.currentValue
        capVal = None
        floorVal = None
        if self.capAttrib:
            capVal = self.capAttrib.GetValue()
            self.baseValue = min(self.baseValue, capVal)
        if self.floorAttrib:
            floorVal = self.floorAttrib.GetValue()
            self.baseValue = max(self.baseValue, floorVal)
        val = self.baseValue
        val = self._ApplyModifierOperationsToVal(val)
        if capVal is not None:
            val = min(val, capVal)
        if floorVal is not None:
            val = max(val, floorVal)
        if self.category in (10, 11, 12):
            val = int(val)
        if self.attribID in (const.attributeCpuLoad,
         const.attributePowerLoad,
         const.attributePowerOutput,
         const.attributeCpuOutput,
         const.attributeCpu,
         const.attributePower):
            val = round(val, 2)
        self.currentValue = val
        self.dirty = False
        self._PerformCallbacksIfValueChanged(prevValue)

    def _ApplyModifierOperationsToVal(self, val):
        if self.incomingModifiers:
            for idx, mods in enumerate(self.incomingModifiers):
                dogmaOperator = const.dgmOperators[const.dgmOperatorPrecedence[idx]]
                for modAttrib in mods:
                    val = dogmaOperator(val, modAttrib.GetValue())

        return val

    def GetValue(self):
        if self.dirty:
            self.Update()
        return self.currentValue

    def MarkDirty(self, silent = False):
        self.dirty = True
        for op, nowDirtyAttrib in list(Seq(self._outgoingModifiers)):
            try:
                nowDirtyAttrib().MarkDirty()
            except AttributeError:
                continue

        for nowDirtyAttrib in Seq(self.nonModifyingDependants):
            try:
                nowDirtyAttrib.MarkDirty()
            except AttributeError:
                continue

        if silent:
            return
        ownerID = None
        if True:
            try:
                ownerID = self.item.ownerID
            except AttributeError:
                LogError('Attribute {} has no `ownerID` on its `item`, just: {}'.format(self, sorted(vars(self.item))))

        itemID = self.item.itemID
        if self.ShoulCallbackAttributeChange(itemID, ownerID):
            try:
                oldValue = self.currentValue
                newValue = self.GetValue()
                self.dogmaLM.attributeChangeCallbacksByAttributeID[self.attribID](self.attribID, itemID, newValue, oldValue)
            except Exception:
                LogException('Error broadcasting attribute change {}'.format(self.dogmaLM.attributeChangeCallbacksByAttributeID[self.attribID]))

        if dogma.IsClient():
            return
        if self.dogmaLM.ShouldMessageItemEvent(itemID):
            try:
                if self.attribID is not None:
                    self.dogmaLM.msgMgr.AddAttribute(self)
            except Exception:
                LogException('Error broadcasting attribute change')

    def ShoulCallbackAttributeChange(self, itemID, ownerID):
        if self.attribID not in self.dogmaLM.attributeChangeCallbacksByAttributeID:
            return False
        if not self.dogmaLM.ShouldMessageItemEvent(itemID, ownerID):
            return False
        return True

    def AddCallbackForChanges(self, func, params):
        if self._onChangeCallbacks is None:
            self._onChangeCallbacks = {}
        self._onChangeCallbacks[func] = params

    def RemoveCallbackForChanges(self, func):
        del self._onChangeCallbacks[func]
        if not self._onChangeCallbacks:
            self._onChangeCallbacks = None

    def _PerformCallbacksIfValueChanged(self, prevValue):
        if self._onChangeCallbacks is None:
            return
        if prevValue != self.currentValue:
            for func, params in self._onChangeCallbacks.iteritems():
                func(self, prevValue, self.currentValue, *params)

    def ConstructMessage(self):
        try:
            if self.item.ownerID is None:
                return
        except ReferenceError:
            return

        clientID = self.item.FindClientID('charid', [self.item.ownerID])
        if clientID is not None:
            newValue = self.GetValue()
            try:
                oldValue = self.clientSideValue
                if oldValue == newValue:
                    return
            except AttributeError:
                oldValue = newValue

            self.clientSideValue = newValue
            if self.dogmaLM.ShouldMessageItemEvent(self.item.itemID):
                simTime = gametime.GetSimTime()
                return (clientID, (('OnModuleAttributeChange',
                   self.item.ownerID,
                   self.item.itemID,
                   self.attribID,
                   simTime,
                   newValue,
                   oldValue,
                   gametime.GetWallclockTime()), simTime))
        else:
            return

    def _makeEmptyIncomingModifiers(self):
        return tuple((set() for x in const.dgmOperatorPrecedence))

    def _initIncomingModifiers(self):
        self.incomingModifiers = self._makeEmptyIncomingModifiers()

    @WrappedMethod
    def AddIncomingModifier(self, op, attribute):
        if self.incomingModifiers is None:
            self._initIncomingModifiers()
        self.incomingModifiers[const.dgmOperatorIDtoIndex[op]].add(attribute)
        self.MarkDirty()

    @WrappedMethod
    def RemoveIncomingModifier(self, op, attribute):
        try:
            self.incomingModifiers[const.dgmOperatorIDtoIndex[op]].remove(attribute)
            self.MarkDirty()
        except (TypeError,
         IndexError,
         KeyError,
         ValueError):
            return

        if self.incomingModifiers is None:
            return
        if not any(self.incomingModifiers):
            self.incomingModifiers = None

    def GetIncomingModifiers(self):
        if self.incomingModifiers is None:
            return []
        result = []
        for opIdx, attribSet in enumerate(self.incomingModifiers):
            result.extend(((const.dgmOperatorPrecedence[opIdx], attrib) for attrib in attribSet))

        return result

    def CountIncomingModifiers(self):
        return len(self.GetIncomingModifiers())

    def AddNonModifyingDependant(self, attribute):
        if self.nonModifyingDependants is None:
            self.nonModifyingDependants = set()
        self.nonModifyingDependants.add(attribute)
        attribute.MarkDirty(silent=True)

    def _makeEmptyOutgoingModifiers(self):
        return set()

    def _initOutgoingModifiers(self):
        self._outgoingModifiers = self._makeEmptyOutgoingModifiers()

    @WrappedMethod
    def AddOutgoingModifier(self, op, attribute):
        if self._outgoingModifiers is None:
            self._initOutgoingModifiers()
        weak = weakref.ref(attribute)
        self._outgoingModifiers.add((op, weak))

    @WrappedMethod
    def RemoveOutgoingModifier(self, op, attribute):
        weak = weakref.ref(attribute)
        try:
            self._outgoingModifiers.remove((op, weak))
        except (AttributeError, KeyError, ValueError):
            return

        if not any(self._outgoingModifiers):
            self._outgoingModifiers = None

    def GetOutgoingModifiers(self):
        if self._outgoingModifiers is None:
            return []
        return [ (opIdx, attrib_weakref()) for opIdx, attrib_weakref in self._outgoingModifiers ]

    def CountOutgoingModifiers(self):
        return len(self.GetOutgoingModifiers())

    def RemoveAllModifiers(self):
        for operator, incomingAttrib in self.GetIncomingModifiers():
            incomingAttrib.RemoveOutgoingModifier(operator, self)

        for operator, outgoingAttrib in self.GetOutgoingModifiers():
            outgoingAttrib.RemoveIncomingModifier(operator, self)

        self._DiscardAllModifiers()

    def _DiscardAllModifiers(self):
        self.incomingModifiers = None
        self._outgoingModifiers = None

    def GetBaseValue(self):
        return self.baseValue

    def SetBaseValue(self, newBaseValue):
        if self.baseValue != newBaseValue:
            self.baseValue = newBaseValue
            self.MarkDirty()

    def ResetBaseValue(self):
        if self.baseValue != self.typeValue:
            self.baseValue = self.typeValue
            self.MarkDirty()

    def IncreaseBaseValue(self, addAmount):
        if not self.item.CanAttributeBeModified():
            return
        self.baseValue += addAmount
        self.MarkDirty()

    def DecreaseBaseValue(self, decAmount):
        if not self.item.CanAttributeBeModified():
            return
        self.baseValue -= decAmount
        self.MarkDirty()

    def GetModifyingItems(self):
        modifyingItems = set()
        if self.incomingModifiers is None:
            return modifyingItems
        for srcAttrib in itertools.chain(*self.incomingModifiers):
            if srcAttrib.item is not None:
                modifyingItems.add(srcAttrib.item.itemID)

        return modifyingItems

    def GetPersistData(self):
        if self.baseValue != self.typeValue:
            return self.baseValue
        else:
            return None

    @zoning.ZONE_METHOD
    def ApplyPersistData(self, pData):
        self.SetBaseValue(pData)
