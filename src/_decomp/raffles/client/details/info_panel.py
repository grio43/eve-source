#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\details\info_panel.py
import eveformat.client
import eveui
import uthread2
from carbon.common.script.util.format import FmtDate
from carbonui import TextColor
from datetimeutils import datetime_to_filetime
from eve.client.script.ui.control.infoIcon import InfoIcon
from eveui.compatibility import CarbonEventHandler
from raffles.client import texture
from raffles.client.localization import Text
from raffles.client.util import character_name, get_market_estimate_text, station_name
from raffles.client.widget.item_icon import ItemIcon
from raffles.client.widget.vertical_center_container import VerticalCenteredContainer

class InfoPanel(eveui.Container):
    default_name = 'InfoPanel'
    default_align = eveui.Align.to_top
    default_height = 100
    default_padBottom = 25

    def __init__(self, raffle, **kwargs):
        super(InfoPanel, self).__init__(**kwargs)
        self._raffle = raffle
        self._layout()
        self._on_status_changed()
        self._raffle.on_status_changed.connect(self._on_status_changed)
        uthread2.start_tasklet(self._time_remaining_routine)

    def Close(self):
        super(InfoPanel, self).Close()
        if self._raffle:
            self._raffle.on_status_changed.disconnect(self._on_status_changed)

    def _on_status_changed(self, *args, **kwargs):
        if not self._raffle.is_finished:
            expiration_label = Text.expires_in()
            expiration_value = self._raffle.time_remaining_text
        else:
            expiration_value = FmtDate(datetime_to_filetime(self._raffle.end_time), 'ln')
            if self._raffle.is_sold_out:
                expiration_label = Text.completion_date()
            else:
                expiration_label = Text.expiration_date()
        self.expiration_label.label.text = expiration_label
        self.expiration_label.value.text = expiration_value

    def _time_remaining_routine(self):
        while not self.destroyed:
            if self._raffle.is_finished:
                break
            self.expiration_label.value.text = self._raffle.time_remaining_text
            uthread2.sleep(1)

    def _layout(self):
        self._construct_left()
        self._construct_right()

    def _construct_left(self):
        container = eveui.Container(name='leftContainer', parent=self, align=eveui.Align.to_left, width=390)
        icon_container = eveui.Container(name='iconContainer', parent=container, align=eveui.Align.to_left, width=100, padRight=8)
        ItemIcon(parent=icon_container, type_id=self._raffle.type_id, item_id=self._raffle.item_id, is_copy=self._raffle.is_blueprint_copy)
        eveui.Sprite(parent=icon_container, align=eveui.Align.center, height=90, width=90, texturePath=texture.details_item_frame)
        info_container = VerticalCenteredContainer(parent=container)
        eveui.EveLabelSmall(parent=info_container, align=eveui.Align.to_top, text=self._raffle.item_group_name, color=TextColor.SECONDARY)
        name_container = eveui.ContainerAutoSize(parent=info_container, align=eveui.Align.to_top)
        width, height = eveui.EveCaptionMedium.MeasureTextSize(self._raffle.item_name)
        if width <= 270:
            label_class = eveui.EveCaptionMedium
            max_lines = 1
            info_icon_left = 8
            info_icon_top = 4
        else:
            label_class = eveui.EveLabelLarge
            max_lines = 2
            info_icon_left = 4
            info_icon_top = 2
        label_class(parent=name_container, align=eveui.Align.top_left, text=self._raffle.item_name, maxWidth=270, padRight=24, maxLines=max_lines)
        InfoIcon(parent=name_container, align=eveui.Align.top_left, top=info_icon_top, left=width + info_icon_left, itemID=self._raffle.item_id, typeID=self._raffle.type_id)
        eveui.EveLabelMedium(parent=info_container, align=eveui.Align.to_top, top=6, color=TextColor.SECONDARY, text=get_market_estimate_text(self._raffle.type_id, self._raffle.item_id))
        link_cont = eveui.ContainerAutoSize(parent=info_container, align=eveui.Align.to_top, top=8)
        HyperLink(parent=link_cont, align=eveui.Align.top_left, raffle=self._raffle)

    def _construct_right(self):
        container = eveui.Container(name='rightContainer', parent=self, padding=(12, 16, 12, 16))
        group_1 = eveui.Container(parent=container, name='group_1', align=eveui.Align.to_left, width=125)
        LabelValue(parent=group_1, align=eveui.Align.to_top, label=Text.tickets(), value=self._raffle.ticket_count)
        ticket_price = eveformat.isk(self._raffle.ticket_price)
        ticket_price_label = LabelValue(parent=group_1, align=eveui.Align.to_bottom, label=Text.ticket_price(), value=ticket_price)
        t = ticket_price_label.value
        t.state = eveui.State.normal
        if self._raffle.good_value:
            t.SetTextColor(TextColor.SUCCESS)
            t.SetHint(u'{}\n{}'.format(ticket_price, Text.good_value_hint()))
        elif self._raffle.bad_value:
            t.SetTextColor(TextColor.WARNING)
            t.SetHint(u'{}\n{}'.format(ticket_price, Text.bad_value_hint()))
        else:
            t.SetHint(ticket_price)
        group_2 = eveui.Container(name='group_2', parent=container, align=eveui.Align.to_left_prop, width=0.45, paddLeft=12)
        location = LabelValue(parent=group_2, align=eveui.Align.to_top, label=Text.location(), value=u'{}\n{}'.format(eveformat.color(text=eveformat.solar_system_with_security_and_jumps(self._raffle.solar_system_id), color=(1.0, 1.0, 1.0)), station_name(self._raffle.location_id, linkify=True)), max_lines=2, height=48)
        location.value.state = eveui.State.normal
        location.value.opacity = 0.75
        group_3 = eveui.Container(parent=container, name='group_3', padLeft=12)
        portrait_container = eveui.Container(parent=group_3, align=eveui.Align.top_left, height=46, width=46)
        self.portrait = eveui.CharacterPortrait(parent=portrait_container, size=46, character_id=self._raffle.owner_id)
        eveui.Frame(parent=portrait_container, padding=-1, opacity=0.5)
        creator = LabelValue(parent=group_3, align=eveui.Align.to_top, padLeft=54, label=Text.created_by(), value=character_name(self._raffle.owner_id, linkify=True))
        creator.value.state = eveui.State.normal
        creator.value.opacity = 0.75
        self.expiration_label = LabelValue(parent=group_3, align=eveui.Align.to_bottom)
        self.expiration_label.height = 16
        self.expiration_label.label.align = eveui.Align.to_left
        self.expiration_label.label.top = 2
        self.expiration_label.value.align = eveui.Align.to_left
        self.expiration_label.value.left = 6
        self.expiration_label.value.width = 100


