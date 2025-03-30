#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\tacticalNavigation\ui\pendingMove.py
import blue
from tacticalNavigation.ballparkFunctions import GetBall
from tacticalNavigation.ui.util import CreateMovementConnector
import uthread2

class PendingMoveIndication:

    def __init__(self, ballID, globalPosition, navPointContainer, timeoutCallback):
        self.connector = None
        self.navPoint = None
        self._timeoutCallback = timeoutCallback
        self.ballID = ballID
        self.globalPosition = globalPosition
        self.navPointContainer = navPointContainer

    def _DelayedDestroy(self):

        def _inner():
            _delay = 3000
            blue.synchro.SleepSim(_delay)
            self.Destroy()

        uthread2.start_tasklet(_inner)

    def Show(self):
        ball = GetBall(self.ballID)
        if ball is not None and ball.ballpark is not None:
            self.navPoint = self.navPointContainer.GetOrCreatePoint(self.globalPosition)
            connector = CreateMovementConnector(ball, self.navPoint.GetNavBall())
            self.connector = connector
            connector.lineConnector.isAnimated = True
            self._DelayedDestroy()

    def Destroy(self):
        if self.navPoint is None:
            return
        self.connector.Destroy()
        self.navPointContainer.Dereference(self.navPoint)
        self.navPointContainer = None
        self.navPoint = None
        self.connector = None
        self._timeoutCallback(self.ballID)
