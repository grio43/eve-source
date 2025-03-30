#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelTraits.py
from carbonui.control.scrollContainer import ScrollContainer
from eve.client.script.ui.shared.traits import HasTraits, TraitsContainer

class PanelTraits(ScrollContainer):
    default_name = 'PanelTraits'
    default_padLeft = 4
    default_padTop = 4
    default_padRight = 4
    default_padBottom = 4

    def ApplyAttributes(self, attributes):
        ScrollContainer.ApplyAttributes(self, attributes)
        self.initialized = False
        self.typeID = attributes.typeID

    def Load(self):
        if self.initialized:
            return
        self.initialized = True
        TraitsContainer(parent=self, typeID=self.typeID, padding=7, traitAttributeIcons=True)

    @classmethod
    def TraitsVisible(cls, typeID):
        return HasTraits(typeID)
