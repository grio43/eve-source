#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\contracts\contractPanels.py
import eveicon
from carbon.common.script.util.format import FmtDate
import uthread
from carbonui import uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.combo import Combo
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.neocom.contracts.contractentry import ContractEntrySmall, ContractStartPageEntry
from eve.client.script.ui.util import searchOld
from eve.client.script.util.contractutils import IsSearchStringLongEnough, ConFmtDate, GetColoredContractStatusText, GetContractLabel
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from eve.common.script.util.contractscommon import CONTYPE_AUCTIONANDITEMECHANGE
import evelink
from eveexceptions import UserError
from localization import GetByLabel
import blue
from utillib import KeyVal
RESULTS_PER_PAGE = 100
MAX_IGNORED = 1000

class StartPagePanel(Container):
    __notifyevents__ = ['OnContractCacheCleared']
    __guid__ = 'xtriui.StartPagePanel'
    submitFunc = None

    def ApplyAttributes(self, attributes):
        super(StartPagePanel, self).ApplyAttributes(attributes)
        self.ConstructLayout()
        sm.RegisterNotify(self)

    def AddItem(self, icon, header, text, isSmall = False):
        header = unicode(header).replace('\n', '')
        text = text.rstrip('\n')
        data = {'header': header,
         'text': text,
         'icon': icon,
         'isSmall': isSmall}
        ContractStartPageEntry(parent=self.startPageScroll, align=uiconst.TOTOP, node=KeyVal(data))

    def ConstructLayout(self):
        header = EveCaptionLarge(text=GetByLabel('UI/Contracts/ContractEntry/MyStartPage'), parent=self, left=14, top=8)
        self.startPageScroll = ScrollContainer(parent=self, align=uiconst.TOALL, padding=(uiconst.defaultPadding,
         header.textheight + uiconst.defaultPadding * 2,
         uiconst.defaultPadding,
         uiconst.defaultPadding))
        self.buttonGroup = ButtonGroup(parent=self, idx=0)
        self.buttonGroup.AddButton(GetByLabel('UI/Inventory/ItemActions/CreateContract'), lambda x: sm.GetService('contracts').OpenCreateContract())

    def Init(self):
        self.startPageScroll.Flush()
        mpi = sm.GetService('contracts').CollectMyPageInfo()
        n = mpi.numContractsLeft
        ntot = mpi.numContractsTotal
        np = mpi.numContractsLeftInCorp
        nforcorp = mpi.numContractsLeftForCorp
        desc = GetByLabel('UI/Contracts/ContractsService/YouCanCreateNew', numContracts=ntot)
        if not idCheckers.IsNPC(eve.session.corpid):
            desc += '<br>' + GetByLabel('UI/Contracts/ContractsService/YouCanCreateForCorp', numContracts=np)
        if session.corprole & appConst.corpRoleContractManager == appConst.corpRoleContractManager:
            desc += '<br>' + GetByLabel('UI/Contracts/ContractsService/YouCanCreateOnBehalfOfCorp', numContracts=nforcorp)
        createLabel = GetByLabel('UI/Contracts/ContractsService/YouCanCreate', numContracts=n)
        self.AddItem('res:/ui/Texture/WindowIcons/contracts.png', evelink.local_service_link('OpenCreateContract', createLabel), desc)
        ignoreList = set(settings.user.ui.Get('contracts_ignorelist', []))
        numAssignedToMeAuctionItemExchange = 0
        numAssignedToMeCourier = 0
        numAssignedToMyCorpAuctionItemExchange = 0
        numAssignedToMyCorpCourier = 0
        if mpi.outstandingContracts is None:
            eve.Message('ConNotReady')
            mpi.outstandingContracts = []
        else:
            for contract in mpi.outstandingContracts:
                if contract[0] in ignoreList or contract[1] in ignoreList:
                    continue
                if contract[2] == session.charid:
                    if contract[3] == appConst.conTypeCourier:
                        numAssignedToMeCourier += 1
                    else:
                        numAssignedToMeAuctionItemExchange += 1
                elif contract[3] == appConst.conTypeCourier:
                    numAssignedToMyCorpCourier += 1
                else:
                    numAssignedToMyCorpAuctionItemExchange += 1

        if mpi.numRequiresAttention > 0:
            attentionReqLabel = GetByLabel('UI/Contracts/ContractsService/RequireAttention', numContracts=mpi.numRequiresAttention)
            attentionReqDescLabel = GetByLabel('UI/Contracts/ContractsService/RequiresAttentionDesc')
            self.AddItem('res:/ui/Texture/WindowIcons/warning.png', evelink.local_service_link('ShowContracts', attentionReqLabel, status=-1, forCorp=0), attentionReqDescLabel)
        if mpi.numRequiresAttentionCorp > 0:
            attentionReqCorpLabel = GetByLabel('UI/Contracts/ContractsService/RequireAttentionCorp', numContracts=mpi.numRequiresAttentionCorp)
            attentionReqCorpDescLabel = GetByLabel('UI/Contracts/ContractsService/RequireAttentionCorpDesc')
            self.AddItem('res:/ui/Texture/WindowIcons/warning.png', evelink.local_service_link('ShowContracts', attentionReqCorpLabel, status=-1, forCorp=1), attentionReqCorpDescLabel)
        if numAssignedToMeAuctionItemExchange > 0 or numAssignedToMeCourier > 0:
            assignedLabel = GetByLabel('UI/Contracts/ContractsService/AssignedPersonal', numContracts=numAssignedToMeAuctionItemExchange + numAssignedToMeCourier)
            subText = ''
            subTextList = []
            if numAssignedToMeAuctionItemExchange > 0:
                auctionLabel = GetByLabel('UI/Contracts/ContractsService/AuctionItemExchange', numContracts=numAssignedToMeAuctionItemExchange)
                method = self._GetContractMethodText(CONTYPE_AUCTIONANDITEMECHANGE, isCorp=0)
                subText += self._GetContractLink(auctionLabel, method)
            if numAssignedToMeCourier > 0:
                assignedCourierLabel = GetByLabel('UI/Contracts/ContractsService/AssignedCourier', numContracts=numAssignedToMeCourier)
                method = self._GetContractMethodText(appConst.conTypeCourier, isCorp=0)
                subText += self._GetContractLink(assignedCourierLabel, method, numSpaces=2)
            self.AddItem('res:/ui/Texture/WindowIcons/info.png', assignedLabel, subText)
        if numAssignedToMyCorpAuctionItemExchange > 0 or numAssignedToMyCorpCourier > 0:
            numContracts = numAssignedToMyCorpAuctionItemExchange + numAssignedToMyCorpCourier
            corpAssignedLabel = GetByLabel('UI/Contracts/ContractsService/AssignedCorp', numContracts=numContracts)
            subText = ''
            if numAssignedToMyCorpAuctionItemExchange > 0:
                corpExchangeLabel = GetByLabel('UI/Contracts/ContractsService/AssignedCorpAuctionItemExchange', numContracts=numAssignedToMyCorpAuctionItemExchange)
                method = self._GetContractMethodText(CONTYPE_AUCTIONANDITEMECHANGE, isCorp=1)
                subText += self._GetContractLink(corpExchangeLabel, method)
            if numAssignedToMyCorpCourier > 0:
                corpCourierLabel = GetByLabel('UI/Contracts/ContractsService/AssignedCorpCourier', numContracts=numAssignedToMyCorpCourier)
                method = self._GetContractMethodText(appConst.conTypeCourier, isCorp=1)
                subText += self._GetContractLink(corpCourierLabel, method)
            self.AddItem('res:/ui/Texture/WindowIcons/info.png', corpAssignedLabel, subText)
        if mpi.numBiddingOn > 0:
            activeLabel = GetByLabel('UI/Contracts/ContractsService/BiddingOn', numAuctions=mpi.numBiddingOn)
            activeDescLabel = GetByLabel('UI/Contracts/ContractsService/BiddingOnDesc')
            self.AddItem('64_16', evelink.local_service_link('ShowContracts', activeLabel, status=10, forCorp=0), activeDescLabel)
        if mpi.numInProgress > 0:
            progressLabel = GetByLabel('UI/Contracts/ContractsService/InProgress', numContracts=mpi.numInProgress)
            progressDescLabel = GetByLabel('UI/Contracts/ContractsService/InProgressDesc')
            self.AddItem('res:/ui/Texture/WindowIcons/info.png', evelink.local_service_link('ShowContracts', progressLabel, status=1, forCorp=0), progressDescLabel)
        if mpi.numBiddingOnCorp > 0:
            biddingOnLabel = GetByLabel('UI/Contracts/ContractsService/BiddingOnCorp', numAuctions=mpi.numBiddingOnCorp)
            biddingOnDescLabel = GetByLabel('UI/Contracts/ContractsService/BiddingOnCorpDesc')
            self.AddItem('64_16', evelink.local_service_link('ShowContracts', biddingOnLabel, status=10, forCorp=1), biddingOnDescLabel)
        if mpi.numInProgressCorp > 0:
            inProgressCorpLabel = GetByLabel('UI/Contracts/ContractsService/InProgressCorp', numContracts=mpi.numInProgressCorp)
            inProgressCorpDescLabel = GetByLabel('UI/Contracts/ContractsService/InProgressCorpDesc')
            self.AddItem('res:/ui/Texture/WindowIcons/info.png', evelink.local_service_link('ShowContracts', inProgressCorpLabel, status=1, forCorp=1), inProgressCorpDescLabel)
        ignoreList = settings.user.ui.Get('contracts_ignorelist', [])
        l = len(ignoreList)
        if l > 0:
            ignoreLabel = GetByLabel('UI/Contracts/ContractsService/Ignoring', numIssuers=l)
            ignoreDescLabel = GetByLabel('UI/Contracts/ContractsService/IngoringDesc', numIssuers=MAX_IGNORED)
            self.AddItem('ui_38_16_208', evelink.local_service_link('OpenIgnoreList', ignoreLabel), ignoreDescLabel, isSmall=True)
        mess = sm.GetService('contracts').GetMessages()
        for i in mess:
            self.AddItem('ui_38_16_208', '', i, isSmall=True)

    def _GetContractMethodText(self, contractType, isCorp):
        methodTextCorp = 'method=OpenAssignedToMe&contractType=%s&isCorp=%s' % (contractType, isCorp)
        return methodTextCorp

    def _GetContractLink(self, label, method, numSpaces = 1):
        link = ' ' * numSpaces
        link += '- <a href="localsvc:%s">%s</a><br>' % (method, label)
        return link

    def OnContractCacheCleared(self, *args):
        if self.display:
            self.Init()


