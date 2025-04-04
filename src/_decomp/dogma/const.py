#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\const.py
import inventorycommon.const
dgmAssPreAssignment = -1
dgmAssPreMul = 0
dgmAssPreDiv = 1
dgmAssModAdd = 2
dgmAssModSub = 3
dgmAssPostMul = 4
dgmAssPostDiv = 5
dgmAssPostPercent = 6
dgmAssPostAssignment = 7
dgmAssPostPercentUnNerfed = 8
dgmAssSpecialSkillRelationship = 9
dgmOperatorPrecedence = [dgmAssPreAssignment,
 dgmAssPreMul,
 dgmAssPreDiv,
 dgmAssModAdd,
 dgmAssModSub,
 dgmAssPostMul,
 dgmAssPostDiv,
 dgmAssPostPercent,
 dgmAssPostPercentUnNerfed,
 dgmAssPostAssignment]
dgmOperatorIDtoIndex = {operator:precedence for precedence, operator in enumerate(dgmOperatorPrecedence)}
assoc = {dgmAssPostPercent: 'Percentage Modifier',
 dgmAssPreMul: 'Multiply before addition',
 dgmAssPreAssignment: 'Assign before all other arithmetic',
 dgmAssModAdd: 'Add',
 dgmAssModSub: 'Subtract',
 dgmAssPostMul: 'Multiply after addition',
 dgmAssPreDiv: 'Divide before addition',
 dgmAssPostDiv: 'Divide after addition',
 dgmAssPostAssignment: 'Assign after all other arithmetic (override)',
 dgmAssPostPercentUnNerfed: "Percentage Modifier that can't be stacking penalised",
 dgmAssSpecialSkillRelationship: 'Special skill relationship'}
dgmNurfableOperations = [dgmAssPreMul,
 dgmAssPostMul,
 dgmAssPostPercent,
 dgmAssPreDiv,
 dgmAssPostDiv]
dgmUnnerfedCategories = [inventorycommon.const.categorySkill,
 inventorycommon.const.categoryImplant,
 inventorycommon.const.categoryShip,
 inventorycommon.const.categoryCharge,
 inventorycommon.const.categorySubSystem]
dgmPreStackingNerfOperators = {dgmAssPreAssignment: lambda ret, value: value,
 dgmAssPreMul: lambda ret, value: ret * value,
 dgmAssPreDiv: lambda ret, value: ret / value,
 dgmAssModAdd: lambda ret, value: ret + value,
 dgmAssModSub: lambda ret, value: ret - value}
dgmOperators = {dgmAssPreAssignment: lambda ret, value: value,
 dgmAssPostAssignment: lambda ret, value: value,
 dgmAssPreMul: lambda ret, value: ret * value,
 dgmAssPostMul: lambda ret, value: ret * value,
 dgmAssPreDiv: lambda ret, value: ret / value,
 dgmAssPostDiv: lambda ret, value: ret / value,
 dgmAssModAdd: lambda ret, value: ret + value,
 dgmAssModSub: lambda ret, value: ret - value,
 dgmAssPostPercent: lambda ret, value: ret * (100 + value) / 100,
 dgmAssPostPercentUnNerfed: lambda ret, value: ret * (100 + value) / 100}
