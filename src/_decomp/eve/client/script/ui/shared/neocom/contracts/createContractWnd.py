#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\contracts\createContractWnd.py
from __future__ import absolute_import
import math
import sys
import evetypes
import utillib
from carbon.common.script.util import timerstuff
from carbon.common.script.util.format import FmtAmt, FmtDate
from carbonui.control.combo import Combo
from carbonui.util.various_unsorted import SortListOfTuples
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.universe import SolarSystem
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.shared.neocom.contracts.contractentry import ContractItemSelect
from eve.client.script.ui.util import uix
import uthread
import log
import blue
from bannedwords.client import bannedwords
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui import uiconst
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.line import Line
from carbonui.primitives.container import Container
from contracts.contractStruct import ContractStruct
from contracts.copyContracts import CopyContractObject, GetMissingTypesTxt, FindMissingBlueprints, FindMissingTypesAndQty
from eve.client.script.ui.control import eveEdit, eveLabel, eveScroll
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.control.listwindow import ListWindow
from eve.client.script.ui.util import searchUtil, searchOld
from eve.client.script.ui.util.form import FormWnd
from eve.client.script.util.contractutils import FmtISKWithDescription, GetContractIcon, IsSearchStringLongEnough, MatchInvTypeName, SelectItemTypeDlg, TypeName
from eve.common.script.search import const as search_const
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.util.contractscommon import CREATECONTRACT_CONFIRM_CHARGESTOHANGAR, CalcContractFees, CanRequestType, EXPIRE_TIMES, GetContractTypeText, MAX_AMOUNT, MAX_NUM_CONTRACTS, MAX_NUM_ITEMS, MAX_TITLE_LENGTH, NUM_CONTRACTS_BY_SKILL, NUM_CONTRACTS_BY_ADVSKILL, NUM_CONTRACTS_BY_SKILL_CORP, const_conBidMinimum, const_conBrokersFeeMinimum, const_conCourierMaxVolume, const_conCourierWarningVolume, const_conDepositMinimum, const_conSalesTax
from eve.common.script.util.eveFormat import FmtISK, RoundISK
from eveexceptions import UserError
from evePathfinder.pathfinderconst import UNREACHABLE_JUMP_COUNT
from globalConfig.getFunctions import GetMaxShipsToContract
from inventorycommon.typeHelpers import GetAveragePrice
from inventorycommon.const import categoryStructure, groupStation, typeBrokerRelations, typeAccounting
from inventorycommon.util import GetItemVolume, IsNPC
from localization import GetByLabel
from menu import MenuLabel
from structures.types import IsFlexStructure
from threadutils import throttled
MIN_CONTRACT_MONEY = 1000

