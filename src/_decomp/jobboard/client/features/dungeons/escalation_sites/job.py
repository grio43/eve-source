#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\escalation_sites\job.py
from carbonui.control.contextMenu.menuData import MenuData
import gametime
import localization
from eve.common.script.sys import eveCfg
from jobboard.client.features.dungeons.job import DungeonJob
from .card import EscalationSiteCard, EscalationListEntry
from .page import EscalationSitePage

class EscalationSiteJob(DungeonJob):
    PAGE_CLASS = EscalationSitePage
    CARD_CLASS = EscalationSiteCard
    LIST_ENTRY_CLASS = EscalationListEntry
    OBJECTIVE_CHAIN_ID = 55

    @property
    def is_linkable(self):
        return False

    @property
    def subtitle(self):
        faction_name = self.faction_name
        if self.difficulty:
            difficulty = localization.GetByLabel('UI/Agency/LevelX', level=self.difficulty)
            if faction_name:
                return u'{} - {}'.format(faction_name, difficulty)
            else:
                return difficulty
        return faction_name

    @property
    def transmission_description(self):
        return localization.GetByMessageID(self._dungeon['transmission_description_id'])

    @property
    def expiration_time(self):
        return self._dungeon['expiration_time']

    @property
    def is_expired(self):
        return self.expiration_time < gametime.GetWallclockTime()

    @property
    def is_available_in_active(self):
        return True

    def _get_warp_to_menu(self):
        if not self.in_same_system or not eveCfg.InSpace():
            return None
        data = MenuData()
        data.AddEntry(localization.GetByLabel('UI/Objectives/Titles/WarpToSite'), self._warp_to_location)
        data.AddSeparator()
        return data

    def _warp_to_location(self):
        sm.GetService('michelle').CmdWarpToStuff('epinstance', self.instance_id)
