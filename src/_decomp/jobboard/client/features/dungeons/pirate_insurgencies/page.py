#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\pirate_insurgencies\page.py
import carbonui
import eveui
import eveformat
import localization
import threadutils
from eve.client.script.ui import eveColor
from carbonui.primitives.cardsContainer import CardsContainer
from pirateinsurgency.client.dashboard.widgets.gauge import SuppressionGauge, CorruptionGauge
from jobboard.client.ui.pages.details_page import DetailsSection
from jobboard.client.features.dungeons.page import DungeonPage

class PirateInsurgencyPage(DungeonPage):

    def _construct_body(self, parent_container):
        super(PirateInsurgencyPage, self)._construct_body(parent_container)
        self._construct_system_details(parent_container)

    def _construct_archetype_info(self, parent_container):
        pass

    @threadutils.threaded
    def _construct_system_details(self, parent_container):
        if self.destroyed:
            return
        if not self.job.is_system_affected_by_insurgency:
            return
        system_section = DetailsSection(parent=parent_container, title=localization.GetByLabel('UI/Opportunities/FWSystemStatusHeader', solar_system_id=self.job.solar_system_id))
        container = system_section.content_container
        system_info_container = CardsContainer(parent=container, align=eveui.Align.to_top, cardHeight=80, cardMaxWidth=500, contentSpacing=(16, 16))
        suppression_container = eveui.Container(parent=system_info_container, align=eveui.Align.to_all)
        self._construct_suppression(suppression_container)
        corruption_container = eveui.Container(parent=system_info_container, align=eveui.Align.to_all)
        self._construct_corruption(corruption_container)

    @threadutils.threaded
    def _construct_suppression(self, parent_container):
        if self.destroyed:
            return
        SuppressionGauge(parent=parent_container, align=eveui.Align.center_left, dashboardSvc=sm.GetService('insurgencyDashboardSvc'), width=64, height=64, stages=self.job.suppression_stages, systemID=self.job.solar_system_id)
        text_container = eveui.ContainerAutoSize(parent=parent_container, align=carbonui.Align.VERTICALLY_CENTERED, padLeft=80, clipChildren=True)
        carbonui.TextBody(parent=text_container, align=eveui.Align.to_top, text=localization.GetByLabel('UI/PirateInsurgencies/suppression'), autoFadeSides=16)
        self._suppression_stage_label = carbonui.TextBody(parent=text_container, align=eveui.Align.to_top, text=localization.GetByLabel('UI/PirateInsurgencies/stageLabel', stage=self.job.system_suppression_stage), bold=True, autoFadeSides=16)
        self._suppression_percentage_label = carbonui.TextBody(parent=text_container, align=eveui.Align.to_top, text=eveformat.percent(self.job.system_suppression_percentage), color=carbonui.TextColor.SECONDARY, autoFadeSides=16)

    @threadutils.threaded
    def _construct_corruption(self, parent_container):
        if self.destroyed:
            return
        CorruptionGauge(parent=parent_container, align=eveui.Align.center_left, dashboardSvc=sm.GetService('insurgencyDashboardSvc'), width=64, height=64, stages=self.job.corruption_stages, systemID=self.job.solar_system_id)
        text_container = eveui.ContainerAutoSize(parent=parent_container, align=carbonui.Align.VERTICALLY_CENTERED, padLeft=80, clipChildren=True)
        carbonui.TextBody(parent=text_container, align=eveui.Align.to_top, text=localization.GetByLabel('UI/PirateInsurgencies/corruption'), autoFadeSides=16)
        self._corruption_stage_label = carbonui.TextBody(parent=text_container, align=eveui.Align.to_top, text=localization.GetByLabel('UI/PirateInsurgencies/stageLabel', stage=self.job.system_corruption_stage), bold=True, autoFadeSides=16)
        self._corruption_percentage_label = carbonui.TextBody(parent=text_container, align=eveui.Align.to_top, text=eveformat.percent(self.job.system_corruption_percentage), color=carbonui.TextColor.SECONDARY, autoFadeSides=16)
