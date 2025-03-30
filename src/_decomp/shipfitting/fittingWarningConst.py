#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipfitting\fittingWarningConst.py
import dogma.const as dogmaConst
import evetypes
from inventorycommon import const as inventoryconst
import eve.common.lib.appConst as appConst
WARNING_PATH = 'res:/UI/Texture/classes/agency/iconExclamation.png'
WARNING_LEVEL_LOW = 1
WARNING_LEVEL_MEDIUM = 2
WARNING_LEVEL_HIGH = 3
WARNING_LEVEL_SKILL = 4
WARNING_ORDER = [WARNING_LEVEL_HIGH,
 WARNING_LEVEL_SKILL,
 WARNING_LEVEL_MEDIUM,
 WARNING_LEVEL_LOW]
YELLOW = (1.0, 0.78, 0.0, 1.0)
RED = (0.8, 0, 0, 1)
WHITE = (0.9, 0.9, 0.9, 1)
ORANGE = (1.0, 0.5, 0.0, 1)
DEFAULT_BADGE_COLOR = (0.5, 0.5, 0.5)
colorByWarningLevel = {WARNING_LEVEL_LOW: WHITE,
 WARNING_LEVEL_MEDIUM: YELLOW,
 WARNING_LEVEL_HIGH: RED,
 WARNING_LEVEL_SKILL: ORANGE}
headerByWarningLevel = {WARNING_LEVEL_LOW: 'UI/Fitting/FittingWindow/Warnings/HeaderLow',
 WARNING_LEVEL_MEDIUM: 'UI/Fitting/FittingWindow/Warnings/HeaderMedium',
 WARNING_LEVEL_HIGH: 'UI/Fitting/FittingWindow/Warnings/HeaderHigh',
 WARNING_LEVEL_SKILL: 'UI/Fitting/FittingWindow/Warnings/HeaderSkills'}
