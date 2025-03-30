#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithmetrics\_datadog.py
import logging
import uthread2
from datadog import ThreadStats, initialize, api
from datadog.threadstats.metrics import MetricsAggregator
import ccpProfile
import monolithconfig
log = logging.getLogger('monolithmetrics._datadog')
constant_tags = ['prefs.clusterName:' + (monolithconfig.get_value('clusterName', 'prefs') or 'Unknown'),
 'boot.version:' + (monolithconfig.get_value('version', 'boot') or 'Unknown'),
 'boot.sync:' + (monolithconfig.get_value('sync', 'boot') or 'Unknown'),
 'boot.build:' + (monolithconfig.get_value('build', 'boot') or 'Unknown'),
 'boot.codename:' + (monolithconfig.get_value('codename', 'boot') or 'Unknown'),
 'boot.role:' + (monolithconfig.get_value('role', 'boot') or 'Unknown')]

class StacklessThreadStats(ThreadStats):

    def start(self, flush_interval = 10, roll_up_interval = 10, device = None, flush_in_thread = True, flush_in_greenlet = False, disabled = False):
        super(StacklessThreadStats, self).start(flush_interval=flush_interval, roll_up_interval=roll_up_interval, device=device, flush_in_thread=flush_in_thread, flush_in_greenlet=flush_in_greenlet, disabled=disabled)
        self._metric_aggregator = SafeMetricsAggregator(self.roll_up_interval)

    def set_credentials(self):
        api_key = monolithconfig.get_value('API_KEY', 'DataDog')
        app_key = monolithconfig.get_value('APP_KEY', 'DataDog')
        initialize(api_key=api_key, app_key=app_key)

    def _start_flush_greenlet(self):
        if self._is_auto_flushing:
            log.info('Autoflushing already started.')
            return
        self._is_auto_flushing = True

        def flush():
            while True:
                with ccpProfile.Timer(__name__ + '::flush'):
                    try:
                        if api._api_key and api._application_key:
                            log.debug('Flushing metrics in tasklet')
                            self.flush()
                    except:
                        try:
                            log.exception('Error flushing in tasklet')
                        except:
                            pass

                uthread2.sleep(self.flush_interval)

        log.info('Starting flush tasklet with interval %s.' % self.flush_interval)
        uthread2.StartTasklet(flush)


class SafeMetricsAggregator(MetricsAggregator):

    def flush(self, timestamp):
        interval = timestamp - timestamp % self._roll_up_interval
        past_intervals = [ i for i in self._metrics.keys() if i < interval ]
        metrics = []
        for i in past_intervals:
            for m in list(self._metrics.pop(i).values()):
                try:
                    metrics += m.flush(i)
                except Exception as e:
                    log.exception('Bad metric in batch')

        return metrics


if not monolithconfig.on_client():
    client = StacklessThreadStats(namespace='eve', constant_tags=constant_tags)
    client.start(flush_interval=10, flush_in_greenlet=True, roll_up_interval=10)
    monolithconfig.add_watch_group_callback(client.set_credentials, 'DataDog')
