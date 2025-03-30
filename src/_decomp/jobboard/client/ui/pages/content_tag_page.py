#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\pages\content_tag_page.py
import carbonui
import eveui
from metadata import get_content_tag_as_object
from .filtered_page import FilteredPage

class ContentTagPage(FilteredPage):
    ONLY_FROM_PROVIDER_ID = None

    def __init__(self, window_controller, content_tag_id, **kwargs):
        self._content_tag = get_content_tag_as_object(content_tag_id)
        super(ContentTagPage, self).__init__(window_controller=window_controller, **kwargs)

    @property
    def primary_content_tag_id(self):
        return self._content_tag.id

    @property
    def info_tooltip(self):
        return ''

    @property
    def _page_title(self):
        return self._content_tag.title

    @property
    def _page_description(self):
        return self._content_tag.description

    @property
    def _page_icon(self):
        return self._content_tag.icon

    def _get_jobs(self):
        return self._service.get_available_jobs(filters=self._filters_controller.get_as_dict(), provider_id=self.ONLY_FROM_PROVIDER_ID)

    def _validate_job(self, job):
        if self.ONLY_FROM_PROVIDER_ID and job.provider_id != self.ONLY_FROM_PROVIDER_ID:
            return False
        return job.is_available_in_browse and super(ContentTagPage, self)._validate_job(job)

    def _construct_header(self):
        self._construct_header_content(self._header_container)
        super(ContentTagPage, self)._construct_header()

    def _construct_header_content(self, parent):
        header = eveui.ContainerAutoSize(parent=parent, align=carbonui.Align.TOTOP, padTop=32, padBottom=32)
        self._construct_header_title(header)
        self._construct_header_description(header)

    def _construct_header_title(self, parent):
        title_container = eveui.ContainerAutoSize(parent=parent, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOPLEFT)
        icon = self._page_icon
        carbonui.TextHeadline(parent=title_container, align=carbonui.Align.TOPLEFT, text=self._page_title, bold=True, padLeft=24 if icon else 0, color=carbonui.TextColor.HIGHLIGHT)
        if icon:
            eveui.Sprite(parent=title_container, align=carbonui.Align.CENTERLEFT, texturePath=icon, height=16, width=16, color=carbonui.TextColor.HIGHLIGHT)

    def _construct_header_description(self, parent):
        description = self._page_description
        if description:
            subtitle_container = eveui.ContainerAutoSize(parent=parent, align=carbonui.Align.TOTOP, padTop=8)
            carbonui.TextBody(parent=subtitle_container, align=carbonui.Align.TOPLEFT, text=description, maxWidth=400)