dgmEnvSelf = 0
dgmEnvChar = 1
dgmEnvShip = 2
dgmEnvTarget = 3
dgmEnvOther = 4
dgmEnvArea = 5
dgmEffActivation = 1
dgmEffArea = 3
dgmEffOnline = 4
dgmEffPassive = 0
dgmEffTarget = 2
dgmEffOverload = 5
dgmEffDungeon = 6
dgmEffSystem = 7
dgmPassiveEffectCategories = (dgmEffPassive, dgmEffDungeon, dgmEffSystem)
dgmTauConstant = 10000
dgmExprSkip = 0
dgmExprOwner = 1
dgmExprShip = 2
dgmExprOwnerAndShip = 3
dgmExprOther = 4
dgmAttrCatGroup = 12
dgmAttrCatType = 11
attributeAccessDifficulty = 901
attributeAccessDifficultyBonus = 902
attributeAccuracyMultiplier = 205
attributeActivationBlocked = 1349
attributeActivationBlockedStrenght = 1350
attributeActivationTargetLoss = 855
attributeAgentAutoPopupRange = 844
attributeAgentCommRange = 841
attributeAgentID = 840
attributeAgility = 70
attributeIgnoreDronesBelowSignatureRadius = 1855
attributeAimedLaunch = 644
attributeAllowInFullyCorruptedHighSec = 5600
attributeAllowInFullyCorruptedLowSec = 5599
attributeAllowRefills = 2019
attributeAllowsCloneJumpsWhenActive = 981
attributeAllowedInCapIndustrialMaintenanceBay = 1891
attributeAllowOnlyFwAttackers = 5206
attributeAmmoLoaded = 127
attributeAnchoringDelay = 556
attributeAnchorDistanceMax = 1591
attributeAnchorDistanceMin = 1590
attributeAnchoringRequiresSovereignty = 1033
attributeRequiresIHubUpgrade = 1595
attributeRequiresSovHubUpgrade = 5688
attributeAnchoringSecurityLevelMax = 1032
attributeAnchoringSecurityLevelMin = 1946
attributeAoeCloudSize = 654
attributeAoeDamageReductionFactor = 1353
attributeAoeDamageReductionSensitivity = 1354
attributeAoeFalloff = 655
attributeAoeFalloffBonus = 857
attributeAoeVelocity = 653
attributeArmorBonus = 65
attributeArmorDamage = 266
attributeArmorDamageAmount = 84
attributeArmorDamageAmountBonus = 895
attributeArmorDamageDurationBonus = 896
attributeArmorDamageLimit = 2035
attributeArmorEmDamageResonance = 267
attributeArmorEmDamageResistanceBonus = 1465
attributeArmorExplosiveDamageResonance = 268
attributeArmorExplosiveDamageResistanceBonus = 1468
attributeArmorHP = 265
attributeArmorHPBonusAdd = 1159
attributeArmorHPMultiplier = 148
attributeArmorHpBonus = 335
attributeArmorKineticDamageResonance = 269
attributeArmorKineticDamageResistanceBonus = 1466
attributeArmorThermalDamageResonance = 270
attributeArmorThermalDamageResistanceBonus = 1467
attributeArmorRepairLimit = 2038
attributeArmorUniformity = 524
attributeAspectRatioHeight = 5760
attributeAspectRatioWidth = 5759
attributeAttributePoints = 185
attributeAurumConversionRate = 1818
attributeBarrageDmgMultiplier = 326
attributeBaseDefenderAllyCost = 1820
attributeBaseMaxScanDeviation = 1372
attributeBaseSensorStrength = 1371
attributeBaseScanRange = 1370
attributeBoosterAttributeModifier = 1126
attributeBoosterDuration = 330
attributeBoosterLastInjectionDatetime = 2422
attributeBoosterness = 1087
attributeBoosterMaxCharAgeHours = 1647
attributeBrokenRepairCostMultiplier = 1264
attributeCanBeJettisoned = 1852
attributeCanCloak = 1163
attributeCanJump = 861
attributeCanNotBeTrainedOnTrial = 1047
attributeCanReceiveCloneJumps = 982
attributeCapacitorBonus = 67
attributeCapacitorCapacity = 482
attributeCapacitorCapacityBonus = 1079
attributeCapacitorCapacityMultiplier = 147
attributeCapacitorCharge = 18
attributeCapacitorRechargeRateMultiplier = 144
attributeCapacitorNeedMultiplier = 216
attributeCapacitorNeed = 6
attributeCapacity = 38
attributeCapacitySecondary = 1233
attributeCapacityBonus = 72
attributeCapRechargeBonus = 314
attributeCaptureProximityInteractivesOnly = 5602
attributeCaptureProximityRange = 1337
attributeCargoCapacityMultiplier = 149
attributeCargoDeliverRange = 2790
attributeCargoGroup = 629
attributeCargoGroup2 = 1846
attributeCargoScanResistance = 188
attributeChanceToNotTargetSwitch = 1651
attributeCharge = 18
attributeChargedArmorDamageMultiplier = 1886
attributeChargeGroup1 = 604
attributeChargeGroup2 = 605
attributeChargeGroup3 = 606
attributeChargeGroup4 = 609
attributeChargeGroup5 = 610
attributeChargeRate = 56
attributeChargeSize = 128
attributeCharisma = 164
attributeCloakingTargetingDelay = 560
attributeCloakingTargetingDelayBonus = 619
attributeCloneJumpCoolDown = 1921
attributeClothingAlsoCoversCategory = 1797
attributeClothingAlsoCoversCategory2 = 2058
attributeClothingRemovesCategory = 1956
attributeClothingRemovesCategory2 = 2063
attributeClothingRuleException = 1957
attributeCloudDuration = 545
attributeCloudEffectDelay = 544
attributeColor = 1417
attributeCommandbonus = 833
attributeConstructionType = 1771
attributeConsumptionQuantity = 714
attributeConsumptionType = 713
attributeContainedSkillPoints = 2461
attributeContrabandDetectionChance = 723
attributeControlTowerMinimumDistance = 1165
attributeCopySpeedPercent = 387
attributeFleetHangarCapacity = 912
attributeCorporationMemberLimit = 190
attributeCpu = 50
attributeCpuLoad = 49
attributeCpuLoadLevelModifier = 1635
attributeCpuLoadPerKm = 1634
attributeCpuMultiplier = 202
attributeCpuOutput = 48
attributeCrystalVolatilityChance = 783
attributeCrystalVolatilityDamage = 784
attributeCrystalsGetDamaged = 786
attributeCynoJammerActivationDelay = 2794
attributeCynosuralFieldSpawnRadius = 2455
attributeDamage = 3
attributeDamageCloudChance = 522
attributeDamageCloudType = 546
attributeDamageMultiplier = 64
attributeDamageMultiplierBonus = 292
attributeDamageMultiplierBonusPerCycle = 2733
attributeDamageMultiplierBonusMax = 2734
attributeRepairMultiplierBonusPerCycle = 2796
attributeRepairMultiplierBonusMax = 2797
attributeDeadspaceUnsafe = 801
attributeDecloakFieldRange = 651
attributeDecryptorID = 1115
attributeDefaultCustomsOfficeTaxRate = 1781
attributeDevIndexMilitary = 1583
attributeDevIndexIndustrial = 1584
attributeDevIndexSovereignty = 1615
attributeDevIndexUpgrade = 1616
attributeDisallowActivateInForcefield = 1920
attributeDisallowAssistance = 854
attributeDisallowDocking = 2354
attributeDisallowEarlyDeactivation = 906
attributeDisallowInEmpireSpace = 1074
attributeDisallowInHazardSystem = 5561
attributeDisallowInHighSec = 1970
attributeDisallowOffensiveModifiers = 872
attributeDisallowRepeatingActivation = 1014
attributeDisallowWhenInvulnerable = 2395
attributeDisallowTethering = 2343
attributeDisallowCloaking = 2454
attributeDisallowDriveJumping = 2453
attributeDistributionID01 = 1755
attributeDistributionID02 = 1756
attributeDistributionID03 = 1757
attributeDistributionID04 = 1758
attributeDistributionID05 = 1759
attributeDistributionID06 = 1760
attributeDistributionID07 = 1761
attributeDistributionID08 = 1762
attributeDistributionID09 = 1763
attributeDistributionID10 = 1764
attributeDistributionIDAngel01 = 1695
attributeDistributionIDAngel02 = 1696
attributeDistributionIDAngel03 = 1697
attributeDistributionIDAngel04 = 1698
attributeDistributionIDAngel05 = 1699
attributeDistributionIDAngel06 = 1700
attributeDistributionIDAngel07 = 1701
attributeDistributionIDAngel08 = 1702
attributeDistributionIDAngel09 = 1703
attributeDistributionIDAngel10 = 1704
attributeDistributionIDBlood01 = 1705
attributeDistributionIDBlood02 = 1706
attributeDistributionIDBlood03 = 1707
attributeDistributionIDBlood04 = 1708
attributeDistributionIDBlood05 = 1709
attributeDistributionIDBlood06 = 1710
attributeDistributionIDBlood07 = 1711
attributeDistributionIDBlood08 = 1712
attributeDistributionIDBlood09 = 1713
attributeDistributionIDBlood10 = 1714
attributeDistributionIDGurista01 = 1715
attributeDistributionIDGurista02 = 1716
attributeDistributionIDGurista03 = 1717
attributeDistributionIDGurista04 = 1718
attributeDistributionIDGurista05 = 1719
attributeDistributionIDGurista06 = 1720
attributeDistributionIDGurista07 = 1721
attributeDistributionIDGurista08 = 1722
attributeDistributionIDGurista09 = 1723
attributeDistributionIDGurista10 = 1724
attributeDistributionIDRogueDrone01 = 1725
attributeDistributionIDRogueDrone02 = 1726
attributeDistributionIDRogueDrone03 = 1727
attributeDistributionIDRogueDrone04 = 1728
attributeDistributionIDRogueDrone05 = 1729
attributeDistributionIDRogueDrone06 = 1730
attributeDistributionIDRogueDrone07 = 1731
attributeDistributionIDRogueDrone08 = 1732
attributeDistributionIDRogueDrone09 = 1733
attributeDistributionIDRogueDrone10 = 1734
attributeDistributionIDSansha01 = 1735
attributeDistributionIDSansha02 = 1736
attributeDistributionIDSansha03 = 1737
attributeDistributionIDSansha04 = 1738
attributeDistributionIDSansha05 = 1739
attributeDistributionIDSansha06 = 1740
attributeDistributionIDSansha07 = 1741
attributeDistributionIDSansha08 = 1742
attributeDistributionIDSansha09 = 1743
attributeDistributionIDSansha10 = 1744
attributeDistributionIDSerpentis01 = 1745
attributeDistributionIDSerpentis02 = 1746
attributeDistributionIDSerpentis03 = 1747
attributeDistributionIDSerpentis04 = 1748
attributeDistributionIDSerpentis05 = 1749
attributeDistributionIDSerpentis06 = 1750
attributeDistributionIDSerpentis07 = 1751
attributeDistributionIDSerpentis08 = 1752
attributeDistributionIDSerpentis09 = 1753
attributeDistributionIDSerpentis10 = 1754
attributeDoesNotEmergencyWarp = 1854
attributeDoomsdayDamageCycleTime = 2265
attributeDoomsdayDamageDuration = 2264
attributeDoomsdayDamageRadius = 2263
attributeDoomsdayEnergyNeutAmount = 2260
attributeDoomsdayEnergyNeutRadius = 2259
attributeDoomsdayEnergyNeutSignatureRadius = 2261
attributeDoomsdayImmobilityDuration = 2428
attributeDoomsdayNoJumpOrCloakDuration = 2427
attributeDoomsdayWarningDuration = 2262
attributeDoomsdayAOEDuration = 2280
attributeDoomsdayAOERange = 2279
attributeDoomsdayAOESignatureRadius = 2281
attributeDoomsdayEnergyNeutResistanceID = 2609
attributeDoomsdayAppliedDBuffDuration = 5412
attributeDeactivateIfOffensive = 1934
attributeDrawback = 1138
attributeDroneBandwidth = 1271
attributeDroneBandwidthLoad = 1273
attributeDroneBandwidthUsed = 1272
attributeDroneCapacity = 283
attributeDroneControlDistance = 458
attributeDroneFocusFire = 1297
attributeDroneIsAggressive = 1275
attributeDroneIsChaotic = 1278
attributeDropChanceOverwrite = 3164
attributeDscanImmune = 1958
attributeDuplicatingChance = 399
attributeDuration = 73
attributeEcmBurstRange = 142
attributeEcuAreaOfInfluence = 1689
attributeEcuDecayFactor = 1683
attributeExtractorHeadCPU = 1690
attributeExtractorHeadPower = 1691
attributeEcuMaxVolume = 1684
attributeEcuOverlapFactor = 1685
attributeEcuNoiseFactor = 1687
attributeEffectDeactivationDelay = 1579
attributeEffectedByIndustrialInvulnModule = 2464
attributeEmDamage = 114
attributeEmDamageResistanceBonus = 984
attributeEmDamageResonance = 113
attributeEmDamageResonanceMultiplier = 133
attributeEmpFieldRange = 99
attributeEnergyNeutralizerAmount = 97
attributeEnergyNeutralizerRangeOptimal = 98
attributeEnergyNeutralizerRangeFalloff = 2452
attributeEnergyNeutralizerSignatureResolution = 2451
attributeEcmJamDuration = 2822
attributeEnergyNeutralizerDuration = 942
attributeEntityArmorRepairAmount = 631
attributeEntityArmorRepairAmountPerSecond = 1892
attributeEntityArmorRepairDelayChanceSmall = 1009
attributeEntityArmorRepairDelayChanceMedium = 1010
attributeEntityArmorRepairDelayChanceLarge = 1011
attributeEntityArmorRepairDuration = 630
attributeEntityAttackDelayMax = 476
attributeEntityAttackDelayMin = 475
attributeEntityAttackRange = 247
attributeEntityCapacitorLevel = 1894
attributeEntityCapacitorLevelModifierSmall = 1895
attributeEntityCapacitorLevelModifierMedium = 1896
attributeEntityCapacitorLevelModifierLarge = 1897
attributeEntityChaseMaxDelay = 580
attributeEntityChaseMaxDelayChance = 581
attributeEntityChaseMaxDistance = 665
attributeEntityChaseMaxDuration = 582
attributeEntityChaseMaxDurationChance = 583
attributeEntityCruiseSpeed = 508
attributeEntityDefenderChance = 497
attributeEntityEquipmentGroupMax = 465
attributeEntityEquipmentMax = 457
attributeEntityEquipmentMin = 456
attributeEntityFactionLoss = 562
attributeEntityFlyRange = 416
attributeEntityFlyRangeFactor = 772
attributeEntityGroupRespawnChance = 640
attributeEntityGroupArmorResistanceBonus = 1676
attributeEntityGroupArmorResistanceActivationChance = 1682
attributeEntityGroupArmorResistanceDuration = 1681
attributeEntityGroupPropJamBonus = 1675
attributeEntityGroupPropJamActivationChance = 1680
attributeEntityGroupPropJamDuration = 1679
attributeEntityGroupShieldResistanceBonus = 1671
attributeEntityGroupShieldResistanceActivationChance = 1673
attributeEntityGroupShieldResistanceDuration = 1672
attributeEntityGroupSpeedBonus = 1674
attributeEntityGroupSpeedActivationChance = 1678
attributeEntityGroupSpeedDuration = 1677
attributeEntityKillBounty = 481
attributeEntityMaxVelocitySignatureRadiusMultiplier = 1133
attributeEntityMaxWanderRange = 584
attributeEntityMissileTypeID = 507
attributeEntityReactionFactor = 466
attributeEntityRemoteECMBaseDuration = 1661
attributeEntityRemoteECMChanceOfActivation = 1664
attributeEntityRemoteECMDuration = 1658
attributeEntityRemoteECMDurationScale = 1660
attributeEntityRemoteECMExtraPlayerScale = 1662
attributeEntityRemoteECMIntendedNumPlayers = 1663
attributeEntityRemoteECMMinDuration = 1659
attributeEntitySecurityMaxGain = 563
attributeEntitySecurityStatusKillBonus = 252
attributeEntityShieldBoostAmount = 637
attributeEntityShieldBoostAmountPerSecond = 1893
attributeEntityShieldBoostDelayChanceSmall = 1006
attributeEntityShieldBoostDelayChanceMedium = 1007
attributeEntityShieldBoostDelayChanceLarge = 1008
attributeEntityShieldBoostDuration = 636
attributeEntitySuperWeaponDuration = 2009
attributeEntitySuperWeaponEmDamage = 2010
attributeEntitySuperWeaponExplosiveDamage = 2013
attributeEntitySuperWeaponFallOff = 2047
attributeEntitySuperWeaponKineticDamage = 2011
attributeEntitySuperWeaponMaxRange = 2046
attributeEntitySuperWeaponOptimalSignatureRadius = 2049
attributeEntitySuperWeaponThermalDamage = 2012
attributeEntitySuperWeaponTrackingSpeed = 2048
attributeEntityWarpScrambleChance = 504
attributeEntityShieldBoostDelayChanceSmallMultiplier = 1015
attributeEntityShieldBoostDelayChanceMediumMultiplier = 1016
attributeEntityShieldBoostDelayChanceLargeMultiplier = 1017
attributeEntityArmorRepairDelayChanceSmallMultiplier = 1018
attributeEntityArmorRepairDelayChanceMediumMultiplier = 1019
attributeEntityArmorRepairDelayChanceLargeMultiplier = 1020
attributeExpiryTime = 1088
attributeExplosionDelay = 281
attributeExplosionDelayWreck = 1162
attributeExplosionRange = 107
attributeExplosiveDamage = 116
attributeExplosiveDamageResistanceBonus = 985
attributeExplosiveDamageResonance = 111
attributeExplosiveDamageResonanceMultiplier = 132
attributeExportTax = 1639
attributeExportTaxMultiplier = 1641
attributeExtractorDepletionRange = 1644
attributeExtractorDepletionRate = 1645
attributeFactionID = 1341
attributeFalloff = 158
attributeFalloffBonus = 349
attributeFalloffEffectiveness = 2044
attributeFallofMultiplier = 517
attributeFastTalkPercentage = 359
attributeFighterAttackAndFollow = 1283
attributeFitsToShipType = 1380
attributeFollowsJumpClones = 1916
attributeFwLpKill = 1555
attributeApparelGender = 1773
attributeGateMaxJumpMass = 2798
attributeGateScrambleStatus = 1973
attributeGfxBoosterID = 246
attributeGfxTurretID = 245
attributeHarvesterQuality = 710
attributeHarvesterType = 709
attributeHasFleetHangars = 911
attributeHasShipMaintenanceBay = 907
attributeHeatAbsorbtionRateHi = 1182
attributeHeatAbsorbtionRateLow = 1184
attributeHeatAbsorbtionRateMed = 1183
attributeHeatAttenuationHi = 1259
attributeHeatAttenuationLow = 1262
attributeHeatAttenuationMed = 1261
attributeHeatCapacityHi = 1178
attributeHeatCapacityLow = 1200
attributeHeatCapacityMed = 1199
attributeHeatDamage = 1211
attributeHeatDissipationRateHi = 1179
attributeHeatDissipationRateLow = 1198
attributeHeatDissipationRateMed = 1196
attributeHeatGenerationMultiplier = 1224
attributeHeatAbsorbtionRateModifier = 1180
attributeHeatHi = 1175
attributeHeatLow = 1177
attributeHeatMed = 1176
attributeHiSecModifier = 2355
attributeHiSlotModifier = 1374
attributeHiSlots = 14
attributeHitsMissilesOnly = 823
attributeHp = 9
attributeHullEmDamageResonance = 974
attributeHullExplosiveDamageResonance = 975
attributeHullKineticDamageResonance = 976
attributeHullThermalDamageResonance = 977
attributeImmuneToSuperWeapon = 1654
attributeDamageDelayDuration = 1839
attributeDotDuration = 5735
attributeDotMaxDamagePerTick = 5736
attributeDotMaxHPPercentagePerTick = 5737
attributeImpactDamage = 660
attributeImplantness = 331
attributeImportTax = 1638
attributeImportTaxMultiplier = 1640
attributeIncapacitationRatio = 156
attributeIntelligence = 165
attributeInventionMEModifier = 1113
attributeInventionMaxRunModifier = 1124
attributeInventionPEModifier = 1114
attributeInventionPropabilityMultiplier = 1112
attributeInventionReverseEngineeringResearchSpeed = 1959
attributeIsIncapacitated = 1168
attributeIsArcheology = 1331
attributeIsCapitalSize = 1785
attributeIsCovert = 1252
attributeIsGlobal = 1207
attributeIsHacking = 1330
attributeIsIndustrialCyno = 2826
attributeIsOnline = 2
attributeIsPointTargeted = 2269
attributeIsRAMcompatible = 998
attributeJobCostMultiplier = 1954
attributeJumpClonesLeft = 1336
attributeJumpDriveCapacitorNeed = 898
attributeJumpDriveConsumptionAmount = 868
attributeGroupJumpDriveConsumptionAmount = 3131
attributeConduitJumpPassengerCount = 3133
attributeJumpDriveConsumptionType = 866
attributeJumpDriveDuration = 869
attributeJumpDriveRange = 867
attributeJumpFatigueMultiplier = 1971
attributeJumpThroughFatigueMultiplier = 1972
attributeJumpHarmonics = 1253
attributeJumpPortalCapacitorNeed = 1005
attributeJumpPortalConsumptionMassFactor = 1001
attributeJumpPortalAdditionalConsumption = 2793
attributeJumpPortalDuration = 1002
attributeKineticDamage = 117
attributeKineticDamageResistanceBonus = 986
attributeKineticDamageResonance = 109
attributeKineticDamageResonanceMultiplier = 131
attributeLauncherGroup = 137
attributeLauncherGroup2 = 602
attributeLauncherGroup3 = 603
attributeLauncherGroup4 = 2076
attributeLauncherGroup5 = 2077
attributeLauncherGroup6 = 2078
attributeLauncherHardPointModifier = 1369
attributeLauncherSlotsLeft = 101
attributeLightningWeaponDamageLossTarget = 2106
attributeLightningWeaponTargetAmount = 2104
attributeLightningWeaponTargetRange = 2105
attributeLightYearDistanceMax = 3097
attributeLocationListID = 3096
attributeLogisticalCapacity = 1631
attributeLootRespawnTime = 470
attributeLowSecModifier = 2356
attributeLowSlotModifier = 1376
attributeLowSlots = 12
attributeManufactureCostMultiplier = 369
attributeManufactureSlotLimit = 196
attributeManufactureTimeMultiplier = 219
attributeManufactureTimePerLevel = 1982
attributeManufacturingTimeResearchSpeed = 385
attributeMass = 4
attributeMassAddition = 796
attributeMassBonusPercentage = 1131
attributeMaxActiveDrones = 352
attributeMaxCharacterSkillPointLimit = 2459
attributeMaxDefenseBunkers = 1580
attributeMaxDirectionalVelocity = 661
attributeMaxGangModules = 435
attributeMaxGroupActive = 763
attributeMaxGroupFitted = 1544
attributeMaxGroupOnline = 978
attributeMaxJumpClones = 979
attributeMaxLaborotorySlots = 467
attributeMaxAttackTargets = 193
attributeMaxLockedTargets = 192
attributeMaxLockedTargetsBonus = 235
attributeMaxMissileVelocity = 664
attributeMaxOperationalDistance = 715
attributeMaxOperationalUsers = 716
attributeMaxRange = 54
attributeMaxRangeBonus = 351
attributeMaxScanDeviation = 788
attributeMaxScanGroups = 1122
attributeMaxScanRange = 2697
attributeMaxShipGroupActive = 910
attributeMaxShipGroupActiveID = 909
attributeMaxStructureDistance = 650
attributeMaxSubSystems = 1367
attributeMaxTargetRange = 76
attributeMaxTargetRangeMultiplier = 237
attributeMaxFOFTargetRange = 2700
attributeMaxTractorVelocity = 1045
attributeMaxTypeFitted = 2431
attributeMaxVelocity = 37
attributeMaxVelocityMultiplier = 1470
attributeMaxVelocityActivationLimit = 1334
attributeMinVelocityActivationLimit = 2608
attributeMaxVelocityLimited = 1333
attributeMaxVelocityBonus = 306
attributeUpwellChainCount = 3037
attributeUpwellChainRange = 3036
attributeMedSlotModifier = 1375
attributeMedSlots = 13
attributeMemory = 166
attributeMinMissileVelDmgMultiplier = 663
attributeMinScanDeviation = 787
attributeMinTargetVelDmgMultiplier = 662
attributeMineralNeedResearchSpeed = 398
attributeIgnoreMiningWaste = 3236
attributeMiningAmount = 77
attributeMiningDroneAmountPercent = 428
attributeMiningWasteVolumeMultiplier = 3153
attributeMiningWasteProbability = 3154
attributeMiningWastedVolumeMultiplierBonus = 3159
attributeMiningWasteProbabilityBonus = 3160
attributeMissileDamageMultiplier = 212
attributeMissileEntityAoeCloudSizeMultiplier = 858
attributeMissileEntityAoeFalloffMultiplier = 860
attributeMissileEntityAoeVelocityMultiplier = 859
attributeMissileEntityFlightTimeMultiplier = 646
attributeMissileEntityVelocityMultiplier = 645
attributeMissileLaunchDuration = 506
attributeMissileNeverDoesDamage = 1075
attributeModifyTargetSpeedChance = 512
attributeModifyTargetSpeedRange = 514
attributeModuleCannotBeUnfit = 2791
attributeModuleIsObsolete = 2696
attributeModuleReactivationDelay = 669
attributeModuleRepairRate = 1267
attributeMonumentAllianceID = 2787
attributeMonumentCorporationID = 3132
attributeMoonAnchorDistance = 711
attributeMoonMiningAmount = 726
attributeNeutReflectAmount = 1815
attributeNeutReflector = 1809
attributeNextActivationTime = 2729
attributeNonBrokenModuleRepairCostMultiplier = 1276
attributeNonDestructible = 1890
attributeNosOverride = 1945
attributeNosReflectAmount = 1814
attributeNosReflector = 1808
attributeNPCAssistancePriority = 1451
attributeNPCAssistanceRange = 1464
attributeNpcCustomsOfficeTaxRate = 1780
attributeNpcDroneBandwidth = 2785
attributeNPCRemoteArmorRepairAmount = 1455
attributeNPCRemoteArmorRepairDuration = 1454
attributeNPCRemoteArmorRepairMaxTargets = 1501
attributeNPCRemoteArmorRepairThreshold = 1456
attributeNPCRemoteShieldBoostAmount = 1460
attributeNPCRemoteShieldBoostDuration = 1458
attributeNPCRemoteShieldBoostMaxTargets = 1502
attributeNPCRemoteShieldBoostThreshold = 1462
attributeNullSecModifier = 2357
attributeOnliningDelay = 677
attributeOnliningRequiresSovUpgrade1 = 1601
attributeOrbitalStrikeAccuracy = 1844
attributeOrbitalStrikeDamage = 1845
attributeOnDeathAOERadius = 2275
attributeOnDeathSignatureRadius = 2276
attributeOnDeathDamageEM = 2271
attributeOnDeathDamageTherm = 2272
attributeOnDeathDamageKin = 2273
attributeOnDeathDamageExp = 2274
attributeOnlyTractorCorpses = 3102
attributeEntityOverviewShipGroupID = 1766
attributePinCycleTime = 1643
attributePinExtractionQuantity = 1642
attributePiTaxReduction = 1926
attributePosAnchoredPerSolarSystemAmount = 1195
attributePowerTransferAmount = 90
attributeProbeCanScanShips = 1413
attributeOperationalDuration = 719
attributeOptimalSigRadius = 620
attributePackageRadius = 690
attributePerception = 167
attributePassiveArmorEmDamageResonance = 1418
attributePassiveArmorExplosiveDamageResonance = 1421
attributePassiveArmorThermalDamageResonance = 1419
attributePassiveArmorKineticDamageResonance = 1420
attributePassiveEmDamageResistanceBonus = 994
attributePassiveExplosiveDamageResistanceBonus = 995
attributePassiveKineticDamageResistanceBonus = 996
attributePassiveShieldEmDamageResonance = 1423
attributePassiveShieldExplosiveDamageResonance = 1422
attributePassiveShieldKineticDamageResonance = 1424
attributePassiveShieldThermalDamageResonance = 1425
attributePassiveThermicDamageResistanceBonus = 997
attributePlanetAnchorDistance = 865
attributePlanetRestriction = 1632
attributePosCargobayAcceptGroup = 1352
attributePosCargobayAcceptType = 1351
attributePosControlTowerPeriod = 722
attributePosPlayerControlStructure = 1167
attributePosStructureControlAmount = 1174
attributePosStructureControlDistanceMax = 1214
attributePower = 30
attributePowerEngineeringOutputBonus = 313
attributePowerIncrease = 549
attributePowerLoad = 15
attributePowerLoadLevelModifier = 1636
attributePowerLoadPerKm = 1633
attributePowerOutput = 11
attributePowerOutputMultiplier = 145
attributePowerTransferRange = 91
attributeMaxNeutralizationRange = 98
attributePreferredSignatureRadius = 1655
attributePreFitServiceSlot0 = 2792
attributePreFitStructureCore = 5701
attributePrimaryAttribute = 180
attributePropulsionFusionStrength = 819
attributePropulsionFusionStrengthBonus = 815
attributePropulsionIonStrength = 820
attributePropulsionIonStrengthBonus = 816
attributePropulsionMagpulseStrength = 821
attributePropulsionMagpulseStrengthBonus = 817
attributePropulsionPlasmaStrength = 822
attributePropulsionPlasmaStrengthBonus = 818
attributeProximityRange = 154
attributePublished = 1975
attributePilotSecurityStatus = 2610
attributeQuantity = 805
attributeRaceID = 195
attributeRadius = 162
attributeRangeFactor = 1373
attributeReactionGroup1 = 842
attributeReactionGroup2 = 843
attributeReactionSlotLimit = 2664
attributeReactionTimeMultiplier = 2662
attributeRechargeRate = 55
attributeRefineryCapacity = 720
attributeRefineryReactionTimeMultiplier = 2721
attributeRefiningDelayMultiplier = 721
attributeRefiningYieldMoonOre = 2445
attributeRefiningYieldNormalOre = 2444
attributeRefiningYieldIce = 2448
attributeRefiningYieldMultiplier = 717
attributeRefiningYieldMutator = 379
attributeRefiningYieldPercentage = 378
attributeReloadTime = 1795
attributeReinforcementDuration = 1612
attributeReinforcementVariance = 1613
attributeRepairCostMultiplier = 187
attributeReprocessingSkillType = 790
attributeRequiredSkill1 = 182
attributeRequiredSkill1Level = 277
attributeRequiredSkill2 = 183
attributeRequiredSkill2Level = 278
attributeRequiredSkill3 = 184
attributeRequiredSkill3Level = 279
attributeRequiredSkill4 = 1285
attributeRequiredSkill4Level = 1286
attributeRequiredSkill5 = 1289
attributeRequiredSkill5Level = 1287
attributeRequiredSkill6 = 1290
attributeRequiredSkill6Level = 1288
attributeRequiredThermoDynamicsSkill = 1212
attributeResistanceShiftAmount = 1849
attributeRigSize = 1547
attributeRigSlots = 1137
attributeRofBonus = 293
attributeSecurityModifier = 2358
attributeServiceSlots = 2056
attributeServiceModuleFuelAmount = 2109
attributeServiceModuleOnlineAmount = 2110
attributeFlagAllAsSuspectOnLoot = 5265
attributeScanAllStrength = 1136
attributeScanFrequencyResult = 1161
attributeScanGravimetricStrength = 211
attributeScanGravimetricStrengthBonus = 238
attributeScanGravimetricStrengthPercent = 1027
attributeScanGravimetricStrengthPercentInterim = 2255
attributeScanLadarStrength = 209
attributeScanLadarStrengthBonus = 239
attributeScanLadarStrengthPercent = 1028
attributeScanLadarStrengthPercentInterim = 2256
attributeScanMagnetometricStrength = 210
attributeScanMagnetometricStrengthBonus = 240
attributeScanMagnetometricStrengthPercent = 1029
attributeScanMagnetometricStrengthPercentInterim = 2257
attributeScanRadarStrength = 208
attributeScanRadarStrengthBonus = 241
attributeScanRadarStrengthPercent = 1030
attributeScanRadarStrengthPercentInterim = 2258
attributeScanWormholeStrength = 1908
attributeEwTargetJam = 831
attributeScanRange = 765
attributeScanResolution = 564
attributeScanResolutionBonus = 566
attributeScanResolutionMultiplier = 565
attributeScanSpeed = 79
attributeSecondaryAttribute = 181
attributeSecurityProcessingFee = 1904
attributeShieldBonus = 68
attributeShieldBonusDurationBonus = 897
attributeShieldBoostMultiplier = 548
attributeShieldCapacity = 263
attributeShieldCapacityMultiplier = 146
attributeShieldCharge = 264
attributeShieldDamageLimit = 2034
attributeShieldEmDamageResonance = 271
attributeShieldEmDamageResistanceBonus = 1489
attributeShieldExplosiveDamageResonance = 272
attributeShieldExplosiveDamageResistanceBonus = 1490
attributeShieldKineticDamageResonance = 273
attributeShieldKineticDamageResistanceBonus = 1491
attributeShieldRadius = 680
attributeShieldRechargeRate = 479
attributeShieldRechargeRateMultiplier = 134
attributeShieldRepairLimit = 2037
attributeShieldThermalDamageResonance = 274
attributeShieldThermalDamageResistanceBonus = 1492
attributeShieldUniformity = 484
attributeShipBrokenModuleRepairCostMultiplier = 1277
attributeShipMaintenanceBayCapacity = 908
attributeShipScanResistance = 511
attributeShouldUseEffectMultiplier = 1652
attributeShouldUseEvasiveManeuver = 1414
attributeShouldUseTargetSwitching = 1648
attributeShouldUseSecondaryTarget = 1649
attributeShouldUseSignatureRadius = 1650
attributeSiegeMassMultiplier = 1471
attributeSiegeModeWarpStatus = 852
attributeSignatureRadius = 552
attributeSignatureRadiusAdd = 983
attributeSignatureRadiusBonus = 554
attributeSignatureRadiusBonusPercent = 973
attributeSignatureResolution = 620
attributeSignatureSuppressorSignatureRadiusBonusPassive = 3113
attributeSkillIsObsolete = 2450
attributeSkillLevel = 280
attributeSkillPoints = 276
attributeSkillPointsSaved = 419
attributeSkillTimeConstant = 275
attributeNonDiminishingSkillInjectorUses = 2806
attributeSlots = 47
attributeSmugglingChance = 445
attributeSocialBonus = 362
attributeSovBillSystemCost = 1603
attributeSovUpgradeSovereigntyHeldFor = 1597
attributeSovUpgradeRequiredOutpostUpgradeLevel = 1600
attributeSpawnWithoutGuardsToo = 903
attributeSpecialCommandCenterHoldCapacity = 1646
attributeSpecialPlanetaryCommoditiesHoldCapacity = 1653
attributeSpecialAmmoHoldCapacity = 1573
attributeSpecialBoosterHoldCapacity = 2657
attributeSpecialCorpseHoldCapacity = 2467
attributeSpecialFuelBayCapacity = 1549
attributeSpecialGasHoldCapacity = 1557
attributeSpecialIndustrialShipHoldCapacity = 1564
attributeSpecialLargeShipHoldCapacity = 1563
attributeSpecialMediumShipHoldCapacity = 1562
attributeSpecialMineralHoldCapacity = 1558
attributeGeneralMiningHoldCapacity = 1556
attributeSpecialIceHoldCapacity = 3136
attributeSpecialAsteroidHoldCapacity = 3227
attributeSpecialSalvageHoldCapacity = 1559
attributeSpecialShipHoldCapacity = 1560
attributeSpecialSmallShipHoldCapacity = 1561
attributeSpecialSubsystemHoldCapacity = 2675
attributeSpecialTutorialLootRespawnTime = 1582
attributeSpecialMaterialBayCapacity = 1770
attributeSpecialMobileDepotHoldCapacity = 5325
attributeSpecialColonyResourcesHoldCapacity = 5646
attributeSpecialQuafeHoldCapacity = 1804
attributeSpecialisationAsteroidTypeList = 3148
attributeSpecialisationAsteroidYieldMultiplier = 782
attributeSpecialOutputMoonMaterialBayCapacity = 5693
attributeSpeedBonus = 80
attributeSpeedBoostFactor = 567
attributeSpeedBoostFactorBonus = 1270
attributeSpeedFactor = 20
attributeSpeedFactorBonus = 1164
attributeSpeedFactorFloor = 2266
attributeStanceSwitchTime = 1985
attributeStationOreRefiningBonus = 1939
attributeStationTypeID = 472
attributeStructureBonus = 82
attributeStructureCanHaveAutoRepair = 5770
attributeStructureCanHaveArmorPhases = 5771
attributeStructureDamageAmount = 83
attributeStructureDamageLimit = 2036
attributeStructureHPMultiplier = 150
attributeStructureItemVisualFlag = 2334
attributeStructureRepairLimit = 2039
attributeStructureUniformity = 525
attributeSubSystemSlot = 1366
attributeSurveyScanRange = 197
attributeSystemEffectDamageReduction = 1686
attributeTypeColorScheme = 1768
attributeTankingModifier = 1657
attributeTankingModifierDrone = 1656
attributeTankingModifierFighter = 2612
attributeTargetFilterTypelistID = 189
attributeTargetHostileRange = 143
attributeTargetLockSilently = 3176
attributeTargetSwitchDelay = 691
attributeTargetSwitchTimer = 1416
attributeTetheringRange = 2268
attributeThermalDamage = 118
attributeThermalDamageResistanceBonus = 987
attributeThermalDamageResonance = 110
attributeThermalDamageResonanceMultiplier = 130
attributeTrackingSpeed = 160
attributeTrackingSpeedBonus = 767
attributeDisallowAgainstEwImmuneTarget = 1798
attributeTurretDamageScalingRadius = 1812
attributeTurretHardpointModifier = 1368
attributeTurretSlotsLeft = 102
attributeTypeListId = 2759
attributeTotalArmorRepairOnTarget = 2808
attributeTotalShieldRepairOnTarget = 2809
attributeTotalHullRepairOnTarget = 2810
attributeTotalCapTransferOnTarget = 2811
attributeUnanchoringDelay = 676
attributeUnfitCapCost = 785
attributeUntargetable = 1158
attributeUpgradeCapacity = 1132
attributeUpgradeCost = 1153
attributeUpgradeLoad = 1152
attributeUpgradeSlotsLeft = 1154
attributeUsageWeighting = 862
attributeValidTargetWhitelist = 5745
attributeVolume = 161
attributeMetaLevel = 633
attributeVulnerabilityRequired = 2111
attributeVelocityModifier = 1076
attributeWarpItemActivationLimit = 5432
attributeWarpBubbleImmune = 1538
attributeWarpBubbleImmuneModifier = 1539
attributeWarpCapacitorNeed = 153
attributeWarpDistanceXAxis = 5429
attributeWarpDistanceYAxis = 5430
attributeWarpDistanceZAxis = 5431
attributeWarpItemActivationLimit = 5432
attributeWarpScrambleRange = 103
attributeWarpScrambleStatus = 104
attributeWarpScrambleStrength = 105
attributeWarpSpeedMultiplier = 600
attributeWeaponRangeMultiplier = 120
attributeWillpower = 168
attributeDisallowActivateOnWarp = 1245
attributeBaseWarpSpeed = 1281
attributeMaxTargetRangeBonus = 309
attributeIndustrialBonusDroneDamage = 2580
attributeReclonerFuelQuantity = 3104
attributeReclonerFuelType = 3105
attributeRateOfFire = 51
attributeCloakStabilizationStrength = 3117
attributeStabilizeCloakDuration = 3118
attributeEnableOpenJumpPortal = 3125
attributeEnablePerformGroupJump = 3126
attributeCompressibleItemsTypeList = 3255
attributeGasDecompressionBaseEfficiency = 3262
attributeGasDecompressionEfficiencyBonus = 3260
attributeActivationRequiresActiveIndustrialCore = 3265
attributeActivationRequiresActiveSiegeModule = 5426
attributeJumpDriveTargetBeaconTypelistID = 3317
attributeJumpPortalPassengerRequiredAttributeID = 3318
attributeJumpConduitPassengerRequiredAttributeID = 3321
attributePauseShieldRepairDpsThreshold = 3354
attributePauseArmorRepairDpsThreshold = 3355
attributePauseHullRepairDpsThreshold = 3356
attributeWormholeMassRegeneration = 1384
attributeWormholeMaxJumpMass = 1385
attributeWormholeMaxStableMass = 1383
attributeWormholeMaxStableTime = 1382
attributeWormholeTargetSystemClass = 1381
attributeWormholeTargetDistribution = 1457
attributeBehaviorArmorRepairerAmount = 2635
attributeBehaviorMicroWarpDriveDischarge = 2614
attributeBehaviorMicroWarpDriveDuration = 2615
attributeBehaviorMicroWarpDriveMassAddition = 2616
attributeBehaviorMicroWarpDriveSignatureRadiusBonus = 2617
attributeBehaviorMicroWarpDriveSpeedFactor = 2618
attributeBehaviorMicroWarpDriveSpeedBoostFactor = 2619
attributeBehaviorMiningAmount = 2489
attributeBehaviorMiningDuration = 2490
attributeBehaviorMiningDischarge = 2674
attributeBehaviorMiningMaxRange = 2673
attributeBehaviorCombatOrbitRange = 2786
attributeBehaviorShieldBoosterAmount = 2723
attributeBehaviorMicroJumpAttackJumpDistance = 2818
attributeBehaviorSmartBombEntityDamageMultiplier = 3039
attributeRemoteResistanceID = 2138
attributeECMResistance = 2253
attributeRemoteAssistanceImpedance = 2135
attributeRemoteRepairImpedance = 2116
attributeEnergyWarfareResistance = 2045
attributeSensorDampenerResistance = 2112
attributeStasisWebifierResistance = 2115
attributeTargetPainterResistance = 2114
attributeWeaponDisruptionResistance = 2113
attributeMaxTargetRangeBonusInterim = 2136
attributeScanResolutionBonusInterim = 2137
attributeFalloffBonusInterim = 2140
attributeMaxRangeBonusInterim = 2139
attributeTrackingSpeedBonusInterim = 2141
attributeExplosionDelayBonus = 596
attributeExplosionDelayBonusInterim = 2144
attributeAoeCloudSizeBonus = 848
attributeAoeCloudSizeBonusInterim = 2142
attributeAoeVelocityBonus = 847
attributeAoeVelocityBonusInterim = 2143
attributeMissileVelocityBonus = 547
attributeMissileVelocityBonusInterim = 2145
attributeSignatureRadiusBonusInterim = 2147
attributeSpeedFactorInterim = 2148
attributeEntosisAssistanceImpedanceMultiplier = 2754
attributeCanActivateInGateCloak = 3123
attributeNumDays = 1551
attributeCharismaBonus = 175
attributeIntelligenceBonus = 176
attributeMemoryBonus = 177
attributePerceptionBonus = 178
attributeWillpowerBonus = 179
attributeVirusCoherence = 1909
attributeVirusStrength = 1910
attributeVirusUtilityElementSlots = 1911
attributeSpewContainerCount = 1912
attributeDefaultJunkLootTypeID = 1913
attributeSpewVelocity = 1914
attributeSpewContainerLifeExtension = 1917
attributeTierDifficulty = 1919
attributeSiphonProMaterial = 1929
attributeSiphonRawMaterial = 1928
attributeSiphonWasteAmount = 1930
attributeHackable = 1927
attributeAsteroidRadiusGrowthFactor = 1980
attributeAsteroidRadiusUnitSize = 1981
attributeAsteroidMaxRadius = 2727
attributeMicroJumpPortalRadius = 2067
attributeMicroJumpDistance = 2066
attributeMicroJumpPortalMaxShipCandidates = 2832
attributeMicroJumpPortalMaxCapitalShipCandidates = 5686
attributeMicroJumpPostActivationScramDuration = 5687
attributeMJDBlocked = 5694
attributeFighterCapacity = 2055
attributeFrigateEscapeBayCapacity = 3020
attributeFighterTubes = 2216
attributeFighterLightSlots = 2217
attributeFighterSupportSlots = 2218
attributeFighterHeavySlots = 2219
attributeFighterStandupLightSlots = 2737
attributeFighterStandupSupportSlots = 2738
attributeFighterStandupHeavySlots = 2739
attributeFighterSquadronSize = 2150
attributeFighterSquadronMaxSize = 2215
attributeFighterSquadronIsHeavy = 2214
attributeFighterSquadronIsLight = 2212
attributeFighterSquadronIsSupport = 2213
attributeFighterSquadronIsStandupLight = 2740
attributeFighterSquadronIsStandupSupport = 2741
attributeFighterSquadronIsStandupHeavy = 2742
attributeFighterSquadronRole = 2270
attributeFighterSquadronOrbitRange = 2223
attributeFighterRefuelingTime = 2426
attributeFighterAbilityAntiFighterMissileResistance = 2189
attributeFighterAbilityAttackTurretDamageMultiplier = 2178
attributeFighterAbilityAttackTurretDuration = 2177
attributeFighterAbilityAttackTurretDamageEM = 2171
attributeFighterAbilityAttackTurretDamageTherm = 2172
attributeFighterAbilityAttackTurretDamageKin = 2173
attributeFighterAbilityAttackTurretDamageExp = 2174
attributeFighterAbilityAttackTurretRangeOptimal = 2175
attributeFighterAbilityAttackTurretRangeFalloff = 2176
attributeFighterAbilityAttackTurretSignatureResolution = 2179
attributeFighterAbilityAttackTurretTrackingSpeed = 2180
attributeFighterAbilityAttackMissileDamageEM = 2227
attributeFighterAbilityAttackMissileDamageTherm = 2228
attributeFighterAbilityAttackMissileDamageKin = 2229
attributeFighterAbilityAttackMissileDamageExp = 2230
attributeFighterAbilityAttackMissileDamageMultiplier = 2226
attributeFighterAbilityAttackMissileReductionFactor = 2231
attributeFighterAbilityAttackMissileReductionSensitivity = 2232
attributeFighterAbilityAttackMissileDuration = 2233
attributeFighterAbilityAttackMissileExplosionRadius = 2234
attributeFighterAbilityAttackMissileExplosionVelocity = 2235
attributeFighterAbilityAttackMissileRangeOptimal = 2236
attributeFighterAbilityAttackMissileRangeFalloff = 2237
attributeFighterAbilityAfterburnerDuration = 2158
attributeFighterAbilityAfterburnerSpeedBonus = 2151
attributeFighterAbilityMicroWarpDriveDuration = 2157
attributeFighterAbilityMicroWarpDriveSignatureRadiusBonus = 2153
attributeFighterAbilityMicroWarpDriveSpeedBonus = 2152
attributeFighterAbilityMicroJumpDriveDistance = 2154
attributeFighterAbilityMicroJumpDriveDuration = 2155
attributeFighterAbilityMicroJumpDriveSignatureRadiusBonus = 2156
attributeFighterAbilityEvasiveManeuversDuration = 2123
attributeFighterAbilityEvasiveManeuversEmResonance = 2118
attributeFighterAbilityEvasiveManeuversExpResonance = 2121
attributeFighterAbilityEvasiveManeuversKinResonance = 2120
attributeFighterAbilityEvasiveManeuversThermResonance = 2119
attributeFighterAbilityEvasiveManeuversSignatureRadiusBonus = 2225
attributeFighterAbilityEvasiveManeuversSpeedBonus = 2224
attributeFighterAbilityMissilesDuration = 2182
attributeFighterAbilityMissilesRange = 2149
attributeFighterAbilityMissilesDamageReductionFactor = 2127
attributeFighterAbilityMissilesDamageReductionSensitivity = 2128
attributeFighterAbilityMissilesExplosionRadius = 2125
attributeFighterAbilityMissilesExplosionVelocity = 2126
attributeFighterAbilityMissilesDamageMultiplier = 2130
attributeFighterAbilityMissilesEMDamage = 2131
attributeFighterAbilityMissilesThermDamage = 2132
attributeFighterAbilityMissilesKinDamage = 2133
attributeFighterAbilityMissilesExpDamage = 2134
attributeFighterAbilityMissilesResistanceID = 2170
attributeFighterAbilityStasisWebifierDuration = 2183
attributeFighterAbilityStasisWebifierFalloffRange = 2187
attributeFighterAbilityStasisWebifierOptimalRange = 2186
attributeFighterAbilityStasisWebifierResistanceID = 2188
attributeFighterAbilityStasisWebifierSpeedPenalty = 2184
attributeFighterAbilityStasisWebifierSpeedPenaltyInterim = 2185
attributeFighterAbilityEnergyNeutralizerAmount = 2211
attributeFighterAbilityEnergyNeutralizerDuration = 2208
attributeFighterAbilityEnergyNeutralizerFalloffRange = 2210
attributeFighterAbilityEnergyNeutralizerOptimalRange = 2209
attributeFighterAbilityEnergyNeutralizerResistanceID = 2207
attributeFighterAbilityWarpDisruptionDuration = 2203
attributeFighterAbilityWarpDisruptionPointStrength = 2205
attributeFighterAbilityWarpDisruptionPointStrengthInterim = 2206
attributeFighterAbilityWarpDisruptionRange = 2204
attributeFighterAbilityECMDuration = 2220
attributeFighterAbilityECMResistanceID = 2252
attributeFighterAbilityECMRangeOptimal = 2221
attributeFighterAbilityECMRangeFalloff = 2222
attributeFighterAbilityECMStrengthGravimetric = 2246
attributeFighterAbilityECMStrengthLadar = 2247
attributeFighterAbilityECMStrengthMagnetometric = 2248
attributeFighterAbilityECMStrengthRadar = 2249
attributeFighterAbilityECMTargetJam = 2251
attributeFighterAbilityTackleDuration = 2238
attributeFighterAbilityTackleRange = 2239
attributeFighterAbilityTackleWebSpeedPenalty = 2242
attributeFighterAbilityTackleWebSpeedPenaltyInterim = 2243
attributeFighterAbilityTackleWarpDisruptionPointStrength = 2425
attributeFighterAbilityKamikazeSignatureRadius = 2329
attributeFighterAbilityKamikazeRange = 2330
attributeFighterAbilityKamikazeDamageEM = 2325
attributeFighterAbilityKamikazeDamageExp = 2328
attributeFighterAbilityKamikazeDamageKin = 2327
attributeFighterAbilityKamikazeDamageTherm = 2326
attributeFighterAbilityKamikazeResistanceID = 2432
attributeFighterAbilityKamikazeResistance = 2433
attributeFighterAbilityLaunchBombType = 2324
attributeEngineeringComplexMaterialBonus = 2600
attributeEngineeringComplexCostBonus = 2601
attributeEngineeringComplexTimeBonus = 2602
attributeExtractionAutoFractureDelay = 2698
attributeExtractionYieldMultiplier = 2704
attributeExtractionFieldSizeMultiplier = 2705
attributeExtractionAsteroidDecayTime = 2706
attributeWeatherID = 2760
attributeDifficultyTier = 2761
attributeActiveSystemJump = 3025
attributeFilamentDescriptionMessageID = 3026
attributeFilamentSpoolupTimeSeconds = 5783
attributeAmountOfFleetsPerMatch = 3050
attributeFleetMemberPickupRadius = 3051
attributeFleetMembersNeeded = 3052
attributeStructureRequiresDeedType = 3101
attributestructureDropLootTableID = 5754
attributeDbuff1ID = 2468
attributeDbuff1Value = 2469
attributeDbuff1Multiplier = 2596
attributeDbuff2ID = 2470
attributeDbuff2Value = 2471
attributeDbuff2Multiplier = 2597
attributeDbuff3ID = 2472
attributeDbuff3Value = 2473
attributeDbuff3Multiplier = 2598
attributeDbuff4ID = 2536
attributeDbuff4Value = 2537
attributeDbuff4Multiplier = 2599
dbuffAttributeValueMappings = {attributeDbuff1ID: attributeDbuff1Value,
 attributeDbuff2ID: attributeDbuff2Value,
 attributeDbuff3ID: attributeDbuff3Value,
 attributeDbuff4ID: attributeDbuff4Value}
