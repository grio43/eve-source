#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\default\test\test_informer.py
from itertoolsext import Bundle
from mock import Mock, patch
from unittest import main
from testsuites.testcases import ClientTestCase
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
SHOULD_DISPLAY_LOGS = False

class OverviewSettings(object):

    def __init__(self):
        self.overviewID = None
        self.defaultOverviewID = None
        self.defaultOverviewInformedOfUpdate = 0

    def set_overview(self, overview_id):
        self.overviewID = overview_id

    def set_default_overview(self, default_id):
        self.defaultOverviewID = default_id

    def set_informed_of_update(self, switch_offered):
        self.defaultOverviewInformedOfUpdate = int(switch_offered)

    def get_overview(self):
        return self.overviewID

    def get_default_overview(self):
        return self.defaultOverviewID

    def get_informed_of_update(self):
        return self.defaultOverviewInformedOfUpdate


class DefaultOverviews(object):

    def __init__(self):
        self.default_overview_id = None
        self._should_inform_of_update = None

    def should_inform_of_update(self):
        return self._should_inform_of_update

    def set_default_overview(self, overview_id):
        self.default_overview_id = overview_id

    def set_should_inform_of_update(self, should_inform_of_update):
        self._should_inform_of_update = should_inform_of_update


class UpdaterTestCase(ClientTestCase):

    def _mock_imported_modules(self):
        self.defaults = DefaultOverviews()
        self.settings = OverviewSettings()
        return {'carbonui': Mock(),
         'carbonui.const': Bundle(ID_YES=1, YESNO=2)}

    def setUp(self):
        super(UpdaterTestCase, self).setUp()
        with patch.dict('sys.modules', self._mock_imported_modules()):
            from eve.client.script.parklife.overview.default.informer import DefaultOverviewUpdateInformer
            self._should_delay = lambda : False
            self.updater = DefaultOverviewUpdateInformer(settings=self.settings, defaults=self.defaults, should_delay=self._should_delay)
            self.updater.is_informing_enabled = Mock(return_value=True)
            if SHOULD_DISPLAY_LOGS:
                self.updater._log_debug = lambda text: logger.info(text)
            else:
                self.updater._log_debug = Mock()

    def _check_has_informed_in_settings(self):
        self.assertEqual(self.settings.get_informed_of_update(), 1)

    def _check_has_not_informed_in_settings(self):
        self.assertEqual(self.settings.get_informed_of_update(), 0)

    def test_inform_when_player_is_existing_user_without_default_who_has_never_been_informed(self):
        self.defaults.set_default_overview('new_default')
        self.defaults.set_should_inform_of_update(True)
        self.settings.set_overview('old_default')
        self.settings.set_informed_of_update(False)
        self.updater._inform_of_update = Mock()
        self.assertTrue(self.updater._should_inform_of_update())
        is_done = self.updater.update()
        self.assertTrue(self.updater._inform_of_update.called)
        self.assertTrue(is_done)
        self._check_has_informed_in_settings()

    def test_delay_informing_when_player_is_existing_user_without_default_who_has_never_been_informed_but_in_npe(self):
        self.defaults.set_default_overview('new_default')
        self.defaults.set_should_inform_of_update(True)
        self.settings.set_overview('old_default')
        self.settings.set_informed_of_update(False)
        self.updater._inform_of_update = Mock()
        self.updater._should_delay = Mock(return_value=True)
        self.assertTrue(self.updater._should_inform_of_update())
        is_done = self.updater.update()
        self.assertFalse(self.updater._inform_of_update.called)
        self.assertFalse(is_done)
        self._check_has_not_informed_in_settings()

    def test_do_nothing_when_player_already_has_the_latest_default(self):
        self.defaults.set_default_overview('new_default')
        self.defaults.set_should_inform_of_update(True)
        self.settings.set_overview('new_default')
        self.settings.set_informed_of_update(True)
        self.updater._inform_of_update = Mock()
        self.assertFalse(self.updater._should_inform_of_update())
        is_done = self.updater.update()
        self.assertFalse(self.updater._inform_of_update.called)
        self.assertTrue(is_done)

    def test_do_nothing_when_player_already_has_the_latest_default_even_if_he_has_never_been_informed(self):
        self.defaults.set_default_overview('new_default')
        self.defaults.set_should_inform_of_update(True)
        self.settings.set_overview('new_default')
        self.settings.set_informed_of_update(False)
        self.updater._inform_of_update = Mock()
        self.assertFalse(self.updater._should_inform_of_update())
        is_done = self.updater.update()
        self.assertFalse(self.updater._inform_of_update.called)
        self.assertTrue(is_done)

    def test_do_nothing_when_this_overview_does_not_require_informing(self):
        self.defaults.set_default_overview('new_default')
        self.defaults.set_should_inform_of_update(False)
        self.settings.set_overview('old_default')
        self.settings.set_informed_of_update(False)
        self.updater._inform_of_update = Mock()
        self.assertFalse(self.updater._should_inform_of_update())
        is_done = self.updater.update()
        self.assertFalse(self.updater._inform_of_update.called)
        self.assertTrue(is_done)

    def test_do_nothing_when_informing_is_disabled(self):
        self.defaults.set_default_overview('new_default')
        self.defaults.set_should_inform_of_update(False)
        self.settings.set_overview('old_default')
        self.settings.set_informed_of_update(False)
        self.updater._is_informing_enabled = False
        self.updater._inform_of_update = Mock()
        is_done = self.updater.update()
        self.assertFalse(self.updater._inform_of_update.called)
        self.assertTrue(is_done)


if __name__ == '__main__':
    main()
