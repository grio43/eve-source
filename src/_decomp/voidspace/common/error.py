#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\voidspace\common\error.py
from voidspace.common.constants import FILAMENT_PROXIMITY_RESTRICTION_RANGE

class VoidSpaceJumpError(Exception):
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
    VOID_SPACE_DISALLOWED = 30
    IN_BANNED_SYSTEM = 31

    def __init__(self, errors):
        self.errors = errors


def get_error_label(get_label, error, *args):
    if error == VoidSpaceJumpError.IN_ABYSS_SYSTEM:
        return get_label('UI/RandomJump/Error/InAbyssSystem', charID=args[0])
    elif error == VoidSpaceJumpError.INVALID_KEY_TYPE:
        return get_label('UI/RandomJump/Error/InvalidKeyType', charID=args[0])
    elif error == VoidSpaceJumpError.INVALID_OWNER:
        return get_label('UI/RandomJump/Error/InvalidOwner', charID=args[0])
    elif error == VoidSpaceJumpError.INVALID_SHIP_TYPE:
        return get_label('UI/RandomJump/Error/InvalidShipType', charID=args[0])
    elif error == VoidSpaceJumpError.ITEM_NOT_REACHABLE:
        return get_label('UI/RandomJump/Error/ItemNotReachable', type=args[0])
    elif error == VoidSpaceJumpError.KEY_NOT_FOUND:
        return get_label('UI/RandomJump/Error/KeyNotFound')
    elif error == VoidSpaceJumpError.PROXIMITY_RESTRICTION:
        return get_label('UI/RandomJump/Error/ProximityRestriction', distance=FILAMENT_PROXIMITY_RESTRICTION_RANGE, type=args[0], charID=args[1])
    elif error == VoidSpaceJumpError.PVP_TIMER_ACTIVE:
        return get_label('UI/RandomJump/Error/PvpTimerActive', charID=args[0])
    elif error == VoidSpaceJumpError.SAFETY_ENGAGED:
        return get_label('UI/RandomJump/Error/SafetyEngaged', charID=args[0])
    elif error == VoidSpaceJumpError.SESSION_CHANGE_IN_PROGRESS:
        return get_label('UI/RandomJump/Error/SessionChangeInProgress', charID=args[0])
    elif error == VoidSpaceJumpError.SHIP_IN_DUNGEON:
        return get_label('UI/RandomJump/Error/ShipInDungeon', charID=args[0])
    elif error == VoidSpaceJumpError.SHIP_IN_FORCE_FIELD:
        return get_label('UI/RandomJump/Error/ShipInForceField', charID=args[0])
    elif error == VoidSpaceJumpError.SHIP_IN_WARP:
        return get_label('UI/RandomJump/Error/ShipInWarp', charID=args[0])
    elif error == VoidSpaceJumpError.SHIP_IS_CLOAKED:
        return get_label('UI/RandomJump/Error/ShipIsCloaked', charID=args[0])
    elif error == VoidSpaceJumpError.SHIP_IS_DOCKED:
        return get_label('UI/RandomJump/Error/ShipIsDocked', charID=args[0])
    elif error == VoidSpaceJumpError.SHIP_IS_INVULNERABLE:
        return get_label('UI/RandomJump/Error/ShipIsInvulnerable', charID=args[0])
    elif error == VoidSpaceJumpError.SHIP_IS_SELF_DESTRUCTING:
        return get_label('UI/RandomJump/Error/ShipIsSelfDestructing', charID=args[0])
    elif error == VoidSpaceJumpError.SHIP_IS_TETHERED:
        return get_label('UI/RandomJump/Error/ShipIsTethered', charID=args[0])
    elif error == VoidSpaceJumpError.SHIP_IS_WARP_SCRAMBLED:
        return get_label('UI/RandomJump/Error/ShipIsWarpScrambled', charID=args[0])
    elif error == VoidSpaceJumpError.SHIP_NOT_FOUND:
        return get_label('UI/RandomJump/Error/ShipNotFound')
    elif error == VoidSpaceJumpError.SHIP_NOT_IN_FLEET:
        return get_label('UI/RandomJump/Error/PlayerNotInFleet')
    elif error == VoidSpaceJumpError.TOO_MANY_IN_FLEET:
        return get_label('UI/RandomJump/Error/FleetToBig', amount=args[0])
    elif error == VoidSpaceJumpError.INVALID_KEY_AMOUNT:
        return get_label('UI/RandomJump/Error/AdditionalFilamentsNeeded')
    elif error == VoidSpaceJumpError.FLEET_MEMBER_NOT_IN_RANGE:
        return get_label('UI/RandomJump/Error/FleetMemberNotInRange', charID=args[0], distance=args[1])
    elif error == VoidSpaceJumpError.DISABLE_MODULE_BEFORE_JUMPING:
        return get_label('UI/RandomJump/Error/DisableModuleBeforeJump', charID=args[0], type=args[1])
    elif error == VoidSpaceJumpError.OVERLOADED_CARGO:
        return get_label('UI/RandomJump/Error/overLoadedCargo', charID=args[0])
    elif error == VoidSpaceJumpError.FLEET_ROLES_NEEDED:
        return get_label('UI/RandomJump/Error/FleetRolesNeeded')
    elif error == VoidSpaceJumpError.CONGESTION_BAN:
        return get_label('UI/PVPFilament/Errors/filamentCongestionBan')
    elif error == VoidSpaceJumpError.VOID_SPACE_DISALLOWED:
        return get_label('UI/VoidSpace/Error/InVoidSpaceSystem')
    elif error == VoidSpaceJumpError.IN_BANNED_SYSTEM:
        return get_label('UI/Abyss/Error/InBannedSystem')
    else:
        return get_label('UI/RandomJump/Error/UnknownError')
