#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\effects\__init__.py
import dogma.data as dogma_data
from eve.common.script.mgt import buffBarConst
import evetypes
from dogma import const
MODIFIER_FUNCTIONS = {'LocationRequiredSkillModifier': 'on all items located in <b>{domain}</b> requiring skill <b>{skillTypeID}</b>',
 'LocationGroupModifier': 'on all items located in <b>{domain}</b> in group <b>{groupID}</b>',
 'OwnerRequiredSkillModifier': 'on all items owned by <b>{domain}</b> that require skill <b>{skillTypeID}</b>',
 'ItemModifier': '<b>{domain}</b>'}
MODIFIER_ATTRIBUTE_NAMES = ['domain',
 'func',
 'modifiedAttributeID',
 'modifyingAttributeID',
 'operation',
 'effectID',
 'groupID',
 'skillTypeID']

def _GetModifierDict(modifier):
    ret = {}
    for key in MODIFIER_ATTRIBUTE_NAMES:
        value = getattr(modifier, key)
        if key in ('modifiedAttributeID', 'modifyingAttributeID'):
            newValue = '{} ({})'.format(dogma_data.get_attribute(value).name, value)
        elif key == 'domain':
            if value is None:
                newValue = 'self'
            else:
                newValue = value.replace('ID', '')
        elif key == 'skillTypeID' and value is not None:
            newValue = evetypes.GetName(value)
        elif key == 'groupID' and value is not None:
            newValue = evetypes.GetGroupNameByGroup(value)
        else:
            newValue = value
        ret[key] = newValue

    ret['domainInfo'] = MODIFIER_FUNCTIONS.get(modifier.func, ' UNKNOWN {func}').format(**ret)
    return ret


def IterReadableModifierStrings(modifiers):
    for modifier in modifiers:
        if modifier.func in MODIFIER_FUNCTIONS:
            formatDict = _GetModifierDict(modifier)
            yield 'Modifies <b>{modifiedAttributeID}</b> on {domainInfo} with attribute <b>{modifyingAttributeID}</b>'.format(**formatDict)
        elif modifier.func == 'EffectStopper':
            effectID = modifier.effectID
            yield 'Forcibly stops effect %s' % dogma_data.get_effect_name(effectID)


def IsCloakingEffect(effectID):
    return effectID in [const.effectCloaking, const.effectCloakingWarpSafe, const.effectCloakingPrototype]


