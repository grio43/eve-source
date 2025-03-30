#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\epic_arcs\page.py
import carbonui
import eveui
import eveformat
import localization
from evelink.client import faction_link
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.shared.epicArcs.epicArcChapterCont import EpicArcChapters
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from jobboard.client.ui.pages.details_page import JobPage
from jobboard.client.ui.progress_bar import ProgressGauge

class EpicArcPage(JobPage):

    def _construct_body(self, parent_container):
        carbonui.TextBody(parent=parent_container, align=eveui.Align.to_top, text=self.job.tag_line, padTop=12, padBottom=12, italic=True)
        container = eveui.Container(parent=parent_container, align=eveui.Align.to_top, height=64, padTop=12, padBottom=12)
        self._construct_progress(container)
        self._construct_faction(container)
        self._construct_chapters(parent_container)

    def _construct_progress(self, parent_container):
        if not self.job.is_active:
            return
        gauge_container = eveui.Container(name='gauge_container', parent=parent_container, align=eveui.Align.to_left_prop, width=0.5)
        self._gauge = ProgressGauge(parent=gauge_container, align=eveui.Align.to_left, radius=32, show_label=True, value=self.job.progress_percentage)
        text_container = eveui.ContainerAutoSize(parent=gauge_container, align=carbonui.Align.VERTICALLY_CENTERED, padLeft=8)
        self._progress_value = carbonui.TextBody(parent=text_container, align=eveui.Align.to_top, text=u'{}/{}'.format(eveformat.number(self.job.current_progress), eveformat.number(self.job.target_progress)))
        self._progress_label = carbonui.TextBody(parent=text_container, align=eveui.Align.to_top, text=localization.GetByLabel('UI/Agents/MissionsCompleted'), color=carbonui.TextColor.SECONDARY)

    def _construct_faction(self, parent_container):
        faction_id = self.job.faction_id
        if not faction_id:
            return
        container = eveui.Container(parent=parent_container, align=eveui.Align.to_top, height=64)
        OwnerIcon(parent=container, state=eveui.State.normal, align=eveui.Align.to_left, width=64, height=64, ownerID=faction_id, opacity=carbonui.TextColor.HIGHLIGHT.opacity)
        text_container = eveui.ContainerAutoSize(parent=container, align=carbonui.Align.VERTICALLY_CENTERED, padLeft=8)
        carbonui.TextBody(parent=text_container, state=eveui.State.normal, align=eveui.Align.to_top, text=faction_link(faction_id))

    def _construct_chapters(self, parent_container):
        agency_provider = sm.GetService('agencyNew').GetContentProvider(contentGroupConst.contentGroupEpicArcs)
        agency_content_piece = None
        for content_piece in agency_provider.GetContentPieces():
            if content_piece.epicArc.epicArcID == self.job.epic_arc_id:
                agency_content_piece = content_piece
                break

        if not agency_content_piece:
            return
        container = eveui.ContainerAutoSize(parent=parent_container, align=eveui.Align.to_top, padTop=12, padBottom=12)
        EpicArcChapters(parent=container, contentPiece=agency_content_piece)
