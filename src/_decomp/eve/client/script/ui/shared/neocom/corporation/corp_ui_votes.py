#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_votes.py
import sys
import blue
import evetypes
import localization
import log
import uthread
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import SortListOfTuples
from corporation import voting
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.button import ButtonEntry
from eve.client.script.ui.control.entries.combo import ComboEntry
from eve.client.script.ui.control.entries.divider import DividerEntry
from eve.client.script.ui.control.entries.edit import EditEntry
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.label_text import LabelText, LabelTextTop
from eve.client.script.ui.control.entries.text import Text
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.client.script.ui.util import uix
from eve.common.lib import appConst as const
from eve.common.script.sys.eveCfg import IsDocked, IsControllingStructure
from eveexceptions import ExceptionEater
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
BTN_HIDDEN = 0
BTN_ENABLED = 1
BTN_DISABLED = 2

class WizardDialogBase(Window):
    __guid__ = 'form.WizardDialogBase'
    _back_button = None
    _cancel_button = None
    _next_button = None
    _ok_button = None

    def OnOK(self, *args):
        self.closedByOK = 1
        self.CloseByUser()

    def OnCancel(self, *args):
        self.CloseByUser()

    def GetNextStep(self):
        return self.step + 1

    def GetPreviousStep(self):
        return self.step - 1

    def OnNext(self, *args):
        self.GoToStep(self.GetNextStep())

    def OnBack(self, *args):
        self.GoToStep(self.GetPreviousStep())

    def GoToStep(self, requestedStep = 1, reload = 0):
        try:
            log.LogInfo('GoToStep requestedStep:', requestedStep, 'reload:', reload, 'self.step:', self.step)
            if self.step == requestedStep and not reload:
                log.LogInfo('GoToStep - Ignoring')
                return
            if not reload and self.step in self.steps:
                data = self.steps[self.step]
                if data is not None:
                    title, funcIn, funcOut = data
                    if funcOut is not None:
                        log.LogInfo('GoToStep - running funcOut', funcOut)
                        try:
                            bCan = funcOut(requestedStep)
                            if not bCan:
                                log.LogInfo('GoToStep - funcOut disallowed continuation to next step')
                                return
                        finally:
                            self.HideLoad()

            data = self.steps[requestedStep]
            scrolllist = []
            if data is not None:
                title, funcIn, funcOut = data
                self.SetNavigationButtons()
                log.LogInfo('GoToStep - running funcIn', funcIn)
                funcIn(requestedStep, scrolllist)
                self.step = requestedStep
            self.HideLoad()
            self.SetHint('')
            self.sr.scroll.Load(fixedEntryHeight=24, contentList=scrolllist)
            if scrolllist:
                uicore.registry.SetFocus(self.sr.scroll)
        except StandardError:
            log.LogException()
            sys.exc_clear()

    def SetNavigationButtons(self, back = BTN_HIDDEN, ok = BTN_HIDDEN, cancel = BTN_HIDDEN, next = BTN_HIDDEN):
        if self.navigationBtns is not None:
            self.navigationBtns.Close()
            self.navigationBtns = None
        else:
            Container(name='push', parent=self.content, align=uiconst.TOTOP, height=6)
        self.navigationBtns = ButtonGroup(parent=self.content, idx=0, align=uiconst.TOBOTTOM)
        self._ok_button = Button(parent=self.navigationBtns, label=localization.GetByLabel('UI/Generic/OK'), func=self.OnOK, args=(), btn_default=1)
        self._back_button = Button(parent=self.navigationBtns, label=localization.GetByLabel('UI/Commands/Back'), func=self.OnBack, args=())
        self._cancel_button = Button(parent=self.navigationBtns, label=localization.GetByLabel('UI/Commands/Cancel'), func=self.OnCancel, args=())
        self._next_button = Button(parent=self.navigationBtns, label=localization.GetByLabel('UI/Commands/Next'), func=self.OnNext, args=(), btn_default=1)
        self.EnableNavigationButton(self._back_button, back)
        self.EnableNavigationButton(self._ok_button, ok)
        self.EnableNavigationButton(self._cancel_button, cancel)
        self.EnableNavigationButton(self._next_button, next)

    def EnableNavigationButton(self, button, btnState):
        if btnState:
            button.state = uiconst.UI_NORMAL
            if btnState == BTN_DISABLED:
                button.Disable()
            else:
                button.Enable()
        else:
            button.state = uiconst.UI_HIDDEN

    def SetSteps(self, steps, firstStep = None):
        log.LogInfo('SetSteps firstStep', firstStep)
        if firstStep is not None and firstStep not in steps:
            raise RuntimeError('SetSteps default step argument is invalid')
        self.steps = steps
        if firstStep is not None:
            self.GoToStep(firstStep)

    def SetHeading(self, heading):
        if self.heading is None:
            self.heading = eveLabel.EveCaptionMedium(text=heading, parent=self.topParent, align=uiconst.CENTERLEFT, left=70, idx=0)
        else:
            self.heading.text = heading

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)


