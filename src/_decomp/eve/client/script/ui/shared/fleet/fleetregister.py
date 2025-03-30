#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fleet\fleetregister.py
import evefleet
import localization
import mathext
from carbonui import uiconst
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.line import Line
from eve.client.script.ui.control import eveLabel
from carbonui.button.group import ButtonGroup
from carbonui.control.checkbox import Checkbox
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from carbonui.control.window import Window
from eve.common.lib.appConst import contactGoodStanding, contactHighStanding
from eveexceptions import UserError
from evefleet.fleetAdvertObject import FleetAdvertCreationObject
WINDOW_WIDTH = 600
DEFAULT_JOIN_LIMIT = 250

class RegisterFleetWindow(Window):
    __guid__ = 'form.RegisterFleetWindow'
    default_windowID = 'RegisterFleetWindow'
    default_width = WINDOW_WIDTH

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        fleetInfo = attributes.fleetInfo
        self.SetCaption(localization.GetByLabel('UI/Fleet/CreateAdvert'))
        self.MakeUnResizeable()
        self.sr.scopeRadioButtons = []
        self.SetupStuff(fleetInfo)

    def SetupStuff(self, fleetInfo = None):
        publicIsGood = False
        publicIsHigh = False
        localIsGood = False
        localIsHigh = False
        if not fleetInfo:
            fleetInfo = settings.char.ui.Get('fleetAdvert_lastAdvert', {})
        fleetName = fleetInfo.get('fleetName', localization.GetByLabel('UI/Fleet/DefaultFleetName', char=session.charid))
        description = fleetInfo.get('description', '')
        needsApproval = fleetInfo.get('joinNeedsApproval', False)
        hideInfo = fleetInfo.get('hideInfo', False)
        updateOnBossChange = fleetInfo.get('updateOnBossChange', False)
        advertJoinLimit = fleetInfo.get('advertJoinLimit', None)
        membergroupsMinStanding = fleetInfo.get('membergroups_minStanding', None)
        membergroupsMinSecurity = fleetInfo.get('membergroups_minSecurity', None)
        publicMinStanding = fleetInfo.get('public_minStanding', None)
        publicMinSecurity = fleetInfo.get('public_minSecurity', None)
        myCorp = evefleet.IsOpenToCorp(fleetInfo)
        myAlliance = evefleet.IsOpenToAlliance(fleetInfo)
        myMilitia = evefleet.IsOpenToMilitia(fleetInfo)
        isPublic = evefleet.IsOpenToPublic(fleetInfo)
        if publicMinStanding == contactGoodStanding:
            publicIsGood = True
        elif publicMinStanding == contactHighStanding:
            publicIsHigh = True
        if membergroupsMinStanding == contactGoodStanding:
            localIsGood = True
        elif membergroupsMinStanding == contactHighStanding:
            localIsHigh = True
        self.sr.main.Flush()
        self.sr.submitButtons = ButtonGroup(btns=[[localization.GetByLabel('UI/Common/Buttons/Submit'), self.Submit, ()], [localization.GetByLabel('UI/Common/Buttons/Cancel'), self.CloseByUser, ()]], parent=self.sr.main, idx=0, padLeft=-self.sr.main.padLeft, padRight=-self.sr.main.padRight)
        gridContainer = GridContainer(name='myGridCont', parent=self.sr.main, align=uiconst.TOALL, columns=2, lines=1)
        leftCont = Container(name='leftCont', parent=gridContainer, padding=(14, 0, 10, 0))
        rightCont = Container(name='rightCont', parent=gridContainer, padding=(10, 0, 14, 0))
        Line(parent=leftCont, align=uiconst.TORIGHT_NOPUSH, padRight=-10)
        eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Fleet/NameOfFleet'), parent=leftCont, align=uiconst.TOTOP)
        self.sr.fleetName = SingleLineEditText(name='fleetName', parent=leftCont, align=uiconst.TOTOP, maxLength=evefleet.FLEETNAME_MAXLENGTH, setvalue=fleetName)
        eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Fleet/Description'), parent=leftCont, padTop=10, align=uiconst.TOTOP_NOPUSH)
        self.sr.description = EditPlainText(setvalue=description, parent=leftCont, align=uiconst.TOTOP, height=150, maxLength=evefleet.FLEETDESC_MAXLENGTH, showattributepanel=True, padTop=6)
        self.sr.description.sr.attribPanel.HideEditOptions()
        eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Fleet/FleetRegistry/OpenFleetTo'), parent=rightCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.sr.myCorpButton = Checkbox(text=localization.GetByLabel('UI/Fleet/FleetRegistry/MyCorporation'), parent=rightCont, settingsKey='corp', checked=myCorp, hint=localization.GetByLabel('UI/Fleet/FleetRegistry/CorpOnlyHint'), callback=self.OnGroupCbChanged)
        if session.allianceid is not None:
            self.sr.myAllianceButton = Checkbox(text=localization.GetByLabel('UI/Fleet/FleetRegistry/MyAlliance'), parent=rightCont, settingsKey='alliance', checked=myAlliance, hint=localization.GetByLabel('UI/Fleet/FleetRegistry/AllianceOnlyHint'), align=uiconst.TOTOP, callback=self.OnGroupCbChanged)
        if session.warfactionid is not None:
            self.sr.myMilitiaButton = Checkbox(text=localization.GetByLabel('UI/Fleet/FleetRegistry/MyMilitia'), parent=rightCont, settingsKey='militia', checked=myMilitia, hint=localization.GetByLabel('UI/Fleet/FleetRegistry/MyMilitiahint'), align=uiconst.TOTOP, callback=self.OnGroupCbChanged)
        self.sr.requireLocalStandingButton = Checkbox(text=localization.GetByLabel('UI/Fleet/FleetRegistry/RequireStanding'), parent=rightCont, settingsKey='requireLocalStanding', checked=bool(membergroupsMinStanding), align=uiconst.TOTOP, hint=localization.GetByLabel('UI/Fleet/FleetRegistry/RequireStandingHint'), padLeft=18)
        self.sr.localGoodStandingCB = RadioButton(text=localization.GetByLabel('UI/Standings/Good'), parent=rightCont, settingsKey='localgood', retval=contactGoodStanding, checked=localIsGood, groupname='localStanding', align=uiconst.TOTOP, padLeft=36)
        self.sr.localHighStandingCB = RadioButton(text=localization.GetByLabel('UI/Standings/Excellent'), parent=rightCont, settingsKey='localhigh', retval=contactHighStanding, checked=localIsHigh, groupname='localStanding', align=uiconst.TOTOP, padLeft=36)
        startVal = 0.5
        if membergroupsMinSecurity is not None:
            startVal = membergroupsMinSecurity / 20.0 + 0.5
        self.sr.requireLocalSecurityButton = Checkbox(text=localization.GetByLabel('UI/Fleet/FleetRegistry/RequireSecurity', securityLevel=startVal), parent=rightCont, settingsKey='requireLocalSecurity', checked=membergroupsMinSecurity is not None, align=uiconst.TOTOP, padLeft=18, hint=localization.GetByLabel('UI/Fleet/FleetRegistry/RequireSecurityHint'))
        self.sr.localSecuritySlider = self.AddSlider(rightCont, 'localSecurity', -10, 10.0, '', startVal=startVal, padLeft=18)
        self.sr.publicButton = Checkbox(text=localization.GetByLabel('UI/Fleet/FleetRegistry/BasedOnStandings'), parent=rightCont, settingsKey='public', checked=isPublic, align=uiconst.TOTOP, hint=localization.GetByLabel('UI/Fleet/FleetRegistry/AddPilots'), callback=self.OnStandingCbChanged)
        self.sr.requireStandingLabel = eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Fleet/FleetRegistry/RequireStanding'), parent=rightCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padLeft=18)
        self.sr.publicGoodStandingCB = RadioButton(text=localization.GetByLabel('UI/Standings/Good'), parent=rightCont, settingsKey='publicgood', retval=contactGoodStanding, checked=publicIsGood, groupname='publicStanding', align=uiconst.TOTOP, padLeft=18)
        self.sr.publicHighStandingCB = RadioButton(text=localization.GetByLabel('UI/Standings/Excellent'), parent=rightCont, settingsKey='publichigh', retval=contactHighStanding, checked=publicIsHigh, groupname='publicStanding', align=uiconst.TOTOP, padLeft=18)
        startVal = 0.5
        if publicMinSecurity is not None:
            startVal = publicMinSecurity / 20.0 + 0.5
        self.sr.requirePublicSecurityButton = Checkbox(text=localization.GetByLabel('UI/Fleet/FleetRegistry/RequireSecurity', securityLevel=startVal), parent=rightCont, settingsKey='requirePublicSecurity', checked=publicMinSecurity is not None, hint=localization.GetByLabel('UI/Fleet/FleetRegistry/RequireSecurityHint'), padLeft=18)
        self.sr.publicSecuritySlider = self.AddSlider(rightCont, 'publicSecurity', -10, 10.0, '', startVal=startVal, padLeft=18)
        self.sr.needsApprovalButton = Checkbox(text=localization.GetByLabel('UI/Fleet/FleetRegistry/RequireApproval'), parent=leftCont, settingsKey='needsApproval', checked=needsApproval, hint=localization.GetByLabel('UI/Fleet/FleetRegistry/RequireApprovalHint'))
        self.sr.hideInfoButton = Checkbox(text=localization.GetByLabel('UI/Fleet/FleetRegistry/HideInfo'), parent=leftCont, settingsKey='hideInfo', checked=hideInfo, hint=localization.GetByLabel('UI/Fleet/FleetRegistry/HideInfoHint'))
        self.sr.updateOnBossChangeCb = Checkbox(text=localization.GetByLabel('UI/Fleet/FleetRegistry/UpdateOnBossChange'), parent=leftCont, settingsKey='updateOnBossChange', checked=updateOnBossChange, hint=localization.GetByLabel('UI/Fleet/FleetRegistry/UpdateOnBossChangeHint'))
        self.sr.canJoinThroughAdLimitCb = Checkbox(text=localization.GetByLabel('UI/Fleet/FleetRegistry/AdvertJoinLimit'), parent=leftCont, settingsKey='advertJoinLimit', checked=bool(advertJoinLimit), padBottom=6, callback=self.OnLimitJoinCb)
        self.sr.canJoinThroughAdLimitCb.GetHint = self.GetAdvertJoinLimitHint
        self.sr.limtedJoinEdit = SingleLineEditInteger(name='edit', parent=leftCont, align=uiconst.TOTOP, padding=(30, 0, 150, 0), minValue=1, maxValue=evefleet.MAX_MEMBERS_IN_FLEET, setvalue=advertJoinLimit or DEFAULT_JOIN_LIMIT)
        leftChildrenHeight = sum([ each.height + each.padTop + each.padBottom for each in leftCont.children ])
        rightChildrenHeight = sum([ each.height + each.padTop + each.padBottom for each in rightCont.children ])
        childrenHeight = max(leftChildrenHeight, rightChildrenHeight)
        windowHeight = childrenHeight + self.header_height + gridContainer.padTop + gridContainer.padBottom + self.sr.submitButtons.height
        self.SetMinSize([WINDOW_WIDTH, windowHeight], refresh=True)
        self.ChangeLocalDisplay()
        self.ChangePublicDisplay()
        self.ChangeLimitJoinDisplay()

    def GetAdvertJoinLimitHint(self, *args):
        limit = self.sr.limtedJoinEdit.GetValue()
        hint = localization.GetByLabel('UI/Fleet/FleetRegistry/AdvertJoinLimitHint', advertJoinLimit=limit)
        return hint

    def OnGroupCbChanged(self, *args):
        self.ChangeLocalDisplay()

    def ChangeLocalDisplay(self):
        groupCbs = filter(None, [self.sr.myCorpButton, self.sr.myAllianceButton, self.sr.myMilitiaButton])
        groupChecked = any((x.GetValue() for x in groupCbs))
        subElements = [self.sr.requireLocalStandingButton,
         self.sr.localGoodStandingCB,
         self.sr.localHighStandingCB,
         self.sr.requireLocalSecurityButton,
         self.sr.localSecuritySlider]
        self.EnableOrDisableElements(groupChecked, subElements)

    def OnStandingCbChanged(self, *args):
        self.ChangePublicDisplay()

    def ChangePublicDisplay(self):
        isChecked = self.sr.publicButton.GetValue()
        subElements = [self.sr.requireStandingLabel,
         self.sr.publicGoodStandingCB,
         self.sr.publicHighStandingCB,
         self.sr.requirePublicSecurityButton,
         self.sr.publicSecuritySlider]
        self.EnableOrDisableElements(isChecked, subElements)

    def EnableOrDisableElements(self, isEnabled, subElements):
        for eachElement in subElements:
            if isEnabled:
                eachElement.Enable()
                eachElement.opacity = 1.0
            else:
                eachElement.Disable()
                eachElement.opacity = 0.3

    def OnLimitJoinCb(self, *args):
        self.ChangeLimitJoinDisplay()

    def ChangeLimitJoinDisplay(self):
        self.EnableOrDisableElements(self.sr.canJoinThroughAdLimitCb.GetValue(), [self.sr.limtedJoinEdit])

    def AddSlider(self, where, config, minval, maxval, header, hint = '', startVal = 0, padLeft = 0):
        _par = Container(name=config + '_slider', parent=where, align=uiconst.TOTOP, padLeft=padLeft, height=10)
        if startVal < minval:
            startVal = minval
        slider = Slider(name=config + '_slider_sub', parent=_par, align=uiconst.TOPLEFT, pos=(18, 0, 180, 10), minValue=minval, maxValue=maxval, value=startVal, config=config, hint=hint, on_dragging=getattr(self, 'OnSetValue_%s' % config))
        return slider

    def OnSetValue_localSecurity(self, slider):
        self.sr.requireLocalSecurityButton.SetLabelText(localization.GetByLabel('UI/Fleet/FleetRegistry/RequireSecurity', securityLevel=slider.GetValue()))

    def OnSetValue_publicSecurity(self, slider):
        self.sr.requirePublicSecurityButton.SetLabelText(localization.GetByLabel('UI/Fleet/FleetRegistry/RequireSecurity', securityLevel=slider.GetValue()))

    def Submit(self):
        fleetSvc = sm.GetService('fleet')
        adInfo = FleetAdvertCreationObject(fleetName=self.sr.fleetName.GetValue(), description=self.sr.description.GetValue(), useAdvanceOptions=True)
        if self.sr.myCorpButton.checked:
            adInfo.AddToInviteScopeMask(evefleet.INVITE_CORP)
        if session.allianceid and self.sr.myAllianceButton.checked:
            adInfo.AddToInviteScopeMask(evefleet.INVITE_ALLIANCE)
        if session.warfactionid and self.sr.myMilitiaButton.checked:
            adInfo.AddToInviteScopeMask(evefleet.INVITE_MILITIA)
        if self.sr.publicButton.checked:
            adInfo.AddToInviteScopeMask(evefleet.INVITE_PUBLIC)
            if self.sr.publicGoodStandingCB.checked:
                minPublicStandings = contactGoodStanding
            elif self.sr.publicHighStandingCB.checked:
                minPublicStandings = contactHighStanding
            else:
                raise UserError('FleetInviteAllWithoutStanding')
            adInfo.public_minStanding = minPublicStandings
            adInfo.public_allowedEntities = self.GetAllowedEntities(minPublicStandings)
            if self.sr.requirePublicSecurityButton.checked:
                adInfo.public_minSecurity = self.sr.publicSecuritySlider.value
        noAccess = False
        if adInfo.IsOpenToMemberEntities():
            if self.sr.requireLocalStandingButton.checked:
                if self.sr.localGoodStandingCB.checked:
                    minMembergroupStandings = contactGoodStanding
                elif self.sr.localHighStandingCB.checked:
                    minMembergroupStandings = contactHighStanding
                else:
                    raise UserError('FleetInviteAllWithoutStanding')
                adInfo.membergroups_minStanding = minMembergroupStandings
                adInfo.membergroups_allowedEntities = self.GetAllowedEntities(minMembergroupStandings)
            else:
                allowedGroups = fleetSvc.GetAllowedGroupIDs(adInfo)
                adInfo.membergroups_allowedEntities = allowedGroups
            if self.sr.requireLocalSecurityButton.checked:
                adInfo.membergroups_minSecurity = self.sr.localSecuritySlider.value
        elif not evefleet.IsOpenToPublic(adInfo):
            noAccess = True
        if adInfo.IsOpenToPublicThroughStandings():
            if not adInfo.GetNumAllowedEntities():
                noAccess = True
        if noAccess:
            if eve.Message('FleetNobodyHasAccess', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return
        adInfo.joinNeedsApproval = bool(self.sr.needsApprovalButton.checked)
        adInfo.hideInfo = bool(self.sr.hideInfoButton.checked)
        adInfo.updateOnBossChange = bool(self.sr.updateOnBossChangeCb.GetValue())
        if self.sr.canJoinThroughAdLimitCb.GetValue():
            limit = self.sr.limtedJoinEdit.GetValue()
            limit = mathext.clamp(limit, 1, evefleet.MAX_MEMBERS_IN_FLEET)
            adInfo.advertJoinLimit = limit
        fleetSvc.RegisterFleet(adInfo)
        settings.char.ui.Set('fleetAdvert_lastAdvertAdvancedOptions', dict(adInfo.GetLimitedAdvancedOptionsData()))
        self.CloseByUser()

    def GetAllowedEntities(self, minRelationship):
        return sm.GetService('addressbook').GetContactsByMinRelationship(minRelationship)
