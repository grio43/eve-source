#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\views\materialGroups.py
import math
from math import acos, cos, sin, asin, pi, fabs
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.util.color import Color
from eve.client.script.ui.shared.industry.views.materialGroupDashedCircle import MaterialGroupDashedCircle
import industry
from localization import GetByLabel
from eve.client.script.ui.control.eveLabel import EveCaptionMedium
from eve.client.script.ui.shared.industry import industryUIConst
from eve.client.script.ui.shared.industry.views.industryLine import IndustryLineTrace
from eve.client.script.ui.shared.industry.views.materialGroup import MaterialGroup
import geo2
import uthread
from carbonui.uicore import uicore
BIGCIRCLE_OFFSET = 100
TOTAL_ROWS = 6
GROUP_NUMROWS = ((6,),
 (3, 3),
 (2, 2, 2),
 (2, 1, 1, 2),
 (1, 1, 2, 1, 1),
 (1, 1, 1, 1, 1, 1))
GROUP_BACKGROUNDS = {GROUP_NUMROWS[0]: 'res:/UI/Texture/Classes/Industry/Input/bg1Groups.png',
 GROUP_NUMROWS[1]: 'res:/UI/Texture/Classes/Industry/Input/bg2Groups.png',
 GROUP_NUMROWS[2]: 'res:/UI/Texture/Classes/Industry/Input/bg3Groups.png',
 GROUP_NUMROWS[3]: 'res:/UI/Texture/Classes/Industry/Input/bg4Groups.png',
 GROUP_NUMROWS[4]: 'res:/UI/Texture/Classes/Industry/Input/bg5Groups.png',
 GROUP_NUMROWS[5]: 'res:/UI/Texture/Classes/Industry/Input/bg6Groups.png',
 (2, 3, 1): 'res:/UI/Texture/Classes/Industry/Input/bgGroups_2_3_1.png',
 (3, 1, 1, 1): 'res:/UI/Texture/Classes/Industry/Input/bgGroups_3_1_1_1.png',
 (4, 2): 'res:/UI/Texture/Classes/Industry/Input/bgGroups_4_2.png',
 (5, 1): 'res:/UI/Texture/Classes/Industry/Input/bgGroups_5_1.png'}

