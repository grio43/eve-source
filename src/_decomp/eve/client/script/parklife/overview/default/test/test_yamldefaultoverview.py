#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\default\test\test_yamldefaultoverview.py
from eve.client.script.parklife.overview.default.yamldefaultoverview import YamlDefaultOverview
import pytest

def _load_data(overview_id):
    overview = YamlDefaultOverview(overview_id, should_inform_of_update=False)
    overview._get_localized_name = lambda x: x
    overview._load_data()
    return overview


def _assert_has_any_presets(overview):
    result = overview.all_presets


def _assert_has_any_tabs(overview):
    result = overview.default_tabs


@pytest.mark.parametrize('data', ['old_default', 'jotunn_default'])
def test_loads_yaml_overview_data(data):
    overview = _load_data(data)
    _assert_has_any_presets(overview)
    _assert_has_any_tabs(overview)


if __name__ == '__main__':
    pytest.main(['-k', 'test_loads_yaml_overview_data'])
