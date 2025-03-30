#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\default\fsddefaultoverview.py
import characterdata.defaultOverviews as overviewData
from eve.client.script.parklife.overview.default.defaultoverview import BaseDefaultOverview, PresetData, TabData

class FsdDefaultOverview(BaseDefaultOverview):

    def _do_load(self):
        all_overviews = overviewData.get_all_overviews()
        self._all_presets = {}
        for overview in all_overviews:
            overview_id = overview['default_overview_id']
            data = PresetData(name=overviewData.get_default_overview_name(overview_id), short_name=overview['overview_short_name'], name_id=overview['overview_name_id'], groups=[ groupID for groupID in overviewData.get_default_overview_groups(overview_id) ])
            self._all_presets[data.short_name] = data

        self._sorted_preset_names = [ overview['overview_short_name'] for overview in sorted(all_overviews, key=lambda k: overviewData.get_default_overview_name(k['default_overview_id'])) ]
        self._default_preset = overviewData.get_default_preset()
        self._default_tabs = {}
        for tab_id, data in overviewData.get_default_tabs().iteritems():
            self._default_tabs[tab_id] = TabData(name=data['name'], color=data['color'], overview_preset=data['overviewPreset'], bracket_preset=data['bracketPreset'])
