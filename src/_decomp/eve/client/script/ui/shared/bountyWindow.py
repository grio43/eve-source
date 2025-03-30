#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\bountyWindow.py
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control import eveIcon, eveLabel, eveScroll
from eve.client.script.ui.control.allUserEntries import AllUserEntries
from carbonui.button.group import ButtonGroup
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.control.expandablemenu import ExpandableMenuContainer
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.util import searchUtil
from eve.common.lib import appConst as const
from eve.common.script.search.const import ResultType
from eve.common.script.sys import idCheckers
from eve.common.script.sys.idCheckers import IsNPC
from eve.common.script.util import bountyUtil, eveFormat
import carbonui.const as uiconst
import localization
import uthread
import log
import blue
from math import pi
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
from globalConfig.getFunctions import CheckPlayerBountyEnabled
SHOW_CHAR = 1
SHOW_CORP = 2
SHOW_ALLIANCE = 3

class BountyWindow(Window):
    __guid__ = 'form.BountyWindow'
    __notifyevents__ = ['OnBountyPlaced']
    default_width = 400
    default_height = 510
    default_minSize = (default_width, default_height)
    default_windowID = 'bounties'
    default_captionLabelPath = 'UI/Station/BountyOffice/BountyOffice'
    default_descriptionLabelPath = 'Tooltips/StationServices/BountyOffice_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/bountyoffice.png'

    def ApplyAttributes(self, attributes):
        CheckPlayerBountyEnabled(sm.GetService('machoNet'))
        Window.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.ownerID = None
        self.searchedForOwnerID = None
        self.topBountyInited = False
        self.bountyHuntersInited = False
        self.myBountiesInited = False
        self.myBountiesUpdated = False
        self.searchingTopBounty = False
        self.searchingPlaceBounty = False
        self.selectedMenu = None
        self.bountySvc = sm.GetService('bountySvc')
        mainCont = Container(name='mainCont', parent=self.sr.main, padding=const.defaultPadding)
        placeBountiesCont = ContainerAutoSize(name='placeBounties', parent=mainCont, align=uiconst.TOBOTTOM, padTop=16)
        eveLabel.EveCaptionMedium(text=localization.GetByLabel('UI/Station/BountyOffice/PlaceBounty'), parent=placeBountiesCont, align=uiconst.TOTOP)
        self.searchCont = Container(name='searchCont', parent=placeBountiesCont, align=uiconst.TOTOP, height=32, padTop=4)
        self.verifiedCont = ContainerAutoSize(name='verifiedCont', parent=placeBountiesCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=32)
        self.verifiedCont.display = False
        placeCont = Container(name='placeCont', parent=placeBountiesCont, align=uiconst.TOTOP, height=32, padTop=4)
        imgCont = Container(name='imgCont', parent=self.searchCont, width=30, align=uiconst.TOLEFT)
        Sprite(name='killerLogo', parent=imgCont, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/silhouette_64.png', pos=(0, 0, 32, 32))
        self.searchEdit = SingleLineEditText(name='searchEdit', parent=self.searchCont, maxLength=32, align=uiconst.TOALL, hintText=localization.GetByLabel('UI/Station/BountyOffice/SearchForUser'), pos=(0, 0, 0, 0), padLeft=4)
        self.searchEdit.OnReturn = self.SearchPlaceBounty
        self.searchEdit.OnDropData = self.PlaceDropData
        self.imgCont = Container(name='imgCont', parent=self.verifiedCont, width=32, align=uiconst.TOLEFT)
        clearCont = Container(name='clearCont', parent=self.verifiedCont, width=24, align=uiconst.TORIGHT)
        textCont = ContainerAutoSize(name='textCont', parent=self.verifiedCont, align=uiconst.TOTOP, padLeft=4)
        self.bountyOwner = Sprite(parent=self.imgCont, align=uiconst.CENTERLEFT, idx=0, texturePath='res:/UI/Texture/silhouette_64.png', pos=(0, 0, 32, 32))
        self.clearBtn = ButtonIcon(name='surrenderBtn', parent=clearCont, align=uiconst.CENTER, width=16, iconSize=16, texturePath='res:/UI/Texture/Icons/73_16_210.png', hint=localization.GetByLabel('UI/Inventory/Clear'), func=self.ClearBounty)
        self.nameLabel = eveLabel.EveLabelMedium(name='bountyName', parent=textCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, maxLines=1)
        self.bountyLabel = eveLabel.EveLabelSmall(name='bountyAmount', parent=textCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.placeBountiesBtn = Button(parent=placeCont, label=localization.GetByLabel('UI/Station/BountyOffice/Place'), align=uiconst.TORIGHT, func=self.PlaceBounty)
        self.placeBountiesBtn.Disable()
        self.bountyAmount = SingleLineEditInteger(name='placeEdit', parent=placeCont, align=uiconst.TOALL, width=0, maxValue=const.MAX_BOUNTY_AMOUNT, hintText=localization.GetByLabel('UI/Station/BountyOffice/EnterAmount'), padRight=const.defaultPadding, top=0, dataType=long)
        self.bountyAmount.OnReturn = self.PlaceBounty
        expandableCont = Container(name='expandableCont', parent=mainCont, align=uiconst.TOALL)
        self.bountiesCont = Container(name='bountiesCont', padTop=2)
        self.searchOnListEdit = QuickFilterEdit(name='searchOnListEdit', parent=self.bountiesCont, maxLength=32, align=uiconst.TOTOP, hintText=localization.GetByLabel('UI/Station/BountyOffice/SearchForUser'), height=32, padTop=2, OnClearFilter=self.ClearSearch, isCharCorpOrAllianceField=True)
        self.searchOnListEdit.ReloadFunction = self.OnSearchFieldChanged
        self.searchOnListEdit.OnReturn = self.SearchTopBounty
        self.topBountiesButtons = ToggleButtonGroup(parent=self.bountiesCont, align=uiconst.TOTOP, callback=self.OnButtonSelected, padTop=4)
        for btnID, label in self.GetMenuTabs():
            self.topBountiesButtons.AddButton(btnID, label, self.bountiesCont)

        self.topBountiesButtons.SelectByID(settings.user.ui.Get('topBountiesType', SHOW_CHAR))
        self.topBountiesScroll = ScrollContainer(name='topBountiesScroll', parent=self.bountiesCont, align=uiconst.TOALL, padTop=4)
        self.bountyHuntersCont = Container(name='bountyHuntersCont', padTop=2)
        self.bountyHunterButtons = ToggleButtonGroup(parent=self.bountyHuntersCont, align=uiconst.TOTOP, callback=self.OnButtonSelected, padTop=4)
        for btnID, label in self.GetMenuTabs():
            self.bountyHunterButtons.AddButton(btnID, label, self.bountyHuntersCont)

        self.bountyHunterButtons.SelectByID(settings.user.ui.Get('bountyHuntersType', SHOW_CHAR))
        self.bountyHuntersScroll = ScrollContainer(name='bountyHuntersScroll', parent=self.bountyHuntersCont, align=uiconst.TOALL, padTop=4)
        self.myBountiesCont = Container(name='myBountiesCont', padTop=2)
        self.myBountiesScroll = ScrollContainer(name='myBountiesScroll', parent=self.myBountiesCont, align=uiconst.TOALL, padTop=4)
        self.noBountiesPlaced = Container(name='loadingCont', parent=self.myBountiesCont, align=uiconst.TOALL)
        eveLabel.EveCaptionMedium(text=localization.GetByLabel('UI/Station/BountyOffice/NoOutstandingBounties'), parent=self.noBountiesPlaced, align=uiconst.CENTER)
        self.em = ExpandableMenuContainer(parent=expandableCont, clipChildren=True)
        self.em.multipleExpanded = False
        emTabs = self.GetEMTabs()
        self.em.Load(emTabs, 'bounties')

    def ConstructTopParent(self):
        topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=52, clipChildren=True)
        SpriteThemeColored(name='mainicon', parent=topParent, state=uiconst.UI_DISABLED, pos=(0, -8, 64, 64), texturePath=self.iconNum, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        self.label = eveLabel.WndCaptionLabel(text=localization.GetByLabel('UI/Station/BountyOffice/BountyOffice'), parent=topParent)

    def LoadTopBounties(self, initialLoad = False):
        self.selectedMenu = 'topBounties'
        if self.topBountyInited:
            return
        showType = settings.user.ui.Get('topBountiesType', SHOW_CHAR)
        self.DrawTopBounties(showType)
        self.topBountyInited = True

    def LoadBountyHunters(self, initialLoad = False):
        self.selectedMenu = 'topBountyHunters'
        if self.bountyHuntersInited:
            return
        showType = settings.user.ui.Get('bountyHuntersType', SHOW_CHAR)
        self.DrawBountyHunters(showType)
        self.bountyHuntersInited = True

    def LoadMyBounties(self, initialLoad = False):
        if self.myBountiesInited and not self.myBountiesUpdated:
            return
        self.DrawMyBounties()
        self.myBountiesInited = True
        self.myBountiesUpdated = False

    def GetEMTabs(self):
        tabs = [(localization.GetByLabel('UI/Station/BountyOffice/MostWanted'),
          self.bountiesCont,
          self.LoadTopBounties,
          None,
          None,
          None,
          False,
          True), (localization.GetByLabel('UI/Station/BountyOffice/TopBountyHunters'),
          self.bountyHuntersCont,
          self.LoadBountyHunters,
          None,
          None,
          None,
          False,
          False), (localization.GetByLabel('UI/Station/BountyOffice/MyBounties'),
          self.myBountiesCont,
          self.LoadMyBounties,
          None,
          None,
          None,
          False,
          False)]
        return tabs

    def GetMenuTabs(self):
        return ((SHOW_CHAR, localization.GetByLabel('UI/Station/BountyOffice/ShowCharacters')), (SHOW_CORP, localization.GetByLabel('UI/Station/BountyOffice/ShowCorporations')), (SHOW_ALLIANCE, localization.GetByLabel('UI/Station/BountyOffice/ShowAlliances')))

    def OnButtonSelected(self, mode, *args):
        if self.selectedMenu == 'topBounties':
            if mode != settings.user.ui.Get('topBountiesType', SHOW_CHAR):
                self.DrawTopBounties(mode)
                settings.user.ui.Set('topBountiesType', mode)
        elif self.selectedMenu == 'topBountyHunters':
            if mode != settings.user.ui.Get('bountyHuntersType', SHOW_CHAR):
                self.DrawBountyHunters(mode)
                settings.user.ui.Set('bountyHuntersType', mode)

    def SearchTopBounty(self, *args):
        if self.searchOnListEdit.GetValue() == '':
            return
        if self.searchingTopBounty:
            return
        self.searchingTopBounty = True
        try:
            ownerID = self.Search(self.searchOnListEdit)
        finally:
            self.searchingTopBounty = False

        if self.searchedForOwnerID and self.searchedForOwnerID == ownerID:
            return
        if ownerID:
            self.searchedForOwnerID = ownerID
            ownerName = cfg.eveowners.Get(ownerID).name
            self.searchOnListEdit.SetValue(ownerName)
            if self.ShowSearched(ownerID):
                self.ScrollToActiveEntry()

    def ScrollToActiveEntry(self):
        uthread.new(self._ScrollToActiveEntry)

    def _ScrollToActiveEntry(self):
        blue.synchro.Yield()
        entry = self.treeEntryByID.get(self.rank, None)
        if not entry:
            return
        _, topEntry = entry.GetAbsolutePosition()
        _, topScroll, _, height = self.topBountiesScroll.mainCont.GetAbsolute()
        denum = height - entry.height
        if denum:
            fraction = float(topEntry - topScroll) / denum
            self.topBountiesScroll.ScrollToVertical(fraction)

    def OnSearchFieldChanged(self, *args):
        if self.searchOnListEdit.GetValue().strip() == '':
            showType = settings.user.ui.Get('topBountiesType', SHOW_CHAR)
            self.DrawTopBounties(showType)

    def PlaceDropData(self, dragObj, nodes):
        for node in nodes:
            if hasattr(node, 'Get'):
                if node.Get('__guid__', None) not in AllUserEntries():
                    return
                ownerID = node.charID
                if ownerID:
                    if idCheckers.IsCharacter(ownerID) or idCheckers.IsCorporation(ownerID) or idCheckers.IsAlliance(ownerID):
                        self.ownerID = ownerID
                        self.ShowResult(ownerID)
                break

    def ClearSearch(self, *args):
        self.searchedForOwnerID = None
        self.searchOnListEdit.SetValue('')
        showType = settings.user.ui.Get('topBountiesType', SHOW_CHAR)
        self.DrawTopBounties(showType)
        self.topBountiesScroll.ScrollToVertical(0.0)

    def SearchPlaceBounty(self, *args):
        if self.searchEdit.GetValue() == '':
            return
        if self.searchingPlaceBounty:
            return
        if self.verifiedCont.display == True:
            return
        self.searchingPlaceBounty = True
        try:
            self.ownerID = self.Search(self.searchEdit)
        finally:
            self.searchingPlaceBounty = False

        if self.ownerID:
            self.ShowResult(self.ownerID)

    def Search(self, edit):
        searchString = edit.GetValue()
        if not searchString or searchString == '':
            return None
        groupIDList = [ResultType.character, ResultType.corporation, ResultType.alliance]
        searchResult = searchUtil.GetResultsList(searchString.strip(), groupIDList, hideNPC=True)
        searchResult = [ x for x in searchResult if not IsNPC(x) ]
        if not len(searchResult):
            edit.SetValue('')
            edit.SetHintText(localization.GetByLabel('UI/Station/BountyOffice/NoOneFound'))
        else:
            if len(searchResult) == 1:
                ownerID = searchResult[0]
                return ownerID
            dlg = BountyPicker.Open(resultList=searchResult)
            dlg.ShowModal()
            if dlg.ownerID:
                return dlg.ownerID
            edit.SetValue('')
            return None

    def ShowSearched(self, ownerID):
        self.topBountiesScroll.Flush()
        self.treeEntryByID = {}
        try:
            searchedBounties = self.bountySvc.SearchBounties(ownerID)
        except:
            self.searchOnListEdit.SetValue('')
            entityName = cfg.eveowners.Get(ownerID).name
            self.searchOnListEdit.SetHintText(localization.GetByLabel('UI/Station/BountyOffice/SearchedForHasNoBounty', entityName=entityName))
            return False

        ownersToPrime = set()
        for rank, bounty in searchedBounties:
            ownersToPrime.add(bounty.targetID)
            if hasattr(bounty, 'corporationID'):
                ownersToPrime.add(bounty.corporationID)
            if hasattr(bounty, 'allianceID'):
                ownersToPrime.add(bounty.allianceID)

        cfg.eveowners.Prime(ownersToPrime)
        if idCheckers.IsCharacter(ownerID):
            contType = CharBounty
        else:
            contType = CorpBounty
        for rank, bounty in searchedBounties:
            focus = False
            corpID = getattr(bounty, 'corporationID', None)
            allianceID = getattr(bounty, 'allianceID', None)
            rowNumber = rank + 1
            bountyAmount = self.bountySvc.GetBountyFromCache(bounty.targetID)
            if bounty.targetID == self.searchedForOwnerID:
                focus = True
                self.rank = rank
            cont = contType(name='topBounty', parent=self.topBountiesScroll, ownerID=bounty.targetID, bounty=bountyAmount, corpID=corpID, allianceID=allianceID, place=rowNumber, focus=focus)
            self.treeEntryByID[rank] = cont

        return True

    def ShowResult(self, ownerID):
        if ownerID and not IsNPC(ownerID):
            self.imgCont.Flush()
            bountyAmount = self.GetBountyAmount(ownerID)
            self.verifiedCont.display = True
            self.placeBountiesBtn.Enable()
            self.searchCont.display = False
            ownerType = cfg.eveowners.Get(ownerID).typeID
            if idCheckers.IsCharacter(ownerID):
                ownerPortrait = Sprite(parent=self.imgCont, align=uiconst.CENTERLEFT, idx=0, texturePath='res:/UI/Texture/silhouette_64.png', pos=(0, 0, 32, 32))
                sm.GetService('photo').GetPortrait(ownerID, 30, ownerPortrait)
            else:
                ownerPortrait = eveIcon.GetLogoIcon(itemID=ownerID, parent=self.imgCont, acceptNone=False, align=uiconst.CENTERLEFT, height=32, width=32, state=uiconst.UI_NORMAL)
            ownerPortrait.OnClick = (self.ShowInfo, ownerID, ownerType)
            ownerName = cfg.eveowners.Get(ownerID).name
            self.bountyOwner.hint = ownerName
            self.nameLabel.text = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=ownerName, info=('showinfo', ownerType, ownerID))
            self.bountyLabel.text = localization.GetByLabel('UI/Common/BountyAmount', bountyAmount=eveFormat.FmtISK(bountyAmount, False))
            minBounty = bountyUtil.GetMinimumBountyAmount(ownerID)
            self.bountyAmount.SetHintText(localization.GetByLabel('UI/Station/BountyOffice/InsertAmount', bountyAmount=eveFormat.FmtISK(minBounty)))
            uicore.registry.SetFocus(self.bountyAmount)
            self.SetBountyHint(ownerID)

    def SetBountyHint(self, ownerID):
        bountyOwnerIDs = self.GetEntities(ownerID)
        bountyAmounts = self.GetBountyAmounts(*bountyOwnerIDs)
        charBounty = 0
        corpBounty = 0
        allianceBounty = 0
        if len(bountyAmounts):
            for ownerID, value in bountyAmounts.iteritems():
                if idCheckers.IsCharacter(ownerID):
                    charBounty = value
                elif idCheckers.IsCorporation(ownerID):
                    corpBounty = value
                elif idCheckers.IsAlliance(ownerID):
                    allianceBounty = value

        bountyHint = localization.GetByLabel('UI/Station/BountyOffice/BountyHint', charBounty=eveFormat.FmtISK(charBounty, 0), corpBounty=eveFormat.FmtISK(corpBounty, 0), allianceBounty=eveFormat.FmtISK(allianceBounty, 0))
        self.bountyLabel.hint = bountyHint

    def GetBountyAmounts(self, *ownerIDs):
        bountyAmounts = sm.GetService('bountySvc').GetBounties(*ownerIDs)
        return bountyAmounts

    def OnBountyPlaced(self, ownerID):
        self.myBountiesUpdated = True
        self.LoadMyBounties()
        if ownerID == self.ownerID and self.verifiedCont.display == True:
            bountyAmount = self.GetBountyAmount(ownerID)
            self.bountyLabel.text = localization.GetByLabel('UI/Common/BountyAmount', bountyAmount=eveFormat.FmtISK(bountyAmount, False))

    def GetEntities(self, ownerID):
        charID = None
        corpID = None
        allianceID = None
        if idCheckers.IsCharacter(ownerID):
            corpInfo = sm.GetService('corp').GetInfoWindowDataForChar(ownerID)
            charID = ownerID
            corpID = corpInfo.corpID
            allianceID = corpInfo.allianceID
        elif idCheckers.IsCorporation(ownerID):
            corpInfo = sm.RemoteSvc('corpmgr').GetPublicInfo(ownerID)
            corpID = ownerID
            allianceID = corpInfo.allianceID
        else:
            allianceID = ownerID
        bountyInfo = (charID, corpID, allianceID)
        return bountyInfo

    def GetBountyAmount(self, ownerID):
        bountyInfo = self.GetEntities(ownerID)
        bountyAmount = self.bountySvc.GetBounty(*bountyInfo)
        return bountyAmount

    def ClearBounty(self, *args):
        self.ownerID = None
        self.searchEdit.SetValue('')
        self.searchCont.display = True
        self.verifiedCont.display = False
        self.bountyAmount.SetHintText(localization.GetByLabel('UI/Station/BountyOffice/EnterAmount'))
        self.placeBountiesBtn.Disable()

    def PlaceBounty(self, *args):
        if self.placeBountiesBtn.disabled:
            return
        if not self.ownerID:
            return
        ownerID = self.ownerID
        amount = self.bountyAmount.GetValue()
        minBounty = bountyUtil.GetMinimumBountyAmount(ownerID)
        if amount < minBounty:
            self.bountyAmount.SetValue('')
            self.bountyAmount.SetHintText(localization.GetByLabel('UI/Station/BountyOffice/TooLowEnterMore', minAmount=eveFormat.FmtISK(minBounty)))
            return
        if ownerID and amount:
            self.bountySvc.AddToBounty(ownerID, amount)
            self.searchEdit.SetValue('')
            self.bountyAmount.SetValue('')
            bountyAmount = self.GetBountyAmount(ownerID)
            self.bountyLabel.text = localization.GetByLabel('UI/Common/BountyAmount', bountyAmount=eveFormat.FmtISK(bountyAmount))
            sm.GetService('objectCaching').InvalidateCachedMethodCall('charMgr', 'GetPublicInfo3', ownerID)
            sm.ScatterEvent('OnBountyPlaced', ownerID)

    def ShowInfo(self, ownerID, typeID, *args):
        sm.GetService('info').ShowInfo(typeID, ownerID)

    def DrawTopBounties(self, showType):
        uthread.new(self.DrawTopBounties_thread, showType)

    def DrawTopBounties_thread(self, showType):
        self.topBountiesScroll.Flush()
        topBounties = self.GetTopBounties(showType)
        if showType == SHOW_CHAR:
            topContType = TopCharBounty
            contType = CharBounty
        else:
            topContType = TopCorpBounty
            contType = CorpBounty
        ownersToPrime = set()
        for b in topBounties:
            ownersToPrime.add(b.targetID)
            if hasattr(b, 'corporationID'):
                ownersToPrime.add(b.corporationID)
            if hasattr(b, 'allianceID'):
                ownersToPrime.add(b.allianceID)

        cfg.eveowners.Prime(ownersToPrime)
        for rowNumber, bounty in enumerate(topBounties):
            corpID = getattr(bounty, 'corporationID', None)
            allianceID = getattr(bounty, 'allianceID', None)
            bountyAmount = self.bountySvc.GetBountyFromCache(bounty.targetID)
            if rowNumber == 10:
                return
            if rowNumber == 0:
                topContType(name='topBounty', parent=self.topBountiesScroll, ownerID=bounty.targetID, bounty=bountyAmount, corpID=corpID, allianceID=allianceID)
            else:
                contType(name='bounty', parent=self.topBountiesScroll, ownerID=bounty.targetID, bounty=bountyAmount, corpID=corpID, allianceID=allianceID, place=rowNumber + 1)

    def GetTopBounties(self, showType):
        if showType == SHOW_CHAR:
            topBounties = self.bountySvc.GetTopPilotBounties(0)
        elif showType == SHOW_CORP:
            topBounties = self.bountySvc.GetTopCorpBounties(0)
        else:
            topBounties = self.bountySvc.GetTopAllianceBounties(0)
        return topBounties

    def DrawBountyHunters(self, showType):
        uthread.new(self.DrawBountyHunters_thread, showType)

    def DrawBountyHunters_thread(self, showType):
        self.bountyHuntersScroll.Flush()
        bountyHunters = self.GetTopBountyHunters(showType)
        if showType == SHOW_CHAR:
            topContType = TopCharBounty
            contType = CharBounty
        else:
            topContType = TopCorpBounty
            contType = CorpBounty
        ownersToPrime = set()
        for b in bountyHunters:
            ownersToPrime.add(b.bountyHunterID)
            if hasattr(b, 'corporationID'):
                ownersToPrime.add(b.corporationID)
            if hasattr(b, 'allianceID'):
                ownersToPrime.add(b.allianceID)

        cfg.eveowners.Prime(ownersToPrime)
        for bounty in bountyHunters:
            ownerID = bounty.bountyHunterID
            corpID = getattr(bounty, 'corporationID', None)
            allianceID = getattr(bounty, 'allianceID', None)
            rowNumber = getattr(bounty, 'rowNumber', 0)
            bountiesClaimed = getattr(bounty, 'bountiesClaimed', 0)
            numberOfKills = getattr(bounty, 'numberOfKills', 0)
            if bounty.rowNumber == 1:
                topContType(name='topBountyHunter', parent=self.bountyHuntersScroll, ownerID=ownerID, corpID=corpID, allianceID=allianceID, bountiesClaimed=bountiesClaimed, numberOfKills=numberOfKills)
            else:
                contType(name='bountyHunter', parent=self.bountyHuntersScroll, ownerID=ownerID, corpID=corpID, allianceID=allianceID, place=rowNumber, bountiesClaimed=bountiesClaimed, numberOfKills=numberOfKills)

    def GetTopBountyHunters(self, showType):
        if showType == SHOW_CHAR:
            bountyHunters = self.bountySvc.GetTopPilotBountyHunters(0)
        elif showType == SHOW_CORP:
            bountyHunters = self.bountySvc.GetTopCorporationBountyHunters(0)
        else:
            bountyHunters = self.bountySvc.GetTopAllianceBountyHunters(0)
        return bountyHunters

    def DrawMyBounties(self):
        uthread.new(self.DrawMyBounties_thread)

    def DrawMyBounties_thread(self):
        self.myBountiesScroll.Flush()
        myBounties = self.bountySvc.GetMyBounties()
        if not len(myBounties):
            self.noBountiesPlaced.display = True
            self.myBountiesScroll.display = False
        else:
            self.noBountiesPlaced.display = False
            self.myBountiesScroll.display = True
            ownersToPrime = set()
            for b in myBounties:
                ownersToPrime.add(b.targetID)
                if hasattr(b, 'corporationID'):
                    ownersToPrime.add(b.corporationID)
                if hasattr(b, 'allianceID'):
                    ownersToPrime.add(b.allianceID)

            cfg.eveowners.Prime(ownersToPrime)
            ownerIDs = set()
            for bounty in myBounties:
                ownerIDs.add(bounty.targetID)
                for entityID in ('corporationID', 'allianceID'):
                    ownerID = getattr(bounty, entityID, None)
                    if ownerID is not None:
                        ownerIDs.add(ownerID)

            sm.GetService('bountySvc').GetBounties(*ownerIDs)
            for bounty in sorted(myBounties, key=lambda x: x.contributionID, reverse=True):
                ownerID = bounty.targetID
                corpID = getattr(bounty, 'corporationID', None)
                allianceID = getattr(bounty, 'allianceID', None)
                myAmount = getattr(bounty, 'amount', 0)
                if idCheckers.IsCharacter(ownerID):
                    contType = CharBounty
                else:
                    contType = CorpBounty
                contType(name='myBounty', parent=self.myBountiesScroll, ownerID=ownerID, corpID=corpID, allianceID=allianceID, myAmount=myAmount)


class TopBountyContainer(Container):
    __notifyevents__ = ['OnBountyPlaced']
    default_height = 138
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.ownerID = attributes.get('ownerID', None)
        self.bounty = attributes.get('bounty', 0)
        self.corpID = attributes.get('corpID', None)
        self.allianceID = attributes.get('allianceID', session.allianceid)
        self.bountiesClaimed = attributes.get('bountiesClaimed', 0)
        self.numberOfKills = attributes.get('numberOfKills', 0)
        self.ConstructLayout()

    def ConstructLayout(self):
        ownerID = self.ownerID
        Container(name='bottomPadding', parent=self, align=uiconst.TOBOTTOM, height=10)
        mainCont = Container(name='mainCont', parent=self, align=uiconst.TOBOTTOM, height=128)
        Fill(bgParent=mainCont, color=(1.0, 1.0, 1.0, 0.075))
        self.imgCont = Container(name='myImgCont', parent=mainCont, align=uiconst.TOLEFT, width=128, state=uiconst.UI_NORMAL)
        self.placeBountyCont = Container(name='placeBountyCont', parent=mainCont, align=uiconst.TORIGHT, width=20, state=uiconst.UI_NORMAL)
        if idCheckers.IsAlliance(self.ownerID):
            bountyOwnerIDs = (self.ownerID, None, None)
        elif idCheckers.IsCorporation(self.ownerID):
            bountyOwnerIDs = (self.ownerID, None, self.allianceID)
        else:
            bountyOwnerIDs = (self.ownerID, self.corpID, self.allianceID)
        utilMenu = PlaceBountyUtilMenu(parent=self.placeBountyCont, ownerID=self.ownerID, bountyOwnerIDs=bountyOwnerIDs, align=uiconst.CENTER)
        self.placeBountyCont.width = utilMenu.width
        myTextCont = Container(name='textCont', parent=mainCont, align=uiconst.TOALL, padLeft=const.defaultPadding * 2, clipChildren=True)
        self.textCont = ContainerAutoSize(parent=myTextCont, name='textCont', align=uiconst.CENTERLEFT)
        self.nameLabel = eveLabel.EveCaptionSmall(text='', parent=self.textCont, maxLines=1, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        self.bountyLabel = eveLabel.EveCaptionSmall(text='', parent=self.textCont, maxLines=1, align=uiconst.TOPLEFT, top=26, state=uiconst.UI_NORMAL)
        ownerName = cfg.eveowners.Get(ownerID).name
        ownerType = self.ownerType = cfg.eveowners.Get(ownerID).typeID
        self.ownerLabel = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=ownerName, info=('showinfo', ownerType, ownerID))
        self.numberCont = ContainerAutoSize(parent=self.imgCont, name='numberCont', align=uiconst.TOPLEFT, idx=0)
        Fill(bgParent=self.numberCont, color=(0.0, 0.0, 0.0, 0.4))
        self.numberLabel = eveLabel.EveCaptionLarge(text='1', parent=self.numberCont, align=uiconst.TOPLEFT, idx=0, left=2, padRight=2)

    def DisplayBountyAmount(self):
        bountyAmount = self.bounty
        self.bountyLabel.text = localization.GetByLabel('UI/Common/BountyAmount', bountyAmount=eveFormat.FmtISK(bountyAmount, 0))
        Sprite(name='wanted', parent=self.imgCont, idx=0, texturePath='res:/UI/Texture/wanted.png', width=128, height=34, align=uiconst.CENTERBOTTOM, state=uiconst.UI_PICKCHILDREN, top=2)

    def OnBountyPlaced(self, ownerID):
        if ownerID == self.ownerID:
            if self.bounty > 0:
                bountyAmount = sm.GetService('bountySvc').GetBountyFromCache(ownerID)
                self.bountyLabel.text = localization.GetByLabel('UI/Common/BountyAmount', bountyAmount=eveFormat.FmtISK(bountyAmount, 0))

    def ShowInfo(self, itemID, typeID, *args):
        sm.GetService('info').ShowInfo(typeID, itemID)


class BountyContainer(Container):
    __notifyevents__ = ['OnBountyPlaced']
    default_height = 76
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.ownerID = attributes.get('ownerID', None)
        self.bounty = attributes.get('bounty', 0)
        self.myAmount = attributes.get('myAmount', 0)
        self.corpID = attributes.get('corpID', None)
        self.allianceID = attributes.get('allianceID', None)
        self.place = attributes.get('place', None)
        self.focus = attributes.get('focus', False)
        self.bountiesClaimed = attributes.get('bountiesClaimed', 0)
        self.numberOfKills = attributes.get('numberOfKills', 0)
        self.ConstructLayout()

    def ConstructLayout(self):
        ownerID = self.ownerID
        theCont = Container(name='theCont', parent=self)
        Container(name='mainCont', parent=theCont, align=uiconst.TOTOP, height=6)
        mainCont = Container(name='mainCont', parent=theCont, align=uiconst.TOTOP, height=64)
        self.imgCont = Container(name='myImgCont', parent=mainCont, align=uiconst.TOLEFT, width=64, state=uiconst.UI_NORMAL)
        if self.focus:
            Fill(bgParent=mainCont, color=(1.0, 1.0, 1.0, 0.075))
        self.placeBountyCont = Container(name='placeBountyCont', parent=mainCont, align=uiconst.TORIGHT, width=20, state=uiconst.UI_NORMAL)
        if idCheckers.IsAlliance(self.ownerID):
            bountyOwnerIDs = (self.ownerID, None, None)
        elif idCheckers.IsCorporation(self.ownerID):
            bountyOwnerIDs = (self.ownerID, None, self.allianceID)
        else:
            bountyOwnerIDs = (self.ownerID, self.corpID, self.allianceID)
        utilMenu = PlaceBountyUtilMenu(parent=self.placeBountyCont, ownerID=self.ownerID, bountyOwnerIDs=bountyOwnerIDs, align=uiconst.CENTER)
        self.placeBountyCont.width = utilMenu.width
        myTextCont = Container(name='textCont', parent=mainCont, align=uiconst.TOALL, padLeft=const.defaultPadding, clipChildren=True)
        self.textCont = ContainerAutoSize(parent=myTextCont, name='textCont', align=uiconst.CENTERLEFT)
        self.nameLabel = eveLabel.EveLabelMedium(text='', parent=self.textCont, maxLines=1, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        self.bountyLabel = eveLabel.EveLabelMediumBold(text='', parent=self.textCont, maxLines=1, align=uiconst.TOPLEFT, top=16, state=uiconst.UI_NORMAL)
        ownerName = cfg.eveowners.Get(ownerID).name
        ownerType = self.ownerType = cfg.eveowners.Get(ownerID).typeID
        self.ownerLabel = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=ownerName, info=('showinfo', ownerType, ownerID))
        self.numberCont = ContainerAutoSize(parent=self.imgCont, name='numberCont', align=uiconst.TOPLEFT, idx=0)
        Fill(bgParent=self.numberCont, color=(0.0, 0.0, 0.0, 0.4))
        self.numberLabel = eveLabel.EveLabelMediumBold(text=self.place, parent=self.numberCont, align=uiconst.TOPLEFT, idx=0, left=2, padRight=2)

    def DisplayMyAmount(self):
        myAmount = self.myAmount
        self.bountyLabel.text = localization.GetByLabel('UI/Station/BountyOffice/MyContribution', bountyAmount=eveFormat.FmtISK(myAmount, 0))
        if idCheckers.IsAlliance(self.ownerID):
            bountyOwnerIDs = (self.ownerID, None, None)
        elif idCheckers.IsCorporation(self.ownerID):
            bountyOwnerIDs = (self.ownerID, None, self.allianceID)
        else:
            bountyOwnerIDs = (self.ownerID, self.corpID, self.allianceID)
        bountyAmount = sm.GetService('bountySvc').GetBounty(*bountyOwnerIDs)
        self.bountyLabel.hint = localization.GetByLabel('UI/Common/BountyAmount', bountyAmount=eveFormat.FmtISK(bountyAmount, 0))
        Sprite(name='wanted', parent=self.imgCont, idx=0, texturePath='res:/UI/Texture/wanted.png', width=64, height=17, align=uiconst.CENTERBOTTOM, state=uiconst.UI_PICKCHILDREN, top=1)

    def DisplayBountyAmount(self):
        bountyAmount = self.bounty
        self.bountyLabel.text = localization.GetByLabel('UI/Common/BountyAmount', bountyAmount=eveFormat.FmtISK(bountyAmount, 0))
        Sprite(name='wanted', parent=self.imgCont, idx=0, texturePath='res:/UI/Texture/wanted.png', width=64, height=17, align=uiconst.CENTERBOTTOM, state=uiconst.UI_PICKCHILDREN, top=1)

    def OnBountyPlaced(self, ownerID):
        if ownerID == self.ownerID:
            if self.bounty > 0:
                bountyAmount = sm.GetService('bountySvc').GetBountyFromCache(ownerID)
                self.bountyLabel.text = localization.GetByLabel('UI/Common/BountyAmount', bountyAmount=eveFormat.FmtISK(bountyAmount, 0))

    def ShowInfo(self, itemID, typeID, *args):
        sm.GetService('info').ShowInfo(typeID, itemID)


class TopCharBounty(TopBountyContainer):

    def ApplyAttributes(self, attributes):
        TopBountyContainer.ApplyAttributes(self, attributes)

    def ConstructLayout(self):
        TopBountyContainer.ConstructLayout(self)
        self.corpLabel = eveLabel.EveLabelMedium(text='', parent=self.textCont, maxLines=1, align=uiconst.TOPLEFT, top=26, state=uiconst.UI_NORMAL)
        self.bountyLabel.top = 44
        self.LoadInfo()

    def LoadInfo(self):
        ownerID = self.ownerID
        corpID = self.corpID
        allianceID = self.allianceID
        ownerType = self.ownerType
        self.nameLabel.text = self.ownerLabel
        ownerLogo = Sprite(parent=self.imgCont, align=uiconst.TOALL, size=128, idx=0, texturePath='res:/UI/Texture/silhouette.png')
        sm.GetService('photo').GetPortrait(ownerID, 128, ownerLogo)
        ownerLogo.OnClick = (self.ShowInfo, ownerID, ownerType)
        ownerLogo.hint = cfg.eveowners.Get(ownerID).name
        if corpID:
            corpText = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(corpID).name, info=('showinfo', const.typeCorporation, corpID))
        if allianceID:
            ticker = cfg.allianceshortnames.Get(allianceID).shortName
            allianceText = ' [%s]' % localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=ticker, info=('showinfo', const.typeAlliance, allianceID))
            corpText += allianceText
        self.corpLabel.text = corpText
        self.nameLabel.text = self.ownerLabel
        if self.bounty > 0:
            self.DisplayBountyAmount()
        elif self.bountiesClaimed > 0:
            self.DisplayISKDestroyed()
        self.numberCont.SetOrder(0)

    def DisplayISKDestroyed(self):
        killAmount = eveFormat.FmtISK(self.bountiesClaimed, 0)
        self.bountyLabel.text = localization.GetByLabel('UI/Station/BountyOffice/BountyClaimed', kills=self.numberOfKills, iskAmount=killAmount)


