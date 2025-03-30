#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\recommendation\recommendationCont.py
import mathext
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import ButtonStyle, fontconst, uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.moreIcon import DescriptionIcon
from eve.client.script.ui.control.eveLabel import Label, EveLabelMedium
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
from eve.client.script.ui.shared.recommendation.const import ANOTHER_ACTIVE, COMPLETED, CURRENT_ACTIVE, NO_ACTIVE, NUM_SLOTS, REJECTED, Sounds, UPDATE_TIMEOUT_SECONDS
from eve.client.script.ui.shared.recommendation.uiConst import LIGHT_GREEN, LIGHT_YELLOW, MAIN_GREEN, MAIN_YELLOW
from localization import GetByLabel
ANIM_DURATION = 0.225
DECO_OPACITY = 0.5
ICON_FILL_OPACITY = 0.75

class RecommendationsCont(Container):
    default_align = uiconst.CENTERTOP
    default_width = 935
    default_height = 415

    def __init__(self, **kwargs):
        super(RecommendationsCont, self).__init__(**kwargs)
        self.allCards = []
        self.recommendationSvc = sm.GetService('recommendationSvc')
        uthread2.StartTasklet(self.ConstructLayout)

    def ConstructLayout(self):
        labelCont = ContainerAutoSize(parent=self, minHeight=65, align=uiconst.TOTOP)
        Label(name='header', parent=labelCont, align=uiconst.TOTOP, text='<center>%s</center>' % GetByLabel('UI/recommendations/OpportunitiesHeader'), fontsize=18, top=12)
        Label(name='text', parent=labelCont, align=uiconst.TOTOP, text='<center>%s</center>' % GetByLabel('UI/recommendations/OpportunitiesDescription'), fontsize=13)
        treatmentsCont = Container(parent=self)
        mainGrid = LayoutGrid(columns=3, parent=treatmentsCont, align=uiconst.CENTERTOP, cellSpacing=20)
        shouldBlinkBtn = self.recommendationSvc.ShouldBtnsBlink()
        self.treatmentCard1 = RecommendationCard(parent=mainGrid, slotIdx=0, shouldBlinkBtn=shouldBlinkBtn)
        self.treatmentCard2 = RecommendationCard(parent=mainGrid, slotIdx=1, shouldBlinkBtn=shouldBlinkBtn)
        self.treatmentCard3 = RecommendationCard(parent=mainGrid, slotIdx=2, shouldBlinkBtn=shouldBlinkBtn)
        self.allCards = [self.treatmentCard1, self.treatmentCard2, self.treatmentCard3]
        self.LoadCards()

    def LoadCards(self):
        if not self.recommendationSvc.HasRecommendations():
            self.recommendationSvc.RequestRecommendations(NUM_SLOTS, allowOld=True)
        for slotIdx, card in enumerate(self.allCards):
            self.LoadCard(card, slotIdx)

    def LoadCard(self, card, slotIdx):
        recommendationController = self.recommendationSvc.GetRecommendationControllerForSlot(slotIdx)
        if not recommendationController:
            return
        card.recommendationController = recommendationController
        card.LoadCard()


