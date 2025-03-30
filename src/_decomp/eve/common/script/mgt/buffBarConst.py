#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\mgt\buffBarConst.py
import signals
from eve.common.lib import appConst
import dbuff.const
ADD_GENERIC_BUFFBAR_BUTTON_SIGNAL = signals.Signal(signalName='addGenericBuffBarButton')
REMOVE_GENERIC_BUFFBAR_BUTTON_SIGNAL = signals.Signal(signalName='removeGenericBuffBarButton')
Slot_WarpScramblerMWD = 'warpScramblerMWD'
Slot_WarpScrambler = 'warpScrambler'
Slot_FighterTackle = 'fighterTackle'
Slot_FocusedWarpScrambler = 'focusedWarpScrambler'
Slot_Webify = 'webify'
Slot_Electronic = 'electronic'
Slot_EwRemoteSensorDamp = 'ewRemoteSensorDamp'
Slot_EwTrackingDisrupt = 'ewTrackingDisrupt'
Slot_EwGuidanceDisrupt = 'ewGuidanceDisrupt'
Slot_EwTargetPaint = 'ewTargetPaint'
Slot_EwEnergyVampire = 'ewEnergyVampire'
Slot_EwEnergyNeut = 'ewEnergyNeut'
Slot_RemoteTracking = 'remoteTracking'
Slot_EnergyTransfer = 'energyTransfer'
Slot_SensorBooster = 'sensorBooster'
Slot_EccmProjector = 'eccmProjector'
Slot_RemoteHullRepair = 'remoteHullRepair'
Slot_RemoteArmorRepair = 'remoteArmorRepair'
Slot_RemoteArmorMutadaptiveRepairer = 'RemoteArmorMutadaptiveRepairer'
Slot_ShieldTransfer = 'shieldTransfer'
Slot_Tethering = 'tethering'
Slot_TetheringRepair = 'tetheringRepair'
Slot_ShieldBurst = 'shieldBurst'
Slot_ArmorBurst = 'armorBurst'
Slot_InformationBurst = 'informationBurst'
Slot_SkirmishBurst = 'skirmishBurst'
Slot_MiningBurst = 'miningBurst'
Slot_InvulnerabilityBurst = 'invulnerabilityBurst'
Slot_TitanBurst = 'titanBurst'
Slot_NotTethered = 'notTethered'
Slot_AoeBioluminescenceCloud = 'aoeBioluminescenceCloud'
Slot_AoeCausticCloud = 'aoeCausticCloud'
Slot_AoePulsePlatform = 'aoePulsePlatform'
Slot_AoePointDefense = 'aoePointDefense'
Slot_AoeFilamentCloud = 'aoeFilamentCloud'
Slot_Weather_CausticToxin = 'weatherCausticToxin'
Slot_Weather_Darkness = 'weatherDarkness'
Slot_Weather_Infernal = 'weatherInfernal'
Slot_Weather_XenonGas = 'weatherXenonGas'
Slot_Weather_ElectricStorm = 'weatherElectricStorm'
Slot_AoeDamageBoost = 'aoeDamageBoost'
Slot_CloakDisrupt = 'CloakDisrupt'
Slot_CloakDefense = 'CloakDefense'
Slot_LinkedToESSMainBank = 'LinkedToESSMainBank'
Slot_LinkedToESSReserveBank = 'LinkedToESSReserveBank'
Slot_LinkWithShipBonuses = 'LinkWithShipBonuses'
Slot_StrangeEffect = 'strangeEffect'
Slot_TetheringRestrictedBySecurity = 'tetheringRestricted'
Slot_RemoteRepairImpedance = 'remoteRepairImpedance'
Slot_DeathZoneProtected = 'deathZoneProtected'
Slot_DeathZoneGracePeriod = 'deathZoneGracePeriod'
Slot_DeathZoneDamage = 'deathZoneDamage'
Slot_SuppressionBonus = 'suppressionBonus'
Slot_LinkedToTowGameObjective = 'LinkedToTowGameObjective'
Slot_CDCloudEffect = 'cdCloudEffect'
Slot_AntiTachyonCloud = 'antiTachyonCloud'
Slot_TractorRepeatingBlocked = 'tractorRepeatingBlocked'
Slot_DotWeaponTarget = 'dotWeaponTarget'
Slot_DotWeaponAttacker = 'dotWeaponAttacker'
Slot_LinkedToTraceGate = 'linkedToTraceGate'
BUFF_SLOT_ICONS = {Slot_WarpScramblerMWD: appConst.iconModuleWarpScramblerMWD,
 Slot_WarpScrambler: appConst.iconModuleWarpScrambler,
 Slot_FighterTackle: appConst.iconModuleFighterTackle,
 Slot_FocusedWarpScrambler: appConst.iconModuleFocusedWarpScrambler,
 Slot_Webify: appConst.iconModuleStasisWeb,
 Slot_Electronic: appConst.iconModuleECM,
 Slot_EwRemoteSensorDamp: appConst.iconModuleSensorDamper,
 Slot_EwTrackingDisrupt: appConst.iconModuleTrackingDisruptor,
 Slot_EwGuidanceDisrupt: appConst.iconModuleGuidanceDisruptor,
 Slot_EwTargetPaint: appConst.iconModuleTargetPainter,
 Slot_EwEnergyVampire: appConst.iconModuleNosferatu,
 Slot_EwEnergyNeut: appConst.iconModuleEnergyNeutralizer,
 Slot_RemoteTracking: appConst.iconModuleRemoteTracking,
 Slot_EnergyTransfer: appConst.iconModuleEnergyTransfer,
 Slot_SensorBooster: appConst.iconModuleSensorBooster,
 Slot_EccmProjector: appConst.iconModuleECCMProjector,
 Slot_RemoteHullRepair: appConst.iconModuleHullRepairer,
 Slot_RemoteArmorRepair: appConst.iconModuleArmorRepairer,
 Slot_RemoteArmorMutadaptiveRepairer: appConst.iconModuleMutadaptiveArmorRepairer,
 Slot_ShieldTransfer: appConst.iconModuleShieldBooster,
 Slot_Tethering: appConst.iconModuleTethering,
 Slot_TetheringRepair: appConst.iconModuleHullRepairer,
 Slot_ShieldBurst: appConst.iconShieldBurst,
 Slot_ArmorBurst: appConst.iconArmorBurst,
 Slot_InformationBurst: appConst.iconInformationBurst,
 Slot_SkirmishBurst: appConst.iconSkirmishBurst,
 Slot_MiningBurst: appConst.iconMiningBurst,
 Slot_InvulnerabilityBurst: appConst.iconIndustrialInvulnerability,
 Slot_TitanBurst: appConst.iconTitanGeneratorMulti,
 Slot_NotTethered: appConst.iconNotTethered,
 Slot_AoeBioluminescenceCloud: appConst.iconAoeBioluminescence,
 Slot_AoeCausticCloud: appConst.iconAoeCausticCloud,
 Slot_AoePulsePlatform: appConst.iconAoePulseBattery,
 Slot_AoePointDefense: appConst.iconAoePointDefense,
 Slot_AoeFilamentCloud: appConst.iconAoeFilamentCloud,
 Slot_Weather_CausticToxin: appConst.iconWeatherCaustic,
 Slot_Weather_Darkness: appConst.iconWeatherDarkness,
 Slot_Weather_Infernal: appConst.iconWeatherInfernal,
 Slot_Weather_XenonGas: appConst.iconWeatherXenonGas,
 Slot_Weather_ElectricStorm: appConst.iconWeatherLightning,
 Slot_AoeDamageBoost: appConst.iconAoeDamageBoost,
 Slot_CloakDisrupt: appConst.iconCloakingDevice,
 Slot_CloakDefense: appConst.iconCloakingDevice,
 Slot_LinkedToESSReserveBank: appConst.iconLinkedToESSReserveBank,
 Slot_LinkedToESSMainBank: appConst.iconLinkedToESSMainBank,
 Slot_LinkWithShipBonuses: appConst.iconLinkedToAnalysisBeacon,
 Slot_StrangeEffect: appConst.iconTitanGeneratorMulti,
 Slot_TetheringRestrictedBySecurity: appConst.iconNotTethered,
 Slot_RemoteRepairImpedance: appConst.iconDoomsday,
 Slot_DeathZoneProtected: appConst.iconDeathZoneProtected,
 Slot_DeathZoneGracePeriod: appConst.iconDeathZoneGracePriod,
 Slot_DeathZoneDamage: appConst.iconDeathZoneDamage,
 Slot_SuppressionBonus: appConst.iconBountyHunting,
 Slot_LinkedToTowGameObjective: appConst.iconLinkedToTowGameObjective,
 Slot_CDCloudEffect: appConst.iconTitanGeneratorMulti,
 Slot_AntiTachyonCloud: appConst.iconAoeCausticCloud,
 Slot_TractorRepeatingBlocked: appConst.iconTractorBeam,
 Slot_DotWeaponTarget: appConst.iconBreacherPod,
 Slot_DotWeaponAttacker: appConst.iconBreacherPod,
 Slot_LinkedToTraceGate: appConst.iconLinkedToTraceGate}
