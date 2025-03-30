#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\dogma\pythonEffects\weaponDisruptionUtil.py
import inventorycommon.const as invconst
import dogma.const as dogmaconst

def GetWeaponDisruptionAttributes():
    return {invconst.categoryShip: [(invconst.typeGunnery, dogmaconst.attributeMaxRangeBonus, dogmaconst.attributeMaxRange),
                             (invconst.typeGunnery, dogmaconst.attributeFalloffBonus, dogmaconst.attributeFalloff),
                             (invconst.typeGunnery, dogmaconst.attributeTrackingSpeedBonus, dogmaconst.attributeTrackingSpeed),
                             (invconst.typeMissileLauncherOperation, dogmaconst.attributeMissileVelocityBonus, dogmaconst.attributeMaxVelocity),
                             (invconst.typeMissileLauncherOperation, dogmaconst.attributeExplosionDelayBonus, dogmaconst.attributeExplosionDelay),
                             (invconst.typeMissileLauncherOperation, dogmaconst.attributeAoeVelocityBonus, dogmaconst.attributeAoeVelocity),
                             (invconst.typeMissileLauncherOperation, dogmaconst.attributeAoeCloudSizeBonus, dogmaconst.attributeAoeCloudSize)],
     invconst.categoryFighter: [(None, dogmaconst.attributeMaxRangeBonus, dogmaconst.attributeFighterAbilityAttackMissileRangeOptimal),
                                (None, dogmaconst.attributeFalloffBonus, dogmaconst.attributeFighterAbilityAttackMissileRangeFalloff),
                                (None, dogmaconst.attributeTrackingSpeedBonus, dogmaconst.attributeFighterAbilityAttackMissileExplosionVelocity),
                                (None, dogmaconst.attributeTrackingSpeedBonus, dogmaconst.attributeFighterAbilityAttackMissileExplosionRadius),
                                (None, dogmaconst.attributeMissileVelocityBonus, dogmaconst.attributeFighterAbilityMissilesRange),
                                (None, dogmaconst.attributeExplosionDelayBonus, dogmaconst.attributeFighterAbilityMissilesRange),
                                (None, dogmaconst.attributeAoeVelocityBonus, dogmaconst.attributeFighterAbilityMissilesExplosionVelocity),
                                (None, dogmaconst.attributeAoeCloudSizeBonus, dogmaconst.attributeFighterAbilityMissilesExplosionRadius)],
     invconst.categoryEntity: [(None, dogmaconst.attributeMaxRangeBonus, dogmaconst.attributeMaxRange),
                               (None, dogmaconst.attributeFalloffBonus, dogmaconst.attributeFalloff),
                               (None, dogmaconst.attributeTrackingSpeedBonus, dogmaconst.attributeTrackingSpeed),
                               (None, dogmaconst.attributeMissileVelocityBonus, dogmaconst.attributeMissileEntityVelocityMultiplier),
                               (None, dogmaconst.attributeExplosionDelayBonus, dogmaconst.attributeMissileEntityFlightTimeMultiplier),
                               (None, dogmaconst.attributeAoeVelocityBonus, dogmaconst.attributeMissileEntityAoeVelocityMultiplier),
                               (None, dogmaconst.attributeAoeCloudSizeBonus, dogmaconst.attributeMissileEntityAoeCloudSizeMultiplier)],
     invconst.categoryDrone: [(None, dogmaconst.attributeMaxRangeBonus, dogmaconst.attributeMaxRange),
                              (None, dogmaconst.attributeFalloffBonus, dogmaconst.attributeFalloff),
                              (None, dogmaconst.attributeTrackingSpeedBonus, dogmaconst.attributeTrackingSpeed),
                              (None, dogmaconst.attributeMissileVelocityBonus, dogmaconst.attributeMissileEntityVelocityMultiplier),
                              (None, dogmaconst.attributeExplosionDelayBonus, dogmaconst.attributeMissileEntityFlightTimeMultiplier),
                              (None, dogmaconst.attributeAoeVelocityBonus, dogmaconst.attributeMissileEntityAoeVelocityMultiplier),
                              (None, dogmaconst.attributeAoeCloudSizeBonus, dogmaconst.attributeMissileEntityAoeCloudSizeMultiplier)]}


