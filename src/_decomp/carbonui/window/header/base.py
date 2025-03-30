#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\header\base.py
import weakref
from carbonui.primitives.base import Base

class WindowHeaderBase(Base):
    COLLAPSED_HEIGHT = 32
    HAS_SUFFICIENT_BOTTOM_PADDING = False

    def __init__(self, **kwargs):
        self.__window_ref = None
        super(WindowHeaderBase, self).__init__(**kwargs)

    @property
    def window(self):
        window = self.__window_ref() if self.__window_ref is not None else None
        if window is not None and not window.closing:
            return window
        else:
            return

    def mount(self, window):
        self.__window_ref = weakref.ref(window)

    def unmount(self, window):
        self.__window_ref = None
