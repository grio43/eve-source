#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\pirate_insurgencies\job.py
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupPirateIncursions
import localization
import eveicon
from fwwarzone.client.facwarUtil import IsMyCombatEnemyFaction, IsMyFwFaction
from jobboard.client.features.dungeons.job import DungeonJob
from .page import PirateInsurgencyPage

class PirateInsurgencyJob(DungeonJob):
    CONTENT_GROUP_ID = contentGroupPirateIncursions
    PAGE_CLASS = PirateInsurgencyPage

    @property
    def is_available_in_browse(self):
        if not super(PirateInsurgencyJob, self).is_available_in_browse:
            return False
        faction_id = self.faction_id
        return IsMyFwFaction(faction_id) or IsMyCombatEnemyFaction(faction_id)

    @property
    def _corruption_service(self):
        return sm.GetService('corruptionSuppressionSvc')

    @property
    def is_system_affected_by_insurgency(self):
        return sm.GetService('insurgencyDashboardSvc').IsSystemAffectedByInsurgency(self.solar_system_id)

    @property
    def suppression_stages(self):
        return self._corruption_service.GetSuppressionStages()

    @property
    def system_suppression(self):
        return self._corruption_service.GetSystemSuppression(self.solar_system_id)

    @property
    def system_suppression_stage(self):
        return self.system_suppression.stage

    @property
    def system_suppression_percentage(self):
        return self.system_suppression.totalProportion

    @property
    def corruption_stages(self):
        return self._corruption_service.GetCorruptionStages()

    @property
    def system_corruption(self):
        return self._corruption_service.GetSystemCorruption(self.solar_system_id)

    @property
    def system_corruption_stage(self):
        return self.system_corruption.stage

    @property
    def system_corruption_percentage(self):
        return self.system_corruption.totalProportion

    def get_buttons(self):
        buttons = super(PirateInsurgencyJob, self).get_buttons()
        buttons.append({'icon': eveicon.pirate_insurgencies,
         'on_click': self._open_insurgency_window,
         'hint': localization.GetByLabel('UI/Agency/FactionWarfare/openFactionWarfareWindow')})
        return buttons

    def _open_insurgency_window(self, *args, **kwargs):
        sm.GetService('cmd').OpenInsurgencyDashboard()
