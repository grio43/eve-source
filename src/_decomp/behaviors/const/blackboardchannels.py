#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\const\blackboardchannels.py
from behaviors.blackboards.scopes import ScopeTypes
ENTITY_GROUP_IDS_BY_FLEET_TYPE_MESSAGE_CHANNEL = 'ENTITY_GROUP_IDS_BY_FLEET_TYPE'
GUARD_OBJECT_ITEM_ID_MESSAGE_CHANNEL = 'GUARD_OBJECT_ITEM_ID'
ROLE_MESSAGE_CHANNEL = 'ROLE'
SPAWN_POSITION_MESSAGE_CHANNEL = 'SPAWN_POSITION'
STANDINGS_FRIENDLY_THRESHOLD_CHANNEL_NAME = 'STANDINGS_FRIENDLY_THRESHOLD'
STANDINGS_HOSTILE_THRESHOLD_CHANNEL_NAME = 'STANDINGS_HOSTILE_THRESHOLD'
UNDOCK_DIRECTION_CHANNEL_NAME = 'UNDOCK_DIRECTION'
DYNAMIC_NPC_SPAWN_NPCS = 'DYNAMIC_NPC_SPAWN_NPCS'
DYNAMIC_NPC_SPAWN_OWNER_ID = 'DYNAMIC_NPC_SPAWN_OWNER_ID'
DYNAMIC_NPC_SPAWN_GROUP_BEHAVIOR_ID = 'DYNAMIC_NPC_SPAWN_GROUP_BEHAVIOR'
DYNAMIC_NPC_SPAWN_OBJECT_ID = 'DYNAMIC_NPC_SPAWN_OBJECT_ID'
DYNAMIC_NPC_SPAWN_DISTANCE = 'DYNAMIC_NPC_SPAWN_DISTANCE'
DYNAMIC_NPC_SPAWN_ITEM_ID = 'DYNAMIC_NPC_SPAWN_ITEM_ID'
GUARD_OBJECT_POSITION_CHANNEL_NAME = 'GUARD_OBJECT_POSITION'
GUARD_OBJECT_ORBIT_RANGE_CHANNEL_NAME = 'GUARD_OBJECT_ORBIT_RANGE'
DRONE_CONTROLLER_CHANNEL_NAME = 'DRONE_CONTROLLER'
GROUP_PRIMARY_TARGET_CHANNEL_NAME = 'GROUP_PRIMARY_TARGET'
CAN_SPAWN_SITES_CHANNEL_NAME = 'CAN_SPAWN_SITES'
IS_DUNGEON_INDEPENDENT_CHANNEL_NAME = 'IS_DUNGEON_INDEPENDENT'
EXTRA_FLEET_MEMBERS_CHANNEL_NAME = 'Extra Fleet Members'
ADDITIONAL_LOOT_TABLES_ADDRESS = (ScopeTypes.EntityGroup, 'ADDITIONAL_LOOT_TABLES')
COMBAT_TARGETS_SET_ADDRESS = (ScopeTypes.EntityGroup, 'COMBAT_TARGETS_SET')
COMBAT_MIN_OPTIMAL_ADDRESS = (ScopeTypes.Item, 'COMBAT_MIN_OPTIMAL_RANGE')
COMBAT_MIN_FALLOFF_ADDRESS = (ScopeTypes.Item, 'COMBAT_MIN_FALLOFF_RANGE')
COMMANDER_ADDRESS = (ScopeTypes.EntityGroup, 'COMMANDER')
DRONE_CONTROLLER_ADDRESS = (ScopeTypes.EntityGroup, 'DRONE_CONTROLLER')
SELF_DESTRUCT_DRONE_ON_CONTROLLER_DEATH_ADDRESS = (ScopeTypes.EntityGroup, 'SELF_DESTRUCT_DRONE_ON_CONTROLLER_DEATH')
GUARD_OBJECT_AGGRESSION_RANGE = (ScopeTypes.EntityGroup, 'GUARD_OBJECT_AGGRESSION_RANGE')
GUARD_OBJECT_ITEM_ID = (ScopeTypes.EntityGroup, GUARD_OBJECT_ITEM_ID_MESSAGE_CHANNEL)
GUARD_OBJECT_POSITION = (ScopeTypes.EntityGroup, GUARD_OBJECT_POSITION_CHANNEL_NAME)
GUARD_OBJECT_ORBIT_RANGE = (ScopeTypes.EntityGroup, GUARD_OBJECT_ORBIT_RANGE_CHANNEL_NAME)
GROUP_PRIMARY_TARGET = (ScopeTypes.EntityGroup, GROUP_PRIMARY_TARGET_CHANNEL_NAME)
HAULER_PICK_UP_BALL_IDS = (ScopeTypes.EntityGroup, 'HAULER_PICK_UP_BALLS')
HAULER_REQUESTED_ADDRESS = (ScopeTypes.EntityGroup, 'HAULER_REQUESTED')
LAST_REINFORCEMENT_REQUEST_COORDINATE_ADDRESS = (ScopeTypes.EntityGroup, 'LAST_REINFORCEMENT_REQUEST_COORDINATE')
MY_COMBAT_TARGET = (ScopeTypes.Item, 'MY_COMBAT_TARGET')
REINFORCEMENT_REQUESTED = (ScopeTypes.EntityGroup, 'REINFORCEMENT_REQUESTED')
STANDINGS_FRIENDLY_THRESHOLD_ADDRESS = (ScopeTypes.EntityGroup, STANDINGS_FRIENDLY_THRESHOLD_CHANNEL_NAME)
STANDINGS_HOSTILE_THRESHOLD_ADDRESS = (ScopeTypes.EntityGroup, STANDINGS_HOSTILE_THRESHOLD_CHANNEL_NAME)
UNSPAWN_ENTITY = (ScopeTypes.Item, 'UNSPAWN_ENTITY')
WARP_SCRAMBLED_ADDRESS = (ScopeTypes.Item, 'WARP_SCRAMBLED')