dbuffAttributeMultiplierMappings = {attributeDbuff1ID: attributeDbuff1Multiplier,
 attributeDbuff2ID: attributeDbuff2Multiplier,
 attributeDbuff3ID: attributeDbuff3Multiplier,
 attributeDbuff4ID: attributeDbuff4Multiplier}
attributeBuffDuration = 2535
attributeHasLongAnimationWhenAddedToSpaceScene = 2827
attributeIsCynoJammer = 3038
subsystemBonusAmarrElectronic = 1507
subsystemBonusGallenteElectronic = 1517
subsystemBonusCaldariElectronic = 1516
subsystemBonusMinmatarElectronic = 1526
effectAdaptiveArmorHardener = 4928
effectAnchorDrop = 649
effectAnchorDropForStructures = 1022
effectAnchorLift = 650
effectAnchorLiftForStructures = 1023
effectArmorRepair = 27
effectBarrage = 263
effectBehaviorNPCRemoteArmorRepair = 6165
effectBombLaunching = 2971
effectCloaking = 607
effectCloakingPrototype = 5945
effectCloakingWarpSafe = 980
effectCloneVatBay = 2858
effectConcordModifyTargetSpeed = 3714
effectConcordTargetJam = 3710
effectCynosuralGeneration = 2857
effectDecreaseTargetSpeed = 586
effectDecreaseTargetSpeedForStructures = 2480
effectDefenderMissileLaunching = 103
effectDeployPledge = 4774
effectDoHacking = 1738
effectDroneCapacityAdddroneCapacityPassive = 3799
effectECMBurst = 53
effectECMBurstJammer = 6714
effectECMBurstJammerQA = 6715
effectEmergencyHullEnergizer = 6484
effectEmpWave = 38
effecttargetABCAttack = 6995
effectChainLightning = 8037
effectEntityChainLightning = 8088
effectShipModuleRemoteArmorMutadaptiveRepairer = 7166
effectEmpWaveGrid = 2071
effectEnergyDestabilizationForStructure = 3003
effectEnergyDestabilizationNew = 2303
effectEnergyNeutralizerFalloff = 6187
effectStarbaseEnergyNeutralizerFalloff = 6696
effectEnergyNosferatuFalloff = 6197
effectEnergyTransfer = 31
effectEntityArmorRepairing = 5370
effectEntityArmorRepairingLarge = 2197
effectEntityArmorRepairingMedium = 2196
effectEntityArmorRepairingSmall = 2195
effectEntityCapacitorDrain = 1872
effectEntitySensorDampen = 1878
effectEntityShieldBoosting = 5371
effectEntityShieldBoostingLarge = 2194
effectEntityShieldBoostingMedium = 2193
effectEntityShieldBoostingSmall = 2192
effectEntitySuperWeapon = 6042
effectEntitySuperWeaponLanceAllRaces = 11716
effectEntityTargetJam = 1871
effectEntityTargetPaint = 1879
effectEntityTrackingDisrupt = 4982
effectEntosisLink = 6063
effectEwTargetPaint = 1549
effectEwTestEffectJam = 1358
effectEwTestEffectWs = 1355
effectFighterMissile = 4729
effectFighterSpeedBoostSigRad = 6382
effectFlagshipmultiRelayEffect = 1495
effectFofMissileLaunching = 104
effectFueledArmorRepair = 5275
effectFueledShieldBoosting = 4936
effectGangAbMwdFactorBoost = 1755
effectGangArmorHardening = 1510
effectGangArmorRepairCapReducerSelfAndProjected = 3165
effectGangArmorRepairSpeedAmplifierSelfAndProjected = 3167
effectGangBonusSignature = 1411
effectGangECCMfixed = 1648
effectGangGasHarvesterAndIceHarvesterAndMiningLaserCapNeedBonus = 3307
effectGangGasHarvesterAndIceHarvesterAndMiningLaserDurationBonus = 3302
effectGangIceHarvestingDurationBonus = 2441
effectGangInformationWarfareRangeBonus = 2642
effectGangInformationWarfareSuperiority = 3647
effectGangMiningLaserAndIceHarvesterAndGasCloudHarvesterMaxRangeBonus = 3296
effectGangPropulsionJammingBoost = 1546
effectGangShieldBoosterAndTransporterCapacitorNeed = 2418
effectGangShieldBoosterAndTransporterSpeed = 2415
effectGangShieldHardening = 1548
effectGuidanceDisrupt = 6383
effectHackOrbital = 4773
effectHardPointModifier = 3773
effectHiPower = 12
effectIndustrialCompactCoreEffect = 8119
effectIndustrialCoreEffect = 4575
effectJumpPortalGeneration = 2152
effectJumpPortalGenerationBO = 3674
effectLauncherFitted = 40
effectLeech = 3250
effectLoPower = 11
effectLightningWeapon = 6447
effectMarauderModeEffect = 5788
effectMaxTargetRangeBonus = 2646
effectMedPower = 13
effectMicroJumpDrive = 4921
effectMicroJumpPortalDrive = 6208
effectMicroJumpPortalDriveCapital = 12126
effectMicroJumpTarget = 5740
effectModuleBonusMicrowarpdrive = 6730
effectModuleBonusAfterburner = 6731
effectMineLaying = 102
effectMining = 17
effectMiningClouds = 2726
effectMiningLaser = 67
effectMissileLaunching = 9
effectMissileLaunchingForEntity = 569
effectModifyArmorResonancePostPercent = 2041
effectModifyHullResonancePostPercent = 3791
effectModifyShieldResonancePostPercent = 2052
effectModifyTargetSpeed2 = 575
effectModuleStasisImpedence = 7124
effectNPCGroupArmorAssist = 4689
effectNPCGroupPropJamAssist = 4688
effectNPCGroupShieldAssist = 4686
effectNPCGroupSpeedAssist = 4687
effectNPCRemoteArmorRepair = 3852
effectNPCRemoteECM = 4656
effectNPCRemoteShieldBoost = 3855
effectOffensiveDefensiveReduction = 4728
effectOnline = 16
effectOnlineForStructures = 901
effectOrbitalStrike = 5141
effectOverloadRofBonus = 3001
effectPacifierDebuffQA = 6716
effectPointDefense = 6443
effectProbeLaunching = 3793
effectProjectileFired = 34
effectProjectileFiredForEntities = 1086
effectRemoteEcmBurst = 2913
effectRemoteTracking = 4560
effectResistanceKillerHullAll = 5994
effectResistanceKillerShieldArmorAll = 5995
effectRigSlot = 2663
effectSalvageDroneEffect = 5163
effectSalvaging = 2757
effectScanStrengthBonusTarget = 124
effectScanStrengthTargetPercentBonus = 2246
effectSensorBoostTargetedHostile = 837
effectShieldBoosting = 4
effectShieldResonanceMultiplyOnline = 105
effectShieldTransfer = 18
effectShipMaxTargetRangeBonusOnline = 3659
effectSiegeModeEffect = 4877
effectSiegeModule = 6582
effectServiceSlot = 6306
effectSkillEffect = 132
effectSlashWeapon = 6201
effectDoomsdayAOEECM = 6513
effectDebuffLance = 11691
effectDoomsdayBeamDOT = 6472
effectDoomsdayConeDOT = 6473
effectDoomsdayHOG = 6474
effectDoomsdayAOEBubble = 6482
effectDoomsdayAOEDamp = 6481
effectDoomsdayAOENeut = 6477
effectDoomsdayAOEPaint = 6478
effectDoomsdayAOETrack = 6479
effectDoomsdayAOEWeb = 6476
effectDotMissileLaunching = 12174
effectSlotModifier = 3774
effectSnowBallLaunching = 2413
effectStructureModuleEffectStasisWebifier = 6682
effectStructureModuleEffectTargetPainter = 6683
effectStructureModuleEffectRemoteSensorDampener = 6684
effectStructureModuleEffectECM = 6685
effectStructureModuleEffectWeaponDisruption = 6686
effectStructureDecreaseTargetSpeed = 6219
effectStructureEnergyNeutralizerFalloff = 6216
effectStructureEwEffectJam = 6218
effectStructureEwTargetPaint = 6221
effectStructureRepair = 26
effectStructureUnanchorForced = 1129
effectStructureCynoJammerOnline = 7120
effectStructureTargetMaxTargetRangeAndScanResolutionBonusAssistance = 6223
effectStructureTargetMaxTargetRangeAndScanResolutionBonusHostile = 6217
effectStructureTargetGunneryMaxRangeFalloffTrackingSpeedBonusAssistance = 6225
effectStructureTargetGunneryMaxRangeAndTrackingSpeedAndFalloffBonusHostile = 6220
effectSubSystem = 3772
effectSuicideBomb = 885
effectSuperWeaponAmarr = 4489
effectSuperWeaponCaldari = 4490
effectSuperWeaponGallente = 4491
effectSuperWeaponMinmatar = 4492
effectTargetArmorRepair = 592
effectTargetAttack = 10
effectTargetAttackForStructures = 1199
effectTargetBreaker = 4942
effectTargetDisintegratorAttack = 6995
effectTargetGunneryMaxRangeAndTrackingSpeedAndFalloffBonusHostile = 3690
effectTargetGunneryMaxRangeAndTrackingSpeedBonusHostile = 3555
effectTargetGunneryMaxRangeAndTrackingSpeedBonusAssistance = 3556
effectTargetMaxTargetRangeAndScanResolutionBonusAssistance = 3583
effectTargetMaxTargetRangeAndScanResolutionBonusHostile = 3584
effectTargetPassively = 54
effectTargetTrackingDisruptorCombinedGunneryAndMissileEffect = 4932
effectTorpedoLaunching = 127
effectTorpedoLaunchingIsOffensive = 2576
effectTractorBeamCan = 2255
effectTractorBeamShip = 6445
effectTriageMode = 4839
effectTriageMode7 = 4893
effectTurretFitted = 42
effectTurretWeaponRangeFalloffTrackingSpeedMultiplyTargetHostile = 3697
effectUseMissiles = 101
effectModuleBonusIndustrialInvulnerability = 6719
effectModuleTitanBurst = 6753
effectAoeBeaconBioluminescenceCloud = 7050
effectAoeBeaconCausticCloud = 7051
effectAoeBeaconPulsePlatform = 7053
effectAoeBeaconPointDefense = 7057
effectAoeFilamentCloud = 7058
effectWeatherCausticToxin = 7059
effectWeatherDarkness = 7060
effectWeatherInfernal = 7062
effectWeatherXenonGas = 7063
effectWeatherElectricStorm = 7061
effectCloneRespawnBay = 8093
effectIndustrialItemCompression = 8364
effectWarpDisruptSphere = 3380
effectWarpDisrupt = 39
effectWarpScrambleBlockMWDWithNPCEffect = 5934
effectWarpScrambleForEntity = 563
effectWarpScrambleForStructure = 2481
effectWarpScrambleTargetMWDBlockActivationForEntity = 5928
effectStructureWarpScrambleBlockMWDWithNPCEffect = 6222
effectEssWarpScramble = 5768
effectConcordWarpScramble = 3713
effectShipModuleFocusedWarpDisruptionScript = 6849
effectShipModuleFocusedWarpScramblingScript = 6848
effectModuleBonusWarfareLinkArmor = 6732
effectModuleBonusWarfareLinkInfo = 6735
effectModuleBonusWarfareLinkMining = 6736
effectModuleBonusWarfareLinkShield = 6733
effectModuleBonusWarfareLinkSkirmish = 6734
effectChargeBonusWarfareCharge = 6737
effectShipModuleRemoteGuidanceComputer = 6429
effectShipModuleRemoteTrackingComputer = 6428
effectShipModuleRemoteHullRepairer = 6185
effectShipModuleRemoteArmorRepairer = 6188
effectShipModuleRemoteShieldBooster = 6186
effectShipModuleRemoteCapacitorTransmitter = 6184
effectRemoteSensorBoostFalloff = 6427
effectRemoteECCMFalloff = 6471
effectShipModuleAncillaryRemoteArmorRepairer = 6651
effectShipModuleAncillaryRemoteShieldBooster = 6652
effectShipModuleGuidanceDisruptor = 6423
effectShipModuleTrackingDisruptor = 6424
effectRemoteSensorDampFalloff = 6422
effectRemoteTargetPaintFalloff = 6425
effectRemoteWebifierFalloff = 6426
effectRemoteECMFalloff = 6470
effectEntityEnergyNeutralizerFalloff = 6691
effectEntityECMFalloff = 6695
effectNpcEntityRemoteArmorRepairer = 6687
effectNpcEntityRemoteHullRepairer = 6689
effectRemoteSensorDampEntity = 6693
effectNpcEntityRemoteShieldBooster = 6688
effectRemoteTargetPaintEntity = 6692
effectRemoteWebifierEntity = 6690
effectNpcEntityWeaponDisruptor = 6694
effectNpcEntityTrackingDisruptor = 6846
effectNpcBehaviorRemoteArmorRepairer = 6741
effectNpcBehaviorRemoteCapacitorTransmitter = 12073
effectNpcBehaviorRemoteShieldBooster = 6742
effectNpcBehaviorWebifier = 6743
effectNpcBehaviorGuidanceDisruptor = 6746
effectNpcBehaviorTrackingDisruptor = 6747
effectBehaviorWarpDisrupt = 6744
effectBehaviorWarpScramble = 6745
effectNpcBehaviorEnergyNeutralizer = 6756
effectNpcBehaviorEnergyNosferatu = 6882
effectBehaviorTargetPainter = 6754
effectBehaviorSensorDampener = 6755
effectBehaviorECM = 6757
effectNpcBehaviorMicroWarpDrive = 6864
effectNpcBehaviorArmorRepairer = 6884
effectNpcBehaviorMiningLaser = 6901
effectNpcBehaviorFakeMiningLaser = 11453
effectNpcBehaviorShieldBooster = 6990
effectNpcBehaviorMicroJumpAttack = 7187
effectNpcBehaviorSmartBomb = 7188
effectFighterAbilityAttackTurret = 6430
effectFighterAbilityAttackMissile = 6465
effectFighterAbilityEvasiveManeuvers = 6439
effectFighterAbilityAfterburner = 6440
effectFighterAbilityMicroWarpDrive = 6441
effectFighterAbilityMicroJumpDrive = 6442
effectFighterAbilityMissiles = 6431
effectFighterAbilityECM = 6437
effectFighterAbilityEnergyNeutralizer = 6434
effectFighterAbilityStasisWebifier = 6435
effectFighterAbilityWarpDisruption = 6436
effectFighterAbilityTackle = 6464
effectFighterAbilityLaunchBomb = 6485
effectFighterDecreaseTargetSpeed = 6418
effectFighterTargetPaint = 6419
effectFighterDamageMultiply = 6420
effectFighterMicroJumpDrive = 6421
effectFighterAbilityKamikaze = 6554
effectAnalyticalMindIntelligenceBonusModAddIntelligenceLocationChar = 306
effectEmpathyCharismaBonusModAddCharismaLocationChar = 302
effectInstantRecallMemoryBonusModAddMemoryLocationChar = 304
effectIronWillWillpowerBonusModAddWillpowerLocationChar = 308
effectSpatialAwarenessPerceptionBonusModAddPerceptionLocationChar = 310
JUMP_DRIVE_DISRUPTION_EFFECTS = (effectWarpScrambleBlockMWDWithNPCEffect,
 effectStructureWarpScrambleBlockMWDWithNPCEffect,
 effectFighterAbilityTackle,
 effectBehaviorWarpScramble,
 effectWarpDisruptSphere,
 effectWarpScrambleTargetMWDBlockActivationForEntity)
