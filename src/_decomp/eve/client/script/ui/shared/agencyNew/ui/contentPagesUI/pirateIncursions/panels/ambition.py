#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\pirateIncursions\panels\ambition.py
from carbonui import uiconst, TextBody
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.section import SectionAutoSize
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.base import BasePanel
from localization import GetByLabel

class AmbitionPanel(BasePanel):

    def __init__(self, *args, **kwargs):
        super(AmbitionPanel, self).__init__(*args, **kwargs)
        self._construct_layout()

    def _construct_layout(self):
        self._ambition_section = SectionAutoSize(name='ambition_section', parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/PirateIncursions/Guides/Ambition/AmbitionSectionTitle'))
        scroll = ScrollContainer(parent=self._ambition_section, align=uiconst.TOTOP, height=180)
        self._ambition_label = TextBody(name='ambition_label', parent=scroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/PirateIncursions/Guides/Ambition/AmbitionSectionText'), padding=5)

    def get_searchable_strings(self):
        return [self._ambition_section.headerText, self._ambition_label.GetText()]
