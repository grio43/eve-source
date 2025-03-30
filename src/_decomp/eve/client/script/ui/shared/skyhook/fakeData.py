#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\skyhook\fakeData.py
import uthread2

class FakeColonyData(object):

    def __init__(self, reagentTypeID, power, worforce, active, harvested, matured):
        self.reagentTypeID = reagentTypeID
        self.power = power
        self.worforce = worforce
        self.active = active
        self.harvested = harvested
        self.matured = matured


class FakeData(object):
    colonyByRemainder = {0: FakeColonyData(reagentTypeID=None, power=None, worforce=50, active=True, harvested=None, matured=None),
     1: FakeColonyData(reagentTypeID=81144, power=None, worforce=None, active=True, harvested=500, matured=100),
     2: FakeColonyData(reagentTypeID=None, power=200, worforce=None, active=True, harvested=None, matured=None)}
    colonyByPlanetID = {40030269: FakeColonyData(reagentTypeID=81144, power=None, worforce=None, active=True, harvested=500, matured=100)}

    def __init__(self, doDelay = False):
        self._doDelay = doDelay

    def _GetColonyInfo(self, planetID):
        if self._doDelay:
            import random
            delay = random.random() * 3
            uthread2.Sleep(delay)
        if planetID in self.colonyByPlanetID:
            return self.colonyByPlanetID[planetID]
        return self.colonyByRemainder[planetID % 3]

    def GetPlanetReagentType(self, planetID):
        return self._GetColonyInfo(planetID).reagentTypeID

    def GetPlanetPowerProduction(self, planetID):
        return self._GetColonyInfo(planetID).power

    def GetPlanetWorkforceProduction(self, planetID):
        return self._GetColonyInfo(planetID).worforce

    def IsProductionActiveAtSkyhook(self, planetID):
        return self._GetColonyInfo(planetID).active

    def StartProductionAtSkyhook(self, planetID):
        print 'Fake StartProductionAtSkyhook'

    def StopProductionAtSkyhook(self, planetID):
        print 'Fake StopProductionAtSkyhook'

    def GetReagentsInSkyhookNow(self, planetID):
        colonyInfo = self._GetColonyInfo(planetID)
        return (colonyInfo.harvested, colonyInfo.matured)
