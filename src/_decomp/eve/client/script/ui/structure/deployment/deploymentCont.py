#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\deployment\deploymentCont.py
import evetypes
from carbon.common.script.util.format import FmtDist
from carbonui.control.combo import Combo
from carbonui.fontconst import EVE_LARGE_FONTSIZE
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.control.button import Button
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge, EveHeaderLarge, EveLabelSmall
from carbonui.control.singlelineedits.prefixed import PrefixedSingleLineEdit
from carbonui.control.window import Window
from carbonui import uiconst
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.structure import ChangeSignalConnect
import eve.client.script.ui.structure.deployment.deploymentContUtil as dUtil
from eve.client.script.ui.structure.deployment.stargateDeploymentCont import StargateDeploymentCont
from eve.common.script.util.structuresCommon import MAX_STRUCTURE_BIO_LENGTH
from globalConfig.getFunctions import IsContentComplianceControlSystemActive
from inventorycommon.const import groupMoon, typeMoonMiningBeacon
from localization import GetByLabel
import structures
import log
from carbonui.uicore import uicore
from moonmining.const import MOONMINING_NOT_POSSIBLE, MOONMINING_POSSIBLE, MAXIMUM_MINING_BEACON_DISTANCE
from structures.deployment import WARPIN_POINT, AUTOMOONMINER_DESIGNATED_SPOTS, AUTOMOONMINER_BEACON
from eve.common.script.sys import idCheckers

