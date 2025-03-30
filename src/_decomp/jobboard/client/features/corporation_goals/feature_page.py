#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\corporation_goals\feature_page.py
import carbonui
import eveui
from eve.client.script.ui.control.eveIcon import CorpIcon
from evelink.client import corporation_link
import localization
from jobboard.client.ui.pages.content_tag_page import ContentTagPage

class CorporationGoalsFeaturePage(ContentTagPage):

    @property
    def info_tooltip(self):
        return localization.GetByLabel('UI/Opportunities/VisibilityCorporationProjects')

    def _construct_header_description(self, parent):
        corporation_id = session.corpid
        if not corporation_id:
            return
        corporation_container = eveui.Container(parent=parent, align=eveui.Align.to_top, height=48, padTop=8)
        CorpIcon(parent=corporation_container, state=eveui.State.normal, align=eveui.Align.center_left, size=48, corpID=corporation_id)
        text_container = eveui.ContainerAutoSize(parent=corporation_container, align=carbonui.Align.VERTICALLY_CENTERED, padLeft=64)
        carbonui.TextHeader(parent=text_container, state=eveui.State.normal, align=eveui.Align.to_top, text=corporation_link(corporation_id), maxLines=2)
