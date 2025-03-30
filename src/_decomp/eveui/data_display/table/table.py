#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\data_display\table\table.py
import __builtin__
import blue
from carbon.common.script.util.commonutils import StripTags
from carbonui.uicore import uicore
import itertoolsext
import localization
import signals
import eveui
from eveui.keyboard import Key
from .row import TableRow, TableHeader
from .constants import COLUMN_LINE_COLOR
BORDER_COLOR = (1, 1, 1, 0.3)

class WIPTable(eveui.Container):
    default_name = 'Table'
    default_clipChildren = True
    default_bgColor = (0, 0, 0, 0.2)

    def __init__(self, columns, data = None, entry_signal_name = None, row_height = 36, row_select = False, row_multi_select = False, row_menu_callback = None, no_data_message = None, id = None, **kwargs):
        super(WIPTable, self).__init__(**kwargs)
        self.on_row_click = signals.Signal(signalName='on_row_click')
        self.on_row_double_click = signals.Signal(signalName='on_row_double_click')
        self.on_row_enter = signals.Signal(signalName='on_row_enter')
        self.on_row_exit = signals.Signal(signalName='on_row_exit')
        self.on_key_down = signals.Signal(signalName='on_key_down')
        self._columns = columns
        self._entry_signal_name = entry_signal_name
        self._row_height = row_height
        self._row_multi_select = row_multi_select
        self._row_select = row_select or row_multi_select
        self._row_menu_callback = row_menu_callback
        self.no_data_message = no_data_message or localization.GetByLabel('UI/Common/NoDataAvailable')
        self._id = 'Table_{}_{}'.format(uicore.registry.GetTopLevelWindowAboveItem(self).name, id) if id else None
        self._selected_entries = []
        self._data = []
        self._sorted_data = []
        self._table_rows = []
        self._column_lines = []
        self._sorted_by = None
        self._sort_ascending = True
        self._total_height = 0
        self._settings = __builtin__.settings
        self._loaded_data = None
        self._load_settings()
        self._subscribe_to_columns()
        self._layout()
        self.data = data
        self.body.Copy = self._copy
        self.body.OnKeyDown = self._on_key_down
        self._select_focus_entry = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if not data:
            self._show_no_data()
            return
        self.no_data_label.Hide()
        old_data = self._data
        self._data = data
        self._total_height = len(data) * self._row_height
        if old_data:
            self._update_selected_entries()
        if self._sorted_by:
            self._sort(self._sorted_by)
        else:
            self._initial_sort()

    def reset(self):
        del self._selected_entries[:]
        self._initial_sort()
        self.scroll_to(0, 0)

    def refresh_all(self):
        for row in self._table_rows:
            row.refresh()

    def refresh_entry(self, entry):
        row = self._get_entry_row(entry)
        if row:
            row.refresh()

    def refresh_column(self, id):
        column = self._get_column(id)
        if column:
            column.refresh()

    @property
    def selected_entries(self):
        return self._selected_entries

    def scroll_to(self, vertical = None, horizontal = None):
        if vertical is not None:
            self.body.ScrollToVertical(vertical)
        if horizontal is not None:
            self.body.ScrollToHorizontal(horizontal)

    def _layout(self):
        self.content_container = eveui.Container(name='ContentContainer', parent=self, padding=1, clipChildren=True)
        self._construct_border()
        self._construct_column_lines()
        self._construct_header()
        self._construct_no_data()
        self._construct_body()

    def _construct_border(self):
        container = eveui.Container(name='BorderContainer', parent=self)
        eveui.Line(parent=container, color=BORDER_COLOR, align=eveui.Align.to_top)
        eveui.Line(parent=container, color=BORDER_COLOR, align=eveui.Align.to_bottom)
        eveui.Line(parent=container, color=BORDER_COLOR, align=eveui.Align.to_left)
        eveui.Line(parent=container, color=BORDER_COLOR, align=eveui.Align.to_right)

    def _construct_column_lines(self):
        container = eveui.Container(name='ColumnLinesContainer', parent=self.content_container)
        for _ in self._columns:
            column_line = eveui.Line(parent=container, align=eveui.Align.to_left_no_push, color=COLUMN_LINE_COLOR)
            self._column_lines.append(column_line)

    def _construct_header(self):
        self.header = TableHeader(parent=self.content_container, columns=self._columns)

    def _construct_no_data(self):
        self.no_data_label = eveui.EveCaptionSmall(parent=self.content_container, align=eveui.Align.to_top, state=eveui.State.hidden, top=20, opacity=0.5)

    def _construct_body(self):
        self.body = eveui.ScrollContainer(name='TableBody', parent=self.content_container)
        self.body.clipCont._OnSizeChange_NoBlock = self._on_container_size_change
        for _ in range(20):
            row = TableRow(columns=self._columns, on_click=self._handle_row_click, on_double_click=self._handle_row_double_click, row_menu_callback=self._row_menu_callback, on_row_enter=self._handle_row_enter, on_row_exit=self._handle_row_exit, entry_signal_name=self._entry_signal_name, parent=self.body, height=self._row_height)
            self._table_rows.append(row)

    def _copy(self, *args):
        data = []
        for entry in self.selected_entries:
            entry_data = []
            for column in self._columns:
                entry_data.append(str(column.get_copy_data(entry)))

            data.append('\t'.join(entry_data))

        if data:
            text = StripTags('\n'.join(data))
            blue.pyos.SetClipboardData(text)

    def _on_key_down(self, key, flag):
        if key == Key.a and Key.ctrl_or_cmd().is_down:
            self._select_all()
        elif key == Key.down:
            self._select_down()
        elif key == Key.up:
            self._select_up()
        elif key == Key.page_down:
            self.body.ScrollByPage(up=False)
        elif key == Key.page_up:
            self.body.ScrollByPage(up=True)
        elif key == Key.home:
            print 'scroll to top'
        elif key == Key.end:
            print 'scroll to bot'
        self.on_key_down(key, flag)

    def Close(self):
        super(WIPTable, self).Close()
        for column in self._columns:
            column.unbind(custom_width=self._adjust_column_width)
            column.on_sort.disconnect(self._on_sort)
            column.on_save.disconnect(self._save_settings)
            column.close()

    def _subscribe_to_columns(self):
        for column in self._columns:
            column.bind(custom_width=self._adjust_column_width)
            column.on_sort.connect(self._on_sort)
            column.on_save.connect(self._save_settings)

    def _on_container_size_change(self, *args):
        self._adjust_column_width()

    def _adjust_column_width(self, *args):
        available_width = self.body.clipCont.GetAbsoluteSize()[0]
        col_span = 0
        for column in self._columns:
            width = column.assigned_width
            if width:
                available_width -= width
            else:
                col_span += column.col_span

        col_span_width = int(round(available_width / float(col_span))) if col_span else 0
        for column in self._columns:
            column.update_width(col_span_width)

        self._adjust_lines()

    def _adjust_lines(self):
        current_pos = 0
        for index, column in enumerate(self._columns):
            current_pos += column.current_width
            self._column_lines[index].left = current_pos

    def _on_sort(self, column):
        if self._sorted_by == column:
            self._sort_ascending = not self._sort_ascending
        else:
            self._sort_ascending = column.default_sort_ascending
        self._sort(column)
        self._save_settings()

    def _sort(self, column):
        self._sorted_by = column
        self._sorted_data = sorted(self._data, key=lambda entry: column.get_sort_value(entry))
        if not self._sort_ascending:
            self._sorted_data.reverse()
        self.header.sorting_changed(column, self._sort_ascending)
        self.scroll_to(vertical=0)
        self._update_rows()

    def _initial_sort(self):
        sortable = None
        for column in self._columns:
            if column.sort_initially:
                sortable = column
                break
            if not sortable and column.is_sortable:
                sortable = column

        if sortable:
            self._sort_ascending = sortable.default_sort_ascending
            self._sort(sortable)
        else:
            self._sorted_data = list(self._data)
            self._update_rows()

    def _handle_row_click(self, row):
        if self._row_select:
            self._handle_selection(row)
        self.on_row_click(row.entry)

    def _handle_row_double_click(self, row):
        self.on_row_double_click(row.entry)

    def _handle_row_enter(self, row):
        self.on_row_enter(row.entry)

    def _handle_row_exit(self, row):
        self.on_row_exit(row.entry)

    def _handle_selection(self, row):
        entry = row.entry
        if not self._row_multi_select:
            self._clear_selected_entries()
            self._select_row(row)
        elif Key.shift.is_down:
            start_index = 0
            end_index = self._sorted_data.index(entry)
            if len(self._selected_entries) > 0:
                if not self._select_focus_entry:
                    self._select_focus_entry = self._selected_entries[len(self._selected_entries) - 1]
                self._clear_selected_entries()
                start_index = self._sorted_data.index(self._select_focus_entry)
            if start_index > end_index:
                start_index, end_index = end_index, start_index
            self._selected_entries.extend(self._sorted_data[start_index:end_index + 1])
            self._refresh_selection()
        elif Key.control.is_down:
            self._select_focus_entry = entry
            if self._is_entry_selected(entry):
                self._deselect_row(row)
            else:
                self._select_row(row)
        else:
            self._select_focus_entry = entry
            self._clear_selected_entries()
            self._select_row(row)

    def _select_all(self):
        del self._selected_entries[:]
        for entry in self.data:
            self._selected_entries.append(entry)

        for row in self._table_rows:
            row.select()

    def _select_down(self):
        select_index = 0
        if not self._selected_entries:
            self.scroll_to(0)
        else:
            for index, row in enumerate(reversed(self._table_rows)):
                if row.is_selected:
                    select_index = len(self._table_rows) - index
                    break

        if select_index < len(self._table_rows):
            self._handle_selection(self._table_rows[select_index])

    def _select_up(self):
        select_index = 0
        if not self._selected_entries:
            self.scroll_to(0)
        else:
            for index, row in enumerate(self._table_rows):
                if row.is_selected:
                    select_index = index - 1
                    break

        if select_index >= 0:
            self._handle_selection(self._table_rows[select_index])

    def _refresh_selection(self):
        for row in self._table_rows:
            if self._is_entry_selected(row.entry):
                row.select()

    def _select_row(self, row):
        self._selected_entries.append(row.entry)
        row.select()

    def _deselect_row(self, row):
        self._selected_entries.remove(row.entry)
        row.deselect()

    def _is_entry_selected(self, entry):
        return entry in self._selected_entries

    def _clear_selected_entries(self):
        for row in self._table_rows:
            row.deselect()

        del self._selected_entries[:]

    def _get_entry_row(self, entry):
        return itertoolsext.first_or_default(self._table_rows, lambda x: x.entry == entry)

    def _update_selected_entries(self):
        for entry in list(self._selected_entries):
            if entry not in self._sorted_data:
                self._selected_entries.remove(entry)

    def _update_rows(self):
        for index, row in enumerate(self._table_rows):
            entry = self._sorted_data[index] if index < len(self._sorted_data) else None
            is_selected = entry in self._selected_entries
            row.set_entry(entry, is_selected)

    def _show_no_data(self):
        self.no_data_label.text = u'<center>{}</center>'.format(self.no_data_message)
        self.no_data_label.Show()

    def _load_settings(self):
        if not self._id:
            return
        self._loaded_data = self._settings.char.ui.Get(self._id, None)
        if not self._loaded_data:
            return
        self._load_sort()
        self._load_columns()

    def _load_sort(self):
        sorted_by = self._loaded_data.get('sorted_by', None)
        if not sorted_by:
            return
        column = self._get_column(sorted_by)
        if column and column.is_sortable:
            self._sort_ascending = self._loaded_data.get('sort_ascending', column.default_sort_ascending)
            self._sorted_by = column

    def _load_columns(self):
        saved_columns = self._loaded_data.get('columns', None)
        if not saved_columns:
            return
        for saved_column in saved_columns:
            column_id = saved_column.get('id', None)
            if not column_id:
                continue
            column = self._get_column(column_id)
            if column:
                column.custom_width = saved_column.get('custom_width', None)

    def _get_column(self, id):
        return itertoolsext.first_or_default(self._columns, lambda x: x.id == id)

    def _save_settings(self):
        if not self._id:
            return
        data = dict()
        data['sorted_by'] = self._sorted_by.id if self._sorted_by else None
        data['sort_ascending'] = self._sort_ascending
        data['columns'] = [ self._save_column(column) for column in self._columns ]
        self._settings.char.ui.Set(self._id, data)

    def _save_column(self, column):
        data = dict()
        data['id'] = column.id
        data['custom_width'] = column.custom_width
        return data
