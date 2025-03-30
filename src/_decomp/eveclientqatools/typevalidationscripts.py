#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\typevalidationscripts.py
import dogma.data as dogma_data
import evetypes
import industry
import dogma.const as dogmaconst
import inventorycommon.const as invconst
from collections import defaultdict
from eveexceptions import UserError
from typematerials.data import get_type_materials_by_id, get_reprocessing_options
from inventorycommon.util import GetPackagedVolume
OPTION_BOOLEAN = 'boolean'
OPTION_FLOAT = 'float'
OPTION_STRING = 'string'

def CheckAttributeRange(attributeDict, attributeID, valueRange):
    attributeName = dogma_data.get_attribute_display_name(attributeID) if dogma_data.has_type_effects(attributeID) else None
    try:
        attributeValue = attributeDict[attributeID]
    except KeyError:
        result = 'Attribute %s not authored' % attributeName
        return (False, result)

    return CheckMinMax(attributeName, attributeValue, valueRange)


def CheckVolumeRange(typeID, valueRange):
    attributeName = dogma_data.get_attribute_name(dogmaconst.attributeVolume)
    attributeValue = evetypes.GetAttributeForType(typeID, attributeName)
    return CheckMinMax(attributeName, attributeValue, valueRange)


def CheckPackagedVolume(typeID, valueRange):
    packagedVolValue = GetPackagedVolume(typeID)
    attributeName = 'packagedVolume'
    attrTypeInfo = dogma_data.get_attribute(dogmaconst.attributeVolume)
    unpackagedVolValue = evetypes.GetAttributeForType(typeID, attrTypeInfo.name)
    if unpackagedVolValue <= packagedVolValue:
        result = 'Packaged volume is not smaller than unpackaged volume (%.2f &lt;= %.2f)' % (packagedVolValue, unpackagedVolValue)
        return (False, result)
    return CheckMinMax(attributeName, packagedVolValue, valueRange)


def CheckMinMax(attributeName, attributeValue, valueRange):
    result = ''
    if attributeValue < valueRange[0]:
        result = 'Attribute %s is too low (%.2f &lt; %.2f)' % (attributeName, attributeValue, valueRange[0])
        return (False, result)
    if attributeValue > valueRange[1]:
        result = 'Attribute %s is too high (%.2f &gt; %.2f)' % (attributeName, attributeValue, valueRange[1])
        return (False, result)
    return (True, result)


