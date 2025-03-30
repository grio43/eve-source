#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fighters\abilityAttributes.py
import dogma.const
from eve.common.script.mgt import fighterConst
dogmaEffectByAbilityID = {fighterConst.ABILITY_ATTACKTURRET: dogma.const.effectFighterAbilityAttackTurret,
 fighterConst.ABILITY_WEBS: dogma.const.effectFighterAbilityStasisWebifier,
 fighterConst.ABILITY_TARGET_PAINT: dogma.const.effectFighterTargetPaint,
 fighterConst.ABILITY_WARP_DISRUPT: dogma.const.effectFighterAbilityWarpDisruption,
 fighterConst.ABILITY_ENERGY_NEUT: dogma.const.effectFighterAbilityEnergyNeutralizer,
 fighterConst.ABILITY_ECM: dogma.const.effectFighterAbilityECM,
 fighterConst.ABILITY_MISSILE: dogma.const.effectFighterAbilityMissiles,
 fighterConst.ABILITY_TACKLE: dogma.const.effectFighterAbilityTackle,
 fighterConst.ABILITY_ATTACKMISSILE: dogma.const.effectFighterAbilityAttackMissile,
 fighterConst.ABILITY_TORPEDOSALVOEM: dogma.const.effectFighterAbilityMissiles,
 fighterConst.ABILITY_TORPEDOSALVOTHERM: dogma.const.effectFighterAbilityMissiles,
 fighterConst.ABILITY_TORPEDOSALVOKIN: dogma.const.effectFighterAbilityMissiles,
 fighterConst.ABILITY_TORPEDOSALVOEXP: dogma.const.effectFighterAbilityMissiles,
 fighterConst.ABILITY_PULSECANNON: dogma.const.effectFighterAbilityAttackMissile,
 fighterConst.ABILITY_BEAMCANNON: dogma.const.effectFighterAbilityAttackMissile,
 fighterConst.ABILITY_BLASTERCANNON: dogma.const.effectFighterAbilityAttackMissile,
 fighterConst.ABILITY_RAILGUN: dogma.const.effectFighterAbilityAttackMissile,
 fighterConst.ABILITY_AUTOCANNON: dogma.const.effectFighterAbilityAttackMissile,
 fighterConst.ABILITY_ARTILLERY: dogma.const.effectFighterAbilityAttackMissile,
 fighterConst.ABILITY_MICROMISSILESWARMEM: dogma.const.effectFighterAbilityMissiles,
 fighterConst.ABILITY_MICROMISSILESWARMTHERM: dogma.const.effectFighterAbilityMissiles,
 fighterConst.ABILITY_MICROMISSILESWARMKIN: dogma.const.effectFighterAbilityMissiles,
 fighterConst.ABILITY_MICROMISSILESWARMEXP: dogma.const.effectFighterAbilityMissiles,
 fighterConst.ABILITY_HEAVYROCKETSALVOEM: dogma.const.effectFighterAbilityMissiles,
 fighterConst.ABILITY_HEAVYROCKETSALVOTHERM: dogma.const.effectFighterAbilityMissiles,
 fighterConst.ABILITY_HEAVYROCKETSALVOKIN: dogma.const.effectFighterAbilityMissiles,
 fighterConst.ABILITY_HEAVYROCKETSALVOEXP: dogma.const.effectFighterAbilityMissiles,
 fighterConst.ABILITY_AFTERBURNER: dogma.const.effectFighterAbilityAfterburner,
 fighterConst.ABILITY_MICROWARPDRIVE: dogma.const.effectFighterAbilityMicroWarpDrive,
 fighterConst.ABILITY_MICRO_JUMP_DRIVE: dogma.const.effectFighterAbilityMicroJumpDrive,
 fighterConst.ABILITY_DAMAGE_BOOST: dogma.const.effectFighterDamageMultiply,
 fighterConst.ABILITY_EVASION: dogma.const.effectFighterAbilityEvasiveManeuvers,
 fighterConst.ABILITY_LAUNCH_BOMB: dogma.const.effectFighterAbilityLaunchBomb,
 fighterConst.ABILITY_KAMIKAZE: dogma.const.effectFighterAbilityKamikaze,
 fighterConst.ABILITY_BLASTERCANNON_CALDARI: dogma.const.effectFighterAbilityAttackMissile,
 fighterConst.ABILITY_RAILGUN_CALDARI: dogma.const.effectFighterAbilityAttackMissile}
