#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\talecommon\const.py
import collections
from eve.common.lib import appConst
from brennivin.itertoolsext import Bundle
from dogma.const import attributeScanGravimetricStrength
from eve.common.lib.appConst import securityClassHighSec
from eve.common.lib.appConst import securityClassLowSec
from eve.common.lib.appConst import securityClassZeroSec
from grouprewards import REWARD_TYPE_LP
from inventorycommon.const import ownerUnknown, groupSun
templateClass = Bundle(incursion=2, knownSpace=3, solarSystem=4, spreadingIncursion=5, onionLayer=6, invasion=7, roamingWeather=8, worldEvents=9)
template = Bundle(guristasFOB=63, bloodRaidersFOB=64)
actionClass = Bundle(spawnOneDungeonAtEachCelestial=1, spawnManyDungeonsAtLocation=2, disableDjinns=3, addDjinnCommand=4, addSystemEffectBeacon=5, addStartSceneAtSceneInfluenceTrigger=6, initializeInfluence=7, setBountySurcharge=8, endTale=9, spawnDungeonAtDeterministicLocation=10, spawnNPCsAtLocation=11, addPeriodicInfluenceTrigger=12, grantTaleReward=13, clearTaleReward=14, periodicStartScene=15, setBlackboardFlag=16, endScene=17, setBlackboardFlagOnSceneRemoved=18, spawnPersistedNpcStructure=19, registerAgencyContent=20, replaceSystemEffectBeacon=21, setInfluence=22, removeDistribution=23, addSystemEnvironment=24, replaceSystemEnvironment=25, scheduleBranchingTale=26, decreaseConcordResponseLevel=27, dropConcordResponseLevel=28, setSlimItemIntegerField=29, scheduleRoamingDistribution=30)
conditionClass = Bundle(checkSolarSystemSecurity=1, checkInitiationChance=2, checkWorldLocation=3, checkInfluence=4, checkSolarSystemSpawnlistProbability=5, checkBlackboardFlag=6, checkSceneTypePresence=7, checkSolarSystemFacWarOccupier=8)
systemInfluenceAny = 0
systemInfluenceDecline = 1
systemInfluenceRising = 2
Parameter = collections.namedtuple('Parameter', 'name parameterType defaultValue prettyName description')
parameterByID = {1: Parameter('dungeonID', int, 0, 'Dungeon ID', 'The ID of the selected dungeon'),
 2: Parameter('dungeonListID', int, None, 'Dungeon list ID', 'The ID of the selected list of dungeons'),
 3: Parameter('dungeonRespawnTime', int, 1, 'Dungeon respawn time', 'Dungeon respawn time in minutes'),
 4: Parameter('dungeonScanStrength', int, 100, 'Dungeon scan strength', 'Dungeon scan strength for scanning down the dungeon'),
 5: Parameter('dungeonSignatureRadius', float, 100.0, 'Dungeon signature radius', 'Dungeon signature radius used for scanning down the dungeon'),
 6: Parameter('dungeonScanStrengthAttrib', float, attributeScanGravimetricStrength, 'Dungeon scan attribute', 'Dungeon scan attribute'),
 7: Parameter('dungeonSpawnLocation', float, None, 'Dungeon spawn location', 'The locations in space where the dungeon is going to respawn'),
 8: Parameter('dungeonSpawnQuantity', int, 1, 'Number of Dungeons', 'The number of dungeons which have to be spawned'),
 9: Parameter('triggeredScene', int, None, 'Triggered Scene', 'The scene which is added to the trigger location when activated'),
 10: Parameter('triggeredSceneLocation', int, None, 'Trigger Location', 'The location the triggered scene is added when the trigger is activated'),
 15: Parameter('disableConvoyDjinn', bool, False, 'Disable convoy djinn', 'Disables the convoy djinn during the tale'),
 16: Parameter('disableCustomsPoliceDjinn', bool, False, 'Disable custom police djinn', 'Disables the custom police during the tale'),
 17: Parameter('disableEmpirePoliceDjinn', bool, False, 'Disable empire police djinn', 'Disables the empire police during the tale'),
 18: Parameter('disableMilitaryFactionDjinn', bool, False, 'Disable military faction djinn', 'Disables the military faction djinn during the tale'),
 19: Parameter('disablePirateDjinn', bool, False, 'Disable pirate djinn', 'Disables the pirate djinn during the tale'),
 20: Parameter('disablePirateAutoDjinn', bool, False, 'Disable pirate auto djinn', 'Disables the pirate auto djinn during the tale'),
 21: Parameter('disablePirateStargateDjinn', bool, False, 'Disable pirate stargate djinn', 'Disables the pirate Stargate djinn during the tale'),
 22: Parameter('directorCommandID', int, 0, 'Director Command ID', 'The Director Command ID in this is added to solar system the scene is running in'),
 23: Parameter('systemEffectBeaconTypeID', int, 0, 'System effect beacon type ID', 'The type ID of the systems effect beacon'),
 24: Parameter('systemEffectBeaconBlockCynosural', bool, False, 'System effect beacon blocks cyno', 'The system effect beacon will also block cynosural jump'),
 25: Parameter('systemInfluenceTriggerDirection', int, systemInfluenceAny, 'Trigger direction', 'What direction the influence should change before the trigger is triggered'),
 26: Parameter('systemInfluenceTriggerValue', float, 0.0, 'Trigger value', 'The value around which the trigger should be triggered'),
 27: Parameter('dummyParameter', float, 0.0, 'Dummy Parameter', 'This is a dummy parameter for actions that take no parameters'),
 28: Parameter('surchargeRate', float, 0.2, 'Surcharge Rate', 'This is the surcharge rate that will be applied to this system'),
 29: Parameter('ownerID', int, ownerUnknown, 'Owner ID', 'Specifies the owner for items deployed through the scene.'),
 30: Parameter('entityTypeID', int, 0, 'Entity TypeID', 'The typeID for NPC to spawn.'),
 31: Parameter('entityAmountMin', int, 1, 'Minimum Entity Spawn Amount', 'The minimum amount of NPCs that should spawn.'),
 32: Parameter('entityAmountMax', int, 1, 'Maximum Entity Spawn Amount', 'The maximum amount of NPCs that should spawn.'),
 44: Parameter('entityGroupId', int, 0, 'Entity Group ID', 'NPC Group ID used to spawn a group of picked NPCs. Overwrites entityTypeID if not None.'),
 45: Parameter('entitySpawnListId', int, 0, 'Entity Spawnlist ID', 'Spawnlist used for picking a single NPC group. Overwrites entityGroupId and entityTypeID if not None.'),
 33: Parameter('entityGroupRespawnTimer', int, 30, 'Group Respawn Timer', 'The time (in minutes) it will take for the whole group to respawn if killed.'),
 34: Parameter('entityReinforcementTypeList', int, 0, 'Reinforcement Spawnlist ID', 'The list of entity groups used for reinforcing the NPC spawn - see: gd/npc/classes&groups and gd/spawnlists.'),
 35: Parameter('entityReinforcementCooldownTimer', int, 0, 'Reinforcement Cooldown Timer', 'The time (in seconds) that can pass between the NPC group asking for reinforcements.'),
 41: Parameter('entityBehaviorTree', str, 'None', 'Behavior Tree Type', 'The type of behavior these NPCs will get spawned with'),
 51: Parameter('entityGroupBehaviorTree', str, 'None', 'Behavior Group Tree Type', 'The type of group behavior these NPCs will get spawned with'),
 42: Parameter('entityGlobalExplorationGroups', int, 0, 'Global Groups for Exploration', 'The list of groupIDs that the NPCs will travel to.'),
 43: Parameter('entityGlobalExplorationOverwrite', bool, False, 'Overwrite Global Exploration', 'Overwrites normal exploration groups, else it extends it.'),
 66: Parameter('entitySpawnTableId', int, 0, 'Entity SpawnTable ID', 'The Spawntable used for picking the NPCs to spawn.'),
 67: Parameter('entitySpawnTablePoints', int, 0, 'Entity SpawnTable Points', 'The Points used to spawn NPCS from the Spawntable.'),
 68: Parameter('hostileResponseThreshold', float, 11.0, 'Hostile Response Threshold', 'Used to overwrite hostile standing response threshold'),
 69: Parameter('friendlyResponseThreshold', float, 11.0, 'Friendly Response Threshold', 'Used to overwrite friendly standing response threshold'),
 11: Parameter('solarSystemSecurityMin', float, 1.0, 'Security minimum', 'The security level of the solar system has to be above this before the condition is true'),
 12: Parameter('solarSystemSecurityMax', float, 0.0, 'Security maximum', 'The security level of the solar system has to be below this before the condition is true'),
 13: Parameter('solarSystemSecurityMinInclusive', bool, True, 'Security minimum inclusive', 'This is whether the minimum should be inclusive or exclusive'),
 14: Parameter('solarSystemSecurityMaxInclusive', bool, False, 'Security maximum inclusive', 'This is whether the maximum should be inclusive or exclusive'),
 37: Parameter('initiateActionsChance', int, 1, 'Action Initiation Chance', 'Chance of initiating any condition/action after this condition.'),
 40: Parameter('invertCondition', bool, False, 'Invert Condition', 'Inverts the true/false result for the condition check; NOT.'),
 38: Parameter('worldLocationId', int, 0, 'World Location ID', 'The ID of a SolarSystem, Region or Constellation, used along with World Location Type.'),
 39: Parameter('worldLocationListId', int, 0, 'World Location List ID', 'The ID of a list containing a group of locations - overwrites base ID if specified.'),
 50: Parameter('influenceStatus', float, 0, 'Influence Status', 'Checks if influence has reached a certain value.'),
 99: Parameter('fwOccupierID', int, ownerUnknown, 'Occupier FactionID', 'Checks if the solar system is occupied by a specific faction'),
 46: Parameter('influencePeriodicTriggerIntervalMinutes', int, 60, 'Periodic Interval', 'Number of minutes between the trigger firing'),
 47: Parameter('influencePeriodicTriggerInfluenceMin', int, 0.0, 'Min Trigger Influence', 'The minimum influence (inclusive) for trigger firing (two decimals)'),
 48: Parameter('influencePeriodicTriggerInfluenceMax', int, 1.0, 'Max Trigger Influence', 'The maximum influence (inclusive) for trigger firing (two decimals)'),
 49: Parameter('influencePeriodicTriggerActionId', int, 0, 'The action to trigger', 'The action to take when the trigger fires succesfully'),
 52: Parameter('solarSystemSpawnListId', int, 0, 'Solar System Spawnlist ID', 'Spawnlist of solarsystem ids with probabilites used to determine the probability in a particular system.'),
 53: Parameter('endSceneOnGroupDestroyed', bool, False, 'End Scene If Group Destroyed', 'Enable if the scene should be removed when the entity group is destroyed.'),
 54: Parameter('sceneTypeToStart', int, 0, 'Scene Type to start at location', 'The Scene Type to start at the location where the action is active.'),
 55: Parameter('periodMinutesMin', int, 60, 'Min length of period in minutes', 'Minimum period time in minites between reactivations'),
 56: Parameter('periodMinutesMax', int, 60, 'Max length of period in minutes', 'Maximum period time in minites between reactivations'),
 57: Parameter('blackboardMessageName', str, 'FLAG', 'Blackboard Message Name', 'Set a blackboard message to a boolean value'),
 58: Parameter('blackboardFlagValue', bool, True, 'Boolean Flag Value', 'Boolean value to set blackboard message to'),
 59: Parameter('sceneTypeToEnd', int, 0, 'Scene Type to end at location', 'The Scene Type to end at the location where the action is active.'),
 60: Parameter('persistedTypeID', int, 0, 'Persisted TypeID', 'TypeID for a persisted space object.'),
 61: Parameter('persistedObjectName', str, 'None', 'Persisted Object Name (DEPRICATED)', 'This is no longer used as the name is generated from type or type and owner if the this is a diamond NPC name.'),
 62: Parameter('endTaleOnItemDestroyed', bool, False, 'End Tale If Item Destroyed', 'Enable if the tale should end when the item is destroyed.'),
 63: Parameter('additionalLootTableID', int, 0, 'Additional Loot Table', 'Loot Table ID used to define additional loot for NPC/Structure'),
 64: Parameter('reinforceCycles', int, 2, 'Nr of Reinforce Cycles', 'Amount of reinforce cycles the spawned structure should have, default&max=2='),
 65: Parameter('isScannable', bool, False, 'Is Structure Scannable', 'If structre is not scannable it will be blocked from appearing in any scan result'),
 70: Parameter('enemyOwnerId', int, 0, 'Enemy Owner', 'The enemy owner for an agency content piece'),
 71: Parameter('titleTextId', int, 0, 'Title Text', 'The content title for agency card'),
 72: Parameter('subtitleTextId', int, 0, 'Subtitle Text', 'The content subtitle for agency card'),
 73: Parameter('expandedTitleTextId', int, 0, 'Expanded Title Text', 'The title for agency card expanded'),
 74: Parameter('expandedSubtitleTextId', int, 0, 'Expanded Subtitle Text', 'The subtitle text for agency expanded'),
 75: Parameter('blurbTextId', int, 0, 'Blurb Text', 'The bottom blurb text for expanded agency card'),
 76: Parameter('contentType', int, 0, 'Agency Content Type', 'The Content Type used by Agency to determine layout and organization'),
 77: Parameter('agencyRewards', list, [], 'Expected Content Rewards', 'The expected rewards for the piece of content'),
 78: Parameter('visibilityMaxRange', int, 5, 'Visibility max number of jumps', 'The maximum number of jumps the content can be seen from'),
 79: Parameter('visibilityExpansionMinutesPerJump', int, 1440, 'Visibility Expansion Minutes Per Jump', 'The minutes from creation until we expand visibility range'),
 80: Parameter('visibilityExpansionExponent', float, 1.0, 'Visibility Expansion Exponent', 'The exponent on jumps to tune how quickly visibility horizon expands. minutes = pow(jumps, exp) * min_per_jump'),
 81: Parameter('replaceSystemEffectBeaconRemoveTypeID', int, 0, 'TypeID to remove (0 to remove all)', 'Remove previously added beacons of this type'),
 82: Parameter('replaceSystemEffectBeaconAddTypeID', int, 0, 'TypeID to add', 'Add an effect beacon of this type'),
 83: Parameter('influenceLevelToSet', int, 0, 'Influence level to set', 'The level at which to set the influence'),
 84: Parameter('systemEnvironmentTypeID', int, 0, 'System environment type ID', 'The type ID of the systems environment'),
 85: Parameter('replaceSystemEnvironmentRemoveTypeID', int, 0, 'TypeID to remove (0 to remove all)', 'Remove previously added environments of this type'),
 86: Parameter('replaceSystemEnvironmentAddTypeID', int, 0, 'TypeID to add', 'Add an environment of this type'),
 87: Parameter('minPlacementDistance', float, 0.2, 'Minimum placement distance (centi-AU)', 'The minimum distance from the spawn location at which this dungeon should spawn in centi-AU'),
 88: Parameter('maxPlacementDistance', float, 0.2, 'Minimum placement distance (centi-AU)', 'The maximum distance from the spawn location at which this dungeon should spawn in centi-AU'),
 89: Parameter('templateID', int, 0, 'Template ID', 'The ID of the selected tale template'),
 90: Parameter('neighborSelectionChance', float, 0.0, 'Percentage of neighbors', 'The percentage chance for each of the parent tales neighboring solar systems to be selected for the tale spawn, unless "Spawn In Current System" is checked in which case that system is chosen if and only if it is in the list.'),
 91: Parameter('spawnInCurrentSystem', bool, False, 'Spawn In Current System', 'If checked, will spawn the tale in the system that is running the triggering scene, unless it is not in the specified distribution list, in which case the tale does not spawn in the current system, but we will attempt to spawn in neighboring systems anyway if authored to do so.'),
 92: Parameter('securityClass', int, securityClassHighSec, 'Security Class', 'The security class'),
 93: Parameter('slimItemFieldName', str, '', 'Slim Item Field Name', 'The name of the slim item field'),
 94: Parameter('slimItemFieldIntegerValue', int, '', 'Slim Item Integer Value', 'The integer value to which to set the slim item field'),
 95: Parameter('celestialGroup', int, groupSun, 'Celestial Group', 'The kind of celestials we should update'),
 96: Parameter('randomSeed', int, 0, 'Random Seed', 'Used along with solarSystemID to deterministically decide where to place the dungeon. When left at 0 will default to the "Scene Row ID", which can be seen here on the left.'),
 97: Parameter('sceneType', int, 0, 'Scene Type', 'Scene Type to match.'),
 98: Parameter('isDungeonScannable', bool, True, 'Scannable', 'Determines if a dungeon will show up on scanners ')}
