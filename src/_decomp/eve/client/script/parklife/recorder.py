#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\recorder.py
import blue
from carbon.common.script.sys.service import Service

class EventRecorder(Service):
    __guid__ = 'svc.recorder'
    __exportedcalls__ = {'StartStateCapture': [],
     'EndStateCapture': []}
    __notifyevents__ = ['DoBallsAdded', 'DoDestinyUpdate', 'DoDestinyUpdates']
    __dependencies__ = []

    def __init__(self):
        super(EventRecorder, self).__init__()
        self.captureBallAttributes = ['name',
         'radius',
         'maxVelocity',
         'x',
         'y',
         'z',
         'vx',
         'vy',
         'vz',
         'gotoX',
         'gotoY',
         'gotoZ',
         'Agility',
         'mode',
         'followId',
         'followRange',
         'mass',
         'maxVelocity',
         'isFree',
         'isGlobal',
         'isMassive',
         'isInteractive',
         'speedFraction']
        self.captureSessionAttributes = ['userid',
         'shipid',
         'solarsystemid',
         'solarsystemid2']
        self.initialState = None
        self.capturingState = False
        self.capturedStateUpdates = []

    def CaptureInitialState(self):
        michelle = sm.StartService('michelle')
        bp = michelle.GetBallpark()
        globalState = {}
        itemState = {}
        for ballID in bp.balls:
            slimItem = bp.GetInvItem(ballID)
            ball = bp.GetBall(ballID)
            itemState[ballID] = ballState = {}
            if slimItem is not None:
                for key, val in slimItem.__dict__.iteritems():
                    ballState[key] = val

            for a in self.captureBallAttributes:
                ballState[a] = getattr(ball, a, None)

        globalState['egoBall'] = bp.ego
        globalState['shipid'] = session.shipid
        globalState['solarsystemid'] = session.solarsystemid
        globalState['solarsystemid2'] = session.solarsystemid2
        globalState['initialTime'] = blue.os.GetSimTime()
        globalState['regionid'] = session.regionid
        self.initialState = (globalState, itemState)

    def StartStateCapture(self):
        self.capturingState = True
        self.capturedStateUpdates = []
        self.CaptureInitialState()

    def EndStateCapture(self, filepath):
        self.capturingState = False
        import cPickle
        print 'Writing State out'
        f = open(filepath, 'wb')
        cPickle.dump((self.initialState[0], self.initialState[1], self.capturedStateUpdates), f)
        f.close()

    def DoDestinyUpdate(self, state, waitForBubble, dogmaMessages = [], doDump = True):
        if self.capturingState:
            filteredStates = []
            for stamp, (funcName, args) in state:
                if funcName != 'AddBalls':
                    filteredStates.append((stamp, (funcName, args)))

            self.capturedStateUpdates.append((blue.os.GetSimTime(), filteredStates))

    def DoDestinyUpdates(self, updates):
        pass

    def DoBallsAdded(self, lst):
        stateUpdate = []
        for ball, slimItem in lst:
            ballState = {}
            if slimItem is not None:
                for key, val in slimItem.__dict__.iteritems():
                    ballState[key] = val

            for a in self.captureBallAttributes:
                ballState[a] = getattr(ball, a, None)

            stateUpdate.append((ball.id, ballState))

        self.capturedStateUpdates.append((blue.os.GetSimTime(), [(0, ('DoBallsAdded', stateUpdate))]))