def GetTrackingDisruptionAttributes():
    return {invconst.categoryShip: [(invconst.typeGunnery, dogmaconst.attributeMaxRangeBonus, dogmaconst.attributeMaxRange), (invconst.typeGunnery, dogmaconst.attributeFalloffBonus, dogmaconst.attributeFalloff), (invconst.typeGunnery, dogmaconst.attributeTrackingSpeedBonus, dogmaconst.attributeTrackingSpeed)],
     invconst.categoryFighter: [(None, dogmaconst.attributeMaxRangeBonus, dogmaconst.attributeFighterAbilityAttackMissileRangeOptimal),
                                (None, dogmaconst.attributeFalloffBonus, dogmaconst.attributeFighterAbilityAttackMissileRangeFalloff),
                                (None, dogmaconst.attributeTrackingSpeedBonus, dogmaconst.attributeFighterAbilityAttackMissileExplosionVelocity),
                                (None, dogmaconst.attributeTrackingSpeedBonus, dogmaconst.attributeFighterAbilityAttackMissileExplosionRadius)],
     invconst.categoryEntity: [(None, dogmaconst.attributeMaxRangeBonus, dogmaconst.attributeMaxRange), (None, dogmaconst.attributeFalloffBonus, dogmaconst.attributeFalloff), (None, dogmaconst.attributeTrackingSpeedBonus, dogmaconst.attributeTrackingSpeed)],
     invconst.categoryDrone: [(None, dogmaconst.attributeMaxRangeBonus, dogmaconst.attributeMaxRange), (None, dogmaconst.attributeFalloffBonus, dogmaconst.attributeFalloff), (None, dogmaconst.attributeTrackingSpeedBonus, dogmaconst.attributeTrackingSpeed)]}


def GetGuidanceDisruptionAttributes():
    return {invconst.categoryShip: [(invconst.typeMissileLauncherOperation, dogmaconst.attributeMissileVelocityBonus, dogmaconst.attributeMaxVelocity),
                             (invconst.typeMissileLauncherOperation, dogmaconst.attributeExplosionDelayBonus, dogmaconst.attributeExplosionDelay),
                             (invconst.typeMissileLauncherOperation, dogmaconst.attributeAoeVelocityBonus, dogmaconst.attributeAoeVelocity),
                             (invconst.typeMissileLauncherOperation, dogmaconst.attributeAoeCloudSizeBonus, dogmaconst.attributeAoeCloudSize)],
     invconst.categoryFighter: [(None, dogmaconst.attributeMissileVelocityBonus, dogmaconst.attributeFighterAbilityMissilesRange),
                                (None, dogmaconst.attributeExplosionDelayBonus, dogmaconst.attributeFighterAbilityMissilesRange),
                                (None, dogmaconst.attributeAoeVelocityBonus, dogmaconst.attributeFighterAbilityMissilesExplosionVelocity),
                                (None, dogmaconst.attributeAoeCloudSizeBonus, dogmaconst.attributeFighterAbilityMissilesExplosionRadius)],
     invconst.categoryEntity: [(None, dogmaconst.attributeMissileVelocityBonus, dogmaconst.attributeMissileEntityVelocityMultiplier),
                               (None, dogmaconst.attributeExplosionDelayBonus, dogmaconst.attributeMissileEntityFlightTimeMultiplier),
                               (None, dogmaconst.attributeAoeVelocityBonus, dogmaconst.attributeMissileEntityAoeVelocityMultiplier),
                               (None, dogmaconst.attributeAoeCloudSizeBonus, dogmaconst.attributeMissileEntityAoeCloudSizeMultiplier)],
     invconst.categoryDrone: [(None, dogmaconst.attributeMissileVelocityBonus, dogmaconst.attributeMissileEntityVelocityMultiplier),
                              (None, dogmaconst.attributeExplosionDelayBonus, dogmaconst.attributeMissileEntityFlightTimeMultiplier),
                              (None, dogmaconst.attributeAoeVelocityBonus, dogmaconst.attributeMissileEntityAoeVelocityMultiplier),
                              (None, dogmaconst.attributeAoeCloudSizeBonus, dogmaconst.attributeMissileEntityAoeCloudSizeMultiplier)]}
