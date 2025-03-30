#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\jobsStrip.py
import math
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.themeColored import FrameThemeColored
from eve.client.script.ui.shared.industry import industryUIConst
from eve.client.script.ui.shared.industry.activitySelectionButtons import ActivitySelectionButtons
import carbonui.const as uiconst
from carbonui.primitives.gradientSprite import GradientSprite
from eve.client.script.ui.shared.industry.submitButton import SubmitButton
import telemetry
from eve.client.script.ui.shared.industry.views.errorFrame import ErrorFrame
from eve.client.script.ui.shared.industry.views.industryTooltips import JobsSummaryTooltipPanel, AllJobsSummaryTooltipPanel
import industry
import localization
from carbonui.uicore import uicore

class JobsStrip(Container):
    default_name = 'JobsStrip'
    default_height = 50

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        callback = attributes.callback
        submit = attributes.submit
        self.oldJobData = None
        self.jobData = attributes.jobData
        self.jobsSummary = JobsSummary(parent=self, align=uiconst.CENTERLEFT, left=10)
        self.allJobsSummary = AllJobsSummary(parent=self, align=uiconst.CENTERLEFT, left=10)
        self.activitySelectionButtons = ActivitySelectionButtons(parent=self, align=uiconst.CENTER, callback=callback, width=248, height=38)
        self.submitBtn = SubmitButton(parent=self, align=uiconst.CENTERRIGHT, fixedheight=30, fixedwidth=120, left=7)
        GradientSprite(bgParent=self, rotation=-math.pi / 2, rgbData=[(0, (0.3, 0.3, 0.3))], alphaData=[(0, 0.3), (1.0, 0.05)])
        FrameThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIBASECONTRAST)
        self.UpdateState()

    @telemetry.ZONE_METHOD
    def OnNewJobData(self, jobData):
        self.jobData = jobData
        self.activitySelectionButtons.OnNewJobData(jobData)
        self.submitBtn.OnNewJobData(jobData)
        if jobData:
            self.jobData.on_updated.connect(self.UpdateState)
            self.jobsSummary.OnNewJobData(jobData)
        self.UpdateState()

    def UpdateState(self, *args):
        if self.jobData:
            self.submitBtn.Show()
            self.jobsSummary.Show()
            self.allJobsSummary.Hide()
        else:
            self.submitBtn.Hide()
            self.jobsSummary.Hide()
            self.allJobsSummary.Show()


class JobsSummary(LayoutGrid):
    default_columns = 2
    default_state = uiconst.UI_NORMAL
    __notifyevents__ = ['OnIndustrySlotsUpdated']

    def ApplyAttributes(self, attributes):
        LayoutGrid.ApplyAttributes(self, attributes)
        self.activityType = None
        self.jobData = None
        self.countCaption = Label(color=Color.GRAY, fontsize=fontconst.EVE_SMALL_FONTSIZE, top=2)
        self.AddCell(self.countCaption, cellPadding=(0, 0, 5, 0))
        self.countLabel = Label()
        cell = self.AddCell(self.countLabel, cellPadding=(5, 0, 5, 3))
        self.slotsErrorFrame = ErrorFrame(parent=cell, align=uiconst.TOALL, state=uiconst.UI_DISABLED, padBottom=3)
        label = Label(text=localization.GetByLabel('UI/Industry/ControlRange'), color=Color.GRAY, fontsize=fontconst.EVE_SMALL_FONTSIZE, top=2)
        self.AddCell(label, cellPadding=(0, 0, 5, 0))
        self.rangeLabel = Label()
        cell = self.AddCell(self.rangeLabel, cellPadding=(5, 0, 5, 0))
        self.rangeErrorFrame = ErrorFrame(parent=cell, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        sm.RegisterNotify(self)

    def OnIndustrySlotsUpdated(self, *args):
        if self.jobData:
            self.UpdateState()

    def OnNewJobData(self, jobData):
        self.jobData = jobData
        if self.jobData:
            self.jobData.on_updated.connect(self.UpdateState)
        self.UpdateState()

    def UpdateState(self, *args):
        activityID = self.jobData.activityID
        activityType = industryUIConst.GetActivityType(activityID)
        changed = self.activityType != activityType
        self.activityType = activityType
        if changed:
            uicore.animations.FadeOut(self, sleep=True, duration=0.1)
            if self.activityType == industryUIConst.TYPE_MANUFACTURING:
                self.countCaption.text = localization.GetByLabel('UI/Industry/ManufacturingJobs')
            elif self.activityType == industryUIConst.TYPE_REACTION:
                self.countCaption.text = localization.GetByLabel('UI/Industry/ReactionJobs')
            elif self.activityType == industryUIConst.TYPE_SCIENCE:
                self.countCaption.text = localization.GetByLabel('UI/Industry/ScienceJobs')
        c = industryUIConst.GetActivityColor(activityID)
        color = Color.RGBtoHex(*c)
        usedSlots = sm.GetService('industrySvc').GetJobCountForActivity(activityID)
        usedSlotsText = '-' if usedSlots is None else usedSlots
        self.countLabel.text = '%s / <color=%s>%s</color>' % (usedSlotsText, color, self.jobData.max_slots)
        skillLabel = industryUIConst.GetControlRangeLabel(self.jobData.max_distance)
        self.rangeLabel.text = '<color=%s>%s' % (color, skillLabel)
        if changed:
            uicore.animations.FadeIn(self, duration=0.3)
        if self.jobData and self.jobData.HasError(industry.Error.SLOTS_FULL):
            self.slotsErrorFrame.Show()
        else:
            self.slotsErrorFrame.Hide()
        if self.jobData and self.jobData.HasError(industry.Error.FACILITY_DISTANCE):
            self.rangeErrorFrame.Show()
        else:
            self.rangeErrorFrame.Hide()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        JobsSummaryTooltipPanel(self.jobData, tooltipPanel)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)


