#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\escalation_sites\page.py
import carbonui
import eveui
import localization
from jobboard.client.ui.pages.details_page import DetailsSection
from jobboard.client.features.dungeons.page import DungeonPage
from jobboard.client.ui.time_remaining import TimeRemaining

class EscalationSitePage(DungeonPage):

    def _construct_body(self, parent_container):
        self._construct_time_remaining(parent_container)
        description_section = DetailsSection(parent=parent_container, title=localization.GetByLabel('UI/Common/Expeditions'), max_content_height=100)
        container = description_section.content_container
        carbonui.TextBody(parent=container, align=eveui.Align.to_top, text=self.job.transmission_description)
        super(EscalationSitePage, self)._construct_body(parent_container)

    def _construct_time_remaining(self, parent_container):
        if self.job.is_expired:
            return
        TimeRemaining(parent=parent_container, align=eveui.Align.to_top, padTop=12, padBottom=12, job=self.job)
