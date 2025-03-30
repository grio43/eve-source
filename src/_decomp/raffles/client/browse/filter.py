#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\browse\filter.py
import eveui
from carbonui import TextColor
from raffles.client import texture
from raffles.client.constants import BlueprintType
from raffles.client.localization import Text, get_blueprint_type_name
from raffles.client.widget.chip import ChipGroup, Chip, ItemTypeChip, ItemGroupChip, ItemCategoryChip, SolarSystemChip, RangeChip, MetaGroupChip
from raffles.client.widget.filter_sliders import TicketCountSlider, TicketPriceSlider
from raffles.client.widget.meta_group_combo import MetaGroupCombo
from raffles.client.widget.saved_filter_combo import saved_filter_combo
from raffles.client.widget.side_sheet import SideSheet

class Filter(SideSheet):
    field_padding = 20

    def __init__(self, controller, on_apply, **kwargs):
        self._controller = controller
        self._on_apply = on_apply
        super(Filter, self).__init__(title=Text.filters(), icon=texture.filter_icon, content_width=420, content_height=465, **kwargs)
        self._update_filter_chips()
        self._update_blueprint()
        self._controller.on_change.connect(self._filter_changed)

    def Close(self):
        super(Filter, self).Close()
        self._controller.on_change.disconnect(self._filter_changed)

    def _filter_changed(self):
        self._on_apply()
        self._update_fields()
        self._update_filter_chips()

    def _reset(self, *args):
        self._controller.reset_filter()

    def _on_item_field_changed(self, instance, suggestion):
        self._controller.item_suggestion = suggestion

    def _on_solar_system_field_changed(self, instance, solar_system_id):
        self._controller.solar_system_id = solar_system_id

    def _update_fields(self):
        self.item_field.complete(self._controller.item_suggestion)
        self.solar_system_field.location_id = self._controller.solar_system_id
        self.meta_group_combo.SelectItemByValue(self._controller.meta_group_id)
        self._update_blueprint()
        self.ticket_count_slider.commit_value(self._controller.ticket_count)
        self.ticket_price_slider.commit_value(self._controller.ticket_price)

    def _update_blueprint(self):
        self.blueprint_combo.SelectItemByValue(self._controller.blueprint_type)
        if self._controller.is_blueprint:
            self.blueprint_container.state = eveui.State.pick_children
        else:
            self.blueprint_container.state = eveui.State.hidden

    def _update_filter_chips(self):
        self.active_type.type_id = self._controller.type_id
        self.active_group.group_id = self._controller.group_id
        self.active_category.category_id = self._controller.category_id
        self.active_blueprint_type.text = self._get_blueprint_type_text()
        self.active_meta_group.meta_group_id = self._controller.meta_group_id
        self.active_location.solar_system_id = self._controller.solar_system_id
        self.active_ticket_count.update(min=self._controller.min_ticket_count_label, max=self._controller.max_ticket_count_label)
        self.active_ticket_price.update(min=self._controller.min_ticket_price_label, max=self._controller.max_ticket_price_label)

    def _get_blueprint_type_text(self):
        if not self._controller.is_blueprint or self._controller.blueprint_type == BlueprintType.all:
            return ''
        return Text.blueprint_chip(blueprint_type=get_blueprint_type_name(self._controller.blueprint_type))

    def _handle_meta_group(self, combo, key, value):
        self._controller.meta_group_id = value

    def _handle_blueprint_type(self, combo, key, value):
        self._controller.blueprint_type = value

    def _clear_blueprint_type(self):
        self._controller.blueprint_type = BlueprintType.all

    def _clear_ticket_price(self, *args):
        self.ticket_price_slider.commit_value((self._controller.ticket_price_increments[0], self._controller.ticket_price_increments[-1]))

    def _clear_ticket_count(self, *args):
        self.ticket_count_slider.commit_value((self._controller.ticket_count_increments[0], self._controller.ticket_count_increments[-1]))

    def on_open(self):
        self.item_field.focused = True

    def _layout(self):
        self._construct_active_filters()
        super(Filter, self)._layout()
        self._construct_content()

    def _construct_active_filters(self):
        chip_group = ChipGroup(on_clear_all=self._reset, parent=self, align=eveui.Align.to_top, height=32, padLeft=50, padRight=8)
        self.active_type = ItemTypeChip(on_clear=lambda *args: self.item_field.clear())
        chip_group.add_chip(self.active_type)
        self.active_group = ItemGroupChip(on_clear=lambda *args: self.item_field.clear())
        chip_group.add_chip(self.active_group)
        self.active_category = ItemCategoryChip(on_clear=lambda *args: self.item_field.clear())
        chip_group.add_chip(self.active_category)
        self.active_blueprint_type = Chip(on_clear=self._clear_blueprint_type)
        chip_group.add_chip(self.active_blueprint_type)
        self.active_meta_group = MetaGroupChip(on_clear=lambda *args: self.meta_group_combo.clear())
        chip_group.add_chip(self.active_meta_group)
        self.active_location = SolarSystemChip(on_clear=lambda *args: self.solar_system_field.clear())
        chip_group.add_chip(self.active_location)
        self.active_ticket_price = RangeChip(on_clear=self._clear_ticket_price, label=Text.chip_price())
        chip_group.add_chip(self.active_ticket_price)
        self.active_ticket_count = RangeChip(on_clear=self._clear_ticket_count, label=Text.chip_ticket_count())
        chip_group.add_chip(self.active_ticket_count)

    def _construct_content(self):
        container = self.content_container
        left = eveui.Container(parent=container, align=eveui.Align.to_left_prop, width=0.5, padRight=10)
        right = eveui.Container(parent=container, align=eveui.Align.to_all, padLeft=10)
        self._construct_left(left)
        self._construct_right(right)

    def _construct_left(self, container):
        InputLabel(parent=container, text=Text.filter_item_label())
        self.item_field = eveui.ItemField(parent=container, align=eveui.Align.to_top, padBottom=self.field_padding, completed_suggestion=self._controller.item_suggestion, category_filter=self._controller.filter_category)
        self.item_field.bind(completed_suggestion=self._on_item_field_changed)
        self.blueprint_container = eveui.ContainerAutoSize(parent=container, state=eveui.State.hidden, align=eveui.Align.to_top)
        InputLabel(parent=self.blueprint_container, align=eveui.Align.to_top, text=Text.filter_blueprint_label())
        self.blueprint_combo = eveui.Combo(parent=self.blueprint_container, align=eveui.Align.to_top, padBottom=self.field_padding, options=self._controller.blueprint_options, callback=self._handle_blueprint_type, select=self._controller.blueprint_type)
        InputLabel(parent=container, text=Text.filter_meta_group_label())
        self.meta_group_combo = MetaGroupCombo(parent=container, align=eveui.Align.to_top, padBottom=self.field_padding, callback=self._handle_meta_group, select=self._controller.meta_group_id)
        InputLabel(parent=container, text=Text.filter_location_label())
        self.solar_system_field = eveui.SolarSystemField(parent=container, align=eveui.Align.to_top, padBottom=self.field_padding, location_id=self._controller.solar_system_id)
        self.solar_system_field.bind(location_id=self._on_solar_system_field_changed)
        saved_filter_combo(parent=container, align=eveui.Align.to_bottom, filter_controller=self._controller, settings_key='raffles_browse_saved_filters')
        InputLabel(parent=container, align=eveui.Align.to_bottom, text=Text.saved_filters())

    def _construct_right(self, container):
        actions_container = eveui.Container(parent=container, align=eveui.Align.to_bottom, height=28)
        self.reset_button = eveui.Button(parent=actions_container, align=eveui.Align.center_right, label=Text.reset(), func=self._reset)
        InputLabel(parent=container, text=Text.ticket_price())
        self.ticket_price_slider = TicketPriceSlider(parent=container, filter_controller=self._controller, padBottom=self.field_padding)
        InputLabel(parent=container, text=Text.ticket_count_label())
        self.ticket_count_slider = TicketCountSlider(parent=container, filter_controller=self._controller)


class InputLabel(eveui.EveLabelMedium):
    default_align = eveui.Align.to_top
    default_padBottom = 4
    default_color = TextColor.SECONDARY
