#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\warDeclare.py
import carbonui.const as uiconst
import gametime
import itertoolsext
import uthread
from caching.memoize import Memoize
from carbon.common.script.util.format import FmtDate
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui.button.const import HEIGHT_NORMAL
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.util.sortUtil import SortListOfTuples
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall, WndCaptionLabel, EveLabelMediumBold
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.singlelineedits.util import GetDroppedCorpOrAllianceName
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import FillThemeColored, SpriteThemeColored
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from eve.client.script.ui.shared.neocom.corporation.war.warDeclareController import WarDeclareController, STEP_PICK_TYPE_CORP, STEP_PICK_HQ, STEP_COST, STEP_SUMMARY, GetWarTypeText, GetWarPartiesText, MUTUAL_WAR, AGGRESSIVE_WAR
from eve.client.script.ui.shared.neocom.corporation.war.warReportConst import ATTACKER_COLOR, DEFENDER_COLOR
from eve.client.script.ui.shared.userentry import User
from eve.client.script.ui.structure.structureIcon import StructureIcon
from eve.common.script.util.eveFormat import FmtISK
from eveservices.menu import GetMenuService
from evewar.const import WAR_SPOOLUP_HOURS, WAR_MUTUAL_WAR_EXPIRY_DAYS, WAR_COOLDOWN_HOURS
from localization import GetByLabel
from signals.signalUtil import ChangeSignalConnect
from evewar import warConst
import eve.common.lib.appConst as appConst
from eve.common.lib import appConst as const
NO_WAR_PERMIT_TEXTURE_PATH = 'res:/UI/Texture/classes/War/noWarPermit.png'
AT_WAR_TEXTURE_PATH = 'res:/UI/Texture/classes/War/atWar_24.png'
ALLIANCE_LOGO = 'res:/UI/Texture/Icons/73_16_31.png'

