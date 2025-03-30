#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\items\probeDogmaItem.py
from baseDogmaItem import BaseDogmaItem
from eve.common.script.sys.idCheckers import IsSolarSystem
from eveprefs import boot

class ProbeDogmaItem(BaseDogmaItem):

    def IsOwnerModifiable(self, locationID = None):
        if boot.role == 'client':
            return True
        if not locationID:
            locationID = self.locationID
        if IsSolarSystem(locationID):
            return True
        return False
