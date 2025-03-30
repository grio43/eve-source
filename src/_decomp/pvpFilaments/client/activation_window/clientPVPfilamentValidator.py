#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pvpFilaments\client\activation_window\clientPVPfilamentValidator.py
import gametime
import blue
import inventorycommon.const as invconst
from abyss import get_all_abyss_system_ids
from eve.common.lib import appConst
from pvpFilaments import PVPJumpError

class ClientPVPFilamentValidator(object):

    def __init__(self, key = None):
        super(ClientPVPFilamentValidator, self).__init__()
        self._is_cloaking = False
        self._is_invulnerable = self._is_invulnerable_timer_active()
        self._key = key
        self._charID = None

    @property
    def errors(self):
        return self._errors

    def add_error(self, error, *args):
        if isinstance(error, PVPJumpError):
            for e, args in error.errors:
                self.add_error(e, *args)

        else:
            self._errors.append((error, args))

    def _is_in_abyss_system(self):
        system_id = self.get_session().solarsystemid2
        return system_id in get_all_abyss_system_ids()

    def _is_session_change_in_progress(self):
        session = self.get_session()
        return session.nextSessionChange > gametime.GetSimTime()

    def _validate_key(self):
        try:
            key = self.get_key_item()
        except PVPJumpError as error:
            self.add_error(error)
            return

        if key.groupID != invconst.groupPVPfilamentKeys:
            self.add_error(PVPJumpError.INVALID_KEY_TYPE, self.get_char_id())
        if key.ownerID != self.get_char_id():
            self.add_error(PVPJumpError.INVALID_OWNER, self.get_char_id())
        if key.stacksize < 1:
            self.add_error(PVPJumpError.INVALID_KEY_AMOUNT)

    def _validate_fleet_required(self):
        session = self.get_session()
        if not session.fleetid:
            self.add_error(PVPJumpError.SHIP_NOT_IN_FLEET)

    def is_docked(self):
        session = self.get_session()
        return session.structureid or session.stationid

    def is_blocked_by_safety(self):
        return self.is_safety_green()

    def set_cloaking(self, is_cloaking):
        self._is_cloaking = is_cloaking

    def set_invulnerable(self, is_invulnerable):
        self._is_invulnerable = is_invulnerable

    def raise_errors(self):
        if self._errors:
            raise PVPJumpError(self._errors)

    def get_session(self):
        return session

    def get_char_id(self):
        if self._charID is None:
            self._charID = self.get_session().charid
        return self._charID

    def get_ship_item(self):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        while dogmaLocation.IsItemLoading(session.shipid):
            blue.synchro.Yield()

        try:
            return dogmaLocation.GetDogmaItem(session.shipid)
        except KeyError:
            raise PVPJumpError([(PVPJumpError.SHIP_NOT_FOUND, ())])

    def is_cloaked(self):
        ship_ball = sm.GetService('michelle').GetBall(session.shipid)
        is_cloaked = ship_ball is not None and ship_ball.isCloaked
        return self._is_cloaking or is_cloaked

    def is_invulnerable(self):
        return self._is_invulnerable

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

    def get_key_item(self):
        return self._key

    def is_safety_green(self):
        safetyLevel = sm.GetService('crimewatchSvc').GetSafetyLevel()
        return safetyLevel == appConst.shipSafetyLevelFull

    def _is_invulnerable_timer_active(self):
        combatTimers = sm.GetService('infoPanel').combatTimerContainer
        return combatTimers.invulnTimer is not None

    def _validate_ship(self):
        try:
            ship = self.get_ship_item()
        except PVPJumpError as error:
            self.add_error(error)
            return

    def validate_jump(self):
        self._errors = []
        self.perform_base_validation_checks()
        if self._errors:
            self.raise_errors()

    def perform_base_validation_checks(self):
        self._validate_ship()
        if self.is_docked():
            self.add_error(PVPJumpError.SHIP_IS_DOCKED, self.get_char_id())
        if self.is_cloaked():
            self.add_error(PVPJumpError.SHIP_IS_CLOAKED, self.get_char_id())
        if self.is_invulnerable():
            self.add_error(PVPJumpError.SHIP_IS_INVULNERABLE, self.get_char_id())
        if self.is_self_destructing():
            self.add_error(PVPJumpError.SHIP_IS_SELF_DESTRUCTING, self.get_char_id())
        if self.is_tethered():
            self.add_error(PVPJumpError.SHIP_IS_TETHERED, self.get_char_id())
        if self.is_warping():
            self.add_error(PVPJumpError.SHIP_IN_WARP, self.get_char_id())
        if self._is_in_abyss_system():
            self.add_error(PVPJumpError.IN_ABYSS_SYSTEM, self.get_char_id())
        if self._is_session_change_in_progress():
            self.add_error(PVPJumpError.SESSION_CHANGE_IN_PROGRESS, self.get_char_id())
        if self.is_pvp_timer_active():
            self.add_error(PVPJumpError.PVP_TIMER_ACTIVE, self.get_char_id())
