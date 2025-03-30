#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\homepage\sequencingJobInfo.py
import uthread2
from carbonui import Align, AxisAlignment, ButtonStyle, ButtonVariant, Density, uiconst
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from cosmetics.client.ships.ship_skin_signals import on_skin_sequencing_job_completed
from cosmetics.client.ships.skins.errors import get_sequencing_error_text
from cosmetics.client.ships.skins.live_data import current_skin_design
from cosmetics.client.shipSkinDataSvc import get_ship_skin_data_svc
from cosmetics.client.shipSkinSequencingSvc import get_ship_skin_sequencing_svc
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship.const import ANIM_DURATION_LONG, SkinrPage
from eve.client.script.ui.cosmetics.ship.controls.costInfo import SequencingJobCostInfo
from eve.client.script.ui.cosmetics.ship.controls.shipName import ShipName
from eve.client.script.ui.cosmetics.ship.pages import current_page
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSignals
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException

class SequencingJobInfo(Container):
    default_opacity = 0.0

    def __init__(self, *args, **kwargs):
        super(SequencingJobInfo, self).__init__(*args, **kwargs)
        self.sequencing_job = None
        self._update_thread = None
        self.construct_layout()
        self.connect_signals()
        self.update()

    def Close(self):
        try:
            self.kill_update_thread()
            self.disconnect_signals()
        finally:
            super(SequencingJobInfo, self).Close()

    def kill_update_thread(self):
        if self._update_thread is not None:
            self._update_thread.kill()
            self._update_thread = None

    def connect_signals(self):
        studioSignals.on_saved_design_selected.connect(self.on_saved_design_selected)
        studioSignals.on_sequencing_job_selected.connect(self.on_sequencing_job_selected)
        studioSignals.on_page_opened.connect(self.on_page_opened)
        on_skin_sequencing_job_completed.connect(self.on_sequencing_job_completed)
        sm.GetService('vgsService').GetStore().GetAccount().accountAurumBalanceChanged.connect(self.on_plex_amount_changed)

    def disconnect_signals(self):
        studioSignals.on_saved_design_selected.disconnect(self.on_saved_design_selected)
        studioSignals.on_sequencing_job_selected.disconnect(self.on_sequencing_job_selected)
        studioSignals.on_page_opened.disconnect(self.on_page_opened)
        on_skin_sequencing_job_completed.disconnect(self.on_sequencing_job_completed)
        sm.GetService('vgsService').GetStore().GetAccount().accountAurumBalanceChanged.disconnect(self.on_plex_amount_changed)

    def construct_layout(self):
        self.construct_buttons()
        self.construct_const_info()
        self.construct_ship_name()

    def construct_buttons(self):
        button_group = ButtonGroup(parent=self, align=Align.TOBOTTOM, button_alignment=AxisAlignment.END, density=Density.EXPANDED, button_size_mode=ButtonSizeMode.DYNAMIC)
        button_group.add_button(Button(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/CreateNewDesign'), variant=ButtonVariant.PRIMARY, func=self.on_create_design_button))
        self.complete_now_button = Button(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/CompleteJobNow'), variant=ButtonVariant.PRIMARY, style=ButtonStyle.SUCCESS, func=self.on_complete_now_button)
        self.complete_now_button.LoadTooltipPanel = self.LoadCompleteNowButtonTooltipPanel
        button_group.add_button(self.complete_now_button)

    def LoadCompleteNowButtonTooltipPanel(self, tooltipPanel, *args):
        if self.has_enough_plex:
            return
        tooltipPanel.columns = 1
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.AddLabelMedium(text=self.insufficient_funds_hint, wrapWidth=300, color=eveColor.DANGER_RED)

    def construct_const_info(self):
        self.cost_info = SequencingJobCostInfo(name='cost_info', parent=self.complete_now_button, align=Align.TOBOTTOM, top=44)

    def construct_ship_name(self):
        self.ship_name = ShipName(name='ship_name', parent=self, align=Align.CENTERTOP)

    def on_create_design_button(self, *args):
        if current_skin_design.get().has_fitted_components():
            ship_type_id = current_skin_design.get().ship_type_id
            current_skin_design.create_blank_design(ship_type_id)
        current_page.set_page_id(SkinrPage.STUDIO_DESIGNER)

    def on_complete_now_button(self, *args):
        try:
            plex_cost = get_ship_skin_sequencing_svc().get_early_completion_cost(self.sequencing_job.job_id)
            if uicore.Message('CompleteSequencingNow', {'plex_cost': plex_cost}, uiconst.YESNO) == uiconst.ID_YES:
                error = get_ship_skin_sequencing_svc().expedite_sequencing(self.sequencing_job.job_id)
                if error is not None:
                    ShowQuickMessage(GetByLabel(get_sequencing_error_text(error)))
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))

    def update(self):
        self.kill_update_thread()
        self._update_thread = uthread2.StartTasklet(self.update_async)

    def update_async(self):
        self.update_cost_info()
        self.update_ship_name()
        self.update_complete_now_button()

    def update_cost_info(self):
        self.cost_info.sequencing_job = self.sequencing_job

    def update_ship_name(self):
        if not self.sequencing_job:
            self.ship_name.ship_type_id = None
            return
        try:
            skin_design = get_ship_skin_data_svc().get_skin_data(self.sequencing_job.skin_hex)
            self.ship_name.ship_type_id = skin_design.ship_type_id if skin_design else None
        except (GenericException, TimeoutException):
            self.ship_name.ship_type_id = None

    def update_complete_now_button(self):
        if self.has_enough_plex:
            self.complete_now_button.style = ButtonStyle.SUCCESS
            self.complete_now_button.func = self.on_complete_now_button
        else:
            self.complete_now_button.style = ButtonStyle.DANGER
            self.complete_now_button.func = None

    @property
    def has_enough_plex(self):
        if not self.sequencing_job:
            return True
        try:
            plex_cost = get_ship_skin_sequencing_svc().get_early_completion_cost(self.sequencing_job.job_id)
            return sm.GetService('vgsService').GetPLEXBalance() >= plex_cost
        except (GenericException, TimeoutException):
            return True

    @property
    def insufficient_funds_hint(self):
        currencies = []
        if not self.has_enough_plex:
            currencies.append(GetByLabel('UI/Common/PLEX'))
        return u'{base} ({currencies})'.format(base=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/InsufficientFunds'), currencies=u'/'.join(currencies))

    def on_saved_design_selected(self, *args):
        self.fade_out()

    def on_sequencing_job_selected(self, sequencing_job):
        self._set_sequencing_job(sequencing_job)
        self.complete_now_button.Show()

    def on_sequencing_job_completed(self, job_id):
        if not self.sequencing_job or self.sequencing_job.job_id != job_id:
            return
        self.complete_now_button.Hide()

    def on_plex_amount_changed(self, *args):
        self.update()

    def on_page_opened(self, page_id, page_args, last_page_id, animate = True):
        self.fade_out()

    def _set_sequencing_job(self, sequencing_job):
        self.sequencing_job = sequencing_job
        if sequencing_job is None:
            self.fade_out()
        else:
            self.fade_out(callback=self.on_fade_out_complete)

    def fade_out(self, callback = None):
        if callback is None:
            self.sequencing_job = None
        self.state = uiconst.UI_DISABLED
        animations.FadeTo(self, self.opacity, 0.0, ANIM_DURATION_LONG, callback=callback)

    def fade_in(self):
        self.state = uiconst.UI_PICKCHILDREN
        animations.FadeTo(self, self.opacity, 1.0, 0.5)

    def on_fade_out_complete(self):
        self.update()
        self.fade_in()
