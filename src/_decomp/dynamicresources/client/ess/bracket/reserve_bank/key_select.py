#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\reserve_bank\key_select.py
import datetime
import datetimeutils
import eveformat
import evetypes
import eveui
import gametime
import localization
import locks
import signals
import threadutils
import uthread2
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from dynamicresources.common.ess.const import LINK_ERROR_ALREADY_LINKED
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.itemIcon import ItemIcon
from dynamicresources.client import color, text
from dynamicresources.client.ess.bracket.label import Header
from dynamicresources.client.ess.bracket.panel import get_absolute_bounds
from dynamicresources.client.ess.bracket.state_machine import State, Transition
from dynamicresources.client.service import get_dynamic_resource_service

class KeySelect(State):

    def __init__(self, parent, on_cancel = None):
        super(KeySelect, self).__init__()
        self._parent = parent
        self._selection_controller = None
        self._content = None
        self._label = None
        self._key_entries = []
        self._button = None
        self._cancelled = False
        self.on_cancel = signals.Signal()
        if on_cancel:
            self.on_cancel.connect(on_cancel)

    @property
    def focus_bounds(self):
        if self._content is None:
            return
        content_bounds = get_absolute_bounds(self._content)
        return content_bounds.inflate(100)

    def enter(self):
        self._content = LayoutGrid(parent=self._parent, align=uiconst.TOPLEFT, columns=1, cellSpacing=(0, 8))
        self._label = Header(parent=self._content, align=uiconst.TOPLEFT, text=text.title_select_key())
        animations.FadeTo(self._label, duration=0.15)
        animations.MorphScalar(self._label, 'left', startVal=-10, endVal=0, duration=0.15)
        service = get_dynamic_resource_service()
        keys = service.GetESSReserveBankKeysForCurrentSystem()
        self._selection_controller = KeySelectController(keys)
        key_list = LayoutGrid(name='key_list', parent=self._content, align=uiconst.TOPLEFT, cellSpacing=(8, 0), columns=len(keys))
        for i, key in enumerate(self._selection_controller.keys):
            entry = KeyEntry(parent=key_list, align=uiconst.TOPLEFT, key=key, on_confirm=self._selection_controller.use, on_disallowed=self.on_cancel)
            self._key_entries.append(entry)
            animations.FadeTo(entry, duration=0.15, timeOffset=i * 0.1)
            animations.MorphScalar(entry, 'left', startVal=-30, endVal=0, duration=0.15, timeOffset=i * 0.1)

        uicore.uilib.RegisterForTriuiEvents([uiconst.UI_MOUSEDOWN], self._on_global_mouse_down)
        self._start_cursor_cancel_loop()

    def exit(self):
        transition = Exit(self._content, self._label, self._key_entries)
        self._content = None
        return transition

    def close(self):
        if self._content:
            self._content.Close()

    def cancel(self):
        if not self._cancelled:
            self._cancelled = True
            self.on_cancel()

    def _on_global_mouse_down(self, target, *args, **kwargs):
        if target is None:
            return True
        focus_bounds = self.focus_bounds
        if focus_bounds is None:
            return True
        click_captured = focus_bounds.contains(*eveui.Mouse.position())
        if not click_captured:
            self.cancel()
            return False
        return True

    @threadutils.threaded
    def _start_cursor_cancel_loop(self):
        cursor_last_within_bounds_at = None
        cursor_distance_grace_period = datetime.timedelta(seconds=2)
        while self._content is not None and not self._content.destroyed:
            cursor_distance = self.focus_bounds.distance_from_point(*eveui.Mouse.position())
            if cursor_distance > 0:
                if cursor_last_within_bounds_at is None:
                    cursor_last_within_bounds_at = gametime.now()
                dt = gametime.now() - cursor_last_within_bounds_at
                if dt >= cursor_distance_grace_period:
                    self.cancel()
                    break
            else:
                cursor_last_within_bounds_at = gametime.now()
            eveui.wait_for_next_frame()


