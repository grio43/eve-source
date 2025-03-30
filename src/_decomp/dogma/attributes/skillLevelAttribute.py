#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\attributes\skillLevelAttribute.py
from dogma.dogmaLogging import LogTraceback
from dogma.attributes import Attribute
from characterskills import GetSkillLevelRaw
from dogma.const import attributeSkillTimeConstant, attributeSkillPoints
import weakref

class SkillLevelAttribute(Attribute):

    def __init__(self, attribID, baseValue, dogmaItem, dogmaLM, staticAttr):
        super(SkillLevelAttribute, self).__init__(attribID, baseValue, dogmaItem, dogmaLM, staticAttr)
        self.skillTimeConstant = dogmaLM.dogmaStaticMgr.GetTypeAttribute2(dogmaItem.invItem.typeID, attributeSkillTimeConstant)
        self.skillPointAttribute = weakref.ref(self.item.attributes[attributeSkillPoints])
        self.skillPointAttribute().AddNonModifyingDependant(self)

    def Update(self):
        prevValue = self.currentValue
        if self.skillPointAttribute() is not None:
            self.currentValue = GetSkillLevelRaw(self.skillPointAttribute().GetValue(), self.skillTimeConstant)
        self.dirty = False
        self._PerformCallbacksIfValueChanged(prevValue)

    def AddIncomingModifier(self, op, attribute):
        LogTraceback('Cannot modify a skill level!')

    def RemoveIncomingModifier(self, op, attribute):
        LogTraceback('Cannot modify a skill level!')
