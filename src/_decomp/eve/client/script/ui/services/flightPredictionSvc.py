#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\flightPredictionSvc.py
import blue
import carbonui.control.button
import destiny
import geo2
import telemetry
import trinity
import uthread
from carbonui import uiconst
from carbon.common.script.sys import service
from carbonui.control.slider import Slider
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from eve.client.script.parklife import states as state
from eve.client.script.ui.control import eveLabel
ANIMSTATE_NONE = None
ANIMSTATE_IN = 'In'
ANIMSTATE_STEADY = 'Steady'
ANIMSTATE_OUT = 'Out'
ANIMSTATE_COMPLETE = 'Complete'
LINEMODE_ONESHOT = 'OneShot'
LINEMODE_MANUAL = 'Manual'
LINEMODE_LOOP = 'Loop'
ANIM_IN_TIME = 0.5
ANIM_OUT_TIME = 0.5
CONFIRM_COLOR = (0.8,
 0.8,
 0.8,
 0.8)
DEFAULT_COLOR = (0.8,
 0.8,
 0.8,
 0.8)
FADEOUT_TIME = 0.5
LINE_WIDTH = 3.0

class PredictionLineSettings():

    def __init__(self, mode = None, range = None, targetID = None, otherData = None):
        self.mode = mode
        self.range = range
        self.targetID = targetID
        self.otherData = otherData


class OrbitRangeDrawer():

    def __init__(self):
        self.lineSet = None

    def AddLinesToScene(self):
        if self.lineSet is None:
            self.lineSet = self.CreateLineset()
        scene = sm.GetService('sceneManager').GetActiveScene()
        if scene is not None:
            if self.lineSet not in scene.objects:
                scene.objects.append(self.lineSet)
            return True
        return False

    def CreateLineset(self):
        lineSet = trinity.EveCurveLineSet()
        lineSet.scaling = (1.0, 1.0, 1.0)
        tex2D1 = trinity.TriTextureParameter()
        tex2D1.name = 'TexMap'
        tex2D1.resourcePath = 'res:/dx9/texture/UI/lineSolid.dds'
        lineSet.lineEffect.resources.append(tex2D1)
        return lineSet

    def Update(self, center, range, closestPoints, width):
        self.AddLinesToScene()
        self.ClearLines()
        d0 = geo2.Vec3SubtractD(center, closestPoints[0])
        d1 = geo2.Vec3SubtractD(center, closestPoints[1])
        up = geo2.Vec3NormalizeD(geo2.Vec3CrossD(d1, d0))
        dir = geo2.Vec3NormalizeD(d0)
        pFar = geo2.Vec3AddD(center, geo2.Vec3ScaleD(dir, range))
        pNear = geo2.Vec3AddD(center, geo2.Vec3ScaleD(dir, -range))
        perp = geo2.Vec3NormalizeD(geo2.Vec3CrossD(dir, up))
        pRight = geo2.Vec3AddD(center, geo2.Vec3ScaleD(perp, range))
        pLeft = geo2.Vec3AddD(center, geo2.Vec3ScaleD(perp, -range))
        width *= LINE_WIDTH
        self.lineSet.AddSpheredLineCrt(pFar, DEFAULT_COLOR, pRight, DEFAULT_COLOR, center, width)
        self.lineSet.AddSpheredLineCrt(pRight, DEFAULT_COLOR, pNear, DEFAULT_COLOR, center, width)
        self.lineSet.AddSpheredLineCrt(pNear, DEFAULT_COLOR, pLeft, DEFAULT_COLOR, center, width)
        self.lineSet.AddSpheredLineCrt(pLeft, DEFAULT_COLOR, pFar, DEFAULT_COLOR, center, width)
        self.lineSet.SubmitChanges()

    def ClearLines(self):
        if self.lineSet is not None:
            self.lineSet.ClearLines()
            self.lineSet.SubmitChanges()

    def TearDownLines(self):
        self.ClearLines()
        scene = sm.GetService('sceneManager').GetActiveScene()
        if scene is not None:
            if self.lineSet in scene.objects:
                scene.objects.remove(self.lineSet)
        self.lineSet = None