parameter = Bundle()
for _parameterID, _parameterLine in parameterByID.iteritems():
    setattr(parameter, _parameterLine.name, _parameterID)

sceneTypeMinConditional = 1000001
sceneTypeMinSystem = 5000001
scenesTypes = Bundle()
conditionalScenesTypes = Bundle()
sceneTypesByID = {1: Bundle(name='headquarters', display='Headquarters'),
 2: Bundle(name='assault', display='Assault'),
 3: Bundle(name='vanguard', display='Vanguard'),
 4: Bundle(name='staging', display='Staging'),
 5: Bundle(name='testscene', display='Test Scene'),
 6: Bundle(name='system', display='Solar System'),
 7: Bundle(name='incursionNeutral', display='Incursion Neutral'),
 8: Bundle(name='incursionStaging', display='Incursion Staging'),
 9: Bundle(name='incursionLightInfestation', display='Incursion Light Infestation'),
 10: Bundle(name='incursionMediumInfestation', display='Incursion Medium Infestation'),
 11: Bundle(name='incursionHeavyInfestation', display='Incursion Heavy Infestation'),
 12: Bundle(name='incursionFinalEncounter', display='Incursion Final Encounter'),
 13: Bundle(name='incursionEndTale', display='Incursion End Tale'),
 100: Bundle(name='onionHeadquarters', display='Central System (Manager)'),
 101: Bundle(name='onionJump1', display='Systems 1 Jump Away'),
 102: Bundle(name='onionJump2', display='Systems 2 Jump Away'),
 103: Bundle(name='onionJump3', display='Systems 3 Jump Away'),
 104: Bundle(name='onionJump4', display='Systems 4 Jump Away'),
 105: Bundle(name='onionJump5', display='Systems 5 Jump Away'),
 106: Bundle(name='onionJump6', display='Systems 6 Jump Away'),
 107: Bundle(name='onionJump7', display='Systems 7 Jump Away'),
 108: Bundle(name='onionJump8', display='Systems 8 Jump Away'),
 109: Bundle(name='onionJump9', display='Systems 9 Jump Away'),
 110: Bundle(name='onionJump10', display='Systems 10 Jump Away'),
 1000001: Bundle(name='boss', display='Boss Spawn'),
 1000002: Bundle(name='endTale', display='End Tale'),
 1000003: Bundle(name='conditionalScene1', display='Conditional Scene 1'),
 1000004: Bundle(name='conditionalScene2', display='Conditional Scene 2'),
 1000005: Bundle(name='conditionalScene3', display='Conditional Scene 3'),
 1000011: Bundle(name='conditionalScene11', display='Conditional Scene 11'),
 1000012: Bundle(name='conditionalScene12', display='Conditional Scene 12'),
 1000013: Bundle(name='conditionalScene13', display='Conditional Scene 13'),
 1000014: Bundle(name='conditionalScene14', display='Conditional Scene 14'),
 1000015: Bundle(name='conditionalScene15', display='Conditional Scene 15'),
 1000016: Bundle(name='conditionalScene16', display='Conditional Scene 16'),
 1000017: Bundle(name='conditionalScene17', display='Conditional Scene 17'),
 1000018: Bundle(name='conditionalScene18', display='Conditional Scene 18'),
 1000019: Bundle(name='conditionalScene19', display='Conditional Scene 19'),
 1000020: Bundle(name='conditionalScene20', display='Conditional Scene 20'),
 1000021: Bundle(name='conditionalScene21', display='Conditional Scene 21'),
 1000022: Bundle(name='conditionalScene22', display='Conditional Scene 22'),
 1000023: Bundle(name='conditionalScene23', display='Conditional Scene 23'),
 1000024: Bundle(name='conditionalScene24', display='Conditional Scene 24'),
 1000025: Bundle(name='conditionalScene25', display='Conditional Scene 25'),
 2000001: Bundle(name='testscene1', display='Conditional Test Scene 1'),
 2000002: Bundle(name='testscene2', display='Conditional Test Scene 2'),
 2000003: Bundle(name='testscene3', display='Conditional Test Scene 3'),
 2000004: Bundle(name='testscene4', display='Conditional Test Scene 4'),
 2000005: Bundle(name='testscene5', display='Conditional Test Scene 5'),
 5000001: Bundle(name='managerInit', display='Initialize Manager ')}