REMOTE_REPAIR_EFFECTS = [effectShipModuleRemoteHullRepairer,
 effectShipModuleRemoteArmorRepairer,
 effectShipModuleRemoteShieldBooster,
 effectShipModuleRemoteCapacitorTransmitter,
 effectShipModuleAncillaryRemoteArmorRepairer,
 effectShipModuleAncillaryRemoteShieldBooster,
 effectNpcEntityRemoteHullRepairer,
 effectNpcEntityRemoteArmorRepairer,
 effectNpcEntityRemoteShieldBooster,
 effectNpcBehaviorRemoteArmorRepairer,
 effectNpcBehaviorRemoteCapacitorTransmitter,
 effectNpcBehaviorRemoteShieldBooster]
dgmAttributesByIdx = {1: attributeIsOnline,
 2: attributeDamage,
 3: attributeCharge,
 4: attributeSkillPoints,
 5: attributeArmorDamage,
 6: attributeShieldCharge,
 7: attributeIsIncapacitated}
dgmGroupableGroupIDs = {inventorycommon.const.groupEnergyWeapon,
 inventorycommon.const.groupProjectileWeapon,
 inventorycommon.const.groupHybridWeapon,
 inventorycommon.const.groupMissileLauncher,
 inventorycommon.const.groupMissileLauncherAssault,
 inventorycommon.const.groupMissileLauncherXLTorpedo,
 inventorycommon.const.groupMissileLauncherXLCruise,
 inventorycommon.const.groupMissileLauncherRapidTorpedo,
 inventorycommon.const.groupMissileLauncherCruise,
 inventorycommon.const.groupMissileLauncherDefender,
 inventorycommon.const.groupMissileLauncherHeavy,
 inventorycommon.const.groupMissileLauncherHeavyAssault,
 inventorycommon.const.groupMissileLauncherRocket,
 inventorycommon.const.groupMissileLauncherSiege,
 inventorycommon.const.groupMissileLauncherStandard,
 inventorycommon.const.groupMissileLauncherRapidHeavy,
 inventorycommon.const.groupStructureAreaMissileLauncher,
 inventorycommon.const.groupStructureFlakMissileLauncher,
 inventorycommon.const.groupStructureMissileLauncher}