class CharBounty(BountyContainer):

    def ApplyAttributes(self, attributes):
        BountyContainer.ApplyAttributes(self, attributes)

    def ConstructLayout(self):
        BountyContainer.ConstructLayout(self)
        self.corpLabel = eveLabel.EveLabelSmall(text='', parent=self.textCont, maxLines=1, align=uiconst.TOPLEFT, top=16, state=uiconst.UI_NORMAL)
        self.bountyLabel.top = 30
        self.LoadInfo()

    def LoadInfo(self):
        ownerID = self.ownerID
        corpID = self.corpID
        allianceID = self.allianceID
        ownerType = self.ownerType
        self.nameLabel.text = self.ownerLabel
        ownerLogo = Sprite(parent=self.imgCont, align=uiconst.TOALL, size=64, idx=0, texturePath='res:/UI/Texture/silhouette_64.png')
        sm.GetService('photo').GetPortrait(ownerID, 64, ownerLogo)
        ownerLogo.OnClick = (self.ShowInfo, ownerID, ownerType)
        ownerLogo.hint = cfg.eveowners.Get(ownerID).name
        if corpID:
            corpText = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(corpID).name, info=('showinfo', const.typeCorporation, corpID))
        if allianceID:
            ticker = cfg.allianceshortnames.Get(allianceID).shortName
            allianceText = ' [%s]' % localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=ticker, info=('showinfo', const.typeAlliance, allianceID))
            corpText += allianceText
        self.corpLabel.text = corpText
        self.nameLabel.text = self.ownerLabel
        if self.bounty > 0:
            self.DisplayBountyAmount()
        elif self.bountiesClaimed > 0:
            self.DisplayISKDestroyed()
        elif self.myAmount > 0:
            self.DisplayMyAmount()
        self.numberCont.SetOrder(0)

    def DisplayISKDestroyed(self):
        killAmount = eveFormat.FmtISK(self.bountiesClaimed, 0)
        self.bountyLabel.text = localization.GetByLabel('UI/Station/BountyOffice/BountyClaimed', kills=self.numberOfKills, iskAmount=killAmount)


