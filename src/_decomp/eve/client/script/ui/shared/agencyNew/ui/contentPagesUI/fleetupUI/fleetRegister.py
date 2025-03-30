#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\fleetupUI\fleetRegister.py
import evefleet
import inventorycommon.const as invConst
from carbon.common.script.util.commonutils import StripTags
from carbonui import ButtonVariant, TextColor, uiconst
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.slider import Slider
from carbonui.fontconst import EVE_LARGE_FONTSIZE
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.line import Line
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import Label, EveLabelMedium
from eve.client.script.ui.shared.agencyNew import agencySignals
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.fleetupUI.fleetRegisterController import FleetRegisterController
from carbonui.primitives.warningContainer import WarningContainer
from eve.client.script.ui.shared.fleet.fleet import FleetSvc, GetAllFleetActivities
from eveexceptions import ExceptionEater, UserError
from evefleet.fleetAdvertObject import FleetAdvertCreationObject
from localization import GetByLabel
from signals import Signal
from signals.signalUtil import ChangeSignalConnect
from utillib import KeyVal
BIG_FONT_SIZE = 26
DEFAULT_JOIN_LIMIT = 250

class FleetRegister(Container):
    __guid__ = 'FleetRegister'
    default_padTop = 30

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.fleetRegisterController = FleetRegisterController()
        self.basicCont = BasicOptionsCont(parent=self, fleetRegisterController=self.fleetRegisterController)
        self.advancedOptionsCont = AdvancedOptionsCont(parent=self, fleetRegisterController=self.fleetRegisterController)
        self.ChangeSignalConnection()
        self.LoadBasic()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.fleetRegisterController.on_load_basic, self.LoadBasic), (self.fleetRegisterController.on_load_advanced, self.LoadAdvanced), (self.fleetRegisterController.on_advanced_saved, self.OnAdvancedSaved)]
        ChangeSignalConnect(signalAndCallback, connect)

    def LoadBasic(self):
        self.basicCont.display = True
        self.advancedOptionsCont.display = False
        self.basicCont.UpdateUI()

    def LoadAdvanced(self):
        self.basicCont.display = False
        self.advancedOptionsCont.display = True
        self.advancedOptionsCont.ReloadCont()

    def OnAdvancedSaved(self):
        self.basicCont.useAdvancedCb.SetChecked(True, False)
        self.LoadBasic()

    def Close(self):
        with ExceptionEater('FleetRegister: Exception when changing connection'):
            self.ChangeSignalConnection(connect=False)
        Container.Close(self)


class SliderAndLabel(ContainerAutoSize):
    default_name = 'SliderAndLabel'

    def ApplyAttributes(self, attributes):
        super(SliderAndLabel, self).ApplyAttributes(attributes)
        configName = attributes.configName
        self.text = attributes.text
        moreInfoText = attributes.moreInfoText
        self.on_checkbox = Signal()
        increments = [ x / 10.0 for x in xrange(-100, 101) ]
        subLevelIndent = 30
        subLevelIndentSlider = 2 * subLevelIndent
        self.checkbox = Checkbox(parent=self, name=configName + 'Cb', align=uiconst.TOBOTTOM, text=self.text, padLeft=subLevelIndent, hint=moreInfoText, callback=self.on_checkbox)
        self.slider = Slider(name=configName + 'Slider', parent=self, align=uiconst.TOBOTTOM, padLeft=subLevelIndentSlider, minValue=-10, maxValue=10, startVal=0, on_dragging=self.UpdateSizeSliderLabel, showLabel=False, increments=increments, idx=0)
        self.checkbox.selectedBgPadding = (-4,
         -4,
         -4,
         -4 - self.slider.height - 7)

    def UpdateSizeSliderLabel(self, slider):
        newText = '%s: %s' % (self.text, self.slider.GetValue())
        self.checkbox.SetLabelText(newText)


class AdvancedOptionsCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.fleetRegisterController = attributes.fleetRegisterController
        self.myAllianceCb = None
        self.myMilitiaCb = None
        self.leftSide = Container(parent=self, name='leftSide', align=uiconst.TOLEFT_PROP, width=0.5)
        self.rightSide = Container(parent=self, name='rightSide', padding=(85, 0, 10, 0))
        self.ConstructUI()

    def ConstructUI(self):
        self.leftSide.Flush()
        self.rightSide.Flush()
        self.myAllianceCb = None
        self.myMilitiaCb = None
        self.ConstructLeftSide()
        self.ConstructRightSide()
        self.ConstructButtons()
        self.UpdateUiElements()

    def ReloadCont(self):
        self.ConstructUI()
        self.LoadData()

    def ConstructLeftSide(self):
        EveLabelMedium(parent=self.leftSide, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Fleetup/OpenFleetTo'))
        self.myCorpCb = Checkbox(parent=self.leftSide, name='myCorpCb', align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Fleetup/MyCorporationCb'), hint=GetByLabel('UI/Agency/Fleetup/MyCorporationCbHint'), callback=self.OnCheckboxChecked)
        self.myAllianceCb = Checkbox(parent=self.leftSide, name='myAllianceCb', align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Fleetup/MyAllianceCb'), hint=GetByLabel('UI/Agency/Fleetup/MyAllianceCbHint'), callback=self.OnCheckboxChecked)
        self.myAllianceCb.display = bool(session.allianceid)
        self.myMilitiaCb = Checkbox(parent=self.leftSide, name='myMilitiaCb', align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Fleetup/MyMilitiaCb'), hint=GetByLabel('UI/Agency/Fleetup/MyMilitiaCbHint'), callback=self.OnCheckboxChecked)
        self.myMilitiaCb.display = bool(session.warfactionid)
        self.membergroupsMinReqStandingCb, self.membergroupsMinReqStandingSlider = self.AddCbAndSlider('minReqStandingMembergroupsCb', GetByLabel('UI/Agency/Fleetup/MinimumRequiredStandings'), GetByLabel('UI/Agency/Fleetup/MinimumRequiredStandingsHint'))
        self.membergroupsMinReqSecurityCb, self.membergroupsMinReqSecuritySlider = self.AddCbAndSlider('minReqSecurityCb', GetByLabel('UI/Agency/Fleetup/MinimumRequiredSecurityStatus'), GetByLabel('UI/Agency/Fleetup/MinimumRequiredSecurityStatusHint'))
        Line(parent=self.leftSide, align=uiconst.TOTOP, padTop=15, padBottom=15, opacity=0.05)
        self.publicCb = Checkbox(parent=self.leftSide, name='myMilitia', align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Fleetup/PubliclyAccessibleCb'), hint=GetByLabel('UI/Agency/Fleetup/PubliclyAccessibleCbHint'), callback=self.OnCheckboxChecked)
        self.publicMinReqStandingCb, self.publicMinReqStandingSlider = self.AddCbAndSlider('minReqStandingCb', GetByLabel('UI/Agency/Fleetup/MinimumRequiredStandings'), GetByLabel('UI/Agency/Fleetup/MinimumRequiredStandingsHint'))
        self.publicMinReqSecurityCb, self.publicMinReqSecuritySlider = self.AddCbAndSlider('minReqSecurity', GetByLabel('UI/Agency/Fleetup/MinimumRequiredSecurityStatus'), GetByLabel('UI/Agency/Fleetup/MinimumRequiredSecurityStatusHint'))

    def AddCbAndSlider(self, configName, text, moreInfoText):
        sliderAndLabel = SliderAndLabel(parent=self.leftSide, align=uiconst.TOTOP, padBottom=7, name=configName, configName=configName, text=text, moreInfoText=moreInfoText)
        sliderAndLabel.on_checkbox.connect(self.OnCheckboxChecked)
        return (sliderAndLabel.checkbox, sliderAndLabel.slider)

    def LoadData(self):
        self.ConstructUI()
        creationObject = self.fleetRegisterController.currentAd
        self.myCorpCb.SetValue(creationObject.IsAdvertOpenToCorp())
        self.myAllianceCb.SetValue(creationObject.IsAdvertOpenToAlliance())
        self.myMilitiaCb.SetValue(creationObject.IsAdvertOpenToMilitia())
        self.membergroupsMinReqStandingCb.SetValue(False if creationObject.membergroups_minStanding is None else True)
        self.membergroupsMinReqStandingSlider.SetValue(creationObject.membergroups_minStanding or 0)
        self.membergroupsMinReqSecurityCb.SetValue(False if creationObject.membergroups_minSecurity is None else True)
        self.membergroupsMinReqSecuritySlider.SetValue(creationObject.membergroups_minSecurity or 0)
        self.publicCb.SetValue(creationObject.IsAdvertOpenToAllPublic() or creationObject.IsAdvertOpenToPublic())
        self.publicMinReqStandingCb.SetValue(False if creationObject.public_minStanding is None else True)
        self.publicMinReqStandingSlider.SetValue(creationObject.public_minStanding or 0)
        self.publicMinReqSecurityCb.SetValue(False if creationObject.public_minSecurity is None else True)
        self.publicMinReqSecuritySlider.SetValue(creationObject.public_minSecurity or 0)
        self.adLimitCb.SetValue(False if creationObject.advertJoinLimit is None else True)
        self.adLimitEdit.SetValue(creationObject.advertJoinLimit or DEFAULT_JOIN_LIMIT)
        self.requireApprovalCb.SetValue(creationObject.joinNeedsApproval)
        self.hideDetailsCb.SetValue(creationObject.hideInfo)
        self.updateOnBossChangeCb.SetValue(not creationObject.updateOnBossChange)

    def ConstructRightSide(self):
        EveLabelMedium(parent=self.rightSide, align=uiconst.TOTOP, text=' ')
        self.adLimitCb = Checkbox(parent=self.rightSide, name='adLimitCb', align=uiconst.TOTOP, text=GetByLabel('UI/Fleet/FleetRegistry/AdvertJoinLimit'), callback=self.OnCheckboxChecked)
        self.adLimitCb.GetHint = self.GetAdvertJoinLimitHint
        adLimitEditCont = ContainerAutoSize(name='adLimitEditCont', parent=self.rightSide, align=uiconst.TOTOP, padLeft=30)
        self.adLimitEdit = SingleLineEditInteger(name='adLimitEdit', parent=adLimitEditCont, align=uiconst.TOPLEFT, minValue=1, maxValue=evefleet.MAX_MEMBERS_IN_FLEET, setvalue=DEFAULT_JOIN_LIMIT)
        adLimitEditCont.width = self.adLimitEdit.width
        Line(parent=self.rightSide, align=uiconst.TOTOP, padTop=15, padBottom=15, opacity=0.05)
        self.requireApprovalCb = Checkbox(parent=self.rightSide, name='requireApprovalCb', align=uiconst.TOTOP, text=GetByLabel('UI/Fleet/FleetRegistry/RequireApproval'), hint=GetByLabel('UI/Fleet/FleetRegistry/RequireApprovalHint'), callback=self.OnCheckboxChecked)
        self.hideDetailsCb = Checkbox(parent=self.rightSide, name='hideDetailsCb', align=uiconst.TOTOP, text=GetByLabel('UI/Fleet/FleetRegistry/HideInfo'), hint=GetByLabel('UI/Fleet/FleetRegistry/HideInfoHint'), callback=self.OnCheckboxChecked)
        self.updateOnBossChangeCb = Checkbox(parent=self.rightSide, name='updateOnBossChangeCb', align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Fleetup/DontUpdateOnBossChangeCb'), hint=GetByLabel('UI/Agency/Fleetup/DontUpdateOnBossChangeCbHint'), callback=self.OnCheckboxChecked)

    def GetAdvertJoinLimitHint(self, *args):
        limit = self.adLimitEdit.GetValue()
        hint = GetByLabel('UI/Fleet/FleetRegistry/AdvertJoinLimitHint', advertJoinLimit=limit)
        return hint

    def ConstructButtons(self):
        btnCont = ContainerAutoSize(parent=self, align=uiconst.BOTTOMRIGHT)
        cancelBtn = Button(name='cancelBtn', parent=btnCont, align=uiconst.BOTTOMRIGHT, label=GetByLabel('UI/Commands/Cancel'), func=self.CancelClicked)
        Button(name='saveBtn', parent=btnCont, align=uiconst.BOTTOMRIGHT, label=GetByLabel('UI/Common/Buttons/Save'), variant=ButtonVariant.PRIMARY, func=self.SaveAdvanced, left=cancelBtn.left + cancelBtn.width + 10)

    def CancelClicked(self, *args):
        self.fleetRegisterController.on_load_basic()

    def SaveAdvanced(self, *arg):
        adInfo = self.fleetRegisterController.currentAd
        adInfo.ResetInviteScope()
        adInfo.ResetAdvancedOptions()
        if self.myCorpCb.checked:
            adInfo.AddToInviteScopeMask(evefleet.INVITE_CORP)
        if session.allianceid and self.myAllianceCb and self.myAllianceCb.checked:
            adInfo.AddToInviteScopeMask(evefleet.INVITE_ALLIANCE)
        if session.warfactionid and self.myMilitiaCb and self.myMilitiaCb.checked:
            adInfo.AddToInviteScopeMask(evefleet.INVITE_MILITIA)
        addressbookSvc = sm.GetService('addressbook')
        if adInfo.IsOpenToMemberEntities():
            if self.membergroupsMinReqStandingCb.checked:
                minMembergroupStandings = self.membergroupsMinReqStandingSlider.GetValue()
                if minMembergroupStandings < -10 or minMembergroupStandings > 10:
                    raise UserError('FleetInviteWithInappropriateStandings')
                adInfo.membergroups_minStanding = minMembergroupStandings
            else:
                allowedGroups = FleetSvc().GetAllowedGroupIDs(adInfo)
                adInfo.membergroups_allowedEntities = allowedGroups
            if self.membergroupsMinReqSecurityCb.checked:
                adInfo.membergroups_minSecurity = self.membergroupsMinReqSecuritySlider.GetValue()
        if self.publicCb.checked:
            adInfo.AddToInviteScopeMask(evefleet.INVITE_PUBLIC_OPEN)
            if self.publicMinReqStandingCb.checked:
                minPublicStandings = self.publicMinReqStandingSlider.GetValue()
                if minPublicStandings < -10 or minPublicStandings > 10:
                    raise UserError('FleetInviteWithInappropriateStandings')
                adInfo.public_minStanding = minPublicStandings
            if self.publicMinReqSecurityCb.checked:
                adInfo.public_minSecurity = self.publicMinReqSecuritySlider.GetValue()
        if self.adLimitCb.checked:
            adInfo.advertJoinLimit = self.adLimitEdit.GetValue()
        adInfo.joinNeedsApproval = self.requireApprovalCb.checked
        adInfo.hideInfo = self.hideDetailsCb.checked
        adInfo.updateOnBossChange = not self.updateOnBossChangeCb.checked
        settings.char.ui.Set('fleetAdvert_lastAdvertAdvancedOptions', dict(adInfo.GetLimitedAdvancedOptionsData()))
        self.fleetRegisterController.on_advanced_saved()

    def OnCheckboxChecked(self, *args):
        self.UpdateUiElements()

    def UpdateUiElements(self):
        groupCbs = filter(None, [self.myCorpCb, self.myAllianceCb, self.myMilitiaCb])
        groupChecked = any((x.checked for x in groupCbs))
        publicChecked = self.publicCb.checked
        for cb, slider, isEnabled in [(self.membergroupsMinReqStandingCb, self.membergroupsMinReqStandingSlider, groupChecked),
         (self.membergroupsMinReqSecurityCb, self.membergroupsMinReqSecuritySlider, groupChecked),
         (self.publicMinReqStandingCb, self.publicMinReqStandingSlider, publicChecked),
         (self.publicMinReqSecurityCb, self.publicMinReqSecuritySlider, publicChecked)]:
            if isEnabled:
                cb.Enable()
                if cb.checked:
                    slider.Enable()
                else:
                    slider.Disable()
            else:
                cb.Disable()
                slider.Disable()


class BasicOptionsCont(Container):
    default_padTop = 32

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.fleetRegisterController = attributes.fleetRegisterController
        leftWidth = 0.46
        leftSide = Container(parent=self, name='leftSide', align=uiconst.TOLEFT_PROP, width=leftWidth)
        rightSide = Container(parent=self, name='rightSide', padding=(100, 0, 10, 0))
        self.nameEdit = SingleLineEditText(name='nameEdit', parent=leftSide, align=uiconst.TOTOP, hintText=GetByLabel('UI/Agency/Fleetup/FleetNameHint'), fontsize=18, height=40, maxLength=evefleet.FLEETNAME_MAXLENGTH, showLetterCounter=True, padBottom=40, clipperPadLeft=14, clipperPadRight=14)
        self.fleetDescLalbel = Label(parent=leftSide, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Fleetup/DescriptionForOwnAd'), fontsize=EVE_LARGE_FONTSIZE)
        self.fleetDescEdit = EditPlainText(parent=leftSide, hasUnderlay=False, hintText=GetByLabel('UI/Agency/Fleetup/DescriptionForOwnAdHint'), maxLength=evefleet.FLEETDESC_MAXLENGTH, align=uiconst.TOTOP, height=280)
        options = [ (v, k) for k, v in GetAllFleetActivities().iteritems() ]
        options.sort(key=lambda x: x[0].lower())
        self.activityPickerCombo = Combo(parent=rightSide, options=options, name='fleetup_activityPicker', align=uiconst.TOPLEFT, label=GetByLabel('UI/Agency/Fleetup/SelectFleetActivity'), adjustWidth=True)
        self.ContructCheckboxesAndExtraInfo(rightSide)
        self.ConstructButtons()
        self.LoadData()

    def ContructCheckboxesAndExtraInfo(self, rightSide):
        self.hideFleetCb = Checkbox(parent=rightSide, name='hideFleetCb', align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Fleetup/HideFleetCb'), top=self.activityPickerCombo.top + self.activityPickerCombo.height + 25, hint=GetByLabel('UI/Agency/Fleetup/HideFleetCbHint'), callback=self.OnCheckboxChecked)
        self.newPlayerFriendlyCb = Checkbox(parent=rightSide, name='newPlayerFriendlyCb', align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Fleetup/NewPlayerFriendlyCb'), hint=GetByLabel('UI/Agency/Fleetup/NewPlayerFriendlyCbHint'))
        self.useAdvancedCb = Checkbox(parent=rightSide, name='useAdvancedCb', align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Fleetup/UseAdvancedOptionsCb'), hint=GetByLabel('UI/Agency/Fleetup/UseAdvancedOptionsCbHint'), callback=self.OnAdvancedCheckboxChecked)
        self.privateWarningCont = WarningContainer(parent=rightSide, align=uiconst.TOTOP, height=40, text=GetByLabel('UI/Agency/Fleetup/PrivateWarning'), top=20, textAlignment=uiconst.TOTOP)
        self.privateWarningCont.display = False
        self.advancecdText = Label(parent=rightSide, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, top=10, padLeft=10)
        self.advancecdText.display = False

    def ConstructButtons(self):
        btnCont = LayoutGrid(columns=3, parent=self, align=uiconst.BOTTOMRIGHT, cellSpacing=(10, 0))
        advancedBtn = Button(name='advancedBtn', align=uiconst.BOTTOMRIGHT, label=GetByLabel('UI/Agency/Fleetup/AdvancedBtn'), func=self.GoToAdvanced)
        self.registerBtn = Button(name='registerBtn', align=uiconst.BOTTOMRIGHT, label=GetByLabel('UI/Agency/Fleetup/RegisterFleetBn'), variant=ButtonVariant.PRIMARY, func=self.RegisterFleet, fixedheight=40)
        btnCont.AddCell(self.registerBtn)
        btnCont.AddCell(advancedBtn)
        cancelBtn = Button(name='cancelBtn', parent=btnCont, align=uiconst.BOTTOMRIGHT, label=GetByLabel('UI/Commands/Cancel'), func=self.CancelClicked)

    def LoadData(self):
        if session.fleetid and not FleetSvc().IsBoss():
            return
        if not self.fleetRegisterController.HasCurrentAd():
            if not session.fleetid or not FleetSvc().IsFleetRegistered():
                fleetInfo = settings.char.ui.Get('fleetAdvert_lastAdvert', {})
                if fleetInfo:
                    if isinstance(fleetInfo, KeyVal):
                        fleetInfo = fleetInfo.__dict__
                    self.fleetRegisterController.currentAd = FleetAdvertCreationObject(**fleetInfo)
            if not self.fleetRegisterController.currentAd.useAdvanceOptions:
                advancedOptions = settings.char.ui.Get('fleetAdvert_lastAdvertAdvancedOptions', {})
                for k, v in advancedOptions.iteritems():
                    setattr(self.fleetRegisterController.currentAd, k, v)

        fleetAd = self.fleetRegisterController.currentAd
        self.nameEdit.SetValue(fleetAd.fleetName)
        self.fleetDescEdit.SetValue(fleetAd.description)
        self.activityPickerCombo.SetValue(fleetAd.activityValue)
        self.useAdvancedCb.SetValue(fleetAd.useAdvanceOptions)
        self.newPlayerFriendlyCb.SetValue(fleetAd.newPlayerFriendly)

    def RegisterFleet(self, *args):
        if self.hideFleetCb.checked:
            adInfo = None
        else:
            fleetName = self.nameEdit.GetValue().strip()
            desc = self.fleetDescEdit.GetValue().strip()
            newPlayerFriendly = self.newPlayerFriendlyCb.checked
            if len(fleetName) < 1:
                raise UserError('CustomInfo', {'info': GetByLabel('UI/Agency/Fleetup/FleetNameRequired')})
            activityValue = self.activityPickerCombo.GetValue()
            if self.useAdvancedCb.checked:
                self.PopulateAllowedAndBannedEntities(self.fleetRegisterController.currentAd)
                advancedOptions = self.fleetRegisterController.currentAd.GetAllAdvancedOptionsData()
                inviteScope = self.fleetRegisterController.currentAd.inviteScope
                useAdvanced = True
            else:
                advancedOptions = {}
                inviteScope = evefleet.INVITE_PUBLIC_OPEN
                useAdvanced = False
            adInfo = FleetAdvertCreationObject(fleetName=fleetName, description=desc, activityValue=activityValue, inviteScope=inviteScope, newPlayerFriendly=newPlayerFriendly, useAdvanceOptions=useAdvanced, **advancedOptions)
        sm.GetService('fleet').CreateAndRegisterFleet(adInfo)
        agencySignals.on_content_group_selected(contentGroupConst.contentGroupFleetUp, setPending=True)

    def PopulateAllowedAndBannedEntities(self, adInfo):
        addressbookSvc = sm.GetService('addressbook')
        minMembergroupStandings = adInfo.membergroups_minStanding
        atOrAboveStanding, belowStanding = addressbookSvc.GetContactsAboveAndBelowRelationship(minMembergroupStandings)
        adInfo.membergroups_allowedEntities = atOrAboveStanding
        adInfo.membergroups_disallowedEntities = belowStanding if minMembergroupStandings <= 0 else set()
        minPublicStandings = adInfo.public_minStanding
        atOrAboveStanding, belowStanding = addressbookSvc.GetContactsAboveAndBelowRelationship(minPublicStandings)
        adInfo.public_allowedEntities = atOrAboveStanding
        adInfo.public_disallowedEntities = belowStanding if minPublicStandings <= 0 else set()

    def CancelClicked(self, *args):
        agencySignals.on_content_group_selected(contentGroupConst.contentGroupFleetUp)

    def GoToAdvanced(self, *args):
        self.fleetRegisterController.on_load_advanced()

    def OnCheckboxChecked(self, *args):
        self.UpdateUI()

    def OnAdvancedCheckboxChecked(self, cb):
        self.fleetRegisterController.currentAd.useAdvanceOptions = cb.checked
        self.UpdateUI()

    def UpdateUI(self, animate = False):
        self.advancecdText.display = False
        if self.hideFleetCb.checked:
            self.useAdvancedCb.Disable()
            self.newPlayerFriendlyCb.Disable()
            self.privateWarningCont.display = True
            self.nameEdit.Disable()
            self.fleetDescEdit.Disable()
            self.fleetDescLalbel.opacity = 0.1
            self.activityPickerCombo.Disable()
        else:
            self.nameEdit.Enable()
            self.fleetDescEdit.Enable()
            self.fleetDescLalbel.opacity = TextColor.NORMAL.opacity
            self.activityPickerCombo.Enable()
            self.useAdvancedCb.Enable()
            self.newPlayerFriendlyCb.Enable()
            self.privateWarningCont.display = False
            self.advancecdText.text = self.GetAdvancedText()
            self.advancecdText.display = True
            if self.useAdvancedCb.checked and not self.advancecdText.text:
                self.advancecdText.text = GetByLabel('UI/Agency/Fleetup/UsingDefaultsSummary')
        if FleetSvc().IsFleetRegistered():
            self.registerBtn.label = GetByLabel('UI/Agency/Fleetup/UpdateRegistration')
        else:
            self.registerBtn.label = GetByLabel('UI/Agency/Fleetup/RegisterFleetBn')
        if session.fleetid:
            if FleetSvc().IsFleetRegistered():
                analyticID = evefleet.UPDATE_AD_BTN_ANALYTIC_ID
            else:
                analyticID = evefleet.REGISTER_AD_ANALYTIC_ID
        elif self.hideFleetCb.checked:
            analyticID = evefleet.CREATE_FLEET_ANALYTIC_ID
        else:
            analyticID = evefleet.CREATE_FLEET_AND_REGISTER_AD_ANALYTIC_ID
        self.registerBtn.analyticID = analyticID

    def GetAdvancedText(self):
        if not self.useAdvancedCb.checked:
            return ''
        return '<br><br>'.join([self.GetScopeText(), self.GetOtherOptionText()])

    def GetScopeText(self):
        currentAd = self.fleetRegisterController.currentAd
        scopeLines = []
        if currentAd.inviteScope == evefleet.INVITE_CLOSED:
            return GetByLabel('UI/Agency/Fleetup/NoOneHasAccess')
        if currentAd.IsAdvertOpenToCorp():
            text = GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/CorporationAccessScope', corpName=cfg.eveowners.Get(session.corpid).name, corpInfo=('showinfo', invConst.typeCorporation, session.corpid))
            text = StripTags(text, stripOnly='br')
            scopeLines.append(text)
        if currentAd.IsAdvertOpenToAlliance() and session.allianceid:
            text = GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/AllianceAccessScope', allianceName=cfg.eveowners.Get(session.allianceid).name, allianceInfo=('showinfo', invConst.typeAlliance, session.allianceid))
            text = StripTags(text, stripOnly='br')
            scopeLines.append(text)
        if currentAd.IsAdvertOpenToMilitia() and session.warfactionid:
            text = GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/MilitiaAccessScope', militiaName=cfg.eveowners.Get(session.warfactionid).name, militiaInfo=('showinfo', invConst.typeFaction, session.warfactionid))
            text = StripTags(text, stripOnly='br')
            scopeLines.append(text)
        if currentAd.membergroups_minStanding is not None or currentAd.membergroups_minSecurity is not None:
            if currentAd.membergroups_minStanding is not None:
                standing = currentAd.membergroups_minStanding
                if currentAd.membergroups_minSecurity is not None:
                    scopeLines.append(GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/MinimumStandingAndSecurity', standing=standing, security=currentAd.membergroups_minSecurity))
                else:
                    scopeLines.append(GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/MinimumStanding', standing=standing))
            elif currentAd.membergroups_minSecurity is not None:
                scopeLines.append(GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/MinimumSecurity', security=currentAd.membergroups_minSecurity))
        if currentAd.IsAdvertOpenToAllPublic() or currentAd.IsAdvertOpenToPublic():
            if scopeLines:
                scopeLines.append('')
            scopeLines.append(GetByLabel('UI/Agency/Fleetup/Public Access'))
            if currentAd.public_minStanding is not None:
                standing = currentAd.public_minStanding
                if currentAd.public_minSecurity is not None:
                    scopeLines.append(GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/MinimumStandingAndSecurity', standing=standing, security=currentAd.public_minSecurity))
                else:
                    scopeLines.append(GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/MinimumStanding', standing=standing))
            elif currentAd.public_minSecurity is not None:
                scopeLines.append(GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/MinimumSecurity', security=currentAd.public_minSecurity))
        if not scopeLines:
            scopeLines.append('-')
        return '<br>'.join(scopeLines)

    def GetOtherOptionText(self):
        currentAd = self.fleetRegisterController.currentAd
        textList = []
        if currentAd.joinNeedsApproval:
            textList.append(GetByLabel('UI/Agency/Fleetup/ApplicationRequiresApprovalSummary'))
        if currentAd.hideInfo:
            textList.append(GetByLabel('UI/Agency/Fleetup/FleetDetailsHiddenSummary'))
        if currentAd.newPlayerFriendly:
            textList.append(GetByLabel('UI/Agency/Fleetup/NewPlayerFriendlySummary'))
        if not currentAd.updateOnBossChange:
            textList.append(GetByLabel('UI/Agency/Fleetup/AdverNotUpdatedOnBossChangeSummary'))
        if currentAd.advertJoinLimit:
            textList.append(GetByLabel('UI/Agency/Fleetup/JoinsLimitedSummary', maxThroughJoin=currentAd.advertJoinLimit))
        return ', '.join(textList)
