#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\launch_darkly.py
import launchdarkly
from logging import getLogger
from nodegraph.client.actions.base import Action
logger = getLogger(__name__)

class TrackMetric(Action):
    atom_id = 520

    def __init__(self, metric_id = None, **kwargs):
        super(TrackMetric, self).__init__(**kwargs)
        self.metric_id = metric_id

    def start(self, **kwargs):
        super(TrackMetric, self).start(**kwargs)
        if self.metric_id:
            try:
                client = launchdarkly.get_client()
                client.track(self.metric_id)
                logger.info('Sent Node Graph metric to LaunchDarkly: %s', self.metric_id)
            except Exception as exc:
                logger.exception('Failed to send Node Graph metric to LaunchDarkly: %s', exc)

    @classmethod
    def get_subtitle(cls, metric_id = '', **kwargs):
        return u'{}'.format(metric_id or '')
