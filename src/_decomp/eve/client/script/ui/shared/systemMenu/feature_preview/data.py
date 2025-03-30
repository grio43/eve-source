#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\feature_preview\data.py
import datetime
import signals
from eve.client.script.ui.shared.systemMenu.feature_preview.message_bus.featurePreviewMessenger import FeaturePreviewMessenger
from eveexceptions import EatsExceptions

class FeaturePreviewData(object):

    def __init__(self, id, title, description, banner, enabled_check, toggle, restart_check = None, prerequisites_check = None, links = None, new_until = None, disable_message = None):
        self.id = id
        self.title = title
        self.description = description
        self._enabled_check = enabled_check
        self._toggle = toggle
        self._restart_check = restart_check
        self._prerequisites_check = prerequisites_check
        self.banner = banner
        self.links = links or []
        self.new_until = new_until
        self.disable_message = disable_message
        self.on_toggle = signals.Signal()

    @property
    def is_enabled(self):
        return self._enabled_check()

    @property
    def is_new(self):
        return self.new_until is not None and datetime.datetime.utcnow().date() < self.new_until

    @property
    def requires_restart(self):
        if self._restart_check is not None:
            return self._restart_check()
        return False

    def toggle(self):
        self._toggle()
        self._log_toggled_event()
        self.on_toggle()

    def check_prerequisites(self):
        if self._prerequisites_check is not None:
            failures = self._prerequisites_check()
            if isinstance(failures, PrerequisiteFailure):
                return [failures]
            else:
                return failures or []

    @EatsExceptions('protoClientLogs')
    def _log_toggled_event(self):
        message_bus = FeaturePreviewMessenger(sm.GetService('publicGatewaySvc'))
        message_bus.feature_toggled(self.id, self.is_enabled)


class PrerequisiteFailure(object):

    def __init__(self, title, description):
        self.title = title
        self.description = description


def get_available_feature_previews():
    feature_previews = []
    return feature_previews
