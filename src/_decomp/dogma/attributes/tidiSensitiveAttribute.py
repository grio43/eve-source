#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\attributes\tidiSensitiveAttribute.py
import gametime
from dogma.attributes import Attribute

class TiDiSensitiveAttribute(Attribute):

    def GetPersistData(self):
        if self.baseValue != self.typeValue:
            return (gametime.GetWallclockTimeNow(), self.baseValue - gametime.GetSimTime())

    def SetBaseValue(self, newBaseValue):
        if isinstance(newBaseValue, tuple):
            timeOfPacking, remainingTime = newBaseValue
            transitTime = gametime.GetWallclockTimeNow() - timeOfPacking
            remainingTime -= transitTime
            newBaseValue = gametime.GetSimTime() + remainingTime
        if self.baseValue != newBaseValue:
            self.baseValue = newBaseValue
            self.MarkDirty()
