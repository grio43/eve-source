#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\info\ships.py
import evetypes
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.themeColored import FillThemeColored
from expertSystems import get_expert_system
from localization import GetByLabel

class ShipsPanel(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.expertSystemTypeID = attributes.get('expertSystemTypeID', None)
        self.expertSystem = get_expert_system(self.expertSystemTypeID)
        self.loaded = False

    def Load(self):
        if self.loaded:
            return
        self.loaded = True
        if not self.expertSystem.associated_type_ids:
            infoCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, clipChildren=True, padding=4)
            FillThemeColored(bgParent=infoCont, colorType=uiconst.COLORTYPE_UIBASECONTRAST)
            EveLabelLarge(text=GetByLabel('UI/InfoWindow/GenericExpertSystem'), parent=infoCont, align=uiconst.TOTOP, padding=10, autoFitToText=True, toolTipTextHeightThreshold=51)
            return
        scrolllist = []
        for shipTypeID in self.expertSystem.associated_type_ids:
            scrolllist.append(GetFromClass(Item, {'label': evetypes.GetName(shipTypeID),
             'typeID': shipTypeID,
             'showinfo': True,
             'getIcon': True,
             'showTooltip': False,
             'disableIcon': sm.GetService('cloneGradeSvc').IsRestrictedForAlpha(shipTypeID)}))

        scroll = Scroll(parent=self, align=uiconst.TOALL, padding=4)
        scroll.Load(fixedEntryHeight=27, contentList=scrolllist)