class Effect(object):
    __guid__ = 'dogmaXP.Effect'
    isPythonEffect = True
    __modifier_only__ = False
    __modifies_character__ = False
    __modifies_ship__ = False
    __modifier_domain_other__ = False
    MODIFIER_CHANGES = []
    LOCATION_AND_GROUP_MODIFIER_CHANGES = []
    SKILL_MODIFIER_CHANGES_FOR_LOCATION = []
    SKILL_MODIFIER_CHANGES_FOR_OWNER = []

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass

    def PreStartChecks(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass

    def StartChecks(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass

    def AddModifiers(self, dogmaLM, toItemID, fromItemID):
        for operation, toAttribID, fromAttribID in self.MODIFIER_CHANGES:
            dogmaLM.AddModifier(operation, toItemID, toAttribID, fromItemID, fromAttribID)

    def RemoveModifiers(self, dogmaLM, toItemID, fromItemID):
        for operation, toAttribID, fromAttribID in self.MODIFIER_CHANGES:
            dogmaLM.RemoveModifier(operation, toItemID, toAttribID, fromItemID, fromAttribID)

    def AddLocationGroupModifiers(self, dogmaLM, toLocationID, fromItemID):
        for operation, groupID, toAttribID, fromAttribID in self.LOCATION_AND_GROUP_MODIFIER_CHANGES:
            dogmaLM.AddLocationGroupModifier(operation, toLocationID, groupID, toAttribID, fromItemID, fromAttribID)

    def RemoveLocationGroupModifiers(self, dogmaLM, toLocationID, fromItemID):
        for operation, groupID, toAttribID, fromAttribID in self.LOCATION_AND_GROUP_MODIFIER_CHANGES:
            dogmaLM.RemoveLocationGroupModifier(operation, toLocationID, groupID, toAttribID, fromItemID, fromAttribID)

    def AddLocationRequiredSkillModifiers(self, dogmaLM, toLocationID, fromItemID):
        for operation, skillTypeID, affectedAttributeID, affectingAttributeID in self.SKILL_MODIFIER_CHANGES_FOR_LOCATION:
            dogmaLM.AddLocationRequiredSkillModifier(operation, toLocationID, skillTypeID, affectedAttributeID, fromItemID, affectingAttributeID)

    def RemoveLocationRequiredSkillModifiers(self, dogmaLM, toLocationID, fromItemID):
        for operation, skillTypeID, affectedAttributeID, affectingAttributeID in self.SKILL_MODIFIER_CHANGES_FOR_LOCATION:
            dogmaLM.RemoveLocationRequiredSkillModifier(operation, toLocationID, skillTypeID, affectedAttributeID, fromItemID, affectingAttributeID)

    def AddOwnerRequiredSkillModifiers(self, dogmaLM, ownerID, fromItemID):
        for operation, affectedSkillTypeID, affectedAttributeID, affectingAttributeID in self.SKILL_MODIFIER_CHANGES_FOR_OWNER:
            dogmaLM.AddOwnerRequiredSkillModifier(operation, ownerID, affectedSkillTypeID, affectedAttributeID, fromItemID, affectingAttributeID)

    def RemoveOwnerRequiredSkillModifiers(self, dogmaLM, ownerID, fromItemID):
        for operation, affectedSkillTypeID, affectedAttributeID, affectingAttributeID in self.SKILL_MODIFIER_CHANGES_FOR_OWNER:
            dogmaLM.RemoveOwnerRequiredSkillModifier(operation, ownerID, affectedSkillTypeID, affectedAttributeID, fromItemID, affectingAttributeID)

    def RefreshEffect(self, dogmaLM, env, itemID, shipID):
        pass


def GetName(effectID):
    return dogma_data.get_effect_name(effectID)


def IsDefault(typeID, effectID):
    for typeEffect in dogma_data.get_type_effects(typeID):
        if effectID == typeEffect.effectID:
            if typeEffect.isDefault:
                return True
            else:
                return False

    raise KeyError()


def GetEwarTypeByEffectID(effectID):
    effect = dogma_data.get_effect(effectID)
    if effect.electronicChance:
        return buffBarConst.Slot_Electronic
    if effect.propulsionChance:
        return buffBarConst.Slot_Webify
    ewarType = BUFF_SLOTS_BY_EFFECT_ID.get(effectID, None)
    return ewarType


BUFF_SLOTS_BY_EFFECT_ID = {const.effectShipModuleFocusedWarpDisruptionScript: buffBarConst.Slot_WarpScrambler,
 const.effectShipModuleFocusedWarpScramblingScript: buffBarConst.Slot_WarpScramblerMWD,
 const.effectEwTargetPaint: buffBarConst.Slot_EwTargetPaint,
 const.effectTargetMaxTargetRangeAndScanResolutionBonusHostile: buffBarConst.Slot_EwRemoteSensorDamp,
 const.effectTargetGunneryMaxRangeAndTrackingSpeedBonusHostile: buffBarConst.Slot_EwTrackingDisrupt,
 const.effectTargetGunneryMaxRangeAndTrackingSpeedAndFalloffBonusHostile: buffBarConst.Slot_EwTrackingDisrupt,
 const.effectTurretWeaponRangeFalloffTrackingSpeedMultiplyTargetHostile: buffBarConst.Slot_EwTrackingDisrupt,
 const.effectEntitySensorDampen: buffBarConst.Slot_EwRemoteSensorDamp,
 const.effectSensorBoostTargetedHostile: buffBarConst.Slot_EwRemoteSensorDamp,
 const.effectNpcEntityTrackingDisruptor: buffBarConst.Slot_EwTrackingDisrupt,
 const.effectGuidanceDisrupt: buffBarConst.Slot_EwGuidanceDisrupt,
 const.effectEntityTargetPaint: buffBarConst.Slot_EwTargetPaint,
 const.effectWarpDisrupt: buffBarConst.Slot_WarpScrambler,
 const.effectDecreaseTargetSpeed: buffBarConst.Slot_Webify,
 const.effectWarpScrambleForEntity: buffBarConst.Slot_WarpScrambler,
 const.effectModifyTargetSpeed2: buffBarConst.Slot_Webify,
 const.effectConcordWarpScramble: buffBarConst.Slot_WarpScrambler,
 const.effectConcordModifyTargetSpeed: buffBarConst.Slot_Webify,
 const.effectWarpScrambleBlockMWDWithNPCEffect: buffBarConst.Slot_WarpScramblerMWD,
 const.effectWarpDisruptSphere: buffBarConst.Slot_FocusedWarpScrambler,
 const.effectLeech: buffBarConst.Slot_EwEnergyVampire,
 const.effectEnergyDestabilizationNew: buffBarConst.Slot_EwEnergyNeut,
 const.effectEntityCapacitorDrain: buffBarConst.Slot_EwEnergyNeut,
 const.effectEnergyDestabilizationForStructure: buffBarConst.Slot_EwEnergyNeut,
 const.effectEnergyNeutralizerFalloff: buffBarConst.Slot_EwEnergyNeut,
 const.effectEnergyNosferatuFalloff: buffBarConst.Slot_EwEnergyVampire,
 const.effectWarpScrambleForStructure: buffBarConst.Slot_WarpScrambler,
 const.effectDecreaseTargetSpeedForStructures: buffBarConst.Slot_Webify,
 const.effectEssWarpScramble: buffBarConst.Slot_WarpScrambler,
 const.effectWarpScrambleTargetMWDBlockActivationForEntity: buffBarConst.Slot_WarpScramblerMWD,
 const.effectEwTestEffectJam: buffBarConst.Slot_Electronic,
 const.effectEntityTargetJam: buffBarConst.Slot_Electronic,
 const.effectFighterAbilityECM: buffBarConst.Slot_Electronic,
 const.effectFighterAbilityEnergyNeutralizer: buffBarConst.Slot_EwEnergyNeut,
 const.effectFighterAbilityStasisWebifier: buffBarConst.Slot_Webify,
 const.effectFighterAbilityWarpDisruption: buffBarConst.Slot_WarpScrambler,
 const.effectFighterAbilityTackle: buffBarConst.Slot_FighterTackle,
 const.effectRemoteSensorDampFalloff: buffBarConst.Slot_EwRemoteSensorDamp,
 const.effectRemoteTargetPaintFalloff: buffBarConst.Slot_EwTargetPaint,
 const.effectShipModuleTrackingDisruptor: buffBarConst.Slot_EwTrackingDisrupt,
 const.effectRemoteWebifierFalloff: buffBarConst.Slot_Webify,
 const.effectShipModuleGuidanceDisruptor: buffBarConst.Slot_EwGuidanceDisrupt,
 const.effectRemoteECMFalloff: buffBarConst.Slot_Electronic,
 const.effectEntityECMFalloff: buffBarConst.Slot_Electronic,
 const.effectStructureEwEffectJam: buffBarConst.Slot_Electronic,
 const.effectStructureEwTargetPaint: buffBarConst.Slot_EwTargetPaint,
 const.effectStructureEnergyNeutralizerFalloff: buffBarConst.Slot_EwEnergyNeut,
 const.effectStructureWarpScrambleBlockMWDWithNPCEffect: buffBarConst.Slot_WarpScramblerMWD,
 const.effectStructureDecreaseTargetSpeed: buffBarConst.Slot_Webify,
 const.effectStructureTargetMaxTargetRangeAndScanResolutionBonusHostile: buffBarConst.Slot_EwRemoteSensorDamp,
 const.effectStructureTargetGunneryMaxRangeAndTrackingSpeedAndFalloffBonusHostile: buffBarConst.Slot_EwTrackingDisrupt,
 const.effectStructureModuleEffectStasisWebifier: buffBarConst.Slot_Webify,
 const.effectStructureModuleEffectTargetPainter: buffBarConst.Slot_EwTargetPaint,
 const.effectStructureModuleEffectRemoteSensorDampener: buffBarConst.Slot_EwRemoteSensorDamp,
 const.effectStructureModuleEffectECM: buffBarConst.Slot_Electronic,
 const.effectStructureModuleEffectWeaponDisruption: buffBarConst.Slot_EwTrackingDisrupt,
 const.effectEntityEnergyNeutralizerFalloff: buffBarConst.Slot_EwEnergyNeut,
 const.effectStarbaseEnergyNeutralizerFalloff: buffBarConst.Slot_EwEnergyNeut,
 const.effectRemoteSensorDampEntity: buffBarConst.Slot_EwRemoteSensorDamp,
 const.effectRemoteTargetPaintEntity: buffBarConst.Slot_EwTargetPaint,
 const.effectNpcEntityWeaponDisruptor: buffBarConst.Slot_EwTrackingDisrupt,
 const.effectRemoteWebifierEntity: buffBarConst.Slot_Webify,
 const.effectRemoteTracking: buffBarConst.Slot_RemoteTracking,
 const.effectEnergyTransfer: buffBarConst.Slot_EnergyTransfer,
 const.effectTargetMaxTargetRangeAndScanResolutionBonusAssistance: buffBarConst.Slot_SensorBooster,
 const.effectScanStrengthTargetPercentBonus: buffBarConst.Slot_EccmProjector,
 const.effectShipModuleRemoteHullRepairer: buffBarConst.Slot_RemoteHullRepair,
 const.effectTargetArmorRepair: buffBarConst.Slot_RemoteArmorRepair,
 const.effectShieldTransfer: buffBarConst.Slot_ShieldTransfer,
 const.effectShipModuleRemoteArmorRepairer: buffBarConst.Slot_RemoteArmorRepair,
 const.effectShipModuleRemoteArmorMutadaptiveRepairer: buffBarConst.Slot_RemoteArmorMutadaptiveRepairer,
 const.effectShipModuleAncillaryRemoteArmorRepairer: buffBarConst.Slot_RemoteArmorRepair,
 const.effectShipModuleRemoteCapacitorTransmitter: buffBarConst.Slot_EnergyTransfer,
 const.effectShipModuleRemoteShieldBooster: buffBarConst.Slot_ShieldTransfer,
 const.effectShipModuleAncillaryRemoteShieldBooster: buffBarConst.Slot_ShieldTransfer,
 const.effectRemoteSensorBoostFalloff: buffBarConst.Slot_SensorBooster,
 const.effectShipModuleRemoteTrackingComputer: buffBarConst.Slot_RemoteTracking,
 const.effectRemoteECCMFalloff: buffBarConst.Slot_EccmProjector,
 const.effectStructureTargetMaxTargetRangeAndScanResolutionBonusAssistance: buffBarConst.Slot_SensorBooster,
 const.effectStructureTargetGunneryMaxRangeFalloffTrackingSpeedBonusAssistance: buffBarConst.Slot_RemoteTracking,
 const.effectNpcEntityRemoteHullRepairer: buffBarConst.Slot_RemoteHullRepair,
 const.effectNpcEntityRemoteArmorRepairer: buffBarConst.Slot_RemoteArmorRepair,
 const.effectNpcEntityRemoteShieldBooster: buffBarConst.Slot_ShieldTransfer,
 const.effectNpcBehaviorRemoteArmorRepairer: buffBarConst.Slot_RemoteArmorRepair,
 const.effectNpcBehaviorRemoteCapacitorTransmitter: buffBarConst.Slot_EnergyTransfer,
 const.effectNpcBehaviorRemoteShieldBooster: buffBarConst.Slot_ShieldTransfer,
 const.effectBehaviorECM: buffBarConst.Slot_Electronic,
 const.effectNpcBehaviorEnergyNeutralizer: buffBarConst.Slot_EwEnergyNeut,
 const.effectNpcBehaviorEnergyNosferatu: buffBarConst.Slot_EwEnergyVampire,
 const.effectNpcBehaviorGuidanceDisruptor: buffBarConst.Slot_EwGuidanceDisrupt,
 const.effectBehaviorSensorDampener: buffBarConst.Slot_EwRemoteSensorDamp,
 const.effectBehaviorTargetPainter: buffBarConst.Slot_EwTargetPaint,
 const.effectNpcBehaviorTrackingDisruptor: buffBarConst.Slot_EwTrackingDisrupt,
 const.effectBehaviorWarpDisrupt: buffBarConst.Slot_WarpScrambler,
 const.effectBehaviorWarpScramble: buffBarConst.Slot_WarpScramblerMWD,
 const.effectNpcBehaviorWebifier: buffBarConst.Slot_Webify}
LOG_EVENT_NAMES_FOR_EWAR_EFFECTS = {const.effectShipModuleFocusedWarpDisruptionScript: 'warpScrambler',
 const.effectShipModuleFocusedWarpScramblingScript: 'warpScramblerMWD',
 const.effectEwTargetPaint: 'ewTargetPaint',
 const.effectTargetMaxTargetRangeAndScanResolutionBonusHostile: 'ewRemoteSensorDamp',
 const.effectTargetGunneryMaxRangeAndTrackingSpeedBonusHostile: 'ewTrackingDisrupt',
 const.effectTargetGunneryMaxRangeAndTrackingSpeedAndFalloffBonusHostile: 'ewTrackingDisrupt',
 const.effectTurretWeaponRangeFalloffTrackingSpeedMultiplyTargetHostile: 'ewTrackingDisrupt',
 const.effectEntitySensorDampen: 'ewRemoteSensorDamp',
 const.effectSensorBoostTargetedHostile: 'ewRemoteSensorDamp',
 const.effectNpcEntityTrackingDisruptor: 'ewTrackingDisrupt',
 const.effectGuidanceDisrupt: 'ewGuidanceDisrupt',
 const.effectEntityTargetPaint: 'ewTargetPaint',
 const.effectWarpDisrupt: 'warpDisrupt',
 const.effectDecreaseTargetSpeed: 'webify',
 const.effectWarpScrambleForEntity: 'warpScrambler',
 const.effectModifyTargetSpeed2: 'webify',
 const.effectConcordWarpScramble: 'warpScrambler',
 const.effectConcordModifyTargetSpeed: 'webify',
 const.effectWarpScrambleBlockMWDWithNPCEffect: 'warpScramblerMWD',
 const.effectWarpDisruptSphere: 'focusedWarpScrambler',
 const.effectLeech: 'ewEnergyVampire',
 const.effectEnergyDestabilizationNew: 'ewEnergyNeut',
 const.effectEntityCapacitorDrain: 'ewEnergyNeut',
 const.effectEnergyDestabilizationForStructure: 'ewEnergyNeut',
 const.effectEnergyNeutralizerFalloff: 'ewEnergyNeut',
 const.effectEnergyNosferatuFalloff: 'ewEnergyVampire',
 const.effectWarpScrambleForStructure: 'warpScrambler',
 const.effectDecreaseTargetSpeedForStructures: 'webify',
 const.effectEssWarpScramble: 'warpScrambler',
 const.effectWarpScrambleTargetMWDBlockActivationForEntity: 'warpScramblerMWD',
 const.effectEwTestEffectJam: 'electronic',
 const.effectEntityTargetJam: 'electronic',
 const.effectFighterAbilityECM: 'electronic',
 const.effectFighterAbilityEnergyNeutralizer: 'ewEnergyNeut',
 const.effectFighterAbilityStasisWebifier: 'webify',
 const.effectFighterAbilityWarpDisruption: 'warpScrambler',
 const.effectFighterAbilityTackle: 'fighterTackle',
 const.effectRemoteSensorDampFalloff: 'ewRemoteSensorDamp',
 const.effectRemoteTargetPaintFalloff: 'ewTargetPaint',
 const.effectShipModuleTrackingDisruptor: 'ewTrackingDisrupt',
 const.effectRemoteWebifierFalloff: 'webify',
 const.effectShipModuleGuidanceDisruptor: 'ewGuidanceDisrupt',
 const.effectRemoteECMFalloff: 'electronic',
 const.effectEntityECMFalloff: 'electronic',
 const.effectStructureEwEffectJam: 'electronic',
 const.effectStructureEwTargetPaint: 'ewTargetPaint',
 const.effectStructureEnergyNeutralizerFalloff: 'ewEnergyNeut',
 const.effectStructureWarpScrambleBlockMWDWithNPCEffect: 'warpScramblerMWD',
 const.effectStructureDecreaseTargetSpeed: 'webify',
 const.effectStructureTargetMaxTargetRangeAndScanResolutionBonusHostile: 'ewRemoteSensorDamp',
 const.effectStructureTargetGunneryMaxRangeAndTrackingSpeedAndFalloffBonusHostile: 'ewTrackingDisrupt',
 const.effectDoomsdayAOEECM: 'electronic',
 const.effectDoomsdayAOEPaint: 'ewTargetPaint',
 const.effectDoomsdayAOENeut: 'ewEnergyNeut',
 const.effectDoomsdayAOEWeb: 'webify',
 const.effectDoomsdayAOETrack: 'ewTrackingDisrupt',
 const.effectDoomsdayAOEDamp: 'ewRemoteSensorDamp',
 const.effectStructureModuleEffectStasisWebifier: 'webify',
 const.effectStructureModuleEffectTargetPainter: 'ewTargetPaint',
 const.effectStructureModuleEffectRemoteSensorDampener: 'ewRemoteSensorDamp',
 const.effectStructureModuleEffectECM: 'electronic',
 const.effectStructureModuleEffectWeaponDisruption: 'ewTrackingDisrupt',
 const.effectEntityEnergyNeutralizerFalloff: 'ewEnergyNeut',
 const.effectStarbaseEnergyNeutralizerFalloff: 'ewEnergyNeut',
 const.effectRemoteSensorDampEntity: 'ewRemoteSensorDamp',
 const.effectRemoteTargetPaintEntity: 'ewTargetPaint',
 const.effectNpcEntityWeaponDisruptor: 'ewTrackingDisrupt',
 const.effectRemoteWebifierEntity: 'webify',
 const.effectBehaviorECM: 'electronic',
 const.effectNpcBehaviorEnergyNeutralizer: 'ewEnergyNeut',
 const.effectNpcBehaviorEnergyNosferatu: 'ewEnergyVampire',
 const.effectNpcBehaviorGuidanceDisruptor: 'ewGuidanceDisrupt',
 const.effectBehaviorSensorDampener: 'ewRemoteSensorDamp',
 const.effectBehaviorTargetPainter: 'ewTargetPaint',
 const.effectNpcBehaviorTrackingDisruptor: 'ewTrackingDisrupt',
 const.effectBehaviorWarpDisrupt: 'warpScrambler',
 const.effectBehaviorWarpScramble: 'warpScramblerMWD',
 const.effectNpcBehaviorWebifier: 'webify'}
SKILL_ACCELERATOR_EFFECT_IDS = {const.effectAnalyticalMindIntelligenceBonusModAddIntelligenceLocationChar,
 const.effectEmpathyCharismaBonusModAddCharismaLocationChar,
 const.effectInstantRecallMemoryBonusModAddMemoryLocationChar,
 const.effectIronWillWillpowerBonusModAddWillpowerLocationChar,
 const.effectSpatialAwarenessPerceptionBonusModAddPerceptionLocationChar}

def IsBoosterSkillAccelerator(dogmaStaticMgr, boosterRecord):
    boosterEffectIds = dogmaStaticMgr.GetPassiveFilteredEffectsByType(boosterRecord.boosterTypeID)
    for effect_id in SKILL_ACCELERATOR_EFFECT_IDS:
        if effect_id in boosterEffectIds:
            return True

    return False
