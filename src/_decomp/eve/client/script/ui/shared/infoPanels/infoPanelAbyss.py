#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelAbyss.py
from carbonui import Align
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.infoPanels.const.infoPanelConst import PANEL_ABYSS
from eve.common.script.sys.idCheckers import IsAbyssalSpaceSystem
from localization import GetByLabel
from objectives.client.ui.objective_chain import ObjectiveChainEntry
from objectives.client.qa_tools import get_objective_chain_context_menu
SCROLL_CONTAINER_HEIGHT_MAX = 450
HEADER_BG_COLOR = (0, 0, 0, 0.35)

class InfoPanelAbyss(InfoPanelBase):
    default_name = 'InfoPanelAbyss'
    panelTypeID = PANEL_ABYSS
    label = 'UI/Agency/ContentGroups/ContentGroupAbyssalDeadspace'

    def ConstructLayout(self):
        super(InfoPanelAbyss, self).ConstructLayout()
        self.header = self.headerCls(parent=self.headerCont, align=Align.CENTERLEFT, text=GetByLabel(self.label))

    @staticmethod
    def IsAvailable():
        if not IsAbyssalSpaceSystem(session.solarsystemid2):
            return False
        objective_chain = sm.GetService('abyss').objective_chain
        if objective_chain:
            return True
        return False

    def __init__(self, **kwargs):
        super(InfoPanelAbyss, self).__init__(**kwargs)

    def ConstructNormal(self):
        if self.destroyed:
            return
        self.mainCont.Flush()
        objective_chain = self.service.objective_chain
        ObjectiveChainEntry(parent=self.mainCont, objective_chain=objective_chain)
        self.headerButton.GetMenu = self.GetMenuHeaderMenu

    def GetMenuHeaderMenu(self):
        objective_chain = self.service.objective_chain
        if objective_chain:
            return get_objective_chain_context_menu(objective_chain, include_blackboard=True)

    def ConstructHeaderButton(self):
        return self.ConstructSimpleHeaderButton()

    @property
    def service(self):
        return sm.GetService('abyss')
