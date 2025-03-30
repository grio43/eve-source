#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\storylines\client\metrics.py
import launchdarkly
from logging import getLogger
from storylines.common.airnpeconstants import AirNpeState
logger = getLogger(__name__)
METRIC_BY_STATE = {AirNpeState.COMPLETED: 'Tutorial Completed',
 AirNpeState.SKIPPED: 'Tutorial Skipped'}

def send_metric(air_npe_state):
    if air_npe_state in METRIC_BY_STATE:
        metric = METRIC_BY_STATE[air_npe_state]
        try:
            client = launchdarkly.get_client()
            client.track(metric)
            logger.info('Sent AIR NPE metric to LaunchDarkly: %s', metric)
        except Exception as exc:
            logger.exception('Failed to send AIR NPE metric to LaunchDarkly: %s', exc)
