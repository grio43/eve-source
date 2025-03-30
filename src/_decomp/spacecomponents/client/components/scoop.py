#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\scoop.py
from carbon.common.script.util.format import FmtDist
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from eve.common.lib.appConst import maxCargoContainerTransferDistance
from spacecomponents.client.display import EntryData, RANGE_ICON
from spacecomponents.common.components.component import Component

class Scoop(Component):

    @staticmethod
    def GetAttributeInfo(typeID, attributes, instance, localization):
        attributeEntries = [EntryData(Header, localization.GetByLabel('UI/Inflight/SpaceComponents/Scoop/InfoAttributesHeader')), EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Scoop/RangeLabel'), FmtDist(getattr(attributes, 'range', maxCargoContainerTransferDistance)), iconID=RANGE_ICON)]
        return attributeEntries
