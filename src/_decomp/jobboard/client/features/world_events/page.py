#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\world_events\page.py
import carbonui
import eveui
import eveicon
import localization
from evelink.client import faction_link
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveIcon import OwnerIcon
from jobboard.client.ui.pages.details_page import JobPage, DetailsSection
from jobboard.client.ui.progress_bar import ProgressGauge
from jobboard.client.ui.time_remaining import TimeRemaining

class WorldEventPage(JobPage):

    def _construct_body(self, parent_container):
        if self.job.expiration_time:
            TimeRemaining(parent=parent_container, align=eveui.Align.to_top, padBottom=12, job=self.job)
        container = eveui.Container(parent=parent_container, align=eveui.Align.to_top, height=64, padTop=12, padBottom=12)
        self._construct_progress(container)
        self._construct_faction(container)
        self._construct_description(parent_container)

    def _construct_progress(self, parent_container):
        if not self.job.has_influence:
            return
        gauge_container = eveui.Container(name='gauge_container', parent=parent_container, align=eveui.Align.to_left_prop, width=0.5)
        self._gauge = ProgressGauge(parent=gauge_container, align=eveui.Align.to_left, radius=32, show_label=False, value=self.job.progress_percentage)
        Sprite(parent=self._gauge, align=carbonui.Align.CENTER, pos=(0, 0, 16, 16), color=carbonui.TextColor.SECONDARY, texturePath=eveicon.ongoing_conflicts)
        text_container = eveui.ContainerAutoSize(parent=gauge_container, align=carbonui.Align.VERTICALLY_CENTERED, padLeft=8)
        self._progress_value = carbonui.TextBody(parent=text_container, align=eveui.Align.to_top, text=u'{value}%'.format(value=int(self.job.progress_percentage * 100)))
        self._progress_label = carbonui.TextBody(parent=text_container, align=eveui.Align.to_top, color=carbonui.TextColor.SECONDARY, text=localization.GetByLabel('UI/WorldEvents/InfluenceProgress'))

    def _construct_description(self, parent_container):
        description = self.job.description
        if not description:
            return
        description_section = DetailsSection(name='details_section_description', parent=parent_container, title=localization.GetByLabel('UI/Common/Description'))
        container = description_section.content_container
        carbonui.TextBody(parent=container, align=eveui.Align.to_top, text=description)

    def _construct_faction(self, parent_container):
        faction_id = self.job.faction_id
        if not faction_id:
            return
        container = eveui.Container(parent=parent_container, align=eveui.Align.to_top, height=64)
        OwnerIcon(parent=container, state=eveui.State.normal, align=eveui.Align.to_left, width=64, height=64, ownerID=faction_id, opacity=carbonui.TextColor.HIGHLIGHT.opacity)
        text_container = eveui.ContainerAutoSize(parent=container, align=carbonui.Align.VERTICALLY_CENTERED, padLeft=8)
        carbonui.TextBody(parent=text_container, state=eveui.State.normal, align=eveui.Align.to_top, text=faction_link(faction_id))
