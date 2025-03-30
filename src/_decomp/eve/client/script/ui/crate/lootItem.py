#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\crate\lootItem.py
from evetypes import GetNameID
from eve.client.script.ui.util.uix import GetTechLevelIcon
from eve.common.script.sys.eveCfg import IsApparel, IsBlueprint, IsShip
from eve.common.script.util.insuranceConst import INSURANCE_ICON
from localization import GetByLabel, GetByMessageID

class AbstractLootItem(object):
    ICON_PATH = None
    ICON_SIZE = 64

    def __init__(self, icon = None):
        self.icon = icon or self.ICON_PATH

    def get_name(self):
        raise NotImplementedError('Must implement loot item naming in derived class')

    def claim(self):
        raise NotImplementedError('Must implement loot item claiming in derived class')

    def get_icon_size(self):
        return self.ICON_SIZE

    def get_icon(self):
        return self.icon

    def get_tech_icon(self, icon = None):
        return None


class LootItemFromType(AbstractLootItem):

    def __init__(self, itemID, typeID, quantity, destinationID, destinationFlagID):
        self.itemID = itemID
        self.typeID = typeID
        self.quantity = quantity
        self.destinationID = destinationID
        self.destinationFlagID = destinationFlagID
        super(LootItemFromType, self).__init__()

    def get_name(self):
        if self.quantity > 1:
            return GetByLabel('UI/Crate/ItemNameAndQuantity', typeID=self.typeID, quantity=self.quantity)
        return GetByMessageID(GetNameID(self.typeID))

    def claim(self):
        sm.RemoteSvc('crateService').ClaimLoot(self.itemID, self.destinationID, self.destinationFlagID)

    def get_icon_size(self):
        if IsBlueprint(self.typeID) or IsApparel(self.typeID) or IsShip(self.typeID):
            return 42
        return 64

    def get_tech_icon(self, icon = None):
        return GetTechLevelIcon(icon, typeID=self.typeID)

    def is_copy(self):
        return self.quantity < 0


class AbstractSpecialLootItem(AbstractLootItem):

    def __init__(self, crateID, name, icon):
        self.crateID = crateID
        self.name = name
        super(AbstractSpecialLootItem, self).__init__(icon)

    def get_name(self):
        return GetByLabel(self.name)


class SkillBundleLootItem(AbstractSpecialLootItem):
    ICON_PATH = 'res:/UI/Texture/icons/50_64_11.png'

    def __init__(self, crateID, skillBundleID):
        self.skillBundleID = skillBundleID
        name, icon = sm.GetService('skills').GetSkillBundleInfo(skillBundleID)
        super(SkillBundleLootItem, self).__init__(crateID, name, icon)

    def claim(self):
        sm.RemoteSvc('crateService').ClaimSkillBundle(self.crateID, self.skillBundleID)


class FittingLootItem(AbstractSpecialLootItem):

    def __init__(self, crateID, fitting, name, icon):
        self.fittingID = fitting
        super(FittingLootItem, self).__init__(crateID, name, icon)

    def claim(self):
        sm.RemoteSvc('crateService').ClaimFitting(self.crateID, self.fittingID)


class InsuranceLootItem(AbstractSpecialLootItem):
    ICON_PATH = INSURANCE_ICON

    def __init__(self, crateID, shipTypeID, insurance):
        insurance_name = GetByLabel('UI/Insurance/QuoteWindow/%s' % insurance)
        name = GetByLabel('UI/Insurance/ShipInsuranceType', item=shipTypeID, insurance=insurance_name)
        super(InsuranceLootItem, self).__init__(crateID, name, icon=None)

    def get_name(self):
        return self.name

    def claim(self):
        pass