class Exit(Transition):

    def __init__(self, content, label, key_entries):
        super(Exit, self).__init__()
        self._content = content
        self._label = label
        self._key_entries = key_entries

    def animation(self):
        animations.FadeOut(self._label, duration=0.2)
        for i, entry in enumerate(reversed(self._key_entries)):
            animations.FadeOut(entry, duration=0.2, timeOffset=i * 0.1)

        self.sleep(max(0.2, 0.2 + (len(self._key_entries) - 1) * 0.1))

    def on_close(self):
        self._content.Close()


class KeySelectController(object):
    __notifyevents__ = ['OnItemChange']

    def __init__(self, keys_static_data):
        self._use_request_outstanding = False
        self._key_types_ids = set((key.type_id for key in keys_static_data))
        count = count_items_in_cargo(self._key_types_ids)
        self._keys = [ Key(static_data, count[static_data.type_id]) for static_data in keys_static_data ]
        ServiceManager.Instance().RegisterNotify(self)

    @property
    def keys(self):
        return self._keys

    def use(self, key):
        if key.type_id not in self._key_types_ids:
            raise ValueError('Unknown key type %s', key.type_id)
        if self._use_request_outstanding:
            return
        self._use_request_outstanding = True
        try:
            service = get_dynamic_resource_service()
            service.RequestUnlockReserveBank(key.type_id)
            service.RequestESSReserveBankLink()
        finally:
            self._use_request_outstanding = False

    @uthread2.debounce(wait=0.3)
    def _update_key_count(self):
        count = count_items_in_cargo(self._key_types_ids)
        for key in self._keys:
            key.count = count[key.type_id]

    def OnItemChange(self, item, change, location):
        if item.typeID in self._key_types_ids:
            self._update_key_count()


class Key(object):

    def __init__(self, key_static_data, count):
        self._static_data = key_static_data
        self._count = count
        self.on_count_changed = signals.Signal()

    @property
    def type_id(self):
        return self._static_data.type_id

    @property
    def name(self):
        return evetypes.GetName(self.type_id)

    @property
    def total_pulses(self):
        return self._static_data.total_pulses

    @property
    def duration(self):
        ess_settings = get_dynamic_resource_service().ess_settings
        pulse_interval = ess_settings.reserve_bank_pulse_interval.total_seconds()
        return datetime.timedelta(seconds=self.total_pulses * pulse_interval)

    @property
    def available(self):
        return self._count > 0

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, count):
        if count != self._count:
            self._count = count
            self.on_count_changed()


def count_items_in_cargo(type_ids):
    count = {type_id:0 for type_id in type_ids}
    if not session.shipid:
        return count
    inv_cache = ServiceManager.Instance().GetService('invCache')
    cargo = inv_cache.GetInventoryFromId(session.shipid)
    for item in cargo.List():
        if item.typeID in count:
            count[item.typeID] += item.quantity

    return count


