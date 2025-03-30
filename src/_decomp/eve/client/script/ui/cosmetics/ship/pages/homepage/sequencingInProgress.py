#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\homepage\sequencingInProgress.py
import logging
from carbonui import Align
from cosmetics.client.shipSkinDataSvc import get_ship_skin_data_svc
from cosmetics.client.ships.ship_skin_signals import on_skin_sequencing_job_updated, on_skin_sequencing_job_completed
from cosmetics.client.ships.skins.live_data import current_skin_design
from cosmetics.common.ships.skins.sequencing_util import get_maximum_concurrent_sequencing_jobs
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship.controls.baseCardSectionContainer import BaseCardSectionContainer
from eve.client.script.ui.cosmetics.ship.pages.cards.sequencingJobCard import SequencingJobCard
from eve.client.script.ui.cosmetics.ship.pages.sequence.tooltipInfoIcons import MaxConcurrentJobsSkillsInfoIcon
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSignals
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from skills.client.util import get_skill_service
from stackless_response_router.exceptions import TimeoutException
log = logging.getLogger(__name__)

class SequencingInProgressSectionContainer(BaseCardSectionContainer):
    __notifyevents__ = ['OnSkillsChanged']
    default_height = 366
    default_minHeight = 366

    def connect_signals(self):
        super(SequencingInProgressSectionContainer, self).connect_signals()
        on_skin_sequencing_job_updated.connect(self._on_skin_sequencing_job_updated)
        on_skin_sequencing_job_completed.connect(self._on_sequencing_job_completed)
        sm.RegisterNotify(self)

    def disconnect_signals(self):
        super(SequencingInProgressSectionContainer, self).disconnect_signals()
        on_skin_sequencing_job_updated.disconnect(self._on_skin_sequencing_job_updated)
        on_skin_sequencing_job_completed.disconnect(self._on_sequencing_job_completed)
        sm.UnregisterNotify(self)

    def OnSkillsChanged(self, *args):
        self.update()

    def _on_skin_sequencing_job_updated(self, *args):
        self.update()

    def _on_sequencing_job_completed(self, *args):
        self.update()

    def construct_header(self):
        super(SequencingInProgressSectionContainer, self).construct_header()
        self.header_layout_grid.columns = 3
        MaxConcurrentJobsSkillsInfoIcon(parent=self.header_layout_grid, align=Align.CENTERLEFT)

    def update_num_items_label(self):
        num_jobs = self.section_controller.get_num_entries()
        num_max = get_maximum_concurrent_sequencing_jobs(get_skill_service().GetMyLevel)
        self.num_items_label.text = u'{}/{}'.format(num_jobs, num_max)

    def construct_card(self, sequencing_job):
        try:
            skin_design = get_ship_skin_data_svc().get_skin_data(sequencing_job.skin_hex)
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
            return None

        card = SequencingJobCard(parent=self.content, sequencing_job=sequencing_job, skin_design=skin_design)
        card.on_click.connect(self.on_card_clicked)
        return card

    def deselect_all_cards(self):
        for card in self.cards:
            card.is_selected = False

    def verify_cards(self):
        for card in self.cards:
            if not card.finished_loading:
                card.update_live_icon()

    def on_card_clicked(self, clicked_card):
        for card in self.cards:
            if card != clicked_card:
                card.is_selected = False

        if clicked_card.is_selected:
            studioSignals.on_sequencing_job_selected(clicked_card.sequencing_job)
        else:
            studioSignals.on_sequencing_job_selected(None)
            current_skin_design.create_blank_design()

    def construct_top_right_button(self):
        pass

    def _get_card_height(self):
        return SequencingJobCard.default_height
