#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\destiny\net\client\_baseticker.py
import abc
import logging
import sys
import blue
logger = logging.getLogger(__name__)

class BaseTicker(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, error_handler):
        self._ballpark = None
        self._history = []
        self._latest_set_state_time = 0
        self._error_handler = error_handler

    def set_ballpark(self, ballpark):
        self._ballpark = ballpark
        self._error_handler.set_ballpark(ballpark)

    @abc.abstractmethod
    def do_pre_tick(self):
        raise NotImplemented

    def update(self, state, wait_for_bubble):
        if self._ballpark is None:
            return
        state = _expand_states(state)
        self._report_update_if_bad(state)
        self._flush_state(state, wait_for_bubble)

    @abc.abstractmethod
    def _flush_state(self, state, wait_for_bubble):
        raise NotImplemented

    @property
    def _current_time(self):
        return self._ballpark.currentTime

    def _dump_history(self):
        if logger.level > logging.INFO:
            return
        logger.info('------ %s History Dump %s -------', self.__class__.__name__, self._current_time)
        rev = self._history[:]
        rev.reverse()
        for state, wait_for_bubble in rev:
            logger.info('state waiting: %s', 'yes' if wait_for_bubble else 'no')
            last_state = None
            last_state_count = 0
            for entry in state:
                event_stamp, event = entry
                func_name, args = event
                next_state = ['[',
                 event_stamp,
                 ']',
                 func_name]
                if next_state != last_state:
                    if last_state is not None:
                        if last_state_count != 1:
                            last_state.append('(x %d)' % last_state_count)
                        logger.info(' '.join([ str(s) for s in last_state ]))
                    last_state = next_state
                    last_state_count = 1
                else:
                    last_state_count += 1

            if last_state is not None:
                if last_state_count != 1:
                    last_state.append('(x %d)' % last_state_count)
                logger.info(' '.join([ str(s) for s in last_state ]))
            logger.info(' ')

    def _report_update_if_bad(self, state):
        timestamps = {action[0] for action in state}
        if len(timestamps) > 1:
            logger.error('Found update batch with %s items and %s timestamps', len(state), len(timestamps))
            for action in state:
                logger.error('Action: %s', action)

            self._error_handler.on_fatal_desync()


def _expand_states(state):
    expanded_states = []
    for action in state:
        if action[1][0] == 'PackagedAction':
            try:
                unpackaged_actions = blue.marshal.Load(action[1][1])
                expanded_states.extend(unpackaged_actions)
            except StandardError:
                logger.exception('Exception whilst expanding a PackagedAction')
                sys.exc_clear()

        else:
            expanded_states.append(action)

    state = expanded_states
    return state
