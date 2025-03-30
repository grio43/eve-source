#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\card.py
import eveui
from eve.client.script.ui import eveThemeColor
import carbonui
import threadutils
from jobboard.client.ui.info_panel_entry import JobInfoPanelEntry
from jobboard.client.ui.card import JobCard
from jobboard.client.ui.list_entry import JobListEntry

class DungeonCard(JobCard):

    def _update_state(self):
        self._update_top_title()
        state_info = self.job.get_state_info()
        if not state_info:
            self._state_container.display = False
            self._left_line.rgb = eveThemeColor.THEME_FOCUS[:3]
            return
        self._left_line.rgb = state_info['color'][:3]
        self._state_icon.texturePath = state_info['icon']
        self._state_icon.color = state_info['color']
        self._state_icon.hint = state_info['text']
        self._state_container.display = True

    def _construct_state_container(self):
        self._state_container = eveui.Container(name='state_container', parent=self._top_right_container, display=False, align=eveui.Align.to_right, width=50)
        self._state_icon = eveui.Sprite(name='icon', parent=self._state_container, state=eveui.State.normal, align=eveui.Align.center, width=16, height=16, outputMode=carbonui.uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.3)
        self._state_icon.OnClick = self.OnClick
        self._state_icon.GetMenu = self.GetMenu
        self._state_icon.GetDragData = self.GetDragData
        self._state_icon.PrepareDrag = self.PrepareDrag

    def _construct_top_right(self):
        self._construct_state_container()

    @threadutils.threaded
    def _construct_bottom_content(self):
        self._construct_subtitle(_get_dungeon_subtitle(self.job))


class DungeonListEntry(JobListEntry):

    @threadutils.threaded
    def _construct_right_content(self, parent):
        self._construct_subtitle(parent, _get_dungeon_subtitle(self.job))


class DungeonInfoPanelEntry(JobInfoPanelEntry):

    def _on_job_updated(self):
        super(DungeonInfoPanelEntry, self)._on_job_updated()
        self._title.text = self._get_title()

    def _get_title(self):
        scan_result_id = self.job.scan_result_id
        if scan_result_id and self.job.in_same_system:
            return u'<color={}>[{}]</color> {}'.format(carbonui.TextColor.NORMAL, scan_result_id, self.job.title)
        return self.job.title


def _get_dungeon_subtitle(job):
    subtitle = job.subtitle
    scan_result_id = job.scan_result_id
    if scan_result_id and job.in_same_system:
        return u'[{}] {}'.format(scan_result_id, subtitle)
    return subtitle
