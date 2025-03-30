#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\list_entry.py
import carbonui
import eveui
from carbonui import Align, TextColor
from eve.client.script.ui import eveColor
from eveicon import IconData
from jobboard.client.ui.base_list_entry import BaseJobListEntry
from jobboard.client.ui.track_button import TrackJobIconButton
GLOW_IDLE = 0.5
GLOW_HOVER = 1.0
GLOW_MOUSE_DOWN = 2.0
OPACITY_IDLE = 0.1
OPACITY_HOVER = 0.2
OPACITY_MOUSEDOWN = 0.4
FLAIR_SIZE = 300

class JobListEntry(BaseJobListEntry):

    def _construct_left_side(self):
        self._construct_solar_system_chip()
        self._construct_left_content(self.left_container)
        self._construct_title_icons(self.left_container)
        title_container = eveui.Container(name='title_container', parent=self.left_container, align=Align.TOALL, clipChildren=True)
        carbonui.TextBody(parent=title_container, align=Align.CENTERLEFT, maxLines=1, text=self.job.title, bold=True, autoFadeSides=16)

    def _construct_right_side(self):
        self._construct_attention_icons(self.right_container)
        self._track_button_container = eveui.ContainerAutoSize(name='track_button_container', parent=self.right_container, align=Align.TORIGHT)
        if not self.job.is_tracked:
            self._track_button_container.opacity = 0
            self._track_button_container.DisableAutoSize()
        TrackJobIconButton(parent=self._track_button_container, align=Align.TORIGHT, job=self.job)
        self._actions_container = eveui.ContainerAutoSize(name='_actions_container', parent=self.right_container, align=Align.TORIGHT, padLeft=4, opacity=0.0)
        self._actions_container.DisableAutoSize()
        self._construct_actions(self._actions_container)
        self.right_content_container = eveui.Container(name='right_content_container', parent=self.right_container, align=Align.TOALL, clipChildren=True)
        self._construct_right_content(self.right_content_container)

    def _construct_attention_icons(self, parent):
        pass

    def _construct_actions(self, parent):
        pass

    def _construct_right_content(self, parent):
        self._construct_subtitle(parent, self.job.subtitle)

    def _construct_reward_icon_and_label(self, icon, value_text):
        cont = eveui.ContainerAutoSize(parent=self.right_content_container, align=Align.TOLEFT, padRight=8)
        icon = eveui.Sprite(parent=cont, align=eveui.Align.center_left, pos=(0, 0, 16, 16), texturePath=icon, color=TextColor.SECONDARY if isinstance(icon, IconData) else eveColor.WHITE)
        label = carbonui.TextBody(parent=cont, align=eveui.Align.center_left, left=20, maxLines=1, autoFadeSides=16, text=value_text, color=TextColor.NORMAL)
        return (icon, label)

    def _construct_subtitle(self, parent, subtitle):
        if subtitle:
            text_container = eveui.Container(parent=parent, align=carbonui.Align.TOALL, clipChildren=True)
            carbonui.TextBody(parent=text_container, align=carbonui.Align.CENTERLEFT, maxLines=1, autoFadeSides=16, text=subtitle)

    def OnMouseEnter(self, *args):
        super(JobListEntry, self).OnMouseEnter(*args)
        eveui.animation.fade_in(self._actions_container, duration=0.3)
        self._actions_container.ExpandWidth()
        eveui.animation.fade_in(self._track_button_container, duration=0.3)
        self._track_button_container.ExpandWidth()

    def OnMouseExit(self, *args):
        super(JobListEntry, self).OnMouseExit(*args)
        eveui.animation.fade_out(self._actions_container, duration=0.2)
        self._actions_container.CollapseWidth(duration=0.3)
        if not self.job.is_tracked:
            eveui.animation.fade_out(self._track_button_container, duration=0.2)
            self._track_button_container.CollapseWidth(duration=0.3)
