#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\pirateIncursions\panels\insurgencies.py
from carbonui.control.scrollContainer import ScrollContainer
from carbonui import uiconst, TextBody
from carbonui.control.section import SectionAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.base import BasePanel
from localization import GetByLabel

class InsurgenciesPanel(BasePanel):
    default_clipChildren = True

    def __init__(self, *args, **kwargs):
        super(InsurgenciesPanel, self).__init__(*args, **kwargs)
        self._construct_layout()

    def _construct_layout(self):
        self._insurgencies_section = SectionAutoSize(name='_insurgencies_section', parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/PirateIncursions/Guides/Insurgencies/InsurgenciesSectionTitle'))
        scroll = ScrollContainer(parent=self._insurgencies_section, align=uiconst.TOTOP, height=240)
        self._insurgencies_label = TextBody(name='_insurgencies_label', parent=scroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/PirateIncursions/Guides/Insurgencies/InsurgenciesSectionText'), padding=5)
        Sprite(name='insurgency_image', parent=self, align=uiconst.TOTOP, width=790, height=233, texturePath='res:/UI/Texture/classes/agency/pirateIncursions/Insurgencies.png', state=uiconst.UI_DISABLED, padTop=5, padBottom=5)

    def get_searchable_strings(self):
        return [self._insurgencies_section.headerText, self._insurgencies_label.GetText()]
