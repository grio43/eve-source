#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\ui\link_with_ship\state\ready.py
import eveicon
import evetypes
import eveui
import gametime
import logging
import uthread2
from analysisbeacon.client.const import SCALING_BILLBOARD_THRESHOLD
from analysisbeacon.client.state import State
from carbon.common.lib.const import SEC
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import TextBody, TextHeadline, TextDetail
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize, Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color, GetColor
from dynamicresources.client.ess.bracket.tether import BracketTether
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from localization import GetByLabel
from localization.formatters import FormatTimeIntervalShortWritten
from mathext import clamp
from inventorycommon.const import typeSkyhookReagentSilo
from spacecomponents.client.ui.link_with_ship import GetLinkButtonLabelPath
from spacecomponents.client.ui.link_with_ship.state.vulnerability_change_controller import SkyhookVulnerabilityChangeController
from spacecomponents.common.components.linkWithShip import LINKSTATE_COMPLETED
logger = logging.getLogger(__name__)
NO_ACTION = 0
OPENED_BY_PLAYER = 1
COLLAPSED_BY_PLAYER = 2
VULNERABILITY_TIMER_UPDATE_INTERVAL = 500

class Ready(State):
    __notifyevents__ = ['OnSkyhookCanBeHacked']

    def __init__(self, panel, item_id, initiate_link_function, characterEnergyCost, linkDuration, linkState, type_id, owner_id):
        self.panel = panel
        self.item_id = item_id
        self.type_id = type_id
        self.owner_id = owner_id
        self.collapsed = True
        self.player_action = NO_ACTION
        self.run_camera_loop = True
        self.initiate_link_function = initiate_link_function
        self.characterEnergyCost = characterEnergyCost
        self.linkDuration = linkDuration
        self.state = linkState
        self._interface_cont = None
        self._linkButton = None
        self._top_grid = None
        self._secure_timer_container = None
        self._timer_container = None
        self._vulnerable_time_remaining_label = None
        self._time_until_vulnerability_change_gauge_circular = None
        self._shield_sprite = None
        self._vulnerability_change_auto_timer = None
        self._change_controller = None
        if self.type_id == typeSkyhookReagentSilo:
            self._change_controller = SkyhookVulnerabilityChangeController(self.item_id, self.type_id, self.refresh_main_grid)

    def refresh_main_grid(self):
        self.panel.button_cont.Flush()
        if self.type_id == typeSkyhookReagentSilo:
            self._vulnerable_time_remaining_label = None
            self._time_until_vulnerability_change_gauge_circular = None
            if self._vulnerability_change_auto_timer:
                self._vulnerability_change_auto_timer.KillTimer()
                self._vulnerability_change_auto_timer = None
            self._sync_at_change_time = False
            change_datetime = self._change_controller.change_datetime or self._change_controller.scheduled_change_datetime
            if change_datetime is not None:
                seconds_until_change = gametime.GetTimeUntilNowFromDateTime(change_datetime, cast_to_class=long)
                if seconds_until_change > 0:
                    self._sync_at_change_time = True
            self._top_grid = LayoutGrid(parent=self.panel.button_cont, columns=2, align=uiconst.TOPLEFT, height=120)
            if not self._change_controller.is_theft_vulnerable:
                self._secure_timer_container = ContainerAutoSize(align=uiconst.TOLEFT, alignMode=uiconst.CENTERLEFT, padding=(0, 0, 20, 0), opacity=1)
                self._top_grid.AddCell(self._secure_timer_container, colSpan=1, minHeight=120)
                self._shield_sprite = Sprite(parent=self._secure_timer_container, align=uiconst.CENTER, width=25, height=25, color=eveColor.SUCCESS_GREEN, texturePath=eveicon.shields)
                self._time_until_vulnerability_change_gauge_circular = GaugeCircular(parent=self._secure_timer_container, useRealTime=True, clockwise=False, color=Color.WHITE, align=uiconst.CENTERLEFT, showMarker=False, lineWidth=5.0, radius=30, colorStart=eveColor.SUCCESS_GREEN, colorEnd=eveColor.SUCCESS_GREEN, colorBg=eveColor.COPPER_OXIDE_GREEN, opacity=1)
                circleCont = Container(parent=self._secure_timer_container, width=120, height=120, name='arcCont', align=uiconst.TOLEFT)
                Sprite(parent=circleCont, texturePath='res:/UI/Texture/classes/pirateinsurgencies/widgets/track/circle.png', width=60, height=60, align=uiconst.CENTERLEFT, color=GetColor(eveColor.COPPER_OXIDE_GREEN, alpha=0.8))
            self.mainGrid = LayoutGrid(parent=self._top_grid, columns=1, align=uiconst.CENTERLEFT)
            from eve.client.script.ui.control.eveLabel import EveLabelMedium
            if self._change_controller.is_theft_vulnerable:
                self._vulnerable_time_remaining_label = EveLabelMedium(parent=self.mainGrid, align=uiconst.TOPLEFT)
            self._update_vulnerability_change_controls()
            self._vulnerability_change_auto_timer = AutoTimer(VULNERABILITY_TIMER_UPDATE_INTERVAL, self._update_vulnerability_change_controls)
            self.SetupNameAndOwner()
            if self._change_controller.is_theft_vulnerable:
                self.SetupShields()
                includeWarning = False
                self.SetupLinkButton(includeWarning, self.state != LINKSTATE_COMPLETED)
        else:
            self.mainGrid = LayoutGrid(parent=self.panel.button_cont, columns=1, align=uiconst.TOPLEFT)
            self.SetupNameAndOwner()
            includeWarning = True
            self.SetupLinkButton(includeWarning, self.state != LINKSTATE_COMPLETED)

    def _update_vulnerability_change_controls(self):
        formatted_remaining_time_string = ''
        tool_tip_string = None
        vulnerability_label_path = 'UI/Structures/States/Vulnerable' if self._change_controller.is_theft_vulnerable else 'UI/Structures/States/Invulnerable'
        update_circle_gauge_value = False
        change_datetime = self._change_controller.change_datetime
        if change_datetime is not None:
            seconds_until_change = gametime.GetTimeUntilNowFromDateTime(change_datetime, cast_to_class=long)
            seconds_until_change = max(seconds_until_change, 0)
            if seconds_until_change == 0:
                if self._sync_at_change_time:
                    self._sync_at_change_time = False
                    self._change_controller._on_theft_vulnerability_window_ended_notice(self._change_controller._parent_skyhook_id)
                    self._change_controller.sync()
                tool_tip_string = GetByLabel(vulnerability_label_path)
            else:
                update_circle_gauge_value = True
                formatted_remaining_time_string = FormatTimeIntervalShortWritten(seconds_until_change, showFrom='day', showTo='second')
                tool_tip_string = GetByLabel('UI/Inflight/SpaceComponents/LinkWithShip/SecureSiloTooltip', seconds_until_vulnerable=seconds_until_change)
        else:
            tool_tip_string = GetByLabel(vulnerability_label_path)
        if self._time_until_vulnerability_change_gauge_circular:
            if update_circle_gauge_value:
                self._update_time_until_vulnerability_change_gauge(animate=True)
            self._time_until_vulnerability_change_gauge_circular.SetHint(tool_tip_string)
        if self._vulnerable_time_remaining_label:
            self._vulnerable_time_remaining_label.SetText(GetByLabel(vulnerability_label_path) + ' ' + formatted_remaining_time_string)
        if self._shield_sprite:
            self._shield_sprite.SetHint(tool_tip_string)

    def _update_time_until_vulnerability_change_gauge(self, animate = True):

        def get_normalized_percentage_of_time_passed(start_time, end_time):
            if not end_time or not end_time:
                return 1.0
            total = (end_time - start_time).total_seconds()
            current_progress = (gametime.now() - start_time).total_seconds()
            proportion = 1.0 - float(current_progress) / float(total if total > 0 else 1)
            proportion = clamp(proportion, 0.0, 1.0)
            return proportion

        value = get_normalized_percentage_of_time_passed(self._change_controller.last_change_datetime, self._change_controller.change_datetime)
        self._time_until_vulnerability_change_gauge_circular.SetValue(value, animate=animate)

    def enter(self):
        if self._change_controller:
            self._change_controller.sync()
            self._change_controller.connect()
        self.bracket_thether = BracketTether(name='link_with_ship_tether', parent=self.panel._ui, align=uiconst.TOPLEFT, collapsed=True, on_close_point_click=self._on_close_point_click, on_click=self._on_close_point_click)
        self.refresh_main_grid()
        self.collapsed = True
        uthread2.start_tasklet(self.camera_loop)

    def SetupNameAndOwner(self):
        typeName = evetypes.GetName(self.type_id)
        TextHeadline(parent=self.mainGrid, align=uiconst.TOPLEFT, text=typeName, color=eveColor.WHITE)
        ownerName = cfg.eveowners.Get(self.owner_id).name
        TextBody(parent=self.mainGrid, align=uiconst.TOPLEFT, text=ownerName)

    def SetupShields(self):
        self.shieldContainer = LinkWithShipShieldCont(name='shieldContainer', parent=self.mainGrid, width=150, align=uiconst.TOPLEFT, height=12, top=12, bottom=12)

    def SetupLinkButton(self, includeWarning, display):
        self._interface_cont = Container(parent=self.mainGrid, align=uiconst.TOPLEFT, width=150, height=60, top=14, display=display, enabled=display)
        self.buttonGrid = LayoutGrid(name='buttonGrid', parent=self._interface_cont, columns=2, align=uiconst.TOPLEFT)
        self._linkButton = Button(name='BeginLinkButton', parent=self.buttonGrid, label=GetByLabel(GetLinkButtonLabelPath(self.type_id)), args=(), func=self._link, height=30)
        if includeWarning:
            LinkWarningIcon(parent=self.buttonGrid, name='warningIcon', texturePath='res:/UI/Texture/classes/crab/warningIcon.png', width=36, height=36, state=uiconst.UI_NORMAL, characterEnergyCost=self.characterEnergyCost, linkDuration=self.linkDuration, typeID=self.type_id)

    def _link(self):
        self.initiate_link_function(sm.GetService('michelle'), self.item_id)

    def _on_close_point_click(self):
        if self.collapsed:
            self.player_action = OPENED_BY_PLAYER
            self.expand()
        else:
            self.player_action = COLLAPSED_BY_PLAYER
            self.collapse()

    def camera_loop(self):
        while self.run_camera_loop:
            distance = self.panel._camera.distance_from_transform(self.panel._transform)
            if distance > SCALING_BILLBOARD_THRESHOLD:
                if self.player_action == COLLAPSED_BY_PLAYER:
                    self.player_action = NO_ACTION
                elif self.player_action == NO_ACTION:
                    self.collapse()
            elif self.player_action == OPENED_BY_PLAYER:
                self.player_action = NO_ACTION
            elif self.player_action == NO_ACTION:
                self.expand()
            eveui.wait_for_next_frame()

    def disable(self):
        if self._interface_cont:
            self._interface_cont.display = False
            self._interface_cont.enabled = False

    def enable(self):
        if self._interface_cont:
            self._interface_cont.display = True
            self._interface_cont.enabled = True

    def updateLinkButton(self, tooltip, busy):
        if self._linkButton:
            self.enable()
            self._linkButton.enabled = not bool(tooltip)
            self._linkButton.busy = busy
            self._linkButton.hint = tooltip

    def exit(self):
        if self._change_controller:
            self._change_controller.disconnect()
        self.run_camera_loop = False
        self.bracket_thether.collapse()
        if self._interface_cont:
            uicore.animations.FadeOut(self._interface_cont)
        uicore.animations.FadeOut(self.bracket_thether, sleep=True)
        self.panel._ui.Flush()
        self.panel.button_cont.Flush()

    def expand(self):
        if self.collapsed:
            self.bracket_thether.expand()
            self.collapsed = False
            animations.MorphScalar(self.panel.button_cont, 'left', startVal=self.panel.button_cont.left, endVal=0, duration=0.2, timeOffset=0.2)
            animations.FadeIn(self.panel.button_cont, duration=0.2, timeOffset=0.2)

    def collapse(self):
        if not self.collapsed:
            self.panel.button_cont.DisableAutoSize()
            self.bracket_thether.collapse()
            self.collapsed = True
            animations.MorphScalar(self.panel.button_cont, 'left', startVal=self.panel.button_cont.left, endVal=-20, duration=0.2)
            animations.FadeOut(self.panel.button_cont, duration=0.2, callback=self.panel.button_cont.EnableAutoSize)

    def _toggle_collapse(self):
        if self.collapsed:
            self.expand()
        else:
            self.collapse()


