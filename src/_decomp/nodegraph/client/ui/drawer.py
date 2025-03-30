#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\drawer.py
import eveui
import threadutils
DRAWER_PAD_DIRECTION = {eveui.Align.to_left: 'padLeft',
 eveui.Align.to_right: 'padRight',
 eveui.Align.to_top: 'padTop',
 eveui.Align.to_bottom: 'padBottom'}

class Drawer(eveui.Container):
    default_name = 'Drawer'
    default_align = eveui.Align.to_all
    default_state = eveui.State.disabled
    default_bgColor = (0, 0, 0, 0.25)
    default_opacity = 0
    default_clipChildren = True
    drawer_animation_time = 0.2

    def __init__(self, content = None, drawer_size = 250, drawer_alignment = eveui.Align.to_left, **kwargs):
        super(Drawer, self).__init__(**kwargs)
        self._drawer_size = drawer_size
        self.content_container = None
        self._is_open = False
        self._transitioning = False
        self._layout()
        self.set_content(content)
        self._content_drawer.align = drawer_alignment
        self._update_drawer_padding()

    def open(self, content = None, drawer_size = None, drawer_alignment = None):
        if self._is_open or self._transitioning:
            return
        self._update_content(content, drawer_size, drawer_alignment)
        self._open()

    def close(self):
        if not self._is_open or self._transitioning:
            return
        self._close()

    def set_content(self, content):
        if content:
            self._content_container.Flush()
            content.SetParent(self._content_container)

    @threadutils.threaded
    def _update_content(self, content, drawer_size, drawer_alignment):
        self.set_content(content)
        if drawer_size:
            self._drawer_size = drawer_size
            self._content_drawer.SetSize(drawer_size, drawer_size)
        if drawer_alignment:
            self._content_drawer.align = drawer_alignment
            self._update_drawer_padding()

    @threadutils.threaded
    def _open(self):
        self._is_open = True
        self._transitioning = True
        self.state = eveui.State.pick_children
        eveui.fade_in(self, duration=self.drawer_animation_time)
        eveui.animate(self._content_drawer, DRAWER_PAD_DIRECTION[self._content_drawer.align], end_value=0, duration=self.drawer_animation_time)
        self._transitioning = False

    @threadutils.threaded
    def _close(self):
        self._is_open = False
        self._transitioning = True
        self.state = eveui.State.disabled
        eveui.fade_out(self, duration=self.drawer_animation_time)
        eveui.animate(self._content_drawer, DRAWER_PAD_DIRECTION[self._content_drawer.align], end_value=-self._drawer_size, duration=self.drawer_animation_time)
        self._transitioning = False

    def _update_drawer_padding(self):
        self._content_drawer.padding = 0
        setattr(self._content_drawer, DRAWER_PAD_DIRECTION[self._content_drawer.align], -self._drawer_size)

    def _handle_close(self, *args, **kwargs):
        if self._transitioning:
            return
        self.close()

    def _layout(self):
        self._content_drawer = eveui.Container(name='content_drawer', parent=self, state=eveui.State.normal, width=self._drawer_size, height=self._drawer_size, bgColor=(0, 0, 0, 0.9))
        self._outside_container = eveui.Container(parent=self, state=eveui.State.normal, align=eveui.Align.to_all)
        self._outside_container.OnClick = self._handle_close
        self._outside_container.GetMenu = self._handle_close
        self._content_container = eveui.Container(name='content_container', parent=self._content_drawer, align=eveui.Align.to_all, padding=16, clipChildren=True)
