#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelMutatorUsedWith.py
from eve.client.script.ui.control.entries.item import GetItemEntriesByMetaGroup
from eve.client.script.ui.shared.info.panels.panelUsedWith import PanelUsedWith
import dynamicitemattributes
import evetypes

class PanelMutatorUsedWith(PanelUsedWith):

    def GetScrollList(self, data, *args):
        mutator = dynamicitemattributes.GetMutator(self.typeID)
        applicableTypes = set()
        for mapping in mutator.inputOutputMapping:
            publishedTypes = filter(evetypes.IsPublished, mapping.applicableTypes)
            applicableTypes.update(publishedTypes)

        return GetItemEntriesByMetaGroup(applicableTypes)
