#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\empireTechnologyViews\shipStatistics.py
from localization import GetByLabel

class ShipStatistic(object):

    def __init__(self, label = None, attributeID = None):
        self.label = label
        self.attributeID = attributeID

    def GetString(self, typeID):
        if self.label and self.attributeID:
            value = self.GetValue(typeID)
            if value:
                return GetByLabel(self.label, value=value)
        return ''

    def GetValue(self, typeID):
        return sm.GetService('godma').GetTypeAttribute(typeID=typeID, attributeID=self.attributeID)


class ShipMassStatistic(ShipStatistic):

    def __init__(self, label = None, labelTonnes = None, attributeID = None):
        self.labelTonnes = labelTonnes
        ShipStatistic.__init__(self, label, attributeID)

    def GetString(self, typeID):
        if self.label and self.attributeID:
            value = self.GetValue(typeID)
            if value:
                if value > 10000.0:
                    value = value / 1000.0
                    return GetByLabel(self.labelTonnes, value=value)
                return GetByLabel(self.label, value=value)
        return ''


SHIELD_LABEL = 'UI/ShipStatistics/ShieldStatistic'
ARMOR_LABEL = 'UI/ShipStatistics/ArmorStatistic'
STRUCTURE_LABEL = 'UI/ShipStatistics/StructureStatistic'
MASS_KG_LABEL = 'UI/ShipStatistics/MassStatisticKg'
MASS_TONNES_LABEL = 'UI/ShipStatistics/MassStatisticTonnes'
MAX_VELOCITY_LABEL = 'UI/ShipStatistics/MaxVelocityStatistic'
WARP_SPEED_LABEL = 'UI/ShipStatistics/WarpSpeedStatistic'
MAX_TARGET_RG_LABEL = 'UI/ShipStatistics/MaxTargetRangeStatistic'
MAX_LOCKED_TARGETS_LABEL = 'UI/ShipStatistics/MaxLockedTargetsStatistic'
SHIELD = ShipStatistic(label=SHIELD_LABEL, attributeID=const.attributeShieldCapacity)
ARMOR = ShipStatistic(label=ARMOR_LABEL, attributeID=const.attributeArmorHP)
STRUCTURE = ShipStatistic(label=STRUCTURE_LABEL, attributeID=const.attributeHp)
MASS = ShipMassStatistic(label=MASS_KG_LABEL, labelTonnes=MASS_TONNES_LABEL, attributeID=const.attributeMass)
MAX_VELOCITY = ShipStatistic(label=MAX_VELOCITY_LABEL, attributeID=const.attributeMaxVelocity)
WARP_SPEED = ShipStatistic(label=WARP_SPEED_LABEL, attributeID=const.attributeBaseWarpSpeed)
MAX_TARGET_RG = ShipStatistic(label=MAX_TARGET_RG_LABEL, attributeID=const.attributeMaxTargetRange)
MAX_LOCKED_TARGETS = ShipStatistic(label=MAX_LOCKED_TARGETS_LABEL, attributeID=const.attributeMaxLockedTargets)
SHIP_STATISTICS = [SHIELD,
 ARMOR,
 STRUCTURE,
 MASS,
 MAX_VELOCITY,
 WARP_SPEED,
 MAX_TARGET_RG,
 MAX_LOCKED_TARGETS]

def GetStatistics(typeID):
    statistics = ''
    for shipStat in SHIP_STATISTICS:
        shipStatString = shipStat.GetString(typeID).upper()
        if statistics and shipStatString:
            statistics += '\n'
        statistics += shipStatString

    return statistics
