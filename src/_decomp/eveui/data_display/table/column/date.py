#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\data_display\table\column\date.py
import datetime
from carbon.common.script.util.format import FmtDate
from datetimeutils import datetime_to_filetime
from eveui.data_display.table.column.attribute import AttributeColumn

class DateColumn(AttributeColumn):

    def __init__(self, format = 'll', **kwargs):
        super(DateColumn, self).__init__(**kwargs)
        self.format = format

    def get_text(self, entry):
        value = self.get_value(entry)
        if isinstance(value, datetime.datetime):
            value = datetime_to_filetime(value)
        return FmtDate(value, self.format)
