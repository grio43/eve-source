#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\const\behaviorroles.py
from dogma.const import effectBehaviorWarpDisrupt, effectNpcBehaviorWebifier, effectBehaviorWarpScramble, effectBehaviorTargetPainter, effectNpcBehaviorSmartBomb, effectNpcBehaviorMicroJumpAttack, effectEntityChainLightning
from dogma.const import effectNpcBehaviorGuidanceDisruptor, effectNpcBehaviorTrackingDisruptor, effectNpcBehaviorEnergyNeutralizer
from dogma.const import effectBehaviorSensorDampener, effectBehaviorECM, effectNpcBehaviorEnergyNosferatu
from dogma.const import effectNpcBehaviorRemoteArmorRepairer, effectNpcBehaviorRemoteCapacitorTransmitter, effectNpcBehaviorRemoteShieldBooster
ROLE_ANTI_DPS = 'anti-dps'
ROLE_ANTI_DPS_WITH_PRIMARY = 'anti-dps (with primary)'
ROLE_ANTI_LOGISTIC = 'anti-logistic'
ROLE_COMMANDER = 'commander'
ROLE_DPS = 'dps'
ROLE_EW = 'ew'
ROLE_LOGISTIC = 'logistic'
ROLE_TACKLER = 'tackler'
ROLE_DREADNOUGHT = 'dreadnought'
COMBAT_ROLES = [ROLE_ANTI_DPS,
 ROLE_ANTI_LOGISTIC,
 ROLE_COMMANDER,
 ROLE_DPS,
 ROLE_EW,
 ROLE_LOGISTIC,
 ROLE_TACKLER,
 ROLE_DREADNOUGHT,
 ROLE_ANTI_DPS_WITH_PRIMARY]
COMBAT_EFFECTS_BY_ROLES = {ROLE_LOGISTIC: (effectNpcBehaviorRemoteArmorRepairer, effectNpcBehaviorRemoteCapacitorTransmitter, effectNpcBehaviorRemoteShieldBooster),
 ROLE_TACKLER: (effectBehaviorWarpDisrupt,
                effectNpcBehaviorWebifier,
                effectBehaviorWarpScramble,
                effectBehaviorTargetPainter),
 ROLE_ANTI_DPS: (effectNpcBehaviorGuidanceDisruptor,
                 effectNpcBehaviorTrackingDisruptor,
                 effectBehaviorTargetPainter,
                 effectNpcBehaviorEnergyNeutralizer,
                 effectNpcBehaviorEnergyNosferatu,
                 effectBehaviorSensorDampener,
                 effectBehaviorECM),
 ROLE_ANTI_DPS_WITH_PRIMARY: (effectNpcBehaviorGuidanceDisruptor,
                              effectNpcBehaviorTrackingDisruptor,
                              effectBehaviorTargetPainter,
                              effectNpcBehaviorEnergyNeutralizer,
                              effectNpcBehaviorEnergyNosferatu,
                              effectBehaviorSensorDampener,
                              effectBehaviorECM),
 ROLE_ANTI_LOGISTIC: (effectNpcBehaviorEnergyNeutralizer,
                      effectBehaviorSensorDampener,
                      effectBehaviorECM,
                      effectBehaviorTargetPainter),
 ROLE_DREADNOUGHT: (),
 ROLE_DPS: (effectNpcBehaviorMicroJumpAttack, effectNpcBehaviorSmartBomb, effectEntityChainLightning)}
COMBAT_DISTRIBUTE_EFFECTS_BY_ROLE = (ROLE_TACKLER, ROLE_ANTI_DPS)
COMBAT_IGNORE_PRIMARY_BY_ROLE = (ROLE_ANTI_DPS,)
