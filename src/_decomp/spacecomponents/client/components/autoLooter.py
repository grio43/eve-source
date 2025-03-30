#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\autoLooter.py
from carbon.common.lib.const import SEC
from carbon.common.script.util.format import FmtDist, FmtTimeInterval
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from eve.common.lib.appConst import maxCargoContainerTransferDistance
from spacecomponents.client.display import EntryData, RANGE_ICON, CYCLE_TIME_ICON
from spacecomponents.common.components.component import Component

class AutoLooter(Component):

    @staticmethod
    def GetAttributeInfo(typeID, attributes, instance, localization):
        attributeEntries = [EntryData(Header, localization.GetByLabel('UI/Inflight/SpaceComponents/AutoLooter/InfoAttributesHeader')), EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/AutoLooter/RangeLabel'), FmtDist(getattr(attributes, 'range', maxCargoContainerTransferDistance)), iconID=RANGE_ICON), EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/AutoLooter/CycleTimeSecondsLabel'), FmtTimeInterval(long(attributes.cycleTimeSeconds * SEC), breakAt='sec'), iconID=CYCLE_TIME_ICON)]
        return attributeEntries
