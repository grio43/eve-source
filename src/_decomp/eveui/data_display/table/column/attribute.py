#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\data_display\table\column\attribute.py
import eveui
from .base import BaseColumn

class AttributeColumn(BaseColumn):

    def __init__(self, attribute_name, align = eveui.Align.center_left, **kwargs):
        kwargs.setdefault('id', attribute_name)
        kwargs.setdefault('copy_data_func', self.get_text)
        super(AttributeColumn, self).__init__(**kwargs)
        self._attribute_name = attribute_name
        self._align = align

    def render_cell(self):
        return eveui.EveLabelSmall(align=self._align)

    def update_cell(self, entry, cell):
        cell.text = self.get_text(entry)

    def get_text(self, entry):
        return self.get_value(entry)

    def get_value(self, entry):
        value = getattr(entry, self._attribute_name)
        return value
