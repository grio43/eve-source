#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\menucheckers\mapCheckers.py
from menucheckers import decorators
from menucheckers.baseCheckers import _BaseSessionWrappingChecker

@decorators.decorated_checker

class MapChecker(_BaseSessionWrappingChecker):

    def __init__(self, itemID, sessionInfo = None, serviceManager = None):
        super(MapChecker, self).__init__(sessionInfo, serviceManager)
        self.itemID = itemID

    def OfferSetDestination(self):
        return self.itemID not in (self.session.stationid, self.session.structureid)

    def OfferRemoveWaypoint(self):
        return self.itemID in self.sm.GetService('starmap').GetWaypoints()
