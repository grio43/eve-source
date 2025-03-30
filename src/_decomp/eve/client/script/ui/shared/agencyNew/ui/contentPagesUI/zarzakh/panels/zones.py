#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\zarzakh\panels\zones.py
from carbonui import uiconst, TextBody
from carbonui.control.section import SectionAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.zarzakh.panels.base import BasePanel
from localization import GetByLabel

class ZonesPanel(BasePanel):

    def __init__(self, *args, **kwargs):
        super(ZonesPanel, self).__init__(*args, **kwargs)
        self._zones_section = None
        self._zones_label = None
        self._construct_layout()

    def _construct_layout(self):
        self._zones_section = SectionAutoSize(name='zones_section', parent=self, align=uiconst.TOALL, headerText=GetByLabel('UI/Agency/Zarzakh/Guides/Zones/ZonesSectionTitle'))
        Sprite(name='zones_image', parent=self._zones_section, align=uiconst.TOTOP, width=739, height=241, texturePath='res:/UI/Texture/classes/agency/zarzakh/zones/banner.png', state=uiconst.UI_DISABLED, padTop=5, padBottom=5)
        self._zones_label = TextBody(name='zones_label', parent=self._zones_section, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Zarzakh/Guides/Zones/ZonesSectionText'), padding=5)

    def get_searchable_strings(self):
        return [self._zones_section.headerText, self._zones_label.GetText()]