WARNING_MISSING_SUBSYSTEMS = 1
WARNING_MODULES_IN_INVALID_FLAGS = 2
WARNING_ARMOR_TANKED_SHIELD_SHIP = 3
WARNING_SHIELD_TANKED_ARMOR_SHIP = 4
WARNING_WRONG_TANKING = 5
WARNING_NOT_PROVIDING_BONUS = 6
WARNING_MIXING_TURRET_GROUPS = 7
WARNING_MIXING_LAUNCHER_GROUPS = 8
WARNING_MIXING_TURRET_SIZES = 9
WARNING_POLARIZED_WEAPONS = 10
WARNING_DUAL_TANKED = 11
WARNING_MULTI_TANKED = 12
WARNING_OVER_CPU_POWER = 13
WARNING_OVER_CPU = 14
WARNING_OVER_POWERGRID = 15
WARNING_OVERLOADED_CARGO = 16
WARNING_OFFLINE_MODULES = 17
WARNING_OVER_CALIBRATION = 18
WARNING_MISSING_REQ_CHARGES = 19
WARNING_MISSING_OPTIONAL_CHARGES = 20
WARNING_STACKING_PENALTY_MED = 21
WARNING_STACKING_PENALTY_LOW = 22
WARNING_STACKING_PENALTY_TARGETED_LOW = 23
WARNING_UNDERSIZED_PROP_MOD = 24
WARNING_DISABLED_BUBBLE_IMMUNITY = 25
WARNING_INEFFICIENT_PROP_MOD = 26
warningsByWarningID = {WARNING_MISSING_SUBSYSTEMS: (WARNING_LEVEL_HIGH, 'UI/Fitting/FittingWindow/Warnings/SubsystemShort', 'UI/Fitting/FittingWindow/Warnings/SubsystemHint'),
 WARNING_OVER_CPU: (WARNING_LEVEL_HIGH, 'UI/Fitting/FittingWindow/Warnings/CpuOverloadedShort', 'UI/Fitting/FittingWindow/Warnings/CpuOverloadedHint'),
 WARNING_OVER_POWERGRID: (WARNING_LEVEL_HIGH, 'UI/Fitting/FittingWindow/Warnings/PowergridOverloadedShort', 'UI/Fitting/FittingWindow/Warnings/PowergridOverloadedHint'),
 WARNING_OVER_CPU_POWER: (WARNING_LEVEL_HIGH, 'UI/Fitting/FittingWindow/Warnings/CpuPowergridOverloadedShort', 'UI/Fitting/FittingWindow/Warnings/CpuPowergridOverloadedHint'),
 WARNING_OVER_CALIBRATION: (WARNING_LEVEL_HIGH, 'UI/Fitting/FittingWindow/Warnings/CalibrationOverloadedShort', 'UI/Fitting/FittingWindow/Warnings/CalibrationOverloadedHint'),
 WARNING_OVERLOADED_CARGO: (WARNING_LEVEL_HIGH, 'UI/Fitting/FittingWindow/Warnings/CargoOverloadedShort', 'UI/Fitting/FittingWindow/Warnings/CargoOverloadedHint'),
 WARNING_MODULES_IN_INVALID_FLAGS: (WARNING_LEVEL_HIGH, 'UI/Fitting/FittingWindow/Warnings/ModulesInInvalidSlotsShort', 'UI/Fitting/FittingWindow/Warnings/ModulesInInvalidSlotsHint'),
 WARNING_WRONG_TANKING: (WARNING_LEVEL_MEDIUM, 'UI/Fitting/FittingWindow/Warnings/IncorrectTankingShort', 'UI/Fitting/FittingWindow/Warnings/IncorrectTankingHint'),
 WARNING_NOT_PROVIDING_BONUS: (WARNING_LEVEL_MEDIUM, 'UI/Fitting/FittingWindow/Warnings/NotProvidingBonusShort', 'UI/Fitting/FittingWindow/Warnings/NotProvidingBonusHint'),
 WARNING_MIXING_TURRET_GROUPS: (WARNING_LEVEL_MEDIUM, 'UI/Fitting/FittingWindow/Warnings/MixingTurretGroupsShort', 'UI/Fitting/FittingWindow/Warnings/MixingTurretGroupsHint'),
 WARNING_MIXING_LAUNCHER_GROUPS: (WARNING_LEVEL_MEDIUM, 'UI/Fitting/FittingWindow/Warnings/MixingLauncherGroupsShort', 'UI/Fitting/FittingWindow/Warnings/MixingLauncherGroupsHint'),
 WARNING_MIXING_TURRET_SIZES: (WARNING_LEVEL_MEDIUM, 'UI/Fitting/FittingWindow/Warnings/MixingTurretSizesShort', 'UI/Fitting/FittingWindow/Warnings/MixingTurretSizesHint'),
 WARNING_DUAL_TANKED: (WARNING_LEVEL_MEDIUM, 'UI/Fitting/FittingWindow/Warnings/ShipIsDualTankedShort', 'UI/Fitting/FittingWindow/Warnings/ShipIsDualTankedHint'),
 WARNING_MULTI_TANKED: (WARNING_LEVEL_MEDIUM, 'UI/Fitting/FittingWindow/Warnings/ShipIsMultiTankedShort', 'UI/Fitting/FittingWindow/Warnings/ShipIsMultiTankedHint'),
 WARNING_OFFLINE_MODULES: (WARNING_LEVEL_MEDIUM, 'UI/Fitting/FittingWindow/Warnings/OfflineModulesShort', 'UI/Fitting/FittingWindow/Warnings/OfflineModulesHint'),
 WARNING_STACKING_PENALTY_MED: (WARNING_LEVEL_MEDIUM, 'UI/Fitting/FittingWindow/Warnings/StackingPenaltyMedShort', 'UI/Fitting/FittingWindow/Warnings/StackingPenaltyMedHint'),
 WARNING_UNDERSIZED_PROP_MOD: (WARNING_LEVEL_MEDIUM, 'UI/Fitting/FittingWindow/Warnings/UndersizedPropModShort', 'UI/Fitting/FittingWindow/Warnings/UndersizedPropModHint'),
 WARNING_DISABLED_BUBBLE_IMMUNITY: (WARNING_LEVEL_MEDIUM, 'UI/Fitting/FittingWindow/Warnings/BubbleImmunityDisabledShort', 'UI/Fitting/FittingWindow/Warnings/BubbleImmunityDisabledHint'),
 WARNING_INEFFICIENT_PROP_MOD: (WARNING_LEVEL_MEDIUM, 'UI/Fitting/FittingWindow/Warnings/InefficientPropModShort', 'UI/Fitting/FittingWindow/Warnings/InefficientPropModHint'),
 WARNING_POLARIZED_WEAPONS: (WARNING_LEVEL_LOW, 'UI/Fitting/FittingWindow/Warnings/PolarizedWeaponsFittedShort', 'UI/Fitting/FittingWindow/Warnings/PolarizedWeaponsFittedHint'),
 WARNING_ARMOR_TANKED_SHIELD_SHIP: (WARNING_LEVEL_LOW, 'UI/Fitting/FittingWindow/Warnings/ArmorTankingShieldShipShort', 'UI/Fitting/FittingWindow/Warnings/ArmorTankingShieldShipHint'),
 WARNING_SHIELD_TANKED_ARMOR_SHIP: (WARNING_LEVEL_LOW, 'UI/Fitting/FittingWindow/Warnings/ShieldTankingArmorShipShort', 'UI/Fitting/FittingWindow/Warnings/ShieldTankingArmorShipHint'),
 WARNING_MISSING_REQ_CHARGES: (WARNING_LEVEL_LOW, 'UI/Fitting/FittingWindow/Warnings/MissingChargesForRequiredShort', 'UI/Fitting/FittingWindow/Warnings/MissingChargesForRequiredHint'),
 WARNING_MISSING_OPTIONAL_CHARGES: (WARNING_LEVEL_LOW, 'UI/Fitting/FittingWindow/Warnings/MissingChargesForOptionalShort', 'UI/Fitting/FittingWindow/Warnings/MissingChargesForOptionalHint'),
 WARNING_STACKING_PENALTY_LOW: (WARNING_LEVEL_LOW, 'UI/Fitting/FittingWindow/Warnings/StackingPenaltyLowShort', 'UI/Fitting/FittingWindow/Warnings/StackingPenaltyLowHint'),
 WARNING_STACKING_PENALTY_TARGETED_LOW: (WARNING_LEVEL_LOW, 'UI/Fitting/FittingWindow/Warnings/StackingPenaltyTargetedLowShort', 'UI/Fitting/FittingWindow/Warnings/StackingPenaltyTargetedLowHint')}