class RecommendationCard(Container):
    default_align = uiconst.CENTERLEFT
    default_height = 326
    default_width = 265
    __notifyevents__ = ['OnOperationDeactivatedUpdate', 'OnOperationCompleted']

    def __init__(self, **kwargs):
        super(RecommendationCard, self).__init__(**kwargs)
        self._recommendationController = None
        self.updateThread = None

    def ApplyAttributes(self, attributes):
        super(RecommendationCard, self).ApplyAttributes(attributes)
        self.slotIdx = attributes.slotIdx
        shouldBlinkBtn = attributes.shouldBlinkBtn
        self.ConstructLayout()
        if shouldBlinkBtn:
            uthread2.call_after_wallclocktime_delay(self.BlinkButton, 0.8)
        sm.RegisterNotify(self)

    def OnOperationDeactivatedUpdate(self):
        self.UpdateCard()

    def OnOperationCompleted(self, category_id, operation_id):
        if self.recommendationController and self.recommendationController.operationID == operation_id:
            self.UpdateCard()

    def ConstructLayout(self):
        self.mainContainer = Container(name='mainContainer', parent=self, align=uiconst.CENTER, width=self.default_width, height=self.default_height)
        Frame(bgParent=self.mainContainer, color=(1, 1, 1, 0.1))
        self.innerCard = Container(name='innerCard', parent=self.mainContainer, padding=1)
        self.backgroundTexture = Sprite(name='backgroundTexture', parent=self.mainContainer, align=uiconst.TOALL, padding=1, opacity=0.7)
        Fill(name='bgFill', parent=self.mainContainer, align=uiconst.TOALL, padding=1, color=(0, 0, 0, 1))
        self.topSection = TopSection(parent=self.innerCard)
        self.dismissButton = Button(name='dismissButton', parent=self.innerCard, align=uiconst.TOPRIGHT, texturePath='res:/UI/Texture/classes/Treatments/recycleIcon.png', iconSize=18, func=self.DismissRecommendation)
        Sprite(name='underlay', parent=self.innerCard, align=uiconst.TOPRIGHT, pos=(0, 0, 32, 32), texturePath='res:/UI/Texture/classes/Treatments/recycleButtonUnderlay.png', opacity=0.35 * DECO_OPACITY)
        self.actionBtn = Button(name='actionBtn', parent=self.innerCard, align=uiconst.CENTERBOTTOM, label=GetByLabel('UI/Agents/Dialogue/Buttons/AcceptMission'), top=8)
        self.textCont = TextCont(parent=self.innerCard, align=uiconst.TOBOTTOM)
        self.loadingWheel = LoadingWheel(name='loadingWheel', parent=self, align=uiconst.CENTER)
        self.loadingWheel.Hide()
        self.refreshButton = Button(name='refreshButton', parent=self, align=uiconst.CENTER, label=GetByLabel('UI/Commands/Refresh'), top=8, func=self.RequestRecommendation)
        self.refreshButton.Hide()

    def BlinkButton(self, numBlinks = 1):
        self.actionBtn.Blink(1, numBlinks)

    def QuitRecommendation(self, *args):
        if not self.recommendationController:
            return
        if not self.QuittingConfirmed():
            return
        self.AnimateClose()
        self.recommendationController.QuitRecommendation()

    @staticmethod
    def QuittingConfirmed():
        message = GetByLabel('UI/recommendations/QuitConfirmation')
        answer = eve.Message('AskAreYouSure', {'cons': message}, uiconst.YESNO)
        if answer == uiconst.ID_YES:
            return True
        return False

    def RequestRecommendation(self, *args):
        self.refreshButton.Hide()
        self.recommendationController.RequestRecommendations(1, allowOld=False)
        self.StartWaitingForUpdate()

    def DismissRecommendation(self, *args):
        if not self.recommendationController:
            return
        operationState = self.recommendationController.GetOperationState()
        if operationState == CURRENT_ACTIVE and not self.QuittingConfirmed():
            return
        self.AnimateClose()
        self.recommendationController.DismissRecommendation()

    def AnimateClose(self):
        animations.MorphScalar(self.mainContainer, 'opacity', startVal=self.opacity, endVal=0.0, duration=ANIM_DURATION, callback=self.StartWaitingForUpdate)

    def AnimateOpen(self):
        self.loadingWheel.Hide()
        animations.MorphScalar(self.mainContainer, 'opacity', startVal=self.mainContainer.opacity, endVal=1.0, duration=ANIM_DURATION, timeOffset=ANIM_DURATION, callback=self.mainContainer.Enable)

    def StartWaitingForUpdate(self):
        self.loadingWheel.Show()
        self.mainContainer.Disable()
        self.updateThread = uthread2.StartTasklet(self._WaitForUpdate)

    def _WaitForUpdate(self):
        secondsWaited = 0
        secondsToWait = UPDATE_TIMEOUT_SECONDS
        while secondsWaited < secondsToWait:
            uthread2.Sleep(1.0)
            secondsWaited += 1

        self.refreshButton.Show()
        self.loadingWheel.Hide()

    def OnNewRecommendationReceived(self):
        uthread2.StartTasklet(self.ProcessUpdatedData)

    def ProcessUpdatedData(self):
        if self.mainContainer.HasAnimation('opacity'):
            uthread2.Sleep(ANIM_DURATION)
        self.refreshButton.Hide()
        self.StopWaitingForData()
        self.LoadCard()
        self.AnimateOpen()

    def StopWaitingForData(self):
        if not self.updateThread:
            return
        self.updateThread.kill()
        self.updateThread = None

    def LoadCard(self):
        if not self.recommendationController or not self.recommendationController.operationID:
            self.AnimateClose()
            return
        self.topSection.LoadSection(self.recommendationController)
        backgroundTexturePath = self.recommendationController.GetBackgroundPath()
        self.backgroundTexture.texturePath = backgroundTexturePath
        self.textCont.LoadText(self.recommendationController)
        self.UpdateCard()
        self.recommendationController.RecommendationDisplayed()

    @property
    def recommendationController(self):
        return self._recommendationController

    @recommendationController.setter
    def recommendationController(self, newController):
        if self._recommendationController:
            return
        self._recommendationController = newController
        self.recommendationController.onNewRecommendation.clear()
        self._recommendationController.onNewRecommendation.connect(self.OnNewRecommendationReceived)

    def UpdateCard(self):
        if self.recommendationController.operationID is None:
            return
        operationState = self.recommendationController.GetOperationState()
        self.topSection.UpdateSection()
        self.UpdateButton(operationState)
        if operationState == COMPLETED:
            if self.recommendationController and self.recommendationController.IsCompletedAndUnseen():
                self.BlinkButton(3)
                uthread2.call_after_wallclocktime_delay(self.ClearSlot, 3.5, self.slotIdx, self.recommendationController.operationID)
                self.recommendationController.MarkCompletionAnimationAsSeen()
                sm.ScatterEvent('OnRecommendationsUpdated')

    def ClearSlot(self, slotIDx, operationID):
        if not self.recommendationController:
            return
        if slotIDx != self.recommendationController.slotIdx:
            return
        if operationID != self.recommendationController.operationID:
            return
        self.recommendationController.ResetController()
        self.AnimateClose()
        self.RequestRecommendation()

    def UpdateButton(self, operationState):
        self.actionBtn.hint = ''
        self.dismissButton.hint = GetByLabel('UI/recommendations/DismissConfirmation')
        if operationState == COMPLETED:
            self.actionBtn.SetLabel(GetByLabel('UI/Market/Orders/StatusCompleted'))
            self.actionBtn.Disable()
            self.actionBtn.func = None
            self.actionBtn.style = ButtonStyle.SUCCESS
            self.dismissButton.hint = GetByLabel('UI/recommendations/GetNewOpportunityHint')
        if operationState == CURRENT_ACTIVE:
            self.actionBtn.SetLabel(GetByLabel('UI/Commands/CmdQuit'))
            self.actionBtn.Enable()
            self.actionBtn.func = self.QuitRecommendation
            self.actionBtn.style = ButtonStyle.WARNING
        elif operationState == ANOTHER_ACTIVE:
            self.actionBtn.SetLabel(GetByLabel('UI/Agents/Dialogue/Buttons/AcceptMission'))
            self.actionBtn.hint = GetByLabel('UI/recommendations/AlreadyActive')
            self.actionBtn.Disable()
            self.actionBtn.func = None
            self.actionBtn.style = ButtonStyle.NORMAL
        elif operationState == NO_ACTIVE:
            self.actionBtn.SetLabel(GetByLabel('UI/Agents/Dialogue/Buttons/AcceptMission'))
            self.actionBtn.Enable()
            self.actionBtn.func = self.recommendationController.AcceptRecommendation
            self.actionBtn.style = ButtonStyle.NORMAL
        else:
            self.actionBtn.style = ButtonStyle.NORMAL
        self.dismissButton.Enable()

    def OnMouseEnter(self, *args):
        if self.innerCard.HasAnimation('opacity'):
            return
        PlaySound(Sounds.HOVER)
        animations.FadeTo(self.backgroundTexture, self.backgroundTexture.opacity, 1.0, 0.2, curveType=uiconst.ANIM_OVERSHOT)

    def OnMouseExit(self, *args):
        if self.innerCard.HasAnimation('opacity'):
            return
        animations.FadeTo(self.backgroundTexture, self.backgroundTexture.opacity, 0.7, 0.2)