damageTypeAttributes = [attributeEmDamage,
 attributeThermalDamage,
 attributeKineticDamage,
 attributeExplosiveDamage]
hullDamageTypeResonanceAttributes = [attributeHullEmDamageResonance,
 attributeHullThermalDamageResonance,
 attributeHullKineticDamageResonance,
 attributeHullExplosiveDamageResonance]
shieldDamageTypeResonanceAttributes = [attributeShieldEmDamageResonance,
 attributeShieldThermalDamageResonance,
 attributeShieldKineticDamageResonance,
 attributeShieldExplosiveDamageResonance]
passiveShieldDamageTypeResonanceAttributes = [attributePassiveShieldEmDamageResonance,
 attributePassiveShieldThermalDamageResonance,
 attributePassiveShieldKineticDamageResonance,
 attributePassiveShieldExplosiveDamageResonance]
armorDamageTypeResonanceAttributes = [attributeArmorEmDamageResonance,
 attributeArmorThermalDamageResonance,
 attributeArmorKineticDamageResonance,
 attributeArmorExplosiveDamageResonance]
passiveArmorDamageTypeResonanceAttributes = [attributePassiveArmorEmDamageResonance,
 attributePassiveArmorThermalDamageResonance,
 attributePassiveArmorKineticDamageResonance,
 attributePassiveArmorExplosiveDamageResonance]
