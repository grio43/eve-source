#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\collapse_section.py
import math
import eveui

class CollapseSection(eveui.ContainerAutoSize):
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top

    def __init__(self, title, default_expanded = True, **kwargs):
        super(CollapseSection, self).__init__(**kwargs)
        self._expanded = settings.user.ui.Get(self._settings_id, default_expanded)
        eveui.Line(parent=self, align=eveui.Align.to_left, padRight=4)
        self._construct_header(title)
        self.content_container = None
        if self._expanded:
            self._construct_body()

    @property
    def is_content_constructed(self):
        return self.content_container is not None

    def construct_content(self):
        pass

    def refresh_content(self, *args, **kwargs):
        if self.content_container:
            self.content_container.Flush()
            if self._expanded:
                self.construct_content()
            else:
                self.content_container = None

    def _construct_header(self, title):
        self.header_container = container = eveui.ContainerAutoSize(parent=self, state=eveui.State.normal, align=eveui.Align.to_top, alignMode=eveui.Align.to_top)
        container.OnClick = self._on_header_click
        container.OnMouseEnter = self._on_header_enter
        container.OnMouseExit = self._on_header_exit
        self._header_fill = eveui.Fill(bgParent=container, opacity=0)
        self._expand_icon = eveui.Sprite(parent=container, align=eveui.Align.center_right, texturePath='res:/UI/Texture/classes/Neocom/arrowDown.png', opacity=0.7, width=8, height=8, left=8, rotation=self._icon_rotation)
        eveui.EveLabelLarge(parent=container, align=eveui.Align.to_top, padding=(4, 4, 12, 4), text=title)

    def _construct_body(self):
        self.content_container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_top, clipChildren=True)
        self.construct_content()

    @property
    def _icon_rotation(self):
        if self._expanded:
            return 0.0
        return math.pi / 2.0

    @property
    def _settings_id(self):
        return 'collapsesection_{}'.format(self.name)

    def _on_header_click(self, *args):
        self._expanded = not self._expanded
        if self._expanded and not self.content_container:
            self._construct_body()
        settings.user.ui.Set(self._settings_id, self._expanded)
        duration = 0.2
        eveui.animate(self._expand_icon, 'rotation', end_value=self._icon_rotation, duration=duration)
        self.content_container.DisableAutoSize()
        goal_height = self.content_container.GetAutoSize()[1] if self._expanded else 0
        eveui.animate(self.content_container, 'height', end_value=goal_height, duration=duration, sleep=True)
        if self._expanded:
            self.content_container.EnableAutoSize()

    def _on_header_enter(self, *args):
        eveui.fade_in(self._header_fill, end_value=0.1, duration=0.1)

    def _on_header_exit(self, *args):
        eveui.fade_out(self._header_fill, duration=0.1)