class TopCorpBounty(TopBountyContainer):

    def ApplyAttributes(self, attributes):
        TopBountyContainer.ApplyAttributes(self, attributes)

    def ConstructLayout(self):
        TopBountyContainer.ConstructLayout(self)
        self.LoadInfo()

    def LoadInfo(self):
        ownerID = self.ownerID
        corpID = self.corpID
        allianceID = self.allianceID
        ownerType = self.ownerType
        ownerLogo = eveIcon.GetLogoIcon(ownerID, parent=self.imgCont, acceptNone=False, align=uiconst.TOPRIGHT, height=128, width=128, state=uiconst.UI_NORMAL)
        if idCheckers.IsCorporation(ownerID):
            if allianceID:
                ticker = cfg.allianceshortnames.Get(allianceID).shortName
                allianceText = ' [%s]' % localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=ticker, info=('showinfo', const.typeAlliance, allianceID))
                self.ownerLabel += allianceText
        ownerLogo.OnClick = (self.ShowInfo, ownerID, ownerType)
        ownerLogo.SetSize(128, 128)
        self.nameLabel.text = self.ownerLabel
        if self.bounty > 0:
            self.DisplayBountyAmount()
        elif self.bountiesClaimed > 0:
            self.DisplayISKDestroyed()

    def DisplayISKDestroyed(self):
        killAmount = eveFormat.FmtISK(self.bountiesClaimed, 0)
        self.bountyLabel.text = localization.GetByLabel('UI/Station/BountyOffice/BountyClaimedCorps', iskAmount=killAmount)


