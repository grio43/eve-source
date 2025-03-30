#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\randomJump\error.py
from abyss import FILAMENT_PROXIMITY_RESTRICTION_RANGE

class RandomJumpError(Exception):
    IN_ABYSS_SYSTEM = 1
    INVALID_KEY_TYPE = 2
    INVALID_OWNER = 3
    INVALID_SHIP_TYPE = 4
    ITEM_NOT_REACHABLE = 5
    KEY_NOT_FOUND = 6
    PROXIMITY_RESTRICTION = 7
    PVP_TIMER_ACTIVE = 8
    SAFETY_ENGAGED = 9
    SESSION_CHANGE_IN_PROGRESS = 10
    INVALID_KEY_AMOUNT = 11
    SHIP_IN_DUNGEON = 12
    SHIP_IN_FORCE_FIELD = 13
    SHIP_IN_WARP = 14
    SHIP_IS_CLOAKED = 15
    SHIP_IS_DOCKED = 16
    SHIP_IS_INVULNERABLE = 17
    SHIP_IS_SELF_DESTRUCTING = 18
    SHIP_IS_TETHERED = 19
    SHIP_IS_WARP_SCRAMBLED = 20
    SHIP_NOT_FOUND = 21
    UNKNOWN_ERROR = 22
    SHIP_NOT_IN_FLEET = 23
    TOO_MANY_IN_FLEET = 24
    FLEET_MEMBER_NOT_IN_RANGE = 25
    DISABLE_MODULE_BEFORE_JUMPING = 26
    OVERLOADED_CARGO = 27
    FLEET_ROLES_NEEDED = 28
    CONGESTION_BAN = 29
    TRIGLAVIAN_SPACE_ONLY = 30
    TRIGLAVIAN_SPACE_DISALLOWED = 31
    NO_STORMS_ACTIVE = 32
    VOID_SPACE_DISALLOWED = 33
    WORMHOLE_SPACE_DISALLOWED = 34
    IN_BANNED_SYSTEM = 35
    INVALID_SHIP = 36
    INVALID_FLEET = 37
    NOT_ACTIVE = 38
    PROXIMITY_TO_GLOBAL_WARP_DISRUPTOR = 39

    def __init__(self, errors):
        self.errors = errors