sensorStrengthPercentAttrs = [attributeScanRadarStrengthBonus,
 attributeScanMagnetometricStrengthBonus,
 attributeScanGravimetricStrengthBonus,
 attributeScanLadarStrengthBonus]
sensorStrengthBonusAttrs = [attributeScanRadarStrengthPercent,
 attributeScanMagnetometricStrengthPercent,
 attributeScanGravimetricStrengthPercent,
 attributeScanLadarStrengthPercent]
sensorStrength = [attributeScanRadarStrength,
 attributeScanMagnetometricStrength,
 attributeScanGravimetricStrength,
 attributeScanLadarStrength]
dungeonSensorStrengthTypes = {attributeScanAllStrength: 'All',
 attributeScanRadarStrength: 'Radar',
 attributeScanLadarStrength: 'Ladar',
 attributeScanGravimetricStrength: 'Gravimetric',
 attributeScanMagnetometricStrength: 'Magnetometric',
 attributeScanWormholeStrength: 'Wormhole'}
signatureTypes = {attributeScanAllStrength: 'Combat Site',
 attributeScanRadarStrength: 'Data Site',
 attributeScanLadarStrength: 'Gas Site',
 attributeScanGravimetricStrength: 'Ore Site',
 attributeScanMagnetometricStrength: 'Relic Site',
 attributeScanWormholeStrength: 'Wormhole'}
