#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\tidiIndicator.py
import math
from collections import Iterable
import blue
import eveui
import localization
import mathext
import uthread
from carbon.common.script.util import logUtil as log
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
labXfromRGB = (0.4124, 0.3576, 0.1805)
labYfromRGB = (0.2126, 0.7152, 0.0722)
labZfromRGB = (0.0193, 0.1192, 0.9505)
labRfromXYZ = (3.2406, -1.5372, -0.4986)
labGfromXYZ = (-0.9689, 1.8758, 0.0415)
labBfromXYZ = (0.0557, -0.204, 1.057)

def GammaCorrect(color):
    if color > 0.04045:
        return ((color + 0.055) / 1.055) ** 2.4
    else:
        return color / 12.92


def UnGammaCorrect(color):
    if color > 0.0031308:
        return 1.055 * color ** (1 / 2.4) - 0.055
    else:
        return 12.92 * color


def RGB2Lab(rgbColor):
    rgbColor = map(GammaCorrect, rgbColor)
    rgbColor = map(lambda x: x * 100, rgbColor)
    x = sum(map(lambda x: x[0] * x[1], zip(rgbColor, labXfromRGB)))
    y = sum(map(lambda x: x[0] * x[1], zip(rgbColor, labYfromRGB)))
    z = sum(map(lambda x: x[0] * x[1], zip(rgbColor, labZfromRGB)))
    x /= 95.047
    y /= 100
    z /= 108.883

    def Labify(x):
        if x > 0.008856:
            return x ** (1 / 3.0)
        else:
            return x * 7.787 + 16 / 116.0

    x, y, z = map(Labify, (x, y, z))
    L = y * 116.0 - 16.0
    a = 500.0 * (x - y)
    b = 200.0 * (y - z)
    return (L, a, b)


def Lab2RGB(labColor):
    L, a, b = labColor
    y = (L + 16.0) / 116.0
    x = y + a * 0.002
    z = y - b * 0.005
    x, y, z = map(lambda x: x ** 3, (x, y, z))

    def what(x):
        if x > 0.008856:
            return x
        else:
            return (x - 16 / 166) / 7.787

    x, y, z = map(what, (x, y, z))
    x *= 95.047
    y *= 100
    z *= 108.883
    x, y, z = map(lambda x: x / 100, (x, y, z))
    r = sum(map(lambda x: x[0] * x[1], zip((x, y, z), labRfromXYZ)))
    g = sum(map(lambda x: x[0] * x[1], zip((x, y, z), labGfromXYZ)))
    b = sum(map(lambda x: x[0] * x[1], zip((x, y, z), labBfromXYZ)))
    return map(UnGammaCorrect, (r, g, b))


rgbLerpValues = [(0, (1, 0, 0)),
 (0.25, (0.94, 0.35, 0.14)),
 (0.5, (1, 1, 0)),
 (0.9, (0, 1, 0)),
 (1, (1, 1, 1))]
labLerpValues = map(lambda x: (x[0], RGB2Lab(x[1])), rgbLerpValues)

def LerpHelper(lerpVals, value, errorValue):
    for i in xrange(len(lerpVals)):
        if value == lerpVals[i][0]:
            return lerpVals[i][1]
        if value > lerpVals[i][0] and value < lerpVals[i + 1][0]:
            lerpPct = (lerpVals[i][0] - value) / float(lerpVals[i][0] - lerpVals[i + 1][0])
            if isinstance(lerpVals[i][1], Iterable):
                return map(lambda x: mathext.lerp(x[0], x[1], lerpPct), zip(lerpVals[i][1], lerpVals[i + 1][1]))
            else:
                return mathext.lerp(lerpVals[i][1], lerpVals[i + 1][1], lerpPct)

    log.LogTraceback('TiDi LerpHelper ran off the edge')
    return errorValue


