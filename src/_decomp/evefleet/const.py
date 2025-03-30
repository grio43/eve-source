#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evefleet\const.py
fleetGroupingRange = 300
fleetJobCreator = 2
fleetJobNone = 0
fleetJobScout = 1
fleetLeaderRole = 1
fleetRoleLeader = 1
fleetRoleMember = 4
fleetRoleSquadCmdr = 3
fleetRoleWingCmdr = 2
fleetCmdrRoles = (fleetRoleLeader, fleetRoleWingCmdr, fleetRoleSquadCmdr)
rejectFleetInviteTimeout = 1
rejectFleetInviteAlreadyInFleet = 2
fleetRejectionReasons = {rejectFleetInviteTimeout: 'UI/Fleet/FleetServer/NoResponse',
 rejectFleetInviteAlreadyInFleet: 'UI/Fleet/FleetServer/AlreadyInFleet'}
FLEET_NONEID = -1
CHANNELSTATE_NONE = 0
CHANNELSTATE_LISTENING = 1
CHANNELSTATE_MAYSPEAK = 2
CHANNELSTATE_SPEAKING = 4
MIN_MEMBERS_IN_FLEET = 50
MAX_MEMBERS_IN_FLEET = 256
MAX_MEMBERS_IN_SQUAD = 256
MAX_SQUADS_IN_WING = 25
MAX_WINGS_IN_FLEET = 25
MAX_NAME_LENGTH = 10
MAX_DAMAGE_SENDERS = 100
BROADCAST_NONE = 0
BROADCAST_DOWN = 1
BROADCAST_UP = 2
BROADCAST_ALL = 3
BROADCAST_UNIVERSE = 0
BROADCAST_SYSTEM = 1
BROADCAST_BUBBLE = 2
INVITE_CLOSED = 0
INVITE_CORP = 1
INVITE_ALLIANCE = 2
INVITE_MILITIA = 4
INVITE_PUBLIC = 8
INVITE_PUBLIC_OPEN = 16
INVITE_ALL = 31
FLEETNAME_MAXLENGTH = 32
FLEETDESC_MAXLENGTH = 250
NODEID_MOD = 10000000
FLEETID_MOD = 10000
WINGID_MOD = 20000
SQUADID_MOD = 30000
BROADCAST_LOCATION = 'Location'
BROADCAST_JUMP_BEACON = 'JumpBeacon'
BROADCAST_HOLD_POSITION = 'HoldPosition'
BROADCAST_TRAVEL_TO = 'TravelTo'
BROADCAST_JUMP_TO = 'JumpTo'
BROADCAST_ALIGN_TO = 'AlignTo'
BROADCAST_NEED_BACKUP = 'NeedBackup'
BROADCAST_WARP_TO = 'WarpTo'
BROADCAST_HEAL_CAPACITOR = 'HealCapacitor'
BROADCAST_HEAL_SHIELD = 'HealShield'
BROADCAST_HEAL_ARMOR = 'HealArmor'
BROADCAST_TARGET = 'Target'
BROADCAST_ENEMY_SPOTTED = 'EnemySpotted'
BROADCAST_IN_POSITION = 'InPosition'
BROADCAST_SHOW_OWN = 'ShowOwnBroadcasts'
BROADCAST_REP_TARGET = 'HealTarget'
ALL_BROADCASTS = [BROADCAST_ENEMY_SPOTTED,
 BROADCAST_NEED_BACKUP,
 BROADCAST_HOLD_POSITION,
 BROADCAST_IN_POSITION,
 BROADCAST_TRAVEL_TO,
 BROADCAST_JUMP_BEACON,
 BROADCAST_LOCATION,
 BROADCAST_TARGET,
 BROADCAST_REP_TARGET,
 BROADCAST_HEAL_ARMOR,
 BROADCAST_HEAL_SHIELD,
 BROADCAST_HEAL_CAPACITOR,
 BROADCAST_WARP_TO,
 BROADCAST_ALIGN_TO,
 BROADCAST_JUMP_TO]
