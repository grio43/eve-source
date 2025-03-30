#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelJobBoard.py
import logging
import blue
import eveui
import eveicon
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.infoPanels.const.infoPanelConst import PANEL_JOB_BOARD, MODE_NORMAL
from carbonui.control.buttonIcon import ButtonIcon
import uthread2
from jobboard.client import get_job_board_service, job_board_signals
import localization
from carbonui.services.setting import SessionSettingNumeric
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
logger = logging.getLogger('job_board')
SCROLL_CONTAINER_HEIGHT_MAX = 450

class InfoPanelJobBoard(InfoPanelBase):
    default_name = 'InfoPanelJobBoard'
    panelTypeID = PANEL_JOB_BOARD
    hasSettings = False
    uniqueUiName = pConst.UNIQUE_NAME_AGENT_MISSION_INFO_PANEL
    label = 'UI/Opportunities/WindowTitle'
    default_iconTexturePath = eveicon.opportunities_board
    expandedJobSettingsName = 'expanded_job'
    featureID = 'opportunities'
    __notifyevents__ = InfoPanelBase.__notifyevents__ + ['OnExpandedMissionChanged']
    _scroll_fraction = SessionSettingNumeric(0, 0.0, 1.0)

    @staticmethod
    def IsAvailable():
        service = get_job_board_service()
        return service.is_available and bool(service.get_tracked_jobs())

    def __init__(self, **kwargs):
        self._expanded_job_id = None
        self._job_entries = {}
        self._scroll_initialized = False
        self._constructing = True
        super(InfoPanelJobBoard, self).__init__(**kwargs)
        self._layout()
        self._refresh_entries()
        self._update_content_container_scroll_position()
        job_board_signals.on_job_state_changed.connect(self._on_job_state_changed)

    def Close(self):
        for entry in self._job_entries.values():
            entry.Close()

        self._job_entries.clear()
        job_board_signals.on_job_state_changed.disconnect(self._on_job_state_changed)
        super(InfoPanelJobBoard, self).Close()

    def ConstructNormal(self):
        if self._constructing or self.destroyed:
            return
        self._debounced_refresh()

    @property
    def service(self):
        return get_job_board_service()

    def _on_tracked_jobs_changed(self):
        if self.destroyed:
            return
        self._debounced_refresh()

    @uthread2.debounce(0.1)
    def _debounced_refresh(self):
        if not self.destroyed:
            self._refresh_entries()

    def _on_job_state_changed(self, job):
        if self.destroyed:
            return
        if job.job_id in self._job_entries:
            self._job_entries[job.job_id].update_state()

    @eveui.skip_if_destroyed
    def _refresh_entries(self):
        jobs = self.service.get_tracked_jobs()
        job_ids = [ job.job_id for job in jobs ]
        previous_job_ids = [ job_id for job_id in self._job_entries.keys() ]
        obsolete_job_ids = list(set(previous_job_ids) - set(job_ids))
        for job_id in obsolete_job_ids:
            job_entry = self._job_entries[job_id]
            job_entry.Close()
            self._job_entries[job_id] = None
            self._job_entries.pop(job_id)

        for index, job in enumerate(jobs):
            if job.job_id not in previous_job_ids:
                self._construct_job_entry(job, index)
            else:
                self._job_entries[job.job_id].SetOrder(index)

        if not self._job_entries:
            self._save_expanded(-1)
        else:
            self._check_update_expanded()
        self._update_content_container_height()

    @eveui.skip_if_destroyed
    def _construct_job_entry(self, job, index):
        try:
            entry = job.INFO_PANEL_ENTRY_CLASS(parent=self._content_container, job=job, padBottom=4, padTop=4, on_click=self._on_entry_clicked, idx=index, callback=self._update_content_container_height)
            self._job_entries[job.job_id] = entry
        except:
            logger.exception('Failed to construct info panel entry %s', job.job_id)

    def _layout(self):
        self._constructing = True
        self._title = eveui.EveCaptionSmall(name='title', parent=self.headerCont, align=eveui.Align.center_left, text=localization.GetByLabel(self.label))
        self._content_container = eveui.ScrollContainer(name='missions_scroll_container', parent=self.mainCont, align=eveui.Align.to_top, height=0)
        self._content_container.OnScrolledVertical = self._on_scroll
        self._constructing = False

    def ConstructHeaderButton(self):
        container = eveui.Container(parent=self.headerBtnCont, align=eveui.Align.center_right, width=28, height=28)
        return ButtonIcon(parent=container, align=eveui.Align.center, iconSize=18, width=18, height=18, texturePath=self.default_iconTexturePath, func=self._open_job_board)

    def _open_job_board(self, *args, **kwargs):
        self.service.open_active_page()

    def _on_entry_clicked(self, job_id):
        if job_id == self._expanded_job_id:
            self._expand_job(None, save=True)
        else:
            self._expand_job(job_id, save=True)

    def _expand_job(self, job_id, save = False):
        self._update_expanded_job_id_settings(job_id)
        self._update_expanded_entries()
        self._scroll_to_expanded()
        if save:
            self._save_expanded(job_id)

    def _update_expanded_entries(self):
        for job_id, entry in self._job_entries.items():
            if job_id == self._expanded_job_id:
                try:
                    entry.expand()
                except:
                    logger.exception('Failed to expand info panel entry %s', entry.name)

            else:
                entry.collapse()

    def _scroll_to_expanded(self):
        blue.synchro.Yield()
        job_id = self._expanded_job_id
        if not job_id or job_id not in self._job_entries:
            return
        self._content_container.ScrollToRevealChildVertical(self._job_entries[job_id])

    def OnStartModeChanged(self, oldMode):
        if not oldMode:
            return
        self._check_update_expanded()

    def OnExpandedMissionChanged(self, featureID = None, missionID = None):
        if not featureID or featureID == self.featureID:
            return
        self._expanded_job_id = -1
        self._update_expanded_entries()
        if self._expanded_job_id != -1:
            self._scroll_to_expanded()

    def _get_expanded_job_id_from_settings(self):
        return settings.char.ui.Get(self.expandedJobSettingsName, self._get_default_expanded_job_id())

    def _get_default_expanded_job_id(self):
        jobs = self.service.get_tracked_jobs()
        for job in jobs:
            if job.job_id in self._job_entries:
                return job.job_id

    def _update_expanded_job_id_settings(self, job_id):
        settings.char.ui.Set(self.expandedJobSettingsName, job_id)
        self._expanded_job_id = job_id

    def _check_update_expanded(self):
        if self.mode == MODE_NORMAL:
            expanded_mission = sm.GetService('infoPanel').GetExpandedMission()
            expanded_id = None
            save = True
            if not expanded_mission or expanded_mission['missionID'] == -1:
                expanded_id = self._get_expanded_job_id_from_settings()
                if expanded_id in (None, -1) or expanded_id not in self._job_entries:
                    expanded_id = self._get_default_expanded_job_id()
            elif expanded_mission['featureID'] == self.featureID:
                expanded_id = expanded_mission['missionID']
                save = settings.char.ui.Get(self.expandedJobSettingsName) != expanded_id
            if expanded_id is not None:
                self._expand_job(expanded_id, save=save)
        else:
            self._save_expanded(-1)

    def _save_expanded(self, expanded_id):
        if expanded_id == -1:
            expanded_mission = sm.GetService('infoPanel').GetExpandedMission()
            if expanded_mission.get('featureID') != self.featureID:
                return
        sm.GetService('infoPanel').SetExpandedMission(self.featureID, expanded_id)

    def _update_content_container_height(self):
        if not self._content_container or self._content_container.destroyed:
            return
        totalHeight = self._content_container.mainCont.height
        self._content_container.height = min(totalHeight, SCROLL_CONTAINER_HEIGHT_MAX)
        self._content_container.clipCont.clipChildren = totalHeight > SCROLL_CONTAINER_HEIGHT_MAX

    def _update_content_container_scroll_position(self):
        blue.synchro.Yield()
        if not self._content_container or self._content_container.destroyed:
            return
        self._scroll_initialized = True
        self._content_container.ScrollToVertical(self._scroll_fraction.get())

    def _on_scroll(self, pos_fraction):
        if self._scroll_initialized:
            self._scroll_fraction.set(self._content_container.GetPositionVertical())
