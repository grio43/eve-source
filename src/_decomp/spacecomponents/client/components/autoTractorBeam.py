#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\autoTractorBeam.py
from carbon.common.lib.const import SEC
from carbon.common.script.util.format import FmtDist, FmtTimeInterval
from dogma import const as dogmaconst
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from spacecomponents.client.display import EntryData, DogmaEntryData, CYCLE_TIME_ICON, RANGE_ICON
from spacecomponents.client.display import GetDogmaAttributeAndValue
from spacecomponents.common.components.component import Component

class AutoTractorBeam(Component):

    @staticmethod
    def GetAttributeInfo(typeID, attributes, instance, localization):
        maxTractorVelocity = GetDogmaAttributeAndValue(typeID, dogmaconst.attributeMaxTractorVelocity)
        attributeEntries = [EntryData(Header, localization.GetByLabel('UI/Inflight/SpaceComponents/AutoTractorBeam/InfoAttributesHeader')),
         EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/AutoTractorBeam/MaxRangeLabel'), FmtDist(attributes.maxRange), iconID=RANGE_ICON),
         EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/AutoTractorBeam/CycleTimeSecondsLabel'), FmtTimeInterval(attributes.cycleTimeSeconds * SEC, breakAt='sec'), iconID=CYCLE_TIME_ICON),
         DogmaEntryData(LabelTextSides, maxTractorVelocity)]
        return attributeEntries

    @staticmethod
    def GetSuppressedDogmaAttributeIDs():
        return [dogmaconst.attributeMaxTractorVelocity, dogmaconst.attributeDuration]
