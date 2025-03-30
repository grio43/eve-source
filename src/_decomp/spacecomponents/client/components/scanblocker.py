#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\scanblocker.py
from carbon.common.script.util.format import FmtDist
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from spacecomponents.client.display import EntryData, RANGE_ICON
from spacecomponents.common.components.component import Component

class ScanBlocker(Component):

    @staticmethod
    def GetAttributeInfo(typeID, attributes, instance, localization):
        attributeEntries = [EntryData(Header, localization.GetByLabel('UI/Inflight/SpaceComponents/ScanBlocker/InfoAttributesHeader')), EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/ScanBlocker/RangeLabel'), FmtDist(attributes.range), iconID=RANGE_ICON)]
        return attributeEntries