turretDamageTypes = {dogma.const.attributeEmDamage: dogma.const.attributeFighterAbilityAttackTurretDamageEM,
 dogma.const.attributeThermalDamage: dogma.const.attributeFighterAbilityAttackTurretDamageTherm,
 dogma.const.attributeKineticDamage: dogma.const.attributeFighterAbilityAttackTurretDamageKin,
 dogma.const.attributeExplosiveDamage: dogma.const.attributeFighterAbilityAttackTurretDamageExp}
attackMissileDamageTypes = {dogma.const.attributeEmDamage: dogma.const.attributeFighterAbilityAttackMissileDamageEM,
 dogma.const.attributeThermalDamage: dogma.const.attributeFighterAbilityAttackMissileDamageTherm,
 dogma.const.attributeKineticDamage: dogma.const.attributeFighterAbilityAttackMissileDamageKin,
 dogma.const.attributeExplosiveDamage: dogma.const.attributeFighterAbilityAttackMissileDamageExp}
missileDamageTypes = {dogma.const.attributeEmDamage: dogma.const.attributeFighterAbilityMissilesEMDamage,
 dogma.const.attributeThermalDamage: dogma.const.attributeFighterAbilityMissilesThermDamage,
 dogma.const.attributeKineticDamage: dogma.const.attributeFighterAbilityMissilesKinDamage,
 dogma.const.attributeExplosiveDamage: dogma.const.attributeFighterAbilityMissilesExpDamage}
FIGHTER_DAMAGE_ATTRIBUTES = turretDamageTypes.values() + attackMissileDamageTypes.values() + missileDamageTypes.values()
infoAttributesByDogmaEffect = {dogma.const.effectFighterAbilityAttackTurret: [dogma.const.attributeFighterAbilityAttackTurretSignatureResolution] + turretDamageTypes.values(),
 dogma.const.effectFighterAbilityAttackMissile: [dogma.const.attributeFighterAbilityAttackMissileExplosionRadius,
                                                 dogma.const.attributeFighterAbilityAttackMissileExplosionVelocity,
                                                 dogma.const.attributeFighterAbilityAttackMissileReductionFactor,
                                                 dogma.const.attributeFighterAbilityAttackMissileReductionSensitivity] + attackMissileDamageTypes.values(),
 dogma.const.effectFighterAbilityEvasiveManeuvers: [dogma.const.attributeFighterAbilityEvasiveManeuversSignatureRadiusBonus,
                                                    dogma.const.attributeFighterAbilityEvasiveManeuversSpeedBonus,
                                                    dogma.const.attributeFighterAbilityEvasiveManeuversEmResonance,
                                                    dogma.const.attributeFighterAbilityEvasiveManeuversThermResonance,
                                                    dogma.const.attributeFighterAbilityEvasiveManeuversKinResonance,
                                                    dogma.const.attributeFighterAbilityEvasiveManeuversExpResonance],
 dogma.const.effectFighterAbilityAfterburner: [dogma.const.attributeFighterAbilityAfterburnerSpeedBonus],
 dogma.const.effectFighterAbilityMicroWarpDrive: [dogma.const.attributeFighterAbilityMicroWarpDriveSpeedBonus, dogma.const.attributeFighterAbilityMicroWarpDriveSignatureRadiusBonus],
 dogma.const.effectFighterAbilityMissiles: [dogma.const.attributeFighterAbilityMissilesExplosionRadius,
                                            dogma.const.attributeFighterAbilityMissilesExplosionVelocity,
                                            dogma.const.attributeFighterAbilityMissilesDamageReductionFactor,
                                            dogma.const.attributeFighterAbilityMissilesDamageReductionSensitivity] + missileDamageTypes.values(),
 dogma.const.effectFighterAbilityEnergyNeutralizer: [dogma.const.attributeFighterAbilityEnergyNeutralizerAmount],
 dogma.const.effectFighterAbilityStasisWebifier: [dogma.const.attributeFighterAbilityStasisWebifierSpeedPenalty],
 dogma.const.effectFighterAbilityWarpDisruption: [dogma.const.attributeFighterAbilityWarpDisruptionPointStrength],
 dogma.const.effectFighterAbilityECM: [dogma.const.attributeFighterAbilityECMStrengthGravimetric,
                                       dogma.const.attributeFighterAbilityECMStrengthLadar,
                                       dogma.const.attributeFighterAbilityECMStrengthMagnetometric,
                                       dogma.const.attributeFighterAbilityECMStrengthRadar],
 dogma.const.effectFighterAbilityTackle: [dogma.const.attributeFighterAbilityTackleWebSpeedPenalty],
 dogma.const.effectFighterMicroJumpDrive: [],
 dogma.const.effectFighterTargetPaint: [],
 dogma.const.effectFighterDamageMultiply: []}
