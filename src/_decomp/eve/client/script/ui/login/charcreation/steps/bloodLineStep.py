#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\steps\bloodLineStep.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.uicore import uicore
from carbon.common.lib.const import genderFemale, genderMale
from characterdata.bloodlines import get_bloodline_ids_by_race_id
from charactercreator import const as ccConst
import charactercreator.client.scalingUtils as ccScalingUtils
from carbonui.fontconst import STYLE_HEADER
from eve.client.script.ui.login.charcreation.charCreation import BaseCharacterCreationStep
from eve.client.script.ui.login.charcreation.charCreationButtons import GenderButton
from eve.client.script.ui.login.charcreation.empireui.backButton import BackButton
from eve.client.script.ui.login.charcreation.empireui.bloodlineBox import BloodlineBox
from eve.client.script.ui.login.charcreation.empireui.bloodlineInfo import BloodlineInfoContainer, GetBloodlineInfoContainerWidth, GetBloodlineInfoContainerHeight
from eve.client.script.ui.login.charcreation.empireui.empireThemedButtons import GetSealHeight, EmpireThemedButton, EmpireThemedDecoration, EmpireThemedButtonState, GetEmpireThemedDecorationSize, BUTTON_TEXT_FONTSIZE_MIN_RES
from eve.client.script.ui.login.charcreation.label import CCLabel
from eve.client.script.ui.login.charcreation.technologyViewUtils import LineDecoration, TECH_NAV_ARROW_SIZE
from eve.client.script.ui.util.uix import GetTextWidth, GetTextHeight
from eve.common.lib import appConst
import localization
import uthread
BACK_BUTTON_WIDTH = 107
BACK_BUTTON_HEIGHT = 36
NEXT_STEP_BUTTON_TOP = 10
NEXT_STEP_BUTTON_TEXT = 'UI/CharacterCreation/CustomizeAppearance'
NEXT_STEP_BUTTON_MIN_TEXT_PADDING = 10
CUSTOMIZE_MOUSEOVER_SOUND = 'ui_es_mouse_over_customize_appearance_play'
CUSTOMIZE_MOUSEEXIT_SOUND = 'ui_es_mouse_over_customize_appearance_stop'
CUSTOMIZE_FLARE_SOUND_INTRO = 'ui_es_customize_appearance_flare_play'
CUSTOMIZE_FLARE_SOUND_OUTRO = 'ui_es_customize_appearance_flare_stop'
BUTTON_SELECT_SOUND = 'ui_icc_button_select_play'
BLOODLINES_HEADER_LABEL = 'UI/CharacterCreation/BloodlineSelection'
BLOODLINE_NOTE_LABEL = 'UI/Login/CharacterCreation/BloodlineSelection/BloodlinesArePurelyAesthetic'
BLOODLINES_INFO_TOP = 11
GENDER_BUTTON_MARGIN = 4
GENDER_BUTTON_SIZE = 23
GENDER_LINE_WIDTH = 1
GENDER_LINE_HEIGHT = 14
BOUNDING_BOX_WIDTH = 105
BOUNDING_BOX_HEIGHT = 325
BOUNDING_BOX_SEPARATION = 50
DISCLAIMER_CONTAINER_TOP = -25
BLOODLINES_NOTE_TOP = 18
BLOODLINES_TEXT_WIDTH = 400
BLOODLINES_NOTE_TEXT_HEIGHT = 28
BLOODLINES_NOTE_BOTTOM = 78
BLOODLINES_NOTE_WIDTH = 580
BLOODLINES_NOTE_FONTSIZE = 11
BLOODLINES_NOTE_BUTTON_TO_TEXT_MARGIN = 14
BLOODLINES_NOTE_LINE_HEIGHT = 4
BLOODLINES_NOTE_LINE_DECO_WIDTH = 41
HOVER_SOUND_EVENTS = {appConst.bloodlineAmarr: 'ui_es_bloodline_mouse_over_amarr_play',
 appConst.bloodlineKhanid: 'ui_es_bloodline_mouse_over_khanid_play',
 appConst.bloodlineNiKunni: 'ui_es_bloodline_mouse_over_nikunni_play',
 appConst.bloodlineGallente: 'ui_es_bloodline_mouse_over_gallente_play',
 appConst.bloodlineIntaki: 'ui_es_bloodline_mouse_over_intaki_play',
 appConst.bloodlineJinMei: 'ui_es_bloodline_mouse_over_jinmei_play',
 appConst.bloodlineDeteis: 'ui_es_bloodline_mouse_over_deteis_play',
 appConst.bloodlineAchura: 'ui_es_bloodline_mouse_over_achura_play',
 appConst.bloodlineCivire: 'ui_es_bloodline_mouse_over_civire_play',
 appConst.bloodlineSebiestor: 'ui_es_bloodline_mouse_over_sebiestor_play',
 appConst.bloodlineVherokior: 'ui_es_bloodline_mouse_over_vherokior_play',
 appConst.bloodlineBrutor: 'ui_es_bloodline_mouse_over_brutor_play'}

