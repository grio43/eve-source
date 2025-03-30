#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\zarzakh\panels\hq.py
from carbonui.primitives.container import Container
from carbonui import uiconst, TextBody
from carbonui.control.section import SectionAutoSize
from carbonui.primitives.gridcontainer import GridContainer
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.zarzakh.panels.base import BasePanel
from localization import GetByLabel

class HQPanel(BasePanel):

    def __init__(self, *args, **kwargs):
        super(HQPanel, self).__init__(*args, **kwargs)
        self._station_section = None
        self._station_label = None
        self._docking_rules_label = None
        self._available_services_label = None
        self._benefits_section = None
        self._benefits_label = None
        self._construct_layout()

    def _construct_layout(self):
        self._construct_station_section()
        self._construct_benefits_section()

    def _construct_station_section(self):
        self._station_section = SectionAutoSize(name='station_section', parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/Zarzakh/Guides/HQ/StationSectionTitle'))
        self._station_label = TextBody(name='station_label', parent=self._station_section, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Zarzakh/Guides/HQ/StationSectionText'), padding=5)
        grid_container = GridContainer(name='grid_container', parent=self._station_section, align=uiconst.TOTOP, contentSpacing=(0, 0), columns=2, height=150)
        self._docking_rules_label = TextBody(name='docking_rules_label', parent=grid_container, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Zarzakh/Guides/HQ/StationSectionDockingRules'), padding=10)
        self._available_services_label = TextBody(name='available_services_label', parent=grid_container, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Zarzakh/Guides/HQ/StationSectionAvailableServices'), padding=10)

    def _construct_benefits_section(self):
        self._benefits_section = SectionAutoSize(name='benefits_section', parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/Zarzakh/Guides/HQ/BenefitsSectionTitle'), padTop=20)
        self._benefits_label = TextBody(name='benefits_label', parent=self._benefits_section, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Zarzakh/Guides/HQ/BenefitsSectionText'), padding=5)

    def get_searchable_strings(self):
        return [self._station_section.headerText,
         self._station_label.GetText(),
         self._docking_rules_label.GetText(),
         self._available_services_label.GetText(),
         self._benefits_section.headerText,
         self._benefits_label.GetText()]
