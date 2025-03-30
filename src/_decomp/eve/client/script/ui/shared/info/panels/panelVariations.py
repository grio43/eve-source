#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelVariations.py
import evetypes
import localization
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.item import GetItemEntriesByMetaGroup
from eve.client.script.ui.control.eveScroll import Scroll
from eve.common.lib import appConst as const

class PanelVariations(Container):

    def ApplyAttributes(self, attributes):
        super(PanelVariations, self).ApplyAttributes(attributes)
        self.typeID = attributes.typeID

    def Load(self):
        self.Flush()
        buttonCont = Container(parent=self, align=uiconst.TOBOTTOM, height=24)
        Button(parent=buttonCont, align=uiconst.CENTER, label=localization.GetByLabel('UI/Compare/CompareButton'), func=self.CompareTypes, args=())
        scroll = Scroll(parent=self, padding=const.defaultPadding)
        variants = evetypes.GetVariations(self.typeID)
        entries = GetItemEntriesByMetaGroup(variants)
        scroll.Load(contentList=entries)

    def CompareTypes(self):
        from eve.client.script.ui.shared.neocom.compare import TypeCompare
        wnd = TypeCompare.GetIfOpen()
        if wnd:
            wnd.AddVariantsOf(self.typeID)
        else:
            TypeCompare.Open(typeID=self.typeID)
