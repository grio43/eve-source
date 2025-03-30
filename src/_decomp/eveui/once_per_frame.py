#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\once_per_frame.py
import functools
import logging
import trinity
import uthread2
logger = logging.getLogger(__name__)

def throttle_once_per_frame(func):
    func._last_call_args = None
    func._throttle_thread = None

    def throttle_thread():
        try:
            wait_for_next_frame()
            while func._last_call_args is not None:
                args, kwargs = func._last_call_args
                func._last_call_args = None
                func(*args, **kwargs)
                wait_for_next_frame()

        finally:
            func._throttle_thread = None

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if func._throttle_thread is None:
            func._last_call_args = None
            func(*args, **kwargs)
            func._throttle_thread = uthread2.start_tasklet(throttle_thread)
        else:
            func._last_call_args = (args, kwargs)

    return wrapper


def wait_for_next_frame():
    channel = uthread2.queue_channel()

    def on_next_frame():
        channel.send(None)
        return True

    scheduler.schedule(on_next_frame)
    channel.receive()


def call_next_frame(func):

    def tasklet():
        wait_for_next_frame()
        func()

    uthread2.start_tasklet(tasklet)


class FrameScheduler(object):

    def __init__(self):
        self._callbacks = {}
        self._job = trinity.CreateRenderJob('eveui_callbacks')
        self._job.PythonCB(self._pump)
        self._pending_add = []
        self._pending_remove = []
        self._next_cookie = 1

    def __del__(self, *args):
        if self._job:
            self._job.UnscheduleRecurring()

    def schedule(self, callback):
        cookie = self._next_cookie
        self._next_cookie += 1
        self._pending_add.append((cookie, callback))
        if not self._is_running:
            self._job.ScheduleRecurring()
        return cookie

    def unschedule(self, cookie):
        self._pending_remove.append(cookie)

    @property
    def _is_running(self):
        return self._job in trinity.renderJobs.recurring

    def _pump(self):
        try:
            self._process_pending_add()
            for cookie, callback in self._callbacks.iteritems():
                should_unschedule = True
                try:
                    should_unschedule = callback()
                except Exception:
                    logger.exception('Failed to execute a once-per-frame callback')

                if should_unschedule:
                    self._pending_remove.append(cookie)

            self._process_pending_remove()
            self._stop_if_no_callbacks()
        except Exception:
            logger.exception('FrameScheduler pump failed!')

    def _process_pending_add(self):
        for cookie, callback in self._pending_add:
            self._callbacks[cookie] = callback

        self._pending_add = []

    def _process_pending_remove(self):
        for cookie in self._pending_remove:
            try:
                del self._callbacks[cookie]
            except Exception:
                pass

        self._pending_remove = []

    def _stop_if_no_callbacks(self):
        if not self._callbacks and not self._pending_add:
            self._job.UnscheduleRecurring()


scheduler = FrameScheduler()