class BloodlineStep(BaseCharacterCreationStep):
    __guid__ = 'uicls.BloodlineStep'
    stepID = ccConst.BLOODLINESTEP
    __notifyevents__ = ['OnSetDevice']

    def ApplyAttributes(self, attributes):
        self.isReady = False
        self.audioSvc = sm.GetService('audio')
        self.useVideos = attributes.Get('useVideos', True)
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        self.buttonContainer = attributes.buttonContainer
        self.bloodlineIDs = []
        self.bloodlineBtns = []
        info = self.GetInfo()
        self.raceID = info.raceID
        self.bloodlineID = info.bloodlineID
        self.genderID = info.genderID
        self.hoveredBloodlineID = None
        self.hoveredGenderID = None
        self.lastBloodlineID = None
        self.lastGenderID = None
        self.lastHoveredBloodlineID = None
        self.lastHoveredGenderID = None
        self.backButtonContainer = None
        self.nextStepButton = None
        self.nextStepButtonDecoration = None
        self.containersByBloodline = {}
        self.genderContainerParentsByBloodline = {}
        self.genderContainerParentsCenteredByBloodline = {}
        self.genderContainersByBloodline = {}
        self.bloodlineButtonsByBloodline = {}
        self.genderLinesByBloodline = {}
        self.buttonsByBloodlineAndGender = {}
        self.boundingBoxesByBloodline = {}
        self.boundingBoxesWrappersByBloodline = {}
        self.tooltipsByBloodline = {}
        self.tooltipLock = uthread.Semaphore()
        for bloodlineID in get_bloodline_ids_by_race_id(self.raceID, shuffle=True):
            self.buttonsByBloodlineAndGender[bloodlineID] = {}
            self.bloodlineIDs.append(bloodlineID)

        self.bloodCont = Container(name='bloodCont', parent=self, align=uiconst.CENTER, width=uicore.desktop.width, height=ccScalingUtils.GetMainPanelHeight(), state=uiconst.UI_PICKCHILDREN)
        self.ConstructBloodlineBanner()
        self.ConstructBloodlineInfo()
        self.ConstructBoundingBoxes()
        self.ConstructGenderButtons()
        self.ConstructBloodlineNote()
        self.UpdateNextButton()
        sm.RegisterNotify(self)
        self.isReady = True

    def ConstructBloodlineBanner(self):
        top = ccScalingUtils.GetBannerHeaderHeight()
        width = ccScalingUtils.GetMainPanelWidth()
        height = ccScalingUtils.GetMainPanelHeight() - top
        self.bloodlineBanner = Container(name='bloodlineBanner', parent=self.bloodCont, align=uiconst.CENTERTOP, width=width, height=height, top=top, state=uiconst.UI_PICKCHILDREN)
        self.parent.SetTitle(localization.GetByLabel(BLOODLINES_HEADER_LABEL))

    def ConstructBloodlineInfo(self):
        bloodlineTextHeight = GetBloodlineInfoContainerHeight()
        bloodlineTextTop = BLOODLINES_INFO_TOP * ccScalingUtils.GetScaleFactor()
        self.bloodlineInfoCont = BloodlineInfoContainer(name='bloodlineInfoCont', parent=self.bloodlineBanner, align=uiconst.TOTOP, height=bloodlineTextHeight, raceID=self.raceID, bloodlineIDs=self.bloodlineIDs, selectedBloodlineID=self.bloodlineID, top=bloodlineTextTop, state=uiconst.UI_HIDDEN)

    def ConstructGenderButtons(self):
        scaleFactor = ccScalingUtils.GetScaleFactor()
        bloodlineContainerWidth = GetBloodlineInfoContainerWidth()
        genderButtonSize = GENDER_BUTTON_SIZE * scaleFactor
        genderMargin = GENDER_BUTTON_MARGIN * scaleFactor
        genderLineHeight = GENDER_LINE_HEIGHT * scaleFactor
        containerSizeDifference = ccScalingUtils.GetMainPanelWidth() - bloodlineContainerWidth
        for bloodlineID in self.bloodlineIDs:
            firstBloodlineBox = self.boundingBoxesByBloodline[bloodlineID][genderFemale]
            left = firstBloodlineBox.left + firstBloodlineBox.width
            self.bloodlineInfoCont.AlignButtonIcons(bloodlineID, left)
            genderBtnContainerLeft = left - genderButtonSize - genderMargin - containerSizeDifference / 2
            genderContainerParent = Container(name='genderContainerParent', parent=self.bloodlineBanner, align=uiconst.TOTOP_NOPUSH, width=bloodlineContainerWidth, height=genderButtonSize, state=uiconst.UI_HIDDEN)
            self.genderContainerParentsByBloodline[bloodlineID] = genderContainerParent
            genderContainerParentCentered = Container(name='genderContainerParentCentered', parent=genderContainerParent, align=uiconst.CENTER, width=bloodlineContainerWidth, height=genderButtonSize)
            self.genderContainerParentsCenteredByBloodline[bloodlineID] = genderContainerParentCentered
            contGender = Container(name='genderContainer_%d' % bloodlineID, parent=genderContainerParentCentered, align=uiconst.TOLEFT, width=genderButtonSize * 2 + 2 * genderMargin, height=genderButtonSize, left=genderBtnContainerLeft)
            self.genderContainersByBloodline[bloodlineID] = contGender
            genderBtnFemale = GenderButton(name='GenderButton_F', parent=contGender, align=uiconst.BOTTOMLEFT, width=genderButtonSize, height=genderButtonSize, spriteWidth=genderButtonSize, spriteHeight=genderButtonSize, genderID=genderFemale, raceID=self.raceID, state=uiconst.UI_HIDDEN)
            self.buttonsByBloodlineAndGender[bloodlineID][genderFemale] = genderBtnFemale
            genderLine = Fill(name='genderLine_Bloodline%d' % bloodlineID, parent=contGender, color=(1.0, 1.0, 1.0, 0.25), align=uiconst.CENTERLEFT, width=GENDER_LINE_WIDTH, height=genderLineHeight, left=genderButtonSize + genderMargin, state=uiconst.UI_HIDDEN)
            self.genderLinesByBloodline[bloodlineID] = genderLine
            genderBtnMale = GenderButton(name='GenderButton_M', parent=contGender, align=uiconst.BOTTOMRIGHT, width=genderButtonSize, height=genderButtonSize, spriteWidth=genderButtonSize, spriteHeight=genderButtonSize, genderID=genderMale, raceID=self.raceID, state=uiconst.UI_HIDDEN)
            self.buttonsByBloodlineAndGender[bloodlineID][genderMale] = genderBtnMale
            if self.bloodlineID and self.bloodlineID == bloodlineID:
                canChangeGender = uicore.layer.charactercreation.controller.CanChangeGender()
                selectedGenderID = self.genderID
                if selectedGenderID is not None and canChangeGender:
                    self.buttonsByBloodlineAndGender[bloodlineID][selectedGenderID].Show()
                    self.buttonsByBloodlineAndGender[bloodlineID][selectedGenderID].Select()
                    deselectedGenderID = not selectedGenderID
                    self.buttonsByBloodlineAndGender[bloodlineID][deselectedGenderID].Hide()

    def ConstructBoundingBoxes(self):
        scaleFactor = ccScalingUtils.GetScaleFactor()
        genderContainerHeight = GENDER_BUTTON_SIZE * scaleFactor
        boundingBoxWidth = BOUNDING_BOX_WIDTH * scaleFactor
        boundingBoxHeight = BOUNDING_BOX_HEIGHT * scaleFactor
        boundingBoxSeparation = BOUNDING_BOX_SEPARATION * scaleFactor
        left = (self.bloodlineBanner.width - 6 * boundingBoxWidth - 3 * boundingBoxSeparation) / 2
        isAnySelected = self.bloodlineID is not None and self.genderID is not None
        for bloodlineID in self.bloodlineIDs:
            boundingBoxWrapper = Container(name='boundingBoxWrapper_Bloodline%s' % bloodlineID, parent=self.bloodlineBanner, align=uiconst.TOTOP_NOPUSH, width=2 * boundingBoxWidth, height=boundingBoxHeight, top=genderContainerHeight, state=uiconst.UI_PICKCHILDREN, opacity=False)
            self.boundingBoxesWrappersByBloodline[bloodlineID] = boundingBoxWrapper
            self.boundingBoxesByBloodline[bloodlineID] = {}
            for gender in [genderFemale, genderMale]:
                isThisBoxSelected = bloodlineID == self.bloodlineID and gender == self.genderID
                showSelectedOnLoad = isThisBoxSelected or not isAnySelected
                boundingBox = BloodlineBox(name='boundingBox_Bloodline%s_Gender%s' % (bloodlineID, gender), parent=boundingBoxWrapper, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, width=boundingBoxWidth + boundingBoxSeparation / 2, height=boundingBoxHeight, left=left if gender == genderFemale else 0, race=self.raceID, bloodlineID=bloodlineID, gender=gender, isSelected=isThisBoxSelected, onSelection=self.OnBoundingBoxSelection, onHover=self.OnBoundingBoxHover, onDehover=self.OnBoundingBoxDehover, useVideos=self.useVideos, showSelectedOnLoad=showSelectedOnLoad, resAlign=uiconst.TORIGHT_NOPUSH if gender == genderFemale else uiconst.TOLEFT_NOPUSH)
                self.boundingBoxesByBloodline[bloodlineID][gender] = boundingBox

            left = left + 2 * boundingBoxWidth + boundingBoxSeparation

    def ConstructBloodlineNote(self):
        noteSizeParameters = self._CalculateNoteSizeParameters()
        self.noteContainer = Container(name='noteContainer', parent=self.bloodlineBanner, align=uiconst.CENTERBOTTOM, width=noteSizeParameters['noteWidth'], height=noteSizeParameters['noteHeight'], state=uiconst.UI_HIDDEN, top=DISCLAIMER_CONTAINER_TOP)
        self.noteContentContainer = Container(name='noteContentContainer', parent=self.noteContainer, align=uiconst.CENTERTOP, width=noteSizeParameters['noteContentWidth'], height=noteSizeParameters['noteHeight'] - noteSizeParameters['topMargin'], state=uiconst.UI_NORMAL, top=noteSizeParameters['topMargin'])
        if not uicore.layer.charactercreation.controller._IsUserInSkipTechnologyStepCohort():
            self.ConstructBackButton()
        self.disclaimerContainer = Container(name='disclaimerContainer', parent=self.noteContentContainer, align=uiconst.TORIGHT, width=noteSizeParameters['textWidth'], state=uiconst.UI_NORMAL)
        self.disclaimerText = CCLabel(name='disclaimerText', parent=self.disclaimerContainer, fontsize=noteSizeParameters['noteTextFontsize'], align=uiconst.TOALL, text=localization.GetByLabel(BLOODLINE_NOTE_LABEL), letterspace=0, top=0, bold=0, fontStyle=STYLE_HEADER)
        self.line = LineDecoration(name='noteLine', parent=self.noteContainer, align=uiconst.TOTOP_NOPUSH, width=noteSizeParameters['noteWidth'], height=BLOODLINES_NOTE_LINE_HEIGHT, lineWidth=noteSizeParameters['noteWidth'], lineDecorationWidth=noteSizeParameters['lineDecoWidth'], invert=False)

    def ConstructBackButton(self):
        if self.backButtonContainer and not self.backButtonContainer.destroyed:
            self.backButtonContainer.Close()
        backButtonWidth = BACK_BUTTON_WIDTH * ccScalingUtils.GetScaleFactor()
        backButtonHeight = BACK_BUTTON_HEIGHT * ccScalingUtils.GetScaleFactor()
        self.backButtonContainer = Container(name='backButtonContainer', parent=self.noteContentContainer, align=uiconst.TOLEFT, width=backButtonWidth, state=uiconst.UI_NORMAL)
        backButtonWrapper = Container(name='backButtonWrapper', parent=self.backButtonContainer, align=uiconst.TOTOP, width=backButtonWidth, height=backButtonHeight)
        BackButton(name='backButton', parent=backButtonWrapper, align=uiconst.CENTER, width=backButtonWidth, height=backButtonHeight, raceID=self.raceID, iconSize=TECH_NAV_ARROW_SIZE * ccScalingUtils.GetScaleFactor())

    def ShouldReactToMouseEvents(self):
        return self.isReady

    def OnBoundingBoxSelection(self, selectedBloodlineID, selectedGender):
        if not self.ShouldReactToMouseEvents():
            return
        for bloodlineID in self.bloodlineIDs:
            for gender in [genderFemale, genderMale]:
                boundingBox = self.boundingBoxesByBloodline[bloodlineID][gender]
                if bloodlineID == selectedBloodlineID and gender == selectedGender:
                    boundingBox.Select()
                else:
                    boundingBox.Deselect()

        uthread.new(self.SelectBloodlineAndGender, selectedBloodlineID, selectedGender)

    def OnBoundingBoxHover(self, hoveredBloodlineID, hoveredGender):
        if not self.ShouldReactToMouseEvents():
            return
        for bloodlineID in self.bloodlineIDs:
            for gender in [genderFemale, genderMale]:
                boundingBox = self.boundingBoxesByBloodline[bloodlineID][gender]
                isThisSelected = self.bloodlineID == bloodlineID and self.genderID == gender
                if not isThisSelected:
                    isThisHovered = bloodlineID == hoveredBloodlineID and gender == hoveredGender
                    if isThisHovered:
                        boundingBox.ShowHover()
                    else:
                        boundingBox.ShowDehover()

        self.hoveredBloodlineID = hoveredBloodlineID
        self.bloodlineInfoCont.HoverBloodline(hoveredBloodlineID)
        if self.hoveredGenderID != hoveredGender:
            sound_event = HOVER_SOUND_EVENTS.get(self.hoveredBloodlineID, 'ui_es_bloodline_mouse_over_stop')
            self.audioSvc.SendUIEvent(sound_event)
        self.hoveredGenderID = hoveredGender
        self._UpdateGenderButtons()

    def OnBoundingBoxDehover(self, dehoveredBloodlineID, dehoveredGender):
        if not self.ShouldReactToMouseEvents():
            return
        isAnySelected = self.bloodlineID is not None and self.genderID is not None
        for bloodlineID in self.bloodlineIDs:
            for gender in [genderFemale, genderMale]:
                boundingBox = self.boundingBoxesByBloodline[bloodlineID][gender]
                if not isAnySelected:
                    boundingBox.ShowSelected()
                else:
                    isThisSelected = self.bloodlineID == bloodlineID and self.genderID == gender
                    isThisDehovered = bloodlineID == dehoveredBloodlineID and gender == dehoveredGender
                    if not isThisSelected and isThisDehovered:
                        boundingBox.ShowDehover()

        if self.hoveredBloodlineID != None:
            self.audioSvc.SendUIEvent('ui_es_bloodline_mouse_over_stop')
        self.hoveredBloodlineID = None
        self.hoveredGenderID = None
        self.ResetBloodlineInfo()
        self._UpdateGenderButtons()

    def ResetBloodlineInfo(self):
        self.bloodlineInfoCont.ResetInfo()
        for bloodlineID in self.bloodlineIDs:
            firstBloodlineBox = self.boundingBoxesByBloodline[bloodlineID][genderFemale]
            left = firstBloodlineBox.left + firstBloodlineBox.width
            self.bloodlineInfoCont.AlignButtonIcons(bloodlineID, left)

    def SelectBloodlineAndGender(self, selectedBloodlineID, selectedGender):
        if selectedBloodlineID is None or selectedGender is None:
            return
        self.audioSvc.SendUIEvent('ui_es_bloodline_mouse_over_stop')
        shouldUpdateNextStepButton = self.bloodlineID is None
        uthread.new(uicore.layer.charactercreation.controller.SelectBloodlineAndGender, selectedBloodlineID, selectedGender)
        self.bloodlineID = selectedBloodlineID
        self.bloodlineInfoCont.SelectBloodline(selectedBloodlineID)
        self.audioSvc.SendUIEvent(BUTTON_SELECT_SOUND)
        self.genderID = selectedGender
        self._UpdateGenderButtons()
        if shouldUpdateNextStepButton:
            self.SetNextStepButtonDecoration()
            self.SetNextStepButton()

    def UpdateLayout(self):
        bloodContWidth = uicore.desktop.width
        bloodContHeight = ccScalingUtils.GetMainPanelHeight()
        hasWidthChanged = self.bloodCont.width != bloodContWidth
        hasHeightChanged = self.bloodCont.height != bloodContHeight
        if self.isReady and (hasWidthChanged or hasHeightChanged):
            self.Reload()

    def UpdateNextButton(self):
        self.buttonContainer.Flush()
        self.SetNextStepButtonDecoration()
        self.SetNextStepButton()

    def _CalculateNoteSizeParameters(self):
        backButtonWidth = BACK_BUTTON_WIDTH * ccScalingUtils.GetScaleFactor()
        noteText = localization.GetByLabel(BLOODLINE_NOTE_LABEL)
        noteTextFontsize = BLOODLINES_NOTE_FONTSIZE * ccScalingUtils.GetScaleFactor()
        textWidth = BLOODLINES_TEXT_WIDTH * ccScalingUtils.GetScaleFactor()
        textHeight = GetTextHeight(strng=noteText, width=textWidth, fontsize=noteTextFontsize, hspace=0, uppercase=0)
        minTextHeight = BLOODLINES_NOTE_TEXT_HEIGHT * ccScalingUtils.GetScaleFactor()
        textHeight = max(minTextHeight, textHeight)
        topMargin = BLOODLINES_NOTE_TOP * ccScalingUtils.GetScaleFactor()
        bottomMargin = BLOODLINES_NOTE_BOTTOM * ccScalingUtils.GetScaleFactor()
        noteWidth = BLOODLINES_NOTE_WIDTH * ccScalingUtils.GetScaleFactor()
        noteHeight = topMargin + textHeight + bottomMargin
        noteButtonToTextMargin = BLOODLINES_NOTE_BUTTON_TO_TEXT_MARGIN * ccScalingUtils.GetScaleFactor()
        noteContentWidth = backButtonWidth + noteButtonToTextMargin + textWidth
        lineDecoWidth = BLOODLINES_NOTE_LINE_DECO_WIDTH * ccScalingUtils.GetScaleFactor()
        noteSizeParameters = {'noteWidth': noteWidth,
         'noteHeight': noteHeight,
         'noteContentWidth': noteContentWidth,
         'topMargin': topMargin,
         'backButtonWidth': backButtonWidth,
         'textWidth': textWidth,
         'noteButtonToTextMargin': noteButtonToTextMargin,
         'noteTextFontsize': noteTextFontsize,
         'lineDecoWidth': lineDecoWidth}
        return noteSizeParameters

    def GetBloodlinePos(self, bloodlineID):
        scaleFactor = ccScalingUtils.GetScaleFactor()
        firstBloodlineBox = self.boundingBoxesByBloodline[bloodlineID][genderFemale]
        left = firstBloodlineBox.left + firstBloodlineBox.width
        self.bloodlineInfoCont.AlignButtonIcons(bloodlineID, left)
        containerSizeDifference = ccScalingUtils.GetMainPanelWidth() - GetBloodlineInfoContainerWidth()
        genderIconSize = GENDER_BUTTON_SIZE * scaleFactor
        genderMargin = GENDER_BUTTON_MARGIN * scaleFactor
        genderBtnContainer = self.genderContainersByBloodline[bloodlineID]
        genderBtnContainer.left = left - genderIconSize - genderMargin - containerSizeDifference / 2

    def _ShouldUpdateGenderButtons(self):
        return self.isReady and self.buttonsByBloodlineAndGender and (self.lastBloodlineID != self.bloodlineID or self.lastGenderID != self.genderID or self.lastHoveredBloodlineID != self.hoveredBloodlineID or self.lastHoveredGenderID != self.hoveredGenderID)

    def _UpdateGenderButtons(self):
        if not self._ShouldUpdateGenderButtons():
            return
        for bloodlineID in self.bloodlineIDs:
            if bloodlineID not in (self.bloodlineID, self.hoveredBloodlineID):
                self.buttonsByBloodlineAndGender[bloodlineID][genderFemale].Hide()
                self.buttonsByBloodlineAndGender[bloodlineID][genderMale].Hide()
                self.genderLinesByBloodline[bloodlineID].Hide()

        if self.bloodlineID is not None and self.genderID is not None:
            genderBtnFemale = self.buttonsByBloodlineAndGender[self.bloodlineID][genderFemale]
            genderBtnMale = self.buttonsByBloodlineAndGender[self.bloodlineID][genderMale]
            genderLine = self.genderLinesByBloodline[self.bloodlineID]
            if self.genderID == genderFemale:
                genderBtnFemale.Select()
                genderBtnMale.Hide()
            else:
                genderBtnFemale.Hide()
                genderBtnMale.Select()
            genderLine.Hide()
        if self.hoveredBloodlineID is not None and self.hoveredGenderID is not None:
            genderLine = self.genderLinesByBloodline[self.hoveredBloodlineID]
            if self.hoveredBloodlineID == self.bloodlineID:
                deselectedGenderID = not self.genderID
                deselectedGenderButton = self.buttonsByBloodlineAndGender[self.hoveredBloodlineID][deselectedGenderID]
                if self.hoveredGenderID == self.genderID:
                    deselectedGenderButton.Hide()
                    genderLine.Hide()
                else:
                    deselectedGenderButton.HoverInHighlighted()
                    genderLine.Show()
            else:
                hoveredGenderID = self.hoveredGenderID
                dehoveredGenderID = not self.hoveredGenderID
                hoveredGenderButton = self.buttonsByBloodlineAndGender[self.hoveredBloodlineID][hoveredGenderID]
                dehoveredGenderButton = self.buttonsByBloodlineAndGender[self.hoveredBloodlineID][dehoveredGenderID]
                hoveredGenderButton.HoverInHighlighted()
                dehoveredGenderButton.Show()
                dehoveredGenderButton.Deselect()
                genderLine.Show()
        self.lastBloodlineID = self.bloodlineID
        self.lastGenderID = self.genderID
        self.lastHoveredBloodlineID = self.hoveredBloodlineID
        self.lastHoveredGenderID = self.hoveredGenderID

    def OnRaceSelected(self, raceID, *args):
        if self.raceID != raceID:
            self.raceID = raceID
            self.Reload(updateRace=True)

    def OnSetDevice(self):
        self.UpdateLayout()

    def CreateCharacter(self):
        self.audioSvc.SendUIEvent('ui_es_button_mouse_down_create_character_play')
        uicore.layer.charactercreation.controller.Approve()

    def CalculateNextStepButtonState(self):
        if self.bloodlineID is not None:
            return EmpireThemedButtonState.NORMAL
        return EmpireThemedButtonState.DISABLED

    def SetNextStepButton(self):
        if self.nextStepButton and not self.nextStepButton.destroyed:
            self.nextStepButton.Close()
        nextStepButtonLabel = localization.GetByLabel(NEXT_STEP_BUTTON_TEXT)
        nextStepButtonLabelFontsize = BUTTON_TEXT_FONTSIZE_MIN_RES * ccScalingUtils.GetScaleFactor()
        nextStepButtonLabelWidth = GetTextWidth(strng=nextStepButtonLabel, fontsize=nextStepButtonLabelFontsize, hspace=0, uppercase=1)
        minWidth = nextStepButtonLabelWidth + 2 * NEXT_STEP_BUTTON_MIN_TEXT_PADDING
        nextStepButtonWidth = max(minWidth, ccScalingUtils.GetCustomizeCharacterButtonWidth())
        nextStepButtonHeight = ccScalingUtils.GetCustomizeCharacterButtonHeight()
        nextStepButtonTop = ccScalingUtils.GetBottomNavHeight() - nextStepButtonHeight - NEXT_STEP_BUTTON_TOP
        self.nextStepButton = EmpireThemedButton(name='NextStepButton', parent=self.buttonContainer, align=uiconst.CENTERBOTTOM, label=nextStepButtonLabel.upper(), raceID=self.raceID, width=nextStepButtonWidth, height=nextStepButtonHeight, top=nextStepButtonTop, buttonState=self.CalculateNextStepButtonState(), mouseOverSound=CUSTOMIZE_MOUSEOVER_SOUND, mouseExitSound=CUSTOMIZE_MOUSEEXIT_SOUND)
        self.nextStepButton.OnClick = self.CreateCharacter

    def SetNextStepButtonDecoration(self):
        if not self.nextStepButtonDecoration:
            width, height = GetEmpireThemedDecorationSize()
            nextStepButtonDecorationContainer = Container(name='NextStepButtonDecoration_Container', parent=self.buttonContainer, align=uiconst.TOTOP_NOPUSH, width=width, height=height, top=-GetSealHeight(), state=uiconst.UI_DISABLED)
            self.nextStepButtonDecoration = EmpireThemedDecoration(name='NextStepButtonDecoration', parent=nextStepButtonDecorationContainer, align=uiconst.CENTERTOP, width=width, height=height, flareSoundIntro=CUSTOMIZE_FLARE_SOUND_INTRO, flareSoundOutro=CUSTOMIZE_FLARE_SOUND_OUTRO)
        nextStepButtonState = self.CalculateNextStepButtonState()
        self.nextStepButtonDecoration.UpdateDecoration(self.raceID, nextStepButtonState)

    def ShowBloodlineInfo(self):
        self.bloodlineInfoCont.Show()

    def HideBloodlineInfo(self):
        self.bloodlineInfoCont.Hide()

    def ShowBoundingBoxes(self):
        for container in self.boundingBoxesWrappersByBloodline.values():
            container.opacity = 1.0

    def HideBoundingBoxes(self):
        for container in self.boundingBoxesWrappersByBloodline.values():
            container.opacity = 0.0

    def ShowGenders(self):
        for genderContainer in self.genderContainerParentsByBloodline.values():
            genderContainer.Show()

    def HideGenders(self):
        for genderContainer in self.genderContainerParentsByBloodline.values():
            genderContainer.Hide()

    def ShowNote(self):
        self.noteContainer.Show()

    def HideNote(self):
        self.noteContainer.Hide()

    def HideContent(self):
        self.HideBloodlineInfo()
        self.HideBoundingBoxes()
        self.HideGenders()
        self.HideNote()

    def Reload(self, updateRace = False):
        if not self.isReady:
            return
        self.isReady = False
        self.HideContent()
        uicore.layer.charactercreation.controller.ReloadBloodlineStep(updateRace=updateRace)