class CorpBounty(BountyContainer):

    def ApplyAttributes(self, attributes):
        BountyContainer.ApplyAttributes(self, attributes)

    def ConstructLayout(self):
        BountyContainer.ConstructLayout(self)
        self.LoadInfo()

    def LoadInfo(self):
        ownerID = self.ownerID
        corpID = self.corpID
        allianceID = self.allianceID
        ownerType = self.ownerType
        ownerLogo = eveIcon.GetLogoIcon(ownerID, parent=self.imgCont, acceptNone=False, align=uiconst.TOPRIGHT, height=64, width=64, state=uiconst.UI_NORMAL)
        if idCheckers.IsCorporation(ownerID):
            if allianceID:
                ticker = cfg.allianceshortnames.Get(allianceID).shortName
                allianceText = ' [%s]' % localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=ticker, info=('showinfo', const.typeAlliance, allianceID))
                self.ownerLabel += allianceText
        ownerLogo.OnClick = (self.ShowInfo, ownerID, ownerType)
        ownerLogo.SetSize(64, 64)
        self.nameLabel.text = self.ownerLabel
        if self.bounty > 0:
            self.DisplayBountyAmount()
        elif self.bountiesClaimed > 0:
            self.DisplayISKDestroyed()
        elif self.myAmount > 0:
            self.DisplayMyAmount()

    def DisplayISKDestroyed(self):
        killAmount = eveFormat.FmtISK(self.bountiesClaimed, 0)
        self.bountyLabel.text = localization.GetByLabel('UI/Station/BountyOffice/BountyClaimedCorps', iskAmount=killAmount)


