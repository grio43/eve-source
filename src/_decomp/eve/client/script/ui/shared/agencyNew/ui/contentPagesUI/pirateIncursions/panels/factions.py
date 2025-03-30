#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\pirateIncursions\panels\factions.py
import eveicon
from carbonui.control.scrollContainer import ScrollContainer
from carbonui import uiconst, TextBody
from carbonui.control.section import SectionAutoSize
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.base import BasePanel
from localization import GetByLabel
from carbonui.control.button import Button

class FactionsPanel(BasePanel):

    def __init__(self, *args, **kwargs):
        super(FactionsPanel, self).__init__(*args, **kwargs)
        self._pirates_section = None
        self._pirates_label = None
        self._zarzakh_section = None
        self._zarzakh_label = None
        self._construct_layout()

    def _construct_layout(self):
        self._pirates_section = SectionAutoSize(name='pirates_section', parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/PirateIncursions/Guides/Factions/PiratesSectionTitle'))
        piratesScroll = ScrollContainer(parent=self._pirates_section, align=uiconst.TOTOP, height=130)
        self._pirates_label = TextBody(name='pirates_label', parent=piratesScroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/PirateIncursions/Guides/Factions/PirateSectionText'), padding=5)
        self._zarzakh_section = SectionAutoSize(name='zarzakh_section', parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/PirateIncursions/Guides/Factions/ZarzakhSectionTitle'), padTop=20)
        zarzakhScroll = ScrollContainer(parent=self._zarzakh_section, align=uiconst.TOTOP, height=130)
        self._zarzakh_label = TextBody(name='zarzakh_label', parent=zarzakhScroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/PirateIncursions/Guides/Factions/ZarzakhSectionText'), padding=5)
        self.actions_container = Container(name='actions_container', parent=self._zarzakh_section, align=uiconst.TOTOP, height=agencyUIConst.CONTENTCARD_HEIGHT, padTop=15)
        button_container = Container(name='button_container', parent=self.actions_container, align=uiconst.TOLEFT_PROP, height=agencyUIConst.CONTENTCARD_HEIGHT, padTop=15, width=0.5)
        Button(name='openEnlistmentButton', parent=button_container, align=uiconst.CENTER, texturePath=eveicon.open_window, label=GetByLabel('UI/Agency/PirateIncursions/openPirateEnlistmentWindow'), func=sm.GetService('cmd').OpenFwEnlistment)

    def get_searchable_strings(self):
        return [self._pirates_section.headerText,
         self._pirates_label.GetText(),
         self._zarzakh_section.headerText,
         self._zarzakh_label.GetText()]
