#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\default\informer.py
import launchdarkly
from logging import getLogger
logger = getLogger(__name__)

class DefaultOverviewUpdateInformer(object):

    def __init__(self, settings, defaults, should_delay = lambda : False):
        self._settings = settings
        self._defaults = defaults
        self._should_delay = should_delay
        self._is_informing_enabled = None

    def is_informing_enabled(self):
        if self._is_informing_enabled is None:
            launchdarkly.get_client().notify_flag(flag_key='default-overview-offer-update', flag_fallback=False, callback=self._refresh_availability)
        return self._is_informing_enabled

    def _refresh_availability(self, ld_client, flag_key, flag_fallback, flag_deleted):
        self._is_informing_enabled = ld_client.get_bool_variation(feature_key=flag_key, fallback=flag_fallback)

    def update(self):
        self._log_debug('Checking whether to update')
        if not self._should_inform_of_update():
            return True
        if not self.is_informing_enabled():
            self._log_debug('Do not inform in this session, as informing is disabled')
            return True
        if self._should_delay():
            self._log_debug('Delay informing until NPE is completed (new character of existing user)')
            return False
        self._inform_of_update()
        self._settings.set_informed_of_update(True)
        self._log_debug('Informed of the latest Default')
        return True

    def _should_inform_of_update(self):
        default_overview = self._defaults.default_overview_id
        should_inform_of_update = self._defaults.should_inform_of_update()
        if not should_inform_of_update:
            self._log_debug('Do not inform, this Default Overview should not inform of updates (default: %s)' % default_overview)
            return False
        current_overview = self._settings.get_overview()
        if current_overview == default_overview:
            self._log_debug('Do not inform, player already has an unedited Default Overview (current: %s, default: %s)' % (current_overview, default_overview))
            return False
        has_informed_of_update = self._settings.get_informed_of_update()
        if has_informed_of_update:
            self._log_debug('Do not inform, player has already been informed before (current: %s, default: %s)' % (current_overview, default_overview))
            return False
        self._log_debug('Inform, player is existing user without the new Default Overview and has not been informed about the update yet (current: %s, default: %s)' % (current_overview, default_overview))
        return True

    def _inform_of_update(self):
        eve.Message('InformOfNewDefaultOverview')

    def _log_debug(self, text):
        settings_text = self._settings.get_settings_report()
        msg = 'Default Overview: {text}. \n{settings_text}'.format(text=text, settings_text=settings_text)
        logger.debug(msg)
