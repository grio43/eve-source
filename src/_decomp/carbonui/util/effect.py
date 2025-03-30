#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\util\effect.py
import logging
import math
import blue
import mathext
import uthread
log = logging.getLogger(__name__)

class UIEffects:

    def StopBlink(self, sprite):
        if not getattr(self, 'blink_running', False):
            return
        if not hasattr(self, 'remPending'):
            self.remPending = []
        self.remPending.append(id(sprite))

    def BlinkSpriteA(self, sprite, a, time = 1000.0, maxCount = 10, passColor = 1, minA = 0.0, timeFunc = blue.os.GetWallclockTime):
        if not hasattr(self, 'blinksA'):
            self.blinksA = {}
        key = id(sprite)
        self.blinksA[key] = (sprite,
         a,
         minA,
         time,
         maxCount,
         passColor,
         timeFunc)
        if key in getattr(self, 'remPending', []):
            self.remPending.remove(key)
        if not getattr(self, 'blink_running', False):
            self.blink_running = True
            uthread.new(self._BlinkThread).context = 'UIObject::effect._BlinkThread'

    def BlinkSpriteRGB(self, sprite, r, g, b, time = 1000.0, maxCount = 10, passColor = 1, timeFunc = blue.os.GetWallclockTime):
        if not hasattr(self, 'blinksRGB'):
            self.blinksRGB = {}
        key = id(sprite)
        self.blinksRGB[key] = (sprite,
         r,
         g,
         b,
         time,
         maxCount,
         passColor,
         timeFunc)
        if key in getattr(self, 'remPending', []):
            self.remPending.remove(key)
        if not getattr(self, 'blink_running', False):
            self.blink_running = True
            uthread.new(self._BlinkThread).context = 'UIObject::effect._BlinkThread'

    def _BlinkThread(self):
        startTimes = {}
        countsA = {}
        countsRGB = {}
        if not hasattr(self, 'blinksA'):
            self.blinksA = {}
        if not hasattr(self, 'blinksRGB'):
            self.blinksRGB = {}
        try:
            while True:
                if not self:
                    return
                rem = []
                for key, each in self.blinksA.iteritems():
                    sprite, a, minA, time, maxCount, passColor, timeFunc = each
                    if not sprite or sprite.destroyed:
                        rem.append(key)
                        continue
                    if passColor and getattr(sprite, 'tripass', None):
                        color = sprite.tripass.textureStage0.customColor
                    else:
                        color = sprite.color
                    if key in getattr(self, 'remPending', []):
                        rem.append(key)
                        color.a = minA or a
                        continue
                    now = timeFunc()
                    try:
                        diff = blue.os.TimeDiffInMs(now, startTimes[timeFunc])
                    except KeyError:
                        startTimes[timeFunc] = now
                        diff = 0

                    pos = diff % time
                    if pos < time / 2.0:
                        ndt = min(pos / (time / 2.0), 1.0)
                        color.a = mathext.lerp(a, minA, ndt)
                    else:
                        ndt = min((pos - time / 2.0) / (time / 2.0), 1.0)
                        color.a = mathext.lerp(minA, a, ndt)
                    if key not in countsA:
                        countsA[key] = now
                    if maxCount and blue.os.TimeDiffInMs(countsA[key], now) / time > maxCount:
                        rem.append(key)
                        color.a = minA or a
                        if key in countsA:
                            del countsA[key]

                for each in rem:
                    if each in self.blinksA:
                        del self.blinksA[each]

                rem = []
                for key, each in self.blinksRGB.iteritems():
                    sprite, r, g, b, time, maxCount, passColor, timeFunc = each
                    if not sprite or sprite.destroyed:
                        rem.append(key)
                        continue
                    if passColor and getattr(sprite, 'tripass', None):
                        color = sprite.tripass.textureStage0.customColor
                    else:
                        color = sprite.color
                    if key in getattr(self, 'remPending', []):
                        rem.append(key)
                        color.r = r
                        color.g = g
                        color.b = b
                        continue
                    now = timeFunc()
                    try:
                        diff = blue.os.TimeDiffInMs(now, startTimes[timeFunc])
                    except KeyError:
                        startTimes[timeFunc] = now
                        diff = 0

                    pos = diff % time
                    if pos < time / 2.0:
                        ndt = min(pos / (time / 2.0), 1.0)
                        color.r = mathext.lerp(r, 0.0, ndt)
                        color.g = mathext.lerp(g, 0.0, ndt)
                        color.b = mathext.lerp(b, 0.0, ndt)
                    else:
                        ndt = min((pos - time / 2.0) / (time / 2.0), 1.0)
                        color.r = mathext.lerp(0.0, r, ndt)
                        color.g = mathext.lerp(0.0, g, ndt)
                        color.b = mathext.lerp(0.0, b, ndt)
                    if key not in countsRGB:
                        countsRGB[key] = now
                    if maxCount and blue.os.TimeDiffInMs(countsRGB[key], now) / time > maxCount:
                        rem.append(key)
                        color.r = r
                        color.g = g
                        color.b = b
                        if key in countsRGB:
                            del countsRGB[key]

                for each in rem:
                    if each in self.blinksRGB:
                        del self.blinksRGB[each]

                self.remPending = []
                if not len(self.blinksA) and not len(self.blinksRGB) or not self.blink_running:
                    self.blinksA = {}
                    self.blinksRGB = {}
                    self.blink_running = False
                    break
                blue.pyos.synchro.Yield()

        except Exception:
            self.blink_running = False
            log.exception()

    def MorphUIMassSpringDamper(self, item, attrname = None, newVal = 1.0, newthread = 1, float = 1, minVal = -10000000000.0, maxVal = 10000000000.0, dampRatio = 0.11, frequency = 20.0, initSpeed = 0.0, maxTime = 1.0, callback = None, initVal = None, timeFunc = blue.os.GetWallclockTime):
        if newthread:
            return uthread.new(self._MorphUIMassSpringDamper, item, attrname, newVal, newthread, float, minVal, maxVal, dampRatio, frequency, initSpeed, maxTime, callback, initVal, timeFunc)
        self._MorphUIMassSpringDamper(item, attrname, newVal, newthread, float, minVal, maxVal, dampRatio, frequency, initSpeed, maxTime, callback, initVal, timeFunc)

    def _MorphUIMassSpringDamper(self, item, attrname, newVal, newthread, float, minVal, maxVal, dampRatio, frequency, initSpeed, maxTime, callback, initVal = None, timeFunc = blue.os.GetWallclockTime):
        if initVal is None and attrname is not None:
            initVal = getattr(item, attrname)
        if initVal == newVal:
            initVal += 1e-05
        t0 = timeFunc()
        xn = newVal - initVal
        x0 = -xn
        w0 = frequency
        L = dampRatio
        if math.fabs(L) >= 1.0:
            L = 0.99
        wd = w0 * math.sqrt(1.0 - L ** 2)
        A = x0
        v0 = initSpeed
        B = (L * w0 * x0 + v0) / wd
        t = 0.0
        val = 0.0
        stopCount = 0
        while t < maxTime:
            t = blue.os.TimeDiffInMs(t0, timeFunc()) / 1000.0
            C = -L * w0 * t
            val = math.exp(C) * (A * math.cos(wd * t) + B * math.sin(wd * t)) + xn
            val = max(minVal - initVal, min(val, maxVal - initVal))
            if math.fabs(val + initVal - newVal) / math.fabs(initVal - newVal) < 0.02:
                stopCount += 1
            if stopCount >= 5:
                break
            setVal = val + initVal
            if not float:
                setVal = int(setVal)
            if attrname and item:
                setattr(item, attrname, setVal)
            if callback:
                callback(item, setVal)
            blue.pyos.synchro.Yield()
            if item and item.destroyed:
                break

        newVal = max(minVal, min(newVal, maxVal))
        if not float:
            newVal = int(newVal)
        if attrname and item:
            setattr(item, attrname, newVal)
        if callback:
            if item and item.destroyed:
                return
            callback(item, newVal)