class LabelValue(eveui.Container):
    default_height = 29

    def __init__(self, label = u'', value = u'', max_lines = 1, **kwargs):
        super(LabelValue, self).__init__(**kwargs)
        self.label = eveui.EveLabelSmall(parent=self, align=eveui.Align.to_top, text=label, color=TextColor.SECONDARY, maxLines=1)
        self.value = eveui.EveLabelMedium(parent=self, align=eveui.Align.to_top, text=value, maxLines=max_lines)


class HyperLink(CarbonEventHandler, eveui.ContainerAutoSize):
    default_state = eveui.State.normal
    isDragObject = True

    def __init__(self, raffle, **kwargs):
        self._raffle = raffle
        super(HyperLink, self).__init__(**kwargs)
        self._layout()

    def _layout(self):
        icon = eveui.ButtonIcon(parent=self, align=eveui.Align.top_left, state=eveui.State.disabled, texture_path=texture.hyperlink_icon, size=20, bgColor=(0.16, 0.21, 0.23, 1))
        self.on_mouse_enter = icon.on_mouse_enter
        self.on_mouse_exit = icon.on_mouse_exit
        if self._raffle.is_private:
            eveui.Frame(bgParent=self, texturePath=texture.panel_1_corner_3px, cornerSize=3, opacity=0.06)
            private_label = eveui.EveLabelMedium(parent=self, align=eveui.Align.top_left, state=eveui.State.disabled, top=3, left=28, text=Text.private_raffle())
            private_label.padRight = 8

    def GetHint(self):
        hint = Text.link_button_hint()
        if self._raffle.is_private:
            hint += u'<br><br>{}'.format(Text.private_raffle_hint())
        return hint

    def GetDragData(self):
        return [self._raffle.get_drag_data()]