class AllJobsSummary(LayoutGrid):
    default_columns = 2
    default_state = uiconst.UI_NORMAL
    __notifyevents__ = ['OnIndustrySlotsUpdated', 'OnSkillsChanged']

    def ApplyAttributes(self, attributes):
        LayoutGrid.ApplyAttributes(self, attributes)
        captionCellPadding = (0, 0, 0, 0)
        countLabelCellPadding = (5, 0, 5, 0)
        self.manufacturingCountCaption = Label(color=Color.GRAY, fontsize=fontconst.EVE_SMALL_FONTSIZE, text=localization.GetByLabel('UI/Industry/ManufacturingJobs'))
        self.AddCell(self.manufacturingCountCaption, cellPadding=captionCellPadding)
        self.manufacturingCountLabel = Label(fontsize=fontconst.EVE_SMALL_FONTSIZE)
        cell = self.AddCell(self.manufacturingCountLabel, cellPadding=countLabelCellPadding)
        self.scienceCountCaption = Label(color=Color.GRAY, fontsize=fontconst.EVE_SMALL_FONTSIZE, text=localization.GetByLabel('UI/Industry/ScienceJobs'))
        self.AddCell(self.scienceCountCaption, cellPadding=captionCellPadding)
        self.scienceCountLabel = Label(fontsize=fontconst.EVE_SMALL_FONTSIZE)
        cell = self.AddCell(self.scienceCountLabel, cellPadding=countLabelCellPadding)
        self.reactionCountCaption = Label(color=Color.GRAY, fontsize=fontconst.EVE_SMALL_FONTSIZE, text=localization.GetByLabel('UI/Industry/ReactionJobs'))
        self.AddCell(self.reactionCountCaption, cellPadding=captionCellPadding)
        self.reactionCountLabel = Label(fontsize=fontconst.EVE_SMALL_FONTSIZE)
        cell = self.AddCell(self.reactionCountLabel, cellPadding=countLabelCellPadding)
        self.UpdateState()
        sm.RegisterNotify(self)

    def OnSkillsChanged(self, *args):
        self.UpdateState()

    def OnIndustrySlotsUpdated(self, *args):
        self.UpdateState()

    def UpdateState(self, *args):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        attributeValues = dogmaLocation.GetIndustryCharacterModifiers(session.charid)
        industrySvc = sm.GetService('industrySvc')
        for activityID, slotLimitAttributeID, countLabel in [(industry.MANUFACTURING, const.attributeManufactureSlotLimit, self.manufacturingCountLabel), (industry.RESEARCH_TIME, const.attributeMaxLaborotorySlots, self.scienceCountLabel), (industry.REACTION, const.attributeReactionSlotLimit, self.reactionCountLabel)]:
            usedSlots = industrySvc.GetJobCountForActivity(activityID)
            c = industryUIConst.GetActivityColor(activityID)
            color = Color.RGBtoHex(*c)
            maxSlots = int(attributeValues[slotLimitAttributeID])
            usedSlotsText = '-' if usedSlots is None else usedSlots
            countLabel.text = '%s / <color=%s>%s</color>' % (usedSlotsText, color, maxSlots)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        AllJobsSummaryTooltipPanel(tooltipPanel)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