for _constID, _constNames in sceneTypesByID.iteritems():
    setattr(scenesTypes, _constNames.name, _constID)

distributionStatus = Bundle(success=1, locationAlreadyUsed=2, failedRequirementFromTemplate=3, exception=4, hardKilled=5)
securityClassToParameterString = {securityClassZeroSec: 'DistributeNullSec',
 securityClassLowSec: 'DistributeLowSec',
 securityClassHighSec: 'DistributeHighSec'}
KNOWN_SPACE_RANDOM_SEED = 42
BLACKLIST_GENERIC = 1
BLACKLIST_INCURSIONS = 3
BLACKLIST_SLEEPER_SCOUTS = 4
INCURSION_TEMPLATE_CLASSES = (templateClass.incursion, templateClass.spreadingIncursion)
INVASION_TEMPLATE_CLASSES = (templateClass.invasion,)
FOB_TEMPLATES = (template.guristasFOB, template.bloodRaidersFOB)
INCURSION_DISTRIBUTIONS_STRING = '%d,%d' % INCURSION_TEMPLATE_CLASSES
INCURSION_STAGING_SCENE_TYPES_STRING = '%d,%d' % (scenesTypes.staging, scenesTypes.incursionStaging)
TALE_VISUAL_OVERLAYS = {1: 'INCURSION_OVERLAY'}
TALE_REWARD_ADJUSTMENTS = {'finalRewardAdjustmentType': REWARD_TYPE_LP,
 'finalRewardMaxAdjustment': 0.2,
 'finalRewardAdjustmentStep': 0.02}