class SmoothSpaceLine():

    def __init__(self, getPointsFunc, settings, lineMode = LINEMODE_MANUAL, color = None, updatePoints = True):
        self.lineSet = None
        self.updateThread = None
        self.getPointsFunc = getPointsFunc
        self.updateDelay = 1.0 / 30.0
        self.settings = PredictionLineSettings(settings.mode, settings.range, settings.targetID, settings.otherData)
        self.points = None
        self.lineMode = lineMode
        self.color = color or DEFAULT_COLOR
        self.updatePoints = updatePoints
        self.ballpark = sm.GetService('michelle').GetBallpark()
        self.killed = False
        self.fadeTime = None
        self.delta = 0
        self.lastTime = self.ballpark.time
        self.orbitDrawer = None
        self.Start()

    def IsAlive(self):
        return self.updateThread is not None

    def SwallowOut(self, confirmed = True):
        self.lineMode = LINEMODE_ONESHOT
        if confirmed:
            self.color = CONFIRM_COLOR
        if self.points is None:
            self.Close()

    def FadeOut(self):
        if self.fadeTime is None:
            self.fadeTime = 1
        if self.points is None:
            self.Close()

    def Close(self):
        self.killed = True

    def Start(self):
        linesInScene = self.AddLinesToScene()
        self.animationPos = 0.0
        self.animState = ANIMSTATE_IN
        if self.updateThread is None and linesInScene:
            self.updateThread = uthread.new(self._LineUpdateThread)
            self.updateThread.context = 'flightPredictionSvc.SmoothSpaceLine.UpdateThread'

    def AddLinesToScene(self):
        if self.lineSet is None:
            self.lineSet = self.CreateLineset()
        scene = sm.GetService('sceneManager').GetActiveScene()
        if scene is not None:
            if self.lineSet not in scene.objects:
                scene.objects.append(self.lineSet)
            return True
        return False

    def CreateLineset(self):
        lineSet = trinity.EveCurveLineSet()
        lineSet.scaling = (1.0, 1.0, 1.0)
        tex2D1 = trinity.TriTextureParameter()
        tex2D1.name = 'TexMap'
        tex2D1.resourcePath = 'res:/dx9/texture/UI/lineSolid.dds'
        lineSet.lineEffect.resources.append(tex2D1)
        return lineSet

    @telemetry.ZONE_METHOD
    def _LineUpdateThread(self):
        while self.animState != ANIMSTATE_COMPLETE and not self.killed:
            if self.points is None or self.updatePoints:
                self.points = self.getPointsFunc(self.settings) or self.points
            if self.points is not None:
                self.MakeLines(self.points)
                self.UpdateAnimationTimers()
            blue.pyos.synchro.Sleep(self.updateDelay)

        if self.orbitDrawer is not None:
            self.orbitDrawer.TearDownLines()
            self.orbitDrawer = None
        self.TearDownLines()
        self.updateThread = None

    def UpdateAnimationTimers(self):
        if self.lastTime is not None:
            self.delta = blue.os.TimeDiffInMs(self.lastTime, blue.os.GetSimTime()) / 1000.0
        self.lastTime = blue.os.GetSimTime()
        self.UpdateAnim()
        if self.fadeTime is not None:
            self.fadeTime -= FADEOUT_TIME * self.delta
            if self.fadeTime < 0:
                self.killed = True

    def UpdateAnim(self):
        inSpeed = self.delta / ANIM_IN_TIME
        outSpeed = self.delta / ANIM_OUT_TIME
        self.animationPos = min(1.0, max(0.0, self.animationPos))
        if self.animState == ANIMSTATE_IN:
            self.animationPos = self.animationPos + inSpeed
            if self.animationPos >= 1.0:
                self.animationPos = 1.0
                self.animState = ANIMSTATE_STEADY
        elif self.animState == ANIMSTATE_STEADY:
            self.animationPos = 1.0
            if self.lineMode in (LINEMODE_LOOP, LINEMODE_ONESHOT):
                self.animState = ANIMSTATE_OUT
        elif self.animState == ANIMSTATE_OUT:
            self.animationPos = self.animationPos - outSpeed
            if self.animationPos <= 0.0:
                self.animationPos = 0.0
                if self.lineMode == LINEMODE_LOOP:
                    self.animState = ANIMSTATE_IN
                else:
                    self.animState = ANIMSTATE_COMPLETE

    @telemetry.ZONE_METHOD
    def GetDrawDataFromPoints(self, points):
        drawPoints = []
        ballPos = self.ballpark.GetCurrentEgoPos()[:3]
        for i, p in enumerate(points):
            percent = float(i) / len(points)
            width = self.GetWidthForPointFraction(percent)
            pos = p[:3]
            if ballPos is not None:
                pos = geo2.Vec3SubtractD(pos, ballPos)
            drawPoints.append((pos, width))

        return drawPoints

    def GetWidthForPointFraction(self, percent):
        width = self.animationPos
        lineWidthModifier = (1.0 - percent) * percent * 4
        lineWidth = LINE_WIDTH * lineWidthModifier * width
        return lineWidth

    @telemetry.ZONE_METHOD
    def MakeLines(self, dataPoints):
        if dataPoints is None:
            raise ValueError('dataPoints is None')
        drawPoints = self.GetDrawDataFromPoints(dataPoints)
        alpha = 1.0
        if self.fadeTime is not None:
            alpha = self.fadeTime
        c = (self.color[0],
         self.color[1],
         self.color[2],
         self.color[3] * alpha)
        self.MakeOrbitRing(drawPoints, alpha)
        self.ClearLines()
        for i in xrange(0, len(drawPoints) - 1):
            p0 = drawPoints[i][0]
            p1 = drawPoints[i + 1][0]
            lineWidth = drawPoints[i][1]
            curvedLine = self.lineSet.AddStraightLine(p0, c, p1, c, lineWidth)

        self.lineSet.SubmitChanges()

    def MakeOrbitRing(self, drawPoints, alpha):
        if self.settings.mode == 'Orbit':
            if self.orbitDrawer is None:
                self.orbitDrawer = OrbitRangeDrawer()
            m = sm.GetService('michelle')
            bp = m.GetBallpark()
            myPos = bp.GetCurrentEgoPos()[:3]
            targetBall = bp.GetBall(self.settings.targetID)
            targetPos = geo2.Vec3SubtractD((targetBall.x, targetBall.y, targetBall.z), myPos)
            closestPoints = [drawPoints[-2][0], drawPoints[-1][0]]
            totalRange = self.settings.range + bp.GetBall(bp.ego).radius + targetBall.radius
            self.orbitDrawer.Update(targetPos, totalRange, closestPoints, self.animationPos * alpha)

    def ClearLines(self):
        self.lineSet.ClearLines()
        self.lineSet.SubmitChanges()

    def TearDownLines(self):
        self.ClearLines()
        scene = sm.GetService('sceneManager').GetActiveScene()
        if scene is not None:
            if self.lineSet in scene.objects:
                scene.objects.remove(self.lineSet)
        self.lineSet = None

    def UpdateSettings(self, newSettings):
        if newSettings.mode is None or newSettings.range is None or newSettings.targetID is None:
            if self.fadeTime is None:
                self.FadeOut()
        else:
            self.fadeTime = None
            if newSettings.mode is not None:
                self.settings.mode = newSettings.mode
                if self.settings.mode != 'Orbit' and self.orbitDrawer is not None:
                    self.orbitDrawer.TearDownLines()
            if newSettings.range is not None:
                self.settings.range = newSettings.range
            if newSettings.targetID is not None:
                self.settings.targetID = newSettings.targetID
        self.settings.otherData = newSettings.otherData


