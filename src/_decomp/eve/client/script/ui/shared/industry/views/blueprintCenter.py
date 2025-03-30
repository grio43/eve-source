#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\views\blueprintCenter.py
from math import pi
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.frame import Frame
from carbonui.primitives.transform import Transform
from eve.client.script.ui.control.themeColored import FrameThemeColored
from eve.client.script.ui.shared.industry import industryUIConst
from eve.client.script.ui.shared.industry.views.errorFrame import ErrorFrame
import industry
import localization
import uthread
import blue
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from localization import GetByLabel
from carbon.common.script.sys.service import ROLE_PROGRAMMER
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.shared.industry.industryUIConst import GetJobColor, COLOR_FRAME
from eve.client.script.ui.shared.industry.views.containersMETE import ContainerME, ContainerTE
from eve.client.script.ui.shared.industry.views.industryCaptionLabel import IndustryCaptionLabel
from eve.client.script.ui.shared.industry.views.skillIcon import SkillIcon
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
WEDGE_TRAVEL = 15

class BlueprintCenter(Container):
    __notifyevents__ = ('OnIndustryWndMouseWheel', 'OnIndustryWndClick', 'OnBlueprintBrowserNumericInput')

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.jobData = attributes.jobData
        self.newNumRuns = None
        self.setJobRunsThread = None
        self.oldJobData = None
        self.numericInputTimer = None
        self.iconCont = BlueprintItemIcon(parent=self, align=uiconst.CENTER, state=uiconst.UI_NORMAL, pos=(0, 0, 64, 64), opacity=0.0, jobData=self.jobData)
        self.errorFrame = ErrorFrame(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=80, height=80)
        self.ConstructBackground()
        self.ConstructRunsCont()
        self.gauge = None
        self.skillSprite = SkillIcon(parent=self, align=uiconst.CENTERBOTTOM, top=5, jobData=self.jobData)
        self.containerME = ContainerME(parent=self, align=uiconst.CENTER, pos=(113, -25, 79, 30), jobData=self.jobData, opacity=0.0)
        self.containerTE = ContainerTE(parent=self, align=uiconst.CENTER, pos=(113, 25, 79, 30), jobData=self.jobData, opacity=0.0)
        self.runsRemainingCont = ContainerAutoSize(name='bpCopyCont', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, top=90)
        self.runsRemainingCont.OnClick = self.OnRunsRemainingContClicked
        self.runsRemainingCaption = IndustryCaptionLabel(parent=self.runsRemainingCont, align=uiconst.CENTERTOP)
        self.runsRemainingLabel = EveLabelMedium(name='runsRemainingLabel', parent=self.runsRemainingCont, align=uiconst.CENTERTOP, top=14)
        self.UpdateState()
        self.AnimEntry()

    def ConstructRunsCont(self):
        self.runsCont = ContainerAutoSize(parent=self, align=uiconst.CENTER, top=100, width=76)
        labelCont = ContainerAutoSize(parent=self.runsCont, align=uiconst.TOTOP)
        self.runsCaption = IndustryCaptionLabel(name='runsCaption', parent=labelCont, align=uiconst.CENTER, text=GetByLabel('UI/Industry/JobRuns'))
        self.runsEdit = BlueprintSingleLineEdit(parent=self.runsCont, align=uiconst.TOTOP, OnChange=self.OnRunsEdit, autoselect=True)
        self.runsPerCopyCont = ContainerAutoSize(name='runsPerCopyCont', parent=self.runsCont, align=uiconst.TOTOP, padTop=8, state=uiconst.UI_HIDDEN)
        labelCont = ContainerAutoSize(parent=self.runsPerCopyCont, align=uiconst.TOTOP)
        IndustryCaptionLabel(name='runsPerCopyCaption', parent=labelCont, align=uiconst.CENTER, text=GetByLabel('UI/Industry/RunsPerCopy'))
        self.runsPerCopyEdit = BlueprintSingleLineEdit(parent=self.runsPerCopyCont, align=uiconst.TOTOP, OnChange=self.OnRunsPerCopyEdit, autoselect=True)

    def OnRunsRemainingContClicked(self, *args):
        if self.runsEdit.state == uiconst.UI_NORMAL:
            self.runsEdit.SetValue(self.jobData.maxRuns)

    def OnBlueprintBrowserNumericInput(self, key, flag):
        if not self.numericInputTimer:
            self.runsEdit.SelectAll()
        else:
            self.numericInputTimer.kill()
        self.numericInputTimer = uthread.new(self.NumericInputTimer)
        self.runsEdit.OnChar(key, flag)

    def NumericInputTimer(self):
        blue.synchro.SleepWallclock(1000)
        self.numericInputTimer = None

    def OnJobUpdated(self, job):
        if self.jobData and self.jobData == job:
            self.UpdateStateJob()

    def UpdateStateJob(self):
        self.iconCont.Show()
        typeID = self.jobData.blueprint.blueprintTypeID
        self.iconCont.SetTypeID(typeID=typeID, bpData=self.jobData.blueprint)
        self.UpdateGaugeValue()
        self.UpdateStateRunsEdit()
        self.UpdateStateRunsPerCopyEdit()
        self.skillSprite.Show()
        self.UpdateRunsRemainingLabel()
        self.containerME.SetValue(self.jobData.blueprint.materialEfficiency)
        self.containerTE.SetValue(self.jobData.blueprint.timeEfficiency)
        self.jobData.on_updated.connect(self.OnJobUpdated)
        activity = self.jobData.GetCurrentActivity()
        if activity and activity.IsOmegaActivity():
            self.iconCont.ShowOmegaOverlay()
        else:
            self.iconCont.HideOmegaOverlay()
        sm.ScatterEvent('OnSelectedIndustryJobChanged', jobData=self.jobData)

    def UpdateRunsRemainingLabel(self):
        if not self.jobData:
            return
        if self.jobData.IsInstalled():
            self.runsRemainingCont.Hide()
        else:
            runsText = self.jobData.GetRunsRemainingLabel()
            if runsText:
                self.runsRemainingCont.Show()
                self.runsRemainingLabel.text = runsText
                self.runsRemainingCaption.text = self.jobData.GetRunsRemainingCaption()
            else:
                self.runsRemainingCont.Hide()

    def SetNumRuns(self, numRuns):
        if not self.jobData.IsInstalled():
            self.runsEdit.SetValue(numRuns)

    def UpdateStateRunsEdit(self):
        if self.jobData.IsInstalled():
            self.runsEdit.SetMinValue(self.jobData.runs)
            self.runsEdit.SetMaxValue(self.jobData.runs)
            self.runsEdit.Show()
            self.runsCaption.Show()
            self.runsEdit.Disable()
        else:
            self.runsEdit.SetMinValue(1)
            self.runsEdit.SetMaxValue(self.jobData.maxRuns)
            self.runsEdit.Enable()
            self.runsEdit.Show()
            self.runsCaption.Show()
        self.runsEdit.SetValue(self.jobData.runs)

    def UpdateStateRunsPerCopyEdit(self):
        if self.jobData.activityID == industry.COPYING:
            if self.jobData.IsInstalled():
                self.runsPerCopyEdit.SetMinValue(self.jobData.licensedRuns)
                self.runsPerCopyEdit.SetMaxValue(self.jobData.licensedRuns)
                self.runsPerCopyEdit.Disable()
            else:
                self.runsPerCopyEdit.SetMinValue(1)
                self.runsPerCopyEdit.SetMaxValue(self.jobData.maxLicensedRuns)
                self.runsPerCopyEdit.Enable()
            self.runsPerCopyEdit.SetValue(self.jobData.licensedRuns)
            self.runsPerCopyCont.Show()
        else:
            self.runsPerCopyCont.Hide()

    def UpdateState(self):
        if self.jobData:
            self.UpdateStateJob()
        else:
            self.iconCont.Hide()
            self.runsEdit.Hide()
            self.runsPerCopyCont.Hide()
            self.runsCaption.Hide()
            self.skillSprite.Hide()
            self.runsRemainingCont.Hide()
            self.containerME.SetValue(0.0)
            self.containerTE.SetValue(0.0)

    def ReconstructGauge(self):
        if self.gauge:
            self.gauge.Close()
            self.gauge = None
        if not self.jobData:
            return
        color = GetJobColor(self.jobData)
        h, s, b = Color(*color).GetHSB()
        colorEnd = Color(*color).SetBrightness(b * 0.5).GetRGBA()
        self.gauge = BlueprintGaugeCircular(name='gauge', parent=self, align=uiconst.CENTER, radius=64, lineWidth=4, colorStart=color, colorEnd=colorEnd, jobData=self.jobData)

    def AnimWedges(self, startVal, endVal, duration, curveType = None):
        uicore.animations.MorphScalar(self.topWedge, 'top', startVal, endVal, duration=duration, curveType=curveType)
        uicore.animations.MorphScalar(self.bottomWedge, 'top', startVal, endVal, duration=duration, curveType=curveType)
        uicore.animations.MorphScalar(self.leftWedge, 'left', startVal, endVal, duration=duration, curveType=curveType)
        uicore.animations.MorphScalar(self.rightWedge, 'left', startVal, endVal, duration=duration, curveType=curveType)

    def AnimEntry(self):
        duration = 0.7
        if self.jobData:
            self.HideDashes()
            if self.topWedge.top < WEDGE_TRAVEL:
                self.AnimWedges(0, WEDGE_TRAVEL, duration)
            else:
                self.AnimWedges(WEDGE_TRAVEL, 18, 0.5, curveType=uiconst.ANIM_WAVE)
            if not self.IsSameBlueprint():
                uicore.animations.FadeTo(self.iconCont, 0.0, 1.0, duration=0.5)
            for obj in (self.containerME, self.containerTE):
                obj.Enable()
                uicore.animations.FadeIn(obj, duration=duration)

        else:
            self.AnimWedges(self.topWedge.top, 0.0, duration)
            for obj in (self.containerME, self.containerTE):
                obj.Disable()
                uicore.animations.FadeOut(obj, duration=duration)

            self.ShowDashes()
        if self.jobData and self.jobData.IsPreview():
            uicore.animations.FadeTo(self.iconCont, 0.0, 0.65, duration=0.5)
            self.errorFrame.Show()
            wedgeColor = industryUIConst.COLOR_NOTREADY
        else:
            self.errorFrame.Hide()
            wedgeColor = Color.WHITE
        for dots in self.wedgeDots:
            dots.SetRGBA(*wedgeColor)

        if self.gauge:
            uicore.animations.BlinkIn(self.gauge, 0.0, 1.0, timeOffset=0.98)
        for dots in self.wedgeDots:
            uicore.animations.BlinkIn(dots, 0.0, 0.85, timeOffset=0.78)

        for pattern in self.wedgeBg:
            if self.jobData and self.jobData.IsPreview():
                color = industryUIConst.COLOR_NOTREADY
            else:
                color = GetJobColor(self.jobData)
            uicore.animations.SpColorMorphTo(pattern, pattern.GetRGBA(), color, duration=0.3)

    def IsSameBlueprint(self):
        if not self.oldJobData or not self.jobData:
            return False
        if self.jobData:
            return self.jobData.blueprint.IsSameBlueprint(self.oldJobData.blueprint)
        return False

    def UpdateGaugeValue(self):
        if not self.gauge or not self.jobData:
            return
        self.gauge.SetValue(self.jobData.GetGaugeValue())

    def SetJobRuns(self, value):
        if not self.jobData:
            return
        if self.jobData.runs == value:
            if self.newNumRuns is None or self.newNumRuns == value:
                return
        self.newNumRuns = value
        if self.setJobRunsThread is None:
            self.setJobRunsThread = uthread.new(self._SetJobRuns)

    def _SetJobRuns(self):
        while self.jobData and self.newNumRuns is not None and not self.destroyed:
            if self.newNumRuns != self.jobData.runs:
                newNumRuns = self.newNumRuns
                self.newNumRuns = None
                self.jobData.runs = newNumRuns
            blue.synchro.SleepWallclock(100)

        if self.jobData:
            self.jobData.on_facility(self.jobData)
        self.setJobRunsThread = None

    def OnRunsEdit(self, value):
        try:
            value = int(value)
        except ValueError:
            return

        if self.jobData and not self.jobData.IsInstalled():
            self.SetJobRuns(value)

    def OnRunsChanged(self):
        self.UpdateGaugeValue()
        self.UpdateRunsRemainingLabel()

    def OnRunsPerCopyEdit(self, value):
        try:
            value = int(value)
        except ValueError:
            return

        self.jobData.licensedRuns = value

    def ConstructBackground(self):
        Frame(name='bgFrame', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=75, height=75, opacity=0.1)
        blueprintBg = FrameThemeColored(name='blueprintBgFill', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Industry/Center/bgFrame.png', width=90, height=90)
        self.dashesCont = Container(name='dashesCont', parent=self, state=uiconst.UI_DISABLED, pos=(75, 0, 150, 150), align=uiconst.CENTER)
        self.bgCont = Container(name='bgCont', parent=self, state=uiconst.UI_DISABLED, width=150, height=150, align=uiconst.CENTER)
        self.topWedge = Container(name='topWedge', parent=self.bgCont, align=uiconst.CENTERTOP, pos=(0, 0, 84, 60))
        topLines = Sprite(bgParent=self.topWedge, texturePath='res:/UI/Texture/classes/Industry/Center/wedgeTopBottom.png')
        topDots = Sprite(bgParent=self.topWedge, texturePath='res:/UI/Texture/classes/Industry/Center/dotsTopBottom.png')
        topBg = Sprite(bgParent=self.topWedge, texturePath='res:/UI/Texture/classes/Industry/Center/bgTop.png', color=COLOR_FRAME)
        self.bottomWedge = Container(name='bottomWedge', parent=self.bgCont, align=uiconst.CENTERBOTTOM, pos=(0, 0, 84, 60))
        bottomLines = Sprite(bgParent=self.bottomWedge, texturePath='res:/UI/Texture/classes/Industry/Center/wedgeTopBottom.png', rotation=pi)
        bottomDots = Sprite(bgParent=self.bottomWedge, texturePath='res:/UI/Texture/classes/Industry/Center/dotsTopBottom.png', rotation=pi)
        bottomBg = Sprite(bgParent=self.bottomWedge, texturePath='res:/UI/Texture/classes/Industry/Center/bgBottom.png', color=COLOR_FRAME)
        self.leftWedge = Container(name='leftWedge', parent=self.bgCont, align=uiconst.CENTERLEFT, pos=(0, 0, 60, 84))
        leftLines = Sprite(bgParent=self.leftWedge, texturePath='res:/UI/Texture/classes/Industry/Center/wedgeLeftRight.png')
        leftDots = Sprite(bgParent=self.leftWedge, texturePath='res:/UI/Texture/classes/Industry/Center/dotsLeftRight.png')
        leftBg = Sprite(bgParent=self.leftWedge, texturePath='res:/UI/Texture/classes/Industry/Center/bgLeft.png', color=COLOR_FRAME)
        self.rightWedge = Container(name='rightWedge', parent=self.bgCont, align=uiconst.CENTERRIGHT, pos=(0, 0, 60, 84))
        rightLines = Sprite(bgParent=self.rightWedge, texturePath='res:/UI/Texture/classes/Industry/Center/wedgeLeftRight.png', rotation=pi)
        rightDots = Sprite(bgParent=self.rightWedge, texturePath='res:/UI/Texture/classes/Industry/Center/dotsLeftRight.png', rotation=pi)
        rightBg = Sprite(bgParent=self.rightWedge, texturePath='res:/UI/Texture/classes/Industry/Center/bgRight.png', color=COLOR_FRAME)
        self.wedgeLines = [topLines,
         bottomLines,
         leftLines,
         rightLines]
        self.wedgeDots = [topDots,
         bottomDots,
         leftDots,
         rightDots]
        self.wedgeBg = [topBg,
         bottomBg,
         leftBg,
         rightBg]

    def ShowDashes(self):
        for rotation in (0,
         pi / 2,
         pi,
         3 * pi / 2):
            BlueDash(parent=self.dashesCont, align=uiconst.CENTERLEFT, rotation=pi / 4 + rotation, rotationCenter=(0.0, 0.5))

    def HideDashes(self):
        self.dashesCont.Flush()

    def OnNewJobData(self, jobData):
        self.oldJobData = self.jobData
        self.jobData = jobData
        self.skillSprite.OnNewJobData(jobData)
        self.containerME.OnNewJobData(jobData)
        self.containerTE.OnNewJobData(jobData)
        self.iconCont.OnNewJobData(jobData)
        self.ReconstructGauge()
        if self.gauge:
            self.gauge.OnNewJobData(jobData)
        self.UpdateState()
        self.AnimEntry()
        self.numericInputTimer = None

    def OnIndustryWndMouseWheel(self, *args):
        if not self.jobData:
            return
        self.runsEdit.OnMouseWheel()
        if uicore.registry.GetFocus() != self.runsEdit:
            uicore.registry.SetFocus(self.runsEdit)

    def OnIndustryWndClick(self):
        if not self.jobData:
            return
        uicore.registry.SetFocus(self.runsEdit)


class BlueprintGaugeCircular(GaugeCircular):
    default_opacity = 0.0

    def ApplyAttributes(self, attributes):
        GaugeCircular.ApplyAttributes(self, attributes)
        self.jobData = attributes.jobData

    def OnNewJobData(self, jobData):
        self.jobData = jobData

    def OnMouseEnter(self, *args):
        GaugeCircular.OnMouseEnter(self, *args)
        sm.GetService('audio').SendUIEvent('ind_circleMouseEnter')

    def SetValue(self, value, *args):
        GaugeCircular.SetValue(self, value, *args)
        sm.GetService('audio').SetGlobalRTPC('ind_circleValue', 100 * value)

    def OnMouseExit(self, *args):
        GaugeCircular.OnMouseExit(self, *args)
        sm.GetService('audio').SendUIEvent('ind_circleMouseExit')

    def OnDropData(self, dragSource, dragData):
        sm.ScatterEvent('OnIndustryDropData', dragSource, dragData)

    def GetTooltipPosition(self, *args):
        l, t, w, h = self.GetAbsolute()
        offset = 43
        return (l,
         t - offset,
         w,
         h + 2 * offset)

    def GetTooltipPointer(self):
        return uiconst.POINT_BOTTOM_2


class BlueDash(Transform):
    default_width = 100
    default_height = 6

    def ApplyAttributes(self, attributes):
        Transform.ApplyAttributes(self, attributes)
        self.sprite1 = Sprite(parent=self, align=uiconst.CENTERLEFT, pos=(0, 0, 49, 6), texturePath='res:/UI/Texture/classes/Industry/Center/blueDash.png')
        self.sprite2 = Sprite(parent=self, align=uiconst.CENTERLEFT, pos=(0, 0, 49, 6), texturePath='res:/UI/Texture/classes/Industry/Center/blueDash.png')
        self.sprite3 = Sprite(parent=self, align=uiconst.CENTERLEFT, pos=(0, 0, 49, 6), texturePath='res:/UI/Texture/classes/Industry/Center/blueDash.png')
        uthread.new(self.Animate)

    def Animate(self):
        x0 = self.default_width
        x1 = 0
        k = 0.22
        while not self.destroyed:
            for i in xrange(2):
                for j, obj in enumerate((self.sprite1, self.sprite2, self.sprite3)):
                    uicore.animations.MorphScalar(obj, 'left', x0, x1, duration=k * (j + 1))
                    uicore.animations.FadeTo(obj, 0.0, 1.5, duration=2 * k, curveType=uiconst.ANIM_WAVE)

                blue.synchro.SleepWallclock(4 * k * 1000)

            blue.synchro.SleepWallclock(1000)


class BlueprintSingleLineEdit(SingleLineEditInteger):

    def Disable(self):
        super(BlueprintSingleLineEdit, self).Disable()
        self.textLabel.left = 0
        self.textLabel.align = uiconst.CENTER
        self.SetReadOnly(True)

    def Enable(self):
        super(BlueprintSingleLineEdit, self).Enable()
        self.textLabel.left = self.textLeftMargin
        self.textLabel.align = uiconst.CENTERLEFT
        self.SetReadOnly(False)


class BlueprintItemIcon(ItemIcon):

    def ApplyAttributes(self, attributes):
        ItemIcon.ApplyAttributes(self, attributes)
        self.jobData = attributes.jobData

    def GetMenu(self):
        bpData = self.jobData.blueprint
        m = GetMenuService().GetMenuFromItemIDTypeID(self.jobData.blueprintID, bpData.blueprintTypeID, includeMarketDetails=True).filter(['UI/Industry/ViewInIndustry'])
        m.append((localization.GetByLabel('UI/Industry/RemoveBlueprint'), self.RemoveBlueprint))
        if session.role & ROLE_PROGRAMMER:
            m.insert(0, ('GM: Give me these materials', self._GiveMeMaterials))
        return m

    def _GiveMeMaterials(self):
        materials = [ (material.typeID, material.quantity) for material in self.jobData.materials ]
        sm.GetService('info').DoCreateMaterials(materials)

    def RemoveBlueprint(self):
        sm.ScatterEvent('OnIndustryRemoveBlueprint')

    def OnNewJobData(self, jobData):
        self.jobData = jobData

    def OnMouseEnter(self, *args):
        ItemIcon.OnMouseEnter(self, *args)
        PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def OnDropData(self, dragSource, dragData):
        sm.ScatterEvent('OnIndustryDropData', dragSource, dragData)

    def GetHint(self):
        hint = ItemIcon.GetHint(self)
        if hint:
            return hint.strip()