class CheckMaterials(object):
    displayName = 'Check Reprocessing Materials'
    options = [['skipNoBlueprint',
      'Skip types without published blueprint',
      OPTION_BOOLEAN,
      False], ['onlyCheckExcessMaterials',
      'Only report materials, which are returned too much',
      OPTION_BOOLEAN,
      True]]
    expandedCategories = [invconst.categoryModule,
     invconst.categoryStarbase,
     invconst.categoryStructureModule,
     invconst.categoryDeployable,
     invconst.categoryDrone,
     invconst.categoryCharge]
    skippedMaterialCategories = [invconst.categoryShip, invconst.categoryFighter]
    skippedMaterialGroups = [invconst.groupTool,
     invconst.groupDecryptorsTakmahl,
     invconst.groupDecryptorsTalocan,
     invconst.groupNamedComponents]
    skippedMaterialTypes = [57470,
     57471,
     57472,
     57473,
     57474,
     57475,
     57476,
     57477,
     57478,
     57479,
     57486,
     57487,
     57488,
     57489]

    def Validate(self, typeID, skipNoBlueprint = False, onlyCheckExcessMaterials = True):
        if not self.IsRefinableOrRecyclable(typeID):
            return (True, 'Check skipped - cannot be reprocessed')
        typeEntries, portionSize = self.GetTypeMaterials(typeID)
        bpEntries = defaultdict(float)
        try:
            batchSize = self.GetBlueprintMaterials(typeID, bpEntries)
        except UserError:
            if typeEntries:
                return (bool(skipNoBlueprint), 'Check not possible - no blueprint found, but reprocessing materials authored!')
            else:
                return (True, 'Check skipped - no blueprint found, and no reprocessing materials authored')

        if batchSize > portionSize:
            factor = float(batchSize) / portionSize
            bpEntries.update(((key, value / factor) for key, value in bpEntries.iteritems()))
        result, skipped = self.CompareEntries(typeEntries, bpEntries, onlyCheckExcessMaterials)
        success = len(result) == 0
        resultString = self.FormatResult(result, skipped)
        return (success, resultString)

    def FormatResult(self, result, skipped):
        resultString = ''
        for key, value in result.iteritems():
            if value > 0:
                resultString += '%s(%s): %s units too much; ' % (evetypes.GetName(key), key, value)
            else:
                resultString += '%s(%s): %s units missing; ' % (evetypes.GetName(key), key, -value)

        return resultString

    def CompareEntries(self, typeEntries, bpEntries, onlyCheckExcessMaterials):
        result = {}
        skipped = 0
        for key, value in typeEntries.iteritems():
            if key in bpEntries:
                diff = value - bpEntries[key]
                if diff > 0:
                    result[key] = diff
                if diff < 0 and not onlyCheckExcessMaterials:
                    result[key] = diff
                del bpEntries[key]
            else:
                result[key] = typeEntries[key]

        if not onlyCheckExcessMaterials:
            for key, value in bpEntries.iteritems():
                if evetypes.GetCategoryID(key) in self.skippedMaterialCategories:
                    skipped += 1
                elif evetypes.GetGroupID(key) in self.skippedMaterialGroups:
                    skipped += 1
                elif key in self.skippedMaterialTypes:
                    skipped += 1
                else:
                    result[key] = -value

        return (result, skipped)

    def IsRefinableOrRecyclable(self, typeID):
        itemOptions = get_reprocessing_options(typeID)
        return itemOptions.isRecyclable or itemOptions.isRefinable

    def GetTypeMaterials(self, typeID):
        typeEntries = {}
        materials = get_type_materials_by_id(typeID)
        portionSize = evetypes.GetPortionSize(typeID)
        for material in materials:
            typeEntries[material.materialTypeID] = material.quantity

        return (typeEntries, portionSize)

    def GetBlueprintMaterials(self, typeID, bpEntries, depth = 0, quantity = 1):
        try:
            bpData = cfg.blueprints.index('productTypeID', typeID)
        except:
            raise UserError('BlueprintDoesNotExist')

        if not bpData or not evetypes.IsPublished(bpData.blueprintTypeID):
            raise UserError('BlueprintDoesNotExist')
        job = industry.Job(bpData, 1)
        batchSize = job.products[0].quantity
        if quantity > 1:
            quantity = quantity / batchSize
        for material in job.materials:
            if evetypes.GetCategoryID(material.typeID) in self.expandedCategories and depth < 3:
                self.GetBlueprintMaterials(material.typeID, bpEntries, depth=depth + 1, quantity=material.quantity)
            else:
                bpEntries[material.typeID] += material.quantity * quantity

        return batchSize


class BasicVolumeCheck(object):
    displayName = 'Basic Volume Check'
    options = [['minimumValue',
      'Minimum value',
      OPTION_FLOAT,
      0.1], ['maximumValue',
      'Maximum value',
      OPTION_FLOAT,
      20]]

    def Validate(self, typeID, minimumValue = 0.0, maximumValue = 999999.0):
        valueRange = [minimumValue, maximumValue]
        success, result = CheckVolumeRange(typeID, valueRange)
        return (success, result)


