#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\zarzakh\panels\jovian.py
from carbonui import uiconst, TextBody
from carbonui.control.section import SectionAutoSize
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.gridcontainer import GridContainer
from stargate.client.const import GATE_LOCK_MAX_TIMER_HOURS
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.common.cards.destination import SetDestinationCard
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.zarzakh.panels.base import BasePanel
from inventorycommon.const import solarSystemZarzakh
from localization import GetByLabel

class JovianPanel(BasePanel):

    def __init__(self, *args, **kwargs):
        super(JovianPanel, self).__init__(*args, **kwargs)
        self._gates_section = None
        self._gates_label = None
        self._tolls_section = None
        self._tolls_label = None
        self._access_section = None
        self._gate_lock_section = None
        self._gate_lock_label = None
        self._construct_layout()

    def _construct_layout(self):
        self._gates_section = SectionAutoSize(name='gates_section', parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/Zarzakh/Guides/Jovian/GatesSectionTitle'))
        self._gates_label = TextBody(name='gates_label', parent=self._gates_section, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=GetByLabel('UI/Agency/Zarzakh/Guides/Jovian/GatesSectionText'), padding=5)
        grid_container = GridContainer(name='grid_container', parent=self, align=uiconst.TOTOP, contentSpacing=(20, 20), columns=2, height=150)
        self._tolls_section = SectionAutoSize(name='tolls_section', parent=grid_container, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/Zarzakh/Guides/Jovian/TollsSectionTitle'))
        self._tolls_label = TextBody(name='tolls_label', parent=self._tolls_section, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=GetByLabel('UI/Agency/Zarzakh/Guides/Jovian/TollsSectionText'), padding=5)
        rightPanel = ContainerAutoSize(name='rightPanel', parent=grid_container, align=uiconst.TOTOP)
        self._access_section = SectionAutoSize(name='access_section', parent=rightPanel, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/Zarzakh/Guides/Jovian/AccessSectionTitle'))
        SetDestinationCard(name='set_destination_card', parent=self._access_section, align=uiconst.TOTOP, solar_system_id=solarSystemZarzakh)
        self._gate_lock_section = SectionAutoSize(name='gates_section', parent=rightPanel, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/Zarzakh/Guides/Jovian/EmanationGateLockTitle'))
        self._gate_lock_section = TextBody(name='gate_lock_label', parent=self._gate_lock_section, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=GetByLabel('UI/Agency/Zarzakh/Guides/Jovian/EmanationGateLockText', hours=GATE_LOCK_MAX_TIMER_HOURS), padding=5)

    def get_searchable_strings(self):
        return [self._gates_section.headerText,
         self._gates_label.GetText(),
         self._tolls_section.headerText,
         self._tolls_label.GetText(),
         self._access_section.headerText]