FINAL_INVASION_DISTRIBUTION = 71
INVASION_DISTRIBUTION_STAGE_ONE = 72
INVASION_DISTRIBUTION_STAGE_TWO = 73
INVASION_DISTRIBUTION_STAGE_THREE = 74
INVASION_DISTRIBUTION_STAGE_FOUR = 75
INVASION_DISTRIBUTION_LOWSEC = 86
INVASION_DISTRIBUTION_DREADNOUGHT_PHASE_HISEC = 88
INVASION_DISTRIBUTION_DREADNOUGHT_PHASE_LOWSEC = 89
INVASION_CHAPTER_THREE_SCOUTS_AND_PATROLS = 99
INVASION_CHAPTER_THREE_TRIGLAVIAN_ESTABLISHMENT = 100
INVASION_CHAPTER_THREE_EMPIRE_FORTIFICATION = 101
INVASION_CHAPTER_THREE_TRIGLAVIAN_VICTORY = 102
INVASION_CHAPTER_THREE_EMPIRE_VICTORY = 103
INVASION_CHAPTER_THREE_TRIGLAVIAN_MINOR_VICTORY = 105
INVASION_CHAPTER_THREE_EDENCOM_MINOR_VICTORY = 106
INVASION_CHAPTER_THREE_MASSIVE_EDENCOM_FORTIFICATION = 110
INVASION_CHAPTER_THREE_MASSIVE_TRIGLAVIAN_INVASION = 111
INVASION_CHAPTER_THREE_EVERGREEN_TRIGLAVIAN_MINOR_VICTORY = 120
INVASION_CHAPTER_THREE_EVERGREEN_EDENCOM_MINOR_VICTORY = 121
INVASION_CHAPTER_THREE_EVERGREEN_EDENCOM_FORTRESS = 122
INVASION_TRIGLAVIAN_CONQUERED_TALES = (INVASION_CHAPTER_THREE_TRIGLAVIAN_VICTORY, INVASION_CHAPTER_THREE_MASSIVE_TRIGLAVIAN_INVASION)
INVASION_CHAPTER_THREE_TALES = [INVASION_CHAPTER_THREE_SCOUTS_AND_PATROLS,
 INVASION_CHAPTER_THREE_TRIGLAVIAN_ESTABLISHMENT,
 INVASION_CHAPTER_THREE_EMPIRE_FORTIFICATION,
 INVASION_CHAPTER_THREE_TRIGLAVIAN_VICTORY,
 INVASION_CHAPTER_THREE_EMPIRE_VICTORY,
 INVASION_CHAPTER_THREE_TRIGLAVIAN_MINOR_VICTORY,
 INVASION_CHAPTER_THREE_EDENCOM_MINOR_VICTORY,
 INVASION_CHAPTER_THREE_MASSIVE_EDENCOM_FORTIFICATION,
 INVASION_CHAPTER_THREE_MASSIVE_TRIGLAVIAN_INVASION]
