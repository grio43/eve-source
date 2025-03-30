#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\default\test\test_fsddefaultoverview.py
from mock import patch, MagicMock
from unittest import main
from eve.client.script.parklife.overview.test.defaultoverview import DEFAULT_OVERVIEW_IN_FSD, DEFAULT_OVERVIEW, DEFAULT_OVERVIEW_PRESET, DEFAULT_OVERVIEW_PRESET_NAMES_SORTED, DEFAULT_TABS_IN_FSD, DEFAULT_OVERVIEW_TABS
from testsuites.testcases import ClientTestCase

def mock_get_all_overviews():
    return DEFAULT_OVERVIEW_IN_FSD


def mock_get_default_overview_name(default_overview_id):
    for overview in DEFAULT_OVERVIEW_IN_FSD:
        if overview['default_overview_id'] == default_overview_id:
            return 'Localized message %s' % overview['overview_name_id']

    return ''


def mock_get_default_overview_groups(default_overview_id):
    for overview in DEFAULT_OVERVIEW_IN_FSD:
        if overview['default_overview_id'] == default_overview_id:
            return overview['default_overview_groups']

    return []


def mock_get_default_preset():
    return DEFAULT_OVERVIEW_PRESET


def mock_get_default_tabs():
    return DEFAULT_TABS_IN_FSD


class FsdDefaultOverviewTest(ClientTestCase):

    def setUp(self):
        super(FsdDefaultOverviewTest, self).setUp()
        from eve.client.script.parklife.overview.default.fsddefaultoverview import FsdDefaultOverview
        self.overview = FsdDefaultOverview(should_inform_of_update=False)

    @patch('eve.client.script.parklife.overview.default.fsddefaultoverview.overviewData.get_all_overviews', MagicMock(side_effect=mock_get_all_overviews))
    @patch('eve.client.script.parklife.overview.default.fsddefaultoverview.overviewData.get_default_overview_name', MagicMock(side_effect=mock_get_default_overview_name))
    @patch('eve.client.script.parklife.overview.default.fsddefaultoverview.overviewData.get_default_overview_groups', MagicMock(side_effect=mock_get_default_overview_groups))
    @patch('eve.client.script.parklife.overview.default.fsddefaultoverview.overviewData.get_default_preset', MagicMock(side_effect=mock_get_default_preset))
    @patch('eve.client.script.parklife.overview.default.fsddefaultoverview.overviewData.get_default_tabs', MagicMock(side_effect=mock_get_default_tabs))
    def test_loads_data(self):
        self.assertDictEqual(self.overview.all_presets, DEFAULT_OVERVIEW)
        self.assertEqual(self.overview.default_preset, DEFAULT_OVERVIEW_PRESET)
        self.assertEqual(self.overview.default_tabs, DEFAULT_OVERVIEW_TABS)
        self.assertEqual(self.overview.sorted_preset_names, DEFAULT_OVERVIEW_PRESET_NAMES_SORTED)


if __name__ == '__main__':
    main()
