#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\abyss\client\validator.py
from abyss.error import Error
from abyss.common.validator import BaseValidator
import blue
import dogma.const
from eve.common.lib import appConst

class ClientValidator(BaseValidator):

    def __init__(self, game_mode, gate_id = None, key = None, type_id = None):
        super(ClientValidator, self).__init__(game_mode)
        self._is_cloaking = False
        self._is_invulnerable = self._is_invulnerable_timer_active()
        self._type_id = type_id
        self._key = key
        self._gate_id = gate_id

    def set_cloaking(self, is_cloaking):
        self._is_cloaking = is_cloaking

    def set_invulnerable(self, is_invulnerable):
        self._is_invulnerable = is_invulnerable

    def raise_errors(self):
        raise Error(self._errors)

    def get_session(self):
        return session

    def get_ship_item(self):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        while dogmaLocation.IsItemLoading(session.shipid):
            blue.synchro.Yield()

        try:
            return dogmaLocation.GetDogmaItem(session.shipid)
        except KeyError:
            raise Error([(Error.SHIP_NOT_FOUND, ())])

    def get_solar_system_security_level(self):
        return sm.GetService('securitySvc').get_modified_security_level(self.get_session().solarsystemid2)

    def is_cloaked(self):
        ship_ball = sm.GetService('michelle').GetBall(session.shipid)
        is_cloaked = ship_ball is not None and ship_ball.isCloaked
        return self._is_cloaking or is_cloaked

    def is_invulnerable(self):
        if self.is_demo_filament():
            return False
        return self._is_invulnerable

    def is_in_banned_system(self):
        return False

    def is_in_active_encounter(self):
        return False

    def is_in_force_field(self):
        return False

    def is_pvp_timer_active(self):
        state, timeout = sm.GetService('crimewatchSvc').GetPvpTimer()
        return state != appConst.pvpTimerStateIdle

    def is_self_destructing(self):
        slimItem = sm.GetService('michelle').GetItem(session.shipid)
        return getattr(slimItem, 'selfDestructTime', None) is not None

    def is_tethered(self):
        fxSequencer = sm.GetService('FxSequencer')
        effects = fxSequencer.GetAllBallActivations(session.shipid)
        for effect in effects:
            if effect.guid == 'effects.Tethering':
                return True

        return False

    def is_warping(self):
        return sm.GetService('michelle').InWarp()

    def is_warp_scrambled(self):
        return False

    def get_closest_of_type(self, types):
        return None

    def get_key_item(self):
        return self._key

    def get_key_tier(self):
        dogmaStaticSvc = sm.GetService('clientDogmaStaticSvc')
        type_id = self._type_id or self.get_key_item().typeID
        return dogmaStaticSvc.GetTypeAttribute2(type_id, dogma.const.attributeDifficultyTier)

    def is_blocked_by_dungeon(self):
        return False

    def is_item_reachable(self, item):
        return True

    def is_safety_green(self):
        if self.is_demo_filament():
            return False
        safetyLevel = sm.GetService('crimewatchSvc').GetSafetyLevel()
        return safetyLevel == appConst.shipSafetyLevelFull

    def get_distance_to_entrance(self):
        return 0

    def get_gate_id(self):
        return self._gate_id

    def get_ships(self):
        return None

    def is_entrance_gate_open(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        slim_item = ballpark.GetInvItem(self.get_gate_id())
        return getattr(slim_item, 'isAbyssGateOpen', False)

    def is_in_same_fleet(self):
        return True

    def _is_invulnerable_timer_active(self):
        combatTimers = sm.GetService('infoPanel').combatTimerContainer
        return combatTimers.invulnTimer is not None