BUFF_SLOT_HINTS = {Slot_WarpScramblerMWD: 'UI/Inflight/EwarHints/WarpScrambledMWD',
 Slot_WarpScrambler: 'UI/Inflight/EwarHints/WarpScrambled',
 Slot_FighterTackle: 'UI/Inflight/EwarHints/FighterTackled',
 Slot_FocusedWarpScrambler: 'UI/Inflight/EwarHints/FocusedWarpScrambled',
 Slot_Webify: 'UI/Inflight/EwarHints/Webified',
 Slot_Electronic: 'UI/Inflight/EwarHints/Jammed',
 Slot_EwRemoteSensorDamp: 'UI/Inflight/EwarHints/SensorDampened',
 Slot_EwTrackingDisrupt: 'UI/Inflight/EwarHints/TrackingDisrupted',
 Slot_EwGuidanceDisrupt: 'UI/Inflight/EwarHints/GuidanceDisrupted',
 Slot_EwTargetPaint: 'UI/Inflight/EwarHints/TargetPainted',
 Slot_EwEnergyVampire: 'UI/Inflight/EwarHints/CapDrained',
 Slot_EwEnergyNeut: 'UI/Inflight/EwarHints/CapNeutralized',
 Slot_RemoteTracking: 'UI/Inflight/EwarHints/RemoteTracking',
 Slot_EnergyTransfer: 'UI/Inflight/EwarHints/EnergyTransfer',
 Slot_SensorBooster: 'UI/Inflight/EwarHints/SensorBooster',
 Slot_EccmProjector: 'UI/Inflight/EwarHints/ECCMProjector',
 Slot_RemoteHullRepair: 'UI/Inflight/EwarHints/RemoteHullRepair',
 Slot_RemoteArmorRepair: 'UI/Inflight/EwarHints/RemoteArmorRepair',
 Slot_RemoteArmorMutadaptiveRepairer: 'UI/Inflight/EwarHints/RemoteMutadaptiveArmorRepair',
 Slot_ShieldTransfer: 'UI/Inflight/EwarHints/ShieldTransfer',
 Slot_Tethering: 'UI/Inflight/EwarHints/Tethered',
 Slot_TetheringRepair: 'UI/Inflight/EwarHints/TetheredRepair',
 Slot_ShieldBurst: 'UI/Inflight/EwarHints/ShieldBurst',
 Slot_ArmorBurst: 'UI/Inflight/EwarHints/ArmorBurst',
 Slot_InformationBurst: 'UI/Inflight/EwarHints/InformationBurst',
 Slot_SkirmishBurst: 'UI/Inflight/EwarHints/SkirmishBurst',
 Slot_MiningBurst: 'UI/Inflight/EwarHints/MiningBurst',
 Slot_InvulnerabilityBurst: 'UI/Inflight/EwarHints/InvulnerabilityBurst',
 Slot_TitanBurst: 'UI/Inflight/EwarHints/TitanBurst',
 Slot_NotTethered: 'UI/Inflight/EwarHints/NotTethered',
 Slot_AoeBioluminescenceCloud: 'UI/Inflight/EwarHints/BioluminescenceCloud',
 Slot_AoeCausticCloud: 'UI/Inflight/EwarHints/CausticCloud',
 Slot_AoePulsePlatform: 'UI/Inflight/EwarHints/PulsePlatform',
 Slot_AoePointDefense: 'UI/Inflight/EwarHints/PointDefense',
 Slot_AoeFilamentCloud: 'UI/Inflight/EwarHints/FilamentCloud',
 Slot_Weather_CausticToxin: 'UI/Inflight/EwarHints/CausticToxin',
 Slot_Weather_Darkness: 'UI/Inflight/EwarHints/Darkness',
 Slot_Weather_Infernal: 'UI/Inflight/EwarHints/Infernal',
 Slot_Weather_XenonGas: 'UI/Inflight/EwarHints/XenonGas',
 Slot_Weather_ElectricStorm: 'UI/Inflight/EwarHints/ElectricStorm',
 Slot_AoeDamageBoost: 'UI/Inflight/EwarHints/DamageBoost',
 Slot_CloakDisrupt: 'UI/Inflight/EwarHints/CloakDisrupt',
 Slot_CloakDefense: 'UI/Inflight/EwarHints/CloakDefense',
 Slot_LinkedToESSMainBank: 'UI/Inflight/EwarHints/LinkedToESSMainBank',
 Slot_LinkedToESSReserveBank: 'UI/Inflight/EwarHints/LinkedToESSReserveBank',
 Slot_LinkWithShipBonuses: 'UI/Inflight/EwarHints/LinkWithShipBonuses',
 Slot_StrangeEffect: 'UI/Inflight/EwarHints/StrangeEffect',
 Slot_TetheringRestrictedBySecurity: 'UI/Messages/1710/TetherDisabledTooltip',
 Slot_RemoteRepairImpedance: 'UI/Inflight/EwarHints/RemoteRepairImpeded',
 Slot_DeathZoneProtected: 'UI/Inflight/SpaceComponents/DeathZoneDamageGenerator/SafeZone',
 Slot_DeathZoneGracePeriod: 'UI/Inflight/SpaceComponents/DeathZoneDamageGenerator/DeathZoneGracePeriod',
 Slot_DeathZoneDamage: 'UI/Inflight/SpaceComponents/DeathZoneDamageGenerator/DeathZoneDamage',
 Slot_SuppressionBonus: 'UI/Inflight/EwarHints/SuppressionEffect',
 Slot_LinkedToTowGameObjective: 'UI/Inflight/SpaceComponents/TowGameObjective/LinkedBuffBarHint',
 Slot_CDCloudEffect: 'UI/Inflight/EwarHints/CDCloudEffect',
 Slot_AntiTachyonCloud: 'UI/Inflight/EwarHints/AntiTachyonCloud',
 Slot_TractorRepeatingBlocked: 'UI/Inflight/EwarHints/TractorRepeatingBlocked',
 Slot_DotWeaponTarget: 'UI/Inflight/EwarHints/DotWeaponApplied',
 Slot_DotWeaponAttacker: 'UI/Inflight/EwarHints/DotWeaponApplied',
 Slot_LinkedToTraceGate: 'UI/Inflight/EwarHints/LinkedToJumpTrace'}