class BasicAttributeCheck(object):
    displayName = 'Check Attribute by Name'
    options = [['minimumValue',
      'Minimum value',
      OPTION_FLOAT,
      0.1], ['maximumValue',
      'Maximum value',
      OPTION_FLOAT,
      20], ['attributeName',
      'Attribute name',
      OPTION_STRING,
      'agility']]

    def Validate(self, typeID, minimumValue = 0.0, maximumValue = 999999.0, attributeName = 'agility'):
        attributeID = self.GetAttributeFromName(attributeName)
        if not attributeID:
            raise UserError('AttributeDoesNotExist')
        attributeDict = sm.GetService('info').GetAttributeDictForType(typeID)
        try:
            attributeValue = attributeDict[attributeID]
        except KeyError:
            result = 'Attribute not authored'
            return (False, result)

        success = minimumValue <= attributeValue <= maximumValue
        result = 'Attribute value: %s' % attributeValue
        return (success, result)

    def GetAttributeFromName(self, attributeName):
        possibleAttr = [ a.attributeID for a in dogma_data.get_all_attributes() if a.name == attributeName ]
        if possibleAttr:
            return possibleAttr[0]
        else:
            return None


class ShipCheck(object):
    displayName = 'Check ships for base attributes'
    options = []
    PACKAGEDVOLUME = 'Volume packaged'
    SIZE_S = 'S'
    SIZE_M = 'M'
    SIZE_L = 'L'
    SIZE_XL = 'XL'
    DEFAULT_VALUE = 'Default'
    SPECIAL_GROUPS = 'Special'
    shipSizeMapping = {0: None,
     1: SIZE_S,
     2: SIZE_M,
     3: SIZE_L,
     4: SIZE_XL}
    specialShipGroups = [invconst.groupShuttle,
     invconst.groupRookieship,
     invconst.groupStrategicCruiser,
     invconst.groupPrototypeExplorationShip]
    rangedAttributes = {dogmaconst.attributeRadius: {DEFAULT_VALUE: [10, 10000],
                                  SIZE_S: [10, 170],
                                  SIZE_M: [75, 700],
                                  SIZE_L: [200, 700],
                                  SIZE_XL: [500, 10000]},
     dogmaconst.attributeCapacity: {DEFAULT_VALUE: [0.0, 50000000]},
     dogmaconst.attributeMass: {DEFAULT_VALUE: [50, 200000000],
                                SIZE_XL: [200000000, 5000000000L]},
     dogmaconst.attributeVolume: {DEFAULT_VALUE: [1000, 1000000],
                                  SIZE_S: [10000, 100000],
                                  SIZE_M: [50000, 500000],
                                  SIZE_L: [100000, 15000000],
                                  SIZE_XL: [10000000, 200000000]},
     PACKAGEDVOLUME: {DEFAULT_VALUE: [500, 1000000],
                      SIZE_XL: [1000000, 10000000]},
     dogmaconst.attributeEmDamageResonance: {DEFAULT_VALUE: [0.6, 1]},
     dogmaconst.attributeExplosiveDamageResonance: {DEFAULT_VALUE: [0.6, 1]},
     dogmaconst.attributeKineticDamageResonance: {DEFAULT_VALUE: [0.6, 1]},
     dogmaconst.attributeThermalDamageResonance: {DEFAULT_VALUE: [0.6, 1]},
     dogmaconst.attributeHp: {DEFAULT_VALUE: [10, 1000000],
                              SIZE_S: [100, 10000],
                              SIZE_M: [100, 10000],
                              SIZE_L: [4000, 50000],
                              SIZE_XL: [10000, 1000000]},
     dogmaconst.attributeStructureUniformity: {DEFAULT_VALUE: [1, 1]},
     dogmaconst.attributeArmorEmDamageResonance: {DEFAULT_VALUE: [0.1, 1]},
     dogmaconst.attributeArmorExplosiveDamageResonance: {DEFAULT_VALUE: [0.1, 1]},
     dogmaconst.attributeArmorKineticDamageResonance: {DEFAULT_VALUE: [0.1, 1]},
     dogmaconst.attributeArmorThermalDamageResonance: {DEFAULT_VALUE: [0.1, 1]},
     dogmaconst.attributeArmorHP: {DEFAULT_VALUE: [100, 1000000],
                                   SIZE_S: [100, 10000],
                                   SIZE_M: [100, 10000],
                                   SIZE_L: [4000, 50000],
                                   SIZE_XL: [10000, 1000000]},
     dogmaconst.attributeArmorUniformity: {DEFAULT_VALUE: [0.75, 0.75]},
     dogmaconst.attributeShieldEmDamageResonance: {DEFAULT_VALUE: [0.1, 1]},
     dogmaconst.attributeShieldExplosiveDamageResonance: {DEFAULT_VALUE: [0.1, 1]},
     dogmaconst.attributeShieldKineticDamageResonance: {DEFAULT_VALUE: [0.1, 1]},
     dogmaconst.attributeShieldThermalDamageResonance: {DEFAULT_VALUE: [0.1, 1]},
     dogmaconst.attributeShieldCapacity: {DEFAULT_VALUE: [100, 1000000],
                                          SIZE_S: [100, 10000],
                                          SIZE_M: [100, 10000],
                                          SIZE_L: [4000, 50000],
                                          SIZE_XL: [10000, 1000000]},
     dogmaconst.attributeShieldUniformity: {DEFAULT_VALUE: [0.75, 0.75],
                                            SPECIAL_GROUPS: [0.5, 0.75]},
     dogmaconst.attributeShieldRechargeRate: {DEFAULT_VALUE: [10000, 50000000]},
     dogmaconst.attributeCapacitorCapacity: {DEFAULT_VALUE: [100, 1000000]},
     dogmaconst.attributeRechargeRate: {DEFAULT_VALUE: [10000, 10000000]},
     dogmaconst.attributeDroneBandwidth: {DEFAULT_VALUE: [0, 5000]},
     dogmaconst.attributeDroneCapacity: {DEFAULT_VALUE: [0, 7500]},
     dogmaconst.attributeCpuOutput: {DEFAULT_VALUE: [0, 100000]},
     dogmaconst.attributePowerOutput: {DEFAULT_VALUE: [0, 2000000]},
     dogmaconst.attributeHiSlots: {DEFAULT_VALUE: [0, 8],
                                   SPECIAL_GROUPS: []},
     dogmaconst.attributeMedSlots: {DEFAULT_VALUE: [0, 8],
                                    SPECIAL_GROUPS: []},
     dogmaconst.attributeLowSlots: {DEFAULT_VALUE: [0, 8],
                                    SPECIAL_GROUPS: []},
     dogmaconst.attributeRigSlots: {DEFAULT_VALUE: [0, 3],
                                    SPECIAL_GROUPS: []},
     dogmaconst.attributeUpgradeCapacity: {DEFAULT_VALUE: [0, 400]},
     dogmaconst.attributeTurretSlotsLeft: {DEFAULT_VALUE: [0, 8]},
     dogmaconst.attributeLauncherSlotsLeft: {DEFAULT_VALUE: [0, 8]},
     dogmaconst.attributePowerLoad: {DEFAULT_VALUE: [0, 0]},
     dogmaconst.attributeCpuLoad: {DEFAULT_VALUE: [0, 0]},
     dogmaconst.attributeDamage: {DEFAULT_VALUE: [0, 0]},
     dogmaconst.attributeAgility: {DEFAULT_VALUE: [0.01, 1000],
                                   SIZE_S: [2, 8],
                                   SIZE_M: [0.3, 2],
                                   SIZE_L: [0.05, 0.5],
                                   SIZE_XL: [0.02, 0.2]},
     dogmaconst.attributeMaxVelocity: {DEFAULT_VALUE: [10, 500]},
     dogmaconst.attributeBaseWarpSpeed: {DEFAULT_VALUE: [1.0, 1.0]},
     dogmaconst.attributeWarpSpeedMultiplier: {DEFAULT_VALUE: [1.0, 20.0]},
     dogmaconst.attributeWarpCapacitorNeed: {DEFAULT_VALUE: [1e-08, 0.001]},
     dogmaconst.attributeHeatAttenuationHi: {DEFAULT_VALUE: [0.0, 0.85],
                                             SPECIAL_GROUPS: []},
     dogmaconst.attributeHeatAttenuationMed: {DEFAULT_VALUE: [0.0, 0.85],
                                              SPECIAL_GROUPS: []},
     dogmaconst.attributeHeatAttenuationLow: {DEFAULT_VALUE: [0.0, 0.85],
                                              SPECIAL_GROUPS: []},
     dogmaconst.attributeHeatCapacityHi: {DEFAULT_VALUE: [100, 100]},
     dogmaconst.attributeHeatCapacityMed: {DEFAULT_VALUE: [100, 100]},
     dogmaconst.attributeHeatCapacityLow: {DEFAULT_VALUE: [100, 100]},
     dogmaconst.attributeHeatDissipationRateHi: {DEFAULT_VALUE: [0.01, 0.01]},
     dogmaconst.attributeHeatDissipationRateMed: {DEFAULT_VALUE: [0.01, 0.01]},
     dogmaconst.attributeHeatDissipationRateLow: {DEFAULT_VALUE: [0.01, 0.01]},
     dogmaconst.attributeHeatGenerationMultiplier: {DEFAULT_VALUE: [0.1, 1.0]},
     dogmaconst.attributeMaxLockedTargets: {DEFAULT_VALUE: [0, 14]},
     dogmaconst.attributeMaxTargetRange: {DEFAULT_VALUE: [0, 200000],
                                          SIZE_XL: [0, 6000000]},
     dogmaconst.attributeScanGravimetricStrength: {DEFAULT_VALUE: [0, 2000]},
     dogmaconst.attributeScanLadarStrength: {DEFAULT_VALUE: [0, 2000]},
     dogmaconst.attributeScanMagnetometricStrength: {DEFAULT_VALUE: [0, 2000]},
     dogmaconst.attributeScanRadarStrength: {DEFAULT_VALUE: [0, 2000]},
     dogmaconst.attributeScanResolution: {DEFAULT_VALUE: [0, 1000],
                                          SPECIAL_GROUPS: []},
     dogmaconst.attributeSignatureRadius: {DEFAULT_VALUE: [20, 30000]}}

    def Validate(self, typeID):
        success = True
        resultList = []
        attributeDict = sm.GetService('info').GetAttributeDictForType(typeID)
        size = self.GetShipSizeFromRigSize(attributeDict)
        for attribute, rangeDict in self.rangedAttributes.iteritems():
            if self.SPECIAL_GROUPS in rangeDict and evetypes.GetGroupID(typeID) in self.specialShipGroups:
                valueRange = rangeDict[self.SPECIAL_GROUPS]
            elif size in rangeDict:
                valueRange = rangeDict[size]
            else:
                valueRange = rangeDict[self.DEFAULT_VALUE]
            if not valueRange:
                continue
            if attribute == dogmaconst.attributeVolume:
                s, res = CheckVolumeRange(typeID, valueRange)
            elif attribute == self.PACKAGEDVOLUME:
                s, res = CheckPackagedVolume(typeID, valueRange)
            else:
                s, res = CheckAttributeRange(attributeDict, attribute, valueRange)
            success = success and s
            if res:
                resultList.append(res)

        result = ', '.join(resultList)
        return (success, result)

    def GetShipSizeFromRigSize(self, attributeDict):
        attributeID = dogmaconst.attributeRigSize
        try:
            attributeValue = attributeDict[attributeID]
        except KeyError:
            return None

        return self.shipSizeMapping[attributeValue]


class BlueprintCheck(object):
    displayName = 'Check blueprints - still very limited'
    options = []
    rangedAttributes = {dogmaconst.attributeVolume: [0.01, 0.01]}

    def Validate(self, typeID):
        success = True
        resultList = []
        attributeDict = sm.GetService('info').GetAttributeDictForType(typeID)
        for attribute, valueRange in self.rangedAttributes.iteritems():
            if attribute == dogmaconst.attributeVolume:
                s, res = CheckVolumeRange(typeID, valueRange)
            else:
                s, res = CheckAttributeRange(attributeDict, attribute, valueRange)
            success = success and s
            if res:
                resultList.append(res)

        result = ', '.join(resultList)
        return (success, result)


validTestScripts = [CheckMaterials,
 BasicVolumeCheck,
 BasicAttributeCheck,
 BlueprintCheck,
 ShipCheck]
