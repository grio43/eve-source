#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\create\tokens.py
from carbonui import TextColor
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.client.script.ui.control.moreIcon import DescriptionIcon
import eveui
import eveformat
from raffles.client import sound, texture
from raffles.client.localization import Text
from raffles.client.widget.error_tooltip import show_error_tooltip
from raffles.client.widget.item_icon import ItemIcon

class Tokens(eveui.Container):
    default_height = 56
    default_state = eveui.State.normal

    def __init__(self, controller, **kwargs):
        self._controller = controller
        super(Tokens, self).__init__(**kwargs)
        self._layout()
        self._on_update()
        self._controller.on_token_changed.connect(self._on_token_changed)
        self._controller.on_price_changed.connect(self._on_update)
        self._controller.on_drag_enter.connect(self._on_drag_enter)
        self._controller.on_drag_exit.connect(self._on_drag_exit)
        self._controller.on_token_error.connect(self._on_token_error)

    def Close(self):
        super(Tokens, self).Close()
        self._controller.on_token_changed.disconnect(self._on_update)
        self._controller.on_price_changed.disconnect(self._on_update)
        self._controller.on_drag_enter.disconnect(self._on_drag_enter)
        self._controller.on_drag_exit.disconnect(self._on_drag_exit)
        self._controller.on_token_error.disconnect(self._on_token_error)

    def _on_drag_enter(self, item):
        if item.typeID == self._controller.token_type_id:
            error = self._controller.validate_token(item)
            if error:
                color = (1, 0.54, 0, 0.1)
            else:
                color = (1, 1, 1, 0.1)
            eveui.animate(self.feedback_frame, 'color', end_value=color, duration=0.1)

    def _on_drag_exit(self, item):
        eveui.fade_out(self.feedback_frame, duration=0.1)

    def _on_token_error(self, error):
        show_error_tooltip(self, error)

    def OnDropData(self, source, data):
        self._controller.drop_data(data)

    def OnDragEnter(self, source, data):
        item = getattr(data[0], 'item', None)
        if item:
            self._controller.on_drag_enter(item)

    def OnDragExit(self, source, data):
        item = getattr(data[0], 'item', None)
        if item:
            self._controller.on_drag_exit(item)

    def _on_token_changed(self):
        if self._controller.token:
            eveui.play_sound(sound.create_item_changed)
        self._on_update()

    def _on_update(self):
        self.tokens_required_label.text = Text.tokens_required(amount=self._controller.tokens_required)
        if self._controller.token:
            self.token_icon.opacity = 1
            self.token_amount_label.text = eveformat.number_readable_short(self._controller.token_amount)
            self.token_location_label.text = self._controller.token_location_name
            self.token_location_label.opacity = 1
            self.token_missing_label.Hide()
            self.warning_icon.height = 26
            self.warning_icon.width = 26
            self.warning_icon.align = eveui.Align.top_left
        else:
            self.token_icon.opacity = 0.5
            self.token_amount_label.text = ''
            self.token_location_label.opacity = 0
            self.token_missing_label.Show()
            self.warning_icon.height = 32
            self.warning_icon.width = 32
            self.warning_icon.align = eveui.Align.center
        if self._controller.has_enough_tokens:
            self.warning_icon.Hide()
            self.token_amount_label.SetTextColor(TextColor.HIGHLIGHT)
        else:
            self.warning_icon.Show()
            self.token_amount_label.SetTextColor(TextColor.WARNING)

    def _layout(self):
        self.feedback_frame = eveui.Frame(bgParent=self, texturePath=texture.panel_1_corner, cornerSize=9, padding=-6, opacity=0)
        description_container = eveui.Container(parent=self, align=eveui.Align.to_right, width=27)
        DescriptionIcon(parent=description_container, align=eveui.Align.center_right, tooltipPanelClassInfo=TokensTooltip(controller=self._controller))
        item_container = eveui.Container(parent=self, align=eveui.Align.to_left, width=56)
        self.warning_icon = eveui.Sprite(parent=item_container, align=eveui.Align.top_left, texturePath=texture.exclamation_icon, width=26, height=26, color=TextColor.WARNING)
        self.token_amount_label = eveui.EveLabelSmall(parent=item_container, align=eveui.Align.bottom_right, left=4, right=4, maxWidth=48, maxLines=1)
        self.token_icon = ItemIcon(parent=item_container, align=eveui.Align.center, width=46, height=46, item=self._controller.token, type_id=self._controller.token_type_id)
        self.token_icon.isDragObject = False
        self.token_icon.OnDropData = self.OnDropData
        self.token_icon.OnDragEnter = self.OnDragEnter
        self.token_icon.OnDragExit = self.OnDragExit
        eveui.Sprite(parent=item_container, align=eveui.Align.center, width=56, height=56, texturePath=texture.create_item_background)
        center_container = eveui.Container(parent=self, padding=(12, 4, 12, 4))
        self.tokens_required_label = eveui.EveLabelMedium(parent=center_container, align=eveui.Align.to_top, color=TextColor.HIGHLIGHT)
        self.token_missing_label = eveui.EveLabelLargeBold(parent=center_container, align=eveui.Align.to_top, text=Text.token_missing(), color=TextColor.SECONDARY)
        self.token_location_label = eveui.EveLabelSmall(name='TokenLocationLabel', parent=center_container, align=eveui.Align.to_top, padTop=4, maxLines=1)


class TokensTooltip(TooltipBaseWrapper):

    def __init__(self, controller, **kwargs):
        super(TokensTooltip, self).__init__(**kwargs)
        self._controller = controller

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric2ColumnTemplate()
        self.tooltipPanel.SetState(eveui.State.normal)
        self.tooltipPanel.margin = 12
        self.tooltipPanel.cellSpacing = 12
        self.tooltipPanel.AddLabelMedium(text=Text.tokens_tooltip(), colSpan=2, align=eveui.Align.to_top)
        market_button = eveui.Button(align=eveui.Align.center_top, label=Text.open_market(), texturePath=texture.market_icon, func=self._controller.open_market)
        nes_button = eveui.Button(align=eveui.Align.center_top, label=Text.open_nes(), texturePath=texture.new_eden_store_icon, func=self._controller.open_nes)
        self.tooltipPanel.AddCell(market_button)
        self.tooltipPanel.AddCell(nes_button)
        return self.tooltipPanel
