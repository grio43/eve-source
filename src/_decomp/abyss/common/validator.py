#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\abyss\common\validator.py
import abc
from abyss.common import TIER_0_DEMO
from abyss.const import get_all_abyss_system_ids
from abyss.common import suspicion
from abyss.common.constants import FILAMENT_PROXIMITY_RESTRICTION_LIST_ID
from abyss.error import Error
from ccpProfile import TimedFunction
from eve.common.lib.appConst import maxStargateJumpingDistance
import evetypes
import gametime
import inventorycommon.const as invconst
from eve.common.script.sys.idCheckers import IsVoidSpaceSystem
from eveuniverse.solar_systems import is_abyssal_filament_restricted

class BaseValidator(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, game_mode):
        self._errors = []
        self.game_mode = game_mode

    @property
    def errors(self):
        return self._errors

    def add_error(self, error, *args):
        if isinstance(error, Error):
            for e, args in error.errors:
                self.add_error(e, *args)

        else:
            self._errors.append((error, args))

    @TimedFunction('abyss::common::validate_jump')
    def validate_jump(self):
        self._errors = []
        self.perform_base_validation_checks()
        self.perform_jump_validation_checks()
        if self._errors:
            self.raise_errors()

    @TimedFunction('abyss::common::validate_deploy')
    def validate_deploy(self):
        self._errors = []
        self.perform_base_validation_checks()
        self.perform_deploy_validation_checks()
        if self._errors:
            self.raise_errors()

    @abc.abstractmethod
    def raise_errors(self):
        pass

    @abc.abstractmethod
    def get_session(self):
        pass

    @abc.abstractmethod
    def get_ship_item(self):
        pass

    @abc.abstractmethod
    def get_solar_system_security_level(self):
        pass

    @abc.abstractmethod
    def is_cloaked(self):
        pass

    @abc.abstractmethod
    def is_invulnerable(self):
        pass

    @abc.abstractmethod
    def is_in_banned_system(self):
        pass

    @abc.abstractmethod
    def is_in_active_encounter(self):
        pass

    @abc.abstractmethod
    def is_in_force_field(self):
        pass

    @abc.abstractmethod
    def is_pvp_timer_active(self):
        pass

    @abc.abstractmethod
    def is_self_destructing(self):
        pass

    @abc.abstractmethod
    def is_tethered(self):
        pass

    @abc.abstractmethod
    def is_warping(self):
        pass

    @abc.abstractmethod
    def is_warp_scrambled(self):
        pass

    @abc.abstractmethod
    def get_closest_of_type(self, types):
        pass

    @abc.abstractmethod
    def get_key_item(self):
        pass

    @abc.abstractmethod
    def get_key_tier(self):
        pass

    @abc.abstractmethod
    def is_blocked_by_dungeon(self):
        pass

    @abc.abstractmethod
    def is_item_reachable(self, item):
        pass

    @abc.abstractmethod
    def is_safety_green(self):
        pass

    @abc.abstractmethod
    def get_distance_to_entrance(self):
        pass

    @abc.abstractmethod
    def get_gate_id(self):
        pass

    @abc.abstractmethod
    def get_ships(self):
        pass

    @abc.abstractmethod
    def is_entrance_gate_open(self):
        pass

    @abc.abstractmethod
    def is_in_same_fleet(self):
        pass

    def is_in_secure_system(self):
        return self.get_max_tier_in_system() == suspicion.FILAMENT_ACTIVATION_NOT_ALLOWED

    def get_max_tier_in_system(self):
        return suspicion.get_max_allowed_tier_by_security_level(self.get_solar_system_security_level())

    def is_suspicious(self):
        max_tier = self.get_max_tier_in_system()
        if max_tier == suspicion.FILAMENT_ACTIVATION_NOT_ALLOWED:
            return False
        return self.get_key_tier() > self.get_max_tier_in_system()

    def is_docked(self):
        session = self.get_session()
        return session.structureid or session.stationid

    def is_blocked_by_safety(self):
        return self.is_suspicious() and self.is_safety_green()

    def has_entered(self):
        ships = self.get_ships()
        return ships is not None and self.get_ship_item().itemID in self.get_ships()

    def is_encounter_full(self):
        ships = self.get_ships()
        return ships is not None and len(ships) >= self.game_mode.max_players

    def perform_base_validation_checks(self):
        if self.is_in_secure_system():
            self.add_error(Error.VERY_SECURE_SYSTEM_DISALLOWED)
        if self.is_in_banned_system():
            self.add_error(Error.CONGESTION_BAN)
        if self._is_in_void_space():
            self.add_error(Error.VOID_SPACE_DISALLOWED)
        self._validate_ship()
        if self.is_docked():
            self.add_error(Error.SHIP_IS_DOCKED)
        if self.is_cloaked():
            self.add_error(Error.SHIP_IS_CLOAKED)
        if self.is_invulnerable():
            self.add_error(Error.SHIP_IS_INVULNERABLE)
        if self.is_in_active_encounter():
            self.add_error(Error.ABYSS_CONTENT_ACTIVE)
        if self.is_in_force_field():
            self.add_error(Error.SHIP_IN_FORCE_FIELD)
        if self.is_pvp_timer_active():
            self.add_error(Error.PVP_TIMER_ACTIVE)
        if self.is_self_destructing():
            self.add_error(Error.SHIP_IS_SELF_DESTRUCTING)
        if self.is_tethered():
            self.add_error(Error.SHIP_IS_TETHERED)
        if self.is_warping():
            self.add_error(Error.SHIP_IN_WARP)
        if self.is_warp_scrambled():
            self.add_error(Error.SHIP_IS_WARP_SCRAMBLED)
        if self._is_in_abyss_system():
            self.add_error(Error.IN_ABYSS_SYSTEM)
        if self._is_session_change_in_progress():
            self.add_error(Error.SESSION_CHANGE_IN_PROGRESS)
        if self._is_in_banned_system():
            self.add_error(Error.IN_BANNED_SYSTEM)

    def perform_deploy_validation_checks(self):
        self._validate_fleet_required()
        self._validate_key()
        self._validate_proximity()
        if self.is_blocked_by_dungeon():
            self.add_error(Error.SHIP_IN_DUNGEON)
        if self.is_blocked_by_safety():
            self.add_error(Error.SAFETY_ENGAGED)

    def perform_jump_validation_checks(self):
        self._is_close_enough_to_entrance()
        if self.game_mode.is_locked_to_creator and not self.is_in_same_fleet():
            self.add_error(Error.SHIP_NOT_IN_SAME_FLEET)
        if not self.is_entrance_gate_open():
            self.add_error(Error.ENTRANCE_CLOSED)
        if self.has_entered():
            self.add_error(Error.SHIP_HAS_ENTERED)
        if self.is_encounter_full():
            self.add_error(Error.MAX_ENTERED)

    def _is_close_enough_to_entrance(self):
        try:
            distance = self.get_distance_to_entrance()
            if distance > maxStargateJumpingDistance:
                self.add_error(Error.PROXIMITY_ENTRANCE, maxStargateJumpingDistance)
        except Exception:
            self.add_error(Error.ENTRANCE_MISSING)

    def _is_in_abyss_system(self):
        system_id = self.get_session().solarsystemid2
        return system_id in get_all_abyss_system_ids()

    def _is_in_void_space(self):
        system_id = self.get_session().solarsystemid2
        return IsVoidSpaceSystem(system_id)

    def _is_session_change_in_progress(self):
        session = self.get_session()
        return session.nextSessionChange > gametime.GetSimTime()

    def _is_in_banned_system(self):
        system_id = self.get_session().solarsystemid2
        return is_abyssal_filament_restricted(system_id)

    def _validate_ship(self):
        try:
            ship = self.get_ship_item()
        except Error as error:
            self.add_error(error)
            return

        if not self.game_mode.is_ship_allowed(ship.typeID):
            self.add_error(self.game_mode.ship_restriction_error_id)

    def _validate_key(self):
        try:
            key = self.get_key_item()
        except Error as error:
            self.add_error(error)
            return

        if key.groupID != invconst.groupAbyssalKeys:
            self.add_error(Error.INVALID_KEY_TYPE)
        if key.ownerID != self.get_session().charid:
            self.add_error(Error.INVALID_OWNER)
        if not self.is_item_reachable(key):
            self.add_error(Error.ITEM_NOT_REACHABLE, key.typeID)
        if key.stacksize < self.game_mode.key_stack_size:
            self.add_error(Error.INVALID_KEY_AMOUNT, self.game_mode.key_stack_size)

    def _validate_proximity(self):
        if self.is_demo_filament():
            return
        restricted_types = evetypes.GetTypeIDsByListID(FILAMENT_PROXIMITY_RESTRICTION_LIST_ID)
        closest_type_id = self.get_closest_of_type(restricted_types)
        if closest_type_id is not None:
            self.add_error(Error.PROXIMITY_RESTRICTION, closest_type_id)

    def _validate_fleet_required(self):
        if not self.game_mode.is_fleet_required:
            return
        session = self.get_session()
        if not session.fleetid:
            self.add_error(Error.SHIP_NOT_IN_FLEET)

    def is_demo_filament(self):
        return self.get_key_tier() == TIER_0_DEMO
