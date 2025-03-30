#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_wars.py
from collections import defaultdict
import blue
import carbonui.const as uiconst
import eve.common.lib.appConst as appConst
import evewar.util as warUtil
import localization
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control import eveScroll
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.client.script.ui.shared.neocom.corporation.corpPanelConst import CorpPanel
from eve.client.script.ui.shared.neocom.corporation.war.corporationOrAlliancePickerDailog import CorporationOrAlliancePickerDailog
from eve.client.script.ui.shared.neocom.corporation.war.warAllyEntry import AllyEntry
from eve.client.script.ui.shared.neocom.corporation.war.warEntry import WarEntry
from eve.client.script.ui.shared.neocom.corporation.war.warWindows import HeaderClear, WarAssistanceOfferWnd, WarSurrenderWnd
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.common.lib import appConst as const
from eve.common.script.sys.idCheckers import IsNPC, IsAlliance, IsCorporation
from eveservices.menu import GetMenuService

class CorpWars(Container):
    is_loaded = False

    def ApplyAttributes(self, attributes):
        super(CorpWars, self).ApplyAttributes(attributes)
        self.searchOwnerID = None
        self.tab_group = None
        corpUISignals.on_war_changed.connect(self.OnWarChanged)

    def Load(self, panel_id, *args):
        if not self.is_loaded:
            self.is_loaded = True
            self.ConstructLayout()

    def ConstructLayout(self):
        self.ourWarsScroll = None
        self.allWarsScroll = None
        self.maxWarID = const.maxInt
        self.warbatches = []
        self.declareBtnCont = ContainerAutoSize(name='declareBtnCont', align=uiconst.TOBOTTOM, parent=self, padTop=8)
        declareBtnGroup = ButtonGroup(parent=self.declareBtnCont)
        declareButton = declareBtnGroup.AddButton(localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/DeclareWar'), self.DeclareWar)
        self.ourWarsCont = Container(name='ourWarsCont', parent=self, align=uiconst.TOALL, display=False)
        self.ourWarsScroll = eveScroll.Scroll(parent=self.ourWarsCont)
        reasonDeclareBtnNotAvailable = None
        isDirector = session.corprole & const.corpRoleDirector == const.corpRoleDirector
        if session.allianceid:
            if not isDirector or sm.GetService('alliance').GetAlliance(session.allianceid).executorCorpID != session.corpid:
                reasonDeclareBtnNotAvailable = 'UI/Corporations/Wars/DeclareWarNotAvailableAlliance'
        elif not isDirector:
            reasonDeclareBtnNotAvailable = 'UI/Corporations/Wars/DeclareWarNotAvailableCorp'
        if reasonDeclareBtnNotAvailable:
            declareButton.Disable()
            declareButton.hint = localization.GetByLabel(reasonDeclareBtnNotAvailable)
        self.allWarsCont = Container(name='allWarsCont', parent=self, align=uiconst.TOALL, display=False)
        allWarsSettingsCont = Container(name='allWarsSettingsCont', parent=self.allWarsCont, align=uiconst.TOTOP, height=Button.default_height, padTop=2)
        browseCont = Container(name='browseCont', parent=self.allWarsCont, align=uiconst.TOBOTTOM, padding=(appConst.defaultPadding,
         0,
         appConst.defaultPadding,
         appConst.defaultPadding), state=uiconst.UI_NORMAL)
        self.prevBtn = Button(parent=browseCont, align=uiconst.TOPLEFT, label=localization.GetByLabel('UI/Common/Prev'), func=lambda : self.PopulateTop50(-1), args=())
        self.nextBtn = Button(parent=browseCont, align=uiconst.TOPRIGHT, label=localization.GetByLabel('UI/Common/Next'), func=lambda : self.PopulateTop50(1), args=())
        browseCont.height = self.nextBtn.height
        self.showCryForHelpCb = Checkbox(parent=allWarsSettingsCont, align=uiconst.TOPLEFT, left=appConst.defaultPadding, height=14, width=300, settingsKey='allwars_showcryforhelp', text=localization.GetByLabel('UI/Corporations/Wars/ShowCryForHelp'), checked=settings.user.ui.Get('allwars_showcryforhelp', 0), callback=self.CheckBoxChange)
        self.showCryForHelpCb.hint = localization.GetByLabel('UI/Corporations/Wars/NotFilterWhenSearching')
        self.searchButton = Button(parent=allWarsSettingsCont, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/Search'), align=uiconst.TOPRIGHT, func=self.Search, btn_default=1)
        self.searchEdit = SingleLineEditText(name='edit', parent=allWarsSettingsCont, left=self.searchButton.width + 4, width=150, align=uiconst.TOPRIGHT, maxLength=32)
        self.searchEdit.OnReturn = self.Search
        self.allWarsScroll = eveScroll.Scroll(parent=self.allWarsCont, padding=(0, 4, 0, 0))
        self.tab_group = ToggleButtonGroup(parent=self, idx=0, align=uiconst.TOTOP, callback=self.Refresh, padBottom=8)
        self.tab_group.AddButton(CorpPanel.WARS_OUR, localization.GetByLabel('UI/Corporations/CorporationWindow/Wars/OurWars'), panel=self.ourWarsCont)
        self.tab_group.AddButton(CorpPanel.WARS_ALL, localization.GetByLabel('UI/Corporations/Wars/AllWars'), panel=self.allWarsCont, hint=localization.GetByLabel('UI/Corporations/Common/UpdateDelay15Minutes'))
        self.tab_group.SelectByID(CorpPanel.WARS_OUR)
        self.killentries = 25

    def GetWarAllyContractMenu(self, entry, *args):
        warNegotiation = entry.sr.node.warNegotiation
        myWarEntityID = session.allianceid if session.allianceid else session.corpid
        menu = []
        if warNegotiation.ownerID1 == myWarEntityID:
            menu.append(('Retract Offer', lambda *args: None))
        else:
            menu.append(('Accept Offer', sm.GetService('war').AcceptAllyNegotiation, (warNegotiation.warNegotiationID,)))
        return menu

    def OnWarChanged(self, war, ownerIDs, change):
        self.Refresh()

    def Refresh(self, *args, **kwargs):
        if not self.tab_group:
            return
        selectedTab = self.tab_group.GetSelected()
        if selectedTab == CorpPanel.WARS_ALL:
            self.ShowAllWars()
        elif selectedTab == CorpPanel.WARS_OUR:
            self.ShowWars()

    def GetEntry(self, warID, scroll):
        for entry in scroll.GetNodes():
            if entry is None or entry.war is None:
                continue
            if entry.panel is None or entry.panel.destroyed:
                continue
            if entry.war.warID == warID:
                return entry

    def GetWarEntryForMyWars(self, war, anyWarsWithAllyEntries = False, allyDataForWar = ()):
        isExpandable = bool(allyDataForWar)
        return GetFromClass(WarEntry, {'label': '',
         'war': war,
         'myWars': True,
         'hasAllyPadding': anyWarsWithAllyEntries,
         'isExpandable': isExpandable,
         'GetSubContent': self.GetAlliesSubContent,
         'openByDefault': True if isExpandable else False,
         'id': ('WarEntry', war.warID),
         'groupItems': allyDataForWar})

    def GetWarEntryForAllWarsList(self, war):
        return GetFromClass(WarEntry, {'label': '',
         'war': war,
         'myWars': False})

    def GetAlliesSubContent(self, nodedata, *args):
        scrollList = []
        for allyEntryData in nodedata.groupItems:
            allyName = cfg.eveowners.Get(allyEntryData['allyID']).name
            isWarNegotiation = bool(allyEntryData.get('warNegotiation', False))
            sortValue = (-isWarNegotiation, allyName.lower())
            entry = GetFromClass(AllyEntry, data=allyEntryData)
            scrollList.append((sortValue, entry))

        scrollList = SortListOfTuples(scrollList)
        return scrollList

    def ShowWars(self, *args):
        owner_id = session.allianceid or session.corpid
        scroll_list = self.get_scroll_entries(owner_id, myWars=True)
        self.ourWarsScroll.Load(contentList=scroll_list, headers=[], noContentHint=self._get_no_content_hint(owner_id))

    def ShowAllWars(self, *args):
        searchValue = self.searchEdit.GetValue()
        if searchValue:
            scroll_list = self.get_scroll_entries(self.searchOwnerID, myWars=False)
            scroll_list.insert(0, self._get_search_entry())
            self.allWarsScroll.Load(contentList=scroll_list, headers=[], noContentHint=self._get_no_content_hint(self.searchOwnerID))
        else:
            self.PopulateTop50()

    def GetFactionWars(self, corpID, *args):
        return sm.GetService('facwar').GetFactionWars(corpID)

    def PopulateTop50(self, browse = None):
        cryForHelp = settings.user.ui.Get('allwars_showcryforhelp', 0)
        if cryForHelp:
            allWars = sm.RemoteSvc('warsInfoMgr').GetWarsRequiringAssistance()
        elif browse == -1 and len(self.warbatches) > 1:
            allWars = self.warbatches[-2]
            self.warbatches = self.warbatches[:-1]
        elif browse == 1 and len(self.warbatches):
            lastWar = self.warbatches[-1][-1]
            allWars = sm.RemoteSvc('warsInfoMgr').GetTop50(lastWar.warID)
            if len(allWars):
                self.warbatches += [allWars]
        else:
            allWars = sm.RemoteSvc('warsInfoMgr').GetTop50(self.maxWarID)
            if len(allWars):
                self.warbatches = [allWars]
        scrolllist = []
        ownerIDsToPrime = set()
        for war in allWars:
            ownerIDsToPrime.update({war.declaredByID, war.againstID})

        cfg.eveowners.Prime(ownerIDsToPrime)
        cfg.corptickernames.Prime(ownerIDsToPrime)
        if allWars:
            for eachWar in sorted(allWars, key=lambda x: x.warID, reverse=True):
                entry = self.GetWarEntryForAllWarsList(eachWar)
                scrolllist.append(entry)

            if len(self.warbatches) <= 1:
                scrolllist.insert(0, GetFromClass(Header, {'label': localization.GetByLabel('UI/Corporations/Wars/NumRecentWars', numWars=len(scrolllist))}))
        self.allWarsScroll.Load(contentList=scrolllist, headers=[], noContentHint='')
        if len(allWars) < appConst.WARS_PER_PAGE:
            self.nextBtn.Disable()
        else:
            self.nextBtn.Enable()
        if len(self.warbatches) > 1:
            self.prevBtn.Enable()
        else:
            self.prevBtn.Disable()

    def get_scroll_entries(self, ownerID, myWars = False):
        regwars = sm.GetService('war').GetWars(ownerID)
        facwars = self.GetFacWars(ownerID)
        allWars = regwars.copy()
        allWars.update(facwars)
        owners = set()
        myWarableID = ownerID if ownerID in (session.allianceid, session.corpid) else session.allianceid or session.corpid
        allyNegotiationsByWarID = defaultdict(list)
        for row in sm.GetService('war').GetAllyNegotiations():
            allyNegotiationsByWarID[row.warID].append(row)
            owners.add(row.ownerID1)
            owners.add(row.ownerID2)
            owners.add(row.declaredByID)
            owners.add(row.againstID)
            if myWarableID == row.ownerID1 and row.warID not in regwars:
                foreignWar = sm.RemoteSvc('warsInfoMgr').GetWarsByOwnerID(row.againstID).Index('warID')[row.warID]
                regwars[row.warID] = warUtil.War(foreignWar)

        for war in allWars.values():
            owners.add(war.declaredByID)
            owners.add(war.againstID)
            owners.update(getattr(war, 'allies', {}).keys())

        owners = filter(None, owners)
        if len(owners):
            cfg.eveowners.Prime(owners)
            cfg.corptickernames.Prime(owners)
        if self.destroyed:
            return
        scrolllist = []
        alliesByAllyIDByWarID = self.GetAllyRowsByWarID(allWars)
        anyWarsWithAllyEntries = bool(alliesByAllyIDByWarID) or bool(allyNegotiationsByWarID)
        for wars in (regwars, facwars):
            for war in wars.values():
                if myWars:
                    alliesByAllyID = alliesByAllyIDByWarID.get(war.warID, {})
                    allyDataForWar = self.GetAllActiveAllyEntryData(war, alliesByAllyID)
                    if war.warID in allyNegotiationsByWarID:
                        allyNegotiationData = [ {'warID': neg.warID,
                         'allyID': neg.ownerID1,
                         'warNegotiation': neg} for neg in allyNegotiationsByWarID[war.warID] if neg.ownerID1 not in alliesByAllyID ]
                        allyDataForWar += allyNegotiationData
                    entry = self.GetWarEntryForMyWars(war, anyWarsWithAllyEntries, allyDataForWar)
                else:
                    entry = self.GetWarEntryForAllWarsList(war)
                scrolllist.append(entry)

        return scrolllist

    def _get_no_content_hint(self, corpOrAllianceID):
        corpName = cfg.eveowners.Get(corpOrAllianceID).ownerName
        notContentHint = localization.GetByLabel('UI/Corporations/CorporationWindow/Wars/CorpOrAllianceNotInvolvedInWars', corpName=corpName)
        return notContentHint

    def _get_search_entry(self):
        searchValue = self.searchEdit.GetValue()
        search_entry = GetFromClass(HeaderClear, {'label': localization.GetByLabel('UI/Corporations/Wars/SearchResult', searchResult=searchValue),
         'func': self.ClearSearch})
        return search_entry

    def GetAllActiveAllyEntryData(self, war, alliesByAllyID):
        allData = []
        for allyID, allyRow in alliesByAllyID.items():
            try:
                data = {'warID': war.warID,
                 'allyID': allyID,
                 'isAlly': True,
                 'allyRow': allyRow,
                 'originalWarTimeFinished': war.timeFinished,
                 'originalWarTimeStarted': war.timeStarted}
                allData.append(data)
            except AttributeError:
                pass

        return allData

    def GetFacWars(self, corpOrAllianceID):
        facwars = {}
        if not session.warfactionid:
            return facwars
        if not IsAlliance(corpOrAllianceID) and not IsCorporation(corpOrAllianceID):
            return facwars
        if sm.GetService('facwar').GetCorporationWarFactionID(session.corpid):
            facwars = self.GetFactionWars(session.corpid)
        return facwars

    def GetAllyRowsByWarID(self, wars):
        alliesByAllyIDByWarID = defaultdict(dict)
        for eachWar in wars.values():
            allies = getattr(eachWar, 'allies', {})
            for allyID, allyRow in allies.items():
                if blue.os.GetWallclockTime() > allyRow.timeFinished:
                    continue
                alliesByAllyIDByWarID[eachWar.warID][allyID] = allyRow

        return dict(alliesByAllyIDByWarID)

    def ClearSearch(self, *args):
        self.searchEdit.SetValue('')
        self.searchOwnerID = None
        self.PopulateTop50()

    def CheckBoxChange(self, *args):
        cryForHelp = self.showCryForHelpCb.GetValue()
        settings.user.ui.Set('allwars_showcryforhelp', cryForHelp)
        self.PopulateTop50()

    def Search(self, *args):
        str = self.searchEdit.GetValue()
        if not str or str == '':
            return
        dlg = CorporationOrAlliancePickerDailog.Open(searchStr=str)
        dlg.ShowModal()
        if dlg.ownerID:
            self.searchOwnerID = dlg.ownerID
            scroll_list = self.get_scroll_entries(dlg.ownerID, self.allWarsScroll)
            self.allWarsScroll.Load(contentList=scroll_list, headers=[], noContentHint=self._get_no_content_hint(dlg.ownerID))

    def DeclareWar(self, *args):
        GetMenuService().DeclareWar()
        self.ShowWars()

    def CreateAllyContract(self, war):
        WarAssistanceOfferWnd.CloseIfOpen()
        requesterID = session.corpid if session.allianceid is None else session.allianceid
        WarAssistanceOfferWnd.Open(war=war, requesterID=requesterID, isRequest=True, iskValue=getattr(war, 'reward', 0))

    def SurrenderWar(self, war, *args):
        WarSurrenderWnd.CloseIfOpen()
        requesterID = session.corpid if session.allianceid is None else session.allianceid
        WarSurrenderWnd.Open(war=war, requesterID=requesterID, isSurrender=True, isAllyRequest=False, isRequest=True)
