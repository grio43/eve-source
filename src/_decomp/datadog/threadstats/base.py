#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\threadstats\base.py
import logging
import os
from functools import wraps
from contextlib import contextmanager
from time import time
from datadog.api.exceptions import ApiNotInitialized
from datadog.threadstats.constants import MetricType
from datadog.threadstats.metrics import MetricsAggregator, Counter, Gauge, Histogram, Timing
from datadog.threadstats.events import EventsAggregator
from datadog.threadstats.reporters import HttpReporter
log = logging.getLogger('datadog.threadstats')

class ThreadStats(object):

    def __init__(self, namespace = '', constant_tags = None):
        self.namespace = namespace
        env_tags = [ tag for tag in os.environ.get('DATADOG_TAGS', '').split(',') if tag ]
        if constant_tags is None:
            constant_tags = []
        self.constant_tags = constant_tags + env_tags
        self._disabled = True

    def start(self, flush_interval = 10, roll_up_interval = 10, device = None, flush_in_thread = True, flush_in_greenlet = False, disabled = False):
        self.flush_interval = flush_interval
        self.roll_up_interval = roll_up_interval
        self.device = device
        self._disabled = disabled
        self._is_auto_flushing = False
        self._metric_aggregator = MetricsAggregator(self.roll_up_interval)
        self._event_aggregator = EventsAggregator()
        self.reporter = HttpReporter()
        self._is_flush_in_progress = False
        self.flush_count = 0
        if self._disabled:
            log.info('ThreadStats instance is disabled. No metrics will flush.')
        elif flush_in_greenlet:
            self._start_flush_greenlet()
        elif flush_in_thread:
            self._start_flush_thread()

    def stop(self):
        if not self._is_auto_flushing:
            return True
        if self._flush_thread:
            self._flush_thread.end()
            self._is_auto_flushing = False
            return True

    def event(self, title, text, alert_type = None, aggregation_key = None, source_type_name = None, date_happened = None, priority = None, tags = None, hostname = None):
        if not self._disabled:
            event_tags = tags
            if self.constant_tags:
                if tags:
                    event_tags = tags + self.constant_tags
                else:
                    event_tags = self.constant_tags
            self._event_aggregator.add_event(title=title, text=text, alert_type=alert_type, aggregation_key=aggregation_key, source_type_name=source_type_name, date_happened=date_happened, priority=priority, tags=event_tags, host=hostname)

    def gauge(self, metric_name, value, timestamp = None, tags = None, sample_rate = 1, host = None):
        if not self._disabled:
            self._metric_aggregator.add_point(metric_name, tags, timestamp or time(), value, Gauge, sample_rate=sample_rate, host=host)

    def increment(self, metric_name, value = 1, timestamp = None, tags = None, sample_rate = 1, host = None):
        if not self._disabled:
            self._metric_aggregator.add_point(metric_name, tags, timestamp or time(), value, Counter, sample_rate=sample_rate, host=host)

    def decrement(self, metric_name, value = 1, timestamp = None, tags = None, sample_rate = 1, host = None):
        if not self._disabled:
            self._metric_aggregator.add_point(metric_name, tags, timestamp or time(), -value, Counter, sample_rate=sample_rate, host=host)

    def histogram(self, metric_name, value, timestamp = None, tags = None, sample_rate = 1, host = None):
        if not self._disabled:
            self._metric_aggregator.add_point(metric_name, tags, timestamp or time(), value, Histogram, sample_rate=sample_rate, host=host)

    def timing(self, metric_name, value, timestamp = None, tags = None, sample_rate = 1, host = None):
        if not self._disabled:
            self._metric_aggregator.add_point(metric_name, tags, timestamp or time(), value, Timing, sample_rate=sample_rate, host=host)

    @contextmanager
    def timer(self, metric_name, sample_rate = 1, tags = None, host = None):
        start = time()
        try:
            yield
        finally:
            end = time()
            self.timing(metric_name, end - start, end, tags=tags, sample_rate=sample_rate, host=host)

    def timed(self, metric_name, sample_rate = 1, tags = None, host = None):

        def wrapper(func):

            @wraps(func)
            def wrapped(*args, **kwargs):
                with self.timer(metric_name, sample_rate, tags, host):
                    result = func(*args, **kwargs)
                    return result

            return wrapped

        return wrapper

    def flush(self, timestamp = None):
        try:
            if self._is_flush_in_progress:
                log.debug('A flush is already in progress. Skipping this one.')
                return False
            if self._disabled:
                log.info("Not flushing because we're disabled.")
                return False
            self._is_flush_in_progress = True
            metrics = self._get_aggregate_metrics(timestamp or time())
            count_metrics = len(metrics)
            if count_metrics:
                self.flush_count += 1
                log.debug('Flush #%s sending %s metrics' % (self.flush_count, count_metrics))
                self.reporter.flush_metrics(metrics)
            else:
                log.debug('No metrics to flush. Continuing.')
            events = self._get_aggregate_events()
            count_events = len(events)
            if count_events:
                self.flush_count += 1
                log.debug('Flush #%s sending %s events' % (self.flush_count, count_events))
                self.reporter.flush_events(events)
            else:
                log.debug('No events to flush. Continuing.')
        except ApiNotInitialized:
            raise
        except:
            try:
                log.exception('Error flushing metrics and events')
            except:
                pass

        finally:
            self._is_flush_in_progress = False

    def _get_aggregate_metrics(self, flush_time = None):
        rolled_up_metrics = self._metric_aggregator.flush(flush_time)
        metrics = []
        for timestamp, value, name, tags, host in rolled_up_metrics:
            metric_tags = tags
            metric_name = name
            if self.constant_tags:
                if tags:
                    metric_tags = tags + self.constant_tags
                else:
                    metric_tags = self.constant_tags
            if self.namespace:
                metric_name = self.namespace + '.' + name
            metric = {'metric': metric_name,
             'points': [[timestamp, value]],
             'type': MetricType.Gauge,
             'host': host,
             'device': self.device,
             'tags': metric_tags}
            metrics.append(metric)

        return metrics

    def _get_aggregate_events(self):
        events = self._event_aggregator.flush()
        return events

    def _start_flush_thread(self):
        from datadog.threadstats.periodic_timer import PeriodicTimer
        if self._is_auto_flushing:
            log.info('Autoflushing already started.')
            return
        self._is_auto_flushing = True

        def flush():
            try:
                log.debug('Flushing metrics in thread')
                self.flush()
            except:
                try:
                    log.exception('Error flushing in thread')
                except:
                    pass

        log.info('Starting flush thread with interval %s.' % self.flush_interval)
        self._flush_thread = PeriodicTimer(self.flush_interval, flush)
        self._flush_thread.start()

    def _start_flush_greenlet(self):
        if self._is_auto_flushing:
            log.info('Autoflushing already started.')
            return
        self._is_auto_flushing = True
        import gevent

        def flush():
            while True:
                try:
                    log.debug('Flushing metrics in greenlet')
                    self.flush()
                    gevent.sleep(self.flush_interval)
                except:
                    try:
                        log.exception('Error flushing in greenlet')
                    except:
                        pass

        log.info('Starting flush greenlet with interval %s.' % self.flush_interval)
        gevent.spawn(flush)
