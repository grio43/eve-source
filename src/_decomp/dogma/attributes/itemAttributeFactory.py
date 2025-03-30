#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\attributes\itemAttributeFactory.py
from dogma.const import attributeSkillLevel, attributeHeatHi, attributeHeatLow, attributeHeatMed, attributeSecurityModifier, attributeNextActivationTime
import weakref
from dogma.attributes import Attribute, SecurityModifierAttribute, StackingNurfedAttribute, HeatAttribute, ChargedAttribute, SkillLevelAttribute, TiDiSensitiveAttribute
from dogma.data import get_attribute
from dogma.data import get_charge_recharge_time_attributes_by_id
from dogma.identity import get_safe_dogma_identity

class NewItemAttributeFactory:

    def __init__(self, item, dogmaLocation, baseAttributes):
        self.dogmaLocation = dogmaLocation
        self.attributes = baseAttributes
        self.item = weakref.proxy(item)

    def GetAttributeInstance(self, attrID):
        attrID = get_safe_dogma_identity(attrID)
        staticAttr = get_attribute(attrID)
        baseValue = None
        if self.attributes and attrID in self.attributes:
            baseValue = self.attributes[attrID]
        if attrID == attributeSkillLevel:
            return SkillLevelAttribute(attrID, baseValue, self.item, self.dogmaLocation, staticAttr)
        elif attrID in get_charge_recharge_time_attributes_by_id():
            return ChargedAttribute(attrID, baseValue, self.item, self.dogmaLocation, staticAttr)
        elif attrID in [attributeHeatHi, attributeHeatMed, attributeHeatLow]:
            return HeatAttribute(attrID, baseValue, self.item, self.dogmaLocation, staticAttr)
        elif not staticAttr.stackable:
            return StackingNurfedAttribute(attrID, baseValue, self.item, self.dogmaLocation, staticAttr)
        elif attrID == attributeSecurityModifier:
            return SecurityModifierAttribute(attrID, self.item, self.dogmaLocation, staticAttr)
        elif attrID == attributeNextActivationTime:
            return TiDiSensitiveAttribute(attrID, baseValue, self.item, self.dogmaLocation, staticAttr)
        else:
            return Attribute(attrID, baseValue, self.item, self.dogmaLocation, staticAttr)
