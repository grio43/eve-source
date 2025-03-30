#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\goals\common\goalConst.py
UPDATE_TIMEOUT_SECONDS = 10

class GoalState:
    UNSPECIFIED = 0
    ACTIVE = 1
    CLOSED = 2
    COMPLETED = 3
    EXPIRED = 4


state_labels = {GoalState.UNSPECIFIED: 'UI/Corporations/Goals/StateUnspecified',
 GoalState.ACTIVE: 'UI/Corporations/Goals/StateActive',
 GoalState.CLOSED: 'UI/Corporations/Goals/StateClosed',
 GoalState.COMPLETED: 'UI/Corporations/Goals/StateCompleted',
 GoalState.EXPIRED: 'UI/Corporations/Goals/StateExpired'}

class OrganizationType:
    CORPORATION = 1
    CHARACTER = 2


class ContributionMethodTypes:
    MANUAL = 'Manual'
    DAMAGE_SHIP = 'DamageShip'
    DELIVER_ITEM = 'DeliverItem'
    KILL_NPC = 'KillNPC'
    MINE_ORE = 'MineOre'
    HARVEST_GAS = 'HarvestGas'
    MANUFACTURE_ITEM = 'ManufactureItem'
    DESTROY_PLAYER_SHIP = 'KillCapsuleer'
    CAPTURE_FACWAR_COMPLEX = 'CaptureFWComplex'
    DEFEND_FACWAR_COMPLEX = 'DefendFWComplex'
    REMOTE_REPAIR_SHIELD = 'RemoteRepairShields'
    REMOTE_REPAIR_ARMOR = 'RemoteRepairArmor'
    WARP_SCRAMBLE = 'WarpScramble'
    SCAN_SIGNATURE = 'ScanSignature'
    COMPLETE_GOAL = 'CompleteGoal'
    SALVAGE_WRECK = 'SalvageWreck'
    EARN_LOYALTY_POINTS = 'EarnLoyaltyPoints'
    EARN_EVER_MARKS = 'EarnEverMarks'
    SHIP_LOSS = 'ShipLoss'
    HACK_CONTAINER = 'HackContainer'
    SHIP_INSURANCE = 'ShipInsurance'
    SPACE_JUMP = 'SpaceJump'


class GoalParameterTypes:
    EVE_TYPE = 'eve_type'
    SHIP_TYPE = 'ship_type'
    MINEABLE_ORE_TYPE = 'mineable_ore_type'
    MANUFACTURABLE_ITEM_TYPE = 'manufacturable_item_type'
    HARVESTABLE_GAS_TYPE = 'harvestable_gas_type'
    SOLAR_SYSTEM = 'solar_system'
    NPC_FACTION = 'npc_faction'
    NPC_CORPORATION = 'npc_corporation'
    LP_NPC_CORPORATION = 'lp_npc_corporation'
    OWNER_IDENTITY = 'owner_identity'
    CORP_OFFICE = 'corp_office'
    CORP_OFFICE_LOCATION = 'corp_office_location'
    FACTIONAL_WARFARE_COMPLEX_TYPE = 'factional_warfare_complex_type'
    ON_BEHALF_OF = 'on_behalf_of'
    SIGNATURE_TYPE = 'signature_type'
    HACKING_CONTAINER_TYPE = 'hacking_container_type'
    BOOLEAN_TYPE = 'boolean_type'
    CAPSULEER_INVOLVEMENT = 'capsuleer_involvement'
    INSURANCE_SHIP_TYPE = 'insurance_ship_type'


class CareerPathId:
    UNSPECIFIED = 0
    EXPLORER = 4
    INDUSTRIALIST = 5
    ENFORCER = 6
    SOLDIER_OF_FORTUNE = 7


class ConflictType:
    ALL = 0
    PVP = 1
    PVE = 2


CAREER_PATH_IDS = [None,
 CareerPathId.EXPLORER,
 CareerPathId.INDUSTRIALIST,
 CareerPathId.ENFORCER,
 CareerPathId.SOLDIER_OF_FORTUNE]
ON_BEHALF_OF_SELF = 'ON_BEHALF_OF_CHARACTER'
ON_BEHALF_OF_CORP = 'ON_BEHALF_OF_CORP'
ON_BEHALF_OF_LABELS = {ON_BEHALF_OF_SELF: 'UI/GameGoalConfig/Parameters/RunJobOnBehalfOfCharacter',
 ON_BEHALF_OF_CORP: 'UI/GameGoalConfig/Parameters/RunJobOnBehalfOfCorp'}
QUASAR_GROUP_NAME = 'eve-organization-goals'
