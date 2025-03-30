#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\data_display\table\column\base.py
import abc
import signals
import proper

def optional(value, default):
    if value is not None:
        return value
    return default


class BaseColumn(proper.Observable):
    __metaclass__ = abc.ABCMeta

    def __init__(self, id = None, title = '', padding = (6, 0, 6, 0), is_sortable = True, sort_initially = False, default_sort_ascending = True, sorting_value_func = None, copy_data_func = None, signal_name = None, col_span = 1, width = 0, is_fixed_width = False, min_width = 44, max_width = 500, **kwargs):
        if id is None:
            raise ValueError('Column ID is required')
        if sort_initially and not is_sortable:
            raise ValueError("Column cannot sort initially if it's not sortable")
        self.id = id
        self.title = title
        self.padding = padding
        self.is_sortable = is_sortable
        self.sort_initially = sort_initially
        self.default_sort_ascending = default_sort_ascending
        self.get_sort_value = optional(sorting_value_func, self.get_value)
        self.get_copy_data = optional(copy_data_func, self.get_value)
        self.signal_name = signal_name
        self.col_span = col_span
        self.width = width
        self.is_fixed_width = is_fixed_width
        self.min_width = min_width
        self.max_width = max_width
        super(BaseColumn, self).__init__(**kwargs)
        self.on_sort = signals.Signal(signalName='on_sort')
        self.on_save = signals.Signal(signalName='on_save')
        self.on_refresh = signals.Signal(signalName='on_refresh')

    def refresh(self):
        self.on_refresh()

    @abc.abstractmethod
    def render_cell(self):
        pass

    @abc.abstractmethod
    def update_cell(self, entry, cell):
        pass

    @abc.abstractmethod
    def get_value(self, entry):
        pass

    def on_row_enter(self, row, cell):
        pass

    def on_row_exit(self, row, cell):
        pass

    def close(self):
        pass

    @property
    def assigned_width(self):
        return self.custom_width or self.width

    def reset_width(self):
        self.custom_width = None
        self.save()

    def update_width(self, col_span_width):
        if self.is_fixed_width:
            self.current_width = self.width
        else:
            width = self.assigned_width or col_span_width * self.col_span
            self.current_width = self._clamp_width(width)

    @proper.ty(default=0)
    def current_width(self):
        pass

    @proper.ty(default=None)
    def custom_width(self):
        pass

    @custom_width.validator
    def edit_custom_width(self, width):
        if width is not None:
            return self._clamp_width(width)

    def _clamp_width(self, width):
        return max(self.min_width, min(self.max_width, width))

    def sort(self):
        if self.is_sortable:
            self.on_sort(self)

    def save(self):
        self.on_save()
