#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\pirateIncursions\panels\fob_lp.py
from carbonui import uiconst, TextBody
from carbonui.control.section import SectionAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.base import BasePanel
from localization import GetByLabel

class FOBPanel(BasePanel):
    default_clipChildren = True

    def __init__(self, *args, **kwargs):
        super(FOBPanel, self).__init__(*args, **kwargs)
        self._construct_layout()

    def _construct_layout(self):
        self._fob_section = SectionAutoSize(name='fob_section', parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/PirateIncursions/Guides/FOBandLP/FOBSectionTitle'))
        Sprite(name='fob_image', parent=self._fob_section, align=uiconst.TOTOP, width=790, height=166, texturePath='res:/UI/Texture/classes/agency/pirateIncursions/PirateFOB.png', state=uiconst.UI_DISABLED, padTop=5, padBottom=5)
        self._fob_label = TextBody(name='fob_label', parent=self._fob_section, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/PirateIncursions/Guides/FOBandLP/FOBSectionText'), padding=5)
        self._lpstores_section = SectionAutoSize(name='lpstores_section', parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/PirateIncursions/Guides/FOBandLP/LPSectionTitle'))
        self._lpstores_label = TextBody(name='lpstores_label', parent=self._lpstores_section, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/PirateIncursions/Guides/FOBandLP/LPSectionText'), padding=5)

    def get_searchable_strings(self):
        return [self._fob_section.headerText,
         self._fob_label.GetText(),
         self._lpstores_section.headerText,
         self._lpstores_label.GetText()]