class CreateContractWnd(Window):
    __guid__ = 'form.CreateContract'
    __notifyevents__ = ['OnDeleteContract']
    default_windowID = 'createcontract'
    default_iconNum = 'res:/ui/Texture/WindowIcons/contracts.png'
    default_captionLabelPath = 'UI/Inventory/ItemActions/CreateContract'
    default_minSize = (410, 520)

    def ApplyAttributes(self, attributes):
        super(CreateContractWnd, self).ApplyAttributes(attributes)
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=42)
        self.ResetWizard()
        contractItems = attributes.contractItems
        copyContract = attributes.copyContract
        copyContractCorpFlagID = attributes.copyContractDisvision
        stationID = attributes.stationID
        flag = attributes.flag
        itemIDs = attributes.itemIDs
        if stationID and not self.CanContractItemsFromLocation(stationID):
            stationID = None
        if stationID:
            self.data.startStation = stationID
            self.data.startStationDivision = const.flagHangar
        if flag:
            self.data.startStationDivision = flag
        if attributes.contractType:
            self.data.type = attributes.contractType
        else:
            self.contractType = const.conTypeNothing
        self.isMultiContract = False
        self.data.items = {}
        self.data.childItems = {}
        if stationID and itemIDs:
            foundItems = []
            itemsInStation = sm.GetService('contracts').GetItemsInDockableLocation(self.data.startStation, False)
            for item in itemsInStation:
                if item.itemID in itemIDs:
                    foundItems.append(item)

            if foundItems:
                self.data.startStationDivision = foundItems[0].flagID
                for item in foundItems:
                    self.data.items[item.itemID] = [item.typeID, item.stacksize, item]

        self.currPage = 0
        self.NUM_STEPS = 4
        self.CREATECONTRACT_TITLES = {const.conTypeNothing: [GetByLabel('UI/Contracts/ContractsWindow/SelectContractType'),
                                '',
                                '',
                                ''],
         const.conTypeAuction: [GetByLabel('UI/Contracts/ContractsWindow/SelectContractType'),
                                GetByLabel('UI/Contracts/ContractsWindow/PickItems'),
                                GetByLabel('UI/Contracts/ContractsWindow/SelectOptions'),
                                GetByLabel('UI/Common/Confirm')],
         const.conTypeItemExchange: [GetByLabel('UI/Contracts/ContractsWindow/SelectContractType'),
                                     GetByLabel('UI/Contracts/ContractsWindow/PickItems'),
                                     GetByLabel('UI/Contracts/ContractsWindow/SelectOptions'),
                                     GetByLabel('UI/Common/Confirm')],
         const.conTypeCourier: [GetByLabel('UI/Contracts/ContractsWindow/SelectContractType'),
                                GetByLabel('UI/Contracts/ContractsWindow/PickItems'),
                                GetByLabel('UI/Contracts/ContractsWindow/SelectOptions'),
                                GetByLabel('UI/Common/Confirm')]}
        self.isContractMgr = eve.session.corprole & const.corpRoleContractManager == const.corpRoleContractManager
        self.marketTypes = sm.GetService('contracts').GetMarketTypes()
        self.sr.pageWnd = {}
        self.lockedItems = {}
        self.state = uiconst.UI_NORMAL
        self.blockconfirmonreturn = 1
        setattr(self, 'first', True)
        if contractItems is not None:
            self._SetStartVariablesInData(contractItems)
        self.buttons = [(GetByLabel('UI/Common/Cancel'),
          self.OnCancel,
          (),
          84), (GetByLabel('UI/Common/Previous'),
          self.OnStepChange,
          -1,
          84), (GetByLabel('UI/Common/Next'),
          self.OnStepChange,
          1,
          84)]
        self.sr.buttonWnd = ButtonGroup(btns=self.buttons, parent=self.sr.main)
        self.sr.buttonCancel = self.sr.buttonWnd.buttons[0]
        self.sr.buttonPrev = self.sr.buttonWnd.buttons[1]
        self.sr.buttonNext = self.sr.buttonWnd.buttons[2]
        if copyContract:
            self.CopyContract(copyContract, copyContractCorpFlagID)
        self.formWnd = FormWnd(name='form', align=uiconst.TOALL, pos=(0, 0, 0, 0), parent=self.sr.main)
        self.GotoPage(0)

    def SetMainIcon(self, texturePath):
        self.icon = texturePath

    def _SetStartVariablesInData(self, contractItems):
        firstItem = contractItems[0]
        startStation = sm.StartService('invCache').GetStationIDOfItem(firstItem)
        if not self.CanContractItemsFromLocation(startStation):
            return
        self.data.startStation = startStation
        dataItems = {}
        for item in contractItems:
            dataItems[item.itemID] = [item.typeID, item.stacksize, item]
            if item.ownerID == session.corpid:
                if not self.isContractMgr:
                    raise UserError('ConNotContractManager')
                self.data.forCorp = True
                self.data.startStation = sm.StartService('invCache').GetStationIDOfItem(item)
                self.data.startStationDivision = item.flagID
            elif item.ownerID != session.charid:
                raise RuntimeError('Not your item!')

        self.data.items = dataItems

    def CopyContract(self, contract, corpFlagID = None):
        c = contract.contract
        self.data.type = c.type
        self.data.startStation = c.startStationID
        self.data.endStation = c.endStationID
        expireTime = 1440 * ((c.dateExpired - c.dateIssued) / const.DAY)
        self.data.expiretime = expireTime
        self.data.duration = c.numDays
        self.data.description = c.title
        self.data.assigneeID = c.assigneeID
        if c.availability == 0:
            self.data.avail = 0
        elif c.assigneeID == session.corpid:
            self.data.avail = 2
            self.data.assigneeID = None
        elif session.allianceid and c.assigneeID == session.allianceid:
            self.data.avail = 3
            self.data.assigneeID = None
        else:
            self.data.avail = 1
        if self.data.assigneeID:
            self.data.name = cfg.eveowners.Get(self.data.assigneeID).name
        self.data.price = c.price
        self.data.reward = c.reward
        self.data.collateral = c.collateral
        self.data.forCorp = c.forCorp
        self.data.reqItems = {}
        if self.data.type == const.conTypeCourier:
            uthread.new(eve.Message, 'ConCopyContractCourier')
        itemsInContract = contract.items
        if not itemsInContract:
            return
        copyContractsObject = CopyContractObject(startStation=self.data.startStation, forCorp=self.data.forCorp, contractItems=itemsInContract, getItemsInStationFunc=sm.GetService('contracts').GetItemsInDockableLocation, corpFlagID=corpFlagID)
        sellItems, sellBlueprintCopies, sellBlueprintOriginals, requestItems = copyContractsObject.GetSellAndRequestedItems()
        foundBlueprint = sellBlueprintCopies or sellBlueprintOriginals
        self.data.reqItems = dict(requestItems)
        self.data.items = {}
        self.data.childItems = {}
        if sellItems or sellBlueprintCopies or sellBlueprintOriginals:
            foundItems, foundBPC, foundBPO = copyContractsObject.FindItemToSellInHangar(sellItems, sellBlueprintCopies, sellBlueprintOriginals)
            notFound = FindMissingTypesAndQty(foundItems, sellItems)
            notFoundBPCs = FindMissingBlueprints(foundBPC, sellBlueprintCopies)
            notFoundBPOs = FindMissingBlueprints(foundBPO, sellBlueprintOriginals)
            if notFound or notFoundBPCs or notFoundBPOs:
                missintTypesTxt = GetMissingTypesTxt(notFound)
                missintTypesTxt += GetMissingTypesTxt(notFoundBPCs)
                missintTypesTxt += GetMissingTypesTxt(notFoundBPOs)
                uthread.new(eve.Message, 'ConCopyContractMissingItems', {'types': missintTypesTxt})
            allFoundItems = []
            for eachDict in (foundItems, foundBPC, foundBPO):
                for eachItemList in eachDict.itervalues():
                    allFoundItems += eachItemList

            if allFoundItems:
                self.data.startStationDivision = allFoundItems[0].flagID
                for item in allFoundItems:
                    self.data.items[item.itemID] = [item.typeID, item.stacksize, item]

        if foundBlueprint:
            uthread.new(eve.Message, 'ConCopyContractBlueprint')

    def _OnClose(self, *args):
        self.UnlockItems()

    def Refresh(self):
        self.GotoPage(self.currPage)

    def Confirm(self, *args):
        pass

    def SetTitle(self):
        pageTitle = self.CREATECONTRACT_TITLES[self.data.type][self.currPage]
        titleLabel = GetByLabel('UI/Contracts/ContractsService/PageOfTotal', pageTitle=pageTitle, pageNum=self.currPage + 1, numPages=self.NUM_STEPS)
        title = titleLabel
        if self.sr.Get('windowCaption', None) is None:
            self.sr.windowCaption = eveLabel.EveCaptionMedium(parent=self.topParent, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, text=title)
        else:
            self.sr.windowCaption.text = title

    def UnlockItems(self):
        if not hasattr(self, 'lockedItems'):
            return
        for i in self.lockedItems.iterkeys():
            sm.StartService('invCache').UnlockItem(i)

        self.lockedItems = {}

    def LockItems(self, itemIDs):
        for i, item in itemIDs.iteritems():
            self.lockedItems[i] = i
            userErrorDict = {'typeID': item[0],
             'action': GetByLabel('UI/Contracts/ContractsWindow/CreatingContract').lower()}
            sm.StartService('invCache').TryLockItem(i, 'lockItemContractFunction', userErrorDict, 1)

    def GotoPage(self, n):
        uthread.Lock(self)
        try:
            if n < 2:
                self.UnlockItems()
            self.currPage = n
            self.SetTitle()
            for p in self.sr.pageWnd:
                self.sr.pageWnd[p].state = uiconst.UI_HIDDEN

            self.formWnd.Flush()
            format = []
            self.form = retfields = reqresult = errorcheck = []
            self.sr.buttonNext.SetLabel(GetByLabel('/Carbon/UI/Common/Next'))
            self.sr.buttonPrev.state = uiconst.UI_NORMAL
            contractIconType = const.conTypeNothing if n == 0 else self.data.type
            self.SetMainIcon(GetContractIcon(contractIconType))
            if n == 0:
                retfields, reqresult, errorcheck = self.BuildPage0()
            elif n == 1:
                self.WriteSelectItems(GetByLabel('UI/Contracts/ContractsWindow/SelectStationToGetItems'))
            elif n == 2:
                errorcheck, reqresult, retfields = self.BuildPage2()
            elif n == 3:
                self.BuildPage3()
            self.formdata = [retfields, reqresult, errorcheck]
        finally:
            uthread.UnLock(self)

    def BuildPage0(self):
        self.sr.buttonPrev.state = uiconst.UI_HIDDEN
        format = []
        format += self.Page0_GetContractTypeOptions()
        s = [0,
         0,
         0,
         0]
        s[getattr(self.data, 'avail', 0)] = 1
        format += self.Page0_GetAvailabilityOptions(s)
        forCorp = getattr(self.data, 'forCorp', 0)
        if self.isContractMgr:
            corpAcctName = sm.GetService('corp').GetMyCorpAccountName() or GetByLabel('UI/Common/None')
            behalfLabel = GetByLabel('UI/Contracts/ContractsService/OnBehalfOfCorp', corpName=cfg.eveowners.Get(eve.session.corpid).name, corpAccountName=corpAcctName)
            format += [{'type': 'btline'}]
            format += [{'type': 'checkbox',
              'label': '_hide',
              'key': 'forCorp',
              'text': behalfLabel,
              'required': 1,
              'frame': 0,
              'setvalue': forCorp,
              'onchange': self.OnForCorpChange}]
        else:
            format += [{'type': 'data',
              'key': 'forCorp',
              'data': {'forCorp': 0}}]
        uthread.new(self.WriteNumContractsAndLimitsLazy)
        limitsParent = Container(name='limitsParent', parent=self.formWnd, align=uiconst.TOBOTTOM, height=10, idx=0, padBottom=8)
        outstandingContractsLabel = GetByLabel('UI/Contracts/ContractsService/OutstandingContractsUnknown')
        labelText = '<color=0xff999999>%s</color>' % outstandingContractsLabel
        self.limitTextWnd = eveLabel.EveLabelSmall(text=labelText, parent=limitsParent, left=6, state=uiconst.UI_DISABLED)
        self.form, retfields, reqresult, self.panels, errorcheck, refresh = sm.GetService('form').GetForm(format, self.formWnd)
        nameEditField = self.form.FindChild('edit_name')
        privateCheckbox = self.form.FindChild('privateCb')
        if nameEditField and privateCheckbox:
            nameEditField.OnChange = lambda *args: self.OnChangePrivateName(privateCheckbox, *args)
        fittedShipsCb = self.form.FindChild('contractTypeCb_fittedShip')
        if fittedShipsCb:
            self.SetFittedShipsCbEnableState(self.data.type or const.conTypeItemExchange)
            fittedShipsCb.padLeft = 16
            fittedShipsCb.hint = GetByLabel('UI/Contracts/FittedShipsHint')
        return (retfields, reqresult, errorcheck)

    def Page0_GetContractTypeOptions(self):
        selected = self.data.type
        if selected == const.conTypeNothing:
            selected = const.conTypeItemExchange
        selectedOptions = [selected]
        if self.IsFittedShipContract(selected):
            selectedOptions = [selected, 'fittedShip']

        def GetFormatLine(conType, textPath, required = 1, group = 'type'):
            return {'type': 'checkbox',
             'label': '_hide',
             'key': conType,
             'text': GetByLabel(textPath),
             'required': required,
             'frame': 0,
             'setvalue': conType in selectedOptions,
             'group': group,
             'OnChange': self.OnContractTypeOptionChanged,
             'name': 'contractTypeCb_%s' % conType}

        format = [{'type': 'header',
          'text': GetByLabel('UI/Contracts/ContractType')}]
        format += [GetFormatLine(const.conTypeAuction, 'UI/Contracts/Auction')]
        format += [GetFormatLine(const.conTypeCourier, 'UI/Contracts/ContractsWindow/Courier')]
        format += [GetFormatLine(const.conTypeItemExchange, 'UI/Contracts/ContractsWindow/ItemExchange')]
        if GetMaxShipsToContract(sm.GetService('machoNet')):
            format += [GetFormatLine('fittedShip', 'UI/Contracts/ContractsWindow/AssembledShips', 0, None)]
        format += [{'type': 'btline'}]
        return format

    def OnContractTypeOptionChanged(self, cb, *args):
        self.SetFittedShipsCbEnableState(cb.GetSettingsKey())

    def SetFittedShipsCbEnableState(self, cbConType):
        fittedShipsCb = self.form.FindChild('contractTypeCb_fittedShip')
        if fittedShipsCb:
            if cbConType in (const.conTypeItemExchange, 'fittedShip'):
                fittedShipsCb.Enable()
            else:
                fittedShipsCb.Disable()

    def Page0_GetAvailabilityOptions(self, s):
        n = getattr(self.data, 'name', '')

        def ChangeSearchBy(combo, *args):
            combo.UpdateSettings()

        searchTypePrefsKey = ('char', 'ui', 'contracts_searchNameBy')
        selectSearchBy = settings.char.ui.Get('contracts_searchNameBy', search_const.MatchBy.partial_terms)
        f = [{'type': 'header',
          'text': GetByLabel('UI/Contracts/ContractsWindow/Availability')},
         {'type': 'checkbox',
          'label': '_hide',
          'key': 0,
          'text': GetByLabel('UI/Generic/Public'),
          'required': 1,
          'frame': 0,
          'setvalue': s[0],
          'group': 'avail',
          'onchange': self.OnAvailChange},
         {'type': 'checkbox',
          'label': '_hide',
          'key': 1,
          'text': GetByLabel('UI/Generic/Private'),
          'required': 1,
          'frame': 0,
          'setvalue': s[1],
          'group': 'avail',
          'onchange': self.OnAvailChange,
          'name': 'privateCb'},
         {'type': 'edit',
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsService/IndentedName'),
          'key': 'name',
          'required': 0,
          'frame': 0,
          'setvalue': n,
          'group': 'name',
          'isCharCorpOrAllianceField': True},
         {'type': 'combo',
          'width': 120,
          'label': GetByLabel('UI/Common/SearchBy'),
          'key': 'searchBy',
          'options': searchUtil.GetSearchByChoices(),
          'setvalue': selectSearchBy,
          'group': 'name',
          'callback': ChangeSearchBy,
          'prefskey': searchTypePrefsKey}]
        if not idCheckers.IsNPC(session.corpid):
            f += [{'type': 'checkbox',
              'label': '_hide',
              'key': 2,
              'text': GetByLabel('UI/Contracts/ContractsWindow/MyCorporation'),
              'required': 1,
              'frame': 0,
              'setvalue': s[2],
              'group': 'avail',
              'onchange': self.OnAvailChange}]
        if session.allianceid:
            f += [{'type': 'checkbox',
              'label': '_hide',
              'key': 3,
              'text': GetByLabel('UI/Contracts/ContractsWindow/MyAlliance'),
              'required': 1,
              'frame': 0,
              'setvalue': s[3],
              'group': 'avail',
              'onchange': self.OnAvailChange}]
        return f

    def BuildPage2(self):
        retfields = reqresult = errorcheck = []
        duration, expireTime, expireTimeOptions = self.GetDurationAndExpireTimes()
        contractType = self.data.type
        if contractType == const.conTypeAuction:
            errorcheck, reqresult, retfields = self.BuildPage2_AddAuctionOption(expireTime, expireTimeOptions, errorcheck, reqresult, retfields)
        elif self.IsFittedShipContract(contractType):
            errorcheck, reqresult, retfields = self.BuildPage2_AddFittedShipOptions(expireTime, expireTimeOptions)
        elif contractType == const.conTypeItemExchange:
            errorcheck, reqresult, retfields = self.BuildPage2_AddItemExchangeOptions(expireTime, expireTimeOptions)
        elif contractType == const.conTypeCourier:
            errorcheck, reqresult, retfields = self.BuildPage2_AddCourierOptions(duration, expireTime, expireTimeOptions)
        return (errorcheck, reqresult, retfields)

    def GetDurationAndExpireTimes(self):
        expireTime = getattr(self.data, 'expiretime', None)
        if expireTime is None:
            expireTime = settings.char.ui.Get('contracts_expiretime_%s' % self.data.type, 1440)
        duration = getattr(self.data, 'duration', None)
        if duration is None:
            duration = settings.char.ui.Get('contracts_duration_%s' % self.data.type, 1)
        expireTimeOptions = []
        for t in EXPIRE_TIMES:
            num = numDays = t / 1440
            txt = GetByLabel('UI/Contracts/ContractsService/QuantityDays', numDays=num)
            numWeeks = t / 10080
            if numWeeks >= 1:
                num = numWeeks
                txt = GetByLabel('UI/Contracts/ContractsService/QuantityWeeks', numWeeks=num)
            expireTimeOptions.append((txt, t))

        return (duration, expireTime, expireTimeOptions)

    def BuildPage2_AddAuctionOption(self, expireTime, expireTimeOptions, errorcheck, reqresult, retfields):
        del expireTimeOptions[-1]
        format = [{'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsWindow/StartingBid'),
          'key': 'price',
          'autoselect': 1,
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'floatonly': [0, MAX_AMOUNT, 2],
          'setvalue': getattr(self.data, 'price', 0)},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsWindow/BuyoutPriceOptional'),
          'key': 'collateral',
          'autoselect': 1,
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'floatonly': [0, MAX_AMOUNT, 2],
          'setvalue': getattr(self.data, 'collateral', 0)},
         {'type': 'push'},
         {'type': 'combo',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsWindow/AuctionTime'),
          'key': 'expiretime',
          'options': expireTimeOptions,
          'setvalue': getattr(self.data, 'expiretime', expireTime)},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 220,
          'label': GetByLabel('UI/Contracts/ContractEntry/DescriptionOptional'),
          'key': 'description',
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'setvalue': getattr(self.data, 'description', '')}]
        self.form, retfields, reqresult, self.panels, errorcheck, refresh = sm.GetService('form').GetForm(format, self.formWnd)
        btnparent = Container(name='btnparent', parent=self.formWnd.sr.price.parent, align=uiconst.TOALL, padLeft=const.defaultPadding)
        Button(parent=btnparent, label=GetByLabel('UI/Contracts/ContractsWindow/EstPrice'), func=self.SetPriceToEstPrice, btn_default=0, align=uiconst.CENTERLEFT)
        return (errorcheck, reqresult, retfields)

    def BuildPage2_AddItemExchangeOptions(self, expireTime, expireTimeOptions):
        isRequestItems = not not self.data.reqItems
        format = [{'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractEntry/IWillPay'),
          'key': 'reward',
          'autoselect': 1,
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'floatonly': [0, MAX_AMOUNT, 2],
          'setvalue': getattr(self.data, 'reward', 0)},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractEntry/IWillRecieve'),
          'key': 'price',
          'autoselect': 1,
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'floatonly': [0, MAX_AMOUNT, 2],
          'setvalue': getattr(self.data, 'price', 0)},
         {'type': 'push'},
         {'type': 'combo',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsWindow/Expiration'),
          'key': 'expiretime',
          'options': expireTimeOptions,
          'setvalue': getattr(self.data, 'expiretime', expireTime)},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 220,
          'label': GetByLabel('UI/Contracts/ContractEntry/DescriptionOptional'),
          'key': 'description',
          'required': 0,
          'frame': 0,
          'maxLength': 50,
          'group': 'avail',
          'setvalue': getattr(self.data, 'description', '')},
         {'type': 'push',
          'height': 10},
         {'type': 'checkbox',
          'required': 1,
          'height': 16,
          'setvalue': isRequestItems,
          'key': 'requestitems',
          'label': '',
          'text': GetByLabel('UI/Contracts/ContractsWindow/AlsoReqItemsFromBuyer'),
          'frame': 0,
          'onchange': self.OnRequestItemsChange}]
        self.form, retfields, reqresult, self.panels, errorcheck, refresh = sm.GetService('form').GetForm(format, self.formWnd)
        self.sr.reqItemsParent = reqItemsParent = Container(name='reqItemsParent', parent=self.formWnd, align=uiconst.TOALL, pos=(0, 0, 0, 0), idx=50)
        left = const.defaultPadding + 3
        top = 16
        self.reqItemTypeWnd = c = SingleLineEditText(name='itemtype', parent=reqItemsParent, label=GetByLabel('UI/Contracts/ContractsWindow/ItemType'), align=uiconst.TOPLEFT, width=248, isTypeField=True)
        c.OnFocusLost = self.ParseItemType
        c.left = left
        c.top = top
        left += c.width + 5
        self.reqItemQtyWnd = c = SingleLineEditInteger(name='itemqty', parent=reqItemsParent, label=GetByLabel('UI/Inventory/ItemQuantity'), align=uiconst.TOPLEFT, width=50, setvalue=1)
        c.left = left
        c.top = top
        left += c.width + 5
        c = Button(parent=reqItemsParent, label=GetByLabel('UI/Contracts/ContractEntry/AddItem'), func=self.AddRequestItem, pos=(left,
         top,
         0,
         0), align=uiconst.TOPLEFT)
        c.top = top
        self.reqItemScroll = eveScroll.Scroll(parent=reqItemsParent, padding=(const.defaultPadding,
         top + c.height + const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.reqItemScroll.sr.id = 'reqitemscroll'
        self.PopulateReqItemScroll()
        btnparent = Container(name='btnparent', parent=self.formWnd.sr.price.parent, align=uiconst.TOALL, padLeft=const.defaultPadding)
        Button(parent=btnparent, label=GetByLabel('UI/Contracts/ContractsWindow/EstPrice'), func=self.SetPriceToEstPrice, btn_default=0, align=uiconst.CENTERLEFT)
        self.ToggleShowRequestItems(isRequestItems)
        return (errorcheck, reqresult, retfields)

    def BuildPage2_AddFittedShipOptions(self, expireTime, expireTimeOptions):
        text = GetByLabel('UI/Contracts/ContractsWindow/AssembledShipOptionText', numShips=len(self.data.items))
        eveLabel.EveLabelMedium(text=text, parent=self.formWnd, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, padding=(7, 0, 7, 0))
        format = [{'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractEntry/IWillRecieve'),
          'key': 'price',
          'autoselect': 1,
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'floatonly': [0, MAX_AMOUNT, 2],
          'setvalue': getattr(self.data, 'price', 0)},
         {'type': 'push'},
         {'type': 'combo',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsWindow/Expiration'),
          'key': 'expiretime',
          'options': expireTimeOptions,
          'setvalue': getattr(self.data, 'expiretime', expireTime)},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 220,
          'label': GetByLabel('UI/Contracts/ContractEntry/DescriptionOptional'),
          'key': 'description',
          'required': 0,
          'frame': 0,
          'maxLength': 50,
          'group': 'avail',
          'setvalue': getattr(self.data, 'description', '')},
         {'type': 'push',
          'height': 10}]
        self.form, retfields, reqresult, self.panels, errorcheck, refresh = sm.GetService('form').GetForm(format, self.formWnd)
        return (errorcheck, reqresult, retfields)

    def BuildPage2_AddCourierOptions(self, duration, expireTime, expireTimeOptions):
        if not self.data.endStation and len(self.data.items) == 1:
            myItemInfo = self.data.items.values()[0]
            if myItemInfo[0] == const.typePlasticWrap:
                wrapItem = myItemInfo[2]
                endStationID = sm.GetService('contracts').GetEndStationIDForCourierWrapID(wrapItem.itemID)
                if endStationID:
                    self.data.endStation = endStationID
        format = [{'type': 'push'},
         {'type': 'edit',
          'label': GetByLabel('UI/Contracts/ContractsWindow/ShipTo'),
          'labelwidth': 150,
          'width': 120,
          'key': 'endStationName',
          'frame': 0,
          'maxLength': 80,
          'setvalue': ''},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsWindow/Reward'),
          'key': 'reward',
          'autoselect': 1,
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'floatonly': [0, MAX_AMOUNT, 2],
          'setvalue': getattr(self.data, 'reward', 0)},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsWindow/Collateral'),
          'key': 'collateral',
          'autoselect': 1,
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'floatonly': [0, MAX_AMOUNT, 2],
          'setvalue': getattr(self.data, 'collateral', 0)},
         {'type': 'push'},
         {'type': 'combo',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsWindow/Expiration'),
          'key': 'expiretime',
          'options': expireTimeOptions,
          'setvalue': expireTime},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 60,
          'label': GetByLabel('UI/Contracts/ContractsWindow/DaysToComplete'),
          'key': 'duration',
          'autoselect': 1,
          'required': 0,
          'frame': 0,
          'group': 'duration',
          'setvalue': duration,
          'intonly': [1, 365]},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 220,
          'label': GetByLabel('UI/Contracts/ContractEntry/DescriptionOptional'),
          'key': 'description',
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'setvalue': getattr(self.data, 'description', '')}]
        self.form, retfields, reqresult, self.panels, errorcheck, refresh = sm.GetService('form').GetForm(format, self.formWnd)
        if self.data.endStation:
            self.SearchStation(self.data.endStation)
        endStationEdit = self.formWnd.sr.endStationName
        endStationEdit.OnFocusLost = self.SearchStationFromEdit
        endStationEdit.isLocationField = True
        endStationEdit.SetValueAfterDragging = self.EndStationSetValueAfterDragging
        btnparent = Container(name='btnparent', parent=endStationEdit.parent, align=uiconst.TOALL, padLeft=const.defaultPadding)
        btn = Button(parent=btnparent, label=GetByLabel('UI/Common/Search'), func=self.SearchStationFromEdit, args=(endStationEdit,), btn_default=0, align=uiconst.CENTERLEFT)
        Line(parent=self.formWnd, align=uiconst.TOTOP, padTop=10)
        self.sr.courierHint = eveLabel.EveLabelSmall(name='courierHint', text='', align=uiconst.TOTOP, parent=self.formWnd, state=uiconst.UI_DISABLED, padding=6)
        self.UpdateCourierHint()
        if not getattr(self, 'courierHint', None):
            self.courierHint = timerstuff.AutoTimer(1000, self.UpdateCourierHint)
        btnparent2 = Container(name='btnparent', parent=self.formWnd.sr.collateral.parent, align=uiconst.TOALL, padLeft=const.defaultPadding)
        btn2 = Button(parent=btnparent2, label=GetByLabel('UI/Contracts/ContractsWindow/EstPrice'), func=self.SetCollateralToEstPrice, btn_default=0, align=uiconst.CENTERLEFT)
        return (errorcheck, reqresult, retfields)

    def EndStationSetValueAfterDragging(self, name, locationID):
        if self.IsDockableLocation(locationID):
            SingleLineEditText.SetValueAfterDragging(self.formWnd.sr.endStationName, name, locationID)
            self.data.endStation = None

    def GetItemQtyLabel(self, iQty, iTypeID):
        return GetByLabel('UI/Contracts/ContractsService/NameXQuantity', typeID=iTypeID, quantity=FmtAmt(iQty))

    def BuildPage3(self):
        contractType = self.data.type
        if hasattr(self.data, 'expiretime'):
            settings.char.ui.Set('contracts_expiretime_%s' % contractType, self.data.expiretime)
        if hasattr(self.data, 'duration'):
            settings.char.ui.Set('contracts_duration_%s' % contractType, self.data.duration)
        rows = []
        contractTypeText = GetContractTypeText(contractType)
        if self.IsFittedShipContract(contractType):
            contractTypeText += ' / %s' % GetByLabel('UI/Contracts/ContractsWindow/AssembledShips')
        rows.append([GetByLabel('UI/Contracts/ContractType'), contractTypeText])
        desc = self.data.description
        if desc == '':
            desc = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/Description'), desc])
        avail = self.data.avail
        a = GetByLabel('UI/Generic/Public')
        if avail > 0:
            a = GetByLabel('UI/Generic/Private')
            assignee = cfg.eveowners.Get(self.data.assigneeID)
            a += ' (<a href=showinfo:%s//%s>%s</a>)' % (assignee.typeID, self.data.assigneeID, assignee.name)
        else:
            regionID = None
            if idCheckers.IsStation(self.data.startStation):
                regionID = cfg.evelocations.Get(self.data.startStation).Station().regionID
            else:
                structureInfo = sm.GetService('structureDirectory').GetStructureInfo(self.data.startStation)
                if structureInfo is not None:
                    regionID = cfg.mapSystemCache.Get(structureInfo.solarSystemID).regionID
            if regionID:
                regionLabel = GetByLabel('UI/Contracts/ContractsService/RegionName', region=regionID)
            else:
                log.LogTraceback('No Region?')
                regionLabel = ''
            a += regionLabel
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/Availability'), a])
        loc = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
        if self.data.startStation:
            loc = cfg.evelocations.Get(self.data.startStation).name
            if idCheckers.IsStation(self.data.startStation):
                startStationTypeID = sm.GetService('ui').GetStationStaticInfo(self.data.startStation).stationTypeID
            else:
                startStationTypeID = sm.GetService('structureDirectory').GetStructureInfo(self.data.startStation).typeID
            loc = GetShowInfoLink(startStationTypeID, loc, self.data.startStation)
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/Location'), loc])
        expireLabel = GetByLabel('UI/Contracts/ContractsService/TimeLeftWithoutCaption', timeLeft=FmtDate(self.data.expiretime * const.MIN + blue.os.GetWallclockTime(), 'ss'), expireTime=FmtDate(self.data.expiretime * const.MIN))
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/Expiration'), expireLabel])
        contractType = self.data.type
        if not self.IsFittedShipContract(contractType):
            rows += self.GetPaymentRows()
        rows.append([])
        if contractType == const.conTypeAuction:
            auctionRows = self.BuildPage3_AddAuctionOptions()
            rows += auctionRows
        elif self.IsFittedShipContract(contractType):
            rows += self.BuildPage3_AddItemExchangeFittedShips()
        elif contractType == const.conTypeItemExchange:
            rows += self.BuildPage3_AddItemExchangeOptions()
        elif contractType == const.conTypeCourier:
            courierRows = self.BuildPage3_AddCourierOptions()
            rows += courierRows
        else:
            raise RuntimeError('Contract type not implemented!')
        self.WriteConfirm(rows)
        self.sr.buttonNext.SetLabel(GetByLabel('UI/Contracts/ContractsWindow/Finish'))

    def GetPaymentRows(self, numContract = 1):
        feeTextAndAmounts = self.GetFeeTextAndAmounts()
        depositText = feeTextAndAmounts['depositText']
        brokersFeeText = feeTextAndAmounts['brokersFeeText']
        salesTaxText = feeTextAndAmounts['salesTaxText']
        if numContract > 1:
            totalDepoitText = FmtISK(numContract * feeTextAndAmounts['depositAmount'], 0)
            totalBrokersFeeText = FmtISK(numContract * feeTextAndAmounts['brokersFeeAmount'], 0)
            totalSalesTaxText = FmtISK(numContract * feeTextAndAmounts['salesTaxAmount'], 0)
            brokersFeeText = GetByLabel('UI/Contracts/ContractsWindow/PerContract', amountText=brokersFeeText, totalText=totalBrokersFeeText, totalColor='red')
            depositText = GetByLabel('UI/Contracts/ContractsWindow/PerContract', amountText=depositText, totalText=totalDepoitText, totalColor='red')
            salesTaxText = GetByLabel('UI/Contracts/ContractsWindow/PerContract', amountText=salesTaxText, totalText=totalSalesTaxText, totalColor='red')
        rows = [[GetByLabel('UI/Contracts/ContractsWindow/SalesTax'), salesTaxText]]
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/BrokersFee'), brokersFeeText])
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/Deposit'), depositText])
        return rows

    def GetFeeTextAndAmounts(self):
        brokersFeeAmount = 0
        depositAmount = 0
        salesTaxAmount = 0
        if self.data.avail > 0:
            salesTax = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
            brokersFeeAmount = const_conBrokersFeeMinimum
            brokersFee = FmtISK(brokersFeeAmount, 0)
            deposit = FmtISK(0.0, 0)
        else:
            skillsSvc = sm.GetService('skills')
            skillLevels = utillib.KeyVal()
            skillLevels.brokerRelations = skillsSvc.GetEffectiveLevel(typeBrokerRelations) or 0
            skillLevels.accounting = skillsSvc.GetEffectiveLevel(typeAccounting) or 0
            ret = CalcContractFees(self.data.Get('price', 0), self.data.Get('reward', 0), self.data.type, self.data.avail, self.data.expiretime, skillLevels, session.solarsystemid2, session.warfactionid)
            salesTaxAmount = ret.salesTaxAmt
            brokersFeeAmount = ret.brokersFeeAmt
            depositAmount = ret.depositAmt
            salesTax = GetByLabel('UI/Contracts/ContractsService/ISKFollowedByPercent', numISK=FmtISK(salesTaxAmount, 0), percentage=ret.salesTax * 100.0)
            if brokersFeeAmount == const_conBrokersFeeMinimum:
                brokersFee = GetByLabel('UI/Contracts/ContractsService/ISKMinimumQuantity', numISK=FmtISK(brokersFeeAmount, 0))
            else:
                brokersFee = GetByLabel('UI/Contracts/ContractsService/ISKFollowedByPercent', numISK=FmtISK(brokersFeeAmount, 0), percentage=ret.brokersFee * 100.0)
            minDeposit = const_conDepositMinimum
            if self.data.type == const.conTypeCourier:
                minDeposit = minDeposit / 10
            if depositAmount == minDeposit:
                deposit = GetByLabel('UI/Contracts/ContractsService/ISKMinimumQuantity', numISK=FmtISK(depositAmount, 0))
            else:
                deposit = GetByLabel('UI/Contracts/ContractsService/ISKFollowedByPercent', numISK=FmtISK(depositAmount, 0), percentage=ret.deposit * 100.0)
            if self.data.type == const.conTypeAuction:
                p = const_conSalesTax - float(skillLevels.accounting) * 0.001
                buyout = self.data.collateral
                if buyout < self.data.Get('price', 0):
                    buyout = MAX_AMOUNT
                ret2 = CalcContractFees(buyout, self.data.Get('reward', 0), self.data.type, self.data.avail, self.data.expiretime, skillLevels, session.solarsystemid2, session.warfactionid)
                maxSalesTax = ret2.salesTaxAmt
                salesTax = GetByLabel('UI/Contracts/ContractsService/PercentOfSalesPriceAtTax', percent=100.0 * p, formattedISKWithUnits=FmtISKWithDescription(maxSalesTax, True))
            elif self.data.type == const.conTypeCourier:
                salesTax = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
        return {'brokersFeeText': brokersFee,
         'depositText': deposit,
         'salesTaxText': salesTax,
         'brokersFeeAmount': brokersFeeAmount,
         'depositAmount': depositAmount,
         'salesTaxAmount': salesTaxAmount}

    def BuildPage3_AddAuctionOptions(self):
        rows = []
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/StartingBid'), FmtISKWithDescription(self.data.price)])
        buyout = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
        if self.data.collateral > 0:
            buyout = FmtISKWithDescription(self.data.collateral)
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/BuyoutPrice'), buyout])
        itemList = []
        for i in self.data.items:
            item = self.data.items[i]
            itemLabel = self.GetItemQtyLabel(item[1], item[0])
            itemList.append(itemLabel)
            chld = self.data.childItems.get(i, [])
            for c in chld:
                childItemLabel = GetByLabel('UI/Contracts/ContractsService/NameXQuantityChild', typeID=c[1], quantity=c[2])
                itemList.append(childItemLabel)

        items = '<br>'.join(itemList)
        rows.append([GetByLabel('UI/Contracts/ContractEntry/ItemsForSale'), items])
        return rows

    def BuildPage3_AddItemExchangeOptions(self):
        rows = [[GetByLabel('UI/Contracts/ContractEntry/IWillPay'), FmtISKWithDescription(self.data.reward)], [GetByLabel('UI/Contracts/ContractEntry/IWillRecieve'), FmtISKWithDescription(self.data.price)]]
        itemList = []
        for i in self.data.items:
            itemLabel = self.GetItemQtyLabel(self.data.items[i][1], self.data.items[i][0])
            itemList.append(itemLabel)
            chld = self.data.childItems.get(i, [])
            for c in chld:
                childItemLabel = GetByLabel('UI/Contracts/ContractsService/NameXQuantityChild', typeID=c[1], quantity=c[2])
                itemList.append(childItemLabel)

        items = '<br>'.join(itemList)
        rows.append([GetByLabel('UI/Contracts/ContractEntry/ItemsForSale'), items])
        listToJoin = []
        for typeID, qty in self.data.reqItems.iteritems():
            labelToAppend = self.GetItemQtyLabel(qty, typeID)
            listToJoin.append(labelToAppend)

        itemStr = '<br>'.join(listToJoin)
        rows.append([GetByLabel('UI/Contracts/ContractEntry/ItemsRequired'), itemStr])
        return rows

    def BuildPage3_AddItemExchangeFittedShips(self):
        numContracts = len(self.data.items)
        rows = []
        rows += self.GetPaymentRows(numContracts)
        pricePerContract = self.data.price
        pricePerContractText = FmtISKWithDescription(pricePerContract)
        if numContracts > 1:
            totalPriceText = FmtISK(numContracts * pricePerContract, 0)
            pricePerContractText = GetByLabel('UI/Contracts/ContractsWindow/PerContract', amountText=pricePerContractText, totalText=totalPriceText, totalColor='green')
        rows += [[GetByLabel('UI/Contracts/ContractEntry/IWillRecieve'), pricePerContractText]]
        rows.append([])
        itemList = []
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/NumberOfContracts'), numContracts])
        numByContainerItemIDs = getattr(self.data, 'numByContainerItemIDs', {})
        for itemID, item in self.data.items.iteritems():
            iTypeID, iQty, iRow = item
            if iQty > 1:
                itemLabel = self.GetItemQtyLabel(iQty, iTypeID)
            else:
                itemLabel = evetypes.GetName(iTypeID)
            shipLocationData = cfg.evelocations.GetIfExists(itemID)
            if shipLocationData:
                itemLabel += ' (%s)' % shipLocationData.name
            numContained = numByContainerItemIDs.get(itemID, 0)
            if numContained:
                itemLabel += '<br><font color=grey>%s</font>' % GetByLabel('UI/Contracts/ContractsWindow/ContainsItemsPostText', numItems=numContained)
            itemList.append('<li>%s</li>' % itemLabel)

        items = ''.join(itemList)
        if items:
            items = '<ol>%s</ol>' % items
        rows.append([GetByLabel('UI/Contracts/ContractEntry/ItemsForSale'), items])
        return rows

    def BuildPage3_AddCourierOptions(self):
        rows = []
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/Reward'), FmtISKWithDescription(self.data.reward)])
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/Collateral'), FmtISKWithDescription(self.data.collateral)])
        loc = ''
        if self.data.startStation:
            loc = cfg.evelocations.Get(self.data.endStation).name
            if idCheckers.IsStation(self.data.endStation):
                typeID = sm.GetService('ui').GetStationStaticInfo(self.data.endStation).stationTypeID
            else:
                typeID = sm.GetService('structureDirectory').GetStructureInfo(self.data.endStation).typeID
            loc = GetShowInfoLink(typeID, loc, itemID=self.data.endStation)
        rows.append([GetByLabel('UI/Common/Destination'), loc])
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/DaysToComplete'), self.data.duration])
        volume = 0
        for i in self.data.items:
            volume += GetItemVolume(self.data.items[i][2], int(self.data.items[i][1]))

        if 0 < volume < 1:
            significantDigits = 2
            decimalPlaces = int(-math.ceil(math.log10(volume)) + significantDigits)
        else:
            decimalPlaces = 2
        volumeLabel = GetByLabel('UI/Contracts/ContractsWindow/NumericVolume', volume=FmtAmt(volume, showFraction=decimalPlaces))
        rows.append([GetByLabel('UI/Inventory/ItemVolume'), volumeLabel])
        items = ''
        itemList = []
        for i in self.data.items:
            item = self.data.items[i]
            itemLabel = self.GetItemQtyLabel(item[1], item[0])
            itemList.append(itemLabel)
            chld = self.data.childItems.get(i, [])
            for c in chld:
                childItemLabel = GetByLabel('UI/Contracts/ContractsService/NameXQuantityChild', typeID=c[1], quantity=c[2])
                itemList.append(childItemLabel)

        items = '<br>'.join(itemList)
        rows.append([GetByLabel('UI/Contracts/ContractEntry/Items'), items])
        return rows

    def OnChangePrivateName(self, privateCheckbox, text):
        if text:
            privateCheckbox.ToggleState()

    def OnRequestItemsChange(self, chkbox, *args):
        if not chkbox.GetValue():
            self.reqItemScroll.Clear()
            self.data.reqItems = {}
        self.ToggleShowRequestItems(not not chkbox.GetValue())

    def ToggleShowRequestItems(self, isIt):
        self.sr.reqItemsParent.state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][isIt]

    def WriteNumContractsAndLimitsLazy(self):
        try:
            n, maxNumContracts = self.GetNumContractsAndLimits(getattr(self.data, 'forCorp', 0), getattr(self.data, 'assigneeID', 0))
            outstandingLabel = GetByLabel('UI/Contracts/ContractsService/OutstandingContractsDisplay', numContracts=n, maxContracts=maxNumContracts)
            self.limitTextWnd.text = '<color=0xff999999>%s</color>' % outstandingLabel
        except:
            sys.exc_clear()

    def OnForCorpChange(self, wnd, *args):
        self.data.forCorp = wnd.GetValue()
        self.OnAvailChange(None)
        self.data.items = {}

    def OnAvailChange(self, wnd, *args):
        uthread.new(self._OnAvailChange, wnd)

    def _OnAvailChange(self, wnd, *args):
        if self.destroyed:
            return
        if not wnd:
            key = getattr(self.data, 'lastAvailKey', 0)
        else:
            key = wnd.data.get('key')
            self.data.lastAvailKey = key
        if key == 2:
            n, maxNumContracts = self.GetNumContractsAndLimits(getattr(self.data, 'forCorp', 0), eve.session.corpid)
        elif key == 1:
            n, maxNumContracts = self.GetNumContractsAndLimits(getattr(self.data, 'forCorp', 0), getattr(self.data, 'assigneeID', 0))
        else:
            n, maxNumContracts = self.GetNumContractsAndLimits(getattr(self.data, 'forCorp', 0), 0)
        try:
            outstandingLabel = GetByLabel('UI/Contracts/ContractsService/OutstandingContractsDisplay', numContracts=n, maxContracts=maxNumContracts)
            self.limitTextWnd.text = '<color=0xff999999>%s</color>' % outstandingLabel
        except:
            sys.exc_clear()

    def CreateContract(self):
        sm.GetService('loading').ProgressWnd(GetByLabel('UI/Contracts/ContractsWindow/CreatingContract'), '', 2, 10)
        try:
            self.itemsCurrentlyBeingContracted = None
            self.state = uiconst.UI_HIDDEN
            contractType = getattr(self.data, 'type', const.conTypeNothing)
            assigneeID = getattr(self.data, 'assigneeID', 0)
            startStationID = getattr(self.data, 'startStation', 0)
            startStationDivision = getattr(self.data, 'startStationDivision', None)
            endStationID = getattr(self.data, 'endStation', 0)
            forCorp = getattr(self.data, 'forCorp', 0) > 0
            if not forCorp:
                startStationDivision = 4
            price = getattr(self.data, 'price', 0)
            reward = getattr(self.data, 'reward', 0)
            collateral = getattr(self.data, 'collateral', 0)
            expiretime = getattr(self.data, 'expiretime', 0)
            duration = getattr(self.data, 'duration', 0)
            title = getattr(self.data, 'description', '')
            description = getattr(self.data, 'body', '')
            items = []
            itemsReq = map(list, self.data.reqItems.items())
            for i in self.data.items:
                items.append([i, self.data.items[i][1]])

            isPrivate = not not assigneeID
            contractIDs = None
            isMultiContract = self.IsFittedShipContract(contractType)
            expectedNumContracts = len(items) if isMultiContract else 1
            contractInfo = ContractStruct(contractType=contractType, isPrivate=isPrivate, assignedToID=assigneeID, minutesExpire=expiretime, numDays=duration, startStationID=startStationID, destinationID=endStationID, price=price, reward=reward, collateral=collateral, title=title, description=description, itemList=items, startStationDivision=startStationDivision, requestItemTypeList=itemsReq, forCorp=forCorp, multiContract=isMultiContract)
            try:
                if isMultiContract:
                    self.itemsCurrentlyBeingContracted = (expectedNumContracts, {x[0] for x in items})
                    sm.RegisterForNotifyEvent(self, 'OnItemChange')
                    sm.GetService('loading').ProgressWnd(GetByLabel('UI/Contracts/ContractsWindow/CreatingContract'), '%s / %s ' % (0, expectedNumContracts), 2, expectedNumContracts + 2)
                contractIDs = sm.GetService('contracts').CreateContract(contractInfo)
            except UserError as e:
                if e.msg == 'NotEnoughCargoSpace':
                    if eve.Message('ConAskRemoveToHangar', {}, uiconst.YESNO) == uiconst.ID_YES:
                        contractID = sm.GetService('contracts').CreateContract(contractInfo, confirm=CREATECONTRACT_CONFIRM_CHARGESTOHANGAR)
                    else:
                        raise
                elif e.msg == 'ConMultiContractAbortedDueToTidi':
                    contractIDs = e.dict.get('createdContractIDs', [])
                    self.UpdateContractItemsAfterFailedMultiContract()
                    self.ShowCreatedContracts(contractIDs, expectedNumContracts, isMultiContract)
                    raise
                else:
                    raise

            self.ShowCreatedContracts(contractIDs, expectedNumContracts, isMultiContract)
        finally:
            sm.UnregisterForNotifyEvent(self, 'OnItemChange')
            self.state = uiconst.UI_NORMAL
            if self.itemsCurrentlyBeingContracted:
                expectedNumContracts, itemsLeft = self.itemsCurrentlyBeingContracted
                itemsProcessed = expectedNumContracts - len(itemsLeft)
                sub = '%s / %s ' % (itemsProcessed, expectedNumContracts)
                steps = expectedNumContracts + 2
            else:
                sub = ''
                steps = 10
            sm.GetService('loading').ProgressWnd(GetByLabel('UI/Contracts/ContractsWindow/CreatingContract'), sub, steps, steps)
            self.itemsCurrentlyBeingContracted = None

    def ShowCreatedContracts(self, contractIDs, expectedNumContracts = None, isMultiContract = False):
        if contractIDs:
            if len(contractIDs) == 1 or not isMultiContract:
                contractID = contractIDs[0]
                sm.GetService('contracts').ShowContract(contractID)
            else:
                sm.GetService('contracts').ShowManyContracts(contractIDs)
            if expectedNumContracts is None or len(contractIDs) >= expectedNumContracts:
                self.Close()

    def UpdateContractItemsAfterFailedMultiContract(self):
        oldItems = set(self.data.items)
        itemsInStation = sm.GetService('contracts').GetItemsInDockableLocation(self.data.startStation, getattr(self.data, 'forCorp', 0))
        itemIDsInStation = {x.itemID for x in itemsInStation}
        toRemove = oldItems - itemIDsInStation
        for toRemoveID in toRemove:
            self.data.items.pop(toRemoveID)

        self.Refresh()

    def OnItemChange(self, item, change, location):
        itemsCurrentlyBeingContracted = getattr(self, 'itemsCurrentlyBeingContracted', None)
        if not itemsCurrentlyBeingContracted:
            return
        expectedNumContracts, itemsLeft = self.itemsCurrentlyBeingContracted
        if item.itemID in itemsLeft:
            itemsLeft.discard(item.itemID)
        itemsProcessed = expectedNumContracts - len(itemsLeft)
        sm.GetService('loading').ProgressWnd(GetByLabel('UI/Contracts/ContractsWindow/CreatingContract'), '%s / %s ' % (itemsProcessed, expectedNumContracts), 2 + itemsProcessed, expectedNumContracts + 2)

    def WriteConfirm(self, rows):
        body = ''
        for r in rows:
            if r == []:
                body += '<tr><td colspan=2><hr></td></tr>'
            elif len(r) == 1:
                body += '<tr><td colspan=2>%s</td></tr>' % r[0]
            else:
                boldKey = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=r[0])
                val = r[1]
                body += '<tr><td width=100 valign=top>%(key)s</td><td>%(val)s</td></tr>' % {'key': boldKey,
                 'val': val}

        message = '\n              <TABLE width="98%%">%s</TABLE>\n        ' % body
        messageArea = eveEdit.Edit(parent=self.formWnd, readonly=1, hideBackground=1)
        messageArea.SetValue(message)

    def ParseItemType(self, wnd, *args):
        if self.destroyed or getattr(self, 'parsingItemType', False):
            return
        try:
            self.parsingItemType = True
            txt = wnd.GetValue()
            if len(txt) == 0 or not IsSearchStringLongEnough(txt):
                return
            types = []
            for t in self.marketTypes:
                if MatchInvTypeName(txt, t.typeID):
                    if CanRequestType(t.typeID):
                        types.append(t.typeID)

            typeID = SelectItemTypeDlg(types)
            if typeID:
                wnd.SetValue(TypeName(typeID))
                self.parsedItemType = typeID
            return typeID
            self.parsedItemType = typeID
        finally:
            self.parsingItemType = False

    def AddRequestItem(self, *args):
        typeID = getattr(self, 'parsedItemType', None) or self.ParseItemType(self.reqItemTypeWnd)
        self.parsedItemType = None
        if not typeID:
            return
        qty = self.reqItemQtyWnd.GetValue()
        if qty < 1:
            return
        self.data.reqItems[typeID] = qty
        self.reqItemTypeWnd.SetValue('')
        self.reqItemQtyWnd.SetValue(1)
        self.PopulateReqItemScroll()

    def RemoveRequestItem(self, wnd, *args):
        del self.data.reqItems[wnd.sr.node.typeID]
        self.PopulateReqItemScroll()

    def PopulateReqItemScroll(self):
        scrolllist = []
        self.reqItemScroll.Clear()
        for typeID, qty in self.data.reqItems.iteritems():
            typeName = TypeName(typeID)
            data = utillib.KeyVal()
            data.label = GetByLabel('UI/Contracts/ContractsService/NameXQuantity', typeID=typeID, quantity=qty)
            data.typeID = typeID
            data.name = typeName
            data.OnDblClick = self.RemoveRequestItem
            data.GetMenu = self.GetReqItemMenu
            scrolllist.append(GetFromClass(Generic, data))

        self.reqItemScroll.Load(contentList=scrolllist, headers=[])
        if scrolllist == []:
            self.reqItemScroll.ShowHint(GetByLabel('UI/Contracts/ContractsWindow/AddItemsAbove'))
        else:
            self.reqItemScroll.ShowHint()

    def GetReqItemMenu(self, wnd, *args):
        m = [(MenuLabel('UI/Generic/RemoveItem'), self.RemoveRequestItem, (wnd,))]
        return m

    def SearchStationFromEdit(self, editField):
        stationID = editField.draggedValue
        self.SearchStation(stationID)

    @staticmethod
    def GetSearchScrollEntryData(searchResults, resultType):
        entryList = []
        if resultType not in (search_const.ResultType.structure_with_inlined_data, search_const.ResultType.station):
            log.LogWarn('resultType %d not recognized')
            return entryList
        for entry in searchResults:
            if resultType == search_const.ResultType.structure_with_inlined_data:
                itemID = entry.structureID
                solarsystemID = entry.solarSystemID
                typeID = entry.typeID
                name = entry.itemName
            elif resultType == search_const.ResultType.station:
                itemID = entry
                station = cfg.stations.Get(itemID)
                solarsystemID = station.solarSystemID
                typeID = station.stationTypeID
                name = cfg.evelocations.Get(itemID).name
            else:
                continue
            data = {'sublevel': 1,
             'showinfo': True,
             'itemID': itemID,
             'listvalue': (itemID, name),
             'solarSystemID': solarsystemID,
             'typeID': typeID,
             'label': name}
            entryList.append(data)

        return entryList

    def SearchStation(self, stationID = None, *args):
        searchstr = self.form.sr.endStationName.GetValue().strip()
        if stationID is None and not IsSearchStringLongEnough(searchstr):
            return
        if stationID and not self.IsDockableLocation(stationID):
            stationID = None
        if stationID is None:
            with sm.GetService('loading').LoadCycle(GetByLabel('UI/Common/Searching'), GetByLabel('UI/Contracts/ContractsService/LoadingSearchHint', searchStr=searchstr)):
                searchResult = self.SearchGetStationID(searchstr)
                if searchResult is None:
                    return
                stationID, locationName = searchResult
        else:
            locationName = cfg.evelocations.Get(stationID).name
        if stationID:
            self.courierDropLocation = stationID
            self.form.sr.endStationName.SetValue(locationName)
        self.data.endStation = stationID

    def SearchGetStationID(self, searchstr):
        resultsByType = searchUtil.GetResultsByGroupID(searchstr.lower(), [search_const.ResultType.station, search_const.ResultType.structure_with_inlined_data])
        if search_const.ResultType.structure_with_inlined_data in resultsByType:
            resultsByType[search_const.ResultType.structure_with_inlined_data] = [ structureInfo for structureInfo in resultsByType.get(search_const.ResultType.structure_with_inlined_data, []) if self.IsDockableType(structureInfo.typeID) ]
        totalResults = len(resultsByType.get(search_const.ResultType.station, [])) + len(resultsByType.get(search_const.ResultType.structure_with_inlined_data, []))
        if totalResults == 1:
            stationID = resultsByType.get(search_const.ResultType.station, [None])[0]
            if stationID:
                return (stationID, cfg.evelocations.Get(stationID).name)
            else:
                structureInfo = resultsByType.get(search_const.ResultType.structure_with_inlined_data)[0]
                return (structureInfo.structureID, structureInfo.itemName)
        scroll = []
        for resultType, results in resultsByType.iteritems():
            if not results:
                continue
            entryList = self.GetSearchScrollEntryData(results, resultType)
            label = GetByLabel('UI/Common/LocationTypes/Stations') if resultType == search_const.ResultType.station else GetByLabel('UI/Common/LocationTypes/Structures')
            scroll.append(GetFromClass(ListGroup, {'GetSubContent': searchUtil.GetSearchSubContent,
             'label': GetByLabel('UI/Search/UniversalSearch/SectionHeader', resultType=label, numberReturned=len(entryList)),
             'groupItems': (SolarSystem, entryList),
             'id': ('search_cat', resultType),
             'sublevel': 0,
             'showlen': 0,
             'showicon': 'hide',
             'cat': resultType,
             'state': 'locked'}))

        header = GetByLabel('UI/Common/SearchResults')
        top = GetByLabel('UI/Search/UniversalSearch/WindowHeaderNumResults', numResults=totalResults, searchStr=searchstr)
        if totalResults >= search_const.max_result_count:
            top = GetByLabel('UI/Search/UniversalSearch/WindowHeaderOverMax', maxNumber=search_const.max_result_count, searchStr=searchstr)
        return ListWindow.ShowList(scroll, 'generic', header, top, 0, isModal=1, windowName='contractEndpointSearch', lstDataIsGrouped=1, unstackable=1, noContentHint=GetByLabel('UI/Search/UniversalSearch/NoResultsReturned', searchStr=searchstr))

    @staticmethod
    def IsDockableLocation(dockableItemID):
        if idCheckers.IsStation(dockableItemID):
            return True
        structureInfo = sm.GetService('structureDirectory').GetStructureInfo(dockableItemID)
        return structureInfo is not None and not IsNPC(structureInfo.ownerID) and not IsFlexStructure(structureInfo.typeID)

    @staticmethod
    def IsDockableType(typeID):
        if evetypes.GetGroupID(typeID) == groupStation:
            return True
        if evetypes.GetCategoryID(typeID) == categoryStructure:
            if IsFlexStructure(typeID):
                return False
            return True
        return False

    def UpdateCourierHint(self):
        if self.data.endStation and self.data.startStation and self.sr.courierHint and not self.sr.courierHint.destroyed:
            hintList = []
            startSolarSystemID = sm.GetService('contracts').GetSolarSystemIDForStationOrStructure(self.data.startStation)
            endSolarSystemID = sm.GetService('contracts').GetSolarSystemIDForStationOrStructure(self.data.endStation)
            numJumps = sm.GetService('clientPathfinderService').GetAutopilotJumpCount(endSolarSystemID, startSolarSystemID)
            perJump = self.formWnd.sr.reward.GetValue() / (numJumps or 1)
            sec = sm.GetService('contracts').GetRouteSecurityWarning(startSolarSystemID, endSolarSystemID)
            volumeHint = ''
            if numJumps == 0:
                hint = GetByLabel('UI/Contracts/ContractsService/CourierHintNoJumps', numISK=FmtISK(perJump))
            elif numJumps == 1:
                hint = GetByLabel('UI/Contracts/ContractsService/CourierHintOneJump', numISK=FmtISK(perJump))
            else:
                hint = GetByLabel('UI/Contracts/ContractsService/CourierHintManyJumps', numJumps=numJumps, numISK=FmtISK(perJump))
            if numJumps != UNREACHABLE_JUMP_COUNT:
                hintList.append('- ' + hint)
            num, totalVolume = self.GetVolumeOfAllItems()
            if totalVolume:
                perM3 = self.formWnd.sr.reward.GetValue() / totalVolume
                v = FmtAmt(totalVolume, showFraction=1)
                hintList.append('- ' + GetByLabel('UI/Contracts/ContractsService/CourierHintIskM3', volume=v, numISK=FmtISK(perM3)))
            if sec:
                hintList.append('- ' + sec)
            hintText = '<br>'.join(hintList)
            self.sr.courierHint.SetText(hintText)

    def GetNumContractsAndLimits(self, forCorp, assigneeID):
        skills = sm.GetService('skills').GetSkills()
        skillTypeID = [const.typeContracting, const.typeCorporationContracting][forCorp]
        skill = skills.get(skillTypeID, None)
        advSkill = skills.get(const.typeAdvancedContracting, None)
        if skill is None:
            lvl = 0
        else:
            lvl = skill.effectiveSkillLevel
        if advSkill is None:
            advlvl = 0
        else:
            advlvl = advSkill.effectiveSkillLevel
        if forCorp:
            maxNumContracts = NUM_CONTRACTS_BY_SKILL_CORP[lvl]
        else:
            maxNumContracts = NUM_CONTRACTS_BY_SKILL[lvl] + NUM_CONTRACTS_BY_ADVSKILL[advlvl]
        innerCorp = False
        if assigneeID > 0:
            if idCheckers.IsCorporation(assigneeID):
                if assigneeID == eve.session.corpid:
                    innerCorp = True
            elif idCheckers.IsCharacter(assigneeID):
                corpID = sm.RemoteSvc('corpmgr').GetCorporationIDForCharacter(assigneeID)
                if corpID == eve.session.corpid and not idCheckers.IsNPC(eve.session.corpid):
                    innerCorp = True
        n = 0
        try:
            if getattr(self, 'numOutstandingContracts', None) is None:
                self.numOutstandingContracts = sm.GetService('contracts').NumOutstandingContracts()
            if forCorp:
                if innerCorp:
                    n = self.numOutstandingContracts.myCorpTotal
                else:
                    n = self.numOutstandingContracts.nonCorpForMyCorp
            elif innerCorp:
                n = self.numOutstandingContracts.myCharTotal
            else:
                n = self.numOutstandingContracts.nonCorpForMyChar
        finally:
            return (n, [maxNumContracts, MAX_NUM_CONTRACTS][innerCorp])

    def FinishStep(self, step):
        uthread.Lock(self)
        try:
            result = sm.GetService('form').ProcessForm(self.formdata[0], self.formdata[1])
            lastType = getattr(self.data, 'type', None)
            if step == 0:
                contractType = result.get('type', None)
                if contractType is None:
                    return False
                if contractType != lastType and not getattr(self, 'first', False):
                    self.ResetWizard()
            setattr(self, 'first', False)
            for i in result:
                setattr(self.data, str(i), result[i])

            if step == 0:
                doContinue = self.FinishPage0()
                if not doContinue:
                    return False
            elif step == 1:
                doContinue = self.FinishStep1()
                if not doContinue:
                    return False
            else:
                if step == 2:
                    return self.FinishStep2()
                raise RuntimeError('Illegal step (%s)' % step)
            return True
        finally:
            uthread.UnLock(self)

    def FinishPage0(self):
        self.isMultiContract = False
        if self.data.type == const.conTypeItemExchange:
            fittedShipsCb = self.form.FindChild('contractTypeCb_fittedShip')
            if fittedShipsCb and fittedShipsCb.checked:
                self.isMultiContract = True
        ownerID = None
        if self.data.avail == 1:
            if IsSearchStringLongEnough(self.data.name):
                exact = getattr(self.data, 'searchBy', search_const.MatchBy.partial_terms)
                ownerID = searchOld.Search(self.data.name.lower(), const.groupCharacter, const.categoryOwner, exact=exact, hideNPC=1, searchWndName='contractFinishStepSearch', hideDustChars=True)
            if not ownerID:
                return False
            if self.data.type == const.conTypeAuction:
                owner = cfg.eveowners.Get(ownerID)
                if owner.IsCharacter() or owner.IsCorporation() and ownerID != session.corpid:
                    raise UserError('CustomInfo', {'info': GetByLabel('UI/Contracts/ContractsService/UserErrorCannotCreatePrivateAuction')})
        elif self.data.name != '':
            raise UserError('CustomInfo', {'info': GetByLabel('UI/Contracts/ContractsService/UserErrorPrivateNameAndStateDontMatch')})
        elif self.data.avail == 2:
            ownerID = eve.session.corpid
        elif self.data.avail == 3:
            ownerID = eve.session.allianceid
            if not ownerID:
                raise UserError('CustomInfo', {'info': GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/CorporationNotInAllianceMessage')})
        self.data.assigneeID = ownerID
        forCorp = bool(self.data.forCorp)
        n, maxNumContracts = self.GetNumContractsAndLimits(forCorp, self.data.assigneeID)
        if n >= maxNumContracts >= 0:
            if forCorp is True:
                skillLabel = GetByLabel('UI/Contracts/ContractsService/IncreaseSkillInfo', skillType=const.typeCorporationContracting)
            else:
                skillLabel = GetByLabel('UI/Contracts/ContractsService/IncreaseSkillInfo', skillType=const.typeContracting)
            errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorMaxContractsReached', numContracts=maxNumContracts, skillInfo=skillLabel)
            raise UserError('CustomInfo', {'info': errorLabel})
        return True

    def FinishStep1(self):
        ILLEGAL_ITEMGROUPS = [const.groupCapsule]
        contractType = self.data.type
        self.data.numByContainerItemIDs = {}
        if self.IsFittedShipContract(contractType):
            numShips = len(self.data.items)
            isForCorp = self.data.forCorp
            currentNum, maxNumContracts = self.GetNumContractsAndLimits(isForCorp, getattr(self.data, 'assigneeID', 0))
            maxMultiContracts = GetMaxShipsToContract(sm.GetService('machoNet'))
            maxMultiContract = min(maxMultiContracts, maxNumContracts - currentNum)
            if numShips > maxMultiContract:
                raise UserError('ConMultiContractExceedAvailable')
            if not numShips:
                raise UserError('ConMultiContractSelectShip')
            for itemID, item in self.data.items.iteritems():
                itemTypeID = item[0]
                itemGroupID = evetypes.GetGroupID(itemTypeID)
                itemRow = item[2]
                if evetypes.GetCategoryID(itemTypeID) != const.categoryShip or not itemRow.singleton:
                    raise UserError('ConMultiContractNotShip')
                if itemGroupID in ILLEGAL_ITEMGROUPS:
                    raise UserError('ConIllegalType')
                if itemID in (eve.session.shipid, eveCfg.GetActiveShip()):
                    raise UserError('ConCannotTradeCurrentShip')

            div = self.data.startStationDivision if isForCorp else const.flagHangar
            numByContainerItemIDs = sm.GetService('contracts').GetNumItemsInContainers(self.data.startStation, self.data.items.keys(), isForCorp, div)
            self.data.numByContainerItemIDs = numByContainerItemIDs
            totalItems = sum(numByContainerItemIDs.itervalues())
            if totalItems:
                if eve.Message('ConMultiContractConfirmShipNumAndContent', {'numShips': len(numByContainerItemIDs),
                 'numItems': totalItems}, buttons=uiconst.YESNO, modal=True, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                    return
        else:
            self.data.childItems = {}
            for i in self.data.items:
                typeID = self.data.items[i][0]
                groupID = evetypes.GetGroupID(typeID)
                categoryID = evetypes.GetCategoryID(typeID)
                if groupID in ILLEGAL_ITEMGROUPS:
                    raise UserError('ConIllegalType')
                if i in (eve.session.shipid, eveCfg.GetActiveShip()):
                    raise UserError('ConCannotTradeCurrentShip')
                isContainer = categoryID == const.categoryShip or groupID in (const.groupCargoContainer,
                 const.groupSecureCargoContainer,
                 const.groupAuditLogSecureContainer,
                 const.groupFreightContainer)
                if isContainer:
                    div = const.flagHangar
                    if self.data.forCorp:
                        div = self.data.startStationDivision
                    itemNameList = []
                    totalVolume = 0
                    for l in sm.GetService('contracts').GetItemsInContainer(self.data.startStation, i, self.data.forCorp, div) or []:
                        itemNameList.append(TypeName(l.typeID))
                        val = [l.itemID, l.typeID, l.stacksize]
                        if i not in self.data.childItems:
                            self.data.childItems[i] = []
                        self.data.childItems[i].append(val)
                        totalVolume += GetItemVolume(l, l.stacksize)

                    if itemNameList:
                        itemsText = ', '.join(itemNameList)
                        msg = 'ConNonEmptyShip' if evetypes.GetCategoryID(typeID) == const.categoryShip else 'ConNonEmptyContainer2'
                        if eve.Message(msg, {'container': typeID,
                         'items': itemsText,
                         'volume': totalVolume}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                            return False

        if contractType == const.conTypeCourier:
            volume = 0
            for i in self.data.items:
                evetypes.RaiseIFNotExists(self.data.items[i][0])
                item = self.data.items[i][2]
                volume += GetItemVolume(item, int(self.data.items[i][1]))

            if volume > const_conCourierMaxVolume:
                raise UserError('ConExceedsMaxVolume', {'max': const_conCourierMaxVolume,
                 'vol': volume})
            elif volume > const_conCourierWarningVolume:
                if eve.Message('ConNeedFreighter', {'vol': volume}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                    return False
        if not self.data.startStation or self.data.startStation == 0:
            raise UserError('CustomInfo', {'info': GetByLabel('UI/Contracts/ContractsService/UserErrorSelectStartingPointForContract')})
        elif contractType in [const.conTypeCourier, const.conTypeAuction] and len(self.data.items) == 0:
            raise UserError('CustomInfo', {'info': GetByLabel('UI/Contracts/ContractsService/UserErrorSelectItemsForContract')})
        if contractType in [const.conTypeAuction, const.conTypeItemExchange]:
            insuranceContracts = []
            for i in self.data.items:
                item = self.data.items[i]
                categoryID = evetypes.GetCategoryID(item[0])
                if item[2].singleton and categoryID == const.categoryShip:
                    contract = sm.GetService('insurance').GetContractForShip(i)
                    if contract:
                        insuranceContracts.append([contract, item[0]])

            for contract in insuranceContracts:
                example = contract[1]
                if (contract[0].ownerID == eve.session.corpid or self.data.forCorp) and self.data.avail != const.conAvailPublic:
                    if eve.Message('ConInsuredShipCorp', {'example': example}, uiconst.YESNO) != uiconst.ID_YES:
                        doContinue = False
                        return doContinue
                elif eve.Message('ConInsuredShip', {'example': example}, uiconst.YESNO) != uiconst.ID_YES:
                    return False

            for i in self.data.items:
                item = self.data.items[i]
                categoryID = evetypes.GetCategoryID(item[0])
                if categoryID == const.categoryShip and item[2].singleton:
                    sm.GetService('invCache').RemoveInventoryContainer(item[2])

        self.LockItems(self.data.items)
        return True

    def FinishStep2(self):
        if hasattr(self.data, 'price'):
            self.data.price = int(self.data.price)
        if hasattr(self.data, 'reward'):
            self.data.reward = int(self.data.reward)
        if hasattr(self.data, 'collateral'):
            self.data.collateral = int(self.data.collateral)
        if len(self.data.description) > MAX_TITLE_LENGTH:
            errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorContractTitleTooLong', length=len(self.data.description), maxLength=MAX_TITLE_LENGTH)
            raise UserError('CustomInfo', {'info': errorLabel})
        if self.data.description:
            bannedwords.check_words_allowed(self.data.description)
        contractType = self.data.type
        if contractType == const.conTypeAuction:
            self.FinishStep2_AuctionContracts()
        elif contractType == const.conTypeCourier:
            doContinue = self.FinishStep2_CourierContract()
            if not doContinue:
                return False
        elif self.IsFittedShipContract(contractType):
            self.FinishStep2_FittedShip()
        elif contractType == const.conTypeItemExchange:
            self.FinishStep2_ItemExchangeContract()
        else:
            raise RuntimeError('Not implemented!')
        return True

    def FinishStep2_AuctionContracts(self):
        if self.data.price < const_conBidMinimum and self.data.avail == 0:
            errorLabel = GetByLabel('UI/Contracts/ContractsWindow/ErrorMinimumBidTooLow', minimumBid=const_conBidMinimum)
            raise UserError('CustomInfo', {'info': errorLabel})
        elif self.data.price > self.data.collateral and self.data.collateral > 0:
            errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorCannotSpecifyBidOverBuyout')
            raise UserError('CustomInfo', {'info': errorLabel})

    def FinishStep2_CourierContract(self):
        if not self.data.endStation and len(self.form.sr.endStationName.GetValue()) > 0:
            self.SearchStationFromEdit(self.form.sr.endStationName)
            if not self.data.endStation:
                return False
        if not self.data.endStation:
            errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorMustSpecifyContractDestination')
            raise UserError('CustomInfo', {'info': errorLabel})
        if not self.data.assigneeID:
            if self.data.reward < MIN_CONTRACT_MONEY:
                errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorMinimumRewardNotMet', minimum=MIN_CONTRACT_MONEY)
                raise UserError('CustomInfo', {'info': errorLabel})
            if self.data.collateral < MIN_CONTRACT_MONEY:
                errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorMinimumCollateralNotMet', minimum=MIN_CONTRACT_MONEY)
                raise UserError('CustomInfo', {'info': errorLabel})
        return True

    def FinishStep2_ItemExchangeContract(self):
        if self.data.price != 0.0 and self.data.reward != 0.0:
            errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorCannotGiveAndReceiveISK')
            raise UserError('CustomInfo', {'info': errorLabel})
        if not self.data.assigneeID:
            if self.data.reqItems == {} and self.data.price < MIN_CONTRACT_MONEY:
                errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorExchangeContractRequestNotMet', minimum=MIN_CONTRACT_MONEY)
                raise UserError('CustomInfo', {'info': errorLabel})
        if self.reqItemTypeWnd.GetValue() != '':
            errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorMustClickAddItem')
            raise UserError('CustomInfo', {'info': errorLabel})
        if not self.data.assigneeID:
            if (self.data.reqItems != {} or self.data.price > 0) and len(self.data.items) == 0 and self.data.reward == 0:
                errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorCannotCreateOneSidedExchangeContract')
                raise UserError('CustomInfo', {'info': errorLabel})

    def FinishStep2_FittedShip(self):
        if getattr(self.data, 'reward', 0):
            raise UserError('ConMultiContracCannotOfferIsk')
        if self.data.reqItems:
            raise UserError('ConMultiContractCannotAskForItems')
        if not self.data.assigneeID:
            if self.data.price < MIN_CONTRACT_MONEY:
                errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorExchangeContractRequestNotMet', minimum=MIN_CONTRACT_MONEY)
                raise UserError('CustomInfo', {'info': errorLabel})
        if not len(self.data.items):
            raise UserError('CustomInfo', {'info': 'You need to include at least 1 ship'})

    def OnComboChange(self, wnd, *args):
        if wnd.name == 'startStation' or wnd.name == 'startStationDivision':
            if wnd.name == 'startStation':
                self.data.startStation = wnd.GetValue()
            else:
                self.data.startStationDivision = wnd.GetValue()
            self.data.items = {}
            self.GotoPage(self.currPage)

    def OnStepChange(self, move, *args):
        if self.currPage + move >= 4:
            if eve.Message('ConConfirmCreateContract', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                try:
                    self.CreateContract()
                except:
                    self.Maximize()
                    raise

        elif self.currPage + move >= 0 and (move < 0 or self.FinishStep(self.currPage)):
            self.GotoPage(self.currPage + move)

    def ClickItem(self, *args):
        pass

    def OnDeleteContract(self, contractID, *args):
        self.numOutstandingContracts = None

    def OnCancel(self, *args):
        if eve.Message('ConAreYouSureYouWantToCancel', None, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.Close()

    def ResetWizard(self):
        self.data = utillib.KeyVal()
        self.data.items = {}
        self.data.reqItems = {}
        self.data.startStation = None
        self.data.endStation = None
        self.data.startStationDivision = 0
        self.data.type = const.conTypeNothing
        self.SetMainIcon(GetContractIcon(const.conTypeNothing))

    def WriteSelectItems(self, title):
        contractType = self.data.type
        forCorp = self.data.forCorp
        deliveriesRoles = const.corpRoleAccountant | const.corpRoleJuniorAccountant | const.corpRoleTrader
        if self.IsFittedShipContract(contractType):
            currentNum, maxNumContracts = self.GetNumContractsAndLimits(forCorp, getattr(self.data, 'assigneeID', 0))
            maxMultiContracts = GetMaxShipsToContract(sm.GetService('machoNet'))
            maxMultiContract = min(maxMultiContracts, maxNumContracts - currentNum)
            text = GetByLabel('UI/Contracts/ContractsWindow/ItemExchangeSelectShips', numShips=maxMultiContract)
            eveLabel.EveLabelMedium(text=text, parent=self.formWnd, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, padding=(7, 0, 7, 0))
            itemIDsToRemove = set()
            for itemID, item in self.data.items.iteritems():
                itemRow = item[2]
                if evetypes.GetCategoryID(item[0]) != const.categoryShip or not itemRow.singleton:
                    itemIDsToRemove.add(itemID)

            for eachItemID in itemIDsToRemove:
                self.data.items.pop(eachItemID)

        if forCorp:
            rows = sm.RemoteSvc('corpmgr').GetAssetInventory(eve.session.corpid, 'offices')
            sortops = []
            for r in rows:
                stationName = cfg.evelocations.Get(r.locationID).name
                sortops.append((stationName, (stationName, r.locationID)))

            if session.corprole & deliveriesRoles > 0:
                rows = sm.RemoteSvc('corpmgr').GetAssetInventory(eve.session.corpid, 'deliveries')
                for r in rows:
                    stationName = cfg.evelocations.Get(r.locationID).name
                    stat = (stationName, (stationName, r.locationID))
                    if stat not in sortops:
                        sortops.append(stat)

            ops = [(title, 0)] + SortListOfTuples(sortops)
        else:
            stations = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStations()
            primeloc = []
            for station in stations:
                primeloc.append(station.stationID)

            if len(primeloc):
                cfg.evelocations.Prime(primeloc)
            sortops = []
            for station in stations:
                stationName = cfg.evelocations.Get(station.stationID).name
                itemCount = station.itemCount
                if station.stationID in (session.stationid, session.structureid):
                    itemCount -= 1
                itemsInStationLabel = GetByLabel('UI/Contracts/ContractsService/ItemsInStation', station=station.stationID, numItems=itemCount)
                sortops.append((stationName.lower(), (itemsInStationLabel, station.stationID)))

            ops = [(title, 0)] + SortListOfTuples(sortops)
        comboParent = Container(name='comboParent', parent=self.formWnd, align=uiconst.TOTOP, top=const.defaultPadding)
        Container(name='push', parent=comboParent, align=uiconst.TOLEFT, width=1)
        Container(name='push', parent=comboParent, align=uiconst.TORIGHT, width=1)
        combo = Combo(label=None, parent=comboParent, options=ops, name='startStation', select=None, callback=self.OnComboChange, align=uiconst.TOALL)
        comboParent.height = Combo.default_height
        if self.data.startStation is None:
            if eve.session.stationid:
                self.data.startStation = eve.session.stationid
            elif eve.session.structureid:
                self.data.startStation = eve.session.structureid
        if forCorp:
            divs = [(GetByLabel('UI/Contracts/ContractsWindow/SelectDivision'), 0)]
            divisions = sm.GetService('corp').GetDivisionNames()
            for flagID in const.flagCorpSAGs:
                divisionID = const.corpDivisionsByFlag[flagID]
                divisionName = divisions[divisionID + 1]
                divs.append((divisionName, flagID))

            if eve.session.corprole & deliveriesRoles > 0:
                divs.append((GetByLabel('UI/Contracts/ContractsWindow/Deliveries'), const.flagCorpDeliveries))
            comboDiv = Combo(label='', parent=comboParent, options=divs, name='startStationDivision', select=None, callback=self.OnComboChange, align=uiconst.TORIGHT, width=100, pos=(1, 0, 0, 0), idx=0)
            Container(name='push', parent=comboParent, align=uiconst.TORIGHT, width=4, idx=1)
            nudge = 18
        for i, entry in enumerate(combo.entries):
            if entry.returnValue == self.data.startStation:
                combo.SelectItemByIndex(i)
                break

        if forCorp:
            for i, entry in enumerate(comboDiv.entries):
                if entry.returnValue == self.data.startStationDivision:
                    comboDiv.SelectItemByIndex(i)
                    break

        c = Container(name='volume', parent=self.formWnd, align=uiconst.TOBOTTOM, width=6, height=20)
        numVolLabel = GetByLabel('UI/Contracts/ContractsService/NumberOfWithVolume', number=0, volume=0)
        self.sr.volumeText = eveLabel.EveLabelMedium(text=numVolLabel, parent=c, state=uiconst.UI_DISABLED, align=uiconst.CENTERRIGHT)
        self.UpdateNumberOfItems()
        self.sr.itemsScroll = eveScroll.Scroll(parent=self.formWnd, padTop=const.defaultPadding, padBottom=const.defaultPadding)
        self.toggleSelectAllCheckbox = Checkbox(parent=self.sr.itemsScroll, align=uiconst.TOPLEFT, checked=0, left=7, callback=self.OnSelectAllCheckboxClicked, idx=0, top=-1)
        self.toggleSelectAllCheckbox.display = False
        if forCorp:
            if not self.data.startStation:
                self.sr.itemsScroll.ShowHint(GetByLabel('UI/Search/SelectStation'))
                if self.data.startStationDivision == 0:
                    self.sr.itemsScroll.ShowHint(GetByLabel('UI/Contracts/ContractEntry/SelectStationDivision'))
            elif self.data.startStationDivision == 0:
                self.sr.itemsScroll.ShowHint(GetByLabel('UI/Contracts/ContractsWindow/SelectDivision'))
        validStartStation = self.data.startStation and self.CanContractItemsFromLocation(self.data.startStation)
        if validStartStation and (not forCorp or self.data.startStationDivision):
            self.sr.itemsScroll.Load(contentList=[], headers=[], noContentHint=GetByLabel('UI/Contracts/ContractsWindow/NoItemsFound'))
            self.sr.itemsScroll.ShowHint(GetByLabel('UI/Contracts/ContractsWindow/GettingItems'))
            items = sm.GetService('contracts').GetItemsInDockableLocation(self.data.startStation, forCorp)
            self.sr.itemsScroll.hiliteSorted = 0
            scrolllist = []

            def sameFlag(itemFlag):
                if itemFlag == self.data.startStationDivision:
                    return True
                if set((itemFlag, self.data.startStationDivision)) == set((const.flagHangar, const.flagCorpSAG1)):
                    return True
                return False

            isFittedShipContract = self.IsFittedShipContract(contractType)
            uix.PrimeEveLocationsBeforeGetItemName(items)
            contractType = self.data.type
            for item in items:
                if forCorp and not sameFlag(item.flagID):
                    continue
                data = uix.GetItemData(item, 'list', viewOnly=1)
                volume = GetItemVolume(item)
                itemName = ''
                isContainer = item.groupID in (const.groupCargoContainer,
                 const.groupSecureCargoContainer,
                 const.groupAuditLogSecureContainer,
                 const.groupFreightContainer) and item.singleton
                if item.categoryID == const.categoryShip or isContainer:
                    if item.itemID == eveCfg.GetActiveShip():
                        continue
                    shipName = cfg.evelocations.GetIfExists(item.itemID)
                    if shipName is not None:
                        itemName = shipName.locationName
                if isFittedShipContract and item.categoryID != const.categoryShip:
                    continue
                scrolllist.append(GetFromClass(ContractItemSelect, {'info': item,
                 'stationID': self.data.startStation,
                 'forCorp': forCorp,
                 'flag': item.flagID,
                 'itemID': item.itemID,
                 'typeID': item.typeID,
                 'isCopy': item.categoryID == const.categoryBlueprint and item.singleton == const.singletonBlueprintCopy,
                 'label': '%s<t>%s<t>%s<t>%s' % (evetypes.GetName(item.typeID),
                           item.stacksize,
                           volume,
                           itemName),
                 'quantity': item.stacksize,
                 'getIcon': 1,
                 'item': item,
                 'checked': item.itemID in self.data.items,
                 'cfgname': item.itemID,
                 'itemData': (item,
                              item.itemID,
                              item.typeID,
                              item.stacksize),
                 'OnChange': self.OnItemSelectedChanged,
                 'GetSortValue': self.GetItemNodeSortValue}))

            if self.sr.itemsScroll is not None:
                if scrolllist:
                    self.sr.itemsScroll.ShowHint()
                self.sr.itemsScroll.sr.id = 'itemsScroll'
                self.sr.itemsScroll.sr.lastSelected = None
                headers = [GetByLabel('UI/Common/Type'),
                 GetByLabel('UI/Inventory/ItemQuantityShort'),
                 GetByLabel('UI/Common/Volume'),
                 GetByLabel('UI/Common/Details')]
                if combo.GetValue() == 0:
                    noContentHint = GetByLabel('UI/Search/SelectStation')
                elif isFittedShipContract:
                    noContentHint = GetByLabel('UI/Contracts/ContractsWindow/NoShipFound')
                else:
                    noContentHint = GetByLabel('UI/Contracts/ContractsWindow/NoItemsFound')
                self.sr.itemsScroll.GetEffectiveColumnOffset = lambda *args: 24
                self.toggleSelectAllCheckbox.display = bool(scrolllist)
                self.sr.itemsScroll.Load(contentList=scrolllist, headers=headers, noContentHint=noContentHint)
                self.UpdateSelectAllCheckbox()

    def GetItemNodeSortValue(self, node, by, sortDirection, idx):
        ret = self.sr.itemsScroll._GetSortValue(by, node, idx)
        if node.checked:
            return (sortDirection, ret)
        return (not sortDirection, ret)

    def IsFittedShipContract(self, contractType):
        if not GetMaxShipsToContract(sm.GetService('machoNet')):
            return False
        return contractType == const.conTypeItemExchange and self.isMultiContract

    def CanContractItemsFromLocation(self, locationID):
        if idCheckers.IsStation(locationID):
            return True
        return sm.GetService('structureDirectory').CanContractFrom(locationID)

    def UpdateSelectAllCheckbox(self):
        self.UpdateSelectAllCheckbox_throttled()

    @throttled(0.5)
    def UpdateSelectAllCheckbox_throttled(self):
        if not self or self.destroyed or not self.sr.itemsScroll or self.sr.itemsScroll.destroyed:
            return
        selectedValues = {x.checked for x in self.sr.itemsScroll.GetNodes()}
        if selectedValues == {1}:
            self.toggleSelectAllCheckbox.SetChecked(True, False)
            self.toggleSelectAllCheckbox.hint = GetByLabel('UI/Common/DeselectAll')
        else:
            self.toggleSelectAllCheckbox.SetChecked(False, False)
            self.toggleSelectAllCheckbox.hint = GetByLabel('UI/Common/SelectAll')

    def OnSelectAllCheckboxClicked(self, cb, *args):
        if cb.GetValue():
            self.SelectAll()
        else:
            self.DeselectAll()
        self.UpdateSelectAllCheckbox()

    def DeselectAll(self, *args):
        self.ChangeCheckboxStates(onoff=False)

    def SelectAll(self, *args):
        self.ChangeCheckboxStates(onoff=True)

    def ChangeCheckboxStates(self, onoff):
        if not self.sr.itemsScroll:
            return
        for node in self.sr.itemsScroll.GetNodes():
            if node:
                node.checked = onoff
                if node.panel:
                    node.panel.sr.checkbox.SetChecked(onoff, 0)
                self.ChangeItemSelection(onoff, updateNumber=False, *node.itemData)

        self.UpdateNumberOfItems()

    def OnItemSelectedChanged(self, isChecked, itemData, *args):
        item, itemID, typeID, qty = itemData
        self.ChangeItemSelection(isChecked, item, itemID, typeID, qty)
        self.UpdateSelectAllCheckbox()

    def ChangeItemSelection(self, checkboxSelected, item, itemID, typeID, qty, updateNumber = True):
        if checkboxSelected:
            self.data.items[itemID] = [typeID, qty, item]
        elif itemID in self.data.items:
            del self.data.items[itemID]
        if updateNumber:
            self.UpdateNumberOfItems()

    def UpdateNumberOfItems(self):
        num, totalVolume = self.GetVolumeOfAllItems()
        numVolLabel = GetByLabel('UI/Contracts/ContractsService/NumberOfWithVolume', number=num, volume=FmtAmt(totalVolume))
        maxItems = MAX_NUM_ITEMS
        if self.IsFittedShipContract(self.data.type):
            maxItems = GetMaxShipsToContract(sm.GetService('machoNet'))
            currentNum, maxNumContracts = self.GetNumContractsAndLimits(self.data.forCorp, getattr(self.data, 'assigneeID', 0))
            maxItems = min(maxItems, maxNumContracts - currentNum)
        if num > maxItems:
            numVolLabel = '<color=red>' + numVolLabel + '</color>'
        self.sr.volumeText.text = numVolLabel

    def GetVolumeOfAllItems(self):
        totalVolume = 0
        num = 0
        for itemID, item in self.data.items.iteritems():
            totalVolume += GetItemVolume(item[2])
            num += 1

        return (num, totalVolume)

    def GetTypePrice(self, typeID):
        return GetAveragePrice(typeID) or evetypes.GetBasePrice(typeID)

    def CalcEstPrice(self):
        price = 0
        for item in self.data.items.itervalues():
            price += int(float(self.GetTypePrice(item[0])) / evetypes.GetPortionSize(item[0]) * item[1])

        price = RoundISK(price)
        if price == 0:
            raise UserError('ConNoEstPrice')
        return price

    def SetCollateralToEstPrice(self, *args):
        price = self.CalcEstPrice()
        if eve.Message('ConEstPrice', {'price': FmtISK(price, 0)}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.formWnd.sr.collateral.SetValue(price)

    def SetPriceToEstPrice(self, *args):
        price = self.CalcEstPrice()
        if eve.Message('ConEstPrice', {'price': FmtISK(price, 0)}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.formWnd.sr.price.SetValue(price)

    def OnItemSplit(self, itemID, amountRemoved):
        if itemID in self.data.items:
            self.data.items[itemID][1] -= amountRemoved
            if self.data.items[itemID][1] <= 0:
                del self.data.items[itemID]
