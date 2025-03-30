#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\tracker.py
import functools
import weakref
import eveui
import trinity
from carbonui import uiconst

class TransformTracker(object):

    def __init__(self, parent, transform, curve_set, tracker_parent = None, name = None):
        self._parent = parent
        self._curve_set = curve_set
        self._children = []
        self._closed = False
        self._tracker = trinity.EveProjectBracket()
        if name is not None:
            self._tracker.name = name
        self._tracker.parent = (tracker_parent or parent).GetRenderObject()
        self._tracker.trackTransform = transform
        self._tracker.bracketUpdateCallback = functools.partial(self._on_tracker_update, self_ref=weakref.ref(self))
        self._tracker.displayChangeCallback = functools.partial(self._on_tracker_display, self_ref=weakref.ref(self))
        curve_set.curves.append(self._tracker)

    def __del__(self):
        self.close()

    def add(self, child, anchor = (0.0, 0.0), offset = (0, 0)):
        child.align = uiconst.NOALIGN
        child.SetParent(self._parent)
        if not self._tracker.isVisible:
            child.display = False
        reference = ChildReference(child, anchor, offset)
        child._OnSizeChange_NoBlock = ChildSizeChangeHandler(tracker=self, child_reference=reference, wrapped_callback=child._OnSizeChange_NoBlock)
        self._children.append(reference)
        reference.update_position(self.get_projected_position())
        return reference

    def remove(self, child):
        for child_reference in self._iter_children():
            child_candidate = child_reference()
            if child_candidate is child:
                self._detach_child(child_reference)
                break
        else:
            return

        self._children.remove(child_reference)

    def close(self):
        if not self._closed:
            for child_reference in self._children:
                self._detach_child(child_reference)

            self._children = None
            self._curve_set.curves.fremove(self._tracker)
            self._curve_set = None
            self._closed = True

    def get_projected_position(self):
        x, y = self._tracker.projectedPosition
        x = eveui.reverse_scale_dpi(x)
        y = eveui.reverse_scale_dpi(y)
        return (x, y)

    @staticmethod
    def _on_tracker_update(tracker, self_ref):
        self = self_ref()
        if self is None:
            return
        projected_position = self.get_projected_position()
        for child_ref in self._iter_children():
            child_ref.update_position(projected_position)

    @staticmethod
    def _on_tracker_display(tracker, is_visible, self_ref):
        self = self_ref()
        if self is None:
            return
        for child_ref in self._iter_children():
            child_ref().display = is_visible

    @staticmethod
    def _detach_child(child_reference):
        child = child_reference()
        if child is not None:
            child._OnSizeChange_NoBlock = child._OnSizeChange_NoBlock.wrapped_callback
            child.SetParent(None)

    def _iter_children(self):
        children_pending_removal = []
        for child_ref in self._children:
            if not child_ref.is_valid:
                children_pending_removal.append(child_ref)
            else:
                yield child_ref

        for child_ref in children_pending_removal:
            self._children.remove(child_ref)


class ChildSizeChangeHandler(object):

    def __init__(self, tracker, child_reference, wrapped_callback = None):
        self._tracker_ref = weakref.ref(tracker)
        self._child_reference = child_reference
        self.wrapped_callback = wrapped_callback

    def __call__(self, width, height):
        tracker = self._tracker_ref()
        if tracker:
            self._child_reference.update_position(tracker.get_projected_position())
        if self.wrapped_callback:
            self.wrapped_callback(width, height)


class ChildReference(object):

    def __init__(self, child, anchor, offset):
        self._child_ref = weakref.ref(child)
        self.anchor = anchor
        self.offset = offset

    @property
    def is_valid(self):
        return self._child_ref() is not None

    def __call__(self):
        return self._child_ref()

    def update_position(self, projected_position):
        child = self._child_ref()
        if child is None:
            return
        x, y = projected_position
        width, height = child.GetCurrentAbsoluteSize()
        if width is None:
            width = 0
        if height is None:
            height = 0
        anchor_x, anchor_y = self.anchor
        offset_x, offset_y = self.offset
        child.translation = (eveui.scale_dpi(x - anchor_x * width + offset_x), eveui.scale_dpi(y - anchor_y * height + offset_y))


from dynamicresources.client.ess.bracket.debug import __reload_update__
