#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\decloakEmitter.py
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from spacecomponents.client.display import EntryData, TIMER_ICON, DICE_ICON
from spacecomponents.common.componentConst import DECLOAK_EMITTER
from spacecomponents.common.components.component import Component
from carbon.common.lib.const import SEC

class DecloakEmitter(Component):

    @staticmethod
    def GetAttributeInfo(typeID, attributes, instance, localization):
        attributeEntries = [EntryData(Header, localization.GetByLabel('UI/Inflight/SpaceComponents/DecloakEmitter/InfoAttributesHeader')), EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/DecloakEmitter/PingIntervalLabel'), localization.GetByLabel('UI/Inflight/SpaceComponents/DecloakEmitter/PingIntervalValue', pingInterval=long(attributes.interval * SEC)), iconID=TIMER_ICON), EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/DecloakEmitter/DecloakChanceLabel'), localization.GetByLabel('UI/Common/Formatting/PercentageDecimal', percentage=attributes.decloakProbability * 100), iconID=DICE_ICON)]
        return attributeEntries


def GetPingIntervalForItem(ballpark, itemID):
    component = ballpark.componentRegistry.GetComponentForItem(itemID, DECLOAK_EMITTER)
    return component.attributes.interval
