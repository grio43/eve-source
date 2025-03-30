#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\test\basetestpresetservice.py
from copy import deepcopy
from eve.client.script.parklife.overview.test.defaultoverview import DefaultOverviewDataMock
from itertoolsext import Bundle
from mock import Mock, patch
from testhelpers.evemocks import SMMock
from testsuites.testcases import ClientTestCase

class ServiceMock(object):

    def Run(self, *args):
        pass


class SettingsMock(Mock):

    def __init__(self, *args, **kwargs):
        super(SettingsMock, self).__init__(*args, **kwargs)
        self.settings = {}

    def Get(self, key, default = None):
        return self.settings.get(key, default)

    def Set(self, key, value):
        self.settings[key] = deepcopy(value)

    def Delete(self, key):
        del self.settings[key]


class UninitializedOverviewPresetsBaseTest(ClientTestCase):

    def _mock_globals(self):
        self.settings = SettingsMock()
        user_settings_mock = Mock()
        user_settings_mock.overview = self.settings
        settings_mock = Mock()
        settings_mock.user = user_settings_mock
        import __builtin__
        __builtin__.settings = settings_mock
        __builtin__.sm = SMMock()

    def _mock_imported_modules(self):
        service_mock = Mock()
        service_mock.Service = ServiceMock
        fsd_default_overview_mock = Mock()
        fsd_default_overview_mock.FsdDefaultOverview = DefaultOverviewDataMock
        yaml_default_overview_mock = Mock()
        yaml_default_overview_mock.YamlDefaultOverview = DefaultOverviewDataMock
        return {'carbon.common.script.sys.service': service_mock,
         'carbonui': Mock(),
         'carbonui.const': Bundle(ID_YES=1, YESNO=2),
         'carbonui.util': Mock(),
         'carbonui.util.color': Mock(),
         'eve.client.script.ui.inflight.overview.beta': Mock(),
         'eve.client.script.parklife.overview.blocker': Mock(),
         'eve.client.script.ui.inflight.overview.overviewWindow': Mock(),
         'eve.client.script.ui.inflight.overviewWindowOld': Mock(),
         'eve.client.script.ui.beta': Mock(),
         'eve.common.script.sys': Mock(),
         'eve.common.script.sys.idCheckers': Mock(),
         'eve.client.script.parklife.overview.default.fsddefaultoverview': fsd_default_overview_mock,
         'eve.client.script.parklife.overview.default.yamldefaultoverview': yaml_default_overview_mock,
         'localization': Mock(),
         'storylines.client.airnpe': Mock()}

    def setUp(self):
        super(UninitializedOverviewPresetsBaseTest, self).setUp()
        self._mock_globals()
        with patch.dict('sys.modules', self._mock_imported_modules()):
            from eve.client.script.parklife.overview.presetservice import OverviewPresetSvc
            self.overview_service = OverviewPresetSvc()
            self.overview_service._Setup()

    def test_can_run_service(self):
        self.overview_service.Run()


class OverviewPresetsBaseTest(UninitializedOverviewPresetsBaseTest):

    def setUp(self):
        super(OverviewPresetsBaseTest, self).setUp()
        self._mock_globals()
        with patch.dict('sys.modules', self._mock_imported_modules()):
            from eve.client.script.parklife.overview.presetservice import OverviewPresetSvc
            self.overview_service = OverviewPresetSvc()
            self.overview_service.Run()
