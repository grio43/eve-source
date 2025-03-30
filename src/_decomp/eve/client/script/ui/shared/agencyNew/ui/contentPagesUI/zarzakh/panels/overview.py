#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\zarzakh\panels\overview.py
from carbonui import uiconst, TextBody
from carbonui.control.section import SectionAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.zarzakh.panels.base import BasePanel
from localization import GetByLabel

class OverviewPanel(BasePanel):

    def __init__(self, *args, **kwargs):
        super(OverviewPanel, self).__init__(*args, **kwargs)
        self._overview_section = None
        self._overview_label = None
        self._construct_layout()

    def _construct_layout(self):
        self._overview_section = SectionAutoSize(name='overview_section', parent=self, align=uiconst.TOALL, headerText=GetByLabel('UI/Agency/Zarzakh/Guides/Overview/OverviewSectionTitle'))
        Sprite(name='overview_image', parent=self._overview_section, align=uiconst.TOTOP, width=739, height=241, texturePath='res:/UI/Texture/classes/agency/zarzakh/overview/banner.png', state=uiconst.UI_DISABLED, padTop=5, padBottom=5)
        self._overview_label = TextBody(name='overview_label', parent=self._overview_section, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Zarzakh/Guides/Overview/OverviewSectionText'), padding=5)

    def get_searchable_strings(self):
        return [self._overview_section.headerText, self._overview_label.GetText()]
