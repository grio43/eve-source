#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillQueuePanel\skillQueuePanelNew.py
import blue
import telemetry
import clonegrade
import evetypes
import expertSystems.client
import gametime
import inventorycommon.const as invconst
import localization
import textImporting.importSkillplanConst as importConst
import uthread
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.commonutils import GetAttrs
from carbonui import uiconst, TextDetail
from carbonui.control.button import Button
from carbonui.control.dragdrop import dragdata
from carbonui.control.scroll import Scroll
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from carbonui.util.various_unsorted import GetClipboardData
from characterskills import SKILLQUEUE_MAX_NUM_SKILLS
from characterskills.util import GetSPForLevelRaw
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveLabelLarge, EveCaptionLarge
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.shared.cloneGrade import cloneStateUtil
from eve.client.script.ui.shared.monetization.multiTrainingOverlay import MultiTrainingOverlay
from eve.client.script.ui.shared.neocom.skillConst import COLOR_SKILL_2, COLOR_TRAININGALLOWED, COLOR_TRAININGNOTALLOWED, COLOR_MOVE_INDICATOR
from eve.client.script.ui.shared.neocom.timelineContainer import TimelineContainer
from eve.client.script.ui.skillPlan import skillPlanUISignals
from eve.client.script.ui.skillPlan.skillPlanEditor.skillPlanDropIndicatorCont import SkillQueueDropIndicatorCont, IsMultiSkillEntryMove
from eve.client.script.ui.skillPlan.skillQueuePanel.skillImportingMsg import SkillImportStatusWindow
from eve.client.script.ui.skillPlan.skillQueuePanel.skillPurchaseOverlay import show_skill_purchase_overlay
from eve.client.script.ui.skillPlan.skillQueuePanel.skillQueueButtons import ExpertSystemIconButton, ApplySkillPointsButtonTooltip, BUTTON_SIZE, ICON_SIZE, SkillInjectorTooltip, AlphaInjectorTooltip, OmegaTrainingSpeedButton
from eve.client.script.ui.skillPlan.skillQueuePanel.skillQueueLastDropEntry import SkillQueueLastDropEntry
from eve.client.script.ui.skillPlan.skillQueuePanel.skillQueueSkillEntry import SkillQueueSkillEntry
from eve.client.script.ui.skilltrading.applySkillPointsWindow import ApplySkillPointsWindow
from eve.common.lib import appConst
from eveexceptions import UserError
from eveui import clipboard
from localization import GetByLabel
from textImporting.importSkillplan import SkillPlanImportingStatus
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
ACTION_ICON = 'res:/UI/Texture/classes/UtilMenu/BulletIcon.png'
QUEUEBAR_HEIGHT = 30
COLOR_BG = (0.2, 0.2, 0.2, 0.5)
FILTER_ALL = 0
FILTER_PARTIAL = 1
FILTER_EXCLUDELVL5 = 2
FITSINQUEUE_DEFAULT = 0
NORMAL_COLORS = [(1, 1, 1, 0.4), (1, 1, 1, 0.8)]

def ShowMultiTrainingMessageOrRaise(e):
    if not MultiTrainingOverlay.IsSuppressed():
        skillPlanUISignals.on_show_multi_training_msg()
        sm.ScatterEvent('OnShowMultiTrainingMessage')
    else:
        raise e