class PlaceBountyUtilMenu(UtilMenu):
    default_name = 'placeBountyUtilMenu'
    default_menuAlign = uiconst.TOPRIGHT
    default_align = uiconst.BOTTOMRIGHT
    default_texturePath = ''
    default_top = -2
    default_iconSize = 0

    def ApplyAttributes(self, attributes):
        label = attributes.label or localization.GetByLabel('UI/Station/BountyOffice/AddBounty')
        attributes.GetUtilMenu = self.SetBounty
        attributes.label = label
        attributes.labelAlign = uiconst.CENTERRIGHT
        UtilMenu.ApplyAttributes(self, attributes)
        self.ownerID = attributes.get('ownerID', None)
        self.bountyOwnerIDs = attributes.get('bountyOwnerIDs', None)
        self.hint = localization.GetByLabel('UI/Station/BountyOffice/PlaceBounty')

    def SetBounty(self, menuParent):
        cont = menuParent.AddContainer(align=uiconst.TOTOP, padding=const.defaultPadding)
        cont.GetEntryWidth = lambda mc = cont: 375
        eveLabel.EveLabelLarge(text=localization.GetByLabel('UI/Station/BountyOffice/PlaceBounty'), parent=cont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, bold=True)
        ownerID = self.ownerID
        victimCont = Container(name='victimCont', parent=cont, align=uiconst.TOTOP, height=30, padTop=8)
        imgCont = Container(name='imgCont', parent=victimCont, width=30, align=uiconst.TOLEFT)
        textCont = Container(name='textCont', parent=victimCont, align=uiconst.TOALL, padLeft=const.defaultPadding)
        nameLabel = eveLabel.EveLabelMedium(name='bountyName', parent=textCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, maxLines=1)
        self.bountyLabel = eveLabel.EveLabelSmall(name='bountyAmount', parent=textCont, align=uiconst.TOBOTTOM, state=uiconst.UI_NORMAL)
        bountyAmount = self.GetBountyAmount(*self.bountyOwnerIDs)
        ownerType = cfg.eveowners.Get(ownerID).typeID
        if idCheckers.IsCharacter(ownerID):
            ownerPortrait = Sprite(parent=imgCont, align=uiconst.TOALL, idx=0, texturePath='res:/UI/Texture/silhouette_64.png')
            sm.GetService('photo').GetPortrait(ownerID, 30, ownerPortrait)
        else:
            ownerPortrait = eveIcon.GetLogoIcon(itemID=ownerID, parent=imgCont, acceptNone=False, align=uiconst.TOPRIGHT, height=30, width=30, state=uiconst.UI_NORMAL)
        ownerName = cfg.eveowners.Get(ownerID).name
        nameLabel.text = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=ownerName, info=('showinfo', ownerType, ownerID))
        self.bountyLabel.text = localization.GetByLabel('UI/Common/BountyAmount', bountyAmount=eveFormat.FmtISK(bountyAmount, False))
        bountyCont = Container(name='bountyCont', parent=cont, align=uiconst.TOTOP, height=32, padTop=10)
        self.placeBountiesBtn = Button(parent=bountyCont, label=localization.GetByLabel('UI/Station/BountyOffice/Place'), align=uiconst.TOPRIGHT, func=self.PlaceBounty)
        minAmount = self.GetMinimumBountyAmount()
        editWidth = 375 - self.placeBountiesBtn.width - 6
        self.bountyAmount = SingleLineEditInteger(name='placeEdit', parent=bountyCont, align=uiconst.TOPLEFT, width=editWidth, maxValue=const.MAX_BOUNTY_AMOUNT, hintText=localization.GetByLabel('UI/Station/BountyOffice/InsertAmount', bountyAmount=eveFormat.FmtISK(minAmount)), padRight=const.defaultPadding, top=0, dataType=long)
        self.bountyAmount.OnReturn = self.PlaceBounty
        self.SetBountyHint()

    def SetBountyHint(self):
        bountyAmounts = self.GetBountyAmounts(*self.bountyOwnerIDs)
        charBounty = 0
        corpBounty = 0
        allianceBounty = 0
        if len(bountyAmounts):
            for ownerID, value in bountyAmounts.iteritems():
                if idCheckers.IsCharacter(ownerID):
                    charBounty = value
                elif idCheckers.IsCorporation(ownerID):
                    corpBounty = value
                elif idCheckers.IsAlliance(ownerID):
                    allianceBounty = value

        bountyHint = localization.GetByLabel('UI/Station/BountyOffice/BountyHint', charBounty=eveFormat.FmtISK(charBounty, 0), corpBounty=eveFormat.FmtISK(corpBounty, 0), allianceBounty=eveFormat.FmtISK(allianceBounty, 0))
        self.bountyLabel.hint = bountyHint

    def GetBountyAmounts(self, *ownerIDs):
        bountyAmounts = sm.GetService('bountySvc').GetBounties(*ownerIDs)
        return bountyAmounts

    def GetBountyAmount(self, *ownerIDs):
        bountyAmount = sm.GetService('bountySvc').GetBounty(*ownerIDs)
        return bountyAmount

    def GetMinimumBountyAmount(self):
        ownerID = self.ownerID
        return bountyUtil.GetMinimumBountyAmount(ownerID)

    def PlaceBounty(self, *args):
        if self.placeBountiesBtn.disabled:
            return
        if not self.ownerID:
            return
        ownerID = self.ownerID
        amount = self.bountyAmount.GetValue()
        minAmount = self.GetMinimumBountyAmount()
        if amount < minAmount:
            self.bountyAmount.SetValue('')
            self.bountyAmount.SetHintText(localization.GetByLabel('UI/Station/BountyOffice/TooLowEnterMore', minAmount=eveFormat.FmtISK(minAmount)))
            return
        if ownerID and amount:
            sm.GetService('bountySvc').AddToBounty(ownerID, amount)
            self.bountyAmount.SetValue('')
            bountyAmount = self.GetBountyAmount(*self.bountyOwnerIDs)
            bountyText = localization.GetByLabel('UI/Common/BountyAmount', bountyAmount=eveFormat.FmtISK(bountyAmount))
            self.bountyLabel.text = bountyText
            sm.GetService('objectCaching').InvalidateCachedMethodCall('charMgr', 'GetPublicInfo3', ownerID)
            sm.ScatterEvent('OnBountyPlaced', ownerID)
            self.CloseMenu()

    def GetFullWidth(self):
        return const.defaultPadding * 2 + self._label.width

    def SetLabel(self, label, labelAlign):
        UtilMenu.SetLabel(self, label, labelAlign)
        self._label.left = const.defaultPadding


