#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\zarzakh\panels\shipcaster.py
from carbonui import uiconst, TextBody
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.section import SectionAutoSize, Section
from carbonui.primitives.gridcontainer import GridContainer
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.encounters.pirateIncursions.pirateIncursionsHomeContentGroup import PirateIncursionsHomeContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards.horizontalContentGroupCard import HorizontalContentGroupCard
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.zarzakh.panels.base import BasePanel
from localization import GetByLabel

class ShipcasterPanel(BasePanel):
    default_clipChildren = True

    def __init__(self, *args, **kwargs):
        super(ShipcasterPanel, self).__init__(*args, **kwargs)
        self._shipcaster_section = None
        self._shipcaster_label = None
        self._goals_section = None
        self._goals_label = None
        self._incursions_section = None
        self._incursions_label = None
        self._construct_layout()

    def _construct_layout(self):
        self._shipcaster_section = SectionAutoSize(name='shipcaster_section', parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/Zarzakh/Guides/Shipcaster/ShipcasterSectionTitle'))
        self._shipcaster_label = TextBody(name='shipcaster_label', parent=self._shipcaster_section, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Zarzakh/Guides/Shipcaster/ShipcasterSectionText'), padding=5)
        grid_container = GridContainer(name='grid_container', parent=self, align=uiconst.TOALL, contentSpacing=(20, 20), columns=2)
        self._goals_section = SectionAutoSize(name='goals_section', parent=grid_container, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/Zarzakh/Guides/Shipcaster/GoalsSectionTitle'))
        self._goals_label = TextBody(name='goals_label', parent=self._goals_section, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Zarzakh/Guides/Shipcaster/GoalsSectionText'), padding=5)
        self._incursions_section = Section(name='incursions_section', parent=grid_container, align=uiconst.TOALL, headerText=GetByLabel('UI/Agency/Zarzakh/Guides/Shipcaster/IncursionsSectionTitle'))
        self._incursions_section_scroll = ScrollContainer(parent=self._incursions_section, align=uiconst.TOALL, alignMode=uiconst.TOTOP, name='_incursions_section_scroll')
        self._incursions_label = TextBody(name='incursions_label', parent=self._incursions_section_scroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Zarzakh/Guides/Shipcaster/IncursionsSectionText'), padding=5)
        HorizontalContentGroupCard(name='pirate_incursions_card', parent=self._incursions_section_scroll, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, contentGroup=PirateIncursionsHomeContentGroup(), contentGroupID=contentGroupConst.contentGroupPirateIncursionsHome, opacity=1.0, padTop=10)
        Button(name='enlistment_button', parent=self._incursions_section_scroll, align=uiconst.TOTOP, texturePath='res:/UI/Texture/WindowIcons/factionalwarfare.png', label=GetByLabel('UI/Agency/FactionWarfare/openFactionWarfareWindow'), func=sm.GetService('cmd').OpenMilitia, padTop=15)

    def get_searchable_strings(self):
        return [self._shipcaster_section.headerText,
         self._shipcaster_label.GetText(),
         self._goals_section.headerText,
         self._goals_label.GetText(),
         self._incursions_section.headerText,
         self._incursions_label.GetText()]