iconPathsByTurretGroup = {inventoryconst.groupProjectileWeapon: 'res:/UI/Texture/Icons/12_64_9.png',
 inventoryconst.groupHybridWeapon: 'res:/UI/Texture/Icons/13_64_1.png',
 inventoryconst.groupEnergyWeapon: 'res:/UI/Texture/Icons/13_64_9.png',
 inventoryconst.groupPrecursorTurret: 'res:/UI/Texture/Icons/Modules/disintegratorCannonS.png'}
iconPathForSizes = {1: 'res:/UI/Texture/classes/Fitting/Small.png',
 2: 'res:/UI/Texture/classes/Fitting/Medium.png',
 3: 'res:/UI/Texture/classes/Fitting/Large.png',
 4: 'res:/UI/Texture/classes/Fitting/XLarge.png'}
INFO_BUBBLE_SHIELD = 20
INFO_BUBBLE_ARMOR = 7
INFO_BUBBLE_SHIELD_OR_ARMOR = 2046
TANKED_FOR_SHILED = 1
TANKED_FOR_ARMOR = 2
DRONE_AND_FIGHTER_BAYS = [appConst.flagDroneBay, appConst.flagFighterBay] + appConst.fighterTubeFlags
GROUPS_AFFECTING_MODULE_GROUPS = {inventoryconst.groupGyrostabilizer: (inventoryconst.groupProjectileWeapon,),
 inventoryconst.groupMagneticFieldStabilizer: (inventoryconst.groupHybridWeapon,),
 inventoryconst.groupHeatSink: (inventoryconst.groupEnergyWeapon,),
 inventoryconst.groupDroneDamageAmplifier: (inventoryconst.groupCombatDrone,
                                            inventoryconst.groupHeavyFighter,
                                            inventoryconst.groupLightFighter,
                                            inventoryconst.groupStructureLightFighter,
                                            inventoryconst.groupStructureHeavyFighter),
 inventoryconst.groupEntropicRadiationSink: (inventoryconst.groupPrecursorTurret,),
 inventoryconst.groupDroneLinkAugmentor: evetypes.GetGroupIDsByCategory(inventoryconst.categoryDrone),
 inventoryconst.groupDroneNavigationComputer: evetypes.GetGroupIDsByCategories((inventoryconst.categoryDrone, inventoryconst.categoryFighter))}
TURRET_GROUPS = [inventoryconst.groupProjectileWeapon,
 inventoryconst.groupHybridWeapon,
 inventoryconst.groupEnergyWeapon,
 inventoryconst.groupPrecursorTurret]
SUBSYSTEM_INFO_BY_SLOT = {appConst.flagSubSystemSlot0: (inventoryconst.groupEngineeringSubSystems, 'res:/UI/Texture/Icons/81_64_11.png'),
 appConst.flagSubSystemSlot1: (inventoryconst.groupDefensiveSubSystems, 'res:/UI/Texture/Icons/81_64_10.png'),
 appConst.flagSubSystemSlot2: (inventoryconst.groupOffensiveSubSystems, 'res:/UI/Texture/Icons/81_64_12.png'),
 appConst.flagSubSystemSlot3: (inventoryconst.groupPropulsionSubSystems, 'res:/UI/Texture/Icons/81_64_13.png')}
HARD_CODED_GROUPIDS = {inventoryconst.typeCivilianGatlingAutocannon: inventoryconst.groupProjectileWeapon,
 inventoryconst.typeCivilianGatlingRailgun: inventoryconst.groupHybridWeapon,
 inventoryconst.typeCivilianLightElectronBlaster: inventoryconst.groupHybridWeapon,
 inventoryconst.typeCivilianGatlingPulseLaser: inventoryconst.groupEnergyWeapon}