damageResistanceBonuses = [attributeEmDamageResistanceBonus,
 attributeThermalDamageResistanceBonus,
 attributeKineticDamageResistanceBonus,
 attributeExplosiveDamageResistanceBonus]
basicAttributes = [attributeRadius,
 attributeMass,
 attributeVolume,
 attributeCapacity,
 attributeRaceID,
 attributePublished]
heatAttributes = [attributeHeatHi, attributeHeatMed, attributeHeatLow]
falloffEffectivnessModuleGroups = [inventorycommon.const.groupEnergyDestabilizer,
 inventorycommon.const.groupEnergyVampire,
 inventorycommon.const.groupEnergyTransferArray,
 inventorycommon.const.groupArmorRepairProjector,
 inventorycommon.const.groupShieldTransporter,
 inventorycommon.const.groupRemoteHullRepairer,
 inventorycommon.const.groupRemoteSensorDamper,
 inventorycommon.const.groupElectronicCounterMeasures,
 inventorycommon.const.groupRemoteSensorBooster,
 inventorycommon.const.groupTrackingLink,
 inventorycommon.const.groupStasisGrappler,
 inventorycommon.const.groupTargetPainter,
 inventorycommon.const.groupTrackingDisruptor,
 inventorycommon.const.groupFueledRemoteShieldBooster]
