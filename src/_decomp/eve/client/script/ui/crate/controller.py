#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\crate\controller.py
from crates import CratesStaticData
from crates.const import MAX_MULTI_OPEN
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.crate.lootItem import LootItemFromType, SkillBundleLootItem, FittingLootItem, InsuranceLootItem
from localization import GetByMessageID, GetByLabel
from log import LogException
from random import shuffle
from signals import Signal

class Texture(object):

    def __init__(self, data):
        self.width = data.width
        self.height = data.height
        self.resPath = data.resPath
        self.color = getattr(data, 'color', None)


class HackingCrateController(object):
    __notifyevents__ = ['ProcessSessionChange']

    def __init__(self, typeID, itemID, stacksize):
        self.typeID = typeID
        self.itemID = itemID
        self.stacksize = stacksize
        self.isOpening = False
        self.loot = None
        self.specialLoot = None
        self.destinationID = None
        self.destinationFlagID = None
        self.onFinish = Signal(signalName='onFinish')
        self.onOpen = Signal(signalName='onOpen')
        self.onSkip = Signal(signalName='onSkip')
        self.onCrateMultiHackEnded = Signal(signalName='onCrateMultiHackEnded')
        sm.RegisterNotify(self)

    @property
    def staticData(self):
        return CratesStaticData().get_crate_by_type_id(self.typeID)

    @property
    def caption(self):
        return GetByMessageID(self.staticData.nameID)

    @property
    def description(self):
        return GetByMessageID(self.staticData.descriptionID)

    @property
    def animatedSplash(self):
        if self.staticData.animatedSplash:
            return Texture(self.staticData.animatedSplash)

    @property
    def staticSplash(self):
        if self.staticData.staticSplash:
            return Texture(self.staticData.staticSplash)

    def LoadLootFromTypes(self, loot):
        shuffle(loot)
        return [ LootItemFromType(itemID, typeID, quantity, self.destinationID, self.destinationFlagID) for itemID, typeID, quantity in loot ]

    def LoadSpecialLoot(self):
        specialLoot = []
        fitting_ids = getattr(self.staticData, 'fittings', []) or []
        for fitting_id in fitting_ids:
            name, icon, ship_type_id, insurance = sm.RemoteSvc('ship').GetShipFittingInfo(fitting_id)
            if insurance:
                specialLoot.append(InsuranceLootItem(self.itemID, ship_type_id, insurance))
            specialLoot.append(FittingLootItem(self.itemID, fitting_id, name, icon))

        skillBundleID = getattr(self.staticData, 'skillBundleID', None)
        if skillBundleID:
            specialLoot.append(SkillBundleLootItem(self.itemID, skillBundleID))
        return specialLoot

    def OpenCrate(self):
        if self.stacksize <= 0:
            raise RuntimeError('No more crates')
        self.isOpening = True
        self.stacksize -= 1
        try:
            self.destinationID, self.destinationFlagID = sm.RemoteSvc('crateService').GetCrateLocation(self.itemID)
            loot = sm.RemoteSvc('crateService').OpenCrate(self.itemID)
            sm.ScatterEvent('OnClientEvent_CrateOpen', self.typeID)
            self.loot = self.LoadLootFromTypes(loot)
            self.specialLoot = self.LoadSpecialLoot()
            self.onOpen()
        except Exception:
            self.stacksize += 1
            self.isOpening = False
            raise

    def OpenMultipleCrates(self):
        qty = min(MAX_MULTI_OPEN, self.stacksize)
        cratesOpened = 0
        numCratesToOpen = qty
        try:
            cratesOpened, numCratesToOpen = sm.RemoteSvc('crateService').ClaimLootFromCrateStack(self.itemID, qty)
        except UserError as e:
            if e.msg in ('MultipleCrateOpenAbortedDueToTidiCratesOpened', 'MultipleCrateOpenAbortedDueToTidiCratesOpened'):
                if e.msg == 'MultipleCrateOpenAbortedDueToTidiCratesOpened':
                    cratesOpened = e.dict['numCratesOpened']
                    self.stacksize -= cratesOpened
            elif e.msg == 'FailedOpeningMultiCrate':
                cratesOpened = e.dict['numCratesOpened']
                self.stacksize -= cratesOpened
            raise
        finally:
            self.onCrateMultiHackEnded(cratesOpened, numCratesToOpen)

        self.ShowResultMessage(cratesOpened, numCratesToOpen)
        self.stacksize -= cratesOpened
        if cratesOpened:
            sm.ScatterEvent('OnClientEvent_CrateOpen', self.typeID)

    def ShowResultMessage(self, cratesOpened, numCratesToOpen):
        if cratesOpened == numCratesToOpen:
            ShowQuickMessage(GetByLabel('UI/Crate/NumCratesSuccessfullyHacked', numCrates=cratesOpened))
        else:
            ShowQuickMessage(GetByLabel('UI/Crate/NumCratesHacked', numCrates=cratesOpened, numCratesToOpen=numCratesToOpen))

    def IsAnyLootLeft(self):
        return self.loot or self.specialLoot

    def ClaimLoot(self):
        if not self.IsAnyLootLeft():
            raise ValueError('No loot to claim')
        item = None
        if self.loot:
            item = self.loot.pop()
            item.claim()
        elif self.specialLoot:
            item = self.specialLoot.pop()
            item.claim()
        if not self.IsAnyLootLeft():
            self.isOpening = False
        return item

    def ClaimAllLoot(self):
        while self.loot:
            item = self.loot.pop()
            try:
                item.claim()
            except Exception:
                LogException('Error claiming loot item %s' % item.get_name())

        while self.specialLoot:
            item = self.specialLoot.pop()
            try:
                item.claim()
            except Exception:
                LogException('Error claiming special loot item %s' % item.get_name())

    def Finish(self):
        self.onFinish()

    def Close(self):
        sm.UnregisterNotify(self)
        self.ClaimAllLoot()
        self.onFinish.clear()
        self.onOpen.clear()

    def ProcessSessionChange(self, isremote, session, change):
        self.Finish()

    def GetSortedLoot(self):
        return self.loot

    def GetSpecialLoot(self):
        return self.specialLoot


