#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\data_display\table\row.py
import eveui
import eveui.compatibility
from .cell import TableCell, TableHeaderCell
from .constants import COLUMN_LINE_COLOR, TABLE_HEADER_HEIGHT

class BaseTableRow(eveui.Container):
    default_state = eveui.State.normal
    default_align = eveui.Align.to_top

    def __init__(self, columns, **kwargs):
        super(BaseTableRow, self).__init__(**kwargs)
        self.columns = columns
        self.table_cells = []


class TableRow(eveui.compatibility.CarbonEventHandler, BaseTableRow):
    default_name = 'TableRow'
    default_state = eveui.State.hidden

    def __init__(self, columns, on_click, on_double_click, row_menu_callback, on_row_enter, on_row_exit, entry_signal_name, **kwargs):
        super(TableRow, self).__init__(columns, **kwargs)
        self.entry = None
        self.is_entered = False
        self.is_selected = False
        self._on_click = on_click
        self._on_double_click = on_double_click
        self._on_row_menu = row_menu_callback
        self._on_row_enter = on_row_enter
        self._on_row_exit = on_row_exit
        self._entry_signal_name = entry_signal_name
        self._layout()

    def _layout(self):
        self.hover_fill = eveui.Fill(bgParent=self, opacity=0)
        self.selected_fill = eveui.Fill(bgParent=self, opacity=0)
        for column in self.columns:
            cell = TableCell(controller=column, parent=self, height=self.height)
            self.table_cells.append(cell)

    def Close(self):
        super(TableRow, self).Close()
        if self.entry:
            self._unsubscribe()

    def set_entry(self, entry, is_selected = False):
        if self.entry:
            self.selected_fill.opacity = 0
            self._unsubscribe()
        self.entry = entry
        if self.entry:
            self.refresh()
            self.is_selected = is_selected
            if is_selected:
                self.selected_fill.opacity = 0.2
            self.Show()
            self._subscribe()
        else:
            self.is_selected = False
            self.Hide()

    def refresh(self):
        for cell in self.table_cells:
            cell.refresh(self.entry)

    def select(self):
        if self.is_selected:
            return
        self.is_selected = True
        eveui.fade_in(self.selected_fill, end_value=0.2, duration=0.2)

    def deselect(self):
        if not self.is_selected:
            return
        self.is_selected = False
        eveui.fade_out(self.selected_fill, duration=0.3)

    def on_click(self, click_count):
        if click_count == 1:
            self._on_click(self)
        elif click_count == 2:
            self._on_double_click(self)

    def GetMenu(self):
        if self._on_row_menu:
            return self._on_row_menu(self.entry)

    def on_mouse_enter(self):
        if self.is_entered:
            return
        self.is_entered = True
        self.hover_fill.opacity = 0.1
        for cell in self.table_cells:
            cell.controller.on_row_enter(row=self, cell=cell.content)

        if self._on_row_enter is not None:
            self._on_row_enter(self)

    def on_mouse_exit(self):
        if not self.is_entered:
            return
        self.is_entered = False
        eveui.fade_out(self.hover_fill, duration=0.1)
        for cell in self.table_cells:
            cell.controller.on_row_exit(row=self, cell=cell.content)

        if self._on_row_exit is not None:
            self._on_row_exit(self)

    def _subscribe(self):
        signal = self._get_entry_signal()
        if signal:
            signal.connect(self._on_entry_change)

    def _unsubscribe(self):
        signal = self._get_entry_signal()
        if signal:
            signal.disconnect(self._on_entry_change)

    def _get_entry_signal(self):
        if self._entry_signal_name:
            return getattr(self.entry, self._entry_signal_name, None)

    def _on_entry_change(self, *args, **kwargs):
        self.refresh()


class TableHeader(BaseTableRow):
    default_name = 'TableHeader'
    default_height = TABLE_HEADER_HEIGHT

    def __init__(self, columns, **kwargs):
        super(TableHeader, self).__init__(columns, **kwargs)
        self._layout()

    def _layout(self):
        eveui.Line(parent=self, color=COLUMN_LINE_COLOR, align=eveui.Align.to_bottom_no_push)
        for column in self.columns:
            cell = TableHeaderCell(controller=column, parent=self, height=self.height)
            self.table_cells.append(cell)

    def sorting_changed(self, column, ascending):
        for cell in self.table_cells:
            cell.sorting_changed(column, ascending)
