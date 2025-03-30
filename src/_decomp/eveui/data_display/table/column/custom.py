#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\data_display\table\column\custom.py
from .base import BaseColumn

class CustomColumn(BaseColumn):

    def __init__(self, render_func, update_func, value_func = None, **kwargs):
        super(CustomColumn, self).__init__(**kwargs)
        self.render_func = render_func
        self.update_func = update_func
        self.value_func = value_func

    def render_cell(self):
        return self.render_func()

    def update_cell(self, entry, cell):
        self.update_func(entry, cell)

    def get_value(self, entry):
        if self.value_func:
            return self.value_func(entry)