class SkillQueuePanelNew(Container):
    __notifyevents__ = ['OnSkillsChanged',
     'OnSkillQueueChanged',
     'OnSkillQueuePaused',
     'OnSkillQueueRefreshed',
     'OnFreeSkillPointsChanged_Local',
     'OnSubscriptionChanged',
     'OnSkillQueueModified']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.queueLastApplied = []
        self.isSaving = False
        self.isApplying = False
        self.skillTimer = None
        self.timelineCont = None
        self.updateThread = None
        self._isSkillPurchaseOverlayActive = False
        self.godma = sm.GetService('godma')
        self.skills = sm.GetService('skills')
        self.skillQueueSvc = sm.GetService('skillqueue')
        self.ConstructLayout()
        self.InitializeData()
        self.ReloadUpdateThread()
        sm.RegisterNotify(self)

    @telemetry.ZONE_METHOD
    def InitializeData(self, *args):
        self.UpdateTimeData()
        self.skillQueueSvc.BeginTransaction()
        self.queueLastApplied = self.skillQueueSvc.GetQueue()
        uthread.new(self.LoadQueue)
        self.UpdateFreeSkillPoints()
        self.UpdateApplySkillPointsButton()

    @telemetry.ZONE_METHOD
    def ConstructLayout(self):
        self.ConstructTopCont()
        self.ConstructSkillQueueBar()
        self.ConstructBottomCont()
        self.ConstructUnallocatedBanner()
        self.ConstructScroll()

    def ConstructUnallocatedBanner(self):
        self.unallocatedTextBanner = Container(name='unallocatedTextBanner', parent=self, align=uiconst.TOBOTTOM, height=40, bgColor=Color(*eveColor.SMOKE_BLUE).SetOpacity(0.2).GetRGBA())
        self.unallocatedText = EveLabelLarge(parent=self.unallocatedTextBanner, align=uiconst.CENTER)

    def ConstructBottomCont(self):
        self.bottomCont = Container(name='bottomCont', parent=self, align=uiconst.TOBOTTOM, height=56, padBottom=8)
        textCont = ContainerAutoSize(parent=self.bottomCont, align=uiconst.BOTTOMLEFT, width=300)
        self.timeLeftLabel = EveCaptionLarge(name='timeLeftLabel', parent=textCont, align=uiconst.TOBOTTOM, padTop=-2, top=-4)
        EveLabelLarge(parent=textCont, align=uiconst.TOBOTTOM, text=GetByLabel('UI/SkillPlan/TrainingTime'))
        uthread.new(self._UpdateTrainingTimeLabelThread)
        buttonIconCont = ContainerAutoSize(name='ButtonIconCont', parent=self.bottomCont, align=uiconst.BOTTOMRIGHT, height=BUTTON_SIZE)
        self._ConstructBottomContButtons(buttonIconCont)
        self.UpdatePausePlayButtonTexturePath()

    def _ConstructBottomContButtons(self, buttonIconCont):
        padLeft = 8
        self.omegaButton = OmegaTrainingSpeedButton(name='omegaButton', parent=buttonIconCont, align=uiconst.TORIGHT, iconSize=32, fixedwidth=60, padLeft=padLeft, texturePath='res:/UI/Texture/classes/Seasons/omega_32x32.png', label='2x')
        self.CheckDisplayOmegaButton()
        self.applySkillPointsButtonIcon = Button(name='ApplySkillPointsButtonIcon', parent=buttonIconCont, align=uiconst.TORIGHT, func=self.OnApplySkillPointsButton, iconSize=ICON_SIZE, padLeft=padLeft, uniqueUiName=pConst.UNIQUE_NAME_APPLY_SP_BTN)
        self.UpdateApplySkillPointsButton()
        if expertSystems.is_expert_systems_enabled():
            from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
            ExpertSystemIconButton(parent=buttonIconCont, align=uiconst.TORIGHT, padLeft=padLeft, iconSize=ICON_SIZE, func=CharacterSheetWindow.OpenExpertSystems, texturePath='res:/UI/Texture/classes/ExpertSystems/logo_simple_white_32.png')
        self.pausePlayButton = Button(parent=buttonIconCont, align=uiconst.TORIGHT, iconSize=20, func=self.StartOrStopTraining, padLeft=padLeft, uniqueUiName=pConst.UNIQUE_NAME_START_TRAINING_BTN)

    def UpdateApplySkillPointsButton(self):
        if self._CanApplySkillPoints():
            tooltipPanelClassInfo = ApplySkillPointsButtonTooltip(len(self.skillQueueSvc.GetQueue()), self.skills.GetFreeSkillPoints())
            texturePath = 'res:/UI/Texture/classes/SkillPlan/buttonIcons/plusIcon.png'
        elif cloneStateUtil.IsOmega():
            tooltipPanelClassInfo = SkillInjectorTooltip()
            texturePath = 'res:/UI/Texture/classes/skilltrading/marketSkillinjector.png'
        else:
            tooltipPanelClassInfo = AlphaInjectorTooltip()
            texturePath = 'res:/UI/Texture/classes/skilltrading/alphaSkillInjector.png'
        self.applySkillPointsButtonIcon.tooltipPanelClassInfo = tooltipPanelClassInfo
        self.applySkillPointsButtonIcon.texturePath = texturePath

    def OnApplySkillPointsButton(self, *args):
        if self._CanApplySkillPoints():
            ApplySkillPointsWindow.Open()
        elif cloneStateUtil.IsOmega():
            self.ShowInjectorInMarket()
        else:
            self.BuyAlphaInjector()

    def _CanApplySkillPoints(self):
        return len(self.skillQueueSvc.GetQueue()) > 0 and self.skills.GetFreeSkillPoints()

    def UpdatePausePlayButtonTexturePath(self):
        if self.skillQueueSvc.SkillInTraining():
            texturePath = 'res:/UI/Texture/classes/SkillPlan/buttonIcons/pauseIcon.png'
            hint = GetByLabel('UI/SkillPlan/PauseTraining')
        else:
            texturePath = 'res:/UI/Texture/classes/SkillPlan/buttonIcons/playIcon.png'
            hint = GetByLabel('UI/SkillPlan/ResumeTraining')
        self.pausePlayButton.texturePath = texturePath
        self.pausePlayButton.SetHint(hint)

    def _UpdateTrainingTimeLabelThread(self):
        while not self.destroyed:
            timeLeft, spLeft = self.skillQueueSvc.GetTrainingLengthOfQueue()
            if self.skillQueueSvc.SkillInTraining():
                self.timeLeftLabel.SetRGBA(*eveColor.WHITE)
                self.timeLeftLabel.text = self.GetTimeLeftText(timeLeft)
                self.timeLeftLabel.text = self.GetTimeLeftText(timeLeft)
                self.spLeftLabel.text = GetByLabel('UI/SkillPlan/SpLeftInQueue', spLeft=spLeft)
            elif not self.skillQueueSvc.GetQueue():
                self.timeLeftLabel.SetRGBA(*eveColor.WHITE)
                self.timeLeftLabel.text = '-'
                self.spLeftLabel.text = '-'
            else:
                self.timeLeftLabel.SetRGBA(*eveColor.HOT_RED)
                self.timeLeftLabel.text = GetByLabel('UI/SkillPlan/TrainingPaused')
                self.spLeftLabel.text = GetByLabel('UI/SkillPlan/SpLeftInQueue', spLeft=spLeft)
            blue.synchro.SleepWallclock(500)

    def GetTimeLeftText(self, timeLeft):
        if session.languageID == 'DE':
            if timeLeft >= gametime.DAY:
                return localization.formatters.FormatTimeIntervalShortWritten(long(timeLeft), showFrom='day', showTo='hour')
            elif timeLeft > gametime.HOUR:
                return localization.formatters.FormatTimeIntervalShortWritten(long(timeLeft), showFrom='hour', showTo='minute')
            else:
                return localization.formatters.FormatTimeIntervalShortWritten(long(timeLeft), showFrom='minute', showTo='second')
        else:
            if timeLeft >= gametime.DAY:
                return localization.formatters.FormatTimeIntervalShortWritten(long(timeLeft), showFrom='day', showTo='minute')
            return localization.formatters.FormatTimeIntervalShortWritten(long(timeLeft), showFrom='hour', showTo='second')

    def ShowInjectorInMarket(self):
        sm.StartService('marketutils').ShowMarketDetails(invconst.typeSkillInjector, None)
        PlaySound(uiconst.SOUND_BUTTON_CLICK)

    def BuyAlphaInjector(self):
        sm.GetService('vgsService').OpenStore(typeIds=[invconst.typeAlphaTrainingInjector])

    def ConstructTopCont(self):
        self.topCont = Container(name='topCont', parent=self, align=uiconst.TOTOP, height=26)
        self.captionLabel = EveCaptionLarge(parent=self.topCont, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/TrainingQueue'))
        self.captionLabel.LoadTooltipPanel = self.LoadCaptionLabelTooltipPanel
        UtilMenu(menuAlign=uiconst.TOPLEFT, parent=self.topCont, align=uiconst.CENTERRIGHT, texturePath='res:/UI/Texture/Icons/77_32_49.png', pos=(0, 0, 24, 24), GetUtilMenu=self.GetUtilMenu, iconSize=24)

    def LoadCaptionLabelTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.AddMediumHeader(text=GetByLabel('UI/SkillPlan/SkillQueueCounterHeader'))
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/SkillPlan/SkillQueueCounterDescription', numMax=SKILLQUEUE_MAX_NUM_SKILLS), wrapWidth=300)

    def UpdateCaptionLabelText(self, numSkills):
        text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/TrainingQueue')
        text += ' <color=%s>%s<fontsize=12>/%s</fontsize></color>' % (eveColor.LED_GREY_HEX, numSkills, SKILLQUEUE_MAX_NUM_SKILLS)
        self.captionLabel.text = text

    def ConstructScroll(self):
        self.dropIndicatorCont = SkillQueueDropIndicatorCont(parent=self, align=uiconst.TOBOTTOM)
        self.dropIndicatorCont.OnDragEnter = self.OnDropContDragEnter
        self.dropIndicatorCont.OnDropData = self.OnDropContDropData
        self.scroll = Scroll(name='skillQueueScroll', parent=self, state=uiconst.UI_PICKCHILDREN, padding=(0, 12, 0, 0))
        self.scroll.HideBackground()
        self.scroll.sr.content.OnDropData = self.DoDropData
        self.scroll.sr.content.OnDragEnter = self.OnContentDragEnter
        self.scroll.sr.content.OnDragExit = self.OnContentDragExit
        self.scroll.sr.content.RemoveSkillFromQueue = self.RemoveSkillFromQueue
        self.scroll.OnDelete = self.RemoveSkillFromQueue
        self.changeIndicator = Line(parent=self.scroll, align=uiconst.TOBOTTOM, state=uiconst.UI_DISABLED, color=COLOR_SKILL_2, weight=2, padTop=-2, opacity=0.0, idx=0)

    def ConstructSkillQueueBar(self):
        skillQueueBar = Container(name='skillQueueBar', parent=self, align=uiconst.TOBOTTOM, height=12, padBottom=14)
        self.timelineCont = TimelineContainer(name='barCont', parent=skillQueueBar, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, height=12, bgColor=COLOR_BG, barHeight=12)
        self.timelineCont.OnMouseEnter = self.OnTimelineContMouseEnter
        self.timelineCont.OnMouseExit = self.OnTimelineContMouseExit
        self.belowBarCont = Container(name='belowBarCont', parent=skillQueueBar, align=uiconst.TOTOP, top=4, height=20, clipChildren=True)
        self.spLeftLabel = TextDetail(parent=self.belowBarCont, align=uiconst.TOTOP_NOPUSH, text='', top=1)
        self.timelineTickCont = Container(name='timelineTickCont', parent=self.belowBarCont, align=uiconst.TOTOP, height=20, opacity=0.0, top=1)

    def OnTimelineContMouseEnter(self, *args):
        animations.FadeIn(self.timelineTickCont)
        animations.FadeOut(self.spLeftLabel)
        self.DrawBars(animate=True)

    def OnTimelineContMouseExit(self):
        animations.FadeOut(self.timelineTickCont)
        animations.FadeIn(self.spLeftLabel, endVal=0.75)
        self.DrawBars(animate=True)

    def GetUtilMenu(self, menuParent):
        menuParent.AddIconEntry(icon='res:/UI/Texture/classes/UtilMenu/BulletIcon.png', text=GetByLabel('UI/SkillPlan/CopySkillsToClipboard'), callback=self.CopySkillsToClipboard)
        hint = GetByLabel('UI/SkillQueue/ImportSkillplanFormatHint', typeID=appConst.typeSpaceshipCommand)
        menuParent.AddIconEntry(icon=ACTION_ICON, text=GetByLabel('UI/SkillQueue/AddSkillPlanToEndOfQueue'), hint=hint, callback=self.ImportFromClipboard)
        menuParent.AddIconEntry(icon=ACTION_ICON, text=GetByLabel('UI/SkillQueue/ReplaceSkillsWithImportedPlan'), hint=hint, callback=self.ImportFromClipboardReplace)
        menuParent.AddIconEntry(icon=ACTION_ICON, text=GetByLabel('UI/SkillQueue/ClearSkillQueue'), callback=self.ClearSkillQueue)

    def CopySkillsToClipboard(self):
        skillsTxt = ''
        for typeID, level in self.skillQueueSvc.GetQueueAsRequirements():
            skillsTxt += '%s %s\n' % (evetypes.GetName(typeID), level)

        clipboard.set(skillsTxt)

    def ClearSkillQueue(self):
        self.DoRemove(None, self.scroll.GetNodes())

    def GrayButton(self, btn, gray = 1):
        inTraining = self.skillQueueSvc.SkillInTraining()
        if gray and not inTraining:
            btn.SetLabel(['<color=gray>', GetByLabel('UI/Commands/Pause')])
            btn.state = uiconst.UI_DISABLED
        else:
            btn.SetLabel(GetByLabel('UI/Commands/Pause'))
            btn.state = uiconst.UI_NORMAL

    def ApplySkillQueueIfNotActive(self, *args):
        self.ApplySkillQueue(activate=not self.IsTraining())

    def ApplySkillQueue(self, activate = True):
        beginNewTransaction = True
        try:
            self.SaveChanges(activate=activate)
        except UserError as e:
            if e.msg == 'UserAlreadyHasSkillInTraining':
                beginNewTransaction = False
                ShowMultiTrainingMessageOrRaise(e)
            elif e.msg == 'SkillInQueueRequiresOmegaCloneState':
                beginNewTransaction = False
                raise
            elif e.msg == 'SkillInQueueOverAlphaSpTrainingSize':
                message = localization.GetByLabel('UI/SkillQueue/AlphaTrainingLimitReached', limit=clonegrade.CLONE_STATE_ALPHA_MAX_TRAINING_SP)
                sm.ScatterEvent('OnShowAlphaTrainingMessage', message)
                skillPlanUISignals.on_show_alpha_training_msg(message)
                if activate:
                    self.ApplySkillQueue(activate=False)
                else:
                    beginNewTransaction = False
            else:
                raise
        finally:
            if beginNewTransaction and not self.skillQueueSvc.IsTransactionOpen():
                self.skillQueueSvc.BeginTransaction()

    def SaveChanges(self, activate = True):
        if self.isSaving:
            return
        self.isSaving = True
        try:
            queue = self.skillQueueSvc.GetQueue()
            self.skillQueueSvc.CommitTransaction(activate=activate)
            self.queueLastApplied = queue
        finally:
            self.isSaving = False

    def PauseTraining(self, *args):
        inTraining = self.skillQueueSvc.SkillInTraining()
        if inTraining:
            sm.StartService('skills').AbortTrain()
            self.ApplySkillQueue(activate=False)

    def Close(self, *args):
        Container.Close(self)
        uthread.new(self.SaveQueueOnClose)

    def SaveQueueOnClose(self):
        if self.isSaving:
            return
        queue = {x.queuePosition:(x.trainingTypeID, x.trainingToLevel) for x in self.skillQueueSvc.GetQueue()}
        queueLastApplied = {x.queuePosition:(x.trainingTypeID, x.trainingToLevel) for x in self.queueLastApplied}
        if queue != queueLastApplied:
            isActive = bool(self.skillQueueSvc.SkillInTraining())
            self.skillQueueSvc.CommitTransaction(activate=isActive)
        else:
            self.skillQueueSvc.RollbackTransaction()

    @telemetry.ZONE_METHOD
    def LoadQueue(self):
        self.queueTimer = 0
        mySkills = sm.StartService('skills').GetSkillsIncludingLapsed()
        queue = self.skillQueueSvc.GetQueue()
        allTrainingLengths = self.skillQueueSvc.GetAllTrainingLengths()
        scrolllist = []
        for traininigSkill in queue:
            skill = mySkills.get(traininigSkill.trainingTypeID, None)
            if skill is None:
                self.skillQueueSvc.RemoveSkillFromQueue(traininigSkill.trainingTypeID, traininigSkill.trainingToLevel)
                continue
            time = allTrainingLengths.get((traininigSkill.trainingTypeID, traininigSkill.trainingToLevel), [0, 0, 0])
            entry = self.GetRightEntry(traininigSkill.trainingTypeID, skill, traininigSkill.trainingToLevel, time[1], time[2])
            scrolllist.append(entry)

        if scrolllist:
            lastDropEntry = GetFromClass(SkillQueueLastDropEntry)
            scrolllist.append(lastDropEntry)
        self.scroll.Load(contentList=scrolllist, noContentHint=GetByLabel('UI/SkillQueue/NoSkillsInTraining'))
        self.UpdateTime()
        self.UpdateAlphaTrainingLimitFrames()
        self.UpdateCaptionLabelText(len(queue))

    def UpdateAlphaTrainingLimitFrames(self):
        cloneGradeSvc = sm.GetService('cloneGradeSvc')
        isOmega = cloneGradeSvc.IsOmega()
        nodes = self.scroll.GetNodes()
        accumulatedSkillPoints = 0
        totalSkillPoints = sm.GetService('skills').GetTotalSkillPointsForCharacterCached()
        for node in nodes:
            if not node.skill:
                continue
            if isOmega:
                if node.panel:
                    node.panel.HideDisabledFrame()
                continue
            skillPointsForPreviousLevel = GetSPForLevelRaw(node.skill.skillRank, node.trainToLevel - 1)
            skillPointsForThisLevel = GetSPForLevelRaw(node.skill.skillRank, node.trainToLevel)
            totalSkillPointsInThisLevel = skillPointsForThisLevel - skillPointsForPreviousLevel
            currentSkillPoints = self.skillQueueSvc.GetEstimatedSkillPointsTrained(node.skill.typeID)
            skillPointsAlreadyTrainedThisLevel = max(currentSkillPoints - skillPointsForPreviousLevel, 0)
            addedSkillPoints = max(0, totalSkillPointsInThisLevel - skillPointsAlreadyTrainedThisLevel)
            accumulatedSkillPoints += addedSkillPoints
            if totalSkillPoints + accumulatedSkillPoints > clonegrade.CLONE_STATE_ALPHA_MAX_TRAINING_SP:
                node.disabledForTraining = True
            elif sm.GetService('cloneGradeSvc').GetMaxSkillLevel(node.skill.typeID) < node.trainToLevel:
                node.disabledForTraining = True
            else:
                node.disabledForTraining = False
            if node.panel:
                if node.disabledForTraining:
                    node.panel.ShowDisabledFrame()
                else:
                    node.panel.HideDisabledFrame()

    def UpdateActiveSkillFlashAnimation(self):
        isTraining = self.skillQueueSvc.SkillInTraining() is not None
        nodes = self.scroll.GetNodes()
        for i, node in enumerate(nodes):
            if not node.panel or isinstance(node.panel, SkillQueueLastDropEntry):
                continue
            if i == 0 and isTraining:
                node.panel.StartFlashAnimation()
            else:
                node.panel.StopFlashAnimation()

    @telemetry.ZONE_METHOD
    def GetRightEntry(self, typeID, skill, trainToLevel, timeLeft, isAccelerated):
        skill = self.skills.GetSkillIncludingLapsed(typeID)
        isTrained = skill is not None
        skillInTraining = self.skillQueueSvc.SkillInTraining()
        inTraining = skillInTraining is not None and skillInTraining.typeID == typeID
        return GetFromClass(SkillQueueSkillEntry, {'invtype': typeID,
         'skill': skill,
         'trained': isTrained,
         'inQueue': 1,
         'trainToLevel': trainToLevel,
         'currentLevel': skill.trainedSkillLevel,
         'timeLeft': timeLeft,
         'skillID': typeID,
         'inTraining': [0, 1][inTraining],
         'isAccelerated': isAccelerated,
         'RemoveFromQueue': self.EntryRemoveFromQueue})

    def EntryRemoveFromQueue(self, x):
        self.DoRemove(None, [x])

    def UpdateTime(self):
        self.UpdateTimeData()
        self.UpdateSkillQueueBar()

    @telemetry.ZONE_METHOD
    def UpdateTimeData(self):
        self.queueEnds = self.skillQueueSvc.GetTrainingEndTimeOfQueue()
        self.queueTimeLeft = self.queueEnds - blue.os.GetWallclockTime()
        self.allTrainingLengths = self.skillQueueSvc.GetAllTrainingLengths()
        self.lasttime = blue.os.GetWallclockTime()

    def ReloadUpdateThread(self):
        if self.updateThread:
            self.updateThread.kill()
        self.updateThread = uthread.new(self.UpdateThread)

    @telemetry.ZONE_METHOD
    def UpdateThread(self, *args):
        while True:
            blue.synchro.SleepWallclock(1000)
            if self.destroyed:
                break
            self._Update()

    def _Update(self):
        inTraining = self.skillQueueSvc.SkillInTraining()
        now = blue.os.GetWallclockTime()
        lasttime = self.lasttime or now
        diff = now - lasttime
        queueEnds = self.queueEnds
        timeLeft = self.queueTimeLeft
        if queueEnds is not None and queueEnds >= now and timeLeft is not None:
            if inTraining and self.skillQueueSvc.FindInQueue(inTraining.typeID, inTraining.trainedSkillLevel + 1) is not None:
                timeLeft = timeLeft - diff
                self.queueTimeLeft = timeLeft
            else:
                queueEnds = self.queueEnds + diff
                self.queueEnds = queueEnds
            self.lasttime = now
            self.UpdateSkillQueueBar()

    def UpdateSkillQueueBar(self):
        self.DrawBars()
        self.DrawTimelineTicks()

    @telemetry.ZONE_METHOD
    def DrawBars(self, animate = False):
        self.timelineCont.FlushLine()
        offset = 0.0
        queue = self.skillQueueSvc.GetQueue()
        entries = self.scroll.GetNodes()
        unallocatedPoints = sm.GetService('skills').GetFreeSkillPoints()
        unallocatedWidth = 0.0
        timelineDuration = self.GetQueueDuration()
        inTraining = self.skillQueueSvc.SkillInTraining()
        actualEnd = self.skillQueueSvc.GetEndOfTraining(inTraining.typeID) if inTraining else None
        for i, (skill, entry) in enumerate(zip(queue, entries)):
            trainingID = (skill.trainingTypeID, skill.trainingToLevel)
            if trainingID not in self.allTrainingLengths:
                continue
            timeLeft = self.allTrainingLengths[trainingID][1]
            if inTraining and skill.trainingTypeID == inTraining.typeID and skill.trainingToLevel - 1 == inTraining.trainedSkillLevel:
                if actualEnd is not None:
                    timeLeft = float(actualEnd - blue.os.GetWallclockTime())
            width = timeLeft / timelineDuration
            segments = []
            if unallocatedPoints > 0:
                pointsTrained = skill.trainingDestinationSP - skill.trainingStartSP
                if unallocatedPoints >= pointsTrained:
                    segments.append((width, Color.WHITE))
                    unallocatedWidth += width
                else:
                    fractionCovered = min(1.0, unallocatedPoints / float(pointsTrained))
                    segments.append((width * fractionCovered, Color.WHITE))
                    segments.append((width * (1.0 - fractionCovered), NORMAL_COLORS[i % 2]))
                    unallocatedWidth += fractionCovered * width
                unallocatedPoints -= pointsTrained
            else:
                segments.append((width, NORMAL_COLORS[i % 2]))
            try:
                if entry.panel is not None:
                    if uicore.uilib.mouseOver == self.timelineCont:
                        entry.panel.DrawTimeline(offset, segments, animate)
                    else:
                        entry.panel.HideTimeline(animate)
            except AttributeError:
                pass

            for w, c in segments:
                color = NORMAL_COLORS[i % 2]
                self.timelineCont.AddSegment(w, color)

            offset += width

        self.timelineCont.SetDuration(timelineDuration)

    def DrawTimelineTicks(self):
        INTERVALS = [(appConst.HOUR,
          6 * appConst.HOUR,
          28,
          localization.formatters.TIME_CATEGORY_HOUR),
         (6 * appConst.HOUR,
          appConst.DAY,
          29,
          localization.formatters.TIME_CATEGORY_DAY),
         (appConst.DAY,
          appConst.WEEK,
          31,
          localization.formatters.TIME_CATEGORY_DAY),
         (appConst.WEEK,
          appConst.MONTH28,
          28,
          localization.formatters.TIME_CATEGORY_MONTH),
         (appConst.MONTH30,
          6 * appConst.MONTH30,
          25,
          localization.formatters.TIME_CATEGORY_MONTH),
         (appConst.MONTH30,
          appConst.YEAR360,
          999,
          localization.formatters.TIME_CATEGORY_YEAR)]
        for minorTick, majorTick, tickLimit, timeCategory in INTERVALS:
            queueDuration = self.GetQueueDuration()
            tickCount = queueDuration / float(minorTick)
            if tickCount > tickLimit:
                continue
            self.timelineTickCont.Flush()
            for i in xrange(1, int(tickCount) + 1):
                timeValue = i * minorTick
                isMajorTick = timeValue % majorTick == 0
                if not isMajorTick:
                    continue
                self.ConstructTimelineTick(i / tickCount, timeCategory, timeValue)

            break

    def ConstructTimelineTick(self, left, timeCategory, timeValue):
        cont = Container(parent=self.timelineTickCont, align=uiconst.TOPLEFT_PROP, left=left, width=1, height=1)
        Line(parent=cont, align=uiconst.TOPLEFT, weight=1, top=-1, width=1, height=5, color=COLOR_BG)
        text = localization.formatters.FormatTimeIntervalShortWritten(timeValue, showFrom=timeCategory, showTo=timeCategory)
        w, _ = EveLabelSmall.MeasureTextSize(text=text)
        EveLabelSmall(parent=cont, align=uiconst.RELATIVE, left=-0.5 * w, top=0, text=text, opacity=0.4)

    def GetQueueDuration(self):
        return max(self.queueTimeLeft, appConst.DAY + appConst.HOUR)

    def OnFreeSkillPointsChanged_Local(self):
        self.UpdateFreeSkillPoints()
        self.UpdateApplySkillPointsButton()

    def UpdateFreeSkillPoints(self):
        unallocatedPoints = sm.GetService('skills').GetFreeSkillPoints()
        if unallocatedPoints > 0:
            color = Color.RGBtoHex(*eveColor.CRYO_BLUE)
            text = GetByLabel('UI/SkillQueue/FreeSkillPointAmount', points=unallocatedPoints, color=color)
            self.unallocatedText.SetText(text)
            self.unallocatedTextBanner.display = True
        else:
            self.unallocatedTextBanner.display = False

    def AddSkillThroughSkillEntry(self, data, queue, idx = -1):
        if not data.Get('trained', True):
            self.HandleMissingSkill(data.skillID, idx)
            return False
        nextLevel = self.skillQueueSvc.FindNextLevel(data.skillID, None, queue)
        if nextLevel is None or nextLevel > 5:
            uicore.Message('CustomNotify', {'notify': GetByLabel('UI/SkillQueue/SkillFullyPlanned')})
            return False
        isCloneStateRestricted = sm.GetService('cloneGradeSvc').IsSkillLevelRestricted(data.skillID, nextLevel)
        if isCloneStateRestricted:
            uicore.Message('CustomNotify', {'notify': GetByLabel('UI/SkillQueue/SkillRequiresCloneStateUpgrade')})
            return False
        self.DoAddSkill(data.invtype, nextLevel, idx)
        return True

    def AddSkillsThroughOtherEntry(self, skillID, idx = None, queue = None, nextLevel = None):
        mySkills = sm.StartService('skills').GetSkillsIncludingLapsed()
        skill = mySkills.get(skillID, None)
        if skill is None:
            self.HandleMissingSkill(skillID, idx)
            return
        if nextLevel is None:
            if queue is None:
                queue = self.skillQueueSvc.GetQueue()
            nextLevel = self.skillQueueSvc.FindNextLevel(skillID, skill.trainedSkillLevel, queue)
        if nextLevel > 5:
            return
        self.DoAddSkill(skillID, nextLevel, idx)
        sm.ScatterEvent('OnSkillQueueRefreshed')
        return True

    def DoAddSkill(self, typeID, level, position = None):
        self.skillQueueSvc.AddSkillToQueue(typeID, level, position=position)

    def HandleMissingSkill(self, typeID, position = None):
        if self._isSkillPurchaseOverlayActive:
            return
        self._isSkillPurchaseOverlayActive = True
        controller = show_skill_purchase_overlay(self, typeID, position)
        controller.on_closed.connect(self._OnSkillPurchaseOverlayClosed)

    def _OnSkillPurchaseOverlayClosed(self):
        self._isSkillPurchaseOverlayActive = False

    def OnSkillQueueModified(self):
        self.LoadQueueAndAnimate()

    def LoadQueueAndAnimate(self):
        self.ReloadUpdateThread()
        animations.FadeTo(self.timelineCont, 1.0, 0.0, duration=0.2, sleep=True)
        self.LoadQueue()
        duration = 2.0
        animations.FadeTo(self.timelineCont, 0.0, 1.0, duration=duration, curveType=uiconst.ANIM_OVERSHOT5)

    def DoMove(self, data, newIdx, queueLength, movingBelow = 0, allEntries = None):
        skillPos = newIdx
        if newIdx == -1:
            skillPos = queueLength - 1
        if len(allEntries) == 1:
            self._DoMoveOneEntry(data, skillPos)
        else:
            self._DoMoveManyEntries(skillPos, queueLength, allEntries)

    def _DoMoveOneEntry(self, data, skillPos):
        trainToLevel = data.Get('trainToLevel', None)
        if data.skillID and trainToLevel:
            self.skillQueueSvc.MoveSkillToPosition(data.skillID, trainToLevel, skillPos)

    def _DoMoveManyEntries(self, skillPos, queueLength, allEntries):
        dataAbovePoint = [ x for x in allEntries if x.idx < skillPos ]
        dataBelowPoint = [ x for x in allEntries if x.idx >= skillPos ]
        reverseData = dataAbovePoint[:]
        reverseData.reverse()
        nextSkillPos = skillPos
        for eachData in reverseData:
            for testPos in xrange(nextSkillPos, 0, -1):
                if self.skillQueueSvc.CheckCanInsertSkillAtPosition(eachData.skillID, eachData.trainToLevel, testPos, check=True):
                    self.skillQueueSvc.MoveSkillToPosition(eachData.skillID, eachData.trainToLevel, testPos)
                    if nextSkillPos == testPos:
                        nextSkillPos -= 1
                    break

        for eachData in dataBelowPoint:
            for testPos in xrange(skillPos, queueLength):
                if self.skillQueueSvc.CheckCanInsertSkillAtPosition(eachData.skillID, eachData.trainToLevel, testPos, check=True):
                    self.skillQueueSvc.MoveSkillToPosition(eachData.skillID, eachData.trainToLevel, testPos)
                    if testPos == skillPos:
                        skillPos += 1
                    break

        uthread2.call_after_wallclocktime_delay(self.ReselectDraggedNodes, 0.3, allEntries)

    def ReselectDraggedNodes(self, allEntries):
        allDragged = {(x.skillID, x.Get('trainToLevel', None)) for x in allEntries}
        nodesToSelect = []
        for eachNode in self.scroll.GetNodes():
            if (eachNode.skillID, eachNode.Get('trainToLevel', None)) in allDragged:
                nodesToSelect.append(eachNode)

        self.scroll.SelectNodes(nodesToSelect)

    def RemoveSkillFromQueue(self, *args):
        selected = self.scroll.GetSelected()
        self.DoRemove(None, selected)

    def DoRemove(self, dragObj, entries, *args):
        entries.reverse()
        removeList = []
        for entry in entries:
            if entry.__guid__ != 'listentry.SkillQueueSkillEntry':
                continue
            if not GetAttrs(entry, 'inQueue'):
                return
            removeList.append(entry)

        skills = [ (entry.invtype, entry.Get('trainToLevel', -1)) for entry in removeList ]
        self.skillQueueSvc.RemoveSkillsFromQueue(skills)
        self.LoadQueue()

    def OnContentDragEnter(self, dragObj, entries, *args):
        self.ShowPositionIndicator(entries)

    def ShowPositionIndicator(self, entries):
        color = self.GetIndicatorColor(entries)
        if not self.scroll.IsScrollbarVisible() and self.scroll.GetNodes():
            lastDropEntry = self.GetLastDropEntry()
            if lastDropEntry:
                lastDropEntry.ShowIndicator(color)
        else:
            self.changeIndicator.SetRGBA(*color)

    def GetIndicatorColor(self, entries):
        if IsMultiSkillEntryMove(entries):
            return COLOR_MOVE_INDICATOR
        try:
            allowedMove = self.skillQueueSvc.IsMoveAllowed(entries[0], None)
        except UserError:
            allowedMove = False

        if allowedMove:
            color = COLOR_TRAININGALLOWED
        elif self.skillQueueSvc.IsSkillEntry(entries[0]):
            color = COLOR_TRAININGNOTALLOWED
        else:
            color = (0, 0, 0, 0)
        return color

    def GetLastDropEntry(self):
        nodes = self.scroll.GetNodes()
        if nodes:
            return nodes[-1].panel

    def OnContentDragExit(self, *args):
        self.HidePositionIndicator()

    def HidePositionIndicator(self):
        self.changeIndicator.opacity = 0.0
        lastDropEntry = self.GetLastDropEntry()
        if lastDropEntry:
            lastDropEntry.HideIndicator()

    def OnDropContDragEnter(self, dragObject, entries):
        uthread2.StartTasklet(self.dropIndicatorCont.OnDragEnterFromParent, entries, self.scroll)

    def OnDropContDropData(self, dropObj, entries):
        if self.scroll.IsScrollbarVisible() and self.scroll.GetScrollProportion() >= 1.0:
            self.DoDropData(dropObj, entries)
        self.dropIndicatorCont.HideIndicator()

    def DoDropData(self, dragObj, entries, idx = -1):
        queue = self.skillQueueSvc.GetQueue()
        self.HidePositionIndicator()
        if not entries:
            return
        if idx == -1:
            idx = len(queue)
        data = entries[0]
        if isinstance(data, dragdata.TypeDragData) and evetypes.IsSkill(data.typeID):
            self.AddSkillsThroughOtherEntry(data.typeID, idx, queue)
        elif data.__guid__ == 'listentry.SkillQueueSkillEntry':
            if data.Get('inQueue', None) and not uicore.uilib.Key(uiconst.VK_SHIFT):
                movingBelow = 0
                if idx > data.idx:
                    movingBelow = 1
                newIdx = max(0, idx)
                if data.skillID:
                    self.DoMove(data, newIdx, len(queue), movingBelow, allEntries=entries)
            else:
                self.AddSkillThroughSkillEntry(data, queue, idx)
        elif data.__guid__ == 'listentry.SkillEntry':
            self.AddSkillThroughSkillEntry(data, queue, idx)
        elif data.__guid__ in ('xtriui.InvItem', 'listentry.InvItem'):
            category = GetAttrs(data, 'rec', 'categoryID')
            if category == appConst.categorySkill:
                sm.StartService('skills').InjectSkillIntoBrain([data.item])
                blue.pyos.synchro.SleepWallclock(500)
                self.AddSkillsThroughOtherEntry(data.item.typeID, idx, queue, nextLevel=1)
        elif data.__guid__ == 'listentry.SkillTreeEntry':
            self.AddSkillsThroughOtherEntry(data.typeID, idx, queue)
        elif data.__guid__ in ('uicls.GenericDraggableForTypeID', 'listentry.GenericMarketItem'):
            categoryID = evetypes.GetCategoryID(data.typeID)
            if categoryID == appConst.categorySkill:
                self.AddSkillsThroughOtherEntry(data.typeID, idx, queue)

    def UpdateQueuedSkillsRemoveButton(self):
        for node in self.scroll.GetNodes():
            if node.__guid__ != 'listentry.SkillQueueSkillEntry':
                continue
            if node.panel:
                node.panel.UpdateRemoveButton()

    def ChangeTimesOnEntriesInQueue(self):
        timesForSkillsInQueue = self.skillQueueSvc.GetAllTrainingLengths()
        for node in self.scroll.GetNodes():
            if node.__guid__ != 'listentry.SkillQueueSkillEntry':
                continue
            times = timesForSkillsInQueue.get((node.skillID, node.trainToLevel))
            if times:
                timeLeft, addedTime, isAccelerated = times
            else:
                addedTime = 0
                isAccelerated = False
            self.ChangeTimeOnSingleEntry(node, timeLeft=addedTime, isAccelerated=isAccelerated)

    def ChangeTimeOnSingleEntry(self, node, timeLeft = 0, isAccelerated = False):
        timeHasChanged = long(node.timeLeft) != long(timeLeft)
        node.timeLeft = timeLeft
        node.isAccelerated = isAccelerated
        if node.panel and timeHasChanged:
            if timeLeft > 0:
                timeLeftText = localization.formatters.FormatTimeIntervalShortWritten(long(timeLeft), showFrom='day', showTo='second')
            else:
                timeLeftText = ''
            node.panel.timeLeftText.SetText(timeLeftText)
            node.panel.UpdateAcceleratedMarker()
            node.panel.FillBoxes(node.skill.trainedSkillLevel, node.trainToLevel)

    def ReloadEntriesIfNeeded(self):
        self.ChangeTimesOnEntriesInQueue()
        self.UpdateQueuedSkillsRemoveButton()

    def OnDropData(self, *args):
        self.DoDropData(*args)

    def OnDragEnter(self, *args):
        self.OnContentDragEnter(*args)

    def OnDragExit(self, *args):
        self.OnContentDragExit(*args)

    def OnSkillsChanged(self, *args):
        self.queueLastApplied = self.skillQueueSvc.GetServerQueue()
        self.skillQueueSvc.PrimeCache(force=True)
        self.UpdatePausePlayButtonTexturePath()
        self.UpdateApplySkillPointsButton()
        self.LoadQueueAndAnimate()

    def OnSubscriptionChanged(self, *args):
        self.OnSkillsChanged()
        self.CheckDisplayOmegaButton()

    def CheckDisplayOmegaButton(self):
        self.omegaButton.display = not sm.GetService('cloneGradeSvc').IsOmega()

    def StartOrStopTraining(self, *args):
        if self.skillQueueSvc.SkillInTraining():
            self.PauseTraining()
        else:
            self.ApplySkillQueue()
            PlaySound('skill_training_start_play')

    def SaveSkillQueue(self):
        isTraining = bool(self.skillQueueSvc.SkillInTraining())
        self.ApplySkillQueue(activate=isTraining)

    def OnSkillQueueChanged(self):
        self.queueLastApplied = self.skillQueueSvc.GetQueue()
        self.OnSkillsChanged()

    def OnSkillQueueRefreshed(self):
        self.OnSkillQueueChanged()

    def OnSkillQueuePaused(self):
        self.OnSkillQueueChanged()

    def ImportFromClipboardReplace(self):
        return self.ImportFromClipboard(clearQueue=1)

    def ImportFromClipboard(self, clearQueue = 0, *args):
        sm.GetService('loading').ProgressWnd(GetByLabel('UI/SkillQueue/ImportingSkillPlan'), '', 1, 6)
        uthread.new(self.ImportFromClipboard_thread, clearQueue)

    def ImportFromClipboard_thread(self, clearQueue = 0, *args):
        importingText = GetByLabel('UI/SkillQueue/ImportingSkillPlan')
        skillplanImporter = self.skillQueueSvc.GetSkillPlanImporter()
        sm.GetService('loading').ProgressWnd(importingText, '', 2, 6)
        skillPlanText = GetClipboardData()
        skillList, failedLines = skillplanImporter.GetSkillsToAdd(skillPlanText, clearQueue)
        if clearQueue:
            nodes = self.scroll.GetNodes()
            self.DoRemove(None, nodes)
        importingStatus = SkillPlanImportingStatus()
        sm.GetService('loading').ProgressWnd(importingText, '', 3, 6)
        skills = sm.GetService('skills').GetSkills()
        for typeID, skillLevel, why in skillList:
            blue.pyos.BeNice()
            if importingStatus.TooManySkillsAdded() and why == importConst.MANUAL_ADD:
                importingStatus.AddToFailed(typeID, skillLevel, importConst.FAILED_TOO_MANY_SKILLS)
                continue
            lowerLevelFailReason = importingStatus.ReasonForFailingForLowerLevel(typeID, skillLevel)
            if lowerLevelFailReason is not None and lowerLevelFailReason != importConst.FAILED_SKILL_IN_QUEUE:
                importingStatus.AddToFailed(typeID, skillLevel, lowerLevelFailReason)
                continue
            skill = skills.get(typeID, None)
            if skill is None or skill.trainedSkillLevel is None:
                importingStatus.AddToFailed(typeID, skillLevel, importConst.FAILED_SKILL_NOT_INJECTED)
                continue
            if skill.trainedSkillLevel >= skillLevel:
                importingStatus.AddToFailed(typeID, skillLevel, importConst.FAILED_PREVIOUSLY_TRAINED)
                continue
            nextLevel = self.skillQueueSvc.FindNextLevel(typeID, skill.trainedSkillLevel, self.skillQueueSvc.skillQueue)
            if sm.GetService('cloneGradeSvc').IsSkillLevelRestricted(typeID, skillLevel):
                importingStatus.AddToFailed(typeID, skillLevel, importConst.FAILED_OMEGA_RESTRICTION)
                continue
            if nextLevel < skillLevel:
                importingStatus.AddToFailed(typeID, skillLevel, importConst.FAILED_INCORRECT_ORDER)
                continue
            try:
                self.DoAddSkill(typeID, skillLevel)
            except UserError as userError:
                importingStatus.AddToFailed(typeID, skillLevel, userError.msg)
            except Exception as e:
                importingStatus.AddToFailed(typeID, skillLevel, 'unknown')
            else:
                importingStatus.IncreaseAddedCount()

        sm.GetService('loading').ProgressWnd(importingText, '', 5, 6)
        self.UpdateTime()
        self.ReloadEntriesIfNeeded()
        sm.GetService('loading').ProgressWnd(importingText, '', 6, 6)
        wnd = SkillImportStatusWindow.Open()
        wnd.LoadInitialImportingStatus(importingStatus, failedLines)

    def ApplySkillPoints(self, *args):
        if self.isApplying:
            return
        self.isApplying = True
        try:
            isTraining = self.IsTraining()
            self.SaveChanges(activate=isTraining)
            self.skillQueueSvc.ApplyFreeSkillPointsToQueue()
            self.skillQueueSvc.BeginTransaction()
            PlaySound('st_allocate_skillpoints_play')
        finally:
            self.isApplying = False

    def IsTraining(self):
        return self.skillQueueSvc.SkillInTraining() is not None
