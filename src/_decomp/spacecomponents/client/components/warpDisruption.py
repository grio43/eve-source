#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\warpDisruption.py
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from spacecomponents.common.components.component import Component
from carbon.common.script.util.format import FmtDist
from spacecomponents.client.display import EntryData, RANGE_ICON

class WarpDisruption(Component):

    @staticmethod
    def GetAttributeInfo(typeID, attributes, instance, localization):
        attributeEntries = [EntryData(Header, localization.GetByLabel('UI/Inflight/SpaceComponents/WarpDisruption/InfoAttributesHeader')), EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/WarpDisruption/WarpDisruptionRangeLabel'), FmtDist(attributes.warpDisruptionRange), iconID=RANGE_ICON)]
        return attributeEntries
