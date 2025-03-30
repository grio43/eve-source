#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\launch_darkly.py
import logging
import launchdarkly
from .base import Condition
MAX_TRIES = 5
logger = logging.getLogger(__name__)

class LaunchDarklyBooleanCheck(Condition):
    atom_id = 478

    def __init__(self, launch_darkly_key = None, default_value = None, **kwargs):
        super(LaunchDarklyBooleanCheck, self).__init__(**kwargs)
        self.value = self.get_atom_parameter_value('default_value', default_value)
        launchdarkly.get_client().notify_flag(launch_darkly_key, self.value, self._refresh_flag)

    def _refresh_flag(self, ld_client, flag_key, flag_fallback, flag_deleted):
        self.value = ld_client.get_bool_variation(feature_key=flag_key, fallback=flag_fallback)

    def validate(self, **kwargs):
        return self.value

    @classmethod
    def get_subtitle(cls, launch_darkly_key, **kwargs):
        return unicode(launch_darkly_key)
