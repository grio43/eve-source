#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelDescription.py
import evetypes
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.common.lib import appConst as const
import carbonui.const as uiconst

class PanelDescription(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.infoType = attributes.infoType
        self.itemID = attributes.itemID
        self.typeID = attributes.typeID
        self.initialized = False
        self.edit = EditPlainText(parent=self, padding=const.defaultPadding, align=uiconst.TOALL, showattributepanel=False, readonly=True)

    def Load(self):
        if self.initialized:
            return
        self.initialized = True
        text = self.GetDescription()
        self.edit.SetValue(text, scrolltotop=1)

    def GetDescription(self):
        if evetypes.GetCategoryID(self.typeID) == const.categoryStructure:
            text = sm.RemoteSvc('structureDirectory').GetStructureDescription(self.itemID)
            return text
        return ''