class MyContractsPanel(Container):
    __guid__ = 'xtriui.MyContractsPanel'
    inited = 0
    submitFunc = None

    def _OnClose(self):
        Container._OnClose(self)
        if self.inited:
            settings.user.ui.Set('mycontracts_filter_tofrom', self.GetIssuedByToFilterValue())
            settings.char.ui.Set('mycontracts_filter_owner', self.GetOwnerFilterValue())
            settings.user.ui.Set('mycontracts_filter_status', self.fltStatus.GetValue())
            settings.user.ui.Set('mycontracts_filter_type', self.GetContractTypeFilterValue())

    def GetOwnerFilterValue(self):
        return self.fltOwner.GetValue()

    def Init(self):
        if not self.inited:
            self.ConstructFilters()
            self.contractlistParent = contractlistParent = Container(name='contractlistParent', align=uiconst.TOALL, pos=(uiconst.defaultPadding,
             uiconst.defaultPadding,
             uiconst.defaultPadding,
             uiconst.defaultPadding), parent=self)
            self.contractlist = contractlist = Scroll(parent=contractlistParent, name='mycontractlist')
            contractlist.sr.id = 'mycontractlist'
            contractlist.ShowHint(GetByLabel('UI/Contracts/ContractsWindow/ClickGetContracts'))
            contractlist.multiSelect = 0
            contractlistParent.top = 5
            self.currPage = 0
            self.pages = {0: None}
            self.fetchingContracts = 0
            self.buttonGroup = ButtonGroup(parent=self, idx=0)
            self.buttonGroup.AddButton(GetByLabel('UI/Inventory/ItemActions/CreateContract'), lambda x: sm.GetService('contracts').OpenCreateContract())
        self.inited = 1
        self.FetchContracts()

    def ConstructFilters(self):
        PAD = 5
        self.filters = filters = Container(name='filters', parent=self, height=24, padTop=16, align=uiconst.TOTOP)
        self.comboGridContainer = comboGridContainer = GridContainer(name='comboContainer', parent=filters, align=uiconst.TOLEFT_PROP, width=0.73, maxWidth=600, contentSpacing=(PAD, 0), columns=4)
        options = [(GetByLabel('UI/Common/All'), None),
         (GetByLabel('UI/Contracts/Auction'), appConst.conTypeAuction),
         (GetByLabel('UI/Contracts/ContractsWindow/ItemExchange'), appConst.conTypeItemExchange),
         (GetByLabel('UI/Contracts/ContractsWindow/Courier'), appConst.conTypeCourier)]
        self.fltType = Combo(name='contractTypeCombo', label=GetByLabel('UI/Contracts/ContractsWindow/ContractType'), parent=comboGridContainer, align=uiconst.TOALL, options=options, select=settings.user.ui.Get('mycontracts_filter_type', None), callback=self.OnComboChange)
        options = [(GetByLabel('UI/Contracts/ContractsWindow/IssuedToBy'), None), (GetByLabel('UI/Contracts/ContractsWindow/IssuedBy'), False), (GetByLabel('UI/Contracts/ContractsWindow/IssuedTo'), True)]
        self.fltToFrom = Combo(name='issuedByToCombo', label=GetByLabel('UI/Contracts/ContractsWindow/Action'), parent=comboGridContainer, align=uiconst.TOALL, options=options, select=settings.user.ui.Get('mycontracts_filter_tofrom', None), callback=self.OnComboChange, adjustWidth=True)
        corpName = cfg.eveowners.Get(eve.session.corpid).name
        charName = cfg.eveowners.Get(eve.session.charid).name
        val = getattr(self, 'lookup', None)
        if not val:
            val = settings.char.ui.Get('mycontracts_filter_owner', charName)
        self.fltOwner = SingleLineEditText(name='ownerCombo', parent=comboGridContainer, align=uiconst.TOALL, label=GetByLabel('UI/Contracts/ContractsWindow/Owner'), setvalue=val)
        ops = [(charName, charName), (corpName, corpName)]
        self.fltOwner.LoadCombo('usernamecombo', ops, self.OnComboChange)
        options = [(GetByLabel('UI/Contracts/ContractEntry/Outstanding'), appConst.conStatusOutstanding),
         (GetByLabel('UI/Contracts/ContractsWindow/InProgress'), appConst.conStatusInProgress),
         (GetByLabel('UI/Contracts/ContractsWindow/Finished'), appConst.conStatusFinished),
         (GetByLabel('UI/Journal/JournalWindow/Contracts/RequiresAttentionFilter'), appConst.conStatusRequiresAttention),
         (GetByLabel('UI/Journal/JournalWindow/Contracts/BidOnByFilter'), appConst.conStatusBidOnBy)]
        self.fltStatus = Combo(name='statusCombo', label=GetByLabel('UI/Contracts/ContractsWindow/Status'), parent=comboGridContainer, align=uiconst.TOALL, options=options, select=settings.user.ui.Get('mycontracts_filter_status', None), callback=self.OnComboChange)
        self.submitBtn = Button(parent=filters, label=GetByLabel('UI/Contracts/ContractsWindow/GetContracts'), func=self.FetchContracts, align=uiconst.TORIGHT, padRight=PAD)
        self.transMyFwdBtn = ButtonIcon(name='transMyFwdBtn', parent=filters, align=uiconst.TORIGHT, width=filters.height, texturePath=eveicon.caret_right, iconSize=16, hint=GetByLabel('UI/Common/ViewMore'), func=self.BrowseNextPage, padRight=4)
        self.transMyBackBtn = ButtonIcon(name='transMyBackBtn', parent=filters, align=uiconst.TORIGHT, width=filters.height, texturePath=eveicon.caret_left, iconSize=16, hint=GetByLabel('UI/Common/Previous'), func=self.BrowsePreviousPage)

    def BrowseNextPage(self):
        return self.BrowseMyContracts(1)

    def BrowsePreviousPage(self):
        return self.BrowseMyContracts(-1)

    def BrowseMyContracts(self, direction, *args):
        self.currPage = max(0, self.currPage + direction)
        self.DoFetchContracts()

    def FetchContracts(self, *args):
        if self.fetchingContracts:
            return
        self.submitBtn.Disable()
        self.fetchingContracts = 1
        uthread.new(self.EnableButtonTimer)
        self.currPage = 0
        self.pages = {0: None}
        self.DoFetchContracts()

    def EnableButtonTimer(self):
        blue.pyos.synchro.SleepWallclock(3000)
        try:
            self.fetchingContracts = 0
            self.submitBtn.Enable()
        except:
            pass

    def DoFetchContracts(self):
        self.contractlist.Load(contentList=[])
        self.contractlist.ShowHint(GetByLabel('UI/Contracts/ContractsWindow/FetchingData'))
        try:
            if self.currPage == 0:
                self.transMyBackBtn.Disable()
            else:
                self.transMyBackBtn.Enable()
            ownerID = self.GetOwnerID()
            if ownerID is None:
                return
            contracts, itemsByContractID = self._GetContractsToShow(ownerID)
            self.PrimeOwnerIDs(contracts)
            scrolllist = []
            for contract in contracts:
                contractItems = itemsByContractID.get(contract.contractID, [])
                entry = self._GetListEntry(contract, contractItems)
                scrolllist.append(entry)

            self.contractlist.ShowHint()
            self.contractlist.Load(contentList=scrolllist, headers=self._GetScrollHeaders())
            if len(scrolllist) == 0:
                self.contractlist.ShowHint(GetByLabel('UI/Contracts/ContractEntry/NoContractsFound'))
            self.UpdatePagination(contracts, scrolllist)
        except UserError:
            self.contractlist.ShowHint(GetByLabel('UI/Contracts/ContractEntry/NoContractsFound'))
            raise

    def PrimeOwnerIDs(self, contracts):
        ownerIDs = set()
        for contract in contracts:
            ownerIDs.add(contract.issuerID)
            ownerIDs.add(contract.issuerCorpID)
            ownerIDs.add(contract.acceptorID)
            ownerIDs.add(contract.assigneeID)

        if 0 in ownerIDs:
            ownerIDs.remove(0)
        cfg.eveowners.Prime(ownerIDs)

    def UpdatePagination(self, contracts, scrolllist):
        if len(contracts) >= 2:
            self.pages[self.currPage] = contracts[0].contractID
            self.pages[self.currPage + 1] = contracts[-1].contractID
        if len(scrolllist) < RESULTS_PER_PAGE or self.GetStatusFilterValue() == appConst.conStatusRequiresAttention:
            self.transMyFwdBtn.Disable()
        else:
            self.transMyFwdBtn.Enable()

    def _GetScrollHeaders(self):
        filtStatus = self.GetStatusFilterValue()
        headers = [GetByLabel('UI/Common/Contract'),
         GetByLabel('UI/Common/Type'),
         GetByLabel('UI/Common/From'),
         GetByLabel('UI/Common/To')]
        if filtStatus == appConst.conStatusOutstanding:
            headers.extend([GetByLabel('UI/Contracts/ContractsWindow/DateIssued'), GetByLabel('UI/Contracts/ContractsWindow/TimeLeft')])
        elif filtStatus == appConst.conStatusInProgress:
            headers.extend([GetByLabel('UI/Contracts/ContractsWindow/DateAccepted'), GetByLabel('UI/Contracts/ContractsWindow/TimeLeft')])
        elif filtStatus == appConst.conStatusRequiresAttention:
            headers.extend([GetByLabel('UI/Contracts/ContractsWindow/Status'), GetByLabel('UI/Contracts/ContractsWindow/TimeLeft')])
        else:
            headers.extend([GetByLabel('UI/Contracts/ContractsWindow/Status'), GetByLabel('UI/Contracts/ContractsWindow/DateCompleted')])
        headers.append(GetByLabel('UI/Contracts/ContractsWindow/InfoByIssuer'))
        return headers

    def _GetListEntry(self, contract, contractItems):
        timeLeftValue = 0
        filtStatus = self.GetStatusFilterValue()
        if filtStatus == appConst.conStatusOutstanding:
            issued = {False: FmtDate(contract.dateIssued, 'ss'),
             True: '-'}[contract.type == appConst.conTypeAuction and contract.issuerID != eve.session.charid]
            timeLeftValue = contract.dateExpired - blue.os.GetWallclockTime()
            additionalColumns = '<t>%s<t>%s' % (issued, ConFmtDate(timeLeftValue, contract.type == appConst.conTypeAuction))
        elif filtStatus == appConst.conStatusInProgress:
            timeLeftValue = contract.dateAccepted + appConst.DAY * contract.numDays - blue.os.GetWallclockTime()
            additionalColumns = '<t>%s<t>%s' % (FmtDate(contract.dateAccepted, 'ss'), ConFmtDate(timeLeftValue, contract.type == appConst.conTypeAuction))
        elif filtStatus == appConst.conStatusRequiresAttention:
            if contract.acceptorID == session.charid:
                timeLeftText = GetByLabel('UI/Journal/JournalWindow/Contracts/Overdue')
            else:
                timeLeftText = GetByLabel('UI/Contracts/Util/ContractExpired')
            statusText = GetColoredContractStatusText(contract.status)
            additionalColumns = '<t>%s<t><color=red>%s</color>' % (statusText, timeLeftText)
        else:
            additionalColumns = '<t>%s<t>%s' % (GetColoredContractStatusText(contract.status), FmtDate(contract.dateCompleted, 'ss'))
        additionalColumns += '<t>%s' % contract.title
        text = GetContractLabel(contract, contractItems, additionalColumns)
        return GetFromClass(ContractEntrySmall, {'contract': contract,
         'contractItems': contractItems,
         'status': filtStatus,
         'text': text,
         'label': text,
         'additionalColumns': additionalColumns,
         'callback': self.OnSelectContract,
         'sort_%s' % GetByLabel('UI/Common/Contract'): text,
         'sort_%s' % GetByLabel('UI/Contracts/ContractsWindow/DateCompleted'): -contract.dateCompleted,
         'sort_%s' % GetByLabel('UI/Contracts/ContractsWindow/TimeLeft'): timeLeftValue})

    def _GetContractsToShow(self, ownerID):
        issuedBy = self.GetIssuedByToFilterValue()
        filtStatus = self.GetStatusFilterValue()
        contractType = self.GetContractTypeFilterValue()
        startContractID = self.pages.get(self.currPage, None)
        if filtStatus == appConst.conStatusRequiresAttention:
            _contracts = self._GetRequireAttentionContractsToShow(ownerID)
        elif filtStatus == appConst.conStatusBidOnBy:
            forCorp = ownerID == session.corpid
            _contracts = sm.GetService('contracts').GetMyBids(forCorp).list
        else:
            _contracts = sm.ProxySvc('contractProxy').GetContractListForOwner(ownerID, filtStatus, contractType, issuedBy, num=RESULTS_PER_PAGE, startContractID=startContractID)
        return (_contracts.contracts, _contracts.items)

    def _GetRequireAttentionContractsToShow(self, ownerID):
        _contracts = sm.GetService('contracts').GetMyExpiredContractList()
        if ownerID == session.charid:
            _contracts = _contracts.mySelf
        else:
            _contracts = _contracts.myCorp
        return _contracts

    def GetIssuedByToFilterValue(self):
        return self.fltToFrom.GetValue()

    def GetContractTypeFilterValue(self):
        return self.fltType.GetValue()

    def GetStatusFilterValue(self):
        return int(self.fltStatus.GetValue())

    def GetOwnerID(self):
        ownerName = self.GetOwnerFilterValue()
        if ownerName == cfg.eveowners.Get(eve.session.charid).name:
            return eve.session.charid
        elif ownerName == cfg.eveowners.Get(eve.session.corpid).name:
            return eve.session.corpid
        elif IsSearchStringLongEnough(ownerName):
            return searchOld.Search(ownerName.lower(), None, appConst.categoryOwner, hideNPC=1, exact=1, searchWndName='contractOwnerNameSearch')
        else:
            return None

    def OnComboChange(self, obj, *args):
        if obj == self.fltType and self.GetContractTypeFilterValue() == -1:
            self.fltType.SetValue(None)

    def OnSelectContract(self, *args):
        pass

    def ShowOwner(self, ownerName):
        self._SetFiltersAndFetch(ownerName, appConst.conStatusFinished)

    def ShowRequireAttention(self, status):
        ownerName = cfg.eveowners.Get(session.charid).name
        self._SetFiltersAndFetch(ownerName, status)

    def ShowRequireAttentionMyCorp(self, status):
        ownerName = cfg.eveowners.Get(session.corpid).name
        self._SetFiltersAndFetch(ownerName, status)

    def _SetFiltersAndFetch(self, ownerName, status = None, toFrom = None, contractType = None):
        self.fltToFrom.SetValue(toFrom)
        self.fltOwner.SetValue(ownerName)
        self.fltStatus.SelectItemByValue(status)
        self.fltType.SelectItemByValue(contractType)
        self.FetchContracts()
