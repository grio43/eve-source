#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\state_machine.py
import logging
import eveui
import gametime
import threadutils
import uthread2
log = logging.getLogger(__name__)

class StateMachine(object):

    def __init__(self):
        self._is_closed = False
        self._active_state = None
        self._next_state = None
        self._is_transitioning = False
        self._active_transition = None

    @property
    def is_closed(self):
        return self._is_closed

    def close(self):
        if self._active_transition is not None:
            self._active_transition.stop()
        if self._active_state is not None:
            self._active_state.close()
            self._active_state = None
        self._is_closed = True

    @threadutils.threaded
    def move_to(self, state):
        self._next_state = state
        if self._is_transitioning:
            if self._active_transition is not None:
                self._active_transition.stop()
            return
        while self._next_state is not None:
            state = self._next_state
            self._next_state = None
            self._move_to(state)

    def _move_to(self, state):
        self._is_transitioning = True
        try:
            if self._active_state is not None:
                if type(self._active_state) == type(state):
                    return
                transition = self._active_state.exit()
                self._active_state.close()
                if transition is not None:
                    self._run_transition(transition)
            if self.is_closed:
                return
            if self._next_state is not None:
                state = self._next_state
                self._next_state = None
            self._active_state = state
            transition = self._active_state.enter()
            if transition is not None:
                self._run_transition(transition)
        finally:
            self._is_transitioning = False

    def _run_transition(self, transition):
        self._active_transition = transition
        try:
            transition.start()
            transition.wait()
        finally:
            self._active_transition = None


class State(object):

    def enter(self):
        return None

    def exit(self):
        return None

    def close(self):
        pass


class Transition(object):

    def __init__(self):
        self._is_started = False
        self._is_stopped = False
        self._is_closed = False
        self._wait_channel = uthread2.queue_channel()
        self._waiting_count = 0

    @property
    def is_stopped(self):
        return self._is_stopped

    def animation(self):
        pass

    def on_close(self):
        pass

    def sleep(self, duration, interruptable = True):
        start = gametime.now()
        while (gametime.now() - start).total_seconds() < duration:
            if interruptable and self._is_stopped:
                raise TransitionStopped()
            eveui.wait_for_next_frame()

    def start(self):
        if self._is_closed:
            raise RuntimeError('Transition has been closed')
        if self._is_started:
            raise RuntimeError('Already started')
        self._is_started = True
        self._perform_transition()

    def wait(self):
        if self._is_closed:
            return
        self._waiting_count += 1
        try:
            self._wait_channel.receive()
        finally:
            self._waiting_count -= 1

    def stop(self):
        self._is_stopped = True

    def close(self):
        if self._is_closed:
            return
        self.stop()
        self._is_closed = True
        if self._waiting_count > 0:
            self._notify_waiting()
        self.on_close()

    @threadutils.threaded
    def _perform_transition(self):
        try:
            self.animation()
        except TransitionStopped:
            pass
        except Exception:
            log.exception('Exception raised during transition')

        try:
            self.close()
        except Exception:
            log.exception('Exception when closing a transition')

        self._notify_waiting()

    def _notify_waiting(self):
        for _ in range(self._waiting_count):
            self._wait_channel.send(None)


class TransitionStopped(Exception):
    pass
