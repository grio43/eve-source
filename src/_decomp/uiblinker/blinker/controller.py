#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\blinker\controller.py
import datetime
import weakref
import eveui
import gametime
import uthread2
from uiblinker.blinker import get_blinker_factory
REFERENCE_RESOLVE_INTERVAL = datetime.timedelta(milliseconds=250)
OBSCURED_CHECK_INTERVAL = datetime.timedelta(milliseconds=100)

class BlinkerController(object):

    def __init__(self, ui_reference, blinker_parent, blinker_type, ui_root):
        self._ui_reference = ui_reference
        self._blinker_parent = blinker_parent
        self._blinker_type = blinker_type
        self._ui_root = ui_root
        self._blinker_by_element = {}
        self._interval_timer_by_blinker = weakref.WeakKeyDictionary()
        self._frame_update_loop_tasklet = None

    @property
    def is_active(self):
        return self._frame_update_loop_tasklet is not None

    def start(self):
        if not self.is_active:
            self._frame_update_loop_tasklet = uthread2.start_tasklet(self._frame_update_loop)

    def stop(self):
        if self.is_active:
            self._frame_update_loop_tasklet.kill()
            self._frame_update_loop_tasklet = None
            for blinker in self._blinker_by_element.itervalues():
                blinker.close()

            self._blinker_by_element.clear()

    def _frame_update_loop(self):
        reference_resolve_interval = TimeIntervalGate(REFERENCE_RESOLVE_INTERVAL)
        while True:
            pending_add, pending_removal, focused = self.get_pending_elements(reference_resolve_interval)
            for element_ref, blinker in self._blinker_by_element.iteritems():
                element = element_ref()
                if element is None or element.destroyed:
                    pending_removal.add(element_ref)
                    continue
                if element in pending_add:
                    pending_add.discard(element)
                if self._interval_timer_by_blinker[blinker].ready():
                    visible = element.IsVisible()
                    clipping = get_clipping(element)
                    if not visible or clipping == Clipping.full:
                        blinker.stop()
                    elif visible:
                        blinker.obscured = clipping == Clipping.middle or is_obscured(element) and clipping != Clipping.full
                        blinker.start()
                if blinker.blinking:
                    blinker.update_blink_area(element)

            factory = get_blinker_factory(self._blinker_type)
            for element in pending_add:
                blinker = factory(parent=self._blinker_parent, element=element)
                self._blinker_by_element[weakref.ref(element)] = blinker
                self._interval_timer_by_blinker[blinker] = TimeIntervalGate(OBSCURED_CHECK_INTERVAL)
                blinker.start()

            for element_ref in pending_removal:
                blinker = self._blinker_by_element.pop(element_ref, None)
                if blinker:
                    blinker.stop()
                    blinker.close()

            if pending_add or pending_removal:
                unique_ui_name = focused.uniqueUiName or focused.name if focused else None
                sm.ScatterEvent('OnBlinkerUpdated', unique_ui_name)
            eveui.wait_for_next_frame()

    def get_pending_elements(self, reference_resolve_interval):
        elements = []
        if reference_resolve_interval.ready():
            elements = self._ui_reference.resolve(self._ui_root)
        focused = elements[0] if elements else None
        return (set(elements), set(), focused)


class BlinkerChainController(BlinkerController):

    def get_pending_elements(self, reference_resolve_interval):
        pending_add = set()
        pending_removal = set()
        focused = None
        if not reference_resolve_interval.ready():
            return (pending_add, pending_removal, focused)
        elements = self._ui_reference.resolve(self._ui_root)
        for element in elements:
            if element is None or element.destroyed:
                continue
            visible = element.IsVisible()
            clipping = get_clipping(element)
            if not visible or clipping == Clipping.full:
                pass
            elif visible:
                pending_add.add(element)
                if focused is None:
                    focused = element
                break

        for element_ref, blinker in self._blinker_by_element.iteritems():
            if element_ref() not in pending_add:
                pending_removal.add(element_ref)
                if focused is None:
                    focused = element_ref()

        return (pending_add, pending_removal, focused)


class TimeIntervalGate(object):

    def __init__(self, interval):
        self._last_enter = None
        self._interval = interval

    def ready(self):
        now = gametime.now()
        if self._last_enter is None or now - self._last_enter >= self._interval:
            self._last_enter = now
            return True
        return False


class Clipping(object):
    none = 1
    partial = 2
    middle = 3
    full = 4


def get_clipping(element):
    my_left, my_top, my_width, my_height = element.GetAbsolute()
    my_bottom = my_top + my_height
    my_right = my_left + my_width
    center_x = my_left + int(round(my_width / 2.0))
    center_y = my_top + int(round(my_height / 2.0))
    clipping_max = Clipping.none
    ancestor = element.parent
    while ancestor:
        if ancestor.parent is None:
            return clipping_max
        left, top, width, height = ancestor.GetAbsolute()
        right = left + width
        bottom = top + height
        if my_left >= right or my_top >= bottom or my_right <= left or my_bottom <= top:
            return Clipping.full
        if center_x < left or center_x > right or center_y < top or center_y > bottom:
            clipping_max = max(Clipping.middle, clipping_max)
        if my_left < left or my_top < top or my_right > right or my_bottom > bottom:
            clipping_max = max(Clipping.partial, clipping_max)
        ancestor = ancestor.parent

    return clipping_max


def is_obscured(element):
    from carbonui.uicore import uicore
    left, top, width, height = element.GetAbsolute()
    center_x = int(round(left + width / 2.0))
    center_y = int(round(top + height / 2.0))
    _, picked = uicore.uilib.PickScreenPosition(eveui.scale_dpi(center_x), eveui.scale_dpi(center_y))
    picked_order_chain = _get_order_chain(picked)
    element_order_chain = _get_order_chain(element)
    for p, e in zip(picked_order_chain, element_order_chain):
        if p == e:
            continue
        return p < e

    return False


def _get_order_chain(element):
    order_chain = []
    while element:
        try:
            order_chain.insert(0, element.GetOrder())
        except AttributeError:
            if not hasattr(element, 'parent'):
                break
            else:
                raise

        element = element.parent

    return order_chain