TEMPLATE_NAME_ID_SCOUTS_AND_PATROLS = 564035
TEMPLATE_NAME_ID_TRIGLAVIAN_ESTABLISHMENT = 564036
TEMPLATE_NAME_ID_EMPIRE_FORTIFICATION = 564037
TEMPLATE_NAME_ID_TRIGLAVIAN_VICTORY = 564038
TEMPLATE_NAME_ID_EMPIRE_VICTORY = 564039
INVASION_CHAPTER_THREE_TALE_TEMPLATE_NAMES = (TEMPLATE_NAME_ID_SCOUTS_AND_PATROLS,
 TEMPLATE_NAME_ID_TRIGLAVIAN_ESTABLISHMENT,
 TEMPLATE_NAME_ID_EMPIRE_FORTIFICATION,
 TEMPLATE_NAME_ID_TRIGLAVIAN_VICTORY,
 TEMPLATE_NAME_ID_EMPIRE_VICTORY)
INVASION_SECURITY_DROPPING_TALE_TEMPLATE_NAMES = (TEMPLATE_NAME_ID_TRIGLAVIAN_ESTABLISHMENT, TEMPLATE_NAME_ID_TRIGLAVIAN_VICTORY)
PRE_WORLD_ARK_STAGES = (INVASION_DISTRIBUTION_STAGE_ONE, INVASION_DISTRIBUTION_STAGE_TWO, INVASION_DISTRIBUTION_STAGE_THREE)
INVASION_DREADNOUGHT_PHASE_TALES = (INVASION_DISTRIBUTION_DREADNOUGHT_PHASE_HISEC, INVASION_DISTRIBUTION_DREADNOUGHT_PHASE_LOWSEC)
INVASION_DISTRIBUTIONS = (INVASION_DISTRIBUTION_STAGE_ONE,
 INVASION_DISTRIBUTION_STAGE_TWO,
 INVASION_DISTRIBUTION_STAGE_THREE,
 INVASION_DISTRIBUTION_STAGE_FOUR,
 FINAL_INVASION_DISTRIBUTION,
 INVASION_DISTRIBUTION_LOWSEC,
 INVASION_DISTRIBUTION_DREADNOUGHT_PHASE_HISEC,
 INVASION_DISTRIBUTION_DREADNOUGHT_PHASE_LOWSEC,
 INVASION_CHAPTER_THREE_SCOUTS_AND_PATROLS,
 INVASION_CHAPTER_THREE_TRIGLAVIAN_ESTABLISHMENT,
 INVASION_CHAPTER_THREE_EMPIRE_FORTIFICATION,
 INVASION_CHAPTER_THREE_TRIGLAVIAN_VICTORY,
 INVASION_CHAPTER_THREE_EMPIRE_VICTORY,
 INVASION_CHAPTER_THREE_TRIGLAVIAN_MINOR_VICTORY,
 INVASION_CHAPTER_THREE_EDENCOM_MINOR_VICTORY,
 INVASION_CHAPTER_THREE_MASSIVE_EDENCOM_FORTIFICATION,
 INVASION_CHAPTER_THREE_MASSIVE_TRIGLAVIAN_INVASION)