RECONNECT_TIMEOUT = 2
ACTIVITY_INCURSIONS = 1
ACTIVITY_FW = 2
ACTIVITY_PIRATE_STRONGHOLD = 3
ACTIVITY_ABYSS = 4
ACTIVITY_COMBAT_ANOMALIES = 5
ACTIVITY_ESCALATIONS = 6
ACTIVITY_MINING = 7
ACTIVITY_EXPLORATION = 8
ACTIVITY_FREE_ROAM = 9
ACTIVITY_PVP = 10
ACTIVITY_MISC = 11
ACTIVITY_MISSIONS = 12
ACTIVITY_ESS = 13
ACTIVITY_HOMEFRONT_OPERATIONS = 14
fleetActivityNames = {ACTIVITY_INCURSIONS: 'UI/Agency/ContentGroups/ContentGroupIncursions',
 ACTIVITY_FW: 'UI/Agency/ContentGroups/ContentGroupFactionalWarfare',
 ACTIVITY_PIRATE_STRONGHOLD: 'UI/Agency/ContentTypePirateStronghold',
 ACTIVITY_ABYSS: 'UI/Agency/ContentGroups/ContentGroupAbyssalDeadspace',
 ACTIVITY_COMBAT_ANOMALIES: 'UI/Agency/ContentGroups/ContentGroupCombatAnomalies',
 ACTIVITY_ESCALATIONS: 'UI/Agency/ContentGroups/ContentGroupEscalations',
 ACTIVITY_MINING: 'UI/Agency/ContentGroups/ContentGroupResourceHarvesting',
 ACTIVITY_EXPLORATION: 'UI/Agency/ContentGroups/ContentGroupExploration',
 ACTIVITY_FREE_ROAM: 'UI/Agency/Fleetup/FreeRoamOption',
 ACTIVITY_PVP: 'UI/Corporations/CorporationWindow/Recruitment/PVP',
 ACTIVITY_MISC: 'UI/Agency/Fleetup/MiscOption',
 ACTIVITY_MISSIONS: 'UI/Agency/Fleetup/MissionsEpicArcsOption',
 ACTIVITY_ESS: 'UI/Agency/ContentGroups/ContentGroupESS',
 ACTIVITY_HOMEFRONT_OPERATIONS: 'UI/Inflight/Scanner/HomefrontOperationSite'}
CREATE_SOURCE_FLEETUP = 1
CREATE_SOURCE_MENU = 2
CREATE_SOURCE_FLEET_FINDER_WND = 3
JOIN_SOURCE_FLEETUP = 1
JOIN_SOURCE_LINK = 2
JOIN_SOURCE_FLEET_FINDER_BTN = 3
JOIN_SOURCE_FLEET_FINDER_ENTRY = 4
REGISTER_BTN_ANALYTIC_ID = 'Fleetup_RegisterFleetCmdBtn'
UPDATE_BTN_ANALYTIC_ID = 'Fleetup_UpdateFleetCmdBtn'
CREATE_FLEET_ANALYTIC_ID = 'Fleetup_CreateFleet'
CREATE_FLEET_AND_REGISTER_AD_ANALYTIC_ID = 'Fleetup_CreateFleetAndRegisterAd'
REGISTER_AD_ANALYTIC_ID = 'Fleetup_RegisterAdThrough'
UPDATE_AD_BTN_ANALYTIC_ID = 'Fleetup_UpdateAd'
REQUEST_TO_JOIN_BTN_ANALYTIC_ID = 'Fleetup_RequestToJoinBtn'
CONFIRM_REQUEST_TO_JOIN_BTN_ANALYTIC_ID = 'Fleetup_ConfirmRequestToJoinBtn'
FORMATION_SKILL = 57317
FORMATION_DISTANCE_SKILL = 57318
RELATIVE_FORMATION_PICKUP_RANGE = 200000
MINIMUM_FORMATION_JITTER = 500
FLEET_FORMATION_SETTING = 'setFleetFormation'
FLEET_FORMATION_SPACING_SETTING = 'setFleetFormationSpacing'
FLEET_FORMATION_SIZE_SETTING = 'setFleetFormationSize'
POINT = 0
SPHERE = 1
PLANE = 2
WALL = 3
ARROW = 4
RELATIVE = 5
FLEET_FORMATIONS = [POINT,
 SPHERE,
 PLANE,
 WALL,
 ARROW,
 RELATIVE]