class BountyPicker(Window):
    __guid__ = 'form.BountyPicker'
    default_windowID = 'BountyPicker'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.ownerID = None
        self.resultList = attributes.Get('resultList', '')
        self.SetScope(uiconst.SCOPE_INGAME)
        self.Confirm = self.ValidateOK
        self.SetCaption(localization.GetByLabel('UI/Station/BountyOffice/PlaceBounty'))
        self.SetMinSize([320, 300])
        self.sr.main = self.GetChild('main')
        self.sr.standardBtns = ButtonGroup(btns=[[localization.GetByLabel('UI/Generic/OK'),
          self.OnOK,
          (),
          81], [localization.GetByLabel('UI/Generic/Cancel'),
          self.OnCancel,
          (),
          81]])
        self.sr.main.children.insert(0, self.sr.standardBtns)
        self.scroll = eveScroll.Scroll(parent=self.sr.main, padding=const.defaultPadding)
        self.scroll.multiSelect = False
        self.MakeList()

    def MakeList(self):
        scrolllist = []
        charList = []
        corpList = []
        allianceList = []
        if self.resultList:
            cfg.eveowners.Prime(self.resultList)
        for ownerID in self.resultList:
            if idCheckers.IsCharacter(ownerID):
                charList.append(ownerID)
            elif idCheckers.IsCorporation(ownerID):
                corpList.append(ownerID)
            elif idCheckers.IsAlliance(ownerID):
                allianceList.append(ownerID)

        if len(charList):
            myLabel = localization.GetByLabel('UI/Search/UniversalSearch/Characters')
            charGroup = self.GetGroup(charList, myLabel, 'charBounty')
            scrolllist.append(charGroup)
        if len(corpList):
            myLabel = localization.GetByLabel('UI/Search/UniversalSearch/Corporations')
            charGroup = self.GetGroup(corpList, myLabel, 'corpBounty')
            scrolllist.append(charGroup)
        if len(allianceList):
            myLabel = localization.GetByLabel('UI/Search/UniversalSearch/Alliances')
            charGroup = self.GetGroup(allianceList, myLabel, 'allianceBounty')
            scrolllist.append(charGroup)
        self.scroll.Load(fixedEntryHeight=18, contentList=scrolllist, noContentHint=localization.GetByLabel('UI/Station/BountyOffice/NoOneFound'))

    def GetGroup(self, list, label, type):
        return GetFromClass(ListGroup, {'GetSubContent': self.GetSubContent,
         'label': label,
         'id': ('bounty', type, label),
         'state': 'locked',
         'BlockOpenWindow': 1,
         'showicon': 'hide',
         'showlen': 1,
         'groupName': type,
         'groupItems': list,
         'updateOnToggle': 0})

    def GetSubContent(self, items, *args):
        cfg.eveowners.Prime(items.groupItems)
        scrolllist = []
        for ownerID in items.groupItems:
            owner = cfg.eveowners.Get(ownerID)
            scrolllist.append((owner.ownerName.lower(), GetFromClass(PlaceBountyEntry, {'label': owner.ownerName,
              'OnDblClick': self.OnOK,
              'typeID': owner.typeID,
              'itemID': ownerID,
              'confirmOnDblClick': 1,
              'listvalue': [owner.ownerName, ownerID]})))

        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def Confirm(self):
        self.OnOK()

    def ValidateOK(self):
        log.LogInfo('ValidateOK')
        if self.ownerID is None:
            return 0
        return 1

    def OnOK(self, *args):
        if len(self.scroll.GetNodes()) == 0:
            self.ownerID = None
            self.CloseByUser()
        sel = self.scroll.GetSelected()
        if sel:
            self.ownerID = sel[0].itemID
            self.CloseByUser()

    def OnCancel(self, *args):
        self.ownerID = None
        self.CloseByUser()