class FlightPredictionService(service.Service):
    __guid__ = 'svc.flightPredictionSvc'
    __notifyevents__ = ['OnStateChange', 'OnViewStateChanged']
    __servicename__ = 'FlightPrediction'
    __displayname__ = 'Flight Prediction Service'
    __dependencies__ = ['michelle', 'menu']
    modeInfoByModeName = {'Approach': ('KeepAtRange', 50),
     'Orbit': ('Orbit', 'Orbit'),
     'KeepAtRange': ('KeepAtRange', 'KeepAtRange'),
     'AlignTo': ('KeepAtRange', 0),
     'WarpTo': ('KeepAtRange', 0)}
    modeNameByCommand = {'CmdApproachItem': 'Approach',
     'CmdOrbitItem': 'Orbit',
     'CmdKeepItemAtRange': 'KeepAtRange',
     'CmdAlignToItem': 'AlignTo',
     'CmdWarpToItem': 'WarpTo'}

    def __init__(self):
        service.Service.__init__(self)
        self.methodsByMode = {'KeepAtRange': self.GetPredictKeepAtRangePoints,
         'Orbit': self.GetPredictOrbitPoints,
         'Current': self.GetCurrentPathPoints,
         'Direction': self.GetGotoDirectionPoints}
        self.numPoints = 10
        self.testLineDrawer = None
        self.ball = None
        self.currentPathLine = None
        self._line = None
        self.lineSettings = PredictionLineSettings(None, None, None)
        self.enabled = False

    def Run(self, memStream = None):
        pass

    def OnViewStateChanged(self, oldView, newView):
        if newView != 'inflight':
            currentLine = self.GetLine()
            if currentLine is not None:
                currentLine.Close()

    def IsActive(self):
        return self.enabled and sm.GetService('viewState').IsViewActive('inflight')

    def GetPoints(self, settings):
        func = self.methodsByMode[settings.mode]
        return func(settings)

    def UpdateLineSettings(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self.lineSettings, k, v)
            lostMode = k == 'mode' and v is None

        if not self.IsActive():
            return
        currentLine = self.GetLine()
        if currentLine is None:
            if self.lineSettings.mode is not None:
                self.SetLine(SmoothSpaceLine(self.GetPoints, self.lineSettings))
        elif lostMode:
            currentLine.FadeOut()
        else:
            currentLine.UpdateSettings(self.lineSettings)

    def OnStateChange(self, itemID, flag, status, *args):
        if not self.IsActive():
            return
        if itemID == session.shipid:
            if flag == state.mouseOver:
                if self.currentPathLine is not None:
                    self.currentPathLine.SwallowOut(confirmed=False)
                if status:
                    settings = PredictionLineSettings(mode='Current')
                    self.currentPathLine = SmoothSpaceLine(self.GetPoints, settings)
        elif flag == state.mouseOver:
            if status:
                self.UpdateLineSettings(targetID=itemID)
            else:
                self.UpdateLineSettings(targetID=None)

    def CommandKeyDown(self, command):
        if not self.IsActive():
            return
        if command not in self.modeNameByCommand:
            return
        modeName = self.modeNameByCommand[command]
        modeInfo = self.modeInfoByModeName[modeName]
        mode = modeInfo[0]
        range = modeInfo[1]
        if not isinstance(range, int):
            range = self.menu.GetDefaultActionDistance(range)
        self.UpdateLineSettings(mode=mode, range=range)

    def CommandKeyUp(self):
        if not self.IsActive():
            return
        self.UpdateLineSettings(mode=None)

    def OptionActivated(self, modeName, targetID, range = None):
        if not self.IsActive():
            return
        line = self.GetLine()
        if line is not None:
            line.SwallowOut()
            self.SetLine(None, withoutFade=True)
            self.UpdateLineSettings(mode=None)
            return
        mode, range = self.GetModeAndRange(modeName, range)
        settings = PredictionLineSettings(mode=mode, range=range, targetID=targetID)
        SmoothSpaceLine(self.GetPoints, settings, lineMode=LINEMODE_ONESHOT, updatePoints=True, color=CONFIRM_COLOR)

    def GotoDirection(self, direction):
        if not self.IsActive():
            return
        settings = PredictionLineSettings(mode='Direction', otherData=direction)
        SmoothSpaceLine(self.GetPoints, settings, lineMode=LINEMODE_ONESHOT, updatePoints=False, color=CONFIRM_COLOR)

    def RadialMenuStateChange(self, modeName, itemID = None, range = None):
        if not self.IsActive():
            return
        if modeName is None:
            self.UpdateLineSettings(mode=None)
            return
        mode, range = self.GetModeAndRange(modeName, range)
        self.UpdateLineSettings(mode=mode, targetID=itemID, range=range)

    def GetModeAndRange(self, modeName, range):
        if modeName not in self.modeInfoByModeName:
            raise ValueError('Invalid mode: ' + str(modeName))
        modeInfo = self.modeInfoByModeName[modeName]
        mode = modeInfo[0]
        if range is None:
            range = modeInfo[1]
            if not isinstance(range, int):
                range = self.menu.GetDefaultActionDistance(range)
        return (mode, range)

    @telemetry.ZONE_METHOD
    def GetPredictOrbitPoints(self, settings):
        if not settings.targetID or not self.HasBall():
            return
        points = self.ball.GetOrbitPredictionPoints(self.numPoints, settings.targetID, settings.range)
        return points

    @telemetry.ZONE_METHOD
    def GetPredictKeepAtRangePoints(self, settings):
        if not settings.targetID or not self.HasBall():
            return
        points = self.ball.GetFollowPredictionPoints(self.numPoints, settings.targetID, settings.range)
        return points

    @telemetry.ZONE_METHOD
    def GetCurrentPathPoints(self, settings):
        if not self.HasBall():
            return None
        if self.ball.mode == destiny.DSTBALL_WARP and self.ball.effectStamp != -1:
            return None
        points = self.ball.GetPredictionPoints(self.numPoints)
        return points

    @telemetry.ZONE_METHOD
    def GetGotoDirectionPoints(self, settings):
        if not settings.otherData or not self.HasBall():
            return
        dir = settings.otherData
        return self.ball.GetGotoDirectionPoints(self.numPoints, dir[0], dir[1], dir[2])

    def HasBall(self):
        ball = self.michelle.GetBall(session.shipid)
        if ball != self.ball:
            if self.ball is not None:
                self.ball.CleanupPrediction()
            self.ball = ball
        return self.ball is not None

    def GetLine(self):
        if self._line is not None:
            if not self._line.IsAlive():
                self._line = None
        return self._line

    def SetLine(self, value, withoutFade = False):
        if self._line is not None and not withoutFade:
            self._line.FadeOut()
        self._line = value