class FixedCrateStackController(object):

    def __init__(self, crate_stack_list):
        self.lootByType = {}
        self.controllers = []
        self.loot = None
        self.specialLoot = None
        self.crate_stack_list = crate_stack_list
        self.crate_list_index = 0
        self.onFinish = Signal(signalName='onFinish')
        self.onOpen = Signal(signalName='onOpen')
        self.onSkip = Signal(signalName='onSkip')
        self.destinationID = None
        self.destinationFlagID = None
        self.onCrateMultiOpenEnded = Signal(signalName='onCrateMultiOpenEnded')

    @property
    def staticData(self):
        typeID, itemID, stacksize = self.crate_stack_list[self.crate_list_index]
        return CratesStaticData().get_crate_by_type_id(typeID)

    @property
    def lootViewDescription(self):
        return GetByMessageID(self.staticData.lootDescriptionID)

    @property
    def caption(self):
        return GetByMessageID(self.staticData.nameID)

    @property
    def description(self):
        return GetByMessageID(self.staticData.descriptionID)

    @property
    def animatedSplash(self):
        if self.staticData.animatedSplash:
            return Texture(self.staticData.animatedSplash)

    @property
    def staticSplash(self):
        if self.staticData.staticSplash:
            return Texture(self.staticData.staticSplash)

    @property
    def stacksize(self):
        return sum((stacksize for typeID, itemID, stacksize in self.crate_stack_list))

    def LoadLootFromTypes(self, loot):
        return [ LootItemFromType(itemID, typeID, quantity, self.destinationID, self.destinationFlagID) for itemID, typeID, quantity in loot ]

    def LoadSpecialLoot(self, itemID):
        specialLoot = []
        skillBundleID = getattr(self.staticData, 'skillBundleID', None)
        if skillBundleID:
            specialLoot.append(SkillBundleLootItem(itemID, skillBundleID))
        fitting_ids = getattr(self.staticData, 'fittings', []) or []
        for fitting_id in fitting_ids:
            name, icon, ship_type_id, insurance = sm.RemoteSvc('ship').GetShipFittingInfo(fitting_id)
            specialLoot.append(FittingLootItem(itemID, fitting_id, name, icon))
            if insurance:
                specialLoot.append(InsuranceLootItem(itemID, ship_type_id, insurance))

        return specialLoot

    def OpenCrate(self):
        if self.stacksize <= 0:
            raise RuntimeError('No more crates')
        self.isOpening = True
        itemID = self.crate_stack_list[self.crate_list_index][1]
        typeID = self.crate_stack_list[self.crate_list_index][0]
        self.DecreaseStackSize()
        try:
            self.destinationID, self.destinationFlagID = sm.RemoteSvc('crateService').GetCrateLocation(itemID)
            loot = sm.RemoteSvc('crateService').OpenCrate(itemID)
            sm.ScatterEvent('OnClientEvent_CrateOpen', typeID)
            self.loot = self.LoadLootFromTypes(loot)
            self.specialLoot = self.LoadSpecialLoot(itemID)
            self.ClaimSpecialLoot()
            if self.crate_stack_list[self.crate_list_index][2] <= 0:
                self.crate_list_index = min(self.crate_list_index + 1, len(self.crate_stack_list) - 1)
            self.onOpen()
        except Exception:
            self.IncreaseStackSize()
            self.isOpening = False
            raise

    def OpenMultipleCrates(self):
        crateEntry = self.crate_stack_list[self.crate_list_index]
        typeID = crateEntry[0]
        itemID = crateEntry[1]
        stacksize = crateEntry[2]
        qty = min(MAX_MULTI_OPEN, stacksize)
        cratesOpened = 0
        numCratesToOpen = qty
        try:
            cratesOpened, numCratesToOpen = sm.RemoteSvc('crateService').ClaimLootFromCrateStack(itemID, qty)
        except UserError as e:
            if e.msg in ('MultipleCrateOpenAbortedDueToTidiCratesOpened', 'MultipleCrateOpenAbortedDueToTidiCratesOpened'):
                if e.msg == 'MultipleCrateOpenAbortedDueToTidiCratesOpened':
                    cratesOpened = e.dict['numCratesOpened']
                    self.DecreaseStackSize(cratesOpened)
            elif e.msg == 'FailedOpeningMultiCrate':
                cratesOpened = e.dict['numCratesOpened']
                self.DecreaseStackSize(cratesOpened)
            raise
        finally:
            self.DecreaseStackSize(cratesOpened)
            self.onCrateMultiOpenEnded(cratesOpened, numCratesToOpen)

        self.ShowResultMessage(cratesOpened, numCratesToOpen)
        if cratesOpened:
            sm.ScatterEvent('OnClientEvent_CrateOpen', typeID)

    def ShowResultMessage(self, cratesOpened, numCratesToOpen):
        if cratesOpened == numCratesToOpen:
            ShowQuickMessage(GetByLabel('UI/Crate/NumCratesSuccessfullyOpened', numCrates=cratesOpened))
        else:
            ShowQuickMessage(GetByLabel('UI/Crate/NumCratesOpened', numCrates=cratesOpened, numCratesToOpen=numCratesToOpen))

    def ClaimSpecialLoot(self):
        specialLoot = self.specialLoot[:]
        while specialLoot:
            item = specialLoot.pop()
            try:
                item.claim()
            except Exception:
                LogException('Error claiming special loot item %s' % item.get_name())

    def Finish(self):
        self.onFinish()

    def DecreaseStackSize(self, amount = 1):
        entry = self.crate_stack_list[self.crate_list_index]
        self.crate_stack_list[self.crate_list_index] = (entry[0], entry[1], entry[2] - amount)
        if entry[2] <= 1:
            self.crate_list_index = min(self.crate_list_index + 1, len(self.crate_stack_list) - 1)

    def IncreaseStackSize(self):
        entry = self.crate_stack_list[self.crate_list_index]
        self.crate_stack_list[self.crate_list_index] = (entry[0], entry[1], entry[2] + 1)

    def Skip(self):
        self.DecreaseStackSize()
        self.onSkip()

    def GetSortedLoot(self):
        return self.LoadLootFromTypes(self.PeekInsideFixedCrate())

    def GetSpecialLoot(self):
        return self.specialLoot or []

    def PeekInsideFixedCrate(self):
        typeID = self.crate_stack_list[self.crate_list_index][0]
        if typeID not in self.lootByType:
            itemID = self.crate_stack_list[self.crate_list_index][1]
            peekResult = sm.RemoteSvc('crateService').PeekInsideFixedCrate(itemID)
            self.lootByType[typeID] = [ (None, typeID_quantity_customInfo[0], typeID_quantity_customInfo[1]) for typeID_quantity_customInfo in peekResult ]
            self.specialLoot = self.LoadSpecialLoot(itemID)
        return self.lootByType[typeID]

    def Close(self):
        self.onFinish.clear()
        self.onOpen.clear()


def CreateController(typeID, itemID, stacksize):
    crate = CratesStaticData().get_crate_by_type_id(typeID)
    if crate.lootPresentationType == 'fixed':
        return FixedCrateStackController([typeID, itemID, stacksize])
    if crate.lootPresentationType == 'hacking':
        return HackingCrateController(typeID, itemID, stacksize)
    raise RuntimeError("Unknown crate presentation type '%s'" % crate.lootPresentationType)


def __SakeReloadHook():
    try:
        from eve.client.script.ui.crate.window import CrateWindow
        instance = CrateWindow.GetIfOpen()
        if instance:
            CrateWindow.Reload(instance)
    except Exception:
        import log
        log.LogException()
