#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\cards\sequencingJobCard.py
import blue
import carbonui
import eveicon
import evetypes
import uthread2
from carbon.common.script.sys.serviceConst import ROLE_QA
from carbonui import Align, TextAlign, TextBody, TextColor, uiconst, PickState, SpriteEffect, ButtonStyle
from carbonui.control.button import Button
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from cosmetics.client.liveIconRenderer import LiveIconSprite
from cosmetics.client.shipSkinSequencingSvc import get_ship_skin_sequencing_svc
from cosmetics.client.ships.skins.errors import NoTimeRemainingException, get_sequencing_error_text
from cosmetics.client.ships.skins.live_data.sequencing_job import SequencingJobState
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship.pages.cards.cardConst import CardBackground, CardMask
from eve.client.script.ui.shared.messagebox import MessageBox
from eve.client.script.ui.shared.neocom.wallet.buyMissingPlexDialog import BuyMissingPlexDialog
from eveservices.menu import GetMenuService
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from signals import Signal
from stackless_response_router.exceptions import TimeoutException
ANIM_DURATION = 0.2
ICON_SIZE = 128

class SequencingJobCard(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL
    default_width = 168
    default_height = 308

    def __init__(self, sequencing_job, skin_design, *args, **kwargs):
        super(SequencingJobCard, self).__init__(*args, **kwargs)
        self.sequencing_job = sequencing_job
        self.skin_design = skin_design
        self._is_selected = False
        self.is_hovered = False
        self.live_icon = None
        self.finished_loading = False
        self.time_label_update_thread = None
        self.expedite_sequencing_thread = None
        self.update_complete_now_thread = None
        self.on_click = Signal('on_click')
        self.construct_layout()
        self.update_live_icon()
        self.update()
        self.connect_signals()
        self.time_label_update_thread = uthread2.start_tasklet(self.update_time_left_label)

    def Close(self):
        try:
            self.kill_threads()
            self.disconnect_signals()
        finally:
            super(SequencingJobCard, self).Close()

    def kill_threads(self):
        self.kill_time_label_update_thread()
        self.kill_expedite_sequencing_thread()
        self.kill_update_complete_now_thread()

    def kill_time_label_update_thread(self):
        if self.time_label_update_thread is not None:
            self.time_label_update_thread.kill()
            self.time_label_update_thread = None

    def kill_expedite_sequencing_thread(self):
        if self.expedite_sequencing_thread is not None:
            self.expedite_sequencing_thread.kill()
            self.expedite_sequencing_thread = None

    def kill_update_complete_now_thread(self):
        if self.update_complete_now_thread is not None:
            self.update_complete_now_thread.kill()
            self.update_complete_now_thread = None

    def connect_signals(self):
        sm.GetService('vgsService').GetStore().GetAccount().accountAurumBalanceChanged.connect(self.on_plex_amount_changed)

    def disconnect_signals(self):
        sm.GetService('vgsService').GetStore().GetAccount().accountAurumBalanceChanged.disconnect(self.on_plex_amount_changed)

    def construct_layout(self):
        self.construct_top_cont()
        self.construct_tier_indicator()
        self.construct_num_runs_label()
        self.construct_label_and_gauge()
        self.construct_complete_now()
        self.construct_ship_icon()

    def on_plex_amount_changed(self, *args):
        self.update()

    def on_live_rendered_icon_ready(self):
        self.finished_loading = True
        self.loading_sprite.display = False
        animations.FadeIn(self.live_icon)
        self.live_icon.on_rendered.disconnect(self.on_live_rendered_icon_ready)

    def on_loading_sprite_fadeout_complete(self):
        self.loading_sprite.display = False

    def construct_label_and_gauge(self):
        self.name_label = carbonui.TextBody(name='name_label', parent=self, align=Align.TOTOP, color=TextColor.HIGHLIGHT, padTop=8, bold=True)
        self.gauge = Gauge(parent=self, align=Align.TOTOP, gaugeHeight=4, padTop=4, color=eveThemeColor.THEME_FOCUS)
        self.time_left_label = carbonui.TextBody(name='time_left_label', parent=self, align=Align.TOTOP, padTop=2)

    def construct_complete_now(self):
        self.complete_now_cont = Container(name='complete_cont', parent=self, align=Align.TOTOP, height=Button.default_height, padBottom=16, padTop=8)
        self.complete_now_label_cont = LayoutGrid(name='complete_now_label_cont', parent=self.complete_now_cont, align=Align.CENTER, cellSpacing=(4, 0))
        Sprite(parent=self.complete_now_label_cont, align=Align.CENTERLEFT, texturePath=eveicon.plex, color=eveColor.PLEX_YELLOW, pos=(0, 0, 16, 16))
        self.complete_now_label = carbonui.TextBody(parent=self.complete_now_label_cont, align=Align.CENTERLEFT)
        self.complete_button = Button(name='complete_button', parent=self.complete_now_cont, align=Align.TOTOP, display=False, pickState=PickState.ON, label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/CompleteJobNow'), func=self.on_complete_button)
        self.complete_button.LoadTooltipPanel = self.LoadCompleteButtonTooltipPanel

    def LoadCompleteButtonTooltipPanel(self, tooltipPanel, *args):
        if self.has_enough_plex:
            return
        tooltipPanel.columns = 1
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.pickState = PickState.ON
        TextBody(parent=tooltipPanel, align=Align.CENTERLEFT, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/InsufficientPLEX', plex_balance=int(sm.GetService('vgsService').GetPLEXBalance()) or 0), color=TextColor.DANGER, maxWidth=220)
        Button(parent=tooltipPanel, label=GetByLabel('UI/Wallet/BuyMore'), func=self.on_buy_more_plex_button, style=ButtonStyle.MONETIZATION, align=Align.TOTOP)

    def on_buy_more_plex_button(self, *args):
        buy_missing_plex_dialog = BuyMissingPlexDialog(required_amount=self.get_early_completion_plex_cost())
        buy_missing_plex_dialog.ShowModal()

    def on_complete_button(self, *args):
        if not self.has_enough_plex:
            return
        try:
            self.complete_button.busy = True
            self.complete_button.disable()
            self.show_expedite_sequencing_popup_async()
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
        finally:
            self.complete_button.busy = False
            self.complete_button.enable()

    def show_expedite_sequencing_popup_async(self):
        self.kill_expedite_sequencing_thread()
        self.expedite_sequencing_thread = uthread2.start_tasklet(self.show_expedite_sequencing_popup)

    def show_expedite_sequencing_popup(self):
        params = {'plex_cost': self.get_early_completion_plex_cost()}
        icon = 'res:/UI/texture/Icons/SKINR.png'
        if MessageBox.show_message_modal('CompleteSequencingNow', params, uiconst.YESNO, icon) == uiconst.ID_YES:
            error = get_ship_skin_sequencing_svc().expedite_sequencing(self.sequencing_job.job_id)
            if error is not None:
                ShowQuickMessage(GetByLabel(get_sequencing_error_text(error)))

    def construct_top_cont(self):
        self.top_cont = Container(name='top_cont', parent=self, align=Align.TOTOP, height=198)

    def construct_num_runs_label(self):
        num_runs_cont = ContainerAutoSize(name='num_runs_Cont', parent=self.top_cont, align=Align.BOTTOMRIGHT, height=46)
        StretchSpriteHorizontal(bgParent=num_runs_cont, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/cards/sequencing/numruns_background.png', leftEdgeSize=34, rightEdgeSize=30)
        label_cont = ContainerAutoSize(name='label_cont', parent=num_runs_cont, align=Align.TOLEFT, padLeft=40, padRight=26)
        self.num_runs_label = carbonui.TextBody(align=Align.CENTERLEFT, top=4, parent=label_cont)

    def construct_ship_icon(self):
        icon_cont = Container(name='icon_cont', parent=self.top_cont, align=Align.CENTER, pos=(0, 0, 168, 198), state=uiconst.UI_DISABLED)
        self.live_icon = LiveIconSprite(name='live_icon', parent=icon_cont, opacity=0.0, viewportWidth=168, viewportHeight=198, bg_texture_path=CardBackground.SEQUENCING, mask_texture_path=CardMask.SEQUENCING)
        self.fallback_background = Sprite(name='fallback_background', bgParent=icon_cont, spriteEffect=SpriteEffect.MASK, textureSecondaryPath=CardMask.SEQUENCING, texturePath=CardBackground.SEQUENCING)
        self.finished_loading = False
        self.live_icon.on_rendered.connect(self.on_live_rendered_icon_ready)
        self.loading_sprite = LoadingWheel(parent=self.top_cont, align=uiconst.CENTER)

    def construct_tier_indicator(self):
        if not self.show_tier_indicator():
            return
        self.tier_label = TextBody(name='tier_label', parent=self.top_cont, align=Align.TOTOP_NOPUSH, textAlign=TextAlign.CENTER, text='{tier}'.format(tier=self.get_skin_tier_level()), color=eveColor.BLACK, shadowOffset=(0, 0), bold=True, padTop=6)
        self.tier_container = Container(name='tier_container', parent=self.top_cont, align=Align.TOTOP_NOPUSH, opacity=0.5, width=self.default_width, height=29)
        self.tier_background = Sprite(name='tier_background', parent=self.tier_container, align=Align.TOTOP_NOPUSH, state=uiconst.UI_DISABLED, texturePath=self.get_skin_tier_texture(), outputMode=uiconst.OutputMode.COLOR_AND_GLOW, glowBrightness=0.4, width=self.default_width, height=29)

    def show_tier_indicator(self):
        return True

    def get_skin_tier_level(self):
        return self.skin_design.tier_level

    def get_skin_tier_texture(self):
        tier_level = self.get_skin_tier_level()
        return 'res:/UI/Texture/classes/Cosmetics/Ship/cards/tier/tier_{level}.png'.format(level=tier_level)

    def update(self):
        self.num_runs_label.text = str(self.sequencing_job.nb_runs)
        self.name_label.text = self.skin_design.name or ''
        self.update_tier_indicator()
        self.fallback_background.texturePath = CardBackground.SEQUENCING_SELECTED if self.is_selected else CardBackground.SEQUENCING
        self.update_complete_now_async()

    def update_complete_now_async(self):
        self.kill_update_complete_now_thread()
        self.update_complete_now_thread = uthread2.start_tasklet(self.update_complete_now)

    def update_complete_now(self):
        if not self.complete_now_cont or self.complete_now_cont.destroyed:
            return
        try:
            plex_cost = self.get_early_completion_plex_cost()
            if plex_cost:
                self.complete_now_cont.display = True
                self.complete_now_label.text = plex_cost
                has_enough_plex = sm.GetService('vgsService').GetPLEXBalance() >= plex_cost
                self.complete_button.style = ButtonStyle.NORMAL if has_enough_plex else ButtonStyle.DANGER
            else:
                self.complete_now_cont.display = False
        except NoTimeRemainingException:
            self.complete_now_cont.display = False

    def get_early_completion_plex_cost(self):
        try:
            plex_cost = get_ship_skin_sequencing_svc().get_early_completion_cost(self.sequencing_job.job_id)
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
            return None

        return plex_cost

    def update_time_left_label(self):
        while not self.destroyed:
            job_state = self.sequencing_job.state
            if job_state == SequencingJobState.STARTED:
                self.time_left_label.text = self.sequencing_job.get_time_remaining_text()
                self.gauge.SetValue(self.sequencing_job.get_completed_ratio(), animate=False)
            elif job_state == SequencingJobState.COMPLETED:
                self.time_left_label.text = GetByLabel('UI/Generic/Completed')
                self.gauge.SetValue(1.0)
            uthread2.Sleep(0.5)

    def update_tier_indicator(self):
        if not self.show_tier_indicator():
            return
        animations.FadeTo(self.tier_container, self.tier_container.opacity, 0.5, ANIM_DURATION)

    def update_live_icon(self, skip_queue = False):
        bg_texture_path = CardBackground.SEQUENCING_SELECTED if self.is_selected else CardBackground.SEQUENCING
        self.live_icon.apply_skin_design(self.skin_design, bg_texture_path, skip_queue)

    @property
    def has_enough_plex(self):
        return sm.GetService('vgsService').GetPLEXBalance() >= self.get_early_completion_plex_cost()

    @property
    def is_selected(self):
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value):
        should_update = value != self._is_selected
        self._is_selected = value
        if should_update:
            self.update()
            self.update_live_icon(skip_queue=True)

    def OnMouseEnter(self, *args):
        self.is_hovered = True
        if self.complete_now_cont.display:
            self.complete_button.display = True
            self.complete_now_label_cont.display = False
        self.update()

    def OnMouseExit(self, *args):
        self.is_hovered = False
        if self.complete_now_cont.display:
            self.complete_button.display = False
            self.complete_now_label_cont.display = True
        self.update()

    def OnClick(self, *args):
        self.is_selected = not self.is_selected
        self.on_click(self)

    def GetMenu(self):
        menu = MenuData()
        type_id = self.skin_design.ship_type_id
        menu.AddEntry(text=evetypes.GetName(type_id), subMenuData=lambda : GetMenuService().GetMenuFromItemIDTypeID(itemID=None, typeID=type_id, includeMarketDetails=True))
        if session.role & ROLE_QA:
            menu.AddEntry(text='Job UUID: {job_uuid}'.format(job_uuid=self.sequencing_job.job_id), func=lambda *args: blue.pyos.SetClipboardData(str(self.sequencing_job.job_id)))
        return menu