class MaterialGroups(Container):
    default_name = 'MaterialGroups'
    __notifyevents__ = ['OnMultipleItemChange', 'OnUIScalingChange']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.jobData = attributes.jobData
        self.materialGroups = []
        self.lines = []
        self.fromLine = None
        self.bigConnectorCircle = None
        self.animateTextThread = None
        noItemsLabelCont = Container(name='noItemsLabelCont', parent=self, align=uiconst.TOPLEFT_PROP, pos=(0.0, 0.5, 0.5, 500), padRight=industryUIConst.RADIUS_CENTERCIRCLE_OUTER)
        self.noItemsRequiredLabel = EveCaptionMedium(name='noItemsRequiredLabel', parent=noItemsLabelCont, align=uiconst.CENTER, opacity=0.0, maxWidth=250)
        self.bg = StretchSpriteHorizontal(name='groupBackground', parent=self, align=uiconst.TOLEFT_PROP, state=uiconst.UI_DISABLED, width=0.5, height=402, leftEdgeSize=10, rightEdgeSize=400)
        groupsData = self.GetMaterialGroups()
        self.ConstructGroups(groupsData)
        self.ConstructLines(groupsData)
        self.UpdateState()
        self.AnimEntry()

    def DrawBigConnectorCircle(self, groupsData):
        x, y = self.GetPointBigCircleLeft()
        if not self.bigConnectorCircle:
            self.bigConnectorCircle = MaterialGroupDashedCircle(name='bigConnectorCircle', parent=self, radius=industryUIConst.RADIUS_CONNECTOR_LARGE, color=industryUIConst.COLOR_READY, numSegments=len(groupsData), lineWidth=3.0, materialsByGroupID=groupsData, jobData=self.jobData)
            self.bigConnectorCircle.UpdateState(1)
        self.bigConnectorCircle.left = x
        self.bigConnectorCircle.top = y - industryUIConst.RADIUS_CONNECTOR_LARGE

    def ConstructLines(self, groupsData):
        for line in self.lines:
            line.Close()

        if self.fromLine:
            self.fromLine.Close()
        self.lines = []
        if self.materialGroups:
            self.DrawBigConnectorCircle(groupsData)
            self.DrawLines()
        if self.jobData:
            self.DrawLineFromCenter()

    def GetStatusText(self):
        if self.jobData:
            status = self.jobData.status
            if status == industry.STATUS_UNSUBMITTED:
                text = GetByLabel('UI/Industry/NoInputItemsRequired')
            elif status == industry.STATUS_INSTALLED:
                text = GetByLabel('UI/Industry/JobActive')
            elif status == industry.STATUS_READY:
                text = GetByLabel('UI/Industry/JobReadyForDelivery')
            else:
                text = self.jobData.GetJobStateLabel()
        else:
            text = GetByLabel('UI/Industry/NoBlueprintSelectedCaption')
        return text

    def ConstructGroups(self, groupsData):
        for group in self.materialGroups:
            group.Close()

        self.materialGroups = []
        numRowsByGroupIdx = self._GetNumRowsByGroup(groupsData)
        bgTexturePath = GROUP_BACKGROUNDS.get(numRowsByGroupIdx, 'res:/UI/Texture/Classes/Industry/Input/bg1Groups.png')
        if groupsData:
            top = 1
            for i, (industryGroupID, materialsData) in enumerate(groupsData):
                numRows = numRowsByGroupIdx[i]
                height = 60 * numRows + 8 * max(0, numRows - 1)
                materialGroup = MaterialGroup(parent=self, industryGroupID=industryGroupID, jobData=self.jobData, materialsData=materialsData, pos=(0,
                 top,
                 400,
                 height), numRows=numRows, opacity=0.0)
                top += height + 8
                self.materialGroups.append(materialGroup)

            statusText = ''
        else:
            statusText = self.GetStatusText()
        self.AnimateStateText(statusText)
        self.bg.SetTexturePath(bgTexturePath)

    def _GetNumRowsByGroup(self, groupsData):
        numGroups = len(groupsData)
        numGroupsIdx = max(numGroups - 1, 0)
        numRowsByGroup = GROUP_NUMROWS[numGroupsIdx]
        MAX_MATERIAL_PER_ROW = 5
        rowsNeeded = []
        for industryGroupID, materialsData in groupsData:
            numMaterials = len(materialsData)
            numRows = int(math.ceil(float(numMaterials) / MAX_MATERIAL_PER_ROW))
            rowsNeeded.append(numRows)

        numRowsNeeded = sum(rowsNeeded)
        if numRowsNeeded > TOTAL_ROWS:
            return numRowsByGroup
        for shouldBe, needed in zip(numRowsByGroup, rowsNeeded):
            if needed > shouldBe:
                if numRowsNeeded < TOTAL_ROWS:
                    lastRowValue = rowsNeeded[-1]
                    newLastRowValue = lastRowValue + (TOTAL_ROWS - numRowsNeeded)
                    rowsNeeded[-1] = newLastRowValue
                return tuple(rowsNeeded)

        return numRowsByGroup

    def AnimateStateText(self, text):
        if self.animateTextThread:
            self.animateTextThread.kill()
        self.animateTextThread = uthread.new(self._AnimateStateText, text)

    def _AnimateStateText(self, text):
        if self.noItemsRequiredLabel.text:
            uicore.animations.FadeOut(self.noItemsRequiredLabel, duration=0.3, sleep=True)
        self.noItemsRequiredLabel.text = text
        uicore.animations.FadeTo(self.noItemsRequiredLabel, 0.0, 0.9, duration=0.6)
        self.animateTextThread = None

    def GetInnerCircleIntersectPoint(self, y):
        pCenter = self.GetPointCenter()
        y = pCenter[1] - y
        th = asin(y / industryUIConst.RADIUS_CENTERCIRCLE_OUTER) + pi
        r = industryUIConst.RADIUS_CENTERCIRCLE_INNER
        p = (r * cos(th), r * sin(th))
        p = geo2.Vec2Add(p, pCenter)
        return (p, th)

    def GetOuterCirclePoint(self, p, p1):
        l = industryUIConst.RADIUS_CENTERCIRCLE_OUTER - industryUIConst.RADIUS_CENTERCIRCLE_INNER
        t = 1.0 - (l - industryUIConst.RADIUS_CONNECTOR_SMALL) / l
        return geo2.Vec2Lerp(p, p1, t)

    def DrawLine(self, points):
        line = IndustryLineTrace(parent=self, opacity=0.0)
        line.AddPoints(points)
        self.lines.append(line)

    def DrawLineFromCenter(self):
        self.fromLine = IndustryLineTrace(name='fromLine', parent=self, opacity=0.0)
        self.fromLine.AddPoints((self.GetPointCenter(), self.GetPointCenterRight()))

    def DrawLineToCenter(self, p):
        self.DrawLine((p, self.GetPointBigCircleLeft()))
        self.DrawLine((self.GetPointBigCircleRight(), self.GetPointCenter()))

    def GetPointCenter(self):
        width, height = self.GetAbsoluteSize()
        return (width / 2, height / 2 + 1)

    def GetPointBigCircleLeft(self):
        x, y = self.GetPointCenter()
        return (x - BIGCIRCLE_OFFSET - industryUIConst.RADIUS_CONNECTOR_LARGE, y)

    def GetPointBigCircleRight(self):
        x, y = self.GetPointCenter()
        return (x - BIGCIRCLE_OFFSET + industryUIConst.RADIUS_CONNECTOR_LARGE, y)

    def GetPointCenterLeft(self):
        x, y = self.GetPointCenter()
        return (x - industryUIConst.RADIUS_CENTERCIRCLE_INNER, y)

    def GetPointCenterRight(self):
        w, h = self.GetCurrentAbsoluteSize()
        return (w - 334, h / 2.0)

    def DrawLines(self):
        x1, y1 = self.GetAbsolutePosition()
        linePoints = []
        thetas = []
        for materialGroup in self.materialGroups:
            pCircleIntersect = materialGroup.GetEndPoint()
            if pCircleIntersect is None:
                continue
            x0, y0 = pCircleIntersect
            p = (x0, materialGroup.top + materialGroup.height / 2.0)
            p1, theta = self.GetInnerCircleIntersectPoint(p[1])
            thetas.append(theta)
            p0 = self.GetOuterCirclePoint(p, p1)
            linePoints.append((p0, p1))

        if len(linePoints) == 1:
            p = linePoints[0][0]
            self.DrawLineToCenter(p)
            return
        if not thetas:
            return
        thetaFirst = thetas[0]
        thetaLast = thetas[-1]
        numPoints = int(fabs((thetaFirst - thetaLast) * 8))
        stepSize = (thetaLast - thetaFirst) / numPoints
        lineStart = linePoints.pop(0)
        arcPoints = [lineStart[0]]
        r = industryUIConst.RADIUS_CENTERCIRCLE_INNER
        for i in xrange(numPoints):
            th = thetaFirst + float(i) * stepSize
            p = (r * cos(th), r * sin(th))
            p = geo2.Vec2Add(self.GetPointCenter(), p)
            arcPoints.append(p)

        lineEnd = linePoints.pop()
        arcPoints.extend([lineEnd[1], lineEnd[0]])
        self.DrawLine(arcPoints)
        for p0, p1 in linePoints:
            self.DrawLine((p0, p1))

        self.DrawLineToCenter(self.GetPointCenterLeft())

    def AnimEntry(self, animate = True):
        k = 0.05
        for i, materialGroup in enumerate(self.materialGroups):
            if animate:
                uicore.animations.FadeTo(materialGroup, 0.0, 1.0, duration=0.3, timeOffset=k * i)
            else:
                materialGroup.opacity = 1.0
            materialGroup.AnimEntry(k * i, animate=animate)

        i = 0
        for i, line in enumerate(self.lines):
            line.AnimEntry(0.2, i, animate=animate)

        if self.fromLine:
            self.fromLine.AnimEntry(0.8, i + 1, animate=animate)
        if self.jobData and animate:
            uicore.animations.FadeTo(self.bg, 0.0, 1.0, duration=0.6)

    def GetMaterialGroups(self):
        if not self.jobData:
            return []
        else:
            return self.jobData.GetMaterialsByGroups()

    def OnMultipleItemChange(self, items, change):
        self.OnRunsChanged()

    def OnRunsChanged(self):
        for materialGroup in self.materialGroups:
            materialGroup.OnRunsChanged()

        self.UpdateState()

    def OnNewJobData(self, jobData):
        if self.destroyed:
            return
        self.jobData = jobData
        groupsData = self.GetMaterialGroups()
        if self.bigConnectorCircle:
            self.bigConnectorCircle.Close()
            self.bigConnectorCircle = None
        self.ConstructGroups(groupsData)
        self.ConstructLines(groupsData)
        self.UpdateState(animate=False)
        self.AnimEntry()

    def UpdateState(self, animate = True):
        isReady = self.IsAllGroupsReady()
        for i, line in enumerate(self.lines):
            line.UpdateColor(isReady, animate=animate)

        if self.fromLine:
            self.fromLine.UpdateColor(isReady, animate=animate)
        if self.bigConnectorCircle:
            self.bigConnectorCircle.UpdateState(self.GetNumGroupsReady(), self.IsAllGroupsReady())

    def IsAllGroupsReady(self):
        for group in self.materialGroups:
            if not group.IsReady():
                return False

        return True

    def GetNumGroupsReady(self):
        return sum([ materialGroup.IsReady() for materialGroup in self.materialGroups ])

    def OnUIScalingChange(self, *args):
        self.OnNewJobData(self.jobData)

    def _OnResize(self, *args):
        if not self.jobData:
            return
        for group in self.materialGroups:
            group.ConstructLines()

        self.ConstructLines(self.GetMaterialGroups())
        self.UpdateState(animate=False)
        self.AnimEntry(animate=False)