class FlightPredictionTestWindow(Window):
    __guid__ = 'form.FlightPredictionTestWindow'
    __dependencies__ = ['flightPredictionSvc']
    default_windowID = 'FlightPredictionTestWindow'
    default_width = 500
    default_height = 250
    default_minSize = (default_width, default_height)
    default_caption = 'Flight Prediction Service Test Window'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.cont = Container(name='cont', parent=self.sr.main, align=uiconst.TOALL, padding=10)
        self.sliders = {}
        self.AddSlider('Animation in time', 0.1, 10, 'ANIM_IN_TIME')
        self.AddSlider('Animation out time', 0.1, 10, 'ANIM_OUT_TIME')
        self.AddSlider('Line width', 2, 50, 'LINE_WIDTH')
        self.AddSlider('Fade out time', 0.1, 10, 'FADEOUT_TIME')
        self.AddColorSliders('Line Color', 'DEFAULT_COLOR')
        self.AddColorSliders('Confirm Color', 'CONFIRM_COLOR')
        carbonui.control.button.Button(parent=self.cont, align=uiconst.TOBOTTOM, label='Export to clipboard', func=self.Export)

    def AddSlider(self, name, min, max, valueName):
        value = globals()[valueName]
        c = Container(parent=self.cont, align=uiconst.TOTOP, height=20)
        l = eveLabel.Label(text=name + ':', parent=c, align=uiconst.TOPLEFT)
        slider = Slider(parent=c, align=uiconst.TOPLEFT, width=100, name=name.replace(' ', ''), state=uiconst.UI_NORMAL, minValue=min, maxValue=max, value=value, on_dragging=self.SetSlider, hint=name, left=l.width + 10)
        label = eveLabel.Label(text=value, parent=c, align=uiconst.TOPLEFT, left=l.width + 120)
        self.sliders[slider] = (valueName, label)

    def AddColorSliders(self, name, valueName):
        c = Container(parent=self.cont, align=uiconst.TOTOP, height=36)
        eveLabel.Label(text=name + ':', parent=c, align=uiconst.TOPLEFT)
        colorCont = Container(parent=c, align=uiconst.BOTTOMLEFT, left=440, width=40, height=20)
        colorFill = Fill(parent=colorCont, color=(1, 0, 1, 1))

        def SetColorValue(slider, valueIndex):
            colorList = list(globals()[valueName])
            colorList[valueIndex] = slider.GetValue()
            globals()[valueName] = tuple(colorList)
            colorFill.color = tuple(colorList)

        colorVal = globals()[valueName]
        self.ColorSlider(c, SetColorValue, 0, 0, colorVal[0])
        self.ColorSlider(c, SetColorValue, 1, 110, colorVal[1])
        self.ColorSlider(c, SetColorValue, 2, 220, colorVal[2])
        self.ColorSlider(c, SetColorValue, 3, 330, colorVal[3])
        self.sliders[c] = (valueName, name)

    def ColorSlider(self, parent, onSet, index, left, val):
        colorName = {0: 'Red',
         1: 'Green',
         2: 'Blue',
         3: 'Alpha'}[index]
        slider = Slider(parent=parent, align=uiconst.BOTTOMLEFT, width=100, name=colorName + 'Slider', minValue=0.0, maxValue=1.0, value=val, on_dragging=lambda slider: onSet(slider, index), hint=colorName, left=left)
        return slider

    def SetSlider(self, slider):
        if slider not in self.sliders:
            return
        valueName, label = self.sliders[slider]
        value = round(slider.GetValue(), 2)
        globals()[valueName] = value
        label.text = value

    def Export(self, button):
        lines = []
        for valueName, label in self.sliders.itervalues():
            value = globals()[valueName]
            if value is not float:
                line = valueName + ' = ' + str(value)
            else:
                line = valueName + ' = ' + str(round(value, 2))
            lines.append(line)

        lines.sort()
        clipboardData = '\n'.join(lines)
        blue.pyos.SetClipboardData(clipboardData)
        eve.Message('CustomNotify', {'notify': 'Data exported to clipboard. Give this to someone to put in flightPredictionSvc.py :D'})
