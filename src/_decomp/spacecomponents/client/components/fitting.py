#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\fitting.py
from carbon.common.script.util.format import FmtDist
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from spacecomponents.client.display import EntryData, RANGE_ICON
from spacecomponents.common.components.component import Component

class Fitting(Component):

    def __init__(self, *args):
        Component.__init__(self, *args)
        self.fittingRange = self.attributes.range

    @staticmethod
    def GetAttributeInfo(typeID, attributes, instance, localization):
        attributeEntries = [EntryData(Header, localization.GetByLabel('UI/Inflight/SpaceComponents/Fitting/InfoAttributesHeader')), EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Fitting/DistanceLabel'), FmtDist(attributes.range), iconID=RANGE_ICON)]
        return attributeEntries
