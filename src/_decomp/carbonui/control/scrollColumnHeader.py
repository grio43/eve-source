#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\scrollColumnHeader.py
import eveicon
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import Axis, uiconst
from carbonui.control.scroll_const import SortDirection
from carbonui.decorative.resize_handle import ResizeHandle
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.text.color import TextColor
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.pointerPanel import GetPanelInterestFromObject

class ColumnHeader(Container):
    DIRECTION_INDICATOR_ICON_SIZE = 16
    SCALE_HANDLE_SIZE = 8
    _text_clipper = None

    def __init__(self, column_id = None, text = None, direction = SortDirection.ASCENDING, on_click = None, on_double_click = None, scalable = False, on_scale_start = None, on_scale_move = None, on_scale_end = None, get_menu = None, selected = False, tab_margin = 0, **kwargs):
        self.id = column_id
        self._direction = direction
        self._direction_indicator = None
        self._get_menu = get_menu
        self._hovered = False
        self._label = None
        self._on_click = on_click
        self._on_double_click = on_double_click
        self._scalable = scalable
        self._scaler = None
        self._selected = selected
        self._tab_margin = tab_margin
        self._text = text
        super(ColumnHeader, self).__init__(**kwargs)
        self._prepare_label()
        self._prepare_direction_indicator()
        if self._scalable:
            self._prepare_scaler(on_scale_start, on_scale_move, on_scale_end)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        if value != self._direction:
            self._direction = value
            self._update()

    @property
    def on_scale_start(self):
        if self._scaler is not None:
            return self._scaler.on_scale_start

    @on_scale_start.setter
    def on_scale_start(self, value):
        if self._scaler is not None:
            self._scaler.on_scale_start = value

    @property
    def on_scale_move(self):
        if self._scaler is not None:
            return self._scaler.on_scale_move

    @on_scale_move.setter
    def on_scale_move(self, value):
        if self._scaler is not None:
            self._scaler.on_scale_move = value

    @property
    def on_scale_end(self):
        if self._scaler is not None:
            return self._scaler.on_scale_end

    @on_scale_end.setter
    def on_scale_end(self, value):
        if self._scaler is not None:
            self._scaler.on_scale_end = value

    def show_resizer_hint(self):
        if self._scaler:
            self._scaler.handle_ghost_visible = True

    def hide_resizer_hint(self):
        if self._scaler:
            self._scaler.handle_ghost_visible = False

    def _prepare_divider(self):
        pass

    def _prepare_label(self):
        self._text_clipper = Container(name='text_clipper', parent=self, align=uiconst.TOALL, padding=self._get_text_clipper_padding(), state=uiconst.UI_PICKCHILDREN, clipChildren=True)
        self._label = EveLabelSmall(parent=self._text_clipper, align=uiconst.CENTERLEFT, text=self._text, state=uiconst.UI_DISABLED, color=self._get_label_color(), autoFadeSides=8)

    def _get_text_clipper_padding(self):
        if self._selected:
            pad_right = 0
        else:
            pad_right = int(round(self.SCALE_HANDLE_SIZE / 2.0))
        return (self._tab_margin,
         0,
         pad_right,
         0)

    def _update_text_clipper_padding(self):
        self._text_clipper.padding = self._get_text_clipper_padding()

    def _get_label_color(self):
        if self._hovered:
            return TextColor.HIGHLIGHT
        else:
            return TextColor.SECONDARY

    def _prepare_direction_indicator(self):
        self._direction_indicator_cont = Container(name='direction_indicator', parent=self, align=uiconst.TORIGHT, left=max(0, self._tab_margin - 4), width=self.DIRECTION_INDICATOR_ICON_SIZE, idx=0)
        self._direction_indicator = Sprite(parent=self._direction_indicator_cont, align=uiconst.CENTER, width=self.DIRECTION_INDICATOR_ICON_SIZE, height=self.DIRECTION_INDICATOR_ICON_SIZE, state=uiconst.UI_DISABLED, texturePath=self._get_direction_indicator_icon(), color=self._get_direction_indicator_color())
        self._direction_indicator_cont.display = self._selected

    def _get_direction_indicator_icon(self):
        if self._direction == SortDirection.ASCENDING:
            return eveicon.caret_up
        if self._direction == SortDirection.DESCENDING:
            return eveicon.caret_down
        raise ValueError('Unknown sort direction')

    def _get_direction_indicator_color(self):
        if self._hovered:
            return TextColor.HIGHLIGHT
        elif self._selected:
            return TextColor.NORMAL
        else:
            return TextColor.SECONDARY

    def _prepare_scaler(self, on_scale_start, on_scale_move, on_scale_end):
        self._scaler = ScaleHandle(parent=self, align=uiconst.TORIGHT_NOPUSH, width=self.SCALE_HANDLE_SIZE, on_scale_start=on_scale_start, on_scale_move=on_scale_move, on_scale_end=on_scale_end, on_double_click=self._on_double_click, hint_delegate=self, idx=0)

    def _update(self):
        if self._direction_indicator is not None:
            self._direction_indicator_cont.display = self._selected
            self._direction_indicator.texturePath = self._get_direction_indicator_icon()
            self._direction_indicator.color = self._get_direction_indicator_color()
        if self._label is not None:
            animations.SpColorMorphTo(self._label, endColor=self._get_label_color(), duration=0.3)

    def select(self, direction = None):
        self._selected = True
        if direction is not None:
            self._direction = direction
        self._update()
        self._update_text_clipper_padding()

    def deselect(self):
        self._selected = False
        self._update()
        self._update_text_clipper_padding()

    def set_label(self, text):
        self._label.text = text

    def Select(self, rev, *args):
        self.select(SortDirection.from_legacy_reversed_sort(rev))

    def Deselect(self):
        self.deselect()

    def OnClick(self, *args):
        if self._on_click is not None:
            PlaySound(uiconst.SOUND_BUTTON_CLICK)
            self._on_click()

    def OnDblClick(self, *args):
        if self._on_double_click is not None:
            self._on_double_click()

    def OnMouseEnter(self, *args):
        self._hovered = True
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self._update()

    def OnMouseExit(self, *args):
        self._hovered = False
        self._update()

    def GetMenu(self, *args):
        if self._get_menu is not None:
            return self._get_menu()

    def GetHeaderHeight(self):
        return max(24, self._label.textheight)

    def GetHint(self):
        if uicore.uilib.auxMouseOver is self._label:
            return
        if self._label is not None and self._label.IsPartiallyClipped(self._label.parent):
            return self._text