FORMATION_ICONS = {POINT: 'res:/UI/Texture/classes/Fleet/FleetFormations/pointFormation.png',
 SPHERE: 'res:/UI/Texture/classes/Fleet/FleetFormations/sphereFormation.png',
 PLANE: 'res:/UI/Texture/classes/Fleet/FleetFormations/planeFormation.png',
 WALL: 'res:/UI/Texture/classes/Fleet/FleetFormations/wallFormation.png',
 ARROW: 'res:/UI/Texture/classes/Fleet/FleetFormations/arrowFormation.png',
 RELATIVE: 'res:/UI/Texture/classes/Fleet/FleetFormations/relativeFormation.png'}
LOCALIZED_FORMATIONS = {POINT: 'UI/Fleet/FleetFormations/PointFormation',
 SPHERE: 'UI/Fleet/FleetFormations/SphereFormation',
 PLANE: 'UI/Fleet/FleetFormations/PlaneFormation',
 WALL: 'UI/Fleet/FleetFormations/WallFormation',
 ARROW: 'UI/Fleet/FleetFormations/ArrowFormation',
 RELATIVE: 'UI/Fleet/FleetFormations/RelativeFormation'}
LOCALIZED_FORMATIONS_SHORT = {POINT: 'UI/Fleet/FleetFormations/Point',
 SPHERE: 'UI/Fleet/FleetFormations/Sphere',
 PLANE: 'UI/Fleet/FleetFormations/Plane',
 WALL: 'UI/Fleet/FleetFormations/Wall',
 ARROW: 'UI/Fleet/FleetFormations/Arrow',
 RELATIVE: 'UI/Fleet/FleetFormations/Relative'}
LOCALIZED_FORMATION_DESCRIPTIONS = {POINT: 'UI/Fleet/FleetFormations/PointFormationDescription',
 SPHERE: 'UI/Fleet/FleetFormations/SphereFormationDescription',
 PLANE: 'UI/Fleet/FleetFormations/PlaneFormationDescription',
 WALL: 'UI/Fleet/FleetFormations/WallFormationDescription',
 ARROW: 'UI/Fleet/FleetFormations/ArrowFormationDescription',
 RELATIVE: 'UI/Fleet/FleetFormations/RelativeFormationDescription'}
FORMATION_USES_SPACING = [PLANE, WALL, ARROW]
FORMATION_USES_SIZE = [SPHERE,
 PLANE,
 WALL,
 ARROW]
FLEET_FORMATION_SPACING = [1000,
 2000,
 3000,
 4000,
 5000,
 10000]
FLEET_FORMATION_SIZE = [10000,
 20000,
 30000,
 40000,
 50000,
 100000]
FLEET_FORMATION_SPACING_SKILL_LEVEL_MAPPING = {FLEET_FORMATION_SPACING[0]: 0,
 FLEET_FORMATION_SPACING[1]: 1,
 FLEET_FORMATION_SPACING[2]: 2,
 FLEET_FORMATION_SPACING[3]: 3,
 FLEET_FORMATION_SPACING[4]: 4,
 FLEET_FORMATION_SPACING[5]: 5}
FLEET_FORMATION_SIZE_SKILL_LEVEL_MAPPING = {FLEET_FORMATION_SIZE[0]: 0,
 FLEET_FORMATION_SIZE[1]: 1,
 FLEET_FORMATION_SIZE[2]: 2,
 FLEET_FORMATION_SIZE[3]: 3,
 FLEET_FORMATION_SIZE[4]: 4,
 FLEET_FORMATION_SIZE[5]: 5}