def get_error_label(get_label, error, *args):
    if error == RandomJumpError.IN_ABYSS_SYSTEM:
        return get_label('UI/RandomJump/Error/InAbyssSystem', charID=args[0])
    elif error == RandomJumpError.INVALID_KEY_TYPE:
        return get_label('UI/RandomJump/Error/InvalidKeyType', charID=args[0])
    elif error == RandomJumpError.INVALID_OWNER:
        return get_label('UI/RandomJump/Error/InvalidOwner', charID=args[0])
    elif error == RandomJumpError.INVALID_SHIP_TYPE:
        return get_label('UI/RandomJump/Error/InvalidShipType', charID=args[0])
    elif error == RandomJumpError.ITEM_NOT_REACHABLE:
        return get_label('UI/RandomJump/Error/ItemNotReachable', type=args[0])
    elif error == RandomJumpError.KEY_NOT_FOUND:
        return get_label('UI/RandomJump/Error/KeyNotFound')
    elif error == RandomJumpError.PROXIMITY_RESTRICTION:
        return get_label('UI/RandomJump/Error/ProximityRestriction', distance=FILAMENT_PROXIMITY_RESTRICTION_RANGE, type=args[0], charID=args[1])
    elif error == RandomJumpError.PVP_TIMER_ACTIVE:
        return get_label('UI/RandomJump/Error/PvpTimerActive', charID=args[0])
    elif error == RandomJumpError.SAFETY_ENGAGED:
        return get_label('UI/RandomJump/Error/SafetyEngaged', charID=args[0])
    elif error == RandomJumpError.SESSION_CHANGE_IN_PROGRESS:
        return get_label('UI/RandomJump/Error/SessionChangeInProgress', charID=args[0])
    elif error == RandomJumpError.SHIP_IN_DUNGEON:
        return get_label('UI/RandomJump/Error/ShipInDungeon', charID=args[0])
    elif error == RandomJumpError.SHIP_IN_FORCE_FIELD:
        return get_label('UI/RandomJump/Error/ShipInForceField', charID=args[0])
    elif error == RandomJumpError.SHIP_IN_WARP:
        return get_label('UI/RandomJump/Error/ShipInWarp', charID=args[0])
    elif error == RandomJumpError.SHIP_IS_CLOAKED:
        return get_label('UI/RandomJump/Error/ShipIsCloaked', charID=args[0])
    elif error == RandomJumpError.SHIP_IS_DOCKED:
        return get_label('UI/RandomJump/Error/ShipIsDocked', charID=args[0])
    elif error == RandomJumpError.SHIP_IS_INVULNERABLE:
        return get_label('UI/RandomJump/Error/ShipIsInvulnerable', charID=args[0])
    elif error == RandomJumpError.SHIP_IS_SELF_DESTRUCTING:
        return get_label('UI/RandomJump/Error/ShipIsSelfDestructing', charID=args[0])
    elif error == RandomJumpError.SHIP_IS_TETHERED:
        return get_label('UI/RandomJump/Error/ShipIsTethered', charID=args[0])
    elif error == RandomJumpError.SHIP_IS_WARP_SCRAMBLED:
        return get_label('UI/RandomJump/Error/ShipIsWarpScrambled', charID=args[0])
    elif error == RandomJumpError.SHIP_NOT_FOUND:
        return get_label('UI/RandomJump/Error/ShipNotFound')
    elif error == RandomJumpError.SHIP_NOT_IN_FLEET:
        return get_label('UI/RandomJump/Error/PlayerNotInFleet')
    elif error == RandomJumpError.TOO_MANY_IN_FLEET:
        return get_label('UI/RandomJump/Error/FleetToBig', amount=args[0])
    elif error == RandomJumpError.INVALID_KEY_AMOUNT:
        return get_label('UI/RandomJump/Error/AdditionalFilamentsNeeded')
    elif error == RandomJumpError.FLEET_MEMBER_NOT_IN_RANGE:
        return get_label('UI/RandomJump/Error/FleetMemberNotInRange', charID=args[0], distance=args[1])
    elif error == RandomJumpError.DISABLE_MODULE_BEFORE_JUMPING:
        return get_label('UI/RandomJump/Error/DisableModuleBeforeJump', charID=args[0], type=args[1])
    elif error == RandomJumpError.OVERLOADED_CARGO:
        return get_label('UI/RandomJump/Error/overLoadedCargo', charID=args[0])
    elif error == RandomJumpError.FLEET_ROLES_NEEDED:
        return get_label('UI/RandomJump/Error/FleetRolesNeeded')
    elif error == RandomJumpError.CONGESTION_BAN:
        return get_label('UI/PVPFilament/Errors/filamentCongestionBan')
    elif error == RandomJumpError.TRIGLAVIAN_SPACE_ONLY:
        return get_label('UI/RandomJump/Error/TriglavianSpaceOnly')
    elif error == RandomJumpError.TRIGLAVIAN_SPACE_DISALLOWED:
        return get_label('UI/RandomJump/Error/TriglavianSpaceDisallowed')
    elif error == RandomJumpError.NO_STORMS_ACTIVE:
        return get_label('UI/RandomJump/Error/NoStormsActive')
    elif error == RandomJumpError.VOID_SPACE_DISALLOWED:
        return get_label('UI/VoidSpace/Error/InVoidSpaceSystem')
    elif error == RandomJumpError.WORMHOLE_SPACE_DISALLOWED:
        return get_label('UI/RandomJump/Error/InWormholeSystem', charID=args[0])
    elif error == RandomJumpError.IN_BANNED_SYSTEM:
        return get_label('UI/Abyss/Error/InBannedSystem')
    elif error == RandomJumpError.INVALID_FLEET:
        return get_label('UI/RandomJump/Error/InvalidFleet', charID=args[0])
    elif error == RandomJumpError.PROXIMITY_TO_GLOBAL_WARP_DISRUPTOR:
        return get_label('UI/RandomJump/Error/InGlobalWarpDisruptor')
    else:
        return get_label('UI/RandomJump/Error/UnknownError')


def get_short_error_path_for_self(error, *args):
    if error == RandomJumpError.PVP_TIMER_ACTIVE:
        return 'UI/RandomJump/Error/PvpTimerActiveShort'
    elif error == RandomJumpError.SAFETY_ENGAGED:
        return 'UI/RandomJump/Error/SafetyEngagedShort'
    elif error == RandomJumpError.SESSION_CHANGE_IN_PROGRESS:
        return 'UI/RandomJump/Error/SessionChangeInProgressShort'
    elif error == RandomJumpError.SHIP_IN_WARP:
        return 'UI/Menusvc/MenuHints/YouAreInWarp'
    elif error == RandomJumpError.SHIP_IS_CLOAKED:
        return 'UI/Menusvc/MenuHints/YouAreCloaked'
    elif error == RandomJumpError.SHIP_IS_INVULNERABLE:
        return 'UI/RandomJump/Error/ShipIsInvulnerableShort'
    elif error == RandomJumpError.SHIP_IS_WARP_SCRAMBLED:
        return 'UI/RandomJump/Error/ShipIsWarpScrambled'
    elif error == RandomJumpError.SHIP_NOT_IN_FLEET:
        return 'UI/RandomJump/Error/PlayerNotInFleetShort'
    elif error == RandomJumpError.FLEET_ROLES_NEEDED:
        return 'UI/RandomJump/Error/FleetRolesNeededShort'
    elif error == RandomJumpError.INVALID_FLEET:
        return 'UI/RandomJump/Error/InvalidFleetShort'
    elif error == RandomJumpError.NOT_ACTIVE:
        return 'UI/RandomJump/Error/NotActiveShort'
    else:
        return 'UI/RandomJump/Error/UnknownError'
