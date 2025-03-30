#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\items\notWantedDogmaItem.py
from dogma.items.baseDogmaItem import BaseDogmaItem
RESISTANCEMATRIX = {const.attributeShieldCharge: [0,
                               0,
                               0,
                               0],
 const.attributeArmorDamage: [0,
                              0,
                              0,
                              0],
 const.attributeDamage: [0,
                         0,
                         0,
                         0]}

class NotWantedDogmaItem(BaseDogmaItem):

    def CanAttributeBeModified(self):
        return False

    def GetResistanceMatrix(self):
        return RESISTANCEMATRIX