INVASION_EFFECTS = [{'name': 'effectIcon_agility_up',
  'texturePath': 'res:/UI/Texture/classes/InfluenceBar/increasedShipAgility.png',
  'hint': 'UI/Invasion/HUD/SystemEffectIncreasedAgilityHint',
  'isScalable': True},
 {'name': 'effectIcon_drone_damage_down',
  'texturePath': 'res:/UI/Texture/classes/InfluenceBar/reducedDroneDamage.png',
  'hint': 'UI/Invasion/HUD/SystemEffectDroneDamageReducedHint',
  'isScalable': True},
 {'name': 'effectIcon_drone_speed_down',
  'texturePath': 'res:/UI/Texture/classes/InfluenceBar/reducedDroneSpeed.png',
  'hint': 'UI/Invasion/HUD/SystemEffectDroneSpeedDecreasedHint',
  'isScalable': True},
 {'name': 'effectIcon_hull_hp_down',
  'texturePath': 'res:/UI/Texture/classes/InfluenceBar/reducedHullHP.png',
  'hint': 'UI/Invasion/HUD/SystemEffectReducedHullHPHint',
  'isScalable': True},
 {'name': 'effectIcon_mining_cycle_time_down',
  'texturePath': 'res:/UI/Texture/classes/InfluenceBar/reducedMiningCycleTime.png',
  'hint': 'UI/Invasion/HUD/SystemEffectReducedMiningCycleTimeHint',
  'isScalable': True}]
