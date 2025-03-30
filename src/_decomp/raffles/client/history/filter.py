#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\history\filter.py
import eveui
from carbonui import TextColor
from raffles.client import texture
from raffles.client.constants import BlueprintType
from raffles.client.localization import Text, get_blueprint_type_name
from raffles.client.widget.chip import ChipGroup, Chip, ItemTypeChip, ItemGroupChip, ItemCategoryChip, SolarSystemChip, RangeChip, MetaGroupChip
from raffles.client.widget.checkbox import Checkbox
from raffles.client.widget.filter_sliders import TicketCountSlider, TicketPriceSlider
from raffles.client.widget.meta_group_combo import MetaGroupCombo
from raffles.client.widget.saved_filter_combo import saved_filter_combo
from raffles.client.widget.side_sheet import SideSheet
from .filter_controller import get_sort_options
checkbox_labels = {'show_joined': Text.show_joined(),
 'show_created': Text.show_created(),
 'show_active': Text.show_active(),
 'show_finished': Text.show_finished(),
 'show_public': Text.show_public(),
 'show_private': Text.show_private()}

class Filter(SideSheet):
    field_padding = 20

    def __init__(self, controller, **kwargs):
        self._controller = controller
        self._checkboxes = {}
        super(Filter, self).__init__(title=Text.filters(), icon=texture.filter_icon, content_width=500, content_height=436, **kwargs)
        self._update_filter_chips()
        self._update_blueprint()
        self._controller.on_change.connect(self._filter_changed)
        self._controller.on_sorting_changed.connect(self._sorting_changed)

    def Close(self):
        super(Filter, self).Close()
        self._controller.on_change.disconnect(self._filter_changed)
        self._controller.on_sorting_changed.disconnect(self._sorting_changed)

    def update_filtered_count(self, filtered, total):
        if filtered < total:
            self.showing_label.text = Text.showing_filtered(filtered_count=filtered, total_count=total)
        else:
            self.showing_label.text = ''

    def _filter_changed(self):
        self._update_fields()
        self._update_filter_chips()

    def _sorting_changed(self):
        self.sort_combo.SelectItemByValue(self._controller.sort_id)
        self._update_sort_button()

    def _reset(self, *args):
        self._controller.reset_all()

    def _on_item_field_changed(self, instance, suggestion):
        self._controller.item_suggestion = suggestion

    def _on_solar_system_field_changed(self, instance, solar_system_id):
        self._controller.solar_system_id = solar_system_id

    def _update_fields(self):
        self.item_field.complete(self._controller.item_suggestion)
        self.solar_system_field.location_id = self._controller.solar_system_id
        self.meta_group_combo.SelectItemByValue(self._controller.meta_group_id)
        self.ticket_count_slider.commit_value(self._controller.ticket_count)
        self.ticket_price_slider.commit_value(self._controller.ticket_price)
        self._update_blueprint()
        self._update_checkboxes()

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
        checkbox_changes = 0
        for checkbox_id in self._checkboxes.iterkeys():
            if self._controller.has_setting_changes(checkbox_id):
                checkbox_changes += 1

        if checkbox_changes:
            total_checkboxes = len(self._checkboxes)
            self.active_checkboxes.text = Text.chip_checkboxes(active=total_checkboxes - checkbox_changes, total=total_checkboxes)
        else:
            self.active_checkboxes.clear()

    def _get_blueprint_type_text(self):
        if not self._controller.is_blueprint or not self._controller.blueprint_type:
            return ''
        return Text.blueprint_chip(blueprint_type=get_blueprint_type_name(self._controller.blueprint_type))

    def _handle_meta_group(self, combo, key, value):
        self._controller.meta_group_id = value

    def _handle_checkbox(self, checkbox):
        self._controller.edit_setting(checkbox.name, checkbox.checked)

    def _handle_sort(self, combo, key, value):
        self._controller.sort_id = value
        self._update_sort_button()

    def _handle_sort_direction(self, *args):
        self._controller.sort_direction = not self._controller.sort_direction
        self._update_sort_button()

    def _update_sort_button(self):
        if self._controller.sort_id:
            self.sort_direction_button.Enable()
        else:
            self.sort_direction_button.Disable()
        self.sort_direction_button.texture_path = self._sort_direction_icon

    def _handle_blueprint_type(self, combo, key, value):
        self._controller.blueprint_type = value

    def _clear_blueprint_type(self):
        self._controller.blueprint_type = BlueprintType.all

    def _clear_ticket_price(self, *args):
        self.ticket_price_slider.commit_value((self._controller.ticket_price_increments[0], self._controller.ticket_price_increments[-1]))

    def _clear_ticket_count(self, *args):
        self.ticket_count_slider.commit_value((self._controller.ticket_count_increments[0], self._controller.ticket_count_increments[-1]))

    def _clear_checkboxes(self, *args):
        self._controller.reset_settings(self._checkboxes.keys())
        self._update_checkboxes()

    def _update_checkboxes(self):
        for checkbox_id, checkbox in self._checkboxes.iteritems():
            checkbox.checked = self._controller.get_setting(checkbox_id)

    @property
    def _sort_direction_icon(self):
        if self._controller.sorting[1]:
            return texture.sort_descending
        else:
            return texture.sort_ascending

    def on_open(self):
        self.item_field.focused = True

    def _layout(self):
        top_container = eveui.Container(parent=self, align=eveui.Align.to_top, height=28)
        showing_container = eveui.ContainerAutoSize(parent=top_container, align=eveui.Align.to_right)
        self.showing_label = eveui.EveLabelMedium(parent=showing_container, align=eveui.Align.center_right, color=TextColor.SECONDARY)
        self._construct_active_filters(top_container)
        super(Filter, self)._layout()
        self._construct_content()

    def _construct_active_filters(self, parent):
        chip_group = ChipGroup(on_clear_all=self._reset, parent=parent, align=eveui.Align.to_top, height=32, padLeft=50, padRight=8)
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
        self.active_checkboxes = Chip(on_clear=self._clear_checkboxes)
        chip_group.add_chip(self.active_checkboxes)

    def _construct_content(self):
        left = eveui.Container(parent=self.content_container, align=eveui.Align.to_left_prop, width=0.5, padRight=8)
        right = eveui.Container(parent=self.content_container, align=eveui.Align.to_all, padLeft=8)
        self._construct_left(left)
        self._construct_right(right)

    def _construct_sorting(self, parent):
        container = eveui.Container(parent=parent, align=eveui.Align.to_top, height=46, padBottom=self.field_padding)
        InputLabel(parent=container, text=Text.sort())
        self.sort_direction_button = SortDirectionButton(parent=container, align=eveui.Align.to_right, func=self._handle_sort_direction, hint=Text.sort_direction(), padLeft=4)
        self.sort_combo = eveui.Combo(parent=container, align=eveui.Align.to_all, options=get_sort_options(), callback=self._handle_sort, select=self._controller.sort_id)
        self._update_sort_button()

    def _construct_left(self, container):
        self._construct_sorting(container)
        InputLabel(parent=container, text=Text.filter_item_label())
        self.item_field = eveui.ItemField(parent=container, align=eveui.Align.to_top, padBottom=self.field_padding, completed_suggestion=self._controller.item_suggestion)
        self.item_field.bind(completed_suggestion=self._on_item_field_changed)
        self.blueprint_container = eveui.ContainerAutoSize(parent=container, state=eveui.State.hidden, align=eveui.Align.to_top)
        InputLabel(parent=self.blueprint_container, align=eveui.Align.to_top, text=Text.filter_blueprint_label())
        self.blueprint_combo = eveui.Combo(parent=self.blueprint_container, align=eveui.Align.to_top, padBottom=self.field_padding, options=self._controller.blueprint_options, callback=self._handle_blueprint_type, select=self._controller.blueprint_type)
        InputLabel(parent=container, text=Text.filter_meta_group_label())
        self.meta_group_combo = MetaGroupCombo(parent=container, align=eveui.Align.to_top, padBottom=self.field_padding, callback=self._handle_meta_group, select=self._controller.meta_group_id)
        InputLabel(parent=container, text=Text.filter_location_label())
        self.solar_system_field = eveui.SolarSystemField(parent=container, align=eveui.Align.to_top, padBottom=self.field_padding, location_id=self._controller.solar_system_id)
        self.solar_system_field.bind(location_id=self._on_solar_system_field_changed)
        saved_filter_combo(parent=container, align=eveui.Align.to_bottom, filter_controller=self._controller, settings_key='raffles_history_saved_filters')
        InputLabel(parent=container, align=eveui.Align.to_bottom, text=Text.saved_filters())

    def _construct_right(self, container):
        checkbox_container = eveui.ContainerAutoSize(parent=container, align=eveui.Align.to_top, padBottom=self.field_padding, clipChildren=True)
        InputLabel(parent=checkbox_container, text=Text.filter_checkboxes())
        self._construct_checkbox_group(checkbox_container, 'show_joined', 'show_created')
        self._construct_checkbox_group(checkbox_container, 'show_active', 'show_finished')
        self._construct_checkbox_group(checkbox_container, 'show_public', 'show_private')
        InputLabel(parent=container, text=Text.ticket_price())
        self.ticket_price_slider = TicketPriceSlider(parent=container, filter_controller=self._controller, padBottom=self.field_padding + 6)
        InputLabel(parent=container, text=Text.ticket_count_label())
        self.ticket_count_slider = TicketCountSlider(parent=container, filter_controller=self._controller, padBottom=self.field_padding + 6)
        self.reset_button = eveui.Button(parent=container, align=eveui.Align.bottom_right, label=Text.reset(), func=self._reset)

    def _construct_checkbox_group(self, parent, left_id, right_id):
        checkbox_group = eveui.Container(parent=parent, align=eveui.Align.to_top, height=26, padBottom=7, bgColor=(0.1, 0.1, 0.1, 0.5))
        checkbox = Checkbox(parent=checkbox_group, align=eveui.Align.to_left_prop, width=0.5, padRight=4, padLeft=4, text=checkbox_labels[left_id], checked=self._controller.get_setting(left_id), callback=self._handle_checkbox)
        checkbox.checkbox.name = left_id
        self._checkboxes[left_id] = checkbox
        checkbox = Checkbox(parent=checkbox_group, align=eveui.Align.to_left_prop, width=1, padLeft=4, padRight=4, text=checkbox_labels[right_id], checked=self._controller.get_setting(right_id), callback=self._handle_checkbox)
        checkbox.checkbox.name = right_id
        self._checkboxes[right_id] = checkbox


class InputLabel(eveui.EveLabelMedium):
    default_align = eveui.Align.to_top
    default_padBottom = 4
    default_color = TextColor.SECONDARY


class SortDirectionButton(eveui.Button):
    default_name = 'SortDirectionButton'
    default_fixedwidth = 30

    def __init__(self, icon_size = (14, 14), texture_path = None, **kwargs):
        super(SortDirectionButton, self).__init__(**kwargs)
        self._icon = eveui.Sprite(parent=self, align=eveui.Align.center, width=icon_size[0], height=icon_size[1], texturePath=texture_path)

    @property
    def texture_path(self):
        return self._icon.texturePath

    @texture_path.setter
    def texture_path(self, texture_path):
        self._icon.texturePath = texture_path

    def Enable(self):
        super(SortDirectionButton, self).Enable()
        self._icon.opacity = 1.0

    def Disable(self):
        super(SortDirectionButton, self).Disable()
        self._icon.opacity = 0.5
