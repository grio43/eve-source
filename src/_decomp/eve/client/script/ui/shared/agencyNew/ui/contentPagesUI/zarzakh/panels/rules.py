#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\zarzakh\panels\rules.py
from carbonui import uiconst, TextBody
from carbonui.control.section import SectionAutoSize
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.zarzakh.panels.base import BasePanel
from localization import GetByLabel

class RulesPanel(BasePanel):

    def __init__(self, *args, **kwargs):
        super(RulesPanel, self).__init__(*args, **kwargs)
        self._zarzakh_section = None
        self._zarzakh_label = None
        self._regulations_section = None
        self._regulations_label = None
        self._construct_layout()

    def _construct_layout(self):
        self._zarzakh_section = SectionAutoSize(name='zarzakh_section', parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/Zarzakh/Guides/Rules/ZarzakhSectionTitle'))
        self._zarzakh_label = TextBody(name='zarzakh_label', parent=self._zarzakh_section, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Zarzakh/Guides/Rules/ZarzakhSectionText'), padding=5)
        self._regulations_section = SectionAutoSize(name='regulations_section', parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/Zarzakh/Guides/Rules/RegulationsSectionTitle'), padTop=20)
        self._regulations_label = TextBody(name='regulations_label', parent=self._regulations_section, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Zarzakh/Guides/Rules/RegulationsSectionText'), padding=5)

    def get_searchable_strings(self):
        return [self._zarzakh_section.headerText,
         self._zarzakh_label.GetText(),
         self._regulations_section.headerText,
         self._regulations_label.GetText()]