class StructureDeploymentWnd(Window):
    default_captionLabelPath = 'UI/Structures/Deployment/DeploymentHeader'
    default_windowID = 'StructureDeploymentWndID'
    default_width = 430
    default_height = 100
    default_minSize = (400, 350)
    default_left = '__center__'

    @staticmethod
    def default_top():
        return int(uicore.desktop.height / 2.0 + 100)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MakeUnstackable()
        self.MakeUnResizeable()
        self.MakeUncollapseable()
        self.scheduleStepBuilt = False
        self.structureTypeID = attributes.typeID
        self.width = self.GetWidthForStructureType()
        self.scheduleCont = None
        self.extraStepCont = None
        self.step = dUtil.STEP_POSITION
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self.content, align=uiconst.TOTOP, callback=self._on_main_cont_size_changed, only_use_callback_when_size_changes=True)
        self.scheduleContParent = ContainerAutoSize(name='scheduleContParent', parent=self.mainCont, align=uiconst.TOTOP)
        self.extraContParent = ContainerAutoSize(name='extraContParent', parent=self.mainCont, align=uiconst.TOTOP)
        self.explanationCont = ContainerAutoSize(name='explanationCont', parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        self.structureDeploymentCont = StructureDeploymentCont(parent=self.mainCont, align=uiconst.TOTOP, structureTypeID=self.structureTypeID, forwardCallback=self.OnForwardBtnClicked, confirmCallback=self.OnConfirmBtnClicked, backCallback=self.OnBackBtnClicked)
        self.BuildExplanationStep()
        self.ChangeSignalConnection()

    def _on_main_cont_size_changed(self):
        _, self.height = self.GetWindowSizeForContentSize(height=self.mainCont.height)

    def GetWidthForStructureType(self):
        if evetypes.IsUpwellStargate(self.structureTypeID):
            return 550
        return self.default_width

    def ChangeSignalConnection(self, connect = True):
        entity = sm.GetService('structureDeployment').GetEntity()
        if entity:
            signalAndCallback = [(entity.on_location_updated, self.OnModelLocationUpdated)]
            ChangeSignalConnect(signalAndCallback, connect)

    def BuildExplanationStep(self):
        text = GetByLabel('UI/Structures/Deployment/IntroHeader')
        EveLabelLarge(parent=self.explanationCont, text=text, align=uiconst.TOTOP, padLeft=20, padTop=8)
        text = GetByLabel(dUtil.GetDeploymentStepsLabelPath(self.structureTypeID))
        EveLabelMedium(parent=self.explanationCont, text=text, align=uiconst.TOTOP, padLeft=30)
        if sm.GetService('warPermit').DoesMyCorpHaveNegativeWarPermit():
            text = '<color=%s>%s</color>' % (dUtil.COLOR_WARNING, GetByLabel('UI/Structures/Deployment/FirstStructureWarning'))
            EveLabelMedium(parent=self.explanationCont, text=text, align=uiconst.TOTOP, padLeft=30)
        warningCont = Container(parent=self.explanationCont, align=uiconst.TOTOP, height=45, padTop=8, padBottom=8)
        self.warningLabelCont = ContainerAutoSize(parent=warningCont, align=uiconst.CENTER, alignMode=uiconst.TOTOP)
        self.warningLabel = EveHeaderLarge(parent=self.warningLabelCont, text='', align=uiconst.TOTOP)
        self.TriggerUIForValidLocation()

    def TriggerUIForValidLocation(self):
        if self.step != dUtil.STEP_POSITION:
            return
        entity = sm.GetService('structureDeployment').GetEntity()
        if entity:
            conflict = entity.FindDeploymentConflict()
            canMoonmine = entity.GetMoonminingAvailabilityValue()
            self.UpdateUIForValidLocation(conflict, canMoonmine)

    def BuildExtraStepIfNeeded(self):
        if self.extraStepCont is None or self.extraStepCont.destroyed:
            self.extraStepCont = ContainerAutoSize(parent=self.extraContParent, align=uiconst.TOTOP)
            self.extraStepCont.display = False
        self.SetExtraStepEnabledState(force=True)

    def BuildScheduleStepIfNeeded(self):
        if self.scheduleCont is None or self.scheduleCont.destroyed:
            extraVariables = self.GetExtraVariables()
            self.scheduleCont = ScheduleCont(parent=self.scheduleContParent, align=uiconst.TOTOP, height=300, nameChangedCallback=self.OnNameChanged, extraVariables=extraVariables, structureTypeID=self.structureTypeID)
            self.scheduleCont.display = False
            self.scheduleStepBuilt = True
        self.SetConfirmEnabledState(force=True)

    def LoadExtraStep(self):
        self.BuildExtraStepIfNeeded()
        if evetypes.IsUpwellStargate(self.structureTypeID):
            self.extraStepCont.Flush()
            stargateCont = StargateDeploymentCont(parent=self.extraStepCont, align=uiconst.TOTOP, height=300)
            listHasBeenPopulated = getattr(self, 'systemListPopulatedAtLeastOnce', False)
            stargateCont.LoadListAndSetFilter(firstTime=not listHasBeenPopulated)
            self.systemListPopulatedAtLeastOnce = True

    def _OnClose(self, *args, **kw):
        sm.GetService('structureDeployment').CancelDeployment()

    def SetExtraStepEnabledState(self, force = False):
        if not force and self.step != dUtil.STEP_EXTRA:
            return
        self.structureDeploymentCont.SetContinueBtnOnExtraStepBtnState()

    def SetConfirmEnabledState(self, force = False):
        if not force and self.step != dUtil.STEP_SCHEDULE:
            return
        isEnabled = len(self.scheduleCont.GetGivenName()) >= structures.MIN_STRUCTURE_NAME_LEN
        self.structureDeploymentCont.SetConfirmEnabledState(isEnabled=isEnabled)

    def OnModelLocationUpdated(self, conflict, canMoonMine):
        if self.step != dUtil.STEP_POSITION:
            return
        self.UpdateUIForValidLocation(conflict, canMoonMine)

    def UpdateUIForValidLocation(self, conflict, canMoonmine):
        isValidLocation = conflict is None
        self.structureDeploymentCont.SetPositionEnabledState(isValidLocation)
        if conflict:
            ballTypeID, minimum, pointType = conflict
            typeName = evetypes.GetName(ballTypeID)
            ballGroupID = evetypes.GetGroupID(ballTypeID)
            distance = FmtDist(abs(minimum))
            if pointType == WARPIN_POINT:
                text = GetByLabel('UI/Structures/Deployment/TooCloseToWarpin', typeName=typeName, distance=distance)
            elif ballGroupID == groupMoon and canMoonmine == MOONMINING_NOT_POSSIBLE:
                text = GetByLabel('UI/Structures/Deployment/TooCloseToMoonTooFarAwayForMoonMining', typeName=typeName, distance=FmtDist(MAXIMUM_MINING_BEACON_DISTANCE))
            elif minimum < 0:
                text = GetByLabel('UI/Structures/Deployment/TooFarFromObject', typeName=typeName, distance=distance)
            else:
                text = GetByLabel('UI/Structures/Deployment/TooCloseToObject', typeName=typeName, distance=distance)
            text = '<color=%s>%s</color>' % (dUtil.COLOR_WARNING, text)
        else:
            text = GetByLabel('UI/Structures/Deployment/ValidLocation')
            if canMoonmine == MOONMINING_POSSIBLE:
                text += '<br>%s' % GetByLabel('UI/Structures/Deployment/ValidLocationForMoonmining')
            text = '<color=%s>%s</color>' % (dUtil.COLOR_VALID, text)
            if canMoonmine == MOONMINING_NOT_POSSIBLE:
                text += '<br><color=%s>%s</color>' % (dUtil.COLOR_WARNING_FAINT, GetByLabel('UI/Structures/Deployment/InvalidForMoonmining'))
        textWidth = self.GetWarningTextWidth(text)
        self.warningLabel.text = '<center>%s</center>' % text
        self.warningLabelCont.width = textWidth + 10

    def GetWarningTextWidth(self, text):
        return uicore.font.GetTextWidth(text, fontsize=EVE_LARGE_FONTSIZE, uppercase=True)

    def OnBackBtnClicked(self, *args):
        self.SwitchSteps(forward=False)

    def OnNameChanged(self, *args):
        self.SetConfirmEnabledState()

    def OnForwardBtnClicked(self, *args):
        self.SwitchSteps(forward=True)

    def OnConfirmBtnClicked(self, *args):
        if self.step != dUtil.STEP_SCHEDULE:
            return
        profileSelected = self.scheduleCont.GetSelectedProfile()
        if len(self.scheduleCont.GetGivenName()) < structures.MIN_STRUCTURE_NAME_LEN or not profileSelected:
            uicore.Message('uiwarning03')
            return
        bio = self.scheduleCont.GetBio()
        reinforceWeekday, reinforceHour = self.scheduleCont.GetReinforcementTime()
        extraVariables = self.GetExtraVariables()
        sm.GetService('structureDeployment').ConfirmDeployment(reinforceWeekday, reinforceHour, profileID=profileSelected, structureName=self.scheduleCont.GetStructureName(), bio=bio, extraVariables=extraVariables)
        self.SetConfirmEnabledState()

    def SwitchSteps(self, forward = True):
        self.Disable()
        try:
            newStep = dUtil.GetNextState(self.step, self.structureTypeID, forward)
            if newStep is None:
                self.CloseByUser()
                return
            self._SwitchSteps(newStep)
            self.TriggerUIForValidLocation()
        finally:
            self.Enable()

    def _SwitchSteps(self, newStep):
        self.structureDeploymentCont.SetBtnForStep(newStep)
        self.structureDeploymentCont.SetContForStep(newStep)
        contsToShow = set()
        if newStep == dUtil.STEP_POSITION:
            contsToShow.add(self.explanationCont)
        elif newStep == dUtil.STEP_EXTRA:
            self.LoadExtraStep()
            contsToShow.add(self.extraStepCont)
        elif newStep == dUtil.STEP_SCHEDULE:
            self.BuildScheduleStepIfNeeded()
            contsToShow.add(self.scheduleCont)
        else:
            return
        self.ChangeContainerVisability(contsToShow)
        showMouseCont = False
        if newStep == dUtil.STEP_POSITION:
            showMouseCont = True
        self.step = newStep
        self.structureDeploymentCont.ChangeMouseContDisplay(doShow=showMouseCont)

    def ChangeContainerVisability(self, contsToShow):
        containersToChange = {self.explanationCont, self.scheduleCont, self.extraStepCont}
        for eachCont in containersToChange:
            if eachCont:
                if eachCont in contsToShow:
                    eachCont.display = True
                else:
                    eachCont.display = False

    def GetExtraVariables(self):
        ret = {}
        if evetypes.IsUpwellStargate(self.structureTypeID):
            ret['destinationSolarsystemID'] = sm.GetService('structureDeployment').GetDestinationSolarsystemID()
        return ret

    def Close(self, *args, **kwds):
        try:
            self.ChangeSignalConnection(connect=False)
        except Exception as e:
            log.LogError('Failed at closing StructureDeploymentWnd in deployment, e = ', e)

        Window.Close(self, *args, **kwds)


class StructureDeploymentCont(Container):
    __notifyevents__ = ['OnExtraDeploymentInfoChanged']
    default_height = 60

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.canConfirm = False
        self.structureTypeID = attributes.structureTypeID
        self.stepID = dUtil.STEP_POSITION
        forwardCallback = attributes.forwardCallback
        self.confirmCallback = attributes.confirmCallback
        self.nameChangedCallback = attributes.nameChangedCallback
        backCallback = attributes.backCallback
        btnRowCont = ContainerAutoSize(parent=self, alignMode=uiconst.TOPLEFT, align=uiconst.TOBOTTOM)
        leftBtnCont = ContainerAutoSize(parent=btnRowCont, name='leftBtnCont', align=uiconst.TOPLEFT)
        rightBtnCont = ContainerAutoSize(parent=btnRowCont, name='rightBtnCont', align=uiconst.TOPRIGHT)
        self.centerCont = Container(parent=btnRowCont, name='centerCont', align=uiconst.CENTER)
        self.forwardBtn = Button(name='forwardBtn', parent=rightBtnCont, align=uiconst.CENTERRIGHT, func=forwardCallback, label=GetByLabel('UI/Structures/Deployment/Position'))
        self.anchorBtn = Button(name='anchorBtn', parent=rightBtnCont, align=uiconst.CENTERRIGHT, func=self.Confirm, label=GetByLabel('UI/Structures/Deployment/ConfirmDeployment'))
        self.backBtn = Button(name='cancelBtn', parent=leftBtnCont, align=uiconst.CENTERLEFT, func=backCallback, label=GetByLabel('UI/Common/Cancel'), hint=GetByLabel(dUtil.CANCEL_TOOLTIP))
        self.SetBtnForStep(dUtil.STEP_POSITION)
        maxBtnWidth = self.GetMaxBtnWidth()
        leftBtnCont.width = rightBtnCont.width = maxBtnWidth
        self.mouseCont = MouseCont(parent=self, structureTypeID=self.structureTypeID, padTop=10)
        sm.RegisterNotify(self)

    def GetMaxBtnWidth(self):
        stepsForStrucure = dUtil.GetStepsForStructure(self.structureTypeID)
        maxWidth = 40
        for eachStep in stepsForStrucure:
            rightBtnLabelPath = dUtil.GetRightBtnLabel(self.structureTypeID, eachStep)
            tW, _ = self.forwardBtn.sr.label.MeasureTextSize(GetByLabel(rightBtnLabelPath))
            maxWidth = max(maxWidth, tW, _ + 20)
            leftBtnLabelPath = dUtil.GetLeftBtnLabel(eachStep)
            tW, _ = self.backBtn.sr.label.MeasureTextSize(GetByLabel(leftBtnLabelPath))
            maxWidth = max(maxWidth, tW, _ + 20)

        return maxWidth

    def OnExtraDeploymentInfoChanged(self, infoChangeDict):
        if self.stepID == dUtil.STEP_EXTRA and evetypes.IsUpwellStargate(self.structureTypeID):
            destinationSolarsystemID = infoChangeDict['destinationSolarsystemID']
            self.SetContinueBtnOnExtraStepBtnState(destinationSolarsystemID)
            if getattr(self, 'stargateDestLabel') and not self.stargateDestLabel.destroyed:
                stargateDestLabel = dUtil.GetDestinationText(destinationSolarsystemID)
                self.stargateDestLabel.text = stargateDestLabel

    def ChangeMouseContDisplay(self, doShow = True):
        self.mouseCont.display = doShow

    def SetContinueBtnOnExtraStepBtnState(self, destinationSolarsystemID = None):
        if evetypes.IsUpwellStargate(self.structureTypeID):
            destinationSolarsystemID = destinationSolarsystemID or sm.GetService('structureDeployment').GetDestinationSolarsystemID()
            self.ChangeBtnStateAndHint(self.forwardBtn, bool(destinationSolarsystemID))

    def SetConfirmEnabledState(self, isEnabled):
        self.canConfirm = isEnabled
        self.ChangeBtnStateAndHint(self.anchorBtn, isEnabled)

    def SetPositionEnabledState(self, isEnabled):
        self.ChangeBtnStateAndHint(self.forwardBtn, isEnabled)

    def ChangeBtnStateAndHint(self, btn, isEnabled):
        tooltip, tooltipDisabled = dUtil.GetRightBtnHints(self.structureTypeID, self.stepID)
        if isEnabled:
            btn.Enable()
            hintPath = tooltip
        else:
            btn.Disable()
            hintPath = tooltipDisabled
        btn.hint = GetByLabel(hintPath)

    def Confirm(self, *args):
        if not self.canConfirm:
            uicore.Message('uiwarning03')
            return
        self.confirmCallback(*args)

    def Cancel(self, *args):
        sm.GetService('structureDeployment').CancelDeployment()

    def SetContForStep(self, newStep):
        self.centerCont.Flush()
        if newStep in (dUtil.STEP_EXTRA, dUtil.STEP_SCHEDULE) and evetypes.IsUpwellStargate(self.structureTypeID):
            self.stargateDestLabel = EveLabelMedium(parent=self.centerCont, name='stargateDestLabel', align=uiconst.CENTER, state=uiconst.UI_NORMAL)
            destSystem = sm.GetService('structureDeployment').GetDestinationSolarsystemID()
            if destSystem:
                stargateDestLabel = dUtil.GetDestinationText(destSystem)
                self.stargateDestLabel.text = stargateDestLabel

    def SetBtnForStep(self, newStepID):
        self.stepID = newStepID
        if newStepID == dUtil.STEP_SCHEDULE:
            self.forwardBtn.display = False
            self.anchorBtn.display = True
        else:
            leftBtnLabelPath = dUtil.GetRightBtnLabel(self.structureTypeID, self.stepID)
            self.forwardBtn.SetLabel(GetByLabel(leftBtnLabelPath))
            self.forwardBtn.display = True
            self.anchorBtn.display = False
        rigthBtnLabelPath = dUtil.GetLeftBtnLabel(self.stepID)
        self.backBtn.SetLabel(GetByLabel(rigthBtnLabelPath))
        rigthBtnHintPath = dUtil.GetLeftBtnHints(self.stepID)
        self.backBtn.hint = GetByLabel(rigthBtnHintPath)


class ScheduleCont(Container):
    __notifyevents__ = ['OnExtraDeploymentInfoChanged']

    def ApplyAttributes(self, attributes):
        self.bioEdit = None
        Container.ApplyAttributes(self, attributes)
        self.nameChangedCallback = attributes.nameChangedCallback
        self.structureTypeID = attributes.structureTypeID
        self.ChangeSignalConnection()
        extraVariables = attributes.extraVariables or {}
        self.commonlyUsedPickedCB = None
        self.nameCont = Container(parent=self, name='nameCont', align=uiconst.TOTOP, height=40)
        self.reinforcementTimeCont = ReinforcementTimeCont(parent=self, name='reinforcementTimeCont', align=uiconst.TOBOTTOM, structureTypeIDs=[self.structureTypeID])
        self.bioCont = Container(parent=self, name='bioCont', align=uiconst.TOALL, padTop=10)
        self.BuildUI(extraVariables=extraVariables)
        sm.RegisterNotify(self)

    def BuildUI(self, extraVariables):
        self.nameCont.Flush()
        self.reinforcementTimeCont.Flush()
        self.bioCont.Flush()
        self.BuildNameCont(extraVariables)
        reinforceWeekday, reinforceHour = sm.GetService('corp').GetStructureReinforceDefault()
        self.reinforcementTimeCont.LoadCont(reinforceWeekday, reinforceHour, structureTypeIDs=[self.structureTypeID])
        self.BuildBio()

    def BuildBio(self):
        if not IsContentComplianceControlSystemActive(sm.GetService('machoNet')):
            text = GetByLabel('UI/Structures/Deployment/SetStructureBio')
            EveLabelSmall(name='bioLabel', parent=self.bioCont, align=uiconst.TOTOP, text=text)
            self.bioEdit = EditPlainText(setvalue='', parent=self.bioCont, align=uiconst.TOALL, maxLength=MAX_STRUCTURE_BIO_LENGTH, padBottom=uiconst.defaultPadding, padTop=4, showattributepanel=True)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = []
        ChangeSignalConnect(signalAndCallback, connect)

    def BuildNameCont(self, extraVariables):
        padding = 0
        profileCont = Container(parent=self.nameCont, align=uiconst.TORIGHT, left=padding)
        self.profileCombo = Combo(label=GetByLabel('UI/Structures/Deployment/ProfileComboLabel'), parent=profileCont, options=self._GetProfileOptions(), name='profileCombo', width=100, align=uiconst.BOTTOMRIGHT, top=padding)
        profileCont.width = self.profileCombo.width
        nameText = GetByLabel('UI/Structures/Deployment/StructureName')
        destinationSolarsystemID = extraVariables.get('destinationSolarsystemID')
        self.ssPrefix = dUtil.GetPrefixForDeployment(self.structureTypeID, destinationSolarsystemID)
        self.nameEdit = PrefixedSingleLineEdit(name='nameEdit', parent=self.nameCont, maxLength=32 + len(self.ssPrefix), align=uiconst.TOBOTTOM, padLeft=padding, padRight=30, top=padding, label=nameText, prefix=self.ssPrefix, OnChange=self.nameChangedCallback)
        profileHeight = self.profileCombo.height - self.profileCombo.sr.label.top
        nameHeight = self.nameEdit.height - self.nameEdit.label.top
        newHeight = max(profileHeight, nameHeight) + 2 * padding
        self.nameCont.height = newHeight

    def _GetProfileOptions(self):
        structureControllers = sm.GetService('structureControllers').GetAllStructuresProfileController()
        profileOptions = []
        defaultProfile = None
        for profileID, profile in structureControllers.GetProfiles(force=True).iteritems():
            if profile.IsDefault():
                defaultProfile = profile
            else:
                profileOptions.append((profile.GetProfileName(), profileID, profile.GetProfileDescription()))

        profileOptions.sort(key=lambda x: x[0].lower())
        if defaultProfile:
            profileOptions.insert(0, (defaultProfile.GetProfileName(), defaultProfile.GetProfileID(), defaultProfile.GetProfileDescription()))
        return profileOptions

    def GetSelectedProfile(self):
        selectedID = self.profileCombo.GetValue()
        return selectedID

    def GetStructureName(self):
        return self.nameEdit.GetValue().strip()

    def GetGivenName(self):
        return self.GetStructureName()[len(self.GetNamePrefix()):]

    def GetNamePrefix(self):
        return self.ssPrefix

    def GetReinforcementTime(self):
        return self.reinforcementTimeCont.GetReinforcementTime()

    def GetBio(self):
        if self.bioEdit:
            return self.bioEdit.GetValue()
        return ''

    def OnExtraDeploymentInfoChanged(self, infoChangeDict):
        if evetypes.IsUpwellStargate(self.structureTypeID):
            destinationSolarsystemID = infoChangeDict['destinationSolarsystemID']
            prefix = dUtil.GetPrefixForDeployment(self.structureTypeID, destinationSolarsystemID)
            self.ssPrefix = prefix
            self.nameEdit.UpdatePrefix(prefix)

    def Close(self):
        try:
            self.ChangeSignalConnection(connect=False)
        except Exception as e:
            log.LogError('Failed at closing ScheduleCont in deployment, e = ', e)

        Container.Close(self)


class MouseCont(Container):
    MOUSE_LEFT_PATH = 'res:/UI/Texture/classes/Achievements/mouseBtnLeft.png'
    MOUSE_RIGHT_PATH = 'res:/UI/Texture/classes/Achievements/mouseBtnRight.png'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        structureTypeID = attributes.structureTypeID
        leftMouseCont = Container(parent=self, name='leftMouseCont', align=uiconst.TOLEFT_PROP, width=0.5)
        rightMouseCont = Container(parent=self, name='rightMouseCont', align=uiconst.TORIGHT_PROP, width=0.5)
        leftMouseSprite = Sprite(parent=leftMouseCont, name='leftMouseSprite', align=uiconst.CENTERRIGHT, texturePath=self.MOUSE_LEFT_PATH, pos=(0, 0, 32, 32))
        rightMouseSprite = Sprite(parent=rightMouseCont, name='rightMouseSprite', align=uiconst.CENTERLEFT, texturePath=self.MOUSE_RIGHT_PATH, pos=(0, 0, 32, 32))
        leftText = GetByLabel('UI/Structures/Deployment/MoveStructure')
        self.leftLabel = EveLabelMedium(parent=leftMouseCont, name='leftLabel', align=uiconst.CENTERRIGHT, pos=(32, -6, 0, 0), text=leftText)
        rightText = GetByLabel('UI/Structures/Deployment/RotateStructure')
        self.rightLabel = EveLabelMedium(parent=rightMouseCont, name='rightLabel', align=uiconst.CENTERLEFT, pos=(32, -6, 0, 0), text=rightText)
        if evetypes.IsUpwellStargate(structureTypeID):
            rightMouseCont.display = False


class ReinforcementTimeCont(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        structureTypeIDs = attributes.structureTypeIDs
        self.LoadCont(structureTypeIDs=structureTypeIDs)

    def LoadCont(self, reinforcementDay = None, reinforcementHour = None, structureTypeIDs = None):
        self.Flush()
        self.reinforcementHourCont = Container(parent=self, name='reinforcementHourCont', align=uiconst.TOTOP, height=40, padTop=10)
        hourPickerText = GetByLabel(dUtil.GetHourPickerLabelPath(structureTypeIDs))
        self.hourPickerLabel = EveLabelSmall(name='hourPickerLabel', parent=self.reinforcementHourCont, top=1, align=uiconst.CENTERLEFT, text=hourPickerText)
        hourHint = GetByLabel(dUtil.GetPrimeHourLabelPath(structureTypeIDs))
        helpIconLeft = self.hourPickerLabel.left + self.hourPickerLabel.textwidth + 2
        MoreInfoIcon(parent=self.reinforcementHourCont, hint=hourHint, left=helpIconLeft, align=uiconst.CENTERLEFT)
        hourOptions = [ ('%.2d:%.2d' % (h, 0), h) for h in xrange(0, 24) ]
        self.hourCombo = Combo(parent=self.reinforcementHourCont, options=hourOptions, name='hourCombo', width=100, align=uiconst.CENTERLEFT, left=200, select=reinforcementHour)
        self.reinforcementHourCont.height = max(self.hourCombo.height, self.hourPickerLabel.textheight + 6)
        text = GetByLabel(dUtil.GetPrimeHourSubtextLabelPath(structureTypeIDs))
        self.hourLabel = EveLabelSmall(name='hourLabel', parent=self, align=uiconst.TOTOP, text=text, top=4)
        maxDayWidth = self.hourPickerLabel.textwidth
        comboLeft = maxDayWidth + 28
        self.hourCombo.left = comboLeft

    def GetReinforcementTime(self):
        dayValue = structures.NO_REINFORCEMENT_WEEKDAY
        return (dayValue, self.hourCombo.GetValue())