TALE_SYSTEM_MODIFIERS = {1: [{'name': 'effectIcon_cyno',
      'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectCyno.png',
      'hint': 'UI/Incursion/HUD/SystemEffectCynoHint',
      'isScalable': False},
     {'name': 'effectIcon_tax',
      'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectTax.png',
      'hint': 'UI/Incursion/HUD/SystemEffectTaxHint',
      'isScalable': False},
     {'name': 'effectIcon_tank',
      'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectResistanceDecrease.png',
      'hint': 'UI/Incursion/HUD/SystemEffectTankingHint',
      'isScalable': True},
     {'name': 'effectIcon_damage',
      'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectDamageDecrease.png',
      'hint': 'UI/Incursion/HUD/SystemEffectDamageHint',
      'isScalable': True}],
 36: [{'name': 'effectIcon_cyno',
       'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectCyno.png',
       'hint': 'UI/Incursion/HUD/SystemEffectCynoHint',
       'isScalable': False},
      {'name': 'effectIcon_damage',
       'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectDamageDecrease.png',
       'hint': 'UI/Incursion/HUD/SystemEffectDamageHint',
       'isScalable': True},
      {'name': 'effectIcon_armor',
       'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectResistanceDecrease.png',
       'hint': 'UI/Incursion/HUD/SystemEffectArmorHint',
       'isScalable': True},
      {'name': 'effectIcon_shield',
       'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectShieldDecrease.png',
       'hint': 'UI/Incursion/HUD/SystemEffectShieldHint',
       'isScalable': True},
      {'name': 'effectIcon_velocity',
       'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectVelocityDecrease.png',
       'hint': 'UI/Incursion/HUD/SystemEffectVelocityHint',
       'isScalable': True}],
 FINAL_INVASION_DISTRIBUTION: INVASION_EFFECTS,
 INVASION_DISTRIBUTION_STAGE_ONE: INVASION_EFFECTS,
 INVASION_DISTRIBUTION_STAGE_THREE: INVASION_EFFECTS,
 INVASION_DISTRIBUTION_STAGE_FOUR: INVASION_EFFECTS,
 INVASION_DISTRIBUTION_LOWSEC: INVASION_EFFECTS,
 INVASION_DISTRIBUTION_DREADNOUGHT_PHASE_HISEC: INVASION_EFFECTS,
 INVASION_DISTRIBUTION_DREADNOUGHT_PHASE_LOWSEC: INVASION_EFFECTS}
