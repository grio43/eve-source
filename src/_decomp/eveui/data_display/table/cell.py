#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\data_display\table\cell.py
import carbonui.const as uiconst
from carbonui.uicore import uicore
import threadutils
import eveui
from eveui.primitive.sprite import Sprite

class BaseTableCell(eveui.Container):
    default_align = eveui.Align.to_left
    default_clipChildren = True

    def __init__(self, controller, **kwargs):
        super(BaseTableCell, self).__init__(**kwargs)
        self.controller = controller
        self.name = self.controller.id
        self.contentContainer = eveui.Container(name='CellContentContainer', parent=self, padding=self.controller.padding, clipChildren=True)
        self.width = self.controller.current_width
        self.controller.bind(current_width=self.update_width)

    def update_width(self, *args):
        self.width = self.controller.current_width

    def Close(self):
        super(BaseTableCell, self).Close()
        self.controller.unbind(current_width=self.update_width)


class TableCell(BaseTableCell):
    default_name = 'TableCell'

    def __init__(self, controller, **kwargs):
        super(TableCell, self).__init__(controller, **kwargs)
        self.entry = None
        self.content = self.controller.render_cell()
        self.content.SetParent(self.contentContainer)
        self.controller.on_refresh.connect(self._refresh_current)

    def refresh(self, entry):
        if self.entry != entry:
            self._unsubscribe(self.entry)
            self._subscribe(entry)
        self.entry = entry
        self.controller.update_cell(self.entry, self.content)

    def _refresh_current(self, *args, **kwargs):
        if self.entry:
            self.refresh(self.entry)

    def _subscribe(self, entry):
        signal = self._get_entry_signal(entry)
        if signal:
            signal.connect(self._refresh_current)

    def _unsubscribe(self, entry):
        if not entry:
            return
        signal = self._get_entry_signal(entry)
        if signal:
            signal.disconnect(self._refresh_current)

    def _get_entry_signal(self, entry):
        if not self.controller.signal_name:
            return None
        return getattr(entry, self.controller.signal_name)

    def Close(self):
        super(TableCell, self).Close()
        self.controller.on_refresh.disconnect(self._refresh_current)
        self._unsubscribe(self.entry)


class TableHeaderCell(BaseTableCell):
    default_name = 'TableHeaderCell'
    default_state = eveui.State.normal

    def __init__(self, controller, **kwargs):
        super(TableHeaderCell, self).__init__(controller, **kwargs)
        self.hint = self.controller.title
        self.title = eveui.EveLabelSmall(parent=self.contentContainer, text=self.controller.title, align=eveui.Align.center)
        self.sort_direction_icon = Sprite(name='SortDirectionIcon', parent=self, align=eveui.Align.center_right, state=eveui.State.hidden, pos=(3, 0, 16, 16))
        if not controller.is_fixed_width:
            ScaleHandle(controller=controller, parent=self)
        self.fix_title()

    def sorting_changed(self, column, ascending):
        if column != self.controller:
            self.title.SetRightAlphaFade(0, 0)
            self.sort_direction_icon.state = eveui.State.hidden
            return
        self.sort_direction_icon.state = eveui.State.disabled
        self.fix_title()
        if ascending:
            self.sort_direction_icon.texturePath = 'res:/UI/Texture/Icons/1_16_16.png'
        else:
            self.sort_direction_icon.texturePath = 'res:/UI/Texture/Icons/1_16_15.png'

    def OnClick(self, *args):
        self.controller.sort()

    def OnDblClick(self, *args):
        self.controller.reset_width()
        self.fix_title()

    def update_width(self, *args):
        super(TableHeaderCell, self).update_width()
        self.fix_title()

    def fix_title(self):
        available_width = self.width - self.controller.padding[0] - self.controller.padding[2]
        if self.sort_direction_icon.state == eveui.State.disabled:
            self.title.SetRightAlphaFade(available_width - 10, 6)
            available_width -= 24
        if self.title.width < available_width:
            self.title.align = eveui.Align.center
        else:
            self.title.align = eveui.Align.center_left


class ScaleHandle(eveui.Container):
    default_state = eveui.State.normal
    default_align = eveui.Align.to_right_no_push
    default_width = 2

    def __init__(self, controller, **kwargs):
        super(ScaleHandle, self).__init__(**kwargs)
        self.controller = controller
        self.cursor = uiconst.UICORSOR_HORIZONTAL_RESIZE
        self.scale_line = eveui.Line(parent=self, color=(1, 1, 1, 1), state=eveui.State.hidden, align=eveui.Align.to_left_no_push)
        self.is_scaling = False

    @threadutils.throttled(0.01)
    def OnMouseMoveDrag(self, *args):
        if args[0] == 0:
            return
        self.is_scaling = True
        current_pos = self.GetAbsolutePosition()[0] + self.width
        self.controller.custom_width = self.controller.current_width + (uicore.uilib.x - current_pos)

    def OnMouseUp(self, *args):
        if not self.is_scaling:
            return
        self.is_scaling = False
        self.controller.save()
