#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\recruitment\corpRecruitmentContainer.py
import time
from collections import defaultdict
import blue
import localization
import uthread
from carbon.common.script.util import timerstuff
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from carbonui.button.group import ButtonGroup
from carbonui.control.basicDynamicScroll import BasicDynamicScroll
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.tabGroup import TabGroup
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.util.color import Color
from carbonui.util.various_unsorted import SortListOfTuples
from chatutil import LinkURLs
from eve.client.script.ui.control import eveLabel, eveScroll
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.rangeSelector import RangeSelector
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.services.corporation import corp_util as corputil
from eve.client.script.ui.shared.neocom.corporation.recruitment.recruitmentEntry import RecruitmentEntry
from eve.client.script.ui.shared.userentry import User
from eve.client.script.ui.util import searchOld
from eve.client.script.util import contractutils
from eve.common.lib.appConst import corpNameMaxLenSR, corpNameMaxLenTQ
from eve.common.script.search.const import MatchBy
from eve.common.script.sys import idCheckers
from evecorporation import corp_ui_recruitment_const as rConst
from evecorporation.corp_ui_recruitment_const import MAX_TIME_RANGE, FILTERSTATE_WANT, UI_SETTING_MAX_ISK_TAX_RATE, UI_SETTING_MAX_LP_TAX_RATE, CHECKBOX_ACTIVE_ICON, CHECKBOX_INACTIVE_ICON
from evecorporation.recruitment import get_recruitment_groups, get_recruitment_type, get_recruitment_types_for_group_id, get_recruitment_group_name
from evecorporation.recruitmentUtil import GetTimeZoneFromMask, RemoveOldPlaystylesFromMask, IsBitSetForTypeID, AddBitToMask, RemoveBitFromMask, BuildMask, IsNumPlaystyleMaskValid, IsOnlyOnePlaystyleType, IsNumAreaOfOperationsValid, IsTimezoneValid, TwoToThePowerOf
from eveexceptions import UserError
from eveprefs import boot
from eveservices.menu import GetMenuService

def GetTodayMidnight():
    midnight = blue.os.GetWallclockTime() / const.DAY * const.DAY
    midnight -= localization.GetTimeDeltaSeconds() * const.SEC
    return midnight


