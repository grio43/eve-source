#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\selectedPlan\selectedSkillPlanContainer.py
import math
import blue
import eveicon
import threadutils
import uthread2
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.button.group import ButtonGroup
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.shared.careerPortal import careerConst
from eve.client.script.ui.skillPlan import skillPlanUISignals
from eve.client.script.ui.skillPlan.contents.skillPlanContents import SkillPlanContents
from eve.client.script.ui.skillPlan.controls.milestoneIndicatorHeader import MilestoneIndicatorHeader
from eve.client.script.ui.skillPlan.milestone.skillPlanProgressIndicator import SkillPlanProgressIndicator
from eve.client.script.ui.skillPlan.selectedPlan.skillPlanLockedCont import SkillPlanLockedCont
from eve.client.script.ui.skillPlan.skillPlanConst import HINT_BY_CAREER_ID, HINT_BY_FACTION_ID, ICON_BY_FACTION_ID
from eve.common.script.util.notificationconst import notificationTypeSkillsAddedFromSkillPlan
from eveui import Sprite
from localization import GetByLabel
from notifications.common.notification import Notification
from skills.skillplan import skillPlanSignals
from skills.skillplan.loggers.skillPlanLogger import log_certified_skill_plan_track_plan_clicked, log_certified_skill_plan_train_all_clicked
from skills.skillplan.skillPlanDragData import SkillPlanDragData
from skills.skillplan.skillPlanService import GetSkillPlanSvc
from uihighlighting.uniqueNameConst import GetUniqueSkillPlanBtn
COLOR_FRAME = eveColor.LED_GREY
PAD = 16
TOP_CONT_HEIGHT = 32
BUTTONS_HEIGHT = 32
BUTTONS_WIDTH = 32
MIDDLE_BUTTONS_WIDTH = 32
MIDDLE_BUTTONS_ICON_SIZE = 20
MIDDLE_BUTTONS_PAD = 4
WIDTH_OVERVIEW_CONT = 0.4
MINWIDTH_OVERVIEW_CONT = 350

def OpenSkillPlanWindow():
    from eve.client.script.ui.skillPlan.skillPlanDockablePanel import SkillPlanDockablePanel
    skill_plans_window = SkillPlanDockablePanel.Open()
    if skill_plans_window and not skill_plans_window.IsFullscreen():
        skill_plans_window.Maximize()


class PlanCompletedBanner(Container):
    default_height = 42

    def ApplyAttributes(self, attributes):
        super(PlanCompletedBanner, self).ApplyAttributes(attributes)
        leftCont = Container(name='leftcont', parent=self, align=uiconst.TOLEFT, width=42, bgColor=eveColor.COPPER_OXIDE_GREEN)
        Sprite(name='completedIcon', parent=leftCont, align=uiconst.CENTER, pos=(0, 0, 34, 34), texturePath='res:/UI/Texture/classes/SkillPlan/completedIcon.png')
        mainCont = Container(name='mainCont', parent=self, bgColor=eveColor.WHITE, padLeft=10)
        EveLabelLarge(parent=mainCont, align=uiconst.CENTERLEFT, text=GetByLabel('UI/SkillPlan/SkillPlanCompleted'), color=eveColor.BLACK, left=14, shadowOffset=(0, 0))


