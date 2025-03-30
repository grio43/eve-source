#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\threadutils\scheduler.py
import heapq
import logging
import random
from collections import namedtuple
import gametime
import uthread2
from carbon.common.lib.const import SEC
from eveexceptions.exceptionEater import ExceptionEater
logger = logging.getLogger(__name__)
__all__ = ['Scheduler', 'SimTimeScheduler', 'WallTimeScheduler']
Event = namedtuple('Event', 'time, priority, action, arguments')

class Scheduler(object):

    def __init__(self, time_func = None, delay_func = None, name = 'default'):
        self._queue = []
        self.time_func = time_func
        self.delay_func = delay_func
        self.is_running = False
        self.is_delaying = None
        self.is_active = False
        self.is_executing_event = False
        self._name = name

    def enter_absolute_event(self, time, priority, action, arguments):
        event = Event(time, priority, action, arguments)
        self._before_enter_event(event)
        heapq.heappush(self._queue, event)
        logger.debug('scheduler %s adding event %s', self._name, event)
        self._after_enter_event()
        return event

    def enter_relative_event(self, delay, priority, action, arguments):
        time = self.time_func() + delay
        return self.enter_absolute_event(time, priority, action, arguments)

    def cancel(self, event):
        self._queue.remove(event)
        heapq.heapify(self._queue)
        logger.debug('scheduler %s cancelled event %s', self._name, event)

    def empty(self):
        return not self._queue

    def run(self):
        try:
            queue = self._queue
            time_func = self.time_func
            pop = heapq.heappop
            self.is_running = True
            while queue:
                next_event = self.next_event()
                now = time_func()
                if now < next_event.time:
                    self.delay(next_event.time - now)
                else:
                    event = pop(queue)
                    if event is next_event:
                        self.is_executing_event = True
                        self.try_execute_event(event, next_event)
                        self.is_executing_event = False
                        self.delay(0)
                    else:
                        heapq.heappush(queue, event)

        finally:
            self.is_running = False

    def try_execute_event(self, event, next_event):
        logger.debug('%s: executing event %s', self._name, event)
        with ExceptionEater('scheduler %s' % self._name):
            next_event.action(*next_event.arguments)

    @property
    def queue(self):
        events = self._queue[:]
        return map(heapq.heappop, [events] * len(events))

    def clear_all_events(self):
        while self._queue:
            self._queue.pop()

        logger.debug('scheduler %s cleared all events', self._name)

    def cancel_by_action_and_arguments(self, action, arguments):
        action_name = action.__name__
        events = [ e for e in self._queue if e.action.__name__ == action_name and e.arguments == arguments ]
        for e in events:
            self.cancel(e)

        logger.debug('scheduler %s cancelled all event named %s with arguments %s', self._name, action_name, arguments)

    def enter_random_interval_event(self, min_delay, max_delay, priority, action, arguments):
        delay = random.randint(min_delay, max_delay)
        return self.enter_relative_event(delay, priority, action, arguments)

    def enter_repeated_interval_event(self, min_delay, max_delay, priority, action, arguments):
        repeated_arguments = (min_delay,
         max_delay,
         priority,
         action,
         arguments)
        return self.enter_random_interval_event(min_delay, max_delay, priority, self._do_event_and_repeat, repeated_arguments)

    def _do_event_and_repeat(self, min_delay, max_delay, priority, action, arguments):
        repeated_arguments = (min_delay,
         max_delay,
         priority,
         action,
         arguments)
        if action(*arguments):
            self.enter_random_interval_event(min_delay, max_delay, priority, self._do_event_and_repeat, repeated_arguments)

    def delay(self, time):
        self.is_delaying = True
        try:
            self.delay_func(time)
        finally:
            self.is_delaying = False

    def start(self):
        self.is_active = True
        if self.queue:
            self._start_worker()

    def _start_worker(self):
        self.worker_thread = uthread2.start_tasklet(self.run)

    def _stop_worker(self):
        if self.worker_thread is None:
            return
        self.worker_thread.kill()
        self.worker_thread = None

    def stop(self):
        self.is_active = False
        self._stop_worker()

    def next_event(self):
        return self.queue[0]

    def _after_enter_event(self):
        if self.is_active and not self.is_running:
            self._start_worker()

    def _before_enter_event(self, new_event):
        if self.is_executing_event:
            return
        if not self.is_active:
            return
        if not self.is_running:
            return
        if not self.is_delaying:
            return
        if not self.empty() and new_event.time < self.next_event().time:
            self._stop_worker()


def sleep_sim_time(blue_time):
    time_seconds = blue_time / float(SEC)
    uthread2.sleep_sim(time_seconds)


class SimTimeScheduler(Scheduler):

    def __init__(self, name = 'sim_time_scheduler'):
        Scheduler.__init__(self, time_func=gametime.GetSimTime, delay_func=sleep_sim_time, name=name)


def sleep_wall_time(blue_time):
    time_seconds = blue_time / float(SEC)
    uthread2.sleep(time_seconds)


class WallTimeScheduler(Scheduler):

    def __init__(self, name = 'wall_time_scheduler'):
        Scheduler.__init__(self, time_func=gametime.GetWallclockTime, delay_func=sleep_wall_time, name=name)