singlePointTargetedEffects = [effectDebuffLance,
 effectDoomsdayBeamDOT,
 effectDoomsdayConeDOT,
 effectDoomsdayHOG,
 effectDoomsdayAOEBubble,
 effectDoomsdayAOEDamp,
 effectDoomsdayAOEECM,
 effectDoomsdayAOENeut,
 effectDoomsdayAOEPaint,
 effectDoomsdayAOETrack,
 effectDoomsdayAOEWeb]
unitAbsolutePercent = 127
unitAttributeID = 119
unitAttributePoints = 120
unitDatetime = 143
unitGroupID = 115
unitHour = 129
unitInverseAbsolutePercent = 108
unitInversedModifierPercent = 111
unitLength = 1
unitMass = 2
unitMilliseconds = 101
unitModifierPercent = 109
unitModifierRealPercent = 205
unitMoney = 133
unitSizeclass = 117
unitTime = 3
unitTypeID = 116
unitVolume = 9
unitCapacitorUnits = 114
unitSlot = 136
unitBoolean = 137
unitUnits = 138
unitBonus = 139
unitLevel = 140
unitHardpoints = 141
unitGender = 142
unitHitpoints = 113
unitMaxVelocity = 11
unitModifierRelativePercent = 124
unitPercentage = 105
unitTeraflops = 106
unitMegaWatts = 107
unitModifierMultiplier = 104
unitWarpSpeed = 144
attributeDataTypeInstanceBoolean = 0
attributeDataTypeInstanceInteger = 1
attributeDataTypeInstanceFloat = 2
attributeDataTypeTypeBoolean = 3
attributeDataTypeTypeInteger = 4
attributeDataTypeTypeFloat = 5
attributeDataTypeInstanceFloatCharge = 6
attributeDataTypeTypeHex = 7
attributeDataTypeTypeDamage = 8
attributeDataTypeTypeMirror = 9
attributeDataTypeTypeAttributeId = 10
attributeDataTypeTypeTypeId = 11
attributeDataTypeTypeGroupId = 12
attributeDataTypeTypeTypeListId = 13
attributeDataTypes = {attributeDataTypeInstanceBoolean: 'instance-boolean',
 attributeDataTypeInstanceInteger: 'instance-integer',
 attributeDataTypeInstanceFloat: 'instance-float',
 attributeDataTypeTypeBoolean: 'type-boolean',
 attributeDataTypeTypeInteger: 'type-integer',
 attributeDataTypeTypeFloat: 'type-float',
 attributeDataTypeInstanceFloatCharge: 'instance-float-charge',
 attributeDataTypeTypeHex: 'type-hex',
 attributeDataTypeTypeDamage: 'type-damage',
 attributeDataTypeTypeMirror: 'type-mirror',
 attributeDataTypeTypeAttributeId: 'type-attribute-id',
 attributeDataTypeTypeTypeId: 'type-type-id',
 attributeDataTypeTypeGroupId: 'type-group-id',
 attributeDataTypeTypeTypeListId: 'type-typelist-id'}
attributeDataTypesInstance = (attributeDataTypeInstanceBoolean,
 attributeDataTypeInstanceInteger,
 attributeDataTypeInstanceFloat,
 attributeDataTypeInstanceFloatCharge)
PREFITTED_MODULE_ATTRIBUTEID_BY_FLAGID = {inventorycommon.const.flagServiceSlot0: attributePreFitServiceSlot0,
 inventorycommon.const.flagStructureDeed: attributePreFitStructureCore}
