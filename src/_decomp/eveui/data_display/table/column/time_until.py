#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\data_display\table\column\time_until.py
import datetime
import threadutils
import uthread2
import localization
from datetimeutils import datetime_to_filetime
from .attribute import AttributeColumn

class TimeUntilColumn(AttributeColumn):

    def __init__(self, short = True, show_from = 'day', show_to = 'second', auto_update_time = None, **kwargs):
        kwargs.setdefault('copy_data_func', self._copy_data)
        super(TimeUntilColumn, self).__init__(**kwargs)
        self.short = short
        self.show_from = show_from
        self.show_to = show_to
        if auto_update_time:
            self._open = True
            self.auto_update(auto_update_time)

    def get_text(self, entry):
        value = self.get_value(entry)
        if isinstance(value, datetime.datetime):
            value = datetime_to_filetime(value)
        time_now = datetime_to_filetime(datetime.datetime.utcnow())
        time_left = max(value - time_now, 0)
        if self.short:
            return localization.formatters.FormatTimeIntervalShortWritten(time_left, showFrom=self.show_from, showTo=self.show_to)
        else:
            return localization.formatters.FormatTimeIntervalWritten(time_left, showFrom=self.show_from, showTo=self.show_to)

    def _copy_data(self, entry):
        value = self.get_value(entry)
        if isinstance(value, datetime.datetime):
            value = datetime_to_filetime(value)
        return localization.GetByLabel('/Carbon/UI/Common/DateTime/SimpleDateUTC', datetime=value)

    def close(self):
        self._open = False

    @threadutils.threaded
    def auto_update(self, sleep_time):
        while self._open:
            uthread2.sleep(sleep_time)
            self.refresh()