class LinkWithShipShieldCont(Container):
    default_name = 'LinkWithShipShieldCont'
    __notifyevents__ = ['OnSkyhookSiloDamageUpdated']
    default_shieldGreyColor = eveColor.LED_GREY
    default_shieldBlueColor = eveColor.FOCUS_BLUE
    default_shieldRedColor = eveColor.DANGER_RED

    def ApplyAttributes(self, attributes):
        super(LinkWithShipShieldCont, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.shieldGrid = LayoutGrid(parent=self, columns=12, align=uiconst.TOPLEFT, cellSpacing=(2, 2), height=16)
        self.icon = Sprite(name='shieldIcon', parent=self.shieldGrid, align=uiconst.CENTERRIGHT, left=4, width=16, height=16, padright=2, texturePath=eveicon.shields)
        self.bars = []
        for i in range(10):
            bar = Fill(align=uiconst.TOLEFT, parent=self.shieldGrid, width=8, Height=12, padTop=2, padBottom=2)
            self.bars.append(bar)

        self.shieldLabel = TextDetail(name='shieldLabel', parent=self.shieldGrid, align=uiconst.TOPLEFT, padLeft=2)

    def OnSkyhookSiloDamageUpdated(self, shieldPercentage):
        shieldPercentage = round(shieldPercentage, 1)
        self.icon.color = self.default_shieldBlueColor
        if shieldPercentage <= 10:
            self.icon.color = self.default_shieldRedColor
        for i, bar in enumerate(self.bars):
            if shieldPercentage > i * 10:
                if shieldPercentage <= 10:
                    bar.color = self.default_shieldRedColor
                else:
                    bar.color = self.default_shieldBlueColor
                    bar.outputMode = uiconst.OUTPUT_COLOR_AND_GLOW
                    bar.glowBrightness = 0.5
            else:
                bar.color = self.default_shieldGreyColor

        self.shieldLabel.text = u'{}%'.format(shieldPercentage)


class LinkWarningIcon(Sprite):

    def ApplyAttributes(self, attributes):
        super(LinkWarningIcon, self).ApplyAttributes(attributes)
        self.characterEnergyCost = attributes.get('characterEnergyCost')
        self.linkDuration = attributes.get('linkDuration')
        self.typeID = attributes.get('typeID')

    def LoadTooltipPanel(self, tooltipPanel, *args):
        grid = LayoutGrid(state=uiconst.UI_NORMAL, columns=2)
        warningSprite = Sprite(align=uiconst.CENTERLEFT, name='warningIcon', texturePath='res:/UI/Texture/classes/crab/warningIcon.png', width=36, height=36, state=uiconst.UI_NORMAL)
        title = EveLabelLarge(text=GetByLabel(GetLinkButtonLabelPath(self.typeID)), bold=True)
        warningLabel = EveLabelMedium(text=GetByLabel('UI/Inflight/SpaceComponents/LinkWithShip/WarnTooltip', linkDuration=self.linkDuration * SEC))
        warningLabel.maxWidth = 190
        energyState = sm.GetService('characterEnergySvc').GetEnergyStateNow()
        energyGauge = Gauge(value=energyState.normalisedEnergyLevel, color=Color.HextoRGBA('#40BBEC'))
        if self.characterEnergyCost is not None:
            maxActivations = int(round(energyState.quiescentEnergyLevel / self.characterEnergyCost))
            for i in range(maxActivations):
                energyGauge.ShowMarker(float(i) / maxActivations, color=Color.BLACK, width=3)

        energyLabel = EveLabelMedium(text=GetByLabel('UI/CharacterEnergy/AvailableEnergy'))
        energyDisplayGrid = LayoutGrid(state=uiconst.UI_NORMAL, columns=2)
        energyDisplayGrid.AddCell(energyLabel, colSpan=1)
        energyDisplayGrid.AddCell(energyGauge, colSpan=1, cellPadding=(5, 7, 0, 0))
        grid.AddCell(title, colSpan=2, cellPadding=(0, 5, 0, 5))
        grid.AddCell(warningSprite, rowSpan=2, cellPadding=(0, 0, 0, 0))
        grid.AddCell(warningLabel, colSpan=1)
        tooltipPanel.AddCell(grid, colSpan=tooltipPanel.columns, cellPadding=(10, 5, 15, 5))
        tooltipPanel.AddCell(energyDisplayGrid, colSpan=tooltipPanel.columns, cellPadding=(10, 5, 5, 5))
