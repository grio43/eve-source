#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skilltrading\applySkillPointsWindow.py
import telemetry
import evetypes
import localization
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.format import IntToRoman
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst, fontconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from characterskills import GetSPForLevelRaw
from characterskills.util import GetLevelProgress
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.eveLabel import Label, EveLabelMedium
from carbonui.control.window import Window
from eve.client.script.ui.control.gauge import Gauge
from skills.skillConst import ICON_BY_GROUPID
from eve.client.script.ui.shared.neocom.skillConst import COLOR_UNALLOCATED_1
from gametime import GetWallclockTime

class ApplySkillPointsWindow(Window):
    default_windowID = 'ApplySkillPointsWindow'
    default_captionLabelPath = 'UI/SkillTrading/ApplySkillPointsWindowCaption'
    default_iconNum = 'res:/UI/Texture/WindowIcons/augmentations.png'
    default_width = 600
    default_height = 350
    default_fixedWidth = 600
    default_minSize = (600, 200)
    default_clipChildren = True
    default_isCollapseable = False
    default_isLightBackgroundConfigurable = False
    default_isStackable = False
    default_isLockable = False
    default_isOverlayable = False
    default_isMinimizable = False
    __notifyevents__ = ['OnClientEvent_SkillAddedToQueue',
     'OnClientEvent_SkillPrioritized',
     'OnClientEvent_SkillsRemovedFromQueue',
     'OnFreeSkillPointsChanged_Local',
     'OnSkillsChanged']

    def ApplyAttributes(self, attributes):
        super(ApplySkillPointsWindow, self).ApplyAttributes(attributes)
        self.skillTypeIDsAndLevels = attributes.get('skillTypeIDsAndLevels', None)
        self.mainArea = self.GetMainArea()
        self.skillQueueSvc = sm.GetService('skillqueue')
        self.skillSvc = sm.GetService('skills')
        self.skillEntriesByTypeIDAndLevel = {}
        self.isSaving = False
        self.isApplying = False
        self.isFinished = False
        self.skillPointsToBeUsed = 0
        self.SaveChanges(activate=self.IsTraining())
        self.ConstructLayout()
        self.PopulateScroll()
        self.SetDescriptionLabel()

    def CloseByUser(self, *args):
        if not self.skillQueueSvc.IsTransactionOpen():
            self.skillQueueSvc.BeginTransaction()
        super(ApplySkillPointsWindow, self).CloseByUser()

    def ConstructLayout(self):
        self.HideHeader()
        self.ConstructHeader()
        self.ConstructFooter()
        self.mainContainer = Container(name='MainContainer', parent=self.mainArea, padding=(4, 0, 4, 0))
        descriptionCont = Container(name='DescriptionCont', parent=self.mainContainer, align=uiconst.TOTOP, height=50)
        self.descriptionLabel = EveLabelMedium(name='Description', parent=descriptionCont, align=uiconst.CENTER)
        self.scrollContainer = ScrollContainer(name='SkillEntryScroll', parent=self.mainContainer, align=uiconst.TOALL)

    def ConstructHeader(self):
        headerContainer = Container(name='HeaderContainer', parent=self.mainArea, align=uiconst.TOTOP, height=35, bgColor=(0.133, 0.133, 0.141, 0.7), padding=(4, 4, 4, 0))
        iconContainer = Container(name='IconContainer', parent=headerContainer, align=uiconst.TOLEFT, width=32, height=32)
        Sprite(name='ApplySkillsIcon', parent=iconContainer, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=26, height=26, left=5, opacity=0.7, texturePath='res:/UI/Texture/classes/skilltrading/applySkillpoints.png')
        labelContainer = ContainerAutoSize(name='HeaderLabelContainer', parent=headerContainer, align=uiconst.TOLEFT, left=10)
        Label(name='ApplySkillsWindowCaption', parent=labelContainer, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/SkillTrading/ApplySkillPointsWindowCaption'))

    def ConstructFooter(self):
        footerContainer = Container(name='footerContainer', parent=self.mainArea, align=uiconst.TOBOTTOM, height=35, bgColor=(0.133, 0.133, 0.141, 0.7), padding=(4, 0, 4, 4))
        self.buttonGroup = ButtonGroup(name='buttonGroup', parent=footerContainer, align=uiconst.CENTER)
        self.buttonGroup.AddButton(localization.GetByLabel('UI/SkillTrading/ConfirmInjectionLabel'), self.ApplySkillPoints, uiName='confirm_skill_injection')
        self.buttonGroup.AddButton(localization.GetByLabel('UI/SkillTrading/CancelInjectionLabel'), self.CloseByUser, uiName='cancel_skill_injection')

    def SetDescriptionLabel(self):
        self.descriptionLabel.SetText(localization.GetByLabel('UI/SkillTrading/ApplySkillPointsDescription', color=Color.RGBtoHex(*COLOR_UNALLOCATED_1), points=self.skillPointsToBeUsed, amount=len(self.skillEntriesByTypeIDAndLevel)))

    def _GetPointsBySkillTypeID(self):
        handler = self.skillSvc.GetSkillHandler()
        if self.skillTypeIDsAndLevels is None:
            return handler.GetFreeSkillPointsAppliedToQueue()
        return handler.GetFreeSkillPointsAppliedToSkills(self.skillTypeIDsAndLevels)

    def _GetIterationSet(self):
        if self.skillTypeIDsAndLevels is None:
            return [ (s.trainingTypeID, s.trainingToLevel) for s in self.skillQueueSvc.GetQueue() ]
        return self.skillTypeIDsAndLevels

    def PopulateScroll(self):
        pointsBySkillTypeID = self._GetPointsBySkillTypeID()
        if not pointsBySkillTypeID:
            self.buttonGroup.buttons[0].Disable()
        else:
            self.buttonGroup.buttons[0].Enable()
        levelAndProgressBySkillTypeID = self.skillQueueSvc.GetSkillLevelAndProgressWithFreePoints(pointsBySkillTypeID)
        self.skillPointsToBeUsed = sum(pointsBySkillTypeID.itervalues())
        queue = self.skillQueueSvc.GetQueue()
        for skillID, skillLevel in self._GetIterationSet():
            levelReachedWithFreePoints, progressWithFreePoints = levelAndProgressBySkillTypeID[skillID] if skillID in levelAndProgressBySkillTypeID else (0, 0)
            if (skillID, skillLevel) in self.skillEntriesByTypeIDAndLevel:
                continue
            entry = ApplySkillPointsListEntry(parent=self.scrollContainer, align=uiconst.TOTOP, skillTypeID=skillID, progressWithFreePoints=progressWithFreePoints, levelReachedWithFreePoints=levelReachedWithFreePoints, trainingToLevel=skillLevel)
            self.skillEntriesByTypeIDAndLevel[skillID, skillLevel] = entry

    @telemetry.ZONE_METHOD
    def ApplySkillPoints(self, *args):
        if self.isApplying:
            return
        self.isApplying = True
        try:
            self.AnimateBars()
            isTraining = self.IsTraining()
            self.SaveChanges(activate=isTraining)
            if self.skillTypeIDsAndLevels is None:
                self.skillQueueSvc.ApplyFreeSkillPointsToQueue()
            else:
                self.skillQueueSvc.ApplyFreeSkillPointsToSkills(self.skillTypeIDsAndLevels)
            self.skillQueueSvc.BeginTransaction()
            PlaySound('st_allocate_skillpoints_play')
        finally:
            self.isApplying = False
            self.isFinished = True
            animations.FadeOut(self.buttonGroup, callback=self.FlushButtonsAndCreateCloseButton)

    def FlushButtonsAndCreateCloseButton(self):
        self.buttonGroup.FlushButtons()
        self.buttonGroup.AddButton(localization.GetByLabel('UI/SkillTrading/CloseInjectionLabel'), self.CloseByUser, uiName='close_skill_injection')
        animations.FadeIn(self.buttonGroup)

    def IsTraining(self):
        return self.skillQueueSvc.SkillInTraining() is not None

    def AnimateBars(self):
        for entry in self.skillEntriesByTypeIDAndLevel.values():
            entry.OnSkillPointsApplied()

    def Reconstruct(self):
        if self.isApplying:
            return
        if self.isFinished:
            return
        self.skillEntriesByTypeIDAndLevel.clear()
        self.scrollContainer.Flush()
        self.PopulateScroll()
        self.SetDescriptionLabel()

    def OnClientEvent_SkillAddedToQueue(self, skillTypeID, skillLevel):
        self.CloseByUser()

    def OnClientEvent_SkillsRemovedFromQueue(self, skillRequirements):
        self.CloseByUser()

    def OnClientEvent_SkillPrioritized(self, skillTypeID):
        self.CloseByUser()

    def OnFreeSkillPointsChanged_Local(self):
        if self.isApplying:
            return
        self.Reconstruct()

    def OnSkillsChanged(self, skillInfo):
        self.Reconstruct()

    def SaveChanges(self, activate = True):
        if self.isSaving:
            return
        self.isSaving = True
        try:
            self.skillQueueSvc.CommitTransaction(activate=activate)
        finally:
            self.isSaving = False


class ApplySkillPointsListEntry(SE_BaseClassCore):
    default_name = 'ApplySkillPointsListEntry'
    __guid__ = 'listentry.ApplySkillPointsListEntry'
    default_height = 55
    default_padTop = 10
    default_padLeft = 5
    default_padRight = 5
    default_complete_color = (0.239, 0.647, 0.278, 0.7)
    default_skillbook_green_color = (0.239, 0.647, 0.278, 1.0)

    def ApplyAttributes(self, attributes):
        super(ApplySkillPointsListEntry, self).ApplyAttributes(attributes)
        self.skillTypeID = attributes.skillTypeID
        self.levelReachedWithFreePoints = attributes.levelReachedWithFreePoints
        self.trainingToLevel = attributes.trainingToLevel
        self.progressWithFreePoints = attributes.progressWithFreePoints
        self.applyingSkillPoints = False
        self.skillSvc = sm.GetService('skills')
        self.skillQueueSvc = sm.GetService('skillqueue')
        self._progress = self.GetProgress()
        self.AdjustProgressWithFreePoints()
        self.ConstructLayout()
        self.SetSkillName()
        self.SetSkillGroupIcon()
        self.SetGaugesToCurrentProgress()
        self.Update()
        self.timeSavedUpdateThread = AutoTimer(method=self.Update, interval=1000)

    def AdjustProgressWithFreePoints(self):
        if self.levelReachedWithFreePoints >= self.trainingToLevel:
            self.progressWithFreePoints = 1.0
        elif self.levelReachedWithFreePoints + 1 < self.trainingToLevel:
            self.progressWithFreePoints = 0.0

    def ConstructLayout(self):
        iconCont = ContainerAutoSize(name='iconCont', parent=self, align=uiconst.TOLEFT)
        self.skillGroupIcon = Sprite(name='SkillGroupIcon', parent=iconCont, align=uiconst.CENTERTOP, width=32, height=32)
        skillBookIconCont = ContainerAutoSize(name='skillBookIconCont', parent=self, align=uiconst.TORIGHT)
        self.skillBookIcon = Sprite(parent=skillBookIconCont, align=uiconst.CENTERTOP, width=32, height=32, texturePath='res:/UI/Texture/Classes/Skills/doNotHave.png')
        middleCont = Container(name='MiddleContainer', parent=self, align=uiconst.TOALL, pos=(10, 0, 5, 0))
        gaugeCont = Container(name='GaugeContainer', parent=middleCont, align=uiconst.TOTOP, height=32)
        Frame(parent=gaugeCont, texturePath='res:/UI/Texture/classes/skilltrading/frame.png', cornerSize=3, opacity=0.5)
        self.skillName = Label(name='SkillName', parent=gaugeCont, align=uiconst.CENTER)
        self.alreadyTrainedGauge = Gauge(name='alreadyTrainedGauge', parent=gaugeCont, align=uiconst.TOTOP_NOPUSH, state=uiconst.UI_DISABLED, height=30, gaugeHeight=30, top=1, color=COLOR_UNALLOCATED_1, opacity=0.7, backgroundColor=(1.0, 1.0, 0.0, 0.0))
        self.aboutToBeTrainedGauge = Gauge(name='aboutToBeTrainedGauge', parent=gaugeCont, align=uiconst.TOTOP_NOPUSH, state=uiconst.UI_DISABLED, height=30, gaugeHeight=30, top=1, color=(0.21, 0.62, 0.74, 0.4), backgroundColor=(1.0, 1.0, 0.0, 0.0))
        timeSavedContainer = Container(name='timeSavedContainer', parent=middleCont, align=uiconst.TOALL, top=3)
        Frame(parent=timeSavedContainer, texturePath='res:/UI/Texture/classes/skilltrading/frame.png', cornerSize=3, opacity=0.5)
        self.timeSavedLabel = Label(name='timeSavedLabel', parent=timeSavedContainer, align=uiconst.CENTER, fontsize=fontconst.EVE_SMALL_FONTSIZE, opacity=0.7)
        self.percentageTrainedLabel = Label(name='percentageTrainedLabel', parent=timeSavedContainer, align=uiconst.CENTERRIGHT, fontsize=fontconst.EVE_SMALL_FONTSIZE, left=5)

    @property
    def progress(self):
        if self.applyingSkillPoints:
            return self._progress
        else:
            return self.GetProgress()

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.UpdateProgressLabel()

    def Close(self):
        self.timeSavedUpdateThread = None
        super(ApplySkillPointsListEntry, self).Close()

    def Update(self):
        self.UpdateLabels()
        self.UpdateAlreadyTrainedGauge()
        self.UpdateAboutToBeTrainedGauge()

    def SetSkillGroupIcon(self):
        self.skillGroupIcon.SetTexturePath(ICON_BY_GROUPID.get(evetypes.GetGroupID(self.skillTypeID)))

    def SetSkillName(self):
        self.skillName.SetText('%s %s' % (evetypes.GetName(self.skillTypeID), IntToRoman(self.trainingToLevel)))

    def UpdateAboutToBeTrainedGauge(self):
        self.aboutToBeTrainedGauge.SetValue(self.progressWithFreePoints, animate=False)

    def UpdateAlreadyTrainedGauge(self):
        self.alreadyTrainedGauge.SetValue(self.progress, animate=False)

    def SetGaugesToCurrentProgress(self):
        self.alreadyTrainedGauge.SetValue(self.progress, animate=False)
        self.aboutToBeTrainedGauge.SetValue(self.progress, animate=False)

    def GetProgress(self):
        progress = 0
        currentSkillLevel = self.skillSvc.MySkillLevel(self.skillTypeID)
        if currentSkillLevel == self.trainingToLevel - 1 and self.skillQueueSvc.FindInQueue(self.skillTypeID, self.trainingToLevel) == 0:
            currentPoints = self.skillQueueSvc.GetEstimatedSkillPointsTrained(self.skillTypeID)
            rank = self.skillSvc.GetSkillRank(self.skillTypeID)
            progress = GetLevelProgress(currentPoints, rank)
        return progress

    def OnSkillPointsApplied(self):
        self.applyingSkillPoints = True
        self.timeSavedUpdateThread = None
        self.AlignGauges()
        animations.MorphScalar(self, 'progress', startVal=self.progress, endVal=self.progressWithFreePoints, callback=lambda : setattr(self, 'progress', self.progressWithFreePoints))

    def AlignGauges(self):
        self.alreadyTrainedGauge.SetValueTimed(value=self.aboutToBeTrainedGauge.value, duration=0.6, callback=self.OnGaugeProgressSet)

    def OnGaugeProgressSet(self):
        if self.progressWithFreePoints == 1.0:
            self.alreadyTrainedGauge.SetColor(self.default_complete_color, animDuration=0.3)
            self.skillBookIcon.SetTexturePath('res:/UI/Texture/Classes/Skills/skillTrainingComplete.png')
            self.skillBookIcon.SetRGBA(*self.default_skillbook_green_color)
            animations.FadeTo(self.alreadyTrainedGauge, startVal=1.0, endVal=1.0, curveType=uiconst.ANIM_OVERSHOT3)

    def GetTimeSaved(self):
        skill = self.skillSvc.GetSkill(self.skillTypeID)
        trainingTimeCalculator = self.skillSvc.GetSkillTrainingTimeCalculator()
        skillPointsPreviousLevel = GetSPForLevelRaw(skill.skillRank, self.trainingToLevel - 1)
        _, totalTimeToTrain = trainingTimeCalculator.get_skill_points_and_time_to_train_given_existing_skill_points(self.skillTypeID, self.trainingToLevel, GetWallclockTime(), skillPointsPreviousLevel)
        return (self.progressWithFreePoints - self.progress) * totalTimeToTrain

    def UpdateLabels(self):
        self.UpdateTimeSavedLabel()
        self.UpdateProgressLabel()

    def UpdateTimeSavedLabel(self):
        text = localization.GetByLabel('UI/SkillTrading/EstimatedSkillTimeSaved', timeSaved=long(self.GetTimeSaved()))
        self.timeSavedLabel.SetText(text)

    def UpdateProgressLabel(self):
        text = localization.GetByLabel('UI/SkillTrading/SkillProgressLabel', progress=round(self.progress * 100, 1), progressWithFreePoints=round(self.progressWithFreePoints * 100, 1))
        self.percentageTrainedLabel.SetText(text)
