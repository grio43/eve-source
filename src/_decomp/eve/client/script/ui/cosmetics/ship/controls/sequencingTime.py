#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\controls\sequencingTime.py
from carbonui.uiconst import PickState
from carbonui.primitives.layoutGrid import LayoutGrid
import eveicon
import gametime
import uthread2
from carbonui import Align, TextBody, TextColor, TextHeader, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from cosmetics.client.ships.skins.live_data import current_skin_design, current_skin_design_signals
from cosmetics.client.shipSkinSequencingSvc import get_ship_skin_sequencing_svc
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship.pages.sequence.tooltipInfoIcons import SequencingTimeSkillsInfoIcon
from localization import GetByLabel, formatters
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException

class SequencingTime(Container):
    default_height = 32

    def __init__(self, *args, **kwargs):
        super(SequencingTime, self).__init__(*args, **kwargs)
        self._update_thread = None
        self.construct_layout()
        self.connect_signals()
        self.update()

    def Close(self):
        try:
            self.kill_update_thread()
            self.disconnect_signals()
        finally:
            super(SequencingTime, self).Close()

    def kill_update_thread(self):
        if self._update_thread:
            self._update_thread.kill()
            self._update_thread = None

    def connect_signals(self):
        current_skin_design_signals.on_design_reset.connect(self.on_design_reset)
        current_skin_design_signals.on_existing_design_loaded.connect(self.on_existing_design_loaded)
        current_skin_design_signals.on_ship_type_id_changed.connect(self.on_ship_type_id_changed)
        current_skin_design_signals.on_slot_fitting_changed.connect(self.on_slot_fitting_changed)

    def disconnect_signals(self):
        current_skin_design_signals.on_design_reset.disconnect(self.on_design_reset)
        current_skin_design_signals.on_existing_design_loaded.disconnect(self.on_existing_design_loaded)
        current_skin_design_signals.on_ship_type_id_changed.disconnect(self.on_ship_type_id_changed)
        current_skin_design_signals.on_slot_fitting_changed.disconnect(self.on_slot_fitting_changed)

    def construct_layout(self):
        self.Flush()
        left_container = Container(name='left_container', parent=self, align=Align.TOLEFT, pickState=PickState.ON, hint=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/TimeToSequence'), width=40)
        Fill(bgParent=left_container, color=eveColor.WHITE, opacity=0.1)
        Sprite(name='icon', parent=left_container, align=Align.CENTER, texturePath=eveicon.hourglass, color=TextColor.NORMAL, pickState=PickState.OFF, pos=(0, 0, 16, 16))
        self.right_container = Container(name='right_container', parent=self, align=Align.TOALL, padLeft=4)
        self.layout_grid = LayoutGrid(parent=self.right_container, align=Align.TORIGHT, cellSpacing=(4, 0))
        self.layout_grid.columns = 2
        self.construct_info_icon()
        self.construct_time_label()

    def construct_info_icon(self):
        SequencingTimeSkillsInfoIcon(name='info_icon', parent=self.layout_grid, align=Align.CENTER)

    def construct_time_label(self):
        self.time_label = TextHeader(name='time_label', parent=self.layout_grid, color=TextColor.HIGHLIGHT, align=Align.CENTER, padLeft=8)

    def update(self):
        self.kill_update_thread()
        self._update_thread = uthread2.start_tasklet(self._update_async)

    def _update_async(self):
        try:
            duration = get_ship_skin_sequencing_svc().get_predicted_job_duration(current_skin_design.get()) * gametime.SEC
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
            duration = 0

        self.construct_layout()
        show_to = 'minute' if duration < gametime.DAY else 'hour'
        self.time_label.text = formatters.FormatTimeIntervalShortWritten(duration, showTo=show_to)

    def on_design_reset(self, *args):
        self.update()

    def on_existing_design_loaded(self, *args):
        self.update()

    def on_ship_type_id_changed(self, *args):
        self.update()

    def on_slot_fitting_changed(self, *args):
        self.update()
