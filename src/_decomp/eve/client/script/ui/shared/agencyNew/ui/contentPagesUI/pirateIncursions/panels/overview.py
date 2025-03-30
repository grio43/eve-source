#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\pirateIncursions\panels\overview.py
from carbonui.control.scrollContainer import ScrollContainer
from carbonui import uiconst, TextBody
from carbonui.control.section import SectionAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.base import BasePanel
from localization import GetByLabel

class OverviewPanel(BasePanel):

    def __init__(self, *args, **kwargs):
        super(OverviewPanel, self).__init__(*args, **kwargs)
        self._overview_section = None
        self._overview_label = None
        self._construct_layout()

    def _construct_layout(self):
        Sprite(name='overview_image', parent=self, align=uiconst.TOTOP, width=790, height=258, texturePath='res:/UI/Texture/classes/agency/pirateIncursions/PirateInsurgencyGuideOverview.png', state=uiconst.UI_DISABLED, padBottom=5)
        self._overview_section = SectionAutoSize(name='overview_section', parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/PirateIncursions/Guides/Overview/OverviewSectionTitle'))
        scroll = ScrollContainer(parent=self._overview_section, align=uiconst.TOTOP, height=180)
        self._overview_label = TextBody(name='overview_label', parent=scroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/PirateIncursions/Guides/Overview/OverviewSectionText'), padding=5)

    def get_searchable_strings(self):
        return [self._overview_section.headerText, self._overview_label.GetText()]