REWARD_SCOUT = 8
REWARD_VANGUARD = 1
REWARD_ASSAULT = 2
REWARD_HQ = 3
REWARD_BOSS = 10
REWARD_THRONE_WORLDS_LIGHT = 15
REWARD_THRONE_WORLDS_MEDIUM = 16
REWARD_THRONE_WORLDS_HEAVY = 17
VANGUARD_PENALTY = 10
ASSAULT_PENALTY = 25
HEADQUARTERS_PENALTY = 50
IncursionInfo = collections.namedtuple('IncursionInfo', ['rewardID',
 'severity',
 'name',
 'text'])
INCURSION_INFO_BY_DUNGEONID = {5191: IncursionInfo(rewardID=REWARD_SCOUT, severity='UI/Incursion/Distributions/SanshaIncursion/Scout', name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/One', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/OneText'),
 5193: IncursionInfo(rewardID=REWARD_SCOUT, severity='UI/Incursion/Distributions/SanshaIncursion/Scout', name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/Two', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/TwoText'),
 5188: IncursionInfo(rewardID=REWARD_SCOUT, severity='UI/Incursion/Distributions/SanshaIncursion/Scout', name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/Three', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/ThreeText'),
 5190: IncursionInfo(rewardID=REWARD_SCOUT, severity='UI/Incursion/Distributions/SanshaIncursion/Scout', name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/Four', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/FourText'),
 5165: IncursionInfo(rewardID=REWARD_VANGUARD, severity='UI/Incursion/Distributions/SanshaIncursion/Vanguard', name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/One', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/OneText'),
 5166: IncursionInfo(rewardID=REWARD_VANGUARD, severity='UI/Incursion/Distributions/SanshaIncursion/Vanguard', name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/Two', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/TwoText'),
 5164: IncursionInfo(rewardID=REWARD_VANGUARD, severity='UI/Incursion/Distributions/SanshaIncursion/Vanguard', name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/Three', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/ThreeText'),
 5167: IncursionInfo(rewardID=REWARD_ASSAULT, severity='UI/Incursion/Distributions/SanshaIncursion/Assault', name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/One', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/OneText'),
 5172: IncursionInfo(rewardID=REWARD_ASSAULT, severity='UI/Incursion/Distributions/SanshaIncursion/Assault', name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/Two', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/TwoText'),
 5168: IncursionInfo(rewardID=REWARD_ASSAULT, severity='UI/Incursion/Distributions/SanshaIncursion/Assault', name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/Three', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/ThreeText'),
 5114: IncursionInfo(rewardID=REWARD_HQ, severity='UI/Incursion/Distributions/SanshaIncursion/Headquarters', name='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/One', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/OneText'),
 5175: IncursionInfo(rewardID=REWARD_HQ, severity='UI/Incursion/Distributions/SanshaIncursion/Headquarters', name='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/Two', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/TwoText'),
 5171: IncursionInfo(rewardID=REWARD_HQ, severity='UI/Incursion/Distributions/SanshaIncursion/Headquarters', name='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/Three', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/ThreeText'),
 5158: IncursionInfo(rewardID=REWARD_BOSS, severity='UI/Incursion/Distributions/SanshaIncursion/Headquarters', name='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/Four', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/FourText'),
 5201: IncursionInfo(rewardID=REWARD_BOSS, severity='UI/Incursion/Distributions/SanshaIncursion/Headquarters', name='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/Five', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/FiveText'),
 5689: IncursionInfo(rewardID=REWARD_THRONE_WORLDS_LIGHT, severity='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/defensiveOutpost', name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrDefensiveOutpost', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrDefensiveOutpostText'),
 5690: IncursionInfo(rewardID=REWARD_THRONE_WORLDS_MEDIUM, severity='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/encampment', name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrEncampment', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrEncampmentText'),
 5691: IncursionInfo(rewardID=REWARD_THRONE_WORLDS_HEAVY, severity='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/battalion', name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrBattalion', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrBattalionText'),
 5692: IncursionInfo(rewardID=REWARD_THRONE_WORLDS_LIGHT, severity='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/moderateInflux', name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/ModerateDrifterInflux', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/ModerateDrifterInfluxText'),
 5693: IncursionInfo(rewardID=REWARD_THRONE_WORLDS_MEDIUM, severity='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/severeinflux', name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/SevereDrifterInflux', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/SevereDrifterInfluxText'),
 5694: IncursionInfo(rewardID=REWARD_THRONE_WORLDS_HEAVY, severity='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/criticalinflux', name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/CriticalDrifterInflux', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/CriticalDrifterInfluxText')}
TALE_DISTRIBUTION_BLACKLIST = 11
GROW_TALE_TRIGGER_ACTION = 1
SHRINK_TALE_TRIGGER_ACTION = 2
HIDDEN_SCENES = (scenesTypes.incursionNeutral,)
