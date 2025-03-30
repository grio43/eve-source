#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\data_display\table\column_line.py
import eveui
from .constants import COLUMN_LINE_COLOR, TABLE_HEADER_HEIGHT

class ColumnLine(eveui.Container):
    default_name = 'ColumnLine'
    default_align = eveui.Align.to_left_no_push
    default_width = 4
    offset = 2

    def __init__(self, controller, **kwargs):
        super(ColumnLine, self).__init__(**kwargs)
        self.controller = controller
        self.line = eveui.Line(parent=self, align=eveui.Align.to_left, color=COLUMN_LINE_COLOR)
        self.line.left = self.offset

    def set_position(self, position):
        self.left = position - self.offset