class ContactContainer(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.charID = None
        self.removeFunc = attributes.Get('removeFunc', None)
        self.addCallback = attributes.Get('addCallback', None)
        self.corpMembers = attributes.Get('corpMembers', [])
        self.iconContainer = Container(parent=self, align=uiconst.CENTERLEFT, pos=(const.defaultPadding,
         0,
         24,
         24))
        self.iconContainer.Hide()
        self.removeContactButton = ButtonIcon(parent=self, align=uiconst.CENTERRIGHT, hint=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdRemove'), func=self.RemoveClick, iconColor=Color.RED, iconSize=16, texturePath='res:/UI/Texture/Icons/73_16_45.png')
        self.contactNameClipper = Container(parent=self)
        self.contactNameLabel = eveLabel.EveLabelMedium(parent=self.contactNameClipper, align=uiconst.CENTERLEFT, autoFadeSides=25)
        Fill(parent=self, color=(0, 0, 0, 0.5))
        Frame(parent=self, color=(1, 1, 1, 0.15), idx=0)
        self.Clear()

    def Clear(self):
        self.iconContainer.Flush()
        self.charID = None
        self.contactNameClipper.padLeft = const.defaultPadding
        self.contactNameClipper.padRight = const.defaultPadding
        self.contactNameLabel.text = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NoRecruiterAssigned')
        self.removeContactButton.Hide()
        self.iconContainer.Hide()

    def Set(self, charID = None):
        self.iconContainer.Flush()
        if charID:
            self.charID = charID
            OwnerIcon(parent=self.iconContainer, size=32, ownerID=charID, pos=(0,
             0,
             self.iconContainer.width,
             self.iconContainer.width))
            self.iconContainer.Show()
            self.contactNameClipper.padLeft = self.iconContainer.width + const.defaultPadding * 2
            self.contactNameClipper.padRight = self.removeContactButton.width + const.defaultPadding * 2
            self.contactNameLabel.text = cfg.eveowners.Get(charID).name
            self.removeContactButton.Show()
            self.addCallback(self, charID)

    def IsSet(self):
        return self.charID

    def RemoveClick(self, *args):
        if self.removeFunc and self.charID:
            self.removeFunc(self.charID)

    def OnDropData(self, dragObj, *args):
        from eve.client.script.ui.shared.userentry import User
        if not self.IsSet() and dragObj.__class__ == User:
            if dragObj.sr.node.itemID in self.corpMembers:
                self.Set(dragObj.sr.node.itemID)

    def GetMenu(self):
        if not self.charID:
            return
        return GetMenuService().GetMenuForOwner(self.charID)


class CorpRecruitmentContainerBase(Container):
    default_alignMode = uiconst.TOTOP

    def AddTimeZonePicker(self, parent, callback, startTimeZoneProportion, endTimeZoneProportion, header = None, minRange = 1 / 24.0, OnEndDragChange = None, maxRange = None):
        adGroups = get_recruitment_groups()
        if header is None:
            self.CreateLabel(parent, adGroups[rConst.TIMEZONE_GROUPID].groupName, adGroups[rConst.TIMEZONE_GROUPID].description, padTop=16)
        else:
            self.CreateLabel(parent, header, padTop=16)
        incrs = []
        midnightTime = GetTodayMidnight()
        for i in range(24):
            if not i % 6:
                date = midnightTime + i * const.HOUR
                text = FmtDate(date, fmt='ns')
                size = 5
            else:
                text = ''
                size = 2
            incrs.append((text, size, i))

        midnightHour = localization.GetByLabel('/Carbon/UI/Common/DateTimeQuantity/DateTimeShort2Elements', value1='24', value2='00')
        incrs.append((midnightHour, 5, 24))
        timeZoneSelector = RangeSelector(parent=parent, align=uiconst.TOTOP, OnIncrementChange=callback, fromProportion=startTimeZoneProportion, toProportion=endTimeZoneProportion, canInvert=True, OnEndDragChange=OnEndDragChange)
        timeZoneSelector.SetIncrements(incrs)
        timeZoneSelector.SetMinRange(minRange=minRange)
        if maxRange is not None:
            timeZoneSelector.SetMaxRange(maxRange=maxRange)
        return timeZoneSelector

    def GetDefaultLanguage(self):
        sessionLang = session.languageID
        if sessionLang == 'DE':
            defaultAdType = get_recruitment_type(rConst.GERMAN_TYPEID)
        elif sessionLang == 'RU':
            defaultAdType = get_recruitment_type(rConst.RUSSIAN_TYPEID)
        elif sessionLang == 'JA':
            defaultAdType = get_recruitment_type(rConst.JAPANESE_TYPEID)
        else:
            defaultAdType = get_recruitment_type(rConst.ENGLISH_TYPEID)
        return defaultAdType

    def AddUtilMenu(self, name, parent, header, menuFunction, padTop = 16):
        self.AddHeaderLabel(header, parent, padTop)
        menuParent = Container(name='menuParent', parent=parent, align=uiconst.TOTOP)
        FillThemeColored(bgParent=menuParent, opacity=0.8, colorType=uiconst.COLORTYPE_UIBASECONTRAST)
        utilMenu = UtilMenu(name=name, parent=menuParent, align=uiconst.TOTOP, GetUtilMenu=menuFunction, texturePath='res:/UI/Texture/Icons/38_16_229.png', label=header)
        menuParent.height = utilMenu.height
        return (menuParent, utilMenu)

    def AddHeaderLabel(self, headerText, parent, padTop = 16):
        headerLabel = EveLabelMedium(name='headerLabel', parent=parent, text=headerText, align=uiconst.TOTOP, bold=True, padTop=padTop)

    def OnHintTextClick(self, utilMenu, *args):
        if utilMenu.IsExpanded():
            return
        uthread.new(utilMenu.ExpandMenu)

    def CreateLabel(self, parent, text, hint = '', padTop = 0, align = None):
        label = eveLabel.EveLabelMedium(parent=parent, text=text, hint=hint, state=uiconst.UI_NORMAL, align=align or uiconst.TOTOP, bold=True, padTop=padTop, padLeft=0)
        return label

    def GetAreasOfOperation(self, *args):
        return get_recruitment_types_for_group_id(rConst.AREA_OF_OPERATIONS_GROUPID)


class CorpRecruitmentAdCreationAndEdit(Window):
    default_minSize = (500, 650)
    default_width = 650

    def ApplyAttributes(self, attributes):
        super(CorpRecruitmentAdCreationAndEdit, self).ApplyAttributes(attributes)
        self.corpSvc = sm.GetService('corp')
        recruitmentCont = CorpRecruitmentContainerCreation(parent=self.sr.main, ownerWnd=self, advertData=attributes.advertData)


class CorpRecruitmentContainerCreation(CorpRecruitmentContainerBase):

    def ApplyAttributes(self, attributes):
        super(CorpRecruitmentContainerCreation, self).ApplyAttributes(attributes)
        self.corpSvc = sm.GetService('corp')
        self.PopulateCorpAdvertsEdit(advertData=attributes.advertData)
        self.ownerWnd = attributes.ownerWnd

    def PopulateCorpAdvertsEdit(self, advertData = None):
        self.Flush()
        if advertData:
            advertID = advertData.adID
            recruiters = self.corpSvc.GetRecruiters(advertID)
            daysRemaining = max(0, int((advertData.expiryDateTime - blue.os.GetWallclockTime()) / const.DAY))
            self.adCreateMask = advertData.typeMask or 0
            self.adLanguageMask = advertData.langMask or 0
            self.otherMask = advertData.otherMask or 0
            minSP = advertData.minSP
            adTitle = advertData.title
            if advertData.hourMask1 is None:
                self.adCreateTimeZone1 = (0, 1.0)
            else:
                timezone = GetTimeZoneFromMask(advertData.hourMask1)
                self.adCreateTimeZone1 = (timezone[0] / 24.0, timezone[1] / 24.0)
        else:
            advertID = None
            recruiters = []
            daysRemaining = 0
            self.adCreateMask = settings.char.ui.Get('corp_recruitment_lastCreateMask', 0)
            self.otherMask = 0
            self.adLanguageMask = settings.char.ui.Get('corp_recruitment_lastCreateLanguageMask', 0)
            self.adCreateTimeZone1 = settings.char.ui.Get('corp_recruitment_lastCreateTimeZone1', (0.0, 1.0))
            minSP = 0
        self.adCreateMask = RemoveOldPlaystylesFromMask(self.adCreateMask)
        self.adCreateAdvertID = advertID
        sidePanel = Container(parent=self, name='sidePanel', align=uiconst.TORIGHT, width=230)
        buttons = [[localization.GetByLabel('UI/Common/Buttons/Submit'),
          self.UpdateAdvert,
          (advertID,),
          None], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.CancelCorpAdvert,
          (None,),
          None]]
        buttons = ButtonGroup(btns=buttons, parent=sidePanel)
        mainArea = Container(parent=self, name='mainArea', align=uiconst.TOALL, padding=const.defaultPadding)
        corpAdvertDetailsContainer = Container(parent=sidePanel, name='corpAdvertDetailsContainer', align=uiconst.TOALL, padding=(const.defaultPadding,
         0,
         const.defaultPadding * 3,
         0))
        self.AddHeaderLabel(get_recruitment_group_name(rConst.PLAYSTYLE_GROUPID), corpAdvertDetailsContainer, 4)
        options = []
        for combinedGroupID in rConst.PLAYSTYLE_GROUPS:
            groupName = localization.GetByLabel(rConst.COMBINED_GROUPS[combinedGroupID].combinedNamePath)
            options.append((groupName, combinedGroupID))

        selected = self.GetGroupWithMostSelected()
        menuParent = Container(parent=corpAdvertDetailsContainer, align=uiconst.TOTOP)
        self.combinedGroupCombo = Combo(parent=menuParent, align=uiconst.TOTOP, options=options, callback=self.OnCombinedGroupsComboChanged, select=selected)
        self.RemoveTypesFromOtherGroups(selected)
        menuParent.height = self.combinedGroupCombo.height
        menuParent = Container(parent=corpAdvertDetailsContainer, align=uiconst.TOTOP, padTop=4)
        FillThemeColored(bgParent=menuParent, opacity=0.8, colorType=uiconst.COLORTYPE_UIBASECONTRAST)
        self.playStyleUtilMenu = UtilMenu(name='playStyleCreate', parent=menuParent, align=uiconst.TOTOP, GetUtilMenu=self.GetAdCreatePlayStyleMenu, texturePath='res:/UI/Texture/Icons/38_16_229.png', label=get_recruitment_group_name(rConst.PLAYSTYLE_GROUPID))
        menuParent.height = self.playStyleUtilMenu.height
        self.UpdateAdCreatePlayStyleHintText()
        checked = IsBitSetForTypeID(rConst.NEWPILOTFRIENTLY_TYPEID, self.otherMask)
        self.newPlayerFriendlyCb = Checkbox(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NewPilotFriendly'), parent=corpAdvertDetailsContainer, settingsKey='adCreate_NewPlayerFriendly', checked=checked, align=uiconst.TOTOP, callback=self.OnNewPlayerFriendlyChanged, padTop=4)
        checked = IsBitSetForTypeID(rConst.NEWPILOTFOCUSED_TYPEID, self.otherMask)
        self.newPlayerFocusedCb = Checkbox(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NewPilotFocused'), parent=corpAdvertDetailsContainer, settingsKey='adCreate_NewPlayerFocused', checked=checked, align=uiconst.TOTOP)
        self.SetNewPilotFocusedEnableState()
        checked = IsBitSetForTypeID(rConst.ROLEPLAY_TYPEID, self.otherMask)
        self.roleplayerFocusedCb = Checkbox(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RoleplayingFocused2'), parent=corpAdvertDetailsContainer, settingsKey='adCreate_RoleplayFocused', checked=checked, align=uiconst.TOTOP)
        areaOfOperationMenuParent, areaOfOperationMenu = self.AddUtilMenu('areaOfOperationCreate', corpAdvertDetailsContainer, get_recruitment_group_name(rConst.AREA_OF_OPERATIONS_GROUPID), self.GetAdCreateAreaOfOperationsOptions)
        self.adCreate_areaOfOperationMenu = areaOfOperationMenu
        self.UpdateAdCreateAreaOfOperationHint()
        hasLanguage = False
        for adType in get_recruitment_types_for_group_id(corputil.RECRUITMENT_GROUP_PRIMARY_LANGUAGE):
            if self.adLanguageMask and adType.typeMask & self.adLanguageMask:
                hasLanguage = True
                break

        if not hasLanguage:
            adType = self.GetDefaultLanguage()
            self.adLanguageMask = AddBitToMask(bit=adType.typeMask, mask=self.adLanguageMask)
        languageMenuParent, languageMenu = self.AddUtilMenu('languageCreation', corpAdvertDetailsContainer, get_recruitment_group_name(corputil.RECRUITMENT_GROUP_PRIMARY_LANGUAGE), self.GetAdCreateLanguageOptions)
        self.adCreate_languageMenu = languageMenu
        self.UpdateAdCreateLanguageHint()
        headerText = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/PrimaryTimeZone')
        self.AddTimeZonePicker(parent=corpAdvertDetailsContainer, callback=self.OnAdCreateTimezoneRangeChange, startTimeZoneProportion=self.adCreateTimeZone1[0], endTimeZoneProportion=self.adCreateTimeZone1[1], header=headerText, maxRange=MAX_TIME_RANGE)
        pad = Container(parent=corpAdvertDetailsContainer, align=uiconst.TOTOP, height=const.defaultPadding)
        maxDurExtension = const.corporationMaxRecruitmentAdDuration - daysRemaining
        if maxDurExtension > 0:
            if not advertID:
                durationHeader = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RecruitmentAdDuration')
            else:
                durationHeader = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/ExtendRecruitmentAdDuration')
            self.CreateLabel(corpAdvertDetailsContainer, durationHeader, padTop=const.defaultPadding)
            incrs = []
            tickTextAdded = False
            i = 0
            for i in range(maxDurExtension + 1):
                if i % 7:
                    incrs.append(('', 2, i))
                else:
                    incrs.append((str(i), 6, i))
                    if i > 0:
                        tickTextAdded = True

            if not tickTextAdded and i > 0:
                lastTuple = incrs[-1]
                newTuple = (str(i), lastTuple[1], lastTuple[2])
                incrs[-1] = newTuple
            defaultDuration = 1
            stepSize = 1.0 / (len(incrs) - 1)
            toProportion = stepSize * defaultDuration
            durationSelector = RangeSelector(parent=corpAdvertDetailsContainer, align=uiconst.TOTOP, OnIncrementChange=self.OnDurationChange, fromProportion=0.0, toProportion=toProportion, canInvert=False)
            durationSelector.SetIncrements(incrs)
            durationSelector.SetFixedRange(fixedFromProportion=0.0)
            if advertID:
                durationSelector.SetMinRange(minRange=0.0)
            else:
                durationSelector.SetMinRange(minRange=stepSize)
            self.adCreateDurationHint = eveLabel.EveLabelSmall(parent=corpAdvertDetailsContainer, align=uiconst.TOTOP, padBottom=8, padLeft=const.defaultPadding * 2, state=uiconst.UI_NORMAL)
            self.UpdateDurationHint(defaultDuration)
        else:
            self.adCreateDuration = 0
        inputLabel = eveLabel.EveLabelMediumBold(parent=corpAdvertDetailsContainer, name='inputLabel', align=uiconst.TOTOP, text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/MinimumSPrequirement'))
        self.spInput = SingleLineEditInteger(parent=corpAdvertDetailsContainer, name='spInput', align=uiconst.TOTOP, maxValue=600000000, setvalue=minSP)
        self.corpMembers = self.corpSvc.GetMemberIDs()
        self.contactsList = []
        recruitmentContainer = Container(parent=sidePanel, name='recruitmentContainer', align=uiconst.TOALL, padding=const.defaultPadding)
        self.contactsFilter = QuickFilterEdit(parent=recruitmentContainer, name='contactsFilter', align=uiconst.TOTOP, maxLength=10, hintText=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/FilterRecruiterCandidates'), padBottom=const.defaultPadding, isCharacterField=True)
        self.contactsFilter.ReloadFunction = lambda : self.FilterOnInsert()
        self.corpMemberPickerScroll = eveScroll.Scroll(parent=recruitmentContainer, align=uiconst.TOALL)
        buttonContainer = Container(parent=recruitmentContainer, name='buttonContainer', align=uiconst.TOBOTTOM, idx=0)
        advertAddContactButton = Button(parent=buttonContainer, name='advertAddContactButton', align=uiconst.CENTER, func=self.AddContactClick, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AddRecruiterToAd'))
        buttonContainer.height = advertAddContactButton.height + 8
        self.contactContainers = {}
        for i in range(0, 6):
            self.contactContainers[i] = ContactContainer(parent=recruitmentContainer, align=uiconst.TOBOTTOM, height=32, padTop=2, removeFunc=self.RemoveContact, addCallback=self.AddContactCallback, state=uiconst.UI_NORMAL, corpMembers=self.corpMembers, idx=0)

        cfg.eveowners.Prime(self.corpMembers)
        scrollList = []
        for member in self.corpMembers:
            scrollList.append((cfg.eveowners.Get(member).name, GetFromClass(User, {'charID': member,
              'OnDblClick': self.OnContactDoubleClick})))

        scrollList = SortListOfTuples(scrollList)
        self.corpMemberPickerScroll.Load(contentList=scrollList)
        for contact in recruiters:
            self.AddContact(contact)

        self.CreateLabel(mainArea, localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdEditTitle'), padTop=6)
        self.corpTitleEdit = SingleLineEditText(parent=mainArea, name='corpTitleEdit', align=uiconst.TOTOP, maxLength=const.corporationRecMaxTitleLength)
        if advertData:
            self.corpTitleEdit.SetValue(adTitle)
        self.CreateLabel(mainArea, text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdEditMessage'), padTop=6)
        self.corpMessageEdit = EditPlainText(parent=mainArea, align=uiconst.TOALL, name='corpMessageEdit', maxLength=const.corporationRecMaxMessageLength, showattributepanel=True)
        self.corpMessageEdit.Paste = self.MessagePaste
        if advertData:
            self.corpMessageEdit.SetValue(advertData.description)
        tabs = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdEditDetails'),
          corpAdvertDetailsContainer,
          self,
          'details'], [localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdRecruiters'),
          recruitmentContainer,
          self,
          'recruiters']]
        tabGroup = TabGroup(name='corpAdEditTabGroup', parent=sidePanel, align=uiconst.TOTOP, padTop=const.defaultPadding * 2, idx=0)
        tabGroup.Startup(tabs)

    def GetGroupWithMostSelected(self):
        groupsWithSelection = defaultdict(int)
        for adTypeID, combinedGroupID in rConst.COMBINED_GROUP_BY_TYPEID.iteritems():
            adType = get_recruitment_type(adTypeID)
            if adType.typeMask & self.adCreateMask:
                groupsWithSelection[combinedGroupID] += 1

        if groupsWithSelection:
            return max(groupsWithSelection, key=lambda x: groupsWithSelection[x])

    def OnCombinedGroupsComboChanged(self, cb, key, val):
        self.RemoveTypesFromOtherGroups(val)
        self.UpdateAdCreatePlayStyleHintText()

    def RemoveTypesFromOtherGroups(self, groupSelected):
        for adTypeID, combinedGroupID in rConst.COMBINED_GROUP_BY_TYPEID.iteritems():
            if combinedGroupID != groupSelected:
                adType = get_recruitment_type(adTypeID)
                self.adCreateMask = RemoveBitFromMask(bit=adType.typeMask, mask=self.adCreateMask)

    def OnNewPlayerFriendlyChanged(self, cb):
        self.SetNewPilotFocusedEnableState()

    def SetNewPilotFocusedEnableState(self):
        if self.newPlayerFriendlyCb.checked:
            self.newPlayerFocusedCb.Enable()
        else:
            self.newPlayerFocusedCb.Disable()
            self.newPlayerFocusedCb.SetValue(False)

    def MessagePaste(self, text):
        text = LinkURLs(text)
        EditPlainText.Paste(self.corpMessageEdit, text)

    def CheckCanSelectPlaystyleOption(self, clickedType):
        if not self.adCreateMask:
            return True
        clickedTypeID = clickedType.typeID
        clickedGroup = rConst.COMBINED_GROUP_BY_TYPEID.get(clickedTypeID, None)
        if clickedGroup is None:
            return
        typesInUse = set()
        for adTypeID, combinedGroupID in rConst.COMBINED_GROUP_BY_TYPEID.iteritems():
            adType = get_recruitment_type(adTypeID)
            if clickedType == adType:
                continue
            inUse = adType.typeMask & self.adCreateMask
            if inUse:
                if combinedGroupID != clickedGroup:
                    raise UserError('CannotSelectDifferentRecruitmentGroup')
                else:
                    typesInUse.add(adTypeID)

        if len(typesInUse) >= rConst.MAX_SELECTED_TYPES:
            raise UserError('CannotSelectMorePlaystyles', {'numMaxOptions': rConst.MAX_SELECTED_TYPES})

    def CheckCanSelectAreaOption(self, clickedType):
        if not self.adCreateMask:
            return True
        typesInUse = set()
        for adType in self.GetAreasOfOperation():
            if clickedType == adType:
                continue
            inUse = adType.typeMask & self.adCreateMask
            if inUse:
                typesInUse.add(adType.typeID)

        if len(typesInUse) >= rConst.MAX_SELECTED_AREAS:
            raise UserError('CannotSelectMoreAreas', {'numMaxOptions': rConst.MAX_SELECTED_TYPES})

    def OnAdCreatePlayStyleChange(self, adType, checked, *args):
        mask = self.adCreateMask
        if checked:
            self.CheckCanSelectPlaystyleOption(adType)
            mask = AddBitToMask(bit=adType.typeMask, mask=mask)
        else:
            mask = RemoveBitFromMask(bit=adType.typeMask, mask=mask)
        self.adCreateMask = mask
        self.UpdateAdCreatePlayStyleHintText()

    def UpdateAdCreatePlayStyleHintText(self):
        mask = self.adCreateMask
        counter = 0
        for combinedGroupID in rConst.PLAYSTYLE_GROUPS:
            adTypeIDs = rConst.COMBINED_GROUPS[combinedGroupID].playstyleTypeIDs
            for adTypeID in adTypeIDs:
                adType = get_recruitment_type(adTypeID)
                if adType.typeMask & mask:
                    counter += 1

        if counter > 0:
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NumFiltersSelected', num=counter)
        else:
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NoFiltersSelected')
        self.playStyleUtilMenu.SetLabel(hint)

    def GetAdCreateAreaOfOperationsOptions(self, menuParent):
        mask = self.adCreateMask
        for adType in get_recruitment_types_for_group_id(rConst.AREA_OF_OPERATIONS_GROUPID):
            checked = adType.typeMask & mask
            typeName = adType.typeName
            menuParent.AddCheckBox(text=typeName, checked=checked, callback=(self.OnAdCreateAreaOfOperationChange, adType, not checked))

    def OnAdCreateAreaOfOperationChange(self, adType, checked):
        mask = self.adCreateMask
        if checked:
            self.CheckCanSelectAreaOption(adType)
            mask = AddBitToMask(bit=adType.typeMask, mask=mask)
        else:
            mask = RemoveBitFromMask(bit=adType.typeMask, mask=mask)
        self.adCreateMask = mask
        self.UpdateAdCreateAreaOfOperationHint()

    def UpdateAdCreateAreaOfOperationHint(self):
        mask = self.adCreateMask
        counter = 0
        for adType in get_recruitment_types_for_group_id(rConst.AREA_OF_OPERATIONS_GROUPID):
            if adType.typeMask & mask:
                counter += 1

        if counter > 0:
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NumFiltersSelected', num=counter)
        else:
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NoFiltersSelected')
        self.adCreate_areaOfOperationMenu.SetLabel(hint)

    def GetAdCreateLanguageOptions(self, menuParent):
        mask = self.adLanguageMask or 0
        for adType in get_recruitment_types_for_group_id(corputil.RECRUITMENT_GROUP_PRIMARY_LANGUAGE):
            checked = adType.typeMask & mask
            menuParent.AddCheckBox(text=adType.typeName, checked=checked, callback=(self.OnAdCreateLanguageChange, adType, not checked))

    def OnAdCreateLanguageChange(self, adType, checked):
        mask = self.adLanguageMask or 0
        if checked:
            mask = AddBitToMask(bit=adType.typeMask, mask=mask)
        else:
            mask = RemoveBitFromMask(bit=adType.typeMask, mask=mask)
        self.adLanguageMask = mask
        self.UpdateAdCreateLanguageHint()

    def UpdateAdCreateLanguageHint(self):
        mask = self.adLanguageMask or 0
        counter = 0
        for adType in get_recruitment_types_for_group_id(corputil.RECRUITMENT_GROUP_PRIMARY_LANGUAGE):
            if adType.typeMask & mask:
                counter += 1

        if counter > 0:
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NumFiltersSelected', num=counter)
        else:
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NoFiltersSelected')
        self.adCreate_languageMenu.SetLabel(hint)

    def OnDurationChange(self, rangeSelector, fromData, toData, *args):
        duration = max(0, toData[-1])
        self.UpdateDurationHint(duration)

    def UpdateDurationHint(self, duration):
        self.adCreateDuration = duration
        durationHint = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RecruitmentAdDurationOptionWithPrice', adDuration=duration * const.DAY, adPrice=contractutils.FmtISKWithDescription(self.AdvertPrice(duration), justDesc=True))
        self.adCreateDurationHint.text = durationHint

    def AdvertPrice(self, days):
        amount = days * const.corporationAdvertisementDailyRate
        if not self.adCreateAdvertID:
            amount += const.corporationAdvertisementFlatFee
        return amount

    def FilterOnInsert(self, *args):
        scrollList = []
        for member in self.corpMembers:
            if member not in self.contactsList and self.contactsFilter.GetValue().lower() in cfg.eveowners.Get(member).name.lower():
                entry = GetFromClass(User, {'charID': member,
                 'OnDblClick': self.OnContactDoubleClick})
                scrollList.append(entry)

        self.corpMemberPickerScroll.Load(contentList=scrollList)

    def AddContactClick(self, *args):
        selected = self.corpMemberPickerScroll.GetSelected()
        if len(selected) and len(self.contactsList) < 6:
            for item in selected:
                self.AddContact(item.itemID)

    def OnContactDoubleClick(self, entry, *args):
        self.AddContact(entry.sr.node.itemID)

    def AddContact(self, charID):
        for container in self.contactContainers.values():
            if not container.IsSet():
                container.Set(charID)
                break

    def AddContactCallback(self, callbackObj, charID):
        if charID in self.contactsList:
            callbackObj.Clear()
        else:
            self.contactsList.append(charID)
            self.FilterOnInsert()

    def RemoveContact(self, charID):
        for container in self.contactContainers.values():
            if container.IsSet() == charID:
                container.Clear()
                self.contactsList.remove(charID)
                self.FilterOnInsert()

    def OnHintTextClick(self, utilMenu, *args):
        if utilMenu.IsExpanded():
            return
        uthread.new(utilMenu.ExpandMenu)

    def UpdateAdvert(self, advertID = None):
        title = self.corpTitleEdit.GetValue().strip()
        if not title:
            raise UserError('CustomInfo', {'info': localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/EnterTitleForAd')})
        description = self.corpMessageEdit.GetValue()
        recruiters = self.contactsList
        days = self.adCreateDuration
        minSP = self.spInput.GetValue()
        typeMask = self.adCreateMask
        languageMask = self.adLanguageMask
        f, t = self.adCreateTimeZone1
        timeZoneMask1 = BuildMask(f * 24, t * 24)

        def TwoToThePowerOf(power):
            return 1 << power

        otherMask = 0
        if self.newPlayerFriendlyCb.GetValue():
            otherMask = AddBitToMask(TwoToThePowerOf(rConst.NEWPILOTFRIENTLY_TYPEID), otherMask)
        if self.newPlayerFocusedCb.GetValue():
            otherMask = AddBitToMask(TwoToThePowerOf(rConst.NEWPILOTFOCUSED_TYPEID), otherMask)
        if self.roleplayerFocusedCb.GetValue():
            otherMask = AddBitToMask(TwoToThePowerOf(rConst.ROLEPLAY_TYPEID), otherMask)
        if not IsNumPlaystyleMaskValid(typeMask):
            raise UserError('CorpRecruitmentNumPlaystyleMaskInvalid', {'numOptions': rConst.MAX_SELECTED_TYPES})
        if not IsOnlyOnePlaystyleType(typeMask):
            raise UserError('CorpRecruitmentTooManyPlaystyleTypesSelected')
        if not IsNumAreaOfOperationsValid(typeMask):
            raise UserError('CorpRecruitmentTooManyAreasSelected', {'numOptions': rConst.MAX_SELECTED_AREAS})
        if not IsTimezoneValid(timeZoneMask1):
            raise UserError('CorpRecruitmentTooManyHoursSelected', {'numHours': rConst.MAX_HOURS})
        if advertID:
            self.corpSvc.UpdateRecruitmentAd(advertID, typeMask, languageMask, description, recruiters, title, days, timeZoneMask1, minSP=minSP, otherMask=otherMask)
        else:
            settings.char.ui.Set('corp_recruitment_lastCreateMask', typeMask)
            settings.char.ui.Set('corp_recruitment_lastCreateLanguageMask', languageMask)
            self.corpSvc.CreateRecruitmentAd(days, typeMask, languageMask, description, recruiters, title, timeZoneMask1, minSP=minSP, otherMask=otherMask)
        self.CloseAdWindow()

    def OnAdCreateTimezoneRangeChange(self, rangeSelector, fromData, toData, fromProportion, toProportion):
        self.adCreateTimeZone1 = (fromProportion, toProportion)

    def CancelCorpAdvert(self, *args):
        self.CloseAdWindow()

    def CloseAdWindow(self, *args):
        if self.ownerWnd and not self.ownerWnd.destroyed:
            self.ownerWnd.Close()

    def GetAdCreatePlayStyleMenu(self, menuParent):
        mask = self.adCreateMask
        selectedGroupID = self.combinedGroupCombo.GetValue()
        for combinedGroupID in rConst.PLAYSTYLE_GROUPS:
            if combinedGroupID != selectedGroupID:
                continue
            adTypeIDs = rConst.COMBINED_GROUPS[combinedGroupID].playstyleTypeIDs
            for adTypeID in adTypeIDs:
                adType = get_recruitment_type(adTypeID)
                checked = bool(adType.typeMask & mask)
                typeName = (adType.typeName,)
                menuParent.AddCheckBox(text=typeName, checked=checked, callback=(self.OnAdCreatePlayStyleChange, adType, not checked))

            menuParent.AddSpace()


class CorpRecruitmentContainerSearch(CorpRecruitmentContainerBase):
    is_loaded = False

    def ApplyAttributes(self, attributes):
        self.corpSvc = sm.GetService('corp')
        timeDiffHours = localization.GetTimeDeltaSeconds() / 3600
        self.localTimeZoneDiff = time.gmtime().tm_hour + timeDiffHours - time.localtime().tm_hour
        super(CorpRecruitmentContainerSearch, self).ApplyAttributes(attributes)

    def Load(self, *args):
        if not self.is_loaded:
            self.is_loaded = True
            self.ConstructLayout()

    def ConstructLayout(self):
        sm.ScatterEvent('OnClientEvent_OpenCorpFinder')
        self.searchMask = settings.char.ui.Get('corporation_recruitment_types', 0)
        ContainerAutoSize(parent=self, name='explanationCont', size=100, align=uiconst.TOTOP)
        rightContainer = ScrollContainer(parent=self, name='corpSearchOptionsContainer', align=uiconst.TORIGHT, padLeft=8, width=240)
        searchCorpID = settings.char.ui.Get('corpRecruitmentSearchCorpID', None)
        if searchCorpID is not None:
            try:
                searchTerm = cfg.eveowners.Get(searchCorpID).name
            except KeyError:
                searchTerm = ''

        else:
            searchTerm = ''
        self.AddHeaderLabel(localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/SearchForCorporation'), rightContainer, 0)
        maxLength = corpNameMaxLenSR if boot.region == 'optic' else corpNameMaxLenTQ
        self.searchField = QuickFilterEdit(parent=rightContainer, align=uiconst.TOTOP, setvalue=searchTerm, hintText=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/TypeHere'), OnClearFilter=self.OnSearchFieldChanged, isCharCorpOrAllianceField=True, maxLength=maxLength, padBottom=16)
        self.searchField.ReloadFunction = self.OnSearchFieldChanged
        self.searchField.OnReturn = self.SearchByCorpName
        corpSearchOptionsContainer = ContainerAutoSize(parent=rightContainer, name='corpSearchOptionsContainer', align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        self.corpSearchOptionsContainer = corpSearchOptionsContainer
        filterStates = self.GetFilterStates()
        haveSubPlayStyle = False
        for combinedGroupID in rConst.PLAYSTYLE_GROUPS:
            adTypeIDs = rConst.COMBINED_GROUPS[combinedGroupID].playstyleTypeIDs
            for adTypeID in adTypeIDs:
                if adTypeID in filterStates:
                    haveSubPlayStyle = True
                    break

        if not haveSubPlayStyle:
            for adTypeID in [rConst.EXPLORATION_TYPEID, rConst.MISSIONRUNNING_TYPEID]:
                filterStates[adTypeID] = FILTERSTATE_WANT

            filterStates[rConst.NEWPILOTFRIENTLY_TYPEID] = FILTERSTATE_WANT
        self.SetFilterStates(filterStates)
        adGroups = get_recruitment_groups()
        playStyleMenuParent, playStyleMenu = self.AddUtilMenu('playStyleSearch', corpSearchOptionsContainer, adGroups[rConst.PLAYSTYLE_GROUPID].groupName, self.GetSearchPlayStyleMenu, 0)
        self.searchPlayStyleMenu = playStyleMenu
        configName = 'corpRec_search_NewPlayerFriendly'
        newPlayerFriendly = settings.char.ui.Get(configName, False)
        self.newPlayerFriendlyCb = Checkbox(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NewPilotFriendly'), parent=corpSearchOptionsContainer, settingsPath=('char', 'ui'), settingsKey=configName, checked=newPlayerFriendly, align=uiconst.TOTOP, padTop=4, callback=self.OnOtherCbChanged)
        self.newPlayerFriendlyCb.typeID = rConst.NEWPILOTFRIENTLY_TYPEID
        configName = 'corpRec_search_newPlayerFocused'
        newPlayerFocused = settings.char.ui.Get(configName, False)
        self.newPlayerFocusedCb = Checkbox(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NewPilotFocused'), parent=corpSearchOptionsContainer, settingsPath=('char', 'ui'), settingsKey=configName, checked=newPlayerFocused, align=uiconst.TOTOP, callback=self.OnOtherCbChanged)
        self.newPlayerFocusedCb.typeID = rConst.NEWPILOTFOCUSED_TYPEID
        configName = 'corpRec_search_roleplaying'
        roleplaying = settings.char.ui.Get(configName, False)
        self.roleplayerFocusedCb = Checkbox(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RoleplayingFocused2'), parent=corpSearchOptionsContainer, settingsPath=('char', 'ui'), settingsKey=configName, checked=roleplaying, align=uiconst.TOTOP, callback=self.OnOtherCbChanged)
        self.roleplayerFocusedCb.typeID = rConst.ROLEPLAY_TYPEID
        hasAreaOfOperation = False
        adTypesByGroup = get_recruitment_types_for_group_id(rConst.AREA_OF_OPERATIONS_GROUPID)
        for adType in adTypesByGroup:
            if adType.typeID in filterStates:
                hasAreaOfOperation = True
                break

        if not hasAreaOfOperation:
            secClass = sm.GetService('map').GetSecurityClass(session.solarsystemid2)
            key = rConst.HIGHSEC_TYPEID
            if secClass == const.securityClassZeroSec:
                if idCheckers.IsWormholeRegion(session.regionid):
                    key = rConst.WORMHOLESPACE_TYPEID
                else:
                    key = rConst.NULLSEC_TYPEID
            elif secClass == const.securityClassLowSec:
                key = rConst.LOWSEC_TYPEID
            filterStates[key] = FILTERSTATE_WANT
        areaOfOperationMenuParent, areaOfOperationMenu = self.AddUtilMenu('areaOfOperationSearch', corpSearchOptionsContainer, adGroups[rConst.AREA_OF_OPERATIONS_GROUPID].groupName, (self.GetSearchFilterOptions, [ type_.typeID for type_ in adTypesByGroup ], 'areaOfOperations'))
        self.searchAreaOfOperationMenu = areaOfOperationMenu
        languageAdTypes = get_recruitment_types_for_group_id(corputil.RECRUITMENT_GROUP_PRIMARY_LANGUAGE)
        filterStateLanguages = self.GetFilterStatesLanguages()
        if languageAdTypes:
            hasLanguage = False
            adTypeIDs = []
            for adType in languageAdTypes:
                adTypeIDs.append(adType.typeID)
                if adType.typeID in filterStateLanguages:
                    hasLanguage = True

            if not hasLanguage:
                defaultAdType = self.GetDefaultLanguage()
                filterStateLanguages[defaultAdType.typeID] = FILTERSTATE_WANT
                self.SetFilterStatesLanguages(filterStateLanguages)
            languageMenuParent, languageMenu = self.AddUtilMenu('languageSearch', corpSearchOptionsContainer, adGroups[corputil.RECRUITMENT_GROUP_PRIMARY_LANGUAGE].groupName, (self.GetSearchFilterOptions, adTypeIDs, 'language'))
            self.searchLanguageMenu = languageMenu
        self.UpdateSearchFilterHints()
        startTimeZoneProportion, endTimeZoneProportion = settings.char.ui.Get('corp_recruitment_searchTimeZoneRange', (None, None))
        if startTimeZoneProportion is None and endTimeZoneProportion is None:
            currentTime = time.gmtime().tm_hour
            startTime = currentTime - 3
            endTime = currentTime + 3
            if startTime < 0:
                startTime = 24 + startTime
            if endTime > 23:
                endTime = endTime - 24
            startTimeZoneProportion = startTime / 24.0
            endTimeZoneProportion = endTime / 24.0
            settings.char.ui.Set('corp_recruitment_searchTimeZoneRange', (startTimeZoneProportion, endTimeZoneProportion))
        headerText = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/Playtime')
        rangeSelector = self.AddTimeZonePicker(parent=corpSearchOptionsContainer, callback=self.OnSearchTimezoneIncrementChange, OnEndDragChange=self.OnSearchTimezoneRangeChange, startTimeZoneProportion=startTimeZoneProportion, endTimeZoneProportion=endTimeZoneProportion, header=headerText)
        self.searchTimeZoneHint = eveLabel.EveLabelSmall(parent=corpSearchOptionsContainer, name='searchTimeZoneHint', align=uiconst.TOTOP, padTop=4, padLeft=const.defaultPadding * 2)
        self.UpdateSearchTimeZoneHint(rangeSelector, int(startTimeZoneProportion * 24), int(endTimeZoneProportion * 24))
        self._corpSizeLabel = self.CreateLabel(corpSearchOptionsContainer, localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/CorporationSize'), padTop=16)
        sizeRange = [0,
         10,
         50,
         100,
         200,
         500,
         1000]
        step = 1.0 / len(sizeRange)
        incrs = [ (str(i), 5, i) for i in sizeRange ]
        incrs.append(('res:/UI/Texture/classes/RangeSelector/infinity.png', 5, const.corpMaxSize))
        minMembers = settings.char.ui.Get('corporation_recruitment_minmembers', 0)
        if minMembers in sizeRange:
            fromProportion = sizeRange.index(minMembers) * step
        else:
            fromProportion = 0.0
        maxMembers = settings.char.ui.Get('corporation_recruitment_maxmembers', 6300)
        if maxMembers in sizeRange:
            toProportion = sizeRange.index(maxMembers) * step
        else:
            toProportion = 1.0
        corpSize = RangeSelector(parent=corpSearchOptionsContainer, align=uiconst.TOTOP, fromProportion=fromProportion, toProportion=toProportion, OnIncrementChange=self.OnCorporationSizeIncrementChange, OnEndDragChange=self.OnCorporationSizeRangeChange)
        corpSize.SetIncrements(incrs)
        corpSize.SetMinRange(minRange=step)
        corpSize._DoOnChangeCallback()
        self._construct_tax_rate_entries(parent=corpSearchOptionsContainer)
        headerText = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/ExcludeHeader')
        self.AddHeaderLabel(headerText, corpSearchOptionsContainer, 10)
        excludeFriendlyFire = settings.char.ui.Get('corporation_recruitment_excludeFriendlyFireChecked', False)
        self.friendlyFireCb = Checkbox(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/ExcludeFriendlyFire'), parent=corpSearchOptionsContainer, settingsKey='friendlyFireCheckbox', checked=excludeFriendlyFire, align=uiconst.TOTOP, callback=self.OnFriendlyFireCheckboxChange, padTop=6)
        excludeAlliancesChecked = settings.char.ui.Get('corporation_recruitment_excludeAlliancesChecked', False)
        self.inAllianceCheckbox = Checkbox(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AllianceCheckboxText'), parent=corpSearchOptionsContainer, settingsKey='allianceCheckbox', checked=excludeAlliancesChecked, align=uiconst.TOTOP, callback=self.OnAllianceCheckboxChange)
        excludeNotEnoughSP = settings.char.ui.Get('corporation_recruitment_excludeNotEnoughSP', False)
        self.notEnoughSPCheckbox = Checkbox(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/MinimumSPCheckboxText'), parent=corpSearchOptionsContainer, settingsKey='notEnoughSPCheckbox', checked=excludeNotEnoughSP, align=uiconst.TOTOP, callback=self.OnSPCheckboxChange)
        rightSide = Container(name='rightSide', parent=self, padding=const.defaultPadding)
        self.rightErrorLabel = eveLabel.EveLabelMedium(name='rightErrorLabel', parent=rightSide, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, padding=(6, 0, 6, 6))
        self.rightErrorLabel.display = False
        self.corpSearchResultsScroll = BasicDynamicScroll(parent=rightSide)
        self._searchReady = True
        self.loadingWheel = LoadingWheel(parent=self.corpSearchResultsScroll, align=uiconst.CENTER)
        self.loadingWheel.display = False
        if searchCorpID and searchTerm != '':
            self.PopulateSearchResultsByCorpID(searchCorpID)
        else:
            self.SearchAdverts()

    @property
    def max_isk_tax_rate(self):
        return settings.char.ui.Get(UI_SETTING_MAX_ISK_TAX_RATE, 100.0)

    @property
    def max_lp_tax_rate(self):
        return settings.char.ui.Get(UI_SETTING_MAX_LP_TAX_RATE, 100.0)

    def _construct_tax_rate_entries(self, parent):
        self.AddHeaderLabel(headerText=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/MaxISKTaxRate'), parent=parent, padTop=10)
        self._isk_tax_rate_edit = SingleLineEditFloat(name='isk_tax_rate_edit', parent=parent, align=uiconst.TOTOP, maxValue=100.0, setvalue=self.max_isk_tax_rate, OnChange=self._on_isk_tax_rate_change)
        self.AddHeaderLabel(headerText=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/MaxLPTaxRate'), parent=parent, padTop=10)
        self._lp_tax_rate_edit = SingleLineEditFloat(name='lp_tax_rate_edit', parent=parent, align=uiconst.TOTOP, maxValue=100.0, setvalue=self.max_lp_tax_rate, OnChange=self._on_lp_tax_rate_change)

    def _on_isk_tax_rate_change(self, *args):
        settings.char.ui.Set(UI_SETTING_MAX_ISK_TAX_RATE, self._isk_tax_rate_edit.GetValue())
        self.DelayedSearchAdverts(delay=100)

    def _on_lp_tax_rate_change(self, *args):
        settings.char.ui.Set(UI_SETTING_MAX_LP_TAX_RATE, self._lp_tax_rate_edit.GetValue())
        self.DelayedSearchAdverts(delay=100)

    def OnSearchFieldChanged(self, *args):
        if self.searchField.GetValue().strip() == '':
            self.rightErrorLabel.display = False
            self.EnableSearchOptions()
            self.corpSearchResultsScroll.RemoveNodes(self.corpSearchResultsScroll.GetNodes())
            self.DelayedSearchAdverts(100)
            settings.char.ui.Set('corpRecruitmentSearchCorpID', None)

    def SearchByCorpName(self, *args):
        searchText = self.searchField.GetValue().strip()
        if searchText.strip() == '':
            self.EnableSearchOptions()
            return
        corpID = searchOld.Search(searchText.lower(), const.groupCorporation, None, hideNPC=1, exact=MatchBy.partial_terms, searchWndName='corpRecruitment')
        if corpID is None:
            self.searchField.SetValue('')
            settings.char.ui.Set('corpRecruitmentSearchCorpID', None)
            return
        self.PopulateSearchResultsByCorpID(corpID)

    def PopulateSearchResultsByCorpID(self, corpID, *args):
        corpName = cfg.eveowners.Get(corpID).name
        self.searchField.SetValue(corpName)
        settings.char.ui.Set('corpRecruitmentSearchCorpID', corpID)
        self.DisableSearchOptions()
        ads = sm.GetService('corp').GetRecruitmentAdsForCorpID(corpID)
        newAds = [ (None, ad) for ad in ads ]
        entries = self.MakeRecruitmentEntriesFromAdList(newAds, None, None, None, {})
        if entries:
            self.rightErrorLabel.display = False
        if not entries:
            text = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdNotFoundForCorp', corpName=corpName)
            self.rightErrorLabel.text = text
            self.rightErrorLabel.display = True
            entries.append(GetFromClass(User, {'charID': corpID,
             'sublevel': 0,
             'showinfo': True,
             'label': ''}))
        self.corpSearchResultsScroll.Clear()
        if entries:
            self.corpSearchResultsScroll.AddNodes(-1, entries, updateScroll=True)
            hint = ''
        else:
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NoAdsFound')
        self.corpSearchResultsScroll.ShowHint(hint)

    def MakeRecruitmentEntriesFromAdList(self, adList, wantMask, wantLanguageMask, otherMask, expandedAd):
        allData = sm.GetService('corp').GetRecruitementEntryDataList(adList, wantMask, wantLanguageMask, otherMask, expandedAd)
        entries = []
        now = blue.os.GetWallclockTime()
        for data in allData:
            if data.advert.expiryDateTime < now:
                continue
            entry = GetFromClass(RecruitmentEntry, data)
            entries.append(entry)

        return entries

    def EnableSearchOptions(self, *args):
        self.corpSearchOptionsContainer.Enable()
        self.corpSearchOptionsContainer.opacity = 1.0

    def DisableSearchOptions(self, *args):
        self.corpSearchOptionsContainer.Disable()
        self.corpSearchOptionsContainer.opacity = 0.3

    def GetSearchPlayStyleMenu(self, menuParent):
        for combinedGroupID in rConst.PLAYSTYLE_GROUPS:
            groupName = localization.GetByLabel(rConst.COMBINED_GROUPS[combinedGroupID].combinedNamePath)
            adTypeIDs = rConst.COMBINED_GROUPS[combinedGroupID].playstyleTypeIDs
            self.GetSearchFilterOptions(menuParent, adTypeIDs, 'playStyle', header=groupName)
            menuParent.AddSpace()

    def GetSearchFilterOptions(self, menuParent, adTypeIDs, configName, header = None):
        if configName == 'language':
            callback = self.ToggleSearchFilterStateLanguage
            filterStates = self.GetFilterStatesLanguages()
        else:
            callback = self.ToggleSearchFilterState
            filterStates = self.GetFilterStates()
        if header:
            headerChecked = True
            for adTypeID in adTypeIDs:
                filterState = filterStates.get(adTypeID, False)
                if filterState != FILTERSTATE_WANT:
                    headerChecked = False
                    break

            if headerChecked:
                icon = CHECKBOX_ACTIVE_ICON
            else:
                icon = CHECKBOX_INACTIVE_ICON
            menuParent.AddHeader(text=header, callback=(self.ToggleSearchFilterStateOnGroup, adTypeIDs), icon=icon)
        for adTypeID in adTypeIDs:
            adType = get_recruitment_type(adTypeID)
            filterState = filterStates.get(adTypeID, False)
            if filterState == FILTERSTATE_WANT:
                icon = CHECKBOX_ACTIVE_ICON
            else:
                icon = CHECKBOX_INACTIVE_ICON
            menuParent.AddCheckBox(text=adType.typeName, checked=filterState, icon=icon, callback=(callback, adType, filterState), indentation=10)

    def ToggleSearchFilterStateOnGroup(self, adTypeIDs):
        filterStates = self.GetFilterStates()
        all = {}
        currentGroupState = True
        for adTypeID in adTypeIDs:
            filterState = filterStates.get(adTypeID, False)
            if filterState != FILTERSTATE_WANT:
                currentGroupState = False
                break

        if currentGroupState:
            newGroupState = False
        else:
            newGroupState = FILTERSTATE_WANT
        for adTypeID in adTypeIDs:
            filterStates[adTypeID] = newGroupState

        self.SetFilterStates(filterStates)
        self.DelayedSearchAdverts()
        self.UpdateSearchFilterHints()

    def UpdateSearchFilterHints(self):
        adTypes = get_recruitment_types_for_group_id(rConst.PLAYSTYLE_GROUPID)
        text, hint = self.GetSearchFilterHintTextForAdTypes(adTypes, 'playStyle')
        self.searchPlayStyleMenu.SetLabel(text)
        self.searchPlayStyleMenu.hint = hint
        adTypes = get_recruitment_types_for_group_id(rConst.AREA_OF_OPERATIONS_GROUPID)
        text, hint = self.GetSearchFilterHintTextForAdTypes(adTypes, 'areaOfOperations')
        self.searchAreaOfOperationMenu.SetLabel(text)
        self.searchAreaOfOperationMenu.hint = hint
        adTypes = get_recruitment_types_for_group_id(rConst.LANGUAGE_GROUPID)
        text, hint = self.GetSearchFilterHintTextForAdTypes(adTypes, 'language')
        self.searchLanguageMenu.SetLabel(text)
        self.searchLanguageMenu.hint = hint

    def GetSearchFilterHintTextForAdTypes(self, adTypes, configName):
        hint = []
        if configName == 'language':
            filterStates = self.GetFilterStatesLanguages()
        else:
            filterStates = self.GetFilterStates()
        wantCounter = 0
        for adType in adTypes:
            filterState = filterStates.get(adType.typeID, None)
            if filterState == FILTERSTATE_WANT:
                wantCounter += 1
                hint.append(adType.typeName)

        if wantCounter > 0:
            text = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NumFiltersSelected', num=wantCounter)
        else:
            text = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NoFiltersSelected')
        return (text, ', '.join(hint))

    def OnSearchTimezoneIncrementChange(self, rangeSelector, fromData, toData, fromProportion, toProportion):
        settings.char.ui.Set('corp_recruitment_searchTimeZoneRange', (fromProportion, toProportion))
        self.UpdateSearchTimeZoneHint(rangeSelector, fromData[2], toData[2])

    def OnSearchTimezoneRangeChange(self, rangeSelector, fromData, toData, fromProportion, toProportion):
        self.OnSearchTimezoneIncrementChange(rangeSelector, fromData, toData, fromProportion, toProportion)
        self.DelayedSearchAdverts(delay=200)

    def UpdateSearchTimeZoneHint(self, rangeSelector, fromHour, toHour):
        midnightTime = GetTodayMidnight()
        if self.localTimeZoneDiff > 0:
            localFromHour = fromHour - self.localTimeZoneDiff + 24
            localToHour = toHour - self.localTimeZoneDiff + 24
        else:
            localFromHour = fromHour - self.localTimeZoneDiff
            localToHour = toHour - self.localTimeZoneDiff
        fromTime = FmtDate(localFromHour * const.HOUR + midnightTime, fmt='ns')
        if localToHour == 24:
            toTime = localization.GetByLabel('/Carbon/UI/Common/DateTimeQuantity/DateTimeShort2Elements', value1='24', value2='00')
        else:
            toTime = FmtDate(localToHour * const.HOUR + midnightTime, fmt='ns')
        rangeSelector._fromHandle.hint = fromTime
        rangeSelector._toHandle.hint = toTime
        text = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/LocalTime', fromTime=fromTime, toTime=toTime)
        self.searchTimeZoneHint.text = text
        self.IndicateLoadingState(loading=True)

    def OnCorporationSizeIncrementChange(self, rangeSelector, fromData, toData, *args):
        settings.char.ui.Set('corporation_recruitment_minmembers', fromData[2])
        settings.char.ui.Set('corporation_recruitment_maxmembers', toData[2])
        self.IndicateLoadingState(loading=True)

    def OnCorporationSizeRangeChange(self, rangeSelector, fromData, toData, *args):
        self.OnCorporationSizeIncrementChange(rangeSelector, fromData, toData)
        self.DelayedSearchAdverts(delay=200)

    def OnFriendlyFireCheckboxChange(self, checkbox):
        self.OnCheckboxChanged(checkbox, 'corporation_recruitment_excludeFriendlyFireChecked')

    def OnAllianceCheckboxChange(self, checkbox):
        self.OnCheckboxChanged(checkbox, 'corporation_recruitment_excludeAlliancesChecked')

    def OnSPCheckboxChange(self, checkbox):
        self.OnCheckboxChanged(checkbox, 'corporation_recruitment_excludeNotEnoughSP')

    def OnCheckboxChanged(self, checkbox, settingString):
        newValue = checkbox.checked
        settings.char.ui.Set(settingString, newValue)
        self.DelayedSearchAdverts()

    def OnOtherCbChanged(self, checkbox):
        checkbox.UpdateSettings()
        adType = get_recruitment_type(checkbox.typeID)
        oldValue = not checkbox.GetValue()
        self.ToggleSearchFilterState(adType, oldValue)

    def DelayedSearchAdverts(self, delay = 800):
        if getattr(self, '_searchReady', False):
            self.delayedSearchAdverts = timerstuff.AutoTimer(delay, self.SearchAdverts)
            self.IndicateLoadingState(loading=True)

    def SearchAdverts(self):
        self.corpSearchResultsScroll.ShowLoading()
        try:
            self._SearchAdverts()
        finally:
            self.corpSearchResultsScroll.HideLoading()

    def _SearchAdverts(self):
        self.delayedSearchAdverts = None
        searchMask = self.searchMask
        settings.char.ui.Set('corporation_recruitment_types', searchMask)
        newResultsEntries = self.GetSearchResults()
        if newResultsEntries:
            hint = None
        else:
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NoAdsFound')
        scroll = self.corpSearchResultsScroll
        newByIDs = {}
        for each in newResultsEntries:
            newByIDs[each.advert.adID] = each

        self.rightErrorLabel.display = False
        removeNodes = []
        keepInScroll = []
        currentAdIDs = []
        for each in scroll.GetNodes():
            currentAdIDs.append(each.advert.adID)
            if each.advert.adID not in newByIDs:
                removeNodes.append(each)
            else:
                each.update(newByIDs[each.advert.adID])
                keepInScroll.append(each)

        for each in newResultsEntries[:]:
            if each.advert.adID in currentAdIDs:
                newResultsEntries.remove(each)
            else:
                each.name = cfg.eveowners.Get(each.corporationID).name

        self.corpSearchResultsScroll.ShowHint(hint)
        if removeNodes:
            self.corpSearchResultsScroll.RemoveNodes(removeNodes, updateScroll=False)
        if newResultsEntries:
            self.corpSearchResultsScroll.AddNodes(-1, newResultsEntries, updateScroll=False)
        allNodes = self.corpSearchResultsScroll.GetNodes()
        if allNodes:
            sortedAllNodes = sorted(allNodes, key=lambda x: (x.grade, x.createDateTime, x.name.lower()), reverse=True)
            self.corpSearchResultsScroll.SetOrderedNodes(sortedAllNodes)
        for each in keepInScroll:
            if each.panel:
                each.panel.Load(each)

        self.IndicateLoadingState(loading=0)

    def IndicateLoadingState(self, loading = False):
        try:
            if loading:
                self.loadingWheel.Show()
                self.corpSearchResultsScroll.sr.maincontainer.opacity = 0.2
            else:
                self.loadingWheel.Hide()
                self.corpSearchResultsScroll.sr.maincontainer.opacity = 1.0
        except:
            pass

    def GetSearchResults(self, *args):
        expandedAd = settings.char.ui.Get('corporation_recruitmentad_expanded', {})
        minMembers = settings.char.ui.Get('corporation_recruitment_minmembers', 0)
        maxMembers = settings.char.ui.Get('corporation_recruitment_maxmembers', 1000)
        maxISKTaxRate = self.max_isk_tax_rate / 100.0
        maxLPTaxRate = self.max_lp_tax_rate / 100.0
        excludeAlliancesChecked = settings.char.ui.Get('corporation_recruitment_excludeAlliancesChecked', False)
        excludeFriendlyFire = settings.char.ui.Get('corporation_recruitment_excludeFriendlyFireChecked', False)
        excludeNotEnoughSP = settings.char.ui.Get('corporation_recruitment_excludeNotEnoughSP', False)
        fromProportion, toProportion = settings.char.ui.Get('corp_recruitment_searchTimeZoneRange', (0.0, 1.0))
        fromHour = fromProportion * 24
        toHour = toProportion * 24

        def GetSearchMask(myFilterStates):
            mask = 0
            for adTypeID, fs in myFilterStates.iteritems():
                adType = get_recruitment_type(adTypeID)
                if adType and fs == FILTERSTATE_WANT:
                    mask = AddBitToMask(bit=adType.typeMask, mask=mask)

            return mask

        filterStates = self.GetFilterStates()
        wantMask = GetSearchMask(filterStates)
        wantMask = RemoveOldPlaystylesFromMask(wantMask)
        filterStateLanguages = self.GetFilterStatesLanguages()
        wantLanguageMask = GetSearchMask(filterStateLanguages)
        if excludeNotEnoughSP:
            spRestriction = int(sm.GetService('skills').GetSkillPoints())
        else:
            spRestriction = None
        otherMask = 0
        for cb in [self.newPlayerFriendlyCb, self.newPlayerFocusedCb, self.roleplayerFocusedCb]:
            if cb.GetValue():
                typeID = getattr(cb, 'typeID')
                otherMask = AddBitToMask(bit=TwoToThePowerOf(typeID), mask=otherMask)

        searchTimeMask = BuildMask(fromHour, toHour)
        ads = sm.GetService('corp').GetRecruitmentAdsByCriteria(typeMask=wantMask, langMask=wantLanguageMask, excludeAlliances=excludeAlliancesChecked, excludeFriendlyFire=excludeFriendlyFire, spRestriction=spRestriction, minMembers=minMembers, maxMembers=maxMembers, maxISKTaxRate=maxISKTaxRate, maxLPTaxRate=maxLPTaxRate, searchTimeMask=searchTimeMask, otherMask=otherMask)
        entries = self.MakeRecruitmentEntriesFromAdList(ads, wantMask, wantLanguageMask, otherMask, expandedAd)
        return entries

    def ToggleSearchFilterState(self, adType, filterState):
        filterState = not filterState
        filterStates = self.GetFilterStates()
        filterStates[adType.typeID] = filterState
        self.SetFilterStates(filterStates)
        self.DelayedSearchAdverts()
        self.UpdateSearchFilterHints()

    def ToggleSearchFilterStateLanguage(self, adType, filterState):
        filterState = not filterState
        filterStates = self.GetFilterStatesLanguages()
        filterStates[adType.typeID] = filterState
        self.SetFilterStatesLanguages(filterStates)
        self.DelayedSearchAdverts()
        self.UpdateSearchFilterHints()

    def GetFilterStates(self):
        return settings.char.ui.Get('corporation_recruitment_searchFilterStatesX', {})

    def SetFilterStates(self, filterStates):
        settings.char.ui.Set('corporation_recruitment_searchFilterStatesX', filterStates)

    def GetFilterStatesLanguages(self):
        return settings.char.ui.Get('corporation_recruitment_searchFilterStatesLanguagesX', {})

    def SetFilterStatesLanguages(self, filterStates):
        settings.char.ui.Set('corporation_recruitment_searchFilterStatesLanguagesX', filterStates)
