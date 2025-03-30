#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\abyss\error.py
from .common.constants import FILAMENT_PROXIMITY_RESTRICTION_RANGE

class Error(Exception):
    ABYSS_CONTENT_ACTIVE = 1
    IN_ABYSS_SYSTEM = 2
    INVALID_KEY_TYPE = 3
    INVALID_OWNER = 4
    INVALID_SHIP_TYPE = 5
    ITEM_NOT_REACHABLE = 6
    KEY_NOT_FOUND = 7
    PROXIMITY_RESTRICTION = 8
    PVP_TIMER_ACTIVE = 9
    SAFETY_ENGAGED = 10
    SESSION_CHANGE_IN_PROGRESS = 11
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
    INVALID_SHIP_TYPE_THREE_PLAYER = 24
    SHIP_NOT_IN_SAME_FLEET = 25
    SHIP_HAS_ENTERED = 26
    MAX_ENTERED = 27
    ENTRANCE_CLOSED = 28
    PROXIMITY_ENTRANCE = 29
    ENTRANCE_MISSING = 30
    INVALID_KEY_AMOUNT = 31
    POCKET_COLLAPSING = 32
    CONGESTION_BAN = 33
    INVALID_SHIP_TYPE_TWO_PLAYER = 34
    VOID_SPACE_DISALLOWED = 35
    VERY_SECURE_SYSTEM_DISALLOWED = 36
    IN_BANNED_SYSTEM = 37

    def __init__(self, errors):
        self.errors = errors


def get_error_label(get_label, error, *args):
    if error == Error.ABYSS_CONTENT_ACTIVE:
        return get_label('UI/Abyss/Error/AbyssContentActive')
    elif error == Error.IN_ABYSS_SYSTEM:
        return get_label('UI/Abyss/Error/InAbyssSystem')
    elif error == Error.INVALID_KEY_TYPE:
        return get_label('UI/Abyss/Error/InvalidKeyType')
    elif error == Error.INVALID_OWNER:
        return get_label('UI/Abyss/Error/InvalidOwner')
    elif error == Error.INVALID_SHIP_TYPE:
        return get_label('UI/Abyss/Error/InvalidShipType')
    elif error == Error.ITEM_NOT_REACHABLE:
        return get_label('UI/Abyss/Error/ItemNotReachable', type=args[0])
    elif error == Error.KEY_NOT_FOUND:
        return get_label('UI/Abyss/Error/KeyNotFound')
    elif error == Error.PROXIMITY_RESTRICTION:
        return get_label('UI/Abyss/Error/ProximityRestriction', distance=FILAMENT_PROXIMITY_RESTRICTION_RANGE, type=args[0])
    elif error == Error.PVP_TIMER_ACTIVE:
        return get_label('UI/Abyss/Error/PvpTimerActive')
    elif error == Error.SAFETY_ENGAGED:
        return get_label('UI/Abyss/Error/SafetyEngaged')
    elif error == Error.SESSION_CHANGE_IN_PROGRESS:
        return get_label('UI/Abyss/Error/SessionChangeInProgress')
    elif error == Error.SHIP_IN_DUNGEON:
        return get_label('UI/Abyss/Error/ShipInDungeon')
    elif error == Error.SHIP_IN_FORCE_FIELD:
        return get_label('UI/Abyss/Error/ShipInForceField')
    elif error == Error.SHIP_IN_WARP:
        return get_label('UI/Abyss/Error/ShipInWarp')
    elif error == Error.SHIP_IS_CLOAKED:
        return get_label('UI/Abyss/Error/ShipIsCloaked')
    elif error == Error.SHIP_IS_DOCKED:
        return get_label('UI/Abyss/Error/ShipIsDocked')
    elif error == Error.SHIP_IS_INVULNERABLE:
        return get_label('UI/Abyss/Error/ShipIsInvulnerable')
    elif error == Error.SHIP_IS_SELF_DESTRUCTING:
        return get_label('UI/Abyss/Error/ShipIsSelfDestructing')
    elif error == Error.SHIP_IS_TETHERED:
        return get_label('UI/Abyss/Error/ShipIsTethered')
    elif error == Error.SHIP_IS_WARP_SCRAMBLED:
        return get_label('UI/Abyss/Error/ShipIsWarpScrambled')
    elif error == Error.SHIP_NOT_FOUND:
        return get_label('UI/Abyss/Error/ShipNotFound')
    elif error == Error.SHIP_NOT_IN_FLEET:
        return get_label('UI/Abyss/Error/PlayerNotInFleet')
    elif error == Error.INVALID_SHIP_TYPE_THREE_PLAYER:
        return get_label('UI/Abyss/Error/InvalidShipTypeFleet')
    elif error == Error.SHIP_NOT_IN_SAME_FLEET:
        return get_label('UI/Abyss/Error/PlayerNotInSameFleet')
    elif error == Error.SHIP_HAS_ENTERED:
        return get_label('UI/Abyss/Error/HasEntered')
    elif error == Error.MAX_ENTERED:
        return get_label('UI/Abyss/Error/MaxEntered')
    elif error == Error.ENTRANCE_CLOSED:
        return get_label('UI/Abyss/Error/EntranceClosed')
    elif error == Error.PROXIMITY_ENTRANCE:
        return get_label('UI/Abyss/Error/ProximityEntrance', distance=args[0])
    elif error == Error.ENTRANCE_MISSING:
        return get_label('UI/Abyss/Error/AbyssalEntranceMissing')
    elif error == Error.POCKET_COLLAPSING:
        return get_label('UI/Abyss/Error/PocketCollapsing')
    elif error == Error.INVALID_KEY_AMOUNT:
        return get_label('UI/Abyss/Error/AdditionalFilamentsNeeded', amount=args[0])
    elif error == Error.CONGESTION_BAN:
        return get_label('UI/PVPFilament/Errors/filamentCongestionBan')
    elif error == Error.INVALID_SHIP_TYPE_TWO_PLAYER:
        return get_label('UI/Abyss/Error/InvalidShipTypeTwoPlayer')
    elif error == Error.VOID_SPACE_DISALLOWED:
        return get_label('UI/VoidSpace/Error/InVoidSpaceSystem')
    elif error == Error.VERY_SECURE_SYSTEM_DISALLOWED:
        return get_label('UI/Abyss/Error/SystemRestriction')
    elif error == Error.IN_BANNED_SYSTEM:
        return get_label('UI/Abyss/Error/InBannedSystem')
    else:
        return get_label('UI/Abyss/Error/UnknownError')
