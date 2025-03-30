#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\tacticalNavigation\navigationPoint.py
from tacticalNavigation.ballparkFunctions import AddClientBall, RemoveClientBall
from tacticalNavigation.navigationBracket import NavigationPointBracket

class NavigationPoint:

    def __init__(self, globalPosition):
        self.globalPosition = globalPosition
        self.clientBall = AddClientBall(globalPosition)
        self.bracket = NavigationPointBracket.Create(self.clientBall)
        self.refCount = 0

    def GetNavBall(self):
        return self.clientBall

    def AddReferrer(self):
        self.refCount += 1

    def RemoveReferrer(self):
        self.refCount -= 1

    def HasReferrers(self):
        return self.refCount > 0

    def Destroy(self):
        self.bracket.Close()
        RemoveClientBall(self.clientBall)
