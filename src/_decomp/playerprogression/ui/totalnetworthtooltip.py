#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\playerprogression\ui\totalnetworthtooltip.py
from carbon.common.script.util.timerstuff import AutoTimer
import carbonui.const as uiconst
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.shared.neocom.wallet import walletUtil
from eve.common.lib import appConst
from localization import GetByLabel
from uthread2 import StartTasklet, call_after_wallclocktime_delay
from carbonui.uicore import uicore
TOOLTIP_WIDTH = 16
TOOLTIP_CLEAR_DELAY_SEC = 0.05
STATE_UPDATE_DELAY_MSEC = 2000
COUNTER_COLOR = '<color=0xffaaaaaa>'
DISCLAIMER_LABEL_PATH = 'UI/VisualProgressStats/TotalNetWorthDisclaimer'
DISCLAIMER_PADDING = (10, 2, 2, 5)

class TotalNetWorthTooltipButton(ButtonIcon):
    default_texturePath = 'res:/UI/Texture/Icons/generic/more_info_16.png'
    default_width = TOOLTIP_WIDTH
    default_height = TOOLTIP_WIDTH
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(TotalNetWorthTooltipButton, self).ApplyAttributes(attributes)
        self.data = attributes['data']
        self._wallet_svc = sm.GetService('wallet')
        self.tooltip_popup = None
        self.is_loading = False
        self.update_thread = None

    def OnMouseEnter(self, *args):
        super(TotalNetWorthTooltipButton, self).OnMouseEnter(*args)
        self.show_tooltip()

    def OnMouseExit(self, *args):
        super(TotalNetWorthTooltipButton, self).OnMouseExit(*args)
        self.hide_tooltip()

    def show_tooltip(self):
        if not self.is_tooltip_available():
            self.is_loading = True
            self.tooltip_popup = uicore.uilib.tooltipHandler.LoadPersistentTooltip(owner=self)
            self.load_tooltip()

    def load_tooltip(self):
        self.tooltip_popup.state = uiconst.UI_NORMAL
        self.tooltip_popup.LoadGeneric3ColumnTemplate()
        self.tooltip_popup.margin = (2, 2, 9, 2)
        for component in self.data.get_components():
            if self.should_display_component(component, component.get_value()):
                cell_obj, button_obj, label_obj, value_obj = self.tooltip_popup.AddButtonLabelValue(name=component.name, buttonTexturePath=component.icon_path, buttonFunc=component.button_function, buttonSize=component.icon_size, label=component.label)
                setattr(self.tooltip_popup, 'cell' + component.name, cell_obj)
                setattr(self.tooltip_popup, 'label' + component.name, label_obj)
                setattr(self.tooltip_popup, 'valueLabel' + component.name, value_obj)

        self.tooltip_popup.AddLabelSmall(name='disclaimer_label', text='<i>%s</i>' % GetByLabel(DISCLAIMER_LABEL_PATH), colSpan=self.tooltip_popup.columns, padding=DISCLAIMER_PADDING, align=uiconst.TOTOP)
        self.update_data()
        self.is_loading = False

    def should_display_component(self, component, new_value):
        if component in self.data.get_components_always_visible():
            return True
        should_display = new_value > 0
        return should_display

    def get_tooltip_value_obj(self, component):
        return getattr(self.tooltip_popup, 'valueLabel' + component.name, None)

    def get_tooltip_cell_obj(self, component):
        return getattr(self.tooltip_popup, 'cell' + component.name, None)

    def hide_tooltip(self):
        if self.is_tooltip_available():
            self.tooltip_popup.CloseWithFade()
        call_after_wallclocktime_delay(self.clear_tooltip, TOOLTIP_CLEAR_DELAY_SEC)

    def clear_tooltip(self):
        if self.is_tooltip_available():
            self.tooltip_popup.Flush()
            self.tooltip_popup.Close()
        self.is_loading = False
        self.tooltip_popup = None
        self.update_thread = None

    def is_tooltip_available(self):
        return self.tooltip_popup and not self.tooltip_popup.destroyed

    def update_data(self, tooltip_data = None):
        if not self.is_tooltip_available():
            return
        if tooltip_data is None:
            tooltip_data = self.data.get_tooltip_data(get_old=True)
        if self.update_thread:
            self.update_thread = AutoTimer(STATE_UPDATE_DELAY_MSEC, self._update_state, tooltip_data)
        else:
            self.update_thread = StartTasklet(self._update_state, tooltip_data)

    def _update_state(self, tooltip_data):
        try:
            if not self._update_tooltip_display(tooltip_data):
                self._update_tooltip_values(tooltip_data)
        finally:
            self.update_thread = None

    def _update_tooltip_display(self, tooltip_data):
        if self.is_loading:
            return False
        should_update = self._should_update_display(self.data.market_data, tooltip_data.market_snapshot) or self._should_update_display(self.data.contract_data, tooltip_data.contract_snapshot) or self._should_update_display(self.data.plex_data, tooltip_data.plex_snapshot)
        if should_update:
            self.clear_tooltip()
            self.show_tooltip()
            return True
        return False

    def _should_update_display(self, component, data_snapshot):
        if not self.is_tooltip_available():
            return False
        cell_obj = self.get_tooltip_cell_obj(component)
        _, new_value = data_snapshot
        old_display = cell_obj.display if cell_obj else False
        new_display = self.should_display_component(component, new_value)
        return old_display != new_display

    def _update_tooltip_values(self, tooltip_data):
        value_updates_data = [(self.get_tooltip_value_obj(self.data.wallet_data), tooltip_data.isk_snapshot), (self.get_tooltip_value_obj(self.data.assets_data), tooltip_data.assets_snapshot)]
        _, new_market_value = tooltip_data.market_snapshot
        if self.should_display_component(self.data.market_data, new_market_value):
            value_updates_data.append((self.get_tooltip_value_obj(self.data.market_data), tooltip_data.market_snapshot))
        _, new_contract_value = tooltip_data.contract_snapshot
        if self.should_display_component(self.data.contract_data, new_contract_value):
            value_updates_data.append((self.get_tooltip_value_obj(self.data.contract_data), tooltip_data.contract_snapshot))
        _, new_plex_value = tooltip_data.plex_snapshot
        if self.should_display_component(self.data.plex_data, new_plex_value):
            value_updates_data.append((self.get_tooltip_value_obj(self.data.plex_data), tooltip_data.plex_snapshot))
        for label, (_, value) in value_updates_data:
            label.SetText(walletUtil.GetBalanceFormatted(value, COUNTER_COLOR, appConst.creditsISK))
