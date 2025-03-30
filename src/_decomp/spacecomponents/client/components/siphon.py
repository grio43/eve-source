#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\siphon.py
import evetypes
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from spacecomponents.client.display import EntryData
from spacecomponents.common.components.component import Component

class Siphon(Component):

    @staticmethod
    def GetAttributeInfo(typeID, attributes, instance, localization):
        attributeEntries = [EntryData(Header, localization.GetByLabel('UI/Inflight/SpaceComponents/Siphon/SiphoningMaterials'))]
        materialNames = []
        for materialID in attributes.materials:
            materialNames.append((evetypes.GetName(materialID), materialID))

        for material in sorted(materialNames):
            attributeEntries.append(EntryData(LabelTextSides, material[0], '', evetypes.GetIconID(material[1]), material[1]))

        return attributeEntries
