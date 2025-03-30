#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\destiny\net\client\_ticker.py
import logging
import sys
from destiny.net.client._baseticker import BaseTicker
from destiny.net.client._util import merge_state_into_history
import blue
logger = logging.getLogger(__name__)
LOCAL_ACTIONS = {'AddBallsToPark', 'RemoveBall', 'RemoveBalls'}

class Ticker(BaseTicker):

    def __init__(self, error_handler, client_ticker_interface):
        super(Ticker, self).__init__(error_handler)
        self._should_rebase = False
        self._last_stamp = -1
        self._states = []
        self._state_is_valid = False
        self._client_ticker_interface = client_ticker_interface

    def set_ballpark(self, ballpark):
        super(Ticker, self).set_ballpark(ballpark)
        self._client_ticker_interface.set_ballpark(ballpark)

    def _flush_state(self, state, wait_for_bubble):
        logger.info('Server Update with %s event(s) added to history', len(state))
        if len(state) == 0:
            logger.warn('Empty state received from remote ballpark')
            return
        if state[0][1][0] == 'SetState':
            self._latest_set_state_time = state[0][0]
            logger.info('Michelle received a SetState at time %s. Clearing out-of-date entries...', self._latest_set_state_time)
            self._history = [ history_entry for history_entry in self._history if history_entry[0][0][0] >= self._latest_set_state_time ]
            self._dump_history()
        else:
            entry_time = state[0][0]
            if entry_time < self._latest_set_state_time:
                logger.warn('Michelle discarded a state that was too old %s < %s', entry_time, self._latest_set_state_time)
                self._dump_history()
                return
        merge_state_into_history(state, self._history, wait_for_bubble)
        self._dump_history()

    def do_pre_tick(self):
        while len(self._history) > 0:
            state, wait_for_bubble = self._history[0]
            if wait_for_bubble:
                return
            event_stamp = state[0][0]
            if event_stamp > self._current_time and event_stamp - self._current_time < 3:
                break
            self._real_flush_state(state)
            del self._history[0]
            if self._state_is_valid and self._should_rebase:
                self.store_state(mid_tick=True)
            if len(self._history) > 1:
                if self._history[0][1]:
                    return
                self._ballpark._parent_Evolve()

    def _set_state(self, state, ego_ball_id):
        self._client_ticker_interface.on_set_state()
        self._ballpark.ClearAll()
        ms = blue.MemStream()
        ms.Write(state)
        self._ballpark.ReadFullStateFromStream(ms)
        self._ballpark.ego = long(ego_ball_id)
        self._ballpark.Start()
        self._state_is_valid = True
        self.flush_simulation_history()

    def _real_flush_state(self, state):
        logger.info('Handling Server Update with %s event(s)', len(state))
        if len(state) == 0:
            logger.warn('Empty state received from remote ballpark')
            return
        event_stamp, event = state[0]
        func_name, args = event
        if func_name == 'SetState':
            if self._client_ticker_interface.should_log_actions():
                logger.info('Action: %12.12s %s - current: %s %s', func_name, event_stamp, self._current_time, args)
            self._set_state(*args)
        if self._state_is_valid:
            self._should_rebase = False
            synchronised = False
            for action in state:
                event_stamp, event = action
                func_name, args = event
                if func_name == 'SetState':
                    continue
                if self._client_ticker_interface.should_log_actions():
                    logger.info('Action: %12.12s %s - current: %s %s', func_name, event_stamp, self._current_time, args)
                try:
                    if not synchronised:
                        synchronised = self.synchronize_to_simulation_time(event_stamp)
                    if not synchronised:
                        logger.warn('Failed to synchronize to %s', event_stamp)
                        self._error_handler.on_recoverable_desync()
                        return
                    self._should_rebase = True
                    if func_name in LOCAL_ACTIONS:
                        apply(getattr(self, func_name), args)
                    else:
                        apply(getattr(self._ballpark, '_parent_' + func_name), args)
                        self._client_ticker_interface.on_ballpark_local_action(func_name, args)
                        if func_name == 'CloakBall':
                            event_ball_id = args[0]
                            if self._ballpark.ego and self._ballpark.ego != event_ball_id:
                                self.RemoveBall(event_ball_id)
                except Exception:
                    message = '{} failed.'.format(func_name)
                    logger.error(message, exc_info=1)
                    sys.exc_clear()
                    continue

        else:
            logger.info('Events ignored')

    def do_post_tick(self, stamp):
        if self._should_rebase:
            self.flush_simulation_history()
            self._should_rebase = False
        elif stamp > self._last_stamp + 10:
            self.store_state()

    def clear_states(self):
        self._states = []

    def store_state(self, mid_tick = False):
        if not self._ballpark.isRunning:
            return
        ms = blue.MemStream()
        self._ballpark.WriteFullStateToStream(ms)
        self._states.append([ms, self._current_time, mid_tick])
        logger.info('store_state: %s mid_tick: %s', self._current_time, mid_tick)
        if len(self._states) > 10:
            self._states = self._states[:1] + self._states[3:3] + self._states[-5:]
        self._last_stamp = self._current_time

    def synchronize_to_simulation_time(self, stamp):
        logger.info('SynchroniseToSimulationTime looking for: %s - current: %s', stamp, self._current_time)
        if stamp < self._current_time:
            last_stamp = 0
            last_state = None
            for item in self._states:
                if item[1] <= stamp:
                    last_stamp = item[1]
                    last_state = item[0]
                else:
                    continue

            if not last_state:
                logger.warn('SynchroniseToSimulationTime: Did not find any state')
                return 0
            self._ballpark._parent_ReadFullStateFromStream(last_state, 1)
        else:
            last_stamp = self._current_time
        for i in range(stamp - last_stamp):
            self._ballpark._parent_Evolve()

        logger.info('SynchroniseToSimulationTime found: %s', self._current_time)
        return 1

    def flush_simulation_history(self, new_base_snapshot = True):
        logger.info('State history rebased at %s newBaseSnapshot %s', self._current_time, new_base_snapshot)
        last_mid_state = None
        if new_base_snapshot and len(self._states):
            last_mid_state = self._states[-1]
            if not last_mid_state[2] or last_mid_state[1] != self._current_time - 1:
                last_mid_state = None
        self.clear_states()
        if new_base_snapshot:
            if last_mid_state:
                self._states.append(last_mid_state)
            self.store_state()
            for state in self._states:
                logger.info('State entry %s', state)

    def AddBallsToPark(self, state):
        ms = blue.MemStream()
        ms.Write(state)
        self._ballpark.ReadFullStateFromStream(ms, 2)

    def RemoveBall(self, ball_id, terminal = False):
        blue.statistics.EnterZone('RemoveBall')
        try:
            if terminal:
                logger.info('Removing ball %s (terminal)')
            else:
                logger.info('Removing ball %s')
            ball = self._ballpark.balls.get(ball_id, None)
            delay = self._client_ticker_interface.get_ball_destruction_delay(ball, is_terminal=terminal)
            self._ballpark._parent_RemoveBall(ball_id, delay)
            self._client_ticker_interface.clean_up_after_ball_removal(ball_id, ball, is_terminal=terminal)
        finally:
            blue.statistics.LeaveZone()

    def RemoveBalls(self, ball_ids, is_release = False):
        blue.statistics.EnterZone('RemoveBalls')
        try:
            self._client_ticker_interface.clean_up_after_multiple_ball_removal(ball_ids, is_release=is_release)
            removal_delays = self._client_ticker_interface.get_ball_destruction_delays(ball_ids, is_release=is_release)
            for ball_id, delay in removal_delays.iteritems():
                self._ballpark._parent_RemoveBall(ball_id, delay)

        finally:
            blue.statistics.LeaveZone()

    def invalidate_state(self):
        self._state_is_valid = False

    def release(self):
        self.RemoveBalls(self._ballpark.balls.iterkeys(), is_release=True)
        self._ballpark.ClearAll()
        self.flush_simulation_history(new_base_snapshot=False)
        self._history = []
        self._latest_set_state_time = 0
        self._state_is_valid = False
