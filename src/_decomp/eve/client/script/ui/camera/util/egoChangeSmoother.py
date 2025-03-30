#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\util\egoChangeSmoother.py
import blue
import geo2
import trinity

class EgoChangeSmoother(object):
    __notifyevents__ = ['ProcessSessionChange', 'OnBallAdded']

    def __init__(self, timelimit = 10.0):
        self.timelimit = timelimit
        self._missingBalls = None
        self._offsets = {}
        self._easeCurve = trinity.Tr2CurveScalar()
        self._easeCurve.AddKey(0, 1, trinity.Tr2CurveInterpolation.HERMITE, 0, 0)
        self._easeCurve.AddKey(1, 0, trinity.Tr2CurveInterpolation.HERMITE, 0, 0)
        self._lastEgo = session.structureid or session.shipid
        sm.RegisterNotify(self)

    def ProcessSessionChange(self, isRemote, sess, change):
        if 'shipid' in change:
            self._UpdateEgoOffset(change['shipid'][1])
        if 'structureid' in change:
            self._UpdateEgoOffset(change['structureid'][1])

    def OnBallAdded(self, slimItem):
        if self._missingBalls is not None and slimItem.itemID in self._missingBalls:
            self._UpdateOffset(*self._missingBalls)

    def _UpdateOffset(self, oldEgo, newEgo):
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is not None:
            old = ballpark.GetBall(oldEgo)
            new = ballpark.GetBall(newEgo)
            if old and new:
                timestamp = blue.os.GetSimTime()
                offset = (old.x - new.x, old.y - new.y, old.z - new.z)
                self._offsets[self._lastEgo] = (timestamp, offset)
                self._missingBalls = None
            else:
                self._missingBalls = (oldEgo, newEgo)

    def _UpdateEgoOffset(self, newEgo):
        if self._lastEgo != newEgo:
            if self._lastEgo:
                self._UpdateOffset(self._lastEgo, newEgo)
            self._lastEgo = newEgo

    def _GetScaledOffset(self, easeTime, currTime, timestamp, offset):
        timeSinceOffset = blue.os.TimeDiffInMs(timestamp, currTime) / 1000.0
        return geo2.Vec3Scale(offset, self._easeCurve.GetValueAt(timeSinceOffset / easeTime))

    def GetTotalOffset(self, easeTime):
        if easeTime <= 0:
            raise RuntimeError('The easeTime must be more than 0. {} given.'.format(easeTime))
        if easeTime > self.timelimit:
            raise RuntimeError('The easeTime ({}) supplied must be less than the timelimit ({}).'.format(easeTime, self.timelimit))
        total = (0, 0, 0)
        if not self._offsets:
            return total
        currTime = blue.os.GetSimTime()
        updatedOffsets = {}
        for key, (timestamp, offset) in self._offsets.iteritems():
            scaledOffset = self._GetScaledOffset(easeTime, currTime, timestamp, offset)
            total = geo2.Vec3Add(total, scaledOffset)
            if any((abs(x) > 0.001 for x in scaledOffset)):
                updatedOffsets[key] = (timestamp, offset)

        self._offsets = updatedOffsets
        return total
