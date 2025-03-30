#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\crimewatch\const.py
from carbon.common.lib.const import SEC, MIN
import inventorycommon
weaponsTimerStateIdle = 100
weaponsTimerStateActive = 101
weaponsTimerStateTimer = 102
weaponsTimerStateInherited = 103
pvpTimerStateIdle = 200
pvpTimerStateActive = 201
pvpTimerStateTimer = 202
pvpTimerStateInherited = 203
criminalTimerStateIdle = 300
criminalTimerStateActiveCriminal = 301
criminalTimerStateActiveSuspect = 302
criminalTimerStateTimerCriminal = 303
criminalTimerStateTimerSuspect = 304
criminalTimerStateInheritedCriminal = 305
criminalTimerStateInheritedSuspect = 306
npcTimerStateIdle = 400
npcTimerStateActive = 401
npcTimerStateTimer = 402
npcTimerStateInherited = 403
disapprovalTimerStateIdle = 500
disapprovalTimerStateActive = 501
disapprovalTimerStateTimer = 502
disapprovalTimerStateInherited = 503
weaponsTimerTimeout = 60 * SEC
pvpTimerTimeout = 15 * MIN
criminalTimerTimeout = 15 * MIN
npcTimerTimeout = 5 * MIN
boosterTimerTimeout = 30 * MIN
disapprovalTimerTimeout = 5 * MIN
crimewatchEngagementTimeoutOngoing = -1
crimewatchEngagementDuration = 5 * MIN
shipSafetyLevelNone = 0
shipSafetyLevelPartial = 1
shipSafetyLevelFull = 2
illegalTargetNpcOwnedGroups = {inventorycommon.const.groupStation, inventorycommon.const.groupStargate}
crimewatchOutcomeNone = 0
crimewatchOutcomeSuspect = 1
crimewatchOutcomeCriminal = 2
crimewatchOutcomeEngagement = 3
crimewatchOutcomeDisapproval = 4
duelOfferExpiryTimeout = 30 * SEC
autoRejectDuelSettingsKey = 'autoRejectDuelInvitations'
securityLevelsPerTagType = {inventorycommon.const.typeSecurityTagCloneSoldierNegotiator: (-2.0, 0.0),
 inventorycommon.const.typeSecurityTagCloneSoldierTransporter: (-5.0, -2.0),
 inventorycommon.const.typeSecurityTagCloneSoldierRecruiter: (-8.0, -5.0),
 inventorycommon.const.typeSecurityTagCloneSoldierTrainer: (-10.0, -8.0)}
securityGainPerTag = 0.5
characterSecurityStatusMax = 10.0
characterSecurityStatusMin = -10.0
groupsSkipCriminalFlags = [inventorycommon.const.groupGangCoordinator, inventorycommon.const.groupSiegeModule]
groupsSkipDisapprovalFlags = groupsSkipCriminalFlags
targetGroupsWithNoSecurityPenalty = targetGroupsWithSuspectPenaltyInHighSec = (inventorycommon.const.groupMobileHomes,
 inventorycommon.const.groupCynoInhibitor,
 inventorycommon.const.groupAutoLooter,
 inventorycommon.const.groupMobileScanInhibitor,
 inventorycommon.const.groupMobileMicroJumpUnit,
 inventorycommon.const.groupOrbitalConstructionPlatforms)
targetGroupsWithNoPenalties = (inventorycommon.const.groupSiphonPseudoSilo,)
containerGroupsWithLootRights = (inventorycommon.const.groupWreck,
 inventorycommon.const.groupCargoContainer,
 inventorycommon.const.groupFreightContainer,
 inventorycommon.const.groupSpewContainer)