class WarDeclareWnd(Window):
    __guid__ = 'warDeclareWnd'
    default_minSize = (450, 500)
    default_windowID = 'warDeclareWnd'
    default_iconNum = 'res:/ui/Texture/WindowIcons/wars.png'
    default_captionLabelPath = 'UI/Corporations/Wars/WarDeclareWarDeclaration'

    def DebugReload(self, *args):
        self.Close()
        uthread.new(WarDeclareWnd)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        defenderID = attributes.defenderOwnerID
        self.currentPageUI = None
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=52, clipChildren=True)
        SpriteThemeColored(name='mainicon', parent=self.topParent, state=uiconst.UI_DISABLED, pos=(6, 2, 48, 48), texturePath=self.iconNum, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        exactChecked = bool(defenderID)
        self.warDeclareController = WarDeclareController(defenderID=defenderID, exactChecked=exactChecked)
        self.windowCaption = WndCaptionLabel(text='', parent=self.topParent, left=60, state=uiconst.UI_DISABLED)
        self.btnCont = Container(name='bntCont', parent=self.sr.main, height=HEIGHT_NORMAL, align=uiconst.TOBOTTOM, padding=(0, 16, 0, 0))
        self.mainArea = Container(name='mainArea', parent=self.sr.main)
        self.AddBtns()
        self.LoadPage()
        self.ChangeSignalConnection()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.warDeclareController.on_war_info_changed, self.OnWarInfoChanged), (self.warDeclareController.on_loading_changed, self.LoadingChanged), (self.warDeclareController.on_war_type_changed, self.WarTypeChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def AddBtns(self):
        self.nextBtn = Button(parent=self.btnCont, label=GetByLabel('/Carbon/UI/Common/Next'), func=self.GoToNextPage, align=uiconst.BOTTOMRIGHT)
        self.declareWarBtn = Button(parent=self.btnCont, label='', func=self.TryDeclareWar, align=uiconst.BOTTOMRIGHT)
        self.backBtn = Button(parent=self.btnCont, label=GetByLabel('/Carbon/UI/Commands/Back'), func=self.GoToPreviousPage, align=uiconst.BOTTOMLEFT)

    def GoToNextPage(self, *args):
        self.warDeclareController.GoToNextPage()
        self.LoadPage()

    def GoToPreviousPage(self, *args):
        self.warDeclareController.GotToPreviousPage()
        self.LoadPage()

    def LoadPage(self):
        self.UpdateHeader()
        currentPage = self.warDeclareController.GetCurrentPage()
        allSteps = self.warDeclareController.GetAllSteps()
        if currentPage not in allSteps:
            currentPage = allSteps[0]
        self.mainArea.Flush()
        self.currentPageUI = None
        if currentPage == STEP_PICK_TYPE_CORP:
            self.currentPageUI = WarDeclarePagePickTypeCorp(parent=self.mainArea, warDeclareController=self.warDeclareController)
        elif currentPage == STEP_PICK_HQ:
            self.currentPageUI = WarDeclarePagePickHQ(parent=self.mainArea, warDeclareController=self.warDeclareController)
        elif currentPage == STEP_COST:
            self.currentPageUI = WarDeclarePageCost(parent=self.mainArea, warDeclareController=self.warDeclareController)
        elif currentPage == STEP_SUMMARY:
            self.currentPageUI = WarDeclarePageSummary(parent=self.mainArea, warDeclareController=self.warDeclareController)
        self.UpdateButtons()

    def UpdateHeader(self):
        pageLabelPath, currentNum, totalNum = self.warDeclareController.GetPageNameAndCount()
        text = GetByLabel(pageLabelPath)
        pageText = ' <color=0x66ffffff>(%s/%s)</color>' % (currentNum, totalNum)
        self.windowCaption.SetText(text + pageText)

    def UpdateButtons(self):
        currentPage = self.warDeclareController.GetCurrentPage()
        self.declareWarBtn.display = False
        self.backBtn.display = False
        self.nextBtn.display = False
        if currentPage == STEP_SUMMARY:
            self.declareWarBtn.display = True
            if self.warDeclareController.IsMutualWar():
                text = GetByLabel('UI/Corporations/Wars/DeclareWarFinializeMutualDeclaration')
            else:
                text = GetByLabel('UI/Corporations/Wars/DeclareWarFinializeAggressiveDeclaration')
            self.declareWarBtn.SetLabel(text)
        else:
            self.nextBtn.display = True
            if self.CanContinueFromPage():
                self.nextBtn.Enable()
            else:
                self.nextBtn.Disable()
        if currentPage != STEP_PICK_TYPE_CORP:
            self.backBtn.display = True

    def CanContinueFromPage(self):
        currentPage = self.warDeclareController.GetCurrentPage()
        if currentPage == STEP_PICK_TYPE_CORP:
            if not self.warDeclareController.GetDefenderID():
                return False
        if self.warDeclareController.IsAggressiveWar():
            return self._CanContinueWithAggressiveWar(currentPage)
        return True

    def _CanContinueWithAggressiveWar(self, currentPage):
        if currentPage == STEP_PICK_HQ and not self.warDeclareController.GetWarHQ():
            return False
        return True

    def TryDeclareWar(self, *args):
        if self.warDeclareController.IsMutualWar():
            self._DoDeclareMutualWar()
        else:
            self._DoDeclareAggressiveWar()

    def _DoDeclareMutualWar(self):
        opponentID = self.warDeclareController.GetDefenderID()
        sm.GetService('mutualWarInvites').SendInvite(opponentID)
        opponentName = cfg.eveowners.Get(opponentID).ownerName
        text = GetByLabel('UI/Corporations/Wars/WarInviteHasBeenSent', opponentName=opponentName)
        eve.Message('CustomNotify', {'notify': text})
        self.Close()

    def _DoDeclareAggressiveWar(self):
        attackerID = self.warDeclareController.GetAttackerID()
        if attackerID != (session.allianceid or session.corpid):
            raise RuntimeError('No longer the same creator')
        warHq = self.warDeclareController.GetWarHQ()
        if not warHq:
            raise RuntimeError("No war hq selected, can't create war!")
        defenderID = self.warDeclareController.GetDefenderID()
        if not defenderID:
            raise RuntimeError('No defender selected')
        if session.allianceid:
            sm.GetService('alliance').DeclareWarAgainst(defenderID, warHQ=warHq)
        else:
            sm.GetService('corp').DeclareWarAgainst(defenderID, warHQ=warHq)
        self.Close()

    def OnWarInfoChanged(self):
        self.UpdateButtons()
        self.UpdateHeader()
        if self.currentPageUI and isinstance(self.currentPageUI, (WarDeclarePagePickTypeCorp, WarDeclarePagePickHQ)):
            self.currentPageUI.SetSelectedText()

    def LoadingChanged(self, isLoading):
        if isLoading:
            self.ShowLoad()
        else:
            self.HideLoad()

    def WarTypeChanged(self):
        if self.currentPageUI and isinstance(self.currentPageUI, WarDeclarePagePickTypeCorp):
            self.currentPageUI.SearchForOwner()

    def Close(self, *args, **kwds):
        with EatSignalChangingErrors(errorMsg='WarDeclareWnd'):
            self.ChangeSignalConnection(connect=False)
        Window.Close(self, *args, **kwds)


class WarDeclarePagePickTypeCorp(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.warDeclareController = attributes.warDeclareController
        EveLabelMedium(parent=self, align=uiconst.TOTOP, text=GetByLabel('UI/Corporations/Wars/WarDeclareSummaryWarType'))
        warType = self.warDeclareController.GetWarType()
        RadioButton(parent=self, text=GetByLabel('UI/Corporations/Wars/WarTypeAggressive'), groupname='warType', align=uiconst.TOTOP, checked=warType == AGGRESSIVE_WAR, callback=self.WarTypeRadioBtnChanged, retval=AGGRESSIVE_WAR)
        RadioButton(parent=self, text=GetByLabel('UI/Corporations/Wars/WarTypeMutual'), groupname='warType', align=uiconst.TOTOP, checked=warType == MUTUAL_WAR, callback=self.WarTypeRadioBtnChanged, retval=MUTUAL_WAR)
        EveLabelSmall(text=GetByLabel('UI/Shared/TypeSearchString'), parent=self, state=uiconst.UI_NORMAL, align=uiconst.TOTOP, top=10)
        currentOpponent = self.warDeclareController.GetDefenderID()
        inpSetValue = ''
        if currentOpponent:
            inpSetValue = cfg.eveowners.Get(currentOpponent).name
        inputArea = Container(name='inputArea', parent=self, align=uiconst.TOTOP)
        self.inpt = SingleLineEditText(name='inpt', parent=inputArea, pos=(0, 0, 200, 0), align=uiconst.CENTERLEFT, maxLength=100, OnReturn=self.SearchForOwner, setvalue=inpSetValue, OnClearFilter=self.SearchForOwner)
        self.inpt.OnDropData = self.OnDropDataInSearcField
        clearBtn = self.inpt.ShowClearButton()
        clearBtn.OnClick = self.SearchFieldCleared
        btnLeft = self.inpt.left + self.inpt.width + 2
        btnText = GetByLabel('UI/Corporations/CorporationWindow/Standings/Search')
        btn = Button(parent=inputArea, label=btnText, left=btnLeft, align=uiconst.CENTERLEFT, func=self.SearchForOwner, btn_default=1)
        exeactChecked = self.warDeclareController.GetExactCheckedValue()
        self.exactChkBox = Checkbox(text=GetByLabel('UI/Corporations/CorporationWindow/Standings/SearchExact'), parent=inputArea, settingsKey='declareWar_SearchExactChk', align=uiconst.CENTERLEFT, pos=(btn.left + btn.width + 10,
         1,
         200,
         0), callback=self.ExactCheckedChanged, checked=exeactChecked)
        inputArea.height = max(self.inpt.height, btn.height, self.exactChkBox.height) + 2
        self.selectedCont = Container(name='selectedCont', parent=self, padding=const.defaultPadding, align=uiconst.TOBOTTOM, height=51)
        FillThemeColored(bgParent=self.selectedCont, align=uiconst.TOALL, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.1)
        self.selectedLabel = EveLabelMedium(parent=self, align=uiconst.TOBOTTOM, text=GetByLabel('UI/Corporations/Wars/WarDeclareSelectedOpponent'), padTop=8)
        self.SetSelectedText()
        self.scroll = Scroll(parent=self, padding=const.defaultPadding)
        self.scroll.multiSelect = False
        self.scroll.OnSelectionChange = self.OnOwnerSelectionChange
        if currentOpponent:
            self.SearchForOwner()
        else:
            noContentHint = GetByLabel('UI/Corporations/Wars/SearchForEntityToWarDeclare')
            self.scroll.Load(noContentHint=noContentHint)

    def SetSelectedText(self):
        self.selectedCont.Flush()
        currentOpponent = self.warDeclareController.GetDefenderID()
        if currentOpponent:
            info = cfg.eveowners.Get(currentOpponent)
            selectedLogo = GetLogoIcon(itemID=currentOpponent, parent=self.selectedCont, acceptNone=False, align=uiconst.CENTERLEFT, pos=(0, 0, 32, 32), state=uiconst.UI_NORMAL, ignoreSize=True)
            self.sr.namelabel = EveLabelMedium(text=info.ownerName, name='nameLabel', parent=self.selectedCont, state=uiconst.UI_DISABLED, pos=(40, 0, 0, 0), align=uiconst.CENTERLEFT)
            self.selectedCont.state = uiconst.UI_NORMAL
            self.selectedCont.GetMenu = lambda *args: GetMenuService().GetMenuFromItemIDTypeID(info.ownerID, info.typeID)
        else:
            ConstructNoResultsContainer(self.selectedCont)
            self.selectedCont.noResultsLabel.text = '<center>%s</center>' % GetByLabel('UI/Corporations/Wars/WarDeclareNoOpponentSelected')
            self.selectedCont.state = uiconst.UI_DISABLED

    def WarTypeRadioBtnChanged(self, cb):
        self.warDeclareController.SetWarType(cb.GetReturnValue())

    def ExactCheckedChanged(self, cb):
        self.warDeclareController.SetExactCheckedValue(cb.GetValue())

    def SearchFieldCleared(self, *args):
        SingleLineEditText.OnClearButtonClick(self.inpt)
        self.SearchForOwner()

    def OnDropDataInSearcField(self, dragObj, nodes):
        SingleLineEditText.OnDropData(self.inpt, dragObj, nodes)
        itemInfo = GetDroppedCorpOrAllianceName(nodes[0])
        if itemInfo is not None:
            self.inpt.SetValueAfterDragging(itemInfo.itemName, itemInfo.itemID)

    def SearchForOwner(self, *args):
        scrolllist = []
        self.warDeclareController.ChangeLoading(True)
        noContentHint = ''
        try:
            self.scroll.ShowLoading()
            groupID, exact = const.groupCorporation, self.exactChkBox.GetValue()
            searchStr = self.inpt.GetValue().strip()
            if len(searchStr) < 1:
                noContentHint = GetByLabel('UI/Corporations/Wars/SearchForEntityToWarDeclare')
                self.warDeclareController.SetDefenderID(None)
                return
            warableResultByID, nonWarableCorpIDs = sm.GetService('war').SearchForWarableEntity(searchStr, exact)
            warableResultByID.pop(session.allianceid, None)
            warableResultByID.pop(session.corpid, None)
            if warableResultByID:
                scrolllist = self.GetUnsortedScrollList(warableResultByID.values())
            else:
                if exact:
                    noContentHint = GetByLabel('UI/Corporations/CorporationWindow/Standings/ExactCorpOrAllianceNameNotFound', searchString=searchStr)
                else:
                    noContentHint = GetByLabel('UI/Corporations/CorporationWindow/Standings/CorpOrAllianceNameNotFound', searchString=searchStr)
                self.warDeclareController.SetDefenderID(None)
            if nonWarableCorpIDs:
                scrolllist += self.GetUnsortedNonWarableCorporationsScrollList(nonWarableCorpIDs)
            scrolllist = SortListOfTuples(scrolllist)
        finally:
            self.scroll.Load(fixedEntryHeight=18, contentList=scrolllist, noContentHint=noContentHint)
            self.scroll.HideLoading()
            self.warDeclareController.ChangeLoading(False)

    def GetUnsortedScrollList(self, ownerInfos):
        selectedOpponent = self.warDeclareController.GetDefenderID()
        isMutualWar = self.warDeclareController.IsMutualWar()
        scrolllist = []
        ownerIDs = [ each.ownerID for each in ownerInfos ]
        cfg.eveowners.Prime(ownerIDs)
        if isMutualWar:
            outgoingTreatiesOwnerIDs = set()
        else:
            outgoingTreaties, incomingTreaties = self.GetPeaceTreaties()
            outgoingTreatiesOwnerIDs = {x.otherOwnerID for x in outgoingTreaties}
        if selectedOpponent:
            selectedOpponentInfo = itertoolsext.first_or_default(ownerInfos, lambda x: x.ownerID == selectedOpponent, None)
            hasPeaceTreaty = selectedOpponent in outgoingTreatiesOwnerIDs
            if not selectedOpponentInfo or not isMutualWar and (not selectedOpponentInfo.warPermit or hasPeaceTreaty):
                selectedOpponent = None
                self.warDeclareController.SetDefenderID(selectedOpponent)
        existingOpponents = self.GetOpponentsInOngoingWars()
        for each in ownerInfos:
            ownerID = each.ownerID
            if ownerID in (session.corpid, session.allianceid):
                continue
            hasWarPermit = each.warPermit
            alreadyAtWar = ownerID in existingOpponents
            hasPeaceTreaty = ownerID in outgoingTreatiesOwnerIDs
            isDisabledEntry = False
            if alreadyAtWar:
                isDisabledEntry = True
            elif not isMutualWar:
                if not hasWarPermit:
                    isDisabledEntry = True
                elif hasPeaceTreaty:
                    isDisabledEntry = True
            owner = cfg.eveowners.Get(ownerID)
            selected = selectedOpponent == ownerID
            entry = GetFromClass(UserSelect, {'label': owner.ownerName,
             'charID': ownerID,
             'isSelected': selected,
             'hasWarPermit': hasWarPermit,
             'isMutualWar': isMutualWar,
             'isDisabledEntry': isDisabledEntry,
             'selectable': not isDisabledEntry,
             'alreadyAtWar': alreadyAtWar,
             'hasPeaceTreaty': hasPeaceTreaty})
            sortTuple = (-selected, owner.ownerName.lower())
            scrolllist.append((sortTuple, entry))

        return scrolllist

    @Memoize(2)
    def GetPeaceTreaties(self):
        outgoingTreaties, incomingTreaties = sm.GetService('war').GetPeaceTreaties()
        return (outgoingTreaties, incomingTreaties)

    def GetOpponentsInOngoingWars(self):
        attackerID = self.warDeclareController.GetAttackerID()
        wars = sm.GetService('war').GetWars(attackerID)
        warParties = set()
        for eachWar in wars.itervalues():
            if eachWar.timeFinished is not None:
                continue
            warParties.add(eachWar.declaredByID)
            warParties.add(eachWar.againstID)

        warParties.discard(attackerID)
        return warParties

    def OnOwnerSelectionChange(self, selectedNodes, *args):
        if selectedNodes:
            ownerID = selectedNodes[0].itemID
        else:
            ownerID = None
        self.warDeclareController.SetDefenderID(ownerID)

    def GetUnsortedNonWarableCorporationsScrollList(self, corpIDs):
        scrolllist = []
        for eachCorpID in corpIDs:
            owner = cfg.eveowners.Get(eachCorpID)
            entry = GetFromClass(UserSelect, {'label': owner.ownerName,
             'charID': eachCorpID,
             'isDisabledEntry': True,
             'selectable': False,
             'inAlliance': True})
            sortTuple = (0, owner.ownerName.lower())
            scrolllist.append((sortTuple, entry))

        return scrolllist


class WarDeclarePagePickHQ(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.warDeclareController = attributes.warDeclareController
        text = GetByLabel('UI/Corporations/Wars/WarDeclarePickHqText', numHours=24)
        EveLabelMedium(text=text, parent=self, padding=(6, 2, 6, 0), state=uiconst.UI_NORMAL, align=uiconst.TOTOP)
        filterEditCont = Container(parent=self, align=uiconst.TOTOP, height=24)
        self.filterEdit = QuickFilterEdit(name='filterEdit', parent=filterEditCont, hintText=GetByLabel('UI/Inventory/Filter'), maxLength=64, left=4, align=uiconst.BOTTOMRIGHT, OnClearFilter=self.OnFilterEditCleared, width=120, isTypeField=True)
        self.filterEdit.ReloadFunction = self.OnFilterEdit
        self.selectedCont = Container(name='selectedCont', parent=self, padding=const.defaultPadding, align=uiconst.TOBOTTOM, height=51)
        FillThemeColored(bgParent=self.selectedCont, align=uiconst.TOALL, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.1)
        self.selectedLabel = EveLabelMedium(parent=self, align=uiconst.TOBOTTOM, text=GetByLabel('UI/Corporations/Wars/WarDeclareSelectedWarHq'), padTop=8, padLeft=4)
        self.SetSelectedText()
        self.structureScroll = Scroll(name='structureScroll', parent=self, padding=const.defaultPadding)
        self.structureScroll.multiSelect = False
        self.structureScroll.OnSelectionChange = self.OnScrollSelectionChange
        uthread.new(self.LoadStructureList)

    def SetSelectedText(self):
        self.selectedCont.Flush()
        warHQ = self.warDeclareController.GetWarHQ()
        if warHQ:
            structureInfo = sm.GetService('structureDirectory').GetStructureInfo(warHQ)
            itemIcon = StructureIcon(parent=self.selectedCont, align=uiconst.CENTERLEFT, typeID=structureInfo.typeID, structureID=structureInfo.structureID, pos=(0, 0, 32, 32), state=uiconst.UI_PICKCHILDREN)
            namelabel = EveLabelMedium(text=structureInfo.itemName, name='nameLabel', parent=self.selectedCont, state=uiconst.UI_DISABLED, pos=(40, 0, 0, 0), align=uiconst.CENTERLEFT)
            self.selectedCont.state = uiconst.UI_NORMAL
            self.selectedCont.GetMenu = lambda *args: GetMenuService().GetMenuFromItemIDTypeID(structureInfo.structureID, structureInfo.typeID)
        else:
            ConstructNoResultsContainer(self.selectedCont)
            self.selectedCont.noResultsLabel.text = '<center>%s</center>' % GetByLabel('UI/Corporations/Wars/WarDeclareNoWarHqSelected')
            self.selectedCont.state = uiconst.UI_DISABLED

    def LoadStructureList(self):
        validWarHQs = sm.GetService('structureDirectory').GetValidWarHQs()
        validStructureIDs = {x.structureID for x in validWarHQs}
        selectedHQ = self.warDeclareController.GetWarHQ()
        if selectedHQ not in validStructureIDs:
            selectedHQ = None
            self.warDeclareController.SetWarHQ(selectedHQ)
        filterText = self.filterEdit.GetValue().strip().lower()
        scrollList = []
        for each in validWarHQs:
            if filterText and each.itemName.lower().find(filterText) < 0:
                continue
            isSelected = each.structureID == selectedHQ
            sortValue = (-isSelected, each.itemName.lower())
            entry = GetFromClass(Item, {'label': each.itemName,
             'typeID': each.typeID,
             'itemID': each.structureID,
             'getIcon': True,
             'isSelected': isSelected,
             'showTooltip': False})
            scrollList.append((sortValue, entry))

        scrollList = SortListOfTuples(scrollList)
        self.structureScroll.ShowLoading()
        if validWarHQs and filterText:
            noContentHint = GetByLabel('UI/Corporations/Wars/WarDeclareNoPotentialHqFoundWithFilter')
        else:
            noContentHint = GetByLabel('UI/Corporations/Wars/WarDeclareNoPotentialHqFound')
        self.structureScroll.Load(contentList=scrollList, noContentHint=noContentHint)
        self.structureScroll.HideLoading()

    def OnFilterEdit(self, *args):
        self.LoadStructureList()

    def OnFilterEditCleared(self, *args):
        self.LoadStructureList()

    def OnScrollSelectionChange(self, selectedNodes):
        if selectedNodes:
            warHq = selectedNodes[0].itemID
        else:
            warHq = None
        self.warDeclareController.SetWarHQ(warHq)


class WarDeclarePageCost(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.warDeclareController = attributes.warDeclareController
        warCost = FmtISK(warConst.COST_OF_WAR, 0)
        text = GetByLabel('UI/Corporations/Wars/WarDeclareCost', warCost=warCost, numHoursCooldown=WAR_COOLDOWN_HOURS)
        EditPlainText(name='warDeclarePageCostEdit', setvalue=text, parent=self, align=uiconst.TOALL, padding=4)


class WarDeclarePageSummary(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        textCont = Container(parent=self, padding=(4, 90, 4, 4))
        PanelUnderlay(bgParent=textCont, name='background')
        self.warDeclareController = attributes.warDeclareController
        iconSize = 64
        iconCont = Container(name='iconCont', parent=self, align=uiconst.TOTOP, height=80)
        centerIconCont = Container(name='centerIconCont', parent=iconCont, align=uiconst.CENTER, pos=(0, 0, 180, 80))
        leftIconCont = Container(name='leftIconCont', parent=centerIconCont, align=uiconst.TOLEFT, width=iconSize)
        rightIconCont = Container(name='rightIconCont', parent=centerIconCont, align=uiconst.TORIGHT, width=iconSize)
        warType = self.warDeclareController.GetWarType()
        attackerLeftText, defenderLeftText = GetWarPartiesText(warType)
        attackerInfo = cfg.eveowners.Get(self.warDeclareController.GetAttackerID())
        defenderInfo = cfg.eveowners.Get(self.warDeclareController.GetDefenderID())
        attackerLogo = GetLogoIcon(itemID=self.warDeclareController.GetAttackerID(), parent=leftIconCont, acceptNone=False, align=uiconst.TOPRIGHT, height=iconSize, width=iconSize, state=uiconst.UI_NORMAL, ignoreSize=True, hint='%s:<br>%s' % (attackerLeftText, attackerInfo.name))
        attackerLogo.OnClick = (self.ShowInfo, attackerInfo.ownerID, attackerInfo.typeID)
        defenderLogo = GetLogoIcon(itemID=self.warDeclareController.GetDefenderID(), parent=rightIconCont, acceptNone=False, align=uiconst.TOPRIGHT, height=iconSize, width=iconSize, state=uiconst.UI_NORMAL, ignoreSize=True, hint='%s:<br>%s' % (defenderLeftText, defenderInfo.name))
        defenderLogo.OnClick = (self.ShowInfo, defenderInfo.ownerID, defenderInfo.typeID)
        attackerLabel = EveLabelMedium(text=attackerLeftText, parent=leftIconCont, align=uiconst.CENTERBOTTOM)
        defenderLabel = EveLabelMedium(text=defenderLeftText, parent=rightIconCont, align=uiconst.CENTERBOTTOM)
        if not self.warDeclareController.IsMutualWar():
            attackerLabel.SetRGBA(*ATTACKER_COLOR)
            defenderLabel.SetRGBA(*DEFENDER_COLOR)
        self.swordsSprite = Sprite(name='swordsSprite', parent=centerIconCont, align=uiconst.CENTER, pos=(0, 0, 32, 32), state=uiconst.UI_NORMAL, opacity=0.3, texturePath='res:/UI/Texture/WindowIcons/wars.png', hint=GetByLabel('UI/Corporations/Wars/Vs'))
        textsToAdd = []
        warType = self.warDeclareController.GetWarType()
        warTypeTuple = (GetByLabel('UI/Corporations/Wars/WarDeclareSummaryWarType'), GetWarTypeText(warType))
        textsToAdd.append(warTypeTuple)
        attackerLink = GetShowInfoLink(attackerInfo.typeID, attackerInfo.name, attackerInfo.ownerID)
        attackerTuple = (attackerLeftText, attackerLink)
        textsToAdd.append(attackerTuple)
        defenderLink = GetShowInfoLink(defenderInfo.typeID, defenderInfo.name, defenderInfo.ownerID)
        defenderTuple = (defenderLeftText, defenderLink)
        textsToAdd.append(defenderTuple)
        if self.warDeclareController.IsMutualWar():
            startTuple = (GetByLabel('UI/Corporations/Wars/WarDeclareSummaryStartTime'), GetByLabel('UI/Corporations/Wars/WarDeclareSummaryMutualWarStartTime', numHoursInSpoolup=WAR_SPOOLUP_HOURS))
            textsToAdd.append(startTuple)
            textsToAdd.append((None, None))
            expiryDate = gametime.GetWallclockTime() + WAR_MUTUAL_WAR_EXPIRY_DAYS * appConst.DAY
            expiryTuple = (GetByLabel('UI/Corporations/Wars/WarDeclareSummaryMutalWarInviteExpiry'), FmtDate(expiryDate))
            textsToAdd.append(expiryTuple)
        else:
            wouldWarStartImmediately = self.WouldWarStartImmediately()
            if wouldWarStartImmediately:
                startTuple = (GetByLabel('UI/Corporations/Wars/WarDeclareSummaryStartTime'), GetByLabel('UI/Corporations/Wars/WarDeclareSummaryFightingStartsNow'))
                textsToAdd.append(startTuple)
            else:
                startTimeStamp = gametime.GetWallclockTime() + const.DAY
                startTuple = (GetByLabel('UI/Corporations/Wars/WarDeclareSummaryStartTime'), FmtDate(startTimeStamp))
                textsToAdd.append(startTuple)
            warHQ = self.warDeclareController.GetWarHQ()
            hqStructureInfo = sm.GetService('structureDirectory').GetStructureInfo(warHQ)
            hqLink = GetShowInfoLink(hqStructureInfo.typeID, hqStructureInfo.itemName, warHQ)
            hqTuple = (GetByLabel('UI/Corporations/Wars/WarDeclareSummaryWarHq'), hqLink)
            textsToAdd.append(hqTuple)
            costTuple = (GetByLabel('UI/Corporations/Wars/WarDeclareSummaryCost'), FmtISK(warConst.COST_OF_WAR, 0))
            textsToAdd.append(costTuple)
        for column1, column2 in textsToAdd:
            if column1 is None and column2 is None:
                Container(parent=textCont, align=uiconst.TOTOP, padding=(6, 6, 20, 0))
                continue
            cont = Container(parent=textCont, align=uiconst.TOTOP, padding=(6, 6, 6, 0))
            rightLabel = EveLabelMedium(text=column2, parent=cont, left=4, state=uiconst.UI_NORMAL, align=uiconst.TORIGHT, maxLines=1)
            cont.height = rightLabel.textheight
            restCont = Container(name='restCont', parent=cont, padRight=6)
            EveLabelMedium(text=column1, parent=restCont, left=4, state=uiconst.UI_NORMAL, align=uiconst.TOTOP, autoFadeSides=35, maxLines=1)

    def ShowInfo(self, itemID, typeID, *args):
        sm.GetService('info').ShowInfo(typeID, itemID)

    def WouldWarStartImmediately(self):
        wars = sm.GetService('war').GetWars(self.warDeclareController.GetAttackerID())
        defenderID = self.warDeclareController.GetDefenderID()
        for eachWar in wars.itervalues():
            if defenderID not in (eachWar.declaredByID, eachWar.againstID):
                continue
            if eachWar.timeFinished:
                return True

        return False


def ConstructNoResultsContainer(parent):
    if not getattr(parent, 'noResultsContainer', None) or parent.noResultsContainer.destroyed:
        noResultsContainer = Container(name='noResultsContainer', parent=parent, align=uiconst.TOALL)
        parent.noResultsContainer = noResultsContainer
        cont = ContainerAutoSize(name='cont', parent=noResultsContainer, align=uiconst.TOTOP)
        FillThemeColored(bgParent=cont, align=uiconst.TOALL, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.1)
        parent.noResultsLabel = EveLabelMediumBold(name='noResultsLabel', parent=cont, align=uiconst.TOTOP, text='', autoFitToText=True, padding=(0, 15, 0, 15))


class UserSelect(User):

    def Startup(self, *args):
        User.Startup(self, args)
        self.extraIcon = Sprite(name='extraIcon', parent=self, align=uiconst.CENTERRIGHT, pos=(20, 0, 16, 16))

    def Load(self, args):
        User.Load(self, args)
        data = self.sr.node
        hasWarPermit = data.hasWarPermit
        alreadyAtWar = data.alreadyAtWar
        inAlliance = data.inAlliance
        hasPeaceTreaty = data.hasPeaceTreaty
        isDisabledEntry = data.isDisabledEntry
        self.extraIcon.display = False
        if isDisabledEntry:
            self.opacity = 0.25
        else:
            self.opacity = 1.0
        hasExtraIcon = isDisabledEntry and (not hasWarPermit or alreadyAtWar or inAlliance or hasPeaceTreaty)
        if hasExtraIcon:
            if inAlliance:
                self.extraIcon.LoadTexture(texturePath=ALLIANCE_LOGO)
                hintText = GetByLabel('UI/Corporations/Wars/WarDeclareInAlliance', corpAllianceName=data.info.name)
            elif hasPeaceTreaty:
                self.extraIcon.LoadTexture(texturePath=NO_WAR_PERMIT_TEXTURE_PATH)
                hintText = GetByLabel('UI/Corporations/Wars/WarDeclareCorpOrAllianceHasForcedPeace', corpAllianceName=data.info.name)
            elif not hasWarPermit:
                self.extraIcon.LoadTexture(texturePath=NO_WAR_PERMIT_TEXTURE_PATH)
                hintText = GetByLabel('UI/Corporations/Wars/WarDeclareCorpOrAllianceDoesNotHaveWarPermit', corpAllianceName=data.info.name)
            elif alreadyAtWar:
                self.extraIcon.LoadTexture(texturePath=AT_WAR_TEXTURE_PATH)
                hintText = GetByLabel('UI/Corporations/Wars/WarDeclareAlreadyAtWar', corpAllianceName=data.info.name)
            self.extraIcon.opacity = 4.0
            self.extraIcon.hint = hintText
            self.extraIcon.display = True

    def GetMenu(self):
        if self.destroyed:
            return
        node = self.sr.node
        return GetMenuService().GetMenuFromItemIDTypeID(node.itemID, node.info.typeID)