class ScaleHandle(Container):
    _handle_ghost_visible = False
    _hovered = False

    def __init__(self, on_scale_start = None, on_scale_move = None, on_scale_end = None, on_double_click = None, name = 'scaler', state = uiconst.UI_NORMAL, cursor = uiconst.UICORSOR_HORIZONTAL_RESIZE, hint_delegate = None, **kwargs):
        self._hint_delegate = hint_delegate
        self._scaling = False
        self.on_double_click = on_double_click
        self.on_scale_start = on_scale_start
        self.on_scale_move = on_scale_move
        self.on_scale_end = on_scale_end
        super(ScaleHandle, self).__init__(name=name, cursor=cursor, state=state, **kwargs)
        self._handle = ResizeHandle(parent=self, align=uiconst.TOALL, orientation=Axis.VERTICAL, state=uiconst.UI_DISABLED, padding=(0, 4, 0, 4))

    @property
    def handle_ghost_visible(self):
        return self._handle_ghost_visible

    @handle_ghost_visible.setter
    def handle_ghost_visible(self, value):
        if self._handle_ghost_visible != value:
            self._handle_ghost_visible = value
            self._update_handle_ghost()

    def _update_handle_ghost(self):
        self._handle.show_line = self._handle_ghost_visible and not self._hovered

    def OnMouseDown(self, button):
        if button == uiconst.MOUSELEFT:
            self._scaling = True
            if self.on_scale_start is not None:
                self.on_scale_start()

    def OnMouseMove(self, *args):
        self._handle.OnMouseMove(*args)
        if self._scaling and self.on_scale_move is not None:
            self.on_scale_move()

    def OnMouseEnter(self, *args):
        self._hovered = True
        self._handle.OnMouseEnter(*args)
        self._update_handle_ghost()

    def OnMouseExit(self, *args):
        self._hovered = False
        self._handle.OnMouseExit(*args)
        self._update_handle_ghost()

    def OnMouseUp(self, button):
        if self._scaling and button == uiconst.MOUSELEFT:
            self._scaling = False
            if self.on_scale_end is not None:
                self.on_scale_end()

    def OnDblClick(self, *args):
        if self.on_double_click is not None:
            self.on_double_click()

    def GetHint(self):
        if self._hint_delegate is not None:
            return self._hint_delegate.GetHint()

    def GetTooltipPosition(self):
        if self._hint_delegate is not None:
            interest_rect, is_blocked = GetPanelInterestFromObject(self._hint_delegate)
            return interest_rect