OFFENSIVE_SLOTS = {Slot_WarpScramblerMWD,
 Slot_WarpScrambler,
 Slot_FighterTackle,
 Slot_FocusedWarpScrambler,
 Slot_Webify,
 Slot_Electronic,
 Slot_EwRemoteSensorDamp,
 Slot_EwTrackingDisrupt,
 Slot_EwGuidanceDisrupt,
 Slot_EwTargetPaint,
 Slot_EwEnergyVampire,
 Slot_EwEnergyNeut,
 Slot_RemoteRepairImpedance,
 Slot_DotWeaponTarget}
FX_GUIDS_BY_SLOT = {Slot_Tethering: 'effects.Tethering',
 Slot_TetheringRepair: 'effects.TetheringRepair',
 Slot_LinkedToESSReserveBank: 'effects.ReserveBankHackingBeam',
 Slot_LinkedToESSMainBank: 'effects.MainBankHackingBeam',
 Slot_LinkedToTowGameObjective: 'effects.DataLink',
 Slot_LinkedToTraceGate: 'effects.LinkedToTraceGate'}
FX_GUIDS_THAT_UPDATE_BUFF_BAR = FX_GUIDS_BY_SLOT.values()
DBUFFS_BY_SLOT = {Slot_FocusedWarpScrambler: [dbuff.const.dbuffWarpPenalty],
 Slot_ShieldBurst: [dbuff.const.dbuffShieldBurst_ShieldHarmonizing, dbuff.const.dbuffShieldBurst_ActiveShielding, dbuff.const.dbuffShieldBurst_ShieldExtension],
 Slot_ArmorBurst: [dbuff.const.dbuffArmorBurst_ArmorEnergizing, dbuff.const.dbuffArmorBurst_RapidRepair, dbuff.const.dbuffArmorBurst_ArmorReinforcement],
 Slot_InformationBurst: [dbuff.const.dbuffInformationBurst_SensorOptimization_ScanResolution,
                         dbuff.const.dbuffInformationBurst_SensorOptimization_TargetingRange,
                         dbuff.const.dbuffInformationBurst_ElectronicSuperiority,
                         dbuff.const.dbuffInformationBurst_ElectronicHardening_Resistance,
                         dbuff.const.dbuffInformationBurst_ElectronicHardening_ScanStrength],
 Slot_SkirmishBurst: [dbuff.const.dbuffSkirmishBurst_EvasiveManeuvers_Signature,
                      dbuff.const.dbuffSkirmishBurst_EvasiveManeuvers_Agility,
                      dbuff.const.dbuffSkirmishBurst_InterdictionManeuvers,
                      dbuff.const.dbuffSkirmishBurst_RapidDeployment],
 Slot_MiningBurst: [dbuff.const.dbuffMiningBurst_MiningLaserFieldEnhancement, dbuff.const.dbuffMiningBurst_MiningLaserOptimization, dbuff.const.dbuffMiningBurst_MiningEquipmentPreservation],
 Slot_InvulnerabilityBurst: [dbuff.const.dbuffInvulnerability_ShieldResistance,
                             dbuff.const.dbuffInvulnerability_ShieldRecharge,
                             dbuff.const.dbuffInvulnerability_DroneDamagePenalty,
                             dbuff.const.dbuffInvulnerability_DisallowWeapons,
                             dbuff.const.dbuffInvulnerability_DisallowEntosis,
                             dbuff.const.dbuffInvulnerability_MassIncrease,
                             dbuff.const.dbuffInvulnerability_ScanResolution],
 Slot_Webify: [dbuff.const.dbuffStasisWebificationBurst],
 Slot_EwTrackingDisrupt: [dbuff.const.dbuffWeaponDisruptionBurst_TurretMaxRange, dbuff.const.dbuffWeaponDisruptionBurst_TurretFalloffRange, dbuff.const.dbuffWeaponDisruptionBurst_TurretTracking],
 Slot_EwGuidanceDisrupt: [dbuff.const.dbuffWeaponDisruptionBurst_MissileVelocity,
                          dbuff.const.dbuffWeaponDisruptionBurst_MissileDuration,
                          dbuff.const.dbuffWeaponDisruptionBurst_ExplosionVelocity,
                          dbuff.const.dbuffWeaponDisruptionBurst_ExplosionRadius],
 Slot_EwRemoteSensorDamp: [dbuff.const.dbuffSensorDampeningBurst_ScanResolution, dbuff.const.dbuffSensorDampeningBurst_MaxTargetRange],
 Slot_EwTargetPaint: [dbuff.const.dbuffTargetIlluminationBurst],
 Slot_Electronic: [dbuff.const.dbuffECMBurst],
 Slot_TitanBurst: [dbuff.const.dbuffAvatarTitanBurst_Bonus1,
                   dbuff.const.dbuffAvatarTitanBurst_Bonus2,
                   dbuff.const.dbuffAvatarTitanBurst_Penalty1,
                   dbuff.const.dbuffAvatarTitanBurst_Penalty2,
                   dbuff.const.dbuffErebusTitanBurst_Bonus1,
                   dbuff.const.dbuffErebusTitanBurst_Bonus2,
                   dbuff.const.dbuffErebusTitanBurst_Penalty1,
                   dbuff.const.dbuffErebusTitanBurst_Penalty2,
                   dbuff.const.dbuffRagnarokTitanBurst_Bonus1,
                   dbuff.const.dbuffRagnarokTitanBurst_Bonus2,
                   dbuff.const.dbuffRagnarokTitanBurst_Penalty1,
                   dbuff.const.dbuffRagnarokTitanBurst_Penalty2,
                   dbuff.const.dbuffLeviathanTitanBurst_Bonus1,
                   dbuff.const.dbuffLeviathanTitanBurst_Bonus2,
                   dbuff.const.dbuffLeviathanTitanBurst_Penalty1,
                   dbuff.const.dbuffLeviathanTitanBurst_Penalty2,
                   dbuff.const.dbuffWeather_MaxTargetRange_Bonus,
                   dbuff.const.dbuffWeather_TargetLockSpeed_Bonus,
                   dbuff.const.dbuffWeather_StasisWebRange_Bonus,
                   dbuff.const.dbuffWeather_EmResistance_Bonus,
                   dbuff.const.dbuffWeather_ArmorResistance_Bonus,
                   dbuff.const.dbuffWeather_MaxVelocity_Bonus,
                   dbuff.const.dbuffWeather_SignatureRadius_Penalty,
                   dbuff.const.dbuffWeather_WeaponDisruption_Bonus],
 Slot_NotTethered: [dbuff.const.dbuffDisallowTether],
 Slot_AoeBioluminescenceCloud: [dbuff.const.dbuffAoe_BioluminescenceCloud_Signature_Penalty],
 Slot_AoeCausticCloud: [dbuff.const.dbuffAoe_CausticCloud_max_velocity_buff, dbuff.const.dbuffAoe_CausticCloud_inertia_buff, dbuff.const.dbuffAoe_proving_tachyon_signatureradius_penalty],
 Slot_AoePulsePlatform: [dbuff.const.dbuffAoe_PulsePlatform_TrackingSpeed_Bonus],
 Slot_AoePointDefense: [],
 Slot_AoeFilamentCloud: [dbuff.const.dbuffAoe_FilamentCloud_ShieldBoostShieldBoost_Penalty, dbuff.const.dbuffAoe_FilamentCloud_ShieldBoostDuration_Bonus],
 Slot_Weather_CausticToxin: [dbuff.const.dbuffWeather_CausticToxin_KineticResistance_Penalty, dbuff.const.dbuffWeather_CausticToxin_ScanResolution_Bonus],
 Slot_Weather_Darkness: [dbuff.const.dbuffWeather_Darkness_TurretRange_Penalty, dbuff.const.dbuffWeather_Darkness_Velocity_Bonus],
 Slot_Weather_Infernal: [dbuff.const.dbuffWeather_Infernal_ArmorHp_Bonus, dbuff.const.dbuffWeather_Infernal_ThermalResistance_Penalty],
 Slot_Weather_XenonGas: [dbuff.const.dbuffWeather_XenonGas_ExplosiveResistance_Penalty, dbuff.const.dbuffWeather_XenonGas_ShieldHp_Bonus],
 Slot_Weather_ElectricStorm: [dbuff.const.dbuffWeather_ElectricStorm_CapacitorRecharge_Bonus, dbuff.const.dbuffWeather_ElectricStorm_EmResistance_Penalty],
 Slot_AoeDamageBoost: [dbuff.const.dbuffAoe_DamageBoost],
 Slot_WarpScrambler: [dbuff.const.dbuffWreck_WarpScramble],
 Slot_CloakDisrupt: [dbuff.const.dbuffDisallowCloak],
 Slot_CloakDefense: [dbuff.const.dbuffStablizeCloak],
 Slot_LinkWithShipBonuses: [dbuff.const.dbuffLinkWithShip_Resists],
 Slot_StrangeEffect: [dbuff.const.dbuffSpacetimeNexusVelocity,
                      dbuff.const.dbuffSpacetimeNexusInertia,
                      dbuff.const.dbuffSpacetimeNexusRecharge,
                      dbuff.const.dbuffSpacetimeNexusModuleCycle,
                      dbuff.const.dbuffSpacetimeNexusTracking,
                      dbuff.const.dbuffSpacetimeNexusCapRecharge,
                      dbuff.const.dbuffSpacetimeNexusSigRadius,
                      dbuff.const.dbuffSpacetimeNexusTurretMissileDamage],
 Slot_TetheringRestrictedBySecurity: [dbuff.const.dbuffTetheringRestrictedBySecurity],
 Slot_RemoteRepairImpedance: [dbuff.const.dbuffRemoteRepairImpedance],
 Slot_SuppressionBonus: [dbuff.const.dbuffSuppressionInterdictionRange],
 Slot_CDCloudEffect: [dbuff.const.dbuffCDCloudVelocity,
                      dbuff.const.dbuffCDCloudInertia,
                      dbuff.const.dbuffCDCloudCapShieldRecharge,
                      dbuff.const.dbuffCDCloudModuleCycle,
                      dbuff.const.dbuffCDCloudTracking],
 Slot_AntiTachyonCloud: [dbuff.const.dbuffAntiTachyonCloudVelocity, dbuff.const.dbuffAntiTachyonCloudInertia, dbuff.const.dbuffAntiTachyonCloudSignatureRadius],
 Slot_TractorRepeatingBlocked: [dbuff.const.dbuffTractorBeamRepeatingActivationBlocked]}
