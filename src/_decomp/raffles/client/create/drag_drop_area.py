#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\create\drag_drop_area.py
import math
import eveformat
import eveui
import evetypes
from raffles.client import sound, texture
from raffles.client.localization import Text
from raffles.client.widget.error_tooltip import show_error_tooltip
from raffles.client.widget.item_icon import ItemIcon

class DragDropArea(eveui.Container):
    default_name = 'ItemDragDrop'
    default_align = eveui.Align.center
    default_width = 180
    default_height = 180
    quantity_background_color_normal = (0.0, 0.0, 0.0, 0.9)
    quantity_background_color_hint = (0.2, 0.6, 1.0, 0.6)

    def __init__(self, controller, **kwargs):
        self._controller = controller
        super(DragDropArea, self).__init__(**kwargs)
        self._layout()
        self._controller.on_item_changed.connect(self._on_item_changed)
        self._controller.on_drag_enter.connect(self._on_drag_enter)
        self._controller.on_drag_exit.connect(self._on_drag_exit)
        self._controller.on_item_error.connect(self._on_item_error)

    def Close(self):
        self._controller.on_item_changed.disconnect(self._on_item_changed)
        self._controller.on_drag_enter.disconnect(self._on_drag_enter)
        self._controller.on_drag_exit.disconnect(self._on_drag_exit)
        self._controller.on_item_error.disconnect(self._on_item_error)

    @property
    def border_padding(self):
        return self.border_container.padLeft

    @border_padding.setter
    def border_padding(self, value):
        self.border_container.padding = value

    @property
    def corner_padding(self):
        return self.corner_container.padLeft

    @corner_padding.setter
    def corner_padding(self, value):
        self.corner_container.padding = value

    def _layout(self):
        container = eveui.Container(parent=self, align=eveui.Align.center, width=self.default_width, height=self.default_height)
        self.error_position = eveui.Container(parent=self, top=16)
        icon_cont = eveui.Container(parent=container, align=eveui.Align.center, width=64, height=64)
        self.item_icon = ItemIcon(parent=icon_cont, item=self._controller.item)
        self.item_icon.isDragObject = False
        self.item_icon.OnDropData = self.OnDropData
        self.item_icon.OnDragEnter = self.OnDragEnter
        self.item_icon.OnDragExit = self.OnDragExit
        self.item_icon.GetHint = self.GetHint
        self.quantity_cont = eveui.Container(parent=icon_cont, align=eveui.Align.bottom_right, state=eveui.State.hidden, pos=(1, 1, 16, 16), bgColor=self.quantity_background_color_normal, idx=0)
        eveui.EveLabelSmallBold(parent=self.quantity_cont, align=eveui.Align.center, text='1')
        self._update_quantity_cont()
        self._construct_frame(container)

    def _get_border_padding(self):
        if self._controller.item:
            return 10
        return 0

    def _get_corner_padding(self):
        if self._controller.item:
            return 0
        return 6

    def _construct_frame(self, parent):
        eveui.Sprite(parent=parent, align=eveui.Align.center, width=110, height=110, texturePath=texture.create_item_background)
        self.border_container = eveui.Container(parent=parent, align=eveui.Align.center, width=160, height=160, padding=self._get_border_padding())
        Border(parent=self.border_container, align=eveui.Align.center_top)
        Border(parent=self.border_container, align=eveui.Align.center_bottom, rotation=math.pi)
        Border(parent=self.border_container, align=eveui.Align.center_right, rotation=-math.pi * 0.5, swap_size=True)
        Border(parent=self.border_container, align=eveui.Align.center_left, rotation=math.pi * 0.5, swap_size=True)
        self.corner_container = eveui.Container(parent=parent, padding=self._get_corner_padding())
        CornerLine(parent=self.corner_container, align=eveui.Align.top_right, rotation=math.pi * 0.75)
        CornerLine(parent=self.corner_container, align=eveui.Align.top_left, rotation=-math.pi * 0.75)
        CornerLine(parent=self.corner_container, align=eveui.Align.bottom_right, rotation=math.pi * 0.25)
        CornerLine(parent=self.corner_container, align=eveui.Align.bottom_left, rotation=math.pi * 0.75)

    def _on_item_error(self, error, error_kwargs):
        show_error_tooltip(self.error_position, error, error_kwargs)

    def _on_drag_enter(self, item):
        if self._controller.item is not None and item == self._controller.item:
            return
        if item.typeID == self._controller.token_type_id:
            return
        eveui.animate(self, 'border_padding', end_value=-4, duration=0.1)

    def _on_drag_exit(self, item = None):
        eveui.animate(self, 'border_padding', end_value=self._get_border_padding(), duration=0.1)

    def _on_item_changed(self):
        self._on_drag_exit()
        eveui.play_sound(sound.create_item_changed)
        self._controller.focus_window()
        self.item_icon.item = self._controller.item
        if self._controller.item:
            self.item_icon.Show()
        else:
            self.item_icon.Hide()
        self._update_quantity_cont()
        eveui.animate(self, 'border_padding', end_value=self._get_border_padding(), duration=0.1)
        eveui.animate(self, 'corner_padding', end_value=self._get_corner_padding(), duration=0.1)

    def _update_quantity_cont(self):
        hint = None
        background_color = self.quantity_background_color_normal
        state = eveui.State.hidden
        if self._controller.item and self._controller.item.quantity > 0:
            if self._controller.item.stacksize > 1:
                background_color = self.quantity_background_color_hint
                state = eveui.State.normal
                hint = Text.quantity_stack_hint(stack_size=eveformat.number(self._controller.item.stacksize))
            else:
                state = eveui.State.pick_children
        self.quantity_cont.hint = hint
        self.quantity_cont.background_color = background_color
        self.quantity_cont.state = state

    def OnDropData(self, source, data):
        self._controller.drop_data(data)

    def OnDragEnter(self, source, data):
        item = getattr(data[0], 'item', None)
        if item:
            self._on_drag_enter(item)

    def OnDragExit(self, source, data):
        self._on_drag_exit()

    def GetHint(self):
        if self._controller.item is None:
            return
        return '<b>%s</b>\n%s' % (evetypes.GetName(self._controller.item.typeID), evetypes.GetDescription(self._controller.item.typeID))


class Border(eveui.Sprite):
    default_texturePath = texture.create_item_border
    default_width = 120
    default_height = 10

    def __init__(self, swap_size = False, **kwargs):
        if swap_size:
            kwargs.setdefault('width', self.default_height)
            kwargs.setdefault('height', self.default_width)
        super(Border, self).__init__(**kwargs)


class CornerLine(eveui.Transform):
    default_height = 30
    default_width = 30

    def __init__(self, **kwargs):
        super(CornerLine, self).__init__(**kwargs)
        eveui.Line(parent=self, align=eveui.Align.center, state=eveui.State.disabled, height=30, width=1, left=-1, opacity=0.15)
