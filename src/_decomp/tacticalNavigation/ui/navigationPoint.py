#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\tacticalNavigation\ui\navigationPoint.py
from tacticalNavigation.navigationPoint import NavigationPoint

class NavigationPointContainer:

    def __init__(self, navPointCallback):
        self.positionToNavPoint = {}
        self.tacticalPoints = []
        self.navPointCallback = navPointCallback

    def GetOrCreatePoint(self, globalPosition):
        if globalPosition in self.positionToNavPoint:
            navPoint = self.positionToNavPoint[globalPosition]
        else:
            navPoint = NavigationPoint(globalPosition)
            self.positionToNavPoint[globalPosition] = navPoint
        navPoint.AddReferrer()
        return navPoint

    def ConfirmNavPoint(self, ballID, navPoint):
        self.navPointCallback(ballID, navPoint.globalPosition)
        if navPoint in self.tacticalPoints:
            return
        tactical = sm.GetService('tactical').GetOverlay()
        tactical.RegisterNavBall(navPoint.GetNavBall())

    def Dereference(self, navPoint):
        navPoint.RemoveReferrer()
        if not navPoint.HasReferrers():
            tactical = sm.GetService('tactical').GetOverlay()
            tactical.UnregisterNavBall(navPoint.GetNavBall())
            navPoint.Destroy()
            del self.positionToNavPoint[navPoint.globalPosition]
