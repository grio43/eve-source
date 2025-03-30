#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\epic_arcs\card.py
import carbonui
import eveui
from carbonui import Align, uiconst, PickState
from carbonui.primitives.sprite import Sprite
from jobboard.client.ui.card import JobHeroCard
from jobboard.client.ui.list_entry import JobListEntry
from jobboard.client.ui.progress_bar import ProgressGauge

class EpicArcCard(JobHeroCard):

    def _on_job_updated(self):
        self._update_gauge()
        self._update_state()

    def _construct_top_right(self):
        self._gauge = ProgressGauge(parent=self._top_right_container, align=Align.CENTER, radius=25, bg_opacity=0.6)
        self._update_gauge(animate=False)

    def _construct_underlay(self):
        container = eveui.Container(name='epic_container', parent=self, align=Align.TOALL, clipChildren=True)
        right_cont = eveui.Container(name='right', parent=container, padding=(0, 16, 8, 16), align=Align.TORIGHT, width=64)
        logo_container = eveui.ContainerAutoSize(name='logo_container', parent=right_cont, align=Align.TOBOTTOM)
        self.faction_logo = Sprite(name='faction_icon', parent=logo_container, align=Align.CENTER, width=48, height=48, color=carbonui.TextColor.SECONDARY, texturePath=self.job.faction_logo, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0, pickState=PickState.OFF)
        super(EpicArcCard, self)._construct_underlay()

    def _update_gauge(self, animate = True):
        if self.job.is_active:
            self._gauge.Show()
            self._gauge.set_value(self.job.progress_percentage, animate=animate)
        else:
            self._gauge.Hide()

    def OnMouseEnter(self, *args):
        super(EpicArcCard, self).OnMouseEnter(*args)
        eveui.animate(self.faction_logo, 'color', carbonui.TextColor.NORMAL, duration=0.2)
        eveui.animate(self.faction_logo, 'glowBrightness', 0.5, duration=0.2)

    def OnMouseExit(self, *args):
        super(EpicArcCard, self).OnMouseExit(*args)
        eveui.animate(self.faction_logo, 'color', carbonui.TextColor.SECONDARY, duration=0.2)
        eveui.animate(self.faction_logo, 'glowBrightness', 0, duration=0.2)

    def _update_hover_frame_color(self):
        pass


class EpicArcListEntry(JobListEntry):

    def _on_job_updated(self):
        self._update_gauge()
        self._update_state()

    def _construct_left_content(self, parent):
        super(EpicArcListEntry, self)._construct_left_content(parent)
        gauge_container = eveui.ContainerAutoSize(name='gauge_container', parent=parent, align=eveui.Align.to_right, padRight=8)
        self._gauge = ProgressGauge(parent=gauge_container, align=eveui.Align.center, radius=12, show_label=False)
        self._update_gauge(animate=False)

    def _update_gauge(self, animate = True):
        if self.job.is_active:
            self._gauge.Show()
            self._gauge.set_value(self.job.progress_percentage, animate=animate)
        else:
            self._gauge.Hide()