class TopSection(Container):
    default_align = uiconst.TOTOP
    default_height = 195

    def ApplyAttributes(self, attributes):
        self.treatmentController = None
        Container.ApplyAttributes(self, attributes)
        StretchSpriteHorizontal(name='contentCardTop', parent=self, align=uiconst.TOTOP_NOPUSH, texturePath='res:/UI/Texture/classes/Treatments/topBar.png', height=14, leftEdgeSize=94, opacity=DECO_OPACITY, padRight=34)
        self.statusLabel = EveLabelMedium(parent=self, align=uiconst.TOPLEFT, pos=(6, 6, 0, 0), text='')
        self.checkmark = Sprite(name='checkmark', parent=self, align=uiconst.TOPLEFT, pos=(24, 15, 32, 32), texturePath='res:/UI/Texture/classes/Treatments/completedIcon.png', color=LIGHT_GREEN)
        self.checkmark.display = False
        self.moreIcon = DescriptionIcon(parent=self, align=uiconst.BOTTOMRIGHT, top=20, left=6)
        iconCont = Container(name='iconCont', parent=self, align=uiconst.CENTERBOTTOM, pos=(0, 6, 122, 140))
        self.treatmentIcon = Sprite(name='treatmentIcon', parent=iconCont, align=uiconst.CENTER, pos=(0, 0, 120, 120))
        self.iconFrame = Sprite(name='iconFrame', parent=iconCont, align=uiconst.CENTER, pos=(0, 0, 122, 140), texturePath='res:/UI/Texture/classes/Treatments/iconFrame.png', opacity=DECO_OPACITY)
        self.iconFill = Sprite(name='iconFill', parent=iconCont, align=uiconst.CENTER, pos=(0, 0, 120, 140), texturePath='res:/UI/Texture/classes/Treatments/iconFrameFilled.png', opacity=0.0)
        Sprite(name='bottomBarLeft', parent=iconCont, align=uiconst.CENTERBOTTOM, pos=(-86, 10, 69, 14), texturePath='res:/UI/Texture/classes/Treatments/bottomBar.png', opacity=DECO_OPACITY)
        Sprite(name='bottomBarRight', parent=iconCont, align=uiconst.CENTERBOTTOM, pos=(86, 10, -69, 14), texturePath='res:/UI/Texture/classes/Treatments/bottomBar.png', opacity=DECO_OPACITY)

    def LoadSection(self, recommendationController):
        self.treatmentController = recommendationController
        self.treatmentIcon.texturePath = recommendationController.GetRecommendationIcon()
        self.moreIcon.LoadTooltipPanel = self.LoadMoreTooltipPanel
        self.UpdateSection()

    def UpdateSection(self):
        operationState = self.treatmentController.GetOperationState()
        self.statusLabel.SetRGBA(*self.statusLabel.default_color)
        self.iconFrame.opacity = DECO_OPACITY
        self.iconFill.opacity = 0.0
        solidIcon = False
        self.statusLabel.text = ''
        treatmentIconColor = Color.WHITE
        self.checkmark.display = False
        if operationState == REJECTED:
            self.statusLabel.text = GetByLabel('UI/Contracts/ContractsWindow/Rejected')
        elif operationState == CURRENT_ACTIVE:
            self.statusLabel.text = GetByLabel('Achievements/UI/active')
            self.statusLabel.SetRGBA(*MAIN_YELLOW)
            iconFillColor = self.GetColorWithOpacity(MAIN_YELLOW, ICON_FILL_OPACITY)
            self.iconFill.SetRGBA(*iconFillColor)
            solidIcon = True
            treatmentIconColor = LIGHT_YELLOW
            self.iconFrame.opacity = 0.0
        elif operationState == COMPLETED:
            iconFillColor = self.GetColorWithOpacity(MAIN_GREEN, ICON_FILL_OPACITY)
            self.iconFill.SetRGBA(*iconFillColor)
            solidIcon = True
            treatmentIconColor = LIGHT_GREEN
            self.iconFrame.opacity = 0.0
            self.checkmark.display = True
        self.treatmentIcon.texturePath = self.treatmentController.GetRecommendationIcon(solidIcon)
        self.treatmentIcon.SetRGBA(*treatmentIconColor)

    def GetColorWithOpacity(self, color, opacity):
        return color[:3] + (opacity,)

    def LoadMoreTooltipPanel(self, tooltipPanel, *args):
        hint = self.treatmentController.GetRecommendationHint()
        if hint:
            tooltipPanel.LoadGeneric1ColumnTemplate()
            tooltipPanel.AddLabelMedium(text=hint, wrapWidth=200)
        agencyContentGroupID = self.treatmentController.GetAgencyContentGroup()
        if agencyContentGroupID:
            if hint:
                tooltipPanel.AddSpacer(height=6)
            tooltipPanel.SetState(uiconst.UI_NORMAL)
            self.showInAgencyBtn = Button(parent=tooltipPanel, align=uiconst.NOALIGN, label=GetByLabel('UI/Agency/ShowInAgency'), hint=GetByLabel('UI/Agency/ShowInAgencyHint'), texturePath='res:/UI/Texture/WindowIcons/theAgency.png', func=lambda *args: self.OpenInAgency(agencyContentGroupID))

    def OpenInAgency(self, agencyContentGroupID):
        AgencyWndNew.OpenAndShowContentGroup(agencyContentGroupID)
        sm.ScatterEvent('OnTreatmentWndOpenedOtherWnd', 'Agency')


