#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\dogma\baseDogmaStaticSvc.py
import sys
import bluepy
import dogma.data as dogma_data
import evetypes
import telemetry
from carbon.common.script.sys.service import Service
from dogma.data import get_effects_indexed_by_effect_id_and_type_id, get_effects_indexed_by_type_id_and_effect_id
from eve.common.lib import appConst as const
from eve.common.script.sys.idCheckers import IsModule
from evetypes.skills import get_dogma_required_skills
from spacecomponents.common.helper import HasIgnoreFittingRestrictionsComponent

class BaseDogmaStaticSvc(Service):
    __guid__ = 'svc.baseDogmaStaticSvc'

    def __init__(self):
        Service.__init__(self)
        self.attributes = {}
        self.attributesByName = {}
        self.attributesByTypeAttribute = {}
        self.effects = {}
        self.unwantedEffects = {const.effectHiPower: True,
         const.effectLoPower: True,
         const.effectMedPower: True,
         const.effectSkillEffect: True}

    def Run(self, *args):
        self.Load()
        self._MonitorStaticDataChanges()

    def _MonitorStaticDataChanges(self):
        dogma_data.DogmaAttributes.ConnectToOnReload(self._ReloadDogmaData)
        dogma_data.DogmaEffects.ConnectToOnReload(self._ReloadDogmaData)
        dogma_data.TypeDogma.ConnectToOnReload(self._ReloadDogmaData)

    def _ReloadDogmaData(self):
        dogma_data.refresh_dogma()
        self.LoadAttributes()
        self.LoadTypeAttributes()
        self.LoadEffects()
        self.LoadTypeEffects(run=False)

    def Load(self):
        with bluepy.Timer('LoadAttributes'):
            self.LoadAttributes()
        with bluepy.Timer('LoadTypeAttributes'):
            self.LoadTypeAttributes()
        with bluepy.Timer('LoadEffects'):
            self.LoadEffects()
        with bluepy.Timer('LoadTypeEffects'):
            self.LoadTypeEffects(run=True)
        self.crystalGroupIDs = cfg.GetCrystalGroups()
        self.controlBunkersByFactionID = {}
        for typeID in evetypes.GetTypeIDsByGroup(const.groupControlBunker):
            factionID = int(self.GetTypeAttribute2(typeID, const.attributeFactionID))
            self.controlBunkersByFactionID[factionID] = typeID

        cgattrs = dogma_data.get_charge_group_attribute_ids()
        self.chargeGroupAttributes = cgattrs
        self.crystalModuleGroupIDs = {}
        for categoryID in (const.categoryModule, const.categoryStructureModule, const.categoryStarbase):
            for groupID in evetypes.GetGroupIDsByCategory(categoryID):
                typeIDs = evetypes.GetTypeIDsByGroup(groupID)
                if len(typeIDs) > 0:
                    typeID = typeIDs.pop()
                    for attributeID in cgattrs:
                        v = self.GetTypeAttribute(typeID, attributeID)
                        if v is not None and v in self.crystalGroupIDs:
                            self.crystalModuleGroupIDs[groupID] = True
                            break

    def LoadAttributes(self):
        self.attributes = dogma_data.get_all_attributes_by_id()
        if len(self.attributes) == 0:
            self.LogError('STATIC DATA MISSING: Dogma Attributes')
        self.attributesByName = dogma_data.get_all_attributes_by_name()
        self.attributesByCategory = dogma_data.get_attribute_list_by_data_type()
        self.chargedAttributes = dogma_data.get_charge_recharge_time_attributes_by_id()
        self.attributesRechargedByAttribute = dogma_data.get_attributes_by_charge_recharge_time_id()
        self.attributesByIdx = {}
        self.idxByAttribute = {}
        self.canFitShipGroupAttributes = []
        self.allowedDroneGroupAttributes = []
        self.chargeGroupAttributes = []
        for att in self.attributesByCategory[const.dgmAttrCatGroup]:
            attributeName = att.name
            if attributeName.startswith('canFitShipGroup'):
                self.canFitShipGroupAttributes.append(att.attributeID)
            elif attributeName.startswith('allowedDroneGroup'):
                self.allowedDroneGroupAttributes.append(att.attributeID)
            elif attributeName.startswith('chargeGroup'):
                self.chargeGroupAttributes.append(att.attributeID)

        self.canFitShipTypeAttributes = []
        self.requiredSkillAttributes = {}
        for att in self.attributesByCategory[const.dgmAttrCatType]:
            attributeName = att.name
            if attributeName == 'fitsToShipType' or attributeName.startswith('canFitShipType'):
                self.canFitShipTypeAttributes.append(att.attributeID)
            elif attributeName.startswith('requiredSkill'):
                levelAttribute = self.attributesByName[attributeName + 'Level']
                self.requiredSkillAttributes[att.attributeID] = levelAttribute.attributeID

        self.shipHardwareModifierAttribs = [(const.attributeHiSlots, const.attributeHiSlotModifier),
         (const.attributeMedSlots, const.attributeMedSlotModifier),
         (const.attributeLowSlots, const.attributeLowSlotModifier),
         (const.attributeTurretSlotsLeft, const.attributeTurretHardpointModifier),
         (const.attributeLauncherSlotsLeft, const.attributeLauncherHardPointModifier)]
        self.resistanceAttributesByLayer = {}
        for attributeID, layerName, hpAttributeID, uniformityAttributeID in ((const.attributeShieldCharge,
          'Shield',
          const.attributeShieldCapacity,
          const.attributeShieldUniformity), (const.attributeArmorDamage,
          'Armor',
          const.attributeArmorHP,
          const.attributeArmorUniformity), (const.attributeDamage,
          '',
          const.attributeHp,
          const.attributeStructureUniformity)):
            self.resistanceAttributesByLayer[attributeID] = [ getattr(const, 'attribute%s%s' % (layerName, resName)) for resName in ('EmDamageResonance', 'ExplosiveDamageResonance', 'KineticDamageResonance', 'ThermalDamageResonance') ]

        self.damageAttributes = (const.attributeEmDamage,
         const.attributeExplosiveDamage,
         const.attributeKineticDamage,
         const.attributeThermalDamage)
        self.damageStateAttributes = (const.attributeDamage, const.attributeArmorDamage, const.attributeShieldCharge)
        self.layerResAttributesByDamage = {}
        for layerAttributeID, resAttribs in self.resistanceAttributesByLayer.iteritems():
            self.layerResAttributesByDamage[layerAttributeID] = zip(self.damageAttributes, resAttribs)

    def LoadEffects(self):
        self.effects = dogma_data.get_all_effects_by_id()
        if len(self.effects) == 0:
            self.LogError('STATIC DATA MISSING: Dogma Effects')
        self.effectsByName = dogma_data.get_all_effects_by_name()

    def LoadTypeEffects(self, run = False):
        self.effectsByType = get_effects_indexed_by_type_id_and_effect_id()
        self.typesByEffect = get_effects_indexed_by_effect_id_and_type_id()
        self.passiveFilteredEffectsByType = {}
        for typeID in self.effectsByType.iterkeys():
            passiveEffects = []
            for effectID in self.effectsByType[typeID].iterkeys():
                if self.unwantedEffects.has_key(effectID):
                    continue
                effect = self.effects[effectID]
                if effect.effectCategory in [const.dgmEffPassive, const.dgmEffSystem]:
                    passiveEffects.append(effectID)

            if len(passiveEffects):
                self.passiveFilteredEffectsByType[typeID] = passiveEffects

        defaultEffect = {}
        for typeID2, effects in dogma_data.get_all_type_ids_and_effects():
            for effect in effects:
                if effect.isDefault:
                    defaultEffect[typeID2] = effect.effectID

        self.defaultEffectByType = defaultEffect

    def LoadAllTypeAttributes(self):
        raise NotImplementedError('LoadAllTypeAttributes - not implemented')

    def LoadSpecificTypeAttributes(self, typeID, attributeID, newRow):
        raise NotImplementedError('LoadSpecificTypeAttributes - not implemented')

    def LoadTypeAttributes(self, typeID = None, attributeID = None, newRow = None):
        if typeID is None:
            self.LoadAllTypeAttributes()
        else:
            self.LoadSpecificTypeAttributes(typeID, attributeID, newRow)

    def GetTypeAttribute(self, typeID, attributeID, defaultValue = None):
        return dogma_data.get_type_attribute(typeID, attributeID, defaultValue)

    def GetTypeAttribute2(self, typeID, attributeID):
        try:
            return self.attributesByTypeAttribute[typeID][attributeID]
        except KeyError:
            return self.attributes[attributeID].defaultValue

    def GetTypeAttributes(self, typeID):
        try:
            return self.attributesByTypeAttribute[typeID]
        except KeyError:
            return {}

    @telemetry.ZONE_METHOD
    def GetRequiredSkills(self, typeID):
        return get_dogma_required_skills(typeID)

    def GetEffect(self, effectID):
        return self.effects[effectID]

    def GetEffectTypes(self):
        return self.effects

    def GetEffectType(self, effectID):
        return self.effects[effectID]

    def GetAttributeType(self, attributeID):
        if isinstance(attributeID, str):
            return self.attributesByName[attributeID]
        return self.attributes[attributeID]

    def GetAttributeByName(self, attributeName):
        ret = self.attributesByName[attributeName]
        return ret.attributeID

    def TypeHasAttribute(self, typeID, attributeID):
        return typeID in self.attributesByTypeAttribute and attributeID in self.attributesByTypeAttribute[typeID]

    def TypeGetOrderedEffectIDs(self, typeID, categoryID = None):
        return self.effectsByType[typeID].iterkeys()

    def TypeGetEffects(self, typeID):
        return self.effectsByType.get(typeID, {})

    def TypeExists(self, typeID):
        return typeID in self.attributesByTypeAttribute

    def TypeHasEffect(self, typeID, effectID):
        return self.effectsByType.has_key(typeID) and self.effectsByType[typeID].has_key(effectID)

    def GetAttributesByCategory(self, categoryID):
        return self.attributesByCategory.get(categoryID, [])

    def EffectGetTypes(self, effectID):
        return self.typesByEffect.get(effectID, {})

    def EffectGetModuleGroups(self, effectID):
        moduleGroups = []
        for typeID in self.typesByEffect.get(effectID, {}):
            categoryID = evetypes.GetCategoryID(typeID)
            if IsModule(categoryID):
                groupID = evetypes.GetGroupID(typeID)
                if groupID not in moduleGroups:
                    moduleGroups.append(groupID)

        return moduleGroups

    def AttributeGetTypes(self, attributeID):
        return self.typesByAttribute.get(attributeID, {})

    def GetCanFitShipGroups(self, typeID):
        rtn = []
        for att in self.canFitShipGroupAttributes:
            try:
                rtn.append(self.attributesByTypeAttribute[typeID][att])
            except KeyError:
                sys.exc_clear()

        return rtn

    def GetChargeGroupAttributes(self):
        return self.chargeGroupAttributes

    def GetCanFitShipTypes(self, typeID):
        rtn = []
        for att in self.canFitShipTypeAttributes:
            try:
                rtn.append(self.attributesByTypeAttribute[typeID][att])
            except KeyError:
                sys.exc_clear()

        return rtn

    def CanFitModuleToShipTypeOrGroup(self, moduleTypeID, shipTypeID, shipGroupID):
        canFitShipGroups = self.GetCanFitShipGroups(moduleTypeID)
        canFitShipTypes = self.GetCanFitShipTypes(moduleTypeID)
        if HasIgnoreFittingRestrictionsComponent(shipTypeID):
            return True
        if not canFitShipGroups and not canFitShipTypes:
            return True
        if canFitShipGroups and shipGroupID in canFitShipGroups:
            return True
        if canFitShipTypes and shipTypeID in canFitShipTypes:
            return True
        return False

    def GetAllowedDroneGroups(self, typeID):
        groups = []
        attributes = self.attributesByTypeAttribute.get(typeID)
        if attributes:
            for attributeID in self.allowedDroneGroupAttributes:
                value = attributes.get(attributeID)
                if value:
                    groups.append(int(value))

        return groups

    def GetDefaultEffect(self, typeID):
        return self.defaultEffectByType[typeID]

    def GetShipHardwareModifierAttribs(self):
        return self.shipHardwareModifierAttribs

    def GetValidChargeGroupsForType(self, typeID):
        ret = set()
        for attributeID in self.chargeGroupAttributes:
            try:
                ret.add(int(self.GetTypeAttribute(typeID, attributeID)))
            except TypeError:
                pass

        return ret

    def GetSkillModifiedAttributePercentageValue(self, attributeID, modifyingAttributeID, skillTypeID, skillRecord = None):
        percentageMod = 1.0
        skillLevel = 0
        if skillRecord:
            skillLevel = skillRecord.effectiveSkillLevel
            try:
                percentageMod = (100 + self.GetTypeAttribute(skillTypeID, modifyingAttributeID, None) * skillLevel) / 100.0
            except TypeError as e:
                self.LogError('dogmaStaticMgr::GetSkillModifiedAttributePercentageValue.Failed calculating modification! %s' % e)
                percentageMod = 1.0

            if not 0.0 <= percentageMod <= 1.0:
                self.LogError('dogmaStaticMgr::GetSkillModifiedAttributePercentageValue.Value %s not a percentile!' % percentageMod)
                percentageMod = 1.0
        return percentageMod

    def GetPassiveFilteredEffectsByType(self, typeID):
        return self.passiveFilteredEffectsByType.get(typeID, [])
