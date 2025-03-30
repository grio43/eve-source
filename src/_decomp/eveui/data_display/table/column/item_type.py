#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\data_display\table\column\item_type.py
import evetypes
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.infoIcon import InfoIcon
from .base import BaseColumn
import eveui
from eveui.primitive.sprite import Sprite

class ItemTypeColumn(BaseColumn):

    def __init__(self, attribute_name, show_text = True, show_icon = True, show_info = True, icon_size = 32, **kwargs):
        kwargs.setdefault('id', attribute_name)
        super(ItemTypeColumn, self).__init__(**kwargs)
        self.attribute_name = attribute_name
        self._show_text = show_text
        self._show_icon = show_icon
        self._show_info = show_info
        self._icon_size = icon_size

    def render_cell(self):
        container = eveui.Container(name='ItemTypeContainer')
        if self._show_info:
            container.info_icon = InfoIcon(parent=container, align=eveui.Align.center_right, state=eveui.State.hidden, iconClass=Sprite)
        if self._show_icon:
            container.item_icon = ItemIcon(parent=container, state=eveui.State.disabled, align=eveui.Align.center_left, showOmegaOverlay=False, height=self._icon_size, width=self._icon_size)
        if self._show_text:
            container.type_name = eveui.EveLabelSmall(parent=container, align=eveui.Align.center_left)
            if self._show_icon:
                container.type_name.left = self._icon_size + 4
        return container

    def update_cell(self, entry, cell):
        type_id = self._get_type_id(entry)
        if self._show_info:
            cell.info_icon.typeID = type_id
        if self._show_icon:
            cell.item_icon.SetTypeID(type_id)
        if self._show_text:
            cell.type_name.text = evetypes.GetName(type_id)

    def get_value(self, entry):
        return evetypes.GetName(self._get_type_id(entry))

    def _get_type_id(self, entry):
        return getattr(entry, self.attribute_name)

    def on_row_enter(self, row, cell):
        if not self._show_info:
            return
        cell.info_icon.state = eveui.State.normal
        if self._show_text:
            fade_end = self.current_width - 26
            if self._show_icon:
                fade_end -= self._icon_size + 4
            cell.type_name.SetRightAlphaFade(fade_end, 12)

    def on_row_exit(self, row, cell):
        if not self._show_info:
            return
        cell.info_icon.state = eveui.State.hidden
        if self._show_text:
            cell.type_name.SetRightAlphaFade(0, 0)