class SelectedSkillPlanContainer(Container):
    __notifyevents__ = ['OnSubscriptionChanged',
     'OnSkillsAvailable',
     'OnSkillQueueChanged',
     'OnSkillsChanged']

    def ApplyAttributes(self, attributes):
        super(SelectedSkillPlanContainer, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        skillPlan = attributes.skillPlan
        self.skillPlan = None
        self.skillsVisible = False
        self.updateComponentsThrottleFunc = None
        skillPlanSignals.on_saved.connect(self.OnSkillPlanSaved)
        skillPlanSignals.on_tracked_plan_changed.connect(self.OnTrackedPlanChanged)
        self.mainCont = Container(name='mainCont', parent=self)
        self.bgCont = Container(name='bgCont', parent=self, align=uiconst.TOLEFT_PROP, width=WIDTH_OVERVIEW_CONT, minWidth=MINWIDTH_OVERVIEW_CONT)
        self.ConstructCloseButton()
        self.ConstructBackground()
        self.overviewCont = Container(name='overviewCont', parent=self.mainCont, align=uiconst.TOLEFT_PROP, width=WIDTH_OVERVIEW_CONT, minWidth=MINWIDTH_OVERVIEW_CONT, padding=(50, 10, 50, 50))
        self.contentsCont = Container(name='contentsCont', parent=self.mainCont, align=uiconst.TOALL, padding=(0, 50, 50, 50))
        self.ConstructOverviewCont()
        self.ConstructContentsCont()
        self.SetSkillPlan(skillPlan)

    def ConstructBackground(self):
        Frame(parent=self.bgCont, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Stroke.png', color=COLOR_FRAME, cornerSize=11)
        Frame(parent=self.bgCont, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', color=(0, 0, 0, 0.92), cornerSize=11)
        Sprite(name='leftWing', parent=self.bgCont, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/SkillPlan/skillPlanWing.png', pos=(-8, 215, 8, 86), color=COLOR_FRAME)
        Sprite(name='rightWing', parent=self.bgCont, align=uiconst.TOPRIGHT, texturePath='res:/UI/Texture/classes/SkillPlan/skillPlanWing.png', pos=(-8, 215, 8, 86), color=COLOR_FRAME, rotation=math.pi)

    def ConstructOverviewCont(self):
        Sprite(name='skillPlanIcon', parent=self.overviewCont, align=uiconst.TOPLEFT, pos=(-36, 6, 20, 20), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/SkillPlan/skillPlanIcon.png')
        self.headerCont = MilestoneIndicatorHeader(parent=self.overviewCont, align=uiconst.TOTOP, padBottom=6)
        self.ConstructIconCont()
        self.skillPlanProgressIndicator = SkillPlanProgressIndicator(parent=self.overviewCont, align=uiconst.TOTOP_PROP, height=0.48)
        self.ConstructMiddleButtonsCont()
        self.toggleContentsButton = Button(name='toggleContentsButton', parent=self.overviewCont, align=uiconst.TOTOP, texturePath='res:/UI/Texture/Shared/DarkStyle/buttonInProgressArrow.png', label=GetByLabel('UI/SkillPlan/ShowSkillPlanContents'), iconSize=12, padTop=16, func=self.OnToggleContents)
        self.completedBanner = PlanCompletedBanner(parent=self.overviewCont, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, padTop=16)
        descriptionScroll = ScrollContainer(parent=self.overviewCont, align=uiconst.TOALL, padTop=16)
        self.descriptionLabel = EveLabelLarge(name='descriptionLabel', parent=descriptionScroll, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, linkStyle=uiconst.LINKSTYLE_REGULAR)
        self.ConstructBottomButtonsCont()
        self.UpdateComponents()

    def ConstructIconCont(self):
        iconCont = Container(name='iconCont', parent=self.overviewCont, align=uiconst.TOTOP_NOPUSH, height=32, padTop=6)
        self.factionIcon = Sprite(name='factionIcon', parent=iconCont, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, pos=(0, 0, 32, 32), opacity=0.5)
        self.factionIcon.LoadTooltipPanel = self.LoadFactionTooltip
        self.careerPathIcon = Sprite(name='careerPathIcon', parent=iconCont, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL, pos=(0, 0, 32, 32), opacity=0.5)
        self.careerPathIcon.LoadTooltipPanel = self.LoadCareerTooltip

    def ConstructCloseButton(self):
        ButtonIcon(name='closeButton', parent=self.bgCont, align=uiconst.TOPRIGHT, pos=(8, 8, 16, 16), texturePath='res:/UI/Texture/Shared/DarkStyle/windowClose.png', func=self.OnCloseButton)

    def OnCloseButton(self, *args):
        skillPlanUISignals.on_close_button()

    def ConstructMiddleButtonsCont(self):
        self.middleButtonsCont = Container(parent=self.overviewCont, name='buttonsCont', align=uiconst.TOTOP, height=MIDDLE_BUTTONS_WIDTH, padTop=16)
        self.controlButtonsCont = ButtonGroup(parent=self.middleButtonsCont, align=uiconst.TOLEFT)
        self.editButton = Button(name='editButton', parent=self.controlButtonsCont, align=uiconst.TOLEFT, texturePath='res:/UI/Texture/classes/SkillPlan/buttonIcons/editPlanIcon.png', func=self.OnEditButton, iconSize=MIDDLE_BUTTONS_ICON_SIZE)
        self.editButton.GetHint = self.GetEditHint
        self.saveButton = Button(name='saveButton', parent=self.controlButtonsCont, align=uiconst.TOLEFT, texturePath='res:/UI/Texture/classes/SkillPlan/buttonIcons/savePlanIcon.png', hint=GetByLabel('UI/SkillPlan/SavePlan'), func=self.SaveSkillPlan, iconSize=MIDDLE_BUTTONS_ICON_SIZE)
        self.shareButton = Button(name='shareButton', parent=self.controlButtonsCont, align=uiconst.TOLEFT, texturePath='res:/UI/Texture/classes/SkillPlan/buttonIcons/sharePlanIcon.png', hint=GetByLabel('UI/SkillPlan/SharePlan'), iconSize=MIDDLE_BUTTONS_ICON_SIZE)
        self.shareButton.GetDragData = self.GetShareButtonDragData
        self.deleteButton = Button(name='deleteButton', parent=self.controlButtonsCont, align=uiconst.TOLEFT, texturePath='res:/UI/Texture/classes/SkillPlan/buttonIcons/delete.png', func=self.OnDeleteButton, iconSize=MIDDLE_BUTTONS_ICON_SIZE)
        self.deleteButton.GetHint = self.GetDeleteHint
        self.trackButton = Button(name='trackButton', parent=self.middleButtonsCont, align=uiconst.TORIGHT, texturePath=eveicon.look_at, func=self.OnTrackButton, iconSize=MIDDLE_BUTTONS_ICON_SIZE, padLeft=MIDDLE_BUTTONS_PAD)
        self.trackButton.GetHint = self.GetTrackHint
        self.saveButton.Disable()
        self.shareButton.Disable()
        self.trackButton.Disable()
        self.deleteButton.Disable()
        self.shareButton.MakeDragObject()

    def GetDeleteHint(self):
        return GetByLabel('UI/SkillPlan/DeletePlan')

    def GetEditHint(self):
        if self.skillPlan.IsEditable():
            return GetByLabel('UI/SkillPlan/EditPlan')
        else:
            return GetByLabel('UI/SkillPlan/SaveAndEditPlan')

    def GetTrackHint(self):
        if not self.skillPlan.IsTrackable():
            return GetByLabel('UI/SkillPlan/SaveAnTrackPlan')
        elif GetSkillPlanSvc().IsSkillPlanTracked(self.skillPlan.GetID()):
            return GetByLabel('UI/SkillPlan/UntrackPlanHint')
        else:
            return GetByLabel('UI/SkillPlan/TrackPlanHint')

    def SaveSkillPlan(self, *args):
        if self.skillPlan:
            skillPlanUISignals.on_selected(self.GetSkillPlanCopy())

    def GetShareButtonDragData(self, *args):
        return SkillPlanDragData(self.skillPlan.GetID(), self.skillPlan.GetName(), self.skillPlan.GetOwnerID())

    def ConstructBottomButtonsCont(self):
        self.bottomButtonsCont = ContainerAutoSize(parent=self.overviewCont, name='bottomButtonsCont', align=uiconst.TOBOTTOM, padTop=6, idx=0)
        lockedContPar = Container(name='lockedContPar', parent=self.bottomButtonsCont, align=uiconst.TOTOP, height=60)
        self.lockedCont = SkillPlanLockedCont(parent=lockedContPar, align=uiconst.CENTERTOP)
        self.lockedCont.onMissingSkillsButtonSignal.connect(self.OnToggleContents)
        self.startTrainingBtn = Button(parent=self.bottomButtonsCont, name='startTrainingButton', align=uiconst.TOTOP, label=GetByLabel('UI/SkillPlan/StartTraining'), iconSize=12, func=self.TrainSkills, padTop=5, analyticID='AddAllSkillsToTrainingQueue')

    def ConstructContentsCont(self):
        self.skillPlanContents = SkillPlanContents(parent=self.contentsCont, name='skillPlanContentsPropCont', align=uiconst.TOLEFT_PROP, width=0.0, opacity=0.0, padding=(10, 18, 0, 0))

    def OnToggleContents(self, *args):
        if self.skillsVisible:
            self.HideSkills()
        else:
            self.ShowSkills()
        self.mainCont.GetAbsolutePosition()
        skillPlanUISignals.on_skill_collapse_changing(self.skillPlan, self.skillsVisible, self)

    def HideSkills(self):
        if self.skillsVisible:
            duration = 0.2
            animations.MorphScalar(self.skillPlanContents, 'width', startVal=self.skillPlanContents.width, endVal=0.0, duration=duration)
            animations.MorphScalar(self.bgCont, 'width', self.bgCont.width, WIDTH_OVERVIEW_CONT, duration=duration)
            animations.FadeTo(self.skillPlanContents, 0.1, 0.0, duration=duration)
            self.skillsVisible = False
            self.skillPlanContents.state = uiconst.UI_DISABLED
            self.UpdateToggleContentsBtn(isSkillPlanVisible=False)

    def ShowSkills(self, *args):
        if not self.skillsVisible:
            uthread2.start_tasklet(self.skillPlanContents.SetSkillPlan, self.skillPlan)
            duration = 0.2
            animations.MorphScalar(self.skillPlanContents, 'width', startVal=self.skillPlanContents.width, endVal=1.0, duration=duration)
            animations.MorphScalar(self.bgCont, 'width', self.bgCont.width, 1.0, duration=duration)
            animations.FadeTo(self.skillPlanContents, 0.0, 1.0, duration=0.4)
            self.skillsVisible = True
            self.skillPlanContents.state = uiconst.UI_PICKCHILDREN
            self.UpdateToggleContentsBtn(isSkillPlanVisible=True)

    def UpdateToggleContentsBtn(self, isSkillPlanVisible):
        if isSkillPlanVisible:
            self.toggleContentsButton.texturePath = 'res:/UI/Texture/Shared/DarkStyle/buttonInProgressArrowRight.png'
            self.toggleContentsButton.SetLabel(GetByLabel('UI/SkillPlan/HideSkillPlanContents'))
        else:
            self.toggleContentsButton.texturePath = 'res:/UI/Texture/Shared/DarkStyle/buttonInProgressArrow.png'
            self.toggleContentsButton.SetLabel(GetByLabel('UI/SkillPlan/ShowSkillPlanContents'))

    def IsCurrentSkillPlan(self, skillPlanID):
        return self.skillPlan and skillPlanID == self.skillPlan.GetID()

    def OnSkillPlanSaved(self, skillPlan):
        if self.IsCurrentSkillPlan(skillPlan.GetID()):
            self.skillPlanContents.SetSkillPlan(self.skillPlan)
            self.UpdateInformation()

    def OnTrackedPlanChanged(self, untrackedPlan, _):
        if untrackedPlan and self.IsCurrentSkillPlan(untrackedPlan.GetID()):
            self.UpdateComponents()

    def SetSkillPlan(self, skillPlan):
        if self.skillPlan:
            animations.FadeTo(self.overviewCont, self.overviewCont.opacity, 0.0, 0.1)
        else:
            self.overviewCont.opacity = 0.0
        self.skillPlan = skillPlan
        self.lockedCont.SetSkillPlan(self.skillPlan)
        self.skillPlanProgressIndicator.SetSkillPlan(self.skillPlan)
        self.headerCont.SetCaption(skillPlan.GetTypeName())
        animations.FadeTo(self.overviewCont, self.overviewCont.opacity, 1.0, 0.1)
        self.saveButton.Enable()
        self.shareButton.Enable()
        self.trackButton.Enable()
        self.deleteButton.Enable()
        self.UpdateInformation()
        self.UpdateComponents()
        self.UpdateUniquUiNames()

    def UpdateUniquUiNames(self):
        try:
            planID = self.skillPlan.GetID().int
            self.toggleContentsButton.uniqueUiName = GetUniqueSkillPlanBtn(planID, 0)
            self.startTrainingBtn.uniqueUiName = GetUniqueSkillPlanBtn(planID, 1)
        except StandardError:
            pass

    def UpdateComponents(self):
        self.UpdateStartTrainingButton()
        self.UpdateTrackedButton()
        self.UpdateLockedCont()
        if self.skillsVisible and self.skillPlanContents:
            self.skillPlanContents.UpdateSkillsMissingBanner()
            self.skillPlanContents.UpdateOmegaBanner()
        if self.skillPlan and self.skillPlan.IsCompleted():
            self.completedBanner.Show()
            self.bottomButtonsCont.Hide()
        else:
            self.completedBanner.Hide()
            self.bottomButtonsCont.Show()

    def UpdateLockedCont(self):
        if not self.skillPlan:
            return
        self.lockedCont.Update()

    def UpdateStartTrainingButton(self):
        if not self.skillPlan or not self.skillPlan.IsTrainable():
            self.startTrainingBtn.Disable()
            self.startTrainingBtn.SetHint(GetByLabel('UI/SkillPlan/StartTrainingLockedHint'))
        elif self.skillPlan.IsQueuedOrTrained():
            self.startTrainingBtn.Disable()
            self.startTrainingBtn.SetHint(GetByLabel('UI/SkillPlan/StartTrainingNothingToTrainHint'))
        else:
            self.startTrainingBtn.Enable()
            self.startTrainingBtn.SetHint(GetByLabel('UI/SkillPlan/StartTrainingHint'))

    def UpdateTrackedButton(self):
        if not self.skillPlan:
            return
        if GetSkillPlanSvc().IsSkillPlanTracked(self.skillPlan.GetID()):
            texturePath = eveicon.camera_untrack
        else:
            texturePath = eveicon.look_at
        self.trackButton.texturePath = texturePath

    def UpdateInformation(self):
        if not self.skillPlan:
            return
        self.headerCont.SetSkillPlanName(self.skillPlan.GetName())
        self.descriptionLabel.text = self.skillPlan.GetDescription()
        self.UpdateFactionIcon()
        self.UpdateCareerPathIcon()
        if self.skillPlan.IsEditable():
            self.editButton.display = True
            self.deleteButton.display = True
        else:
            self.editButton.display = False
            self.deleteButton.display = False

    def UpdateCareerPathIcon(self):
        careerPathID = self.skillPlan.GetCareerPathID()
        if careerPathID:
            self.careerPathIcon.display = True
            self.careerPathIcon.texturePath = careerConst.CAREERS_32_SIZES[careerPathID]
        else:
            self.careerPathIcon.display = False

    def UpdateFactionIcon(self):
        factionID = self.skillPlan.GetFactionID()
        if factionID:
            self.factionIcon.Show()
            self.factionIcon.texturePath = ICON_BY_FACTION_ID[factionID]
        else:
            self.factionIcon.Hide()

    def OnTrackButton(self, *args):
        if not self.skillPlan:
            return
        if not self.skillPlan.IsTrackable():
            self._CreateCopySelectAndTrack()
        else:
            self._ToggleTracked(self.skillPlan.GetID())

    def _CreateCopySelectAndTrack(self):
        skillPlan = self.GetSkillPlanCopy()
        skillPlanUISignals.on_selected(skillPlan)
        GetSkillPlanSvc().SetTrackedSkillPlanID(skillPlan.GetID())

    def _ToggleTracked(self, skillPlanID):
        if GetSkillPlanSvc().IsSkillPlanTracked(skillPlanID):
            GetSkillPlanSvc().SetTrackedSkillPlanID(None)
        else:
            GetSkillPlanSvc().SetTrackedSkillPlanID(skillPlanID)
            if self.skillPlan.IsCertified():
                log_certified_skill_plan_track_plan_clicked(skillPlanID)
        self.UpdateTrackedButton()

    def GetSkillPlanCopy(self):
        uthread2.start_tasklet(eve.Message, 'SkillPlanCopied')
        return GetSkillPlanSvc().SaveCopyOfPlanAsPersonalSkillPlan(self.skillPlan)

    def OnEditButton(self, *args):
        skillPlan = self.skillPlan if self.skillPlan.IsEditable() else self.GetSkillPlanCopy()
        skillPlanUISignals.on_edit_button(skillPlan)

    def OnDeleteButton(self, *args):
        self.deleteButton.Disable()
        try:
            skillPlanUISignals.on_delete_button(self.skillPlan.GetID())
        finally:
            self.deleteButton.Enable()

    def TrainSkills(self, *args):
        if self.skillPlan:
            numSkillsAdded = self.skillPlan.AddToTrainingQueue()
            self._CheckSetCurrentSkillPlanAsTracked()
            self.UpdateTrackedButton()
            if numSkillsAdded > 0:
                skillPlanId = self.skillPlan.GetID()
                skillPlanName = self.skillPlan.GetName()
                self.TriggerSkillsAddedNotification(numSkillsAdded, skillPlanName)
                if self.skillPlan.IsCertified():
                    log_certified_skill_plan_train_all_clicked(skillPlanId)

    def _CheckSetCurrentSkillPlanAsTracked(self):
        trackedSkillplan = GetSkillPlanSvc().GetTrackedSkillPlan()
        skillPlan = self.skillPlan if self.skillPlan.IsTrackable() else self.GetSkillPlanCopy()
        if trackedSkillplan is None:
            GetSkillPlanSvc().SetTrackedSkillPlanID(skillPlan.GetID())
        elif trackedSkillplan.GetID() != skillPlan.GetID():
            if uicore.Message('AskTrackPlan', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                GetSkillPlanSvc().SetTrackedSkillPlanID(skillPlan.GetID())

    def OnSubscriptionChanged(self):
        self.UpdateComponents()

    def OnSkillsAvailable(self, typeIDs):
        self.UpdateComponents()

    def OnSkillQueueChanged(self):
        if self.destroyed:
            return
        self.UpdateComponents_throttled()

    def OnSkillsChanged(self, change):
        self.UpdateComponents()

    def UpdateComponents_throttled(self):
        if not getattr(self, 'updateComponentsThrottleFunc', None):

            @threadutils.throttled(1.0)
            def _UpdateComponents_throttled():
                self.UpdateComponents()

            self.updateComponentsThrottleFunc = _UpdateComponents_throttled
        self.updateComponentsThrottleFunc()

    @staticmethod
    def TriggerSkillsAddedNotification(numSkills, planName):
        notification = Notification.MakeSkillNotification(header=GetByLabel('UI/SkillPlan/SkillsAddedNotification', numSkills=numSkills, planName=planName), text='', created=blue.os.GetWallclockTime(), callBack=None, notificationType=notificationTypeSkillsAddedFromSkillPlan)
        sm.ScatterEvent('OnNewNotificationReceived', notification)

    def LoadFactionTooltip(self, tooltipPanel, *args):
        factionID = self.skillPlan.GetFactionID()
        if factionID:
            self._LoadTooltipForIcons(tooltipPanel, GetByLabel('UI/SkillPlan/SkillPlanFaction'), GetByLabel(HINT_BY_FACTION_ID[factionID]))

    def LoadCareerTooltip(self, tooltipPanel, *args):
        careerPath = self.skillPlan.GetCareerPathID()
        if careerPath:
            self._LoadTooltipForIcons(tooltipPanel, GetByLabel('UI/SkillPlan/SkillPlanCareerPath'), GetByLabel(HINT_BY_CAREER_ID[careerPath]))

    def _LoadTooltipForIcons(self, tooltipPanel, header, text):
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.columns = 1
        tooltipPanel.AddMediumHeader(text=header)
        tooltipPanel.AddLabelMedium(text=text, wrapWidth=300)


class LinkedSkillPlanContainer(SelectedSkillPlanContainer):

    def ApplyAttributes(self, attributes):
        super(LinkedSkillPlanContainer, self).ApplyAttributes(attributes)
        self.contentsCont.padRight = 6
        self.bgCont.width = 1.0
        showSkills = attributes.showSkills
        if showSkills:
            self._ShowSkillsPanel()
            self.skillsVisible = True
        else:
            self._HideSkillsPanel()

    def ConstructBackground(self):
        pass

    def ConstructCloseButton(self):
        pass

    def UpdateInformation(self):
        super(LinkedSkillPlanContainer, self).UpdateInformation()
        self.deleteButton.display = False

    def HideSkills(self):
        if self.skillsVisible:
            self._HideSkillsPanel()
            self.skillsVisible = False

    def _HideSkillsPanel(self):
        self.skillPlanContents.width = 0.0
        self.skillPlanContents.opacity = 0.0
        self.skillPlanContents.state = uiconst.UI_DISABLED
        self.overviewCont.width = 1.0
        self.UpdateToggleContentsBtn(isSkillPlanVisible=False)

    def ShowSkills(self, *args):
        if not self.skillsVisible:
            self._ShowSkillsPanel()
            self.skillsVisible = True

    def _ShowSkillsPanel(self):
        uthread2.start_tasklet(self.skillPlanContents.SetSkillPlan, self.skillPlan)
        self.skillPlanContents.width = 1.0
        self.skillPlanContents.opacity = 1.0
        self.skillPlanContents.state = uiconst.UI_PICKCHILDREN
        self.overviewCont.width = WIDTH_OVERVIEW_CONT
        self.UpdateToggleContentsBtn(isSkillPlanVisible=True)

    def OnTrackButton(self, *args):
        super(LinkedSkillPlanContainer, self).OnTrackButton(*args)
        if not self.skillPlan:
            return
        OpenSkillPlanWindow()

    def OnEditButton(self, *args):
        OpenSkillPlanWindow()
        super(LinkedSkillPlanContainer, self).OnEditButton(*args)

    def TrainSkills(self, *args):
        if self.skillPlan:
            OpenSkillPlanWindow()
        super(LinkedSkillPlanContainer, self).TrainSkills(*args)