class TextCont(Container):
    default_name = 'treatmentContTextCont'
    default_bgColor = (0, 0, 0, 0.5)
    default_height = 130

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.headerLabel = Label(name='header', parent=self, align=uiconst.TOTOP, fontsize=18, top=5, padding=(10, 0, 10, 0))
        self.textLabelScrollingCont = ScrollingTextCont(parent=self, height=self.height, fontsize=13, labelPadding=(10, 0, 10, 0))

    def LoadText(self, treatmentController):
        header = treatmentController.GetOperationName()
        text = treatmentController.GetOperationDescription()
        self.headerLabel.text = '<center>%s</center>' % header
        width = RecommendationCard.default_width - self.headerLabel.padLeft - self.headerLabel.padRight
        w, h = self.headerLabel.MeasureTextSize(header, width=width, fontsize=self.headerLabel.fontsize)
        scrollingHeight = self.height - h - self.headerLabel.top - 50
        self.textLabelScrollingCont.UpdateHeight(scrollingHeight)
        self.textLabelScrollingCont.SetText('<center>%s</center>' % text)


SEC_PER_PIXEL = 0.07

class ScrollingTextCont(Container):
    default_align = uiconst.TOTOP_NOPUSH
    default_state = uiconst.UI_NORMAL
    default_name = 'labelCont'
    default_clipChildren = True
    default_fontsize = fontconst.EVE_MEDIUM_FONTSIZE
    fadeHeight = 14

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        text = attributes.text
        labelPadding = attributes.labelPadding or 0
        fontsize = attributes.fontsize or self.default_fontsize
        self.label = Label(name='scrollContLabel', parent=self, align=uiconst.TOTOP_NOPUSH, text='', fontsize=fontsize, padding=labelPadding)
        self.SetText(text)

    def SetText(self, text):
        self.label.text = text
        self.label.SetBottomAlphaFade(self.height, maxFadeHeight=self.fadeHeight)

    def UpdateHeight(self, newHeight):
        self.height = newHeight

    def OnMouseEnter(self, *args):
        diff = self.label.textheight - self.height
        if diff <= 2:
            return
        duration = mathext.clamp(SEC_PER_PIXEL * diff, 0, 2.0)
        animations.MorphScalar(self.label, 'padTop', self.label.padTop, -diff, duration=duration)
        fadeEndValue = (self.label.textheight, self.fadeHeight)
        self.label.SetBottomAlphaFade(*fadeEndValue)

    def OnMouseExit(self, *args):
        self.label.StopAnimations()
        self.label.padTop = 0
        self.label.SetBottomAlphaFade(self.height, self.fadeHeight)