class KeyEntry(ContainerAutoSize):

    def __init__(self, parent, align, key, on_confirm = None, on_disallowed = None):
        super(KeyEntry, self).__init__(parent=parent, align=align, alignMode=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        self.key = key
        self._item = None
        self._button = None
        self._hovered = False
        self._busy = False
        self.on_confirm = signals.Signal()
        if on_confirm:
            self.on_confirm.connect(on_confirm)
        self.on_disallowed = signals.Signal()
        if on_disallowed:
            self.on_disallowed.connect(on_disallowed)
        self._layout()
        self._update(animate=False)
        self.key.on_count_changed.connect(self._update)

    def _layout(self):
        self._item = KeyEntryItem(parent=self, align=uiconst.TOPLEFT, key=self.key)
        self._button_cont = ContainerAutoSize(parent=self, align=uiconst.TOPLEFT, top=self._item.height - 10, opacity=0.0)
        self._button = Button(parent=self._button_cont, align=uiconst.TOPLEFT, label=text.action_use_key(), func=self._confirm, args=())

    def _update(self, animate = True):
        if not self._item:
            return
        if self._hovered or self._busy:
            self._item.hovered = True
            if not self._busy and self.key.available:
                self._button.Enable()
            else:
                self._button.Disable()
            if self.key.available:
                if animate:
                    animations.FadeIn(self._button_cont, duration=0.2)
                    if self._button_cont.top == 0:
                        self._button_cont.top = self._item.height - 10
                    animations.MorphScalar(self._button_cont, 'top', startVal=self._button_cont.top, endVal=self._item.height + 8, duration=0.2)
                else:
                    self._button_cont.opacity = 1.0
                    self._button_cont.top = self._item.height + 8
        else:
            self._item.hovered = False
            self._button.Disable()
            if animate:

                def move_button():
                    self._button_cont.top = 0

                animations.FadeOut(self._button_cont, duration=0.1, callback=move_button)
            else:
                self._button_cont.opacity = 0.0
                self._button_cont.top = 0

    @locks.SingletonCall
    @threadutils.threaded
    def _confirm(self):
        self._busy = True
        self._update(animate=False)
        service = get_dynamic_resource_service()
        main_bank_link = service.ess_state_provider.state.main_bank.link
        if main_bank_link and main_bank_link.character_id == session.charid:
            message = text.link_error_description(LINK_ERROR_ALREADY_LINKED)
            if message is not None:
                uicore.Message('CustomNotify', {'notify': message})
            self.on_disallowed()
            return
        try:
            self.on_confirm(self.key)
        finally:
            uthread2.sleep(1.0)
            self._busy = False
            self._update(animate=False)

    def OnMouseEnter(self, *args):
        eveui.Sound.button_hover.play()
        self._hovered = True
        self._update()

    def OnMouseExit(self, *args):
        self._hovered = False
        self._update()


class KeyEntryItem(ContainerAutoSize):

    def __init__(self, parent, align, key):
        super(KeyEntryItem, self).__init__(parent=parent, align=align, state=uiconst.UI_NORMAL, width=80, alignMode=uiconst.TOTOP)
        self.key = key
        self._hovered = False
        self._icon = None
        self._label = None
        self._underlay = None
        self._layout()
        self._update()
        self.key.on_count_changed.connect(self._update)

    @property
    def hovered(self):
        return self._hovered

    @hovered.setter
    def hovered(self, hovered):
        if hovered != self._hovered:
            self._hovered = hovered
            self._update()

    def _layout(self):
        iconTransform = Transform(parent=ContainerAutoSize(parent=self, align=uiconst.TOTOP, top=10), align=uiconst.TOTOP, state=uiconst.UI_DISABLED, width=42, height=42)
        self._icon = ItemIcon(parent=iconTransform, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=42, height=42, typeID=self.key.type_id)
        label_cont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, top=8, padding=(8, 0, 8, 3))
        self._label = eveLabel.EveLabelSmall(parent=label_cont, align=uiconst.TOTOP, text=eveformat.center(self.key.name), color=(1.0, 1.0, 1.0, 0.8))
        self._underlay = Frame(bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', cornerSize=9, color=(0.0, 0.0, 0.0, 0.5))

    def _update(self):
        if self.key.available:
            self._icon.opacity = 1.0
            self._label.opacity = 0.8
        else:
            self._icon.opacity = 0.5
            self._label.opacity = 0.3
        if self._hovered and self.key.available:
            underlay_color = color.smoke_blue.with_alpha(0.6).rgba
        elif not self.key.available:
            underlay_color = color.mordus_legion.with_alpha(0.2).rgba
        else:
            underlay_color = color.black.with_alpha(0.5).rgba
        animations.SpColorMorphTo(self._underlay, endColor=underlay_color, duration=0.15)

    def GetHint(self):
        duration = datetimeutils.timedelta_to_filetime_delta(self.key.duration)
        duration_string = localization.formatters.FormatTimeIntervalWritten(duration)
        hint = u'{}<br>{}'.format(eveformat.bold(self.key.name), text.hint_key_info(pulses=self.key.total_pulses, duration=eveformat.color(duration_string, color.focus)))
        if not self.key.available:
            hint = u'{}<br><br>{}'.format(hint, eveformat.color(text.hint_key_unavailable(), color.warning))
        return hint

    def GetMenu(self):
        menu_service = ServiceManager.Instance().GetService('menu')
        return menu_service.GetMenuFromItemIDTypeID(typeID=self.key.type_id, itemID=None, includeMarketDetails=True)


from dynamicresources.client.ess.bracket.debug import __reload_update__
