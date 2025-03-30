#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\factional_warfare_enlistment\job.py
from eve.common.lib import appConst
from carbonui.control.contextMenu.menuData import MenuData
from fwwarzone.client.dashboard.const import FACTION_ID_TO_ENLIST_PROMPT
import localization
import logging
import uthread2
from metadata.common import ContentTags
from objectives.client.objective_chain import ObjectiveChain
from objectives.common.objective_context import ObjectivesContext
from jobboard.client.job import BaseJob
logger = logging.getLogger('job_board')

class FactionalWarfareEnlistmentJob(BaseJob):

    def __init__(self, job_id, provider, faction_id):
        self._faction_id = faction_id
        self._objective_chain = None
        self._context = ObjectivesContext()
        self._solar_system_id = None
        content_id = self._faction_id
        super(FactionalWarfareEnlistmentJob, self).__init__(job_id, content_id, provider)
        if self.is_tracked:
            uthread2.start_tasklet(self._update_location)

    def update(self):
        if not self.is_tracked or not self._solar_system_id:
            self._update_location()
        super(FactionalWarfareEnlistmentJob, self).update()

    def _update_location(self):
        try:
            _, station_id = sm.GetService('facwar').GetNearestFactionWarfareStationData(self._faction_id, fallbackToLightYears=True)
        except Exception as e:
            logger.error('Failed to get nearest faction location %s - e=%s', self._faction_id, e)
            return

        if not station_id:
            return
        self._context.update_value('location_id', station_id)
        if station_id is None:
            self._solar_system_id = None
        else:
            station = cfg.evelocations.Get(station_id)
            self._solar_system_id = station.solarSystemID

    def on_tracked(self):
        self._update_location()

    @property
    def faction_id(self):
        return self._faction_id

    @property
    def title(self):
        return FACTION_ID_TO_ENLIST_PROMPT[self._faction_id]

    @property
    def solar_system_id(self):
        return self._solar_system_id

    @property
    def location_id(self):
        return self._context.get_value('location_id')

    @property
    def is_available_in_active(self):
        return self.is_tracked

    @property
    def is_available_in_browse(self):
        return False

    @property
    def is_trackable(self):
        return not self.is_removed

    @property
    def is_completed(self):
        return session.warfactionid == self.faction_id

    @property
    def objective_chain(self):
        if not self._objective_chain:
            objective_chain = ObjectiveChain(content_id=58, context=self._context)
            objective_chain.start()
            self._objective_chain = objective_chain
        return self._objective_chain

    def get_menu(self):
        from objectives.client.qa_tools import is_qa, get_objective_chain_context_menu
        if is_qa() and self._objective_chain:
            data = MenuData()
            data.AddEntry('QA', subMenuData=get_objective_chain_context_menu(self._objective_chain, include_blackboard=True))
            data.entrylist.extend(super(FactionalWarfareEnlistmentJob, self).get_menu().entrylist)
            return data
        else:
            return super(FactionalWarfareEnlistmentJob, self).get_menu()

    def get_cta_buttons(self):
        return [{'icon': 'res:/UI/Texture/WindowIcons/factionalwarfare.png',
          'on_click': self._open_enlistment_window,
          'label': localization.GetByLabel('UI/FactionWarfare/FwEnlistmentWnd')}]

    def _get_content_tag_ids(self):
        if self.faction_id in appConst.factionsEmpires:
            return [ContentTags.feature_factional_warfare, ContentTags.career_path_soldier_of_fortune]
        else:
            return [ContentTags.feature_pirate_insurgencies, ContentTags.career_path_soldier_of_fortune]

    def _open_enlistment_window(self, *args, **kwargs):
        sm.GetService('cmd').OpenFwEnlistment()