class VoteWizardDialog(WizardDialogBase):
    __guid__ = 'form.VoteWizardDialog'
    default_windowID = 'VoteWizardDialog'
    default_iconNum = 'res:/ui/Texture/WindowIcons/votes.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.scope = uiconst.SCOPE_INGAME
        self.heading = None
        self.step = 0
        self.navigationBtns = None
        self.voteTypes = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeCreateShares'), voting.voteShares]]
        self.voteTypes.append([localization.GetByLabel('UI/Corporations/Common/ExpelCorpMember'), voting.voteKickMember])
        self.voteTypes.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeGeneral'), voting.voteGeneral])
        if IsDocked() or IsControllingStructure():
            self.voteTypes.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeLockBlueprint'), voting.voteItemLockdown])
            self.voteTypes.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeUnlockBlueprint'), voting.voteItemUnlock])
        self.voteTypesDict = {}
        for description, value in self.voteTypes:
            self.voteTypesDict[value] = description

        self.InitVote(attributes)
        steps = {1: (localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/SelectVoteType'), self.OnSelectVoteType, None),
         3: (localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeCreateShares'), self.OnSelectShareVote, self.OnLeaveShareVote),
         4: (localization.GetByLabel('UI/Corporations/Common/ExpelCorpMember'), self.OnSelectExpelVote, self.OnLeaveExpelVote),
         5: (localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeLockBlueprint'), self.OnSelectLockdownVote, self.OnLeaveLockdownVote),
         6: (localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeUnlockBlueprint'), self.OnSelectUnlockVote, self.OnLeaveUnlockVote),
         7: (localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeGeneral'), self.OnSelectGeneralVote, self.OnLeaveGeneralVote),
         8: (localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteOptions'), self.OnSelectVoteOptions, self.OnLeaveVoteOptions),
         9: (localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteDetails'), self.OnSelectVoteDetails, self.OnLeaveVoteDetails),
         10: (localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteSummary'), self.OnSelectVoteSummary, None)}
        self.content.Flush()
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=58, clipChildren=True)
        SpriteThemeColored(name='mainicon', parent=self.topParent, state=uiconst.UI_DISABLED, pos=(0, -2, 64, 64), texturePath=self.iconNum, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        self.sr.scroll = eveScroll.Scroll(parent=self.content, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.SetSteps(steps, 1)
        self.SetHeading(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ProposeVote'))
        self.SetCaption(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ProposeVote'))
        self.SetMinSize([400, 300])

    def InitVote(self, attributes = None):
        get = attributes.get if attributes is not None else (lambda x: None)
        self.ownerName = get('ownerName') or localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/HintSelectCorporationOrAlliance')
        self.ownerID = get('ownerID') or 0
        self.voteTitle = get('voteTitle')
        self.voteDescription = get('voteDescription')
        self.voteDays = get('voteDays') or 1
        self.voteShares = get('voteShares') or 1
        self.memberID = get('memberID') or 0
        self.memberName = get('memberName') or localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/HintSelectMember')
        self.voteOptions = get('voteOptions') or []
        self.voteOptionsCount = get('voteOptionsCount') or 2
        self.itemID = get('itemID') or 0
        self.typeID = get('typeID') or 0
        self.flagInput = get('flagInput')
        self.voteType = get('voteType') or self.voteTypes[0][1]
        self.locationID = get('locationID') or session.stationid or session.structureid

    def OnSelectVoteType(self, step, scrolllist):
        self.SetNavigationButtons(cancel=BTN_ENABLED, next=BTN_ENABLED)
        scrolllist.append(GetFromClass(ComboEntry, {'options': self.voteTypes,
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/SelectVoteType'),
         'cfgName': 'voteType',
         'setValue': self.voteType,
         'OnChange': self.OnComboChange,
         'name': 'voteType'}))

    def LogCurrentVoteType(self):
        log.LogInfo(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/CurrentVoteType'), self.voteType, 'name:', self.voteTypesDict[self.voteType])

    def GetNextStep(self):
        log.LogInfo('GetNextStep>>')
        self.LogCurrentVoteType()
        log.LogInfo('current step:', self.step, 'detail:', self.steps[self.step])
        nextStep = None
        if self.step == 1:
            if self.voteType == voting.voteShares:
                nextStep = 3
            elif self.voteType == voting.voteKickMember:
                nextStep = 4
            elif self.voteType == voting.voteItemLockdown:
                nextStep = 5
            elif self.voteType == voting.voteItemUnlock:
                nextStep = 6
            elif self.voteType == voting.voteGeneral:
                nextStep = 7
        if nextStep is None and self.step in (2, 3, 4, 5, 6, 8):
            nextStep = 9
        if nextStep is None:
            nextStep = self.step + 1
        log.LogInfo('next step:', nextStep, 'detail:', self.steps[nextStep])
        log.LogInfo('GetNextStep<<')
        return nextStep

    def GetPreviousStep(self):
        log.LogInfo('GetPreviousStep>>')
        self.LogCurrentVoteType()
        log.LogInfo('current step:', self.step, 'detail:', self.steps[self.step])
        prevStep = None
        if self.step in (2, 3, 4, 5, 6, 7):
            prevStep = 1
        if prevStep is None and self.step == 9:
            if self.voteType == voting.voteShares:
                prevStep = 3
            elif self.voteType == voting.voteKickMember:
                prevStep = 4
            elif self.voteType == voting.voteItemLockdown:
                prevStep = 5
            elif self.voteType == voting.voteItemUnlock:
                prevStep = 6
            elif self.voteType == voting.voteGeneral:
                prevStep = 8
        if prevStep is None:
            prevStep = self.step - 1
        log.LogInfo('prev step:', prevStep, 'detail:', self.steps.get(prevStep, ' - '))
        log.LogInfo('GetPreviousStep>>')
        return prevStep

    def OnSelectUnlockVote(self, step, scrolllist):
        self.SetNavigationButtons(back=BTN_ENABLED, cancel=BTN_ENABLED, next=BTN_HIDDEN if self.itemID == 0 else BTN_ENABLED)
        lockedItems = []
        if session.stationid or session.structureid:
            lockedItems = sm.GetService('lockedItems').GetLockedItemsByLocation(self.locationID)
        if len(lockedItems) == 0:
            scrolllist.append(GetFromClass(Header, {'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/HintNoLockedItemsInLocation')}))
            log.LogInfo('No Corp Hangar available')
            return
        accessibleHangars = self.GetAccessibleHangars()
        accessibleHangars.append((localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/OptionAllLockedItemsAtStation'), const.flagHangarAll))
        default = self.flagInput
        if self.flagInput is None or self.flagInput not in {ah[1] for ah in accessibleHangars}:
            default = accessibleHangars[0][1]
        if self.flagInput is None and default is not None:
            self.flagInput = default
        scrolllist.append(GetFromClass(ComboEntry, {'options': accessibleHangars,
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/SelectItemToUnlock'),
         'cfgName': 'install_item_from',
         'setValue': default,
         'OnChange': self.OnComboChange,
         'name': 'install_item_from'}))
        scrolllist.append(GetFromClass(DividerEntry))
        self.PopulateLockedItems(scrolllist)

    def GenerateBlueprintExtraInfo(self, blueprint):
        infoList = []
        if not blueprint.original:
            if blueprint.runsRemaining != -1:
                infoList.append(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/CopyRuns', runsRemaining=blueprint.runsRemaining))
            else:
                infoList.append(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/CopyRunsInfinite'))
        if blueprint.timeEfficiency:
            infoList.append(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ProductivityLevel', productivityLevel=blueprint.timeEfficiency))
        if blueprint.materialEfficiency:
            infoList.append(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/MaterialLevel', materialLevel=blueprint.materialEfficiency))
        return localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ExtraInfoWrapper', extraInfo=localization.formatters.FormatGenericList(infoList))

    def PopulateLockedItems(self, scrolllist):
        log.LogInfo('>PopulateLockedItems')
        hangarItems = self.GetHangarItemsToUse(self.flagInput)
        if hangarItems is None:
            return scrolllist
        sanctionedActionsInEffect = sm.GetService('corpvotes').GetSanctionedActions(voting.SANCTIONED_ACTION_STATUS_IN_EFFECT)
        sanctionedActionsByLockedItemID = {sa.parameter:sa for sa in sanctionedActionsInEffect if sa.voteType == voting.voteItemLockdown and sa.parameter and sa.inEffect}
        lastDay = blue.os.GetWallclockTime() - const.DAY
        voteCaseIDByItemToUnlockID = {}
        corpvotes = sm.GetService('corpvotes')
        for voteCase in corpvotes.GetVoteCasesByCorporation(session.corpid, voting.VOTECASE_STATUS_OPEN):
            if voteCase.voteType == voting.voteItemUnlock and voteCase.endDateTime > lastDay:
                for option in corpvotes.GetVoteCaseOptions(voteCase.voteCaseID, voteCase.corporationID):
                    if option.parameter:
                        voteCaseIDByItemToUnlockID[option.parameter] = voteCase.voteCaseID

        blueprints = self.GetBlueprints(locked=True, flag=self.flagInput)
        listentries = []
        for item in hangarItems:
            locked = sm.GetService('lockedItems').IsItemIDLocked(item.itemID)
            extraInfo = None
            if not locked:
                continue
            if item.itemID not in sanctionedActionsByLockedItemID:
                continue
            if item.itemID in voteCaseIDByItemToUnlockID:
                continue
            if evetypes.GetCategoryID(item.typeID) == const.categoryBlueprint:
                blueprint = blueprints.get(item.itemID)
                if blueprint is None:
                    log.LogInfo('Someone nabbed', item.itemID, 'while I was looking for it.')
                    continue
                extraInfo = self.GenerateBlueprintExtraInfo(blueprint)
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/LockedBlueprintLabel', item=item.typeID, extraInfo=extraInfo)
            listentries.append((label, GetFromClass(Item, {'info': item,
              'itemID': item.itemID,
              'typeID': item.typeID,
              'label': label,
              'getIcon': 1,
              'OnClick': self.ClickHangarItem})))

        listentries = SortListOfTuples(listentries)
        scrolllist += listentries

    def OnLeaveUnlockVote(self, nextStep):
        log.LogInfo('OnLeaveUnlockVote')
        if self.itemID == 0:
            if nextStep == 1:
                return 1
            return 0
        return 1

    def OnSelectLockdownVote(self, step, scrolllist):
        try:
            log.LogInfo('>OnSelectLockdownVote self.step:', self.step, ' step:', step)
            self.SetNavigationButtons(back=BTN_DISABLED, cancel=BTN_ENABLED, next=BTN_HIDDEN if self.itemID == 0 else BTN_ENABLED)
            hangars = self.GetAccessibleHangars()
            if not (sm.GetService('officeManager').GetCorpOfficeAtLocation() and hangars):
                label = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/NoCorpHangarAvailable')
                scrolllist.append(GetFromClass(Header, {'label': label}))
                log.LogInfo('No Corp Hangar available')
                return
            default = None
            if self.flagInput is not None:
                for description, flag in hangars:
                    if self.flagInput == flag:
                        default = flag
                        break

            scrolllist.append(GetFromClass(Header, {'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/OnlyUsedBPCanBeLocked')}))
            scrolllist.append(GetFromClass(ComboEntry, {'options': hangars,
             'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/SelectItemsToLockDown'),
             'cfgName': 'install_item_from',
             'setValue': default,
             'OnChange': self.OnComboChange,
             'name': 'install_item_from'}))
            scrolllist.append(GetFromClass(DividerEntry))
            if default is None:
                self.flagInput = hangars[0][1]
            self.PopulateHangarView(scrolllist)
        finally:
            self.SetNavigationButtons(back=BTN_ENABLED, cancel=BTN_ENABLED, next=BTN_HIDDEN if self.itemID == 0 else BTN_ENABLED)
            log.LogInfo('<OnSelectLockdownVote')

    @staticmethod
    def GetAccessibleHangars(canView = 1, canTake = 0):
        options = []
        divisions = sm.GetService('corp').GetDivisionNames()
        for flagID in const.flagCorpSAGs:
            if canView and not session.corprole & const.corpHangarQueryRolesByFlag[flagID]:
                continue
            if canTake and not session.corprole & const.corpHangarTakeRolesByFlag[flagID]:
                continue
            divisionID = const.corpDivisionsByFlag[flagID]
            hangarDescription = divisions[divisionID + 1]
            options.append((hangarDescription, flagID))

        return options

    def GetHangarItemsToUse(self, flagID = None):
        corpmgr = sm.RemoteSvc('corpmgr')
        listing = corpmgr.GetAssetInventoryForLocation(session.corpid, self.locationID, 'offices')
        listing.extend(corpmgr.GetAssetInventoryForLocation(session.corpid, self.locationID, 'impounded'))
        if flagID in (None, const.flagHangarAll):
            return listing
        return [ i for i in listing if i.flagID == flagID ]

    def GetBlueprints(self, locked = False, flag = None):
        data = {}
        for blueprint in sm.GetService('blueprintSvc').GetCorporationBlueprints()[0]:
            if self.locationID not in (blueprint.locationID, blueprint.facilityID):
                continue
            if flag and blueprint.locationFlagID != flag:
                continue
            if blueprint.locationTypeID != const.typeOffice and not blueprint.isImpounded:
                continue
            if not blueprint.singleton:
                continue
            if not blueprint.original:
                continue
            if sm.GetService('lockedItems').IsItemIDLocked(blueprint.itemID) != locked:
                continue
            if blueprint.jobID > 0:
                continue
            data[blueprint.blueprintID] = blueprint

        return data

    def PopulateHangarView(self, scrolllist):
        try:
            log.LogInfo('>PopulateHangarView')
            listentries = []
            for blueprint in self.GetBlueprints(flag=self.flagInput).itervalues():
                label = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/BlueprintWithSize', item=blueprint.typeID, stacksize=blueprint.quantity, extraInfo=self.GenerateBlueprintExtraInfo(blueprint))
                listentries.append((label, GetFromClass(Item, {'info': blueprint,
                  'itemID': blueprint.itemID,
                  'typeID': blueprint.typeID,
                  'label': label,
                  'getIcon': 1,
                  'OnClick': self.ClickHangarItem})))

            listentries = SortListOfTuples(listentries)
            scrolllist += listentries
        finally:
            log.LogInfo('<PopulateHangarView')

    def ClickHangarItem(self, entry, *args):
        if self.voteType in (voting.voteItemLockdown, voting.voteItemUnlock):
            isLocked = sm.GetService('lockedItems').IsItemLocked(entry.sr.node.info)
            selectable = self.voteType == voting.voteItemLockdown and not isLocked
            selectable = selectable or self.voteType == voting.voteItemUnlock and isLocked
            if selectable:
                self.SetSelectedItem(entry.sr.node.itemID, entry.sr.node.typeID)

    def SetSelectedItem(self, itemID, typeID):
        try:
            log.LogInfo('>SetSelectedItem')
            self.itemID = itemID
            self.typeID = typeID
            self.SetNavigationButtons(back=BTN_ENABLED, cancel=BTN_ENABLED, next=BTN_HIDDEN if self.itemID == 0 else BTN_ENABLED)
        finally:
            log.LogInfo('<SetSelectedItem')

    def OnLeaveLockdownVote(self, nextStep):
        log.LogInfo('OnLeaveLockdownVote')
        if self.itemID == 0:
            if nextStep == 1:
                return 1
            return 0
        return 1

    def OnSelectShareVote(self, step, scrolllist):
        self.SetNavigationButtons(back=BTN_ENABLED, cancel=BTN_ENABLED, next=BTN_ENABLED)
        scrolllist.append(GetFromClass(EditEntry, {'OnReturn': None,
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/NumberOfShares'),
         'setValue': self.voteShares,
         'name': 'voteSharesCtrl',
         'intmode': (1, 10000000)}))

    def OnLeaveShareVote(self, nextStep):
        control = self.GetChild('voteSharesCtrl')
        if hasattr(control, 'GetValue'):
            self.voteShares = control.GetValue()
        else:
            self.voteShares = control.sr.edit.GetValue()
        return 1

    def OnSelectExpelVote(self, step, scrolllist):
        self.SetNavigationButtons(back=BTN_ENABLED, cancel=BTN_ENABLED, next=BTN_ENABLED)
        scrolllist.append(GetFromClass(LabelTextTop, {'label': localization.GetByLabel('UI/Corporations/Common/ExpelCorpMember'),
         'text': self.memberName}))
        scrolllist.append(GetFromClass(ButtonEntry, {'label': '',
         'caption': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Pick'),
         'OnClick': self.PickMember,
         'args': (None,)}))

    def PickMember(self, *args):
        memberslist = []
        for memberID in sm.GetService('corp').GetMemberIDsWithMoreThanAvgShares():
            who = cfg.eveowners.Get(memberID).ownerName
            memberslist.append([who, memberID, const.typeCharacter])

        res = uix.ListWnd(memberslist, 'character', localization.GetByLabel('UI/Corporations/Common/SelectCorpMember'), localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/SelectMemberToExpel'), 1)
        if res:
            if session.charid == res[1]:
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/CannotExpelYourself')})
                return
            self.memberID = res[1]
            self.memberName = res[0]
            self.GoToStep(self.step, reload=1)

    def OnLeaveExpelVote(self, nextStep):
        if nextStep < self.step:
            return 1
        if self.memberID == 0:
            return 0
        return 1

    def OnSelectGeneralVote(self, step, scrolllist):
        self.SetNavigationButtons(back=BTN_ENABLED, cancel=BTN_ENABLED, next=BTN_ENABLED)
        scrolllist.append(GetFromClass(EditEntry, {'OnReturn': None,
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/NumberOfOptions'),
         'setValue': self.voteOptionsCount,
         'name': 'voteOptionsCtrl',
         'intmode': (2, voting.MAX_VOTE_OPTIONS)}))

    def OnLeaveGeneralVote(self, nextStep):
        control = self.GetChild('voteOptionsCtrl')
        if hasattr(control, 'GetValue'):
            self.voteOptionsCount = control.GetValue()
        else:
            self.voteOptionsCount = control.sr.edit.GetValue()
        return 1

    def OnSelectVoteOptions(self, step, scrolllist):
        self.SetNavigationButtons(back=BTN_ENABLED, cancel=BTN_ENABLED, next=BTN_ENABLED)
        i = 0
        while i < self.voteOptionsCount:
            i += 1
            title = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/OptionText', option=i)
            identifier = 'voteOption%s' % i
            value = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/EnterTextForOption', option=i)
            if len(self.voteOptions) >= i:
                value = self.voteOptions[i - 1]
            scrolllist.append(GetFromClass(EditEntry, {'OnReturn': None,
             'label': title,
             'hintText': value,
             'name': identifier,
             'maxLength': 100}))

    def OnLeaveVoteOptions(self, nextStep):
        self.voteOptions = []
        i = 0
        while i < self.voteOptionsCount:
            i += 1
            identifier = 'voteOption%s' % i
            entry = self.GetEntry(identifier)
            if not entry:
                continue
            value = entry.setValue.strip()
            if len(value) == 0:
                if nextStep < self.step:
                    continue
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/OptionCannotBeMepty')})
                return 0
            self.voteOptions.append(value)

        return 1

    def GetEntry(self, identifier):
        for entry in self.sr.scroll.GetNodes():
            if entry.name == identifier:
                return entry

    def OnSelectVoteDetails(self, step, scrolllist):
        self.SetNavigationButtons(back=BTN_ENABLED, cancel=BTN_ENABLED, next=BTN_ENABLED)
        scrolllist.append(GetFromClass(EditEntry, {'OnReturn': None,
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Title'),
         'setValue': self.GetVoteTitle(),
         'name': 'voteTitleCtrl',
         'maxLength': 100}))
        scrolllist.append(GetFromClass(EditEntry, {'OnReturn': None,
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Description'),
         'setValue': self.GetVoteDescription(),
         'name': 'voteDescriptionCtrl',
         'maxLength': 1000}))
        scrolllist.append(GetFromClass(EditEntry, {'OnReturn': None,
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/NumberOfDays'),
         'setValue': self.voteDays,
         'name': 'voteDaysCtrl',
         'intmode': (1, voting.MAX_VOTE_DURATION)}))

    def OnLeaveVoteDetails(self, nextStep):
        control = self.GetChild('voteTitleCtrl')
        if hasattr(control, 'GetValue'):
            self.voteTitle = control.GetValue().strip()
        else:
            self.voteTitle = control.sr.edit.GetValue().strip()
        control = self.GetChild('voteDescriptionCtrl')
        if hasattr(control, 'GetValue'):
            self.voteDescription = control.GetValue().strip()
        else:
            self.voteDescription = control.sr.edit.GetValue().strip()
        control = self.GetChild('voteDaysCtrl')
        if hasattr(control, 'GetValue'):
            self.voteDays = control.GetValue()
        else:
            self.voteDays = control.sr.edit.GetValue()
        if nextStep < self.step:
            return 1
        if len(self.voteTitle) == 0:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/HintTitleCannotBeEmpty')})
            return 0
        if len(self.voteDescription) == 0:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/HintDescriptionCannotBeMEmpty')})
            return 0
        return 1

    def OnSelectVoteSummary(self, step, scrolllist):
        self.SetNavigationButtons(back=BTN_ENABLED, ok=BTN_ENABLED, cancel=BTN_ENABLED)
        for name, type in self.voteTypes:
            if type == self.voteType:
                scrolllist.append(self._GetLabelTextEntry(localization.GetByLabel('UI/Common/Type'), name))

        if self.voteType == voting.voteItemLockdown:
            scrolllist.append(self._GetLabelTextEntry(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Lockdown'), evetypes.GetName(self.typeID)))
        elif self.voteType == voting.voteItemUnlock:
            scrolllist.append(self._GetLabelTextEntry(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Unlock'), evetypes.GetName(self.typeID)))
        elif self.voteType == voting.voteShares:
            scrolllist.append(self._GetLabelTextEntry(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/SharesToCreate'), self.voteShares))
        elif self.voteType == voting.voteKickMember:
            scrolllist.append(self._GetLabelTextEntry(localization.GetByLabel('UI/Corporations/Common/ExpelCorpMember'), self.memberName))
        elif self.voteType == voting.voteGeneral:
            i = 0
            while i < self.voteOptionsCount:
                i += 1
                scrolllist.append(self._GetLabelTextEntry(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/OptionText', option=i), self.voteOptions[i - 1]))

        scrolllist.append(self._GetLabelTextEntry(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Title'), self.voteTitle))
        scrolllist.append(self._GetLabelTextEntry(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Description'), self.voteDescription))
        scrolllist.append(self._GetLabelTextEntry(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/NumberOfDays'), self.voteDays))

    def _GetLabelTextEntry(self, label, text):
        return GetFromClass(LabelText, {'label': label,
         'text': text,
         'textpos': 200})

    def GetVoteTitle(self):
        if self.voteTitle is None:
            if self.voteType == voting.voteShares:
                self.voteTitle = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/CreateShares', shares=self.voteShares)
            elif self.voteType == voting.voteItemLockdown:
                self.voteTitle = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/LockdownItem', item=self.typeID)
            elif self.voteType == voting.voteItemUnlock:
                self.voteTitle = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/UnlockItem', item=self.typeID)
            elif self.voteType == voting.voteKickMember:
                self.voteTitle = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ExpelFromCorporation', char=self.memberID)
            elif self.voteType == voting.voteGeneral:
                self.voteTitle = ''
            else:
                log.LogError('Unknown Vote type')
        return self.voteTitle

    def GetVoteDescription(self):
        if self.voteDescription is None:
            self.voteDescription = ''
        return self.voteDescription

    def OnOK(self, *args):
        self.EnableNavigationButton(self._ok_button, False)
        data = {'title': self.voteTitle,
         'description': self.voteDescription,
         'votetype': self.voteType,
         'time': self.voteDays,
         'shares': self.voteShares,
         'kickmember': self.memberID,
         'memberName': self.memberName,
         'options': self.voteOptions,
         'itemID': self.itemID,
         'typeID': self.typeID,
         'locationID': self.locationID}
        sm.GetService('corpvotes').CreateVote(data)
        WizardDialogBase.OnOK(self, args)

    def OnComboChange(self, combo, header, value, *args):
        if combo.name == 'voteType':
            self.InitVote()
            self.voteType = value
        if combo.name == 'install_item_from':
            log.LogInfo('>OnComboChange self.step:', self.step)
            self.flagInput = value
            uthread.new(self.GoToStep, self.step, reload=1)


class CorpVotes(Container):
    default_name = 'CorpVotesContainer'
    __guid__ = 'CorpVotes'
    __nonpersistvars__ = []

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.corpID = attributes.get('corpID', None)
        self.isCorpPanel = attributes.get('isCorpPanel', True)
        self.sr.inited = False
        self.mainBtns = None
        self.sr.headers = [localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Title'), localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Started'), localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Ends')]
        self.noClosedVotesHint = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/NoClosedVotes')
        self.noOpenVotesHint = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/NoOpenVotes')
        self.noAccessHint = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/AccessDeniedOnlyShareholders')
        self.corpvotes = sm.GetService('corpvotes')
        corpUISignals.on_vote_case_changed.connect(self.OnVoteCaseChanged)
        corpUISignals.on_vote_cast.connect(self.OnVoteCast)

    def IAmAMemberOfThisCorp(self):
        return self.corpID == session.corpid

    def Load(self, *args):
        if self.corpID is None:
            self.corpID = session.corpid
        if not self.sr.Get('inited', 0):
            self.state = uiconst.UI_HIDDEN
            self.sr.inited = 1
            buttonOptions = []
            bottomContainer = Container(name='bottomContainer', parent=self, height=25, align=uiconst.TOBOTTOM, top=4)
            self.buttonsContainer = Container(name='buttonsContainer', align=uiconst.TOALL, parent=bottomContainer, state=uiconst.UI_PICKCHILDREN)
            if self.IAmAMemberOfThisCorp() and session.corprole & const.corpRoleDirector == const.corpRoleDirector:
                buttonOptions.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ProposeVote'),
                 self.ProposeVote,
                 (),
                 81])
            corpCEO = sm.GetService('corp').GetCorporation().ceoID
            if self.IAmAMemberOfThisCorp() and session.charid != corpCEO and self.corpvotes.CanRunForCEO():
                buttonOptions.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/RunForCEO'),
                 self.ProposeCEOVote,
                 (),
                 81])
            self.mainBtns = ButtonGroup(btns=buttonOptions, parent=self.buttonsContainer, align=uiconst.CENTER)
            if not buttonOptions:
                self.buttonsContainer.state = uiconst.UI_HIDDEN
            self.sr.scroll = eveScroll.Scroll(name='votes', parent=self, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            self.sr.tabs = ToggleButtonGroup(parent=self, idx=0, align=uiconst.TOTOP, callback=self.RefreshVotes, padBottom=8)
            self.sr.tabs.AddButton('open', localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/OpenVotes'))
            self.sr.tabs.AddButton('closed', localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ClosedVotes'))
            self.sr.tabs.SelectByID('open')
        self.state = uiconst.UI_PICKCHILDREN

    def OnVoteCaseChanged(self, corporationID, voteCaseID):
        if self is None or self.destroyed or not self.sr.inited:
            return
        self.ReloadVoteCaseSubContentIfVisible(corporationID, voteCaseID)
        self.RefreshVotes()

    def OnVoteCast(self, corporationID, voteCaseID):
        if self is None or self.destroyed or not self.sr.inited:
            return
        self.ReloadVoteCaseSubContentIfVisible(corporationID, voteCaseID)
        self.RefreshVotes()

    def GetEntryVoteCase(self, corporationID, voteCaseID):
        for entry in self.sr.scroll.GetNodes():
            if entry is None or entry is None:
                continue
            if entry.panel is None or entry.panel.destroyed:
                continue
            if not entry.vote:
                continue
            if entry.vote.corporationID == corporationID and entry.vote.voteCaseID == voteCaseID:
                return entry

    def ShouldVoteCaseBeCurrentlyVisible(self, corporationID, voteCaseID):
        if corporationID != self.corpID:
            return False
        votes = []
        selectedTab = self.sr.tabs.GetSelected()
        if selectedTab == 'open':
            votes = self.corpvotes.GetVoteCasesByCorporation(self.corpID, voting.VOTECASE_STATUS_OPEN)
        elif selectedTab == 'closed':
            votes = self.corpvotes.GetVoteCasesByCorporation(self.corpID, voting.VOTECASE_STATUS_CLOSED)
        if voteCaseID in (c.voteCaseID for c in votes):
            return True
        return False

    def ReloadVoteCaseSubContentIfVisible(self, corporationID, voteCaseID):
        if not self.ShouldVoteCaseBeCurrentlyVisible(corporationID, voteCaseID):
            return
        entry = self.GetEntryVoteCase(corporationID, voteCaseID)
        if entry is None or not entry.id:
            return
        if entry.subEntries:
            rm = entry.subEntries
            entry.subEntries = []
            entry.open = 0
            self.sr.scroll.RemoveEntries(rm)
        if entry.GetSubContent and uicore.registry.GetListGroupOpenState(entry.id):
            self.sr.scroll.RemoveEntries(entry.GetSubContent(entry))
            entry.open = 1
        if entry.panel and not entry.panel.destroyed:
            entry.panel.RefreshGroupWindow(0)

    def RefreshVotes(self, *args, **kwargs):
        if self is None or self.destroyed or not self.sr.inited:
            return
        selectedTab = self.sr.tabs.GetSelected()
        if selectedTab == 'open':
            self.ShowOpenVotes()
        elif selectedTab == 'closed':
            self.ShowClosedVotes()

    def ShowOpenVotes(self, *args):
        with sm.GetService('corpui').ShowLoad('Votes_ShowOpenVotes'):
            if not self.corpvotes.CanViewVotes(self.corpID):
                self.sr.scroll.Load(fixedEntryHeight=19, contentList=[], headers=self.sr.headers, noContentHint=self.noAccessHint)
                return
            scrolllist = []
            for vote in self.corpvotes.GetVoteCasesByCorporation(self.corpID, voting.VOTECASE_STATUS_OPEN):
                title = self.GetVoteText(vote)
                description = vote.description
                starts = FmtDate(vote.startDateTime, 'ls')
                ends = FmtDate(vote.endDateTime, 'ls')
                scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetOpenVoteSubContent,
                 'label': title + '<t>' + starts + '<t>' + ends,
                 'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Title'): title.lower(),
                 'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Description'): description.lower(),
                 'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Started'): vote.startDateTime,
                 'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Ends'): vote.endDateTime,
                 'groupItems': None,
                 'id': ('corpopenvotes', vote.voteCaseID),
                 'tabs': [],
                 'state': 'locked',
                 'vote': vote,
                 'showicon': 'hide',
                 'hint': description,
                 'BlockOpenWindow': 1}))

            self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=self.sr.headers, noContentHint=self.noOpenVotesHint)

    def GetOpenVoteSubContent(self, nodedata, *args):
        with ExceptionEater('GetOpenVoteSubContent'):
            vote = nodedata.vote
            scrolllist = []
            options = self.corpvotes.GetVoteCaseOptions(vote.voteCaseID, self.corpID)
            if not options:
                return scrolllist
            charVotes = sm.GetService('corpvotes').GetVotes(self.corpID, vote.voteCaseID)
            hasVoted = len(charVotes)
            votedFor = charVotes[0].optionID if hasVoted else -1
            canVote = sm.GetService('corpvotes').CanVote(self.corpID)
            for i, option in enumerate(options, 1):
                text = self.GetVoteOptionText(option, vote)
                entry = {'sublevel': 1}
                if hasVoted or not canVote:
                    if option.optionID == votedFor:
                        entry['text'] = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteItemHasVoted', optionNumber=i, optionText=text)
                    else:
                        entry['text'] = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteItemCannotVote', optionNumber=i, optionText=text)
                    scrolllist.append(GetFromClass(Text, entry))
                else:
                    entry['caption'] = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Vote')
                    entry['OnClick'] = self.InsertVote
                    entry['args'] = (self.corpID, vote.voteCaseID, option.optionID)
                    entry['label'] = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteItemCanVote', optionNumber=i, optionText=text)
                    scrolllist.append(GetFromClass(ButtonEntry, entry))

            entry = {'line': 1,
             'sublevel': 1}
            for option in options:
                if not option.parameter:
                    continue
                if vote.voteType in [voting.voteItemLockdown, voting.voteItemUnlock]:
                    entry['itemID'] = option.parameter
                    entry['typeID'] = option.parameter1
                    entry['text'] = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/MoreInfoItemLocatedAtLocation', item=option.parameter1, loc=option.parameter2)
                    scrolllist.append(GetFromClass(Text, entry))

            return scrolllist

    def ShowClosedVotes(self):
        with sm.GetService('corpui').ShowLoad('Votes_ShowClosedVotes'):
            scrolllist = []
            for vote in self.corpvotes.GetVoteCasesByCorporation(self.corpID, voting.VOTECASE_STATUS_CLOSED):
                title = self.GetVoteText(vote)
                description = vote.description
                starts = FmtDate(vote.startDateTime, 'ls')
                ends = FmtDate(vote.endDateTime, 'ls')
                scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetClosedVoteSubContent,
                 'label': title + '<t>' + starts + '<t>' + ends,
                 'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Title'): title.lower(),
                 'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Description'): description.lower(),
                 'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Started'): vote.startDateTime,
                 'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Ends'): vote.endDateTime,
                 'groupItems': None,
                 'id': ('corpclosedvotes', vote.voteCaseID),
                 'tabs': [],
                 'state': 'locked',
                 'vote': vote,
                 'showicon': 'hide',
                 'hint': description,
                 'BlockOpenWindow': 1}))
                uicore.registry.SetListGroupOpenState(('corpclosedvotes', vote.voteCaseID), 0)

            self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=self.sr.headers, noContentHint=self.noClosedVotesHint)

    def OnCheckboxChange(self, checkbox, *args):
        eve.Message(checkbox.checked)

    def GetClosedVoteSubContent(self, nodedata, *args):
        with ExceptionEater('GetClosedVoteSubContent'):
            vote = nodedata.vote
            scrolllist = []
            infos = []
            options = self.corpvotes.GetVoteCaseOptions(vote.voteCaseID, self.corpID)
            totalVotes = sum((o.votesFor for o in options))
            for option in options:
                text = self.GetVoteOptionText(option, vote)
                percent = 0
                if totalVotes > 0:
                    percent = option.votesFor / totalVotes * 100
                voteInfo = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ClosedVoteResultColumn', percentage=percent, votesFor=option.votesFor, totalVotes=totalVotes)
                scrolllist.append(GetFromClass(Text, {'text': '<t>'.join((text, voteInfo))}))
                if not option.parameter:
                    continue
                entry = {'line': 1}
                if vote.voteType in (voting.voteItemLockdown, voting.voteItemUnlock):
                    entry['text'] = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/MoreInfoItemLocatedAtLocation', item=option.parameter1, loc=option.parameter2)
                    entry['itemID'] = option.parameter
                    entry['typeID'] = option.parameter1
                    infos.append(GetFromClass(Text, entry))

            return scrolllist + infos

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)

    def InsertVote(self, corpID, voteCaseID, voteValue, sender, *args):
        if sender is not None and hasattr(sender, 'state'):
            sender.state = uiconst.UI_DISABLED
        sm.GetService('corpvotes').InsertVote(corpID, voteCaseID, voteValue)

    def ProposeVote(self, *args):
        if not (self.IAmAMemberOfThisCorp() and session.corprole & const.corpRoleDirector == const.corpRoleDirector):
            eve.Message('CrpOnlyDirectorsCanProposeVotes')
            return
        dlg = VoteWizardDialog.Open()
        dlg.ShowModal()

    def ProposeCEOVote(self, *args):
        if not (self.IAmAMemberOfThisCorp() and sm.GetService('corpvotes').CanRunForCEO()):
            eve.Message('CantRunForCEOAtTheMoment')
            return
        format = [{'type': 'btline'}]
        format.append({'type': 'checkbox',
         'setvalue': 1,
         'key': voting.voteCEO,
         'group': 'votetype',
         'label': '_hide',
         'text': '_hide',
         'hidden': 1})
        format.append({'type': 'push',
         'frame': 1,
         'height': 6})
        format.append({'type': 'edit',
         'setvalue': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteMemberForCEO', char=session.charid),
         'key': 'title',
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Title'),
         'required': 1,
         'frame': 1,
         'maxlength': 500})
        format.append({'type': 'bbline'})
        format.append({'type': 'push'})
        format.append({'type': 'btline'})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'textedit',
         'key': 'description',
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Description'),
         'frame': 1,
         'maxLength': 100})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'bbline'})
        format.append({'type': 'push'})
        format.append({'type': 'btline'})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'edit',
         'setvalue': 1,
         'intonly': [1, 5],
         'key': 'time',
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DaysToLive'),
         'frame': 1})
        format.append({'type': 'bbline'})
        retval = uix.HybridWnd(format=format, caption=localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ProposeVote'), windowID='proposeVote', modal=1, buttons=uiconst.OKCANCEL, location=None, minW=320)
        if retval is not None:
            sm.GetService('corpvotes').CreateVote(retval)

    def GetVoteText(self, vote):
        return voting.GetVoteText(vote)

    def GetVoteOptionText(self, option, vote):
        return voting.GetVoteOptionText(option, vote)