class PlaceBountyEntry(Generic):
    __guid__ = 'listentry.PlaceBountyEntry'

    def Startup(self, *args):
        Generic.Startup(self, args)
        self.sr.label.left = 40
        self.sr.label.state = uiconst.UI_NORMAL
        self.imgCont = Container(name='imgCont', parent=self, width=34, align=uiconst.TOLEFT, padTop=2, padBottom=2, padLeft=2)
        self.stateCont = Container(name='stateCont', parent=self, width=16, align=uiconst.TORIGHT)

    def Load(self, node):
        self.sr.node = node
        data = node
        ownerID = self.ownerID = data.itemID
        self.typeID = data.typeID
        label = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=data.label, info=('showinfo', self.typeID, self.ownerID))
        self.sr.label.text = label
        if node.selected:
            self.Select()
        else:
            self.Deselect()
        if idCheckers.IsCharacter(ownerID):
            ownerLogo = Sprite(parent=self.imgCont, align=uiconst.TOALL, size=32, texturePath='res:/UI/Texture/silhouette_64.png')
            sm.GetService('photo').GetPortrait(ownerID, 32, ownerLogo)
        else:
            ownerLogo = eveIcon.GetLogoIcon(ownerID, parent=self.imgCont, acceptNone=False, align=uiconst.TOPRIGHT, height=32, width=32, state=uiconst.UI_NORMAL)
            ownerLogo.SetSize(32, 32)
        ownerLogo.OnClick = (self.ShowInfo, ownerID, self.typeID)
        ownerLogo.hint = cfg.eveowners.Get(ownerID).name

    def GetHeight(_self, *args):
        node, width = args
        node.height = 38
        return node.height

    def GetMenu(self):
        if self.sr.node.Get('GetMenu', None):
            return self.sr.node.GetMenu(self)
        if self.ownerID:
            return GetMenuService().GetMenuFromItemIDTypeID(self.ownerID, self.typeID, includeMarketDetails=True)
        if self.typeID:
            return GetMenuService().GetMenuFromItemIDTypeID(None, self.typeID, includeMarketDetails=True)
        return []

    def ShowInfo(self, ownerID, typeID, *args):
        sm.GetService('info').ShowInfo(typeID, ownerID)
