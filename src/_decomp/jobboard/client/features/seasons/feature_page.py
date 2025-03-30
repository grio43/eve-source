#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\seasons\feature_page.py
import localization
from carbonui import Align
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from jobboard.client.ui.pages.content_tag_page import ContentTagPage
from seasons.client.util import OpenSeasonsWindow

class SeasonsFeaturePage(ContentTagPage):

    def _construct_header_description(self, parent):
        super(SeasonsFeaturePage, self)._construct_header_description(parent)
        button_container = ContainerAutoSize(parent=parent, align=Align.TOTOP, padTop=12)
        Button(parent=button_container, label=localization.GetByLabel('UI/Opportunities/OpenAgency'), func=self._open_agency)

    def _open_agency(self, *args, **kwargs):
        OpenSeasonsWindow()