class TiDiIndicator(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.state = uiconst.UI_HIDDEN
        self.initialized = False
        size = 24
        self.ramps = Container(parent=self, name='ramps', pos=(0,
         0,
         size,
         size), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        leftRampCont = Container(parent=self.ramps, name='leftRampCont', pos=(0,
         0,
         size / 2,
         size), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, clipChildren=True)
        self.leftRamp = Transform(parent=leftRampCont, name='leftRamp', pos=(0,
         0,
         size,
         size), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        Sprite(parent=self.leftRamp, name='rampSprite', pos=(0,
         0,
         size / 2,
         size), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/TiDiIndicator/left.png', color=(0.0, 0.0, 0.0, 0.55))
        rightRampCont = Container(parent=self.ramps, name='rightRampCont', pos=(0,
         0,
         size / 2,
         size), align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, clipChildren=True)
        self.rightRamp = Transform(parent=rightRampCont, name='rightRamp', pos=(-size / 2,
         0,
         size,
         size), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        Sprite(parent=self.rightRamp, name='rampSprite', pos=(size / 2,
         0,
         size / 2,
         size), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/TiDiIndicator/right.png', color=(0.0, 0.0, 0.0, 0.55))
        self.coloredPie = Sprite(parent=self, name='tidiColoredPie', pos=(0,
         0,
         size,
         size), texturePath='res:/UI/Texture/classes/TiDiIndicator/circle.png', color=(0, 1, 0, 1), state=uiconst.UI_DISABLED)
        background = Sprite(parent=self, name='tidiBackground', pos=(0,
         0,
         size,
         size), texturePath='res:/UI/Texture/classes/TiDiIndicator/shadow.png', color=(0.2, 0.2, 0.2, 0.5), state=uiconst.UI_DISABLED)
        uthread.new(self.Animate)

    def StartupAnim(self):
        fadeLerps = ((0, 0), (750, 1), (1500, 1))
        spinLerps = ((0, 1),
         (250, 1),
         (600, 0),
         (950, 1),
         (1500, 1))
        startTime = blue.os.GetWallclockTime()
        elapsedTimeMS = 0
        while self and not self.destroyed and elapsedTimeMS < 1500:
            self.opacity = LerpHelper(fadeLerps, elapsedTimeMS, 0)
            spin = LerpHelper(spinLerps, elapsedTimeMS, 0)
            leftRamp = min(1.0, max(0.0, spin * 2))
            rightRamp = min(1.0, max(0.0, spin * 2 - 1.0))
            self.leftRamp.SetRotation(math.pi + math.pi * leftRamp)
            self.rightRamp.SetRotation(math.pi + math.pi * rightRamp)
            color = LerpHelper(labLerpValues, spin, (1, 1, 1))
            self.coloredPie.SetRGBA(*(Lab2RGB(color) + [0.65]))
            eveui.wait_for_next_frame()
            elapsedTimeMS = blue.os.TimeDiffInMs(startTime, blue.os.GetWallclockTime())

    def ShutdownAnim(self):
        self.leftRamp.SetRotation(0)
        self.rightRamp.SetRotation(0)
        fadeLerps = ((0, 1), (750, 0))
        startTime = blue.os.GetWallclockTime()
        elapsedTimeMS = 0
        while self and not self.destroyed and elapsedTimeMS < 750:
            self.opacity = LerpHelper(fadeLerps, elapsedTimeMS, 0)
            eveui.wait_for_next_frame()
            elapsedTimeMS = blue.os.TimeDiffInMs(startTime, blue.os.GetWallclockTime())

        self.state = uiconst.UI_HIDDEN
        self.opacity = 0

    def Animate(self):
        if not self or self.destroyed:
            return
        prevFactor = 1
        while self and not self.destroyed:
            curFactor = blue.os.desiredSimDilation
            if (not self.initialized or curFactor != prevFactor) and (curFactor < 0.98 or prevFactor < 0.98):
                if not self.initialized:
                    prevFactor = curFactor
                self.state = uiconst.UI_NORMAL
                self.hint = localization.GetByLabel('UI/Neocom/TidiTooltip', tidiAmount=int(curFactor * 100))
                if self.opacity < 1:
                    self.StartupAnim()
                    continue

                def RotateAndColor(animFactor):
                    animFactor = min(max(animFactor, 0), 1)
                    leftRamp = min(1.0, max(0.0, animFactor * 2))
                    rightRamp = min(1.0, max(0.0, animFactor * 2 - 1.0))
                    self.leftRamp.SetRotation(math.pi + math.pi * leftRamp)
                    self.rightRamp.SetRotation(math.pi + math.pi * rightRamp)
                    color = LerpHelper(labLerpValues, animFactor, (0, 0, 0))
                    self.coloredPie.SetRGBA(*(Lab2RGB(color) + [0.65]))

                startTime = blue.os.GetWallclockTime()
                elapsedTimeMS = 0
                animDurationMS = 500
                while self and not self.destroyed and elapsedTimeMS < animDurationMS:
                    portionDone = elapsedTimeMS / float(animDurationMS)
                    animFactor = mathext.lerp(prevFactor, curFactor, portionDone)
                    RotateAndColor(animFactor)
                    eveui.wait_for_next_frame()
                    elapsedTimeMS = blue.os.TimeDiffInMs(startTime, blue.os.GetWallclockTime())

                RotateAndColor(curFactor)
                prevFactor = curFactor
                if curFactor >= 0.98 and self:
                    self.ShutdownAnim()
            self.initialized = True
            eveui.wait_for_next_frame()