DAMAGE_TYPES_BY_FIGHTER_DAMAGE_ATTRIBUTE = {}
for damageTypesDict in [turretDamageTypes, attackMissileDamageTypes, missileDamageTypes]:
    for damageType, fighterDamageAttribute in damageTypesDict.items():
        DAMAGE_TYPES_BY_FIGHTER_DAMAGE_ATTRIBUTE[fighterDamageAttribute] = damageType

def _GetAbilitiesFromDogmaEffectID(dogmaEffectID):
    return [ x for x, effectID in dogmaEffectByAbilityID.iteritems() if effectID == dogmaEffectID ]


damageMultipliersByDogmaEffectID = {dogma.const.effectFighterAbilityAttackTurret: dogma.const.attributeFighterAbilityAttackTurretDamageMultiplier,
 dogma.const.effectFighterAbilityAttackMissile: dogma.const.attributeFighterAbilityAttackMissileDamageMultiplier,
 dogma.const.effectFighterAbilityMissiles: dogma.const.attributeFighterAbilityMissilesDamageMultiplier}
damageMultiplierByAbilityID = {}
for eachDogmaEffectID, eachMultiplierAttrID in damageMultipliersByDogmaEffectID.iteritems():
    damageMultiplierByAbilityID.update({attrID:eachMultiplierAttrID for attrID in _GetAbilitiesFromDogmaEffectID(eachDogmaEffectID)})

def GetDamageMultiplierAttributeFromAbilityID(abilityID):
    return damageMultiplierByAbilityID.get(abilityID, None)


def GetDogmaEffectIDForAbilityID(abilityID):
    return dogmaEffectByAbilityID.get(abilityID)


def GetDogmaAttributeIDsForAbilityID(abilityID):
    effectID = GetDogmaEffectIDForAbilityID(abilityID)
    if effectID is not None:
        return infoAttributesByDogmaEffect.get(effectID)


def GetAbilityRangeAndFalloffAttributeIDs(dogmaStaticMgr, abilityID):
    rangeAttributeID = None
    falloffAttributeID = None
    effectID = GetDogmaEffectIDForAbilityID(abilityID)
    if effectID is not None:
        effect = dogmaStaticMgr.effects[effectID]
        rangeAttributeID = effect.rangeAttributeID
        falloffAttributeID = effect.falloffAttributeID
    return (rangeAttributeID, falloffAttributeID)


def GetAbilityDurationAttributeID(dogmaStaticMgr, abilityID):
    effectID = GetDogmaEffectIDForAbilityID(abilityID)
    if effectID is not None:
        effect = dogmaStaticMgr.effects[effectID]
        return effect.durationAttributeID
