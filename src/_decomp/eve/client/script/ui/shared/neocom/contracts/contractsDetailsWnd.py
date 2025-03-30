#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\contracts\contractsDetailsWnd.py
from collections import defaultdict
import dogma.data as dogma_data
import evetypes
import log
import utillib
from brennivin.itertoolsext import Bundle
from carbon.common.script.util.format import FmtAmt, FmtDate
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from eve.client.script.ui.control import eveEdit, eveIcon, eveLabel, eveScroll
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.shared.neocom.contracts.contractDraggableIcon import ContractDraggableIcon
from eve.client.script.util.contractutils import GetContractIcon, ConFmtDate, FmtISKWithDescription, COL_GET, COL_PAY, CategoryName, GetCorpseName
from eve.common.lib import appConst as const
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.sys.idCheckers import IsNPC
from eve.common.script.util import contractscommon
from eve.common.script.sys.eveCfg import GetShipFlagLocationName
import blue
import localization
from eve.common.script.util.contractscommon import IsPlayerAllowedToRejectContract
from eve.common.script.util.eveFormat import FmtISK
from eveexceptions import UserError
from eveservices.menu import GetMenuService
from localization import GetByLabel
from menu import MenuLabel
BCancel = 0
BAccept = 1
BReject = 2
BComplete = 3
BDelete = 4
BSucceed = 5
BFail = 6
BGetItems = 7
BGetMoney = 8
BAcceptForCorp = 9
BPlaceBid = 10
HISTORY_LENGTH = 10

class ContractDetailsWindow(Window):
    __guid__ = 'form.ContractDetailsWindow'
    default_windowID = 'contractdetails'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        contractID = attributes.contractID
        self.contract = None
        self.buttons = []
        self.isContractMgr = False
        self.contractID = contractID
        self.sr.main.clipChildren = True
        self.sr.main.padRight = const.defaultPadding
        self.scope = uiconst.SCOPE_INGAME
        self.SetCaption(GetByLabel('UI/Common/Contract') % {'name': '-'})
        self.LoadTabs()
        self.icon = GetContractIcon(const.conTypeNothing)
        self.SetMinSize([520, 200])
        self.MakeUnstackable()
        self.MakeUncollapseable()
        self.history = settings.user.ui.Get('contracts_history', [])
        self.state = uiconst.UI_HIDDEN
        self.pathfinder = sm.GetService('clientPathfinderService')
        self.Init()

    def Init(self):
        self.corpseNameLabel = None
        self.sr.main.Flush()
        topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=52, clipChildren=True)
        SpriteThemeColored(name='mainicon', parent=topParent, state=uiconst.UI_DISABLED, pos=(0, -5, 64, 64), texturePath=self.iconNum, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        self.buttons = []
        contract = sm.GetService('contracts').GetContract(self.contractID, force=True)
        if not contract:
            self.HistoryRemove(self.contractID)
            self.Close()
            raise UserError('ConContractNotFound')
        self.contract = contract
        c = contract.contract
        self.contractID = c.contractID
        self.isContractMgr = isContractMgr = session.corprole & const.corpRoleContractManager == const.corpRoleContractManager
        canRejectContract = IsPlayerAllowedToRejectContract(c, session.charid, session.corpid, session.allianceid, session.corprole)
        isAssignedToMePersonally = c.assigneeID == session.charid
        isAcceptedByMe = c.acceptorID == session.charid or c.acceptorID == session.corpid and isContractMgr
        isAcceptedByMyCorp = c.acceptorID == session.corpid
        isIssuedByMe = c.issuerID == session.charid or c.issuerCorpID == session.corpid and c.forCorp and isContractMgr
        isIssuedByMePersonally = c.issuerID == session.charid
        isExpired = c.dateExpired < blue.os.GetWallclockTime()
        isOverdue = c.dateAccepted + const.DAY * c.numDays < blue.os.GetWallclockTime()
        title = GetByLabel('UI/Contracts/ContractsService/ContractTitleAndType', contractTitle=contractscommon.GetContractTitle(c, contract.items), contractType=contractscommon.GetContractTypeText(c.type))
        self.icon = GetContractIcon(c.type)
        icon = ContractDraggableIcon(name='theicon', align=uiconst.TOPLEFT, parent=self, height=64, width=64, left=0, top=11)
        icon.Startup(c, title)
        icon.state = uiconst.UI_NORMAL
        Container(name='push', parent=self.sr.main, align=uiconst.TOLEFT, width=6)
        Container(name='push', parent=self.sr.main, align=uiconst.TORIGHT, width=6)
        titleParent = Container(name='titleparent', parent=topParent, align=uiconst.TOPLEFT, top=12, left=70, width=430)
        l = eveLabel.EveLabelLarge(text=title, parent=titleParent, width=400, state=uiconst.UI_DISABLED)
        titleParent.height = l.textheight + 2 * const.defaultPadding
        self.HistoryAdd(self.contractID, c.startSolarSystemID, title)
        text = GetBasicInfoText(c)
        tabs = [115, 480]
        basicInfoParent = Container(name='infocontainer', parent=self.sr.main, align=uiconst.TOTOP, padRight=const.defaultPadding)
        basicInfo = eveLabel.EveLabelMedium(text=text, parent=basicInfoParent, top=const.defaultPadding, idx=0, tabs=tabs, state=uiconst.UI_NORMAL, left=6)
        basicInfoParent.height = basicInfo.textheight + 5
        Line(parent=basicInfoParent, align=uiconst.TOTOP)
        isResizable = False
        if c.status == const.conStatusInProgress:
            if isAcceptedByMe:
                if c.type != 4:
                    self.AddButton(BComplete)
                self.AddButton(BFail)
            elif isIssuedByMe and isOverdue:
                self.AddButton(BFail)
            elif isAcceptedByMyCorp and c.type == const.conTypeCourier:
                self.AddButton(BComplete)
        if c.type == const.conTypeAuction:
            text = ''
            text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/StartingBid'), FmtISKWithDescription(c.price))
            bo = [GetByLabel('UI/Contracts/ContractEntry/NoneParen'), FmtISKWithDescription(c.collateral)][c.collateral > 0]
            text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/BuyoutPrice'), bo)
            b = GetByLabel('UI/Contracts/ContractEntry/NoBids')
            if len(contract.bids) > 0:
                b = GetByLabel('UI/Contracts/ContractsWindow/BidsSoFar', numISK=FmtISKWithDescription(contract.bids[0].amount), numBids=len(contract.bids))
            text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/CurrentBid'), b)
            timeleft = GetByLabel('UI/Contracts/ContractsWindow/Finished')
            if c.status == const.conStatusOutstanding:
                diff = c.dateExpired - blue.os.GetWallclockTime()
                if c.dateExpired - blue.os.GetWallclockTime() > 0:
                    timeleft = ConFmtDate(diff, True)
            text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/TimeLeft'), timeleft)
            isExpired = c.dateExpired < blue.os.GetWallclockTime()
            isCancelled = c.status == const.conStatusCancelled
            highBidder = None
            if len(contract.bids) > 0:
                highBidder = contract.bids[0].bidderID
            if not isCancelled:
                if session.charid == highBidder:
                    if isExpired:
                        strToBold = GetByLabel('UI/Contracts/ContractsWindow/YouWon')
                    else:
                        strToBold = GetByLabel('UI/Contracts/ContractsWindow/YouAreHighBidder')
                    boldStr = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=strToBold)
                    rowInfo = '<color=%s>%s</color>' % (COL_GET, boldStr)
                    text += AddBasicInfoRow('', rowInfo)
                elif session.corpid == highBidder:
                    if isExpired:
                        strToBold = GetByLabel('UI/Contracts/ContractsWindow/YourCorpWon')
                    else:
                        strToBold = GetByLabel('UI/Contracts/ContractsWindow/YourCorpHighBidder')
                    boldStr = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=strToBold)
                    rowInfo = '<color=%s>%s</color>' % (COL_GET, boldStr)
                    text += AddBasicInfoRow('', rowInfo)
                else:
                    for i in range(len(contract.bids)):
                        b = contract.bids[i]
                        if i != 0:
                            if b.bidderID == session.charid:
                                if isExpired:
                                    strToBold = GetByLabel('UI/Contracts/ContractsWindow/YouLost')
                                else:
                                    strToBold = GetByLabel('UI/Contracts/ContractsWindow/YouHaveBeenOutBid')
                                boldStr = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=strToBold)
                                rowInfo = '<color=%s>%s</color>' % (COL_PAY, boldStr)
                                text += AddBasicInfoRow('', rowInfo)
                            elif b.bidderID == session.corpid:
                                if isExpired:
                                    strToBold = GetByLabel('UI/Contracts/ContractsWindow/YourCorpLost')
                                else:
                                    strToBold = GetByLabel('UI/Contracts/ContractsWindow/YourCorpWasOutBid')
                                boldStr = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=strToBold)
                                rowInfo = '<color=%s>%s</color>' % (COL_PAY, boldStr)
                                text += AddBasicInfoRow('', rowInfo)
                            break

                    if isExpired and len(contract.bids) > 0:
                        winner = cfg.eveowners.Get(contract.bids[0].bidderID)
                        showInfoLink = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLinkWithMore', showInfoName=winner.ownerName, info=('showinfo', winner.typeID, winner.ownerID), more=GetByLabel('UI/Contracts/ContractsWindow/WonThisAuction'))
                        text += AddBasicInfoRow('', showInfoLink)
            infoParent = Container(name='infocontainer', parent=self.sr.main, align=uiconst.TOTOP, width=const.defaultPadding)
            info = eveLabel.EveLabelMedium(text=text, parent=infoParent, top=const.defaultPadding, idx=0, tabs=tabs, state=uiconst.UI_NORMAL, left=6)
            infoParent.height = info.textheight + 2 * const.defaultPadding
            Line(parent=infoParent, align=uiconst.TOTOP)
            Line(parent=infoParent, align=uiconst.TOBOTTOM)
            isResizable = self.InsertItemList(contract, '<color=%s>%s</color>' % (COL_GET, [GetByLabel('UI/Contracts/ContractsWindow/YouWillGet'), GetByLabel('UI/Contracts/ContractsWindow/BuyerWillGet')][session.charid == c.issuerID]), True, 3)
            if len(contract.bids) > 0 and isExpired and not isCancelled:
                if c.status != const.conStatusFinishedIssuer and c.status != const.conStatusFinished and isIssuedByMe:
                    self.AddButton(BGetMoney)
                if c.status != const.conStatusFinishedContractor and c.status != const.conStatusFinished and (contract.bids[0].bidderID == session.charid or contract.bids[0].bidderID == session.corpid and isContractMgr):
                    self.AddButton(BGetItems)
            if isIssuedByMe and not isCancelled:
                if (c.status == const.conStatusOutstanding or c.status == const.conStatusRejected) and len(contract.bids) == 0:
                    self.AddButton(BDelete)
            if not isIssuedByMePersonally and c.status == const.conStatusOutstanding:
                if not isExpired:
                    self.AddButton(BPlaceBid)
                    if canRejectContract and not highBidder:
                        self.AddButton(BReject)
        elif c.type == const.conTypeItemExchange:
            text = ''
            if c.price > 0:
                if session.charid == c.issuerID:
                    rowLabel = GetByLabel('UI/Contracts/ContractsWindow/BuyerWillPay')
                else:
                    rowLabel = GetByLabel('UI/Contracts/ContractsWindow/YouWillPay')
                boldIsk = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=FmtISKWithDescription(c.price))
                rowInfo = '<color=%s>%s</color>' % (COL_PAY, boldIsk)
                text += AddBasicInfoRow(rowLabel, rowInfo)
            if c.reward > 0 or c.price == 0:
                if session.charid == c.issuerID:
                    rowLabel = GetByLabel('UI/Contracts/ContractsWindow/BuyerWillGet')
                else:
                    rowLabel = GetByLabel('UI/Contracts/ContractsWindow/YouWillGet')
                boldIsk = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=FmtISKWithDescription(c.reward))
                rowInfo = '<color=%s>%s</color>' % (COL_GET, boldIsk)
                text += AddBasicInfoRow(rowLabel, rowInfo)
            infoParent = Container(name='infocontainer', parent=self.sr.main, align=uiconst.TOTOP, width=const.defaultPadding)
            info = eveLabel.EveLabelLarge(text=text, parent=infoParent, top=const.defaultPadding, idx=0, tabs=tabs, state=uiconst.UI_NORMAL, left=6)
            infoParent.height = info.textheight + 2 * const.defaultPadding
            Line(parent=infoParent, align=uiconst.TOTOP)
            Line(parent=infoParent, align=uiconst.TOBOTTOM)
            fixedSize = False
            for i in contract.items:
                if not i.inCrate:
                    fixedSize = True

            isResizable = self.InsertItemList(contract, '<color=%s>%s</color>' % (COL_GET, [GetByLabel('UI/Contracts/ContractsWindow/YouWillGet'), GetByLabel('UI/Contracts/ContractsWindow/BuyerWillGet')][session.charid == c.issuerID]), True, 2, fixedSize=fixedSize)
            if self.InsertItemList(contract, '<color=%s>%s</color>' % (COL_PAY, [GetByLabel('UI/Contracts/ContractsWindow/YouWillPay'), GetByLabel('UI/Contracts/ContractsWindow/BuyerWillPay')][session.charid == c.issuerID]), False, 2, hint=GetByLabel('UI/Contracts/ContractEntry/NoRequiredItems'), forceList=True):
                isResizable = True
            if isIssuedByMe:
                if c.status == const.conStatusOutstanding or c.status == const.conStatusRejected:
                    self.AddButton(BDelete)
            if c.status == const.conStatusOutstanding and (not isIssuedByMePersonally or isAssignedToMePersonally):
                if not isExpired:
                    self.AddButton(BAccept)
                    if isContractMgr:
                        self.AddButton(BAcceptForCorp)
                    if canRejectContract:
                        self.AddButton(BReject)
        elif c.type == const.conTypeCourier:
            text = ''
            if c.status == const.conStatusInProgress:
                de = c.dateExpired
                if c.status == const.conStatusInProgress:
                    de = c.dateAccepted + const.DAY * c.numDays
                diff = de - blue.os.GetWallclockTime()
                if diff > 0:
                    timeleft = GetByLabel('UI/Contracts/ContractsService/TimeLeftWithoutCaption', timeLeft=ConFmtDate(diff, False), expireTime=FmtDate(de, 'ss'))
                else:
                    overdueLabel = GetByLabel('UI/Contracts/ContractsService/Overdue', time=FmtDate(-diff, 'ss'))
                    timeleft = '<color=red>%s</color>' % overdueLabel
                text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/TimeLeft'), timeleft)
            elif c.status == const.conStatusOutstanding:
                rowInfoText = GetByLabel('UI/Contracts/ContractsService/QuantityDays', numDays=c.numDays)
                text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/CompleteIn'), rowInfoText)
            volumeLabel = GetByLabel('UI/Contracts/ContractsWindow/NumericVolume', volume=FmtAmt(c.volume, showFraction=0 if c.volume > 10 else 2))
            text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsSearch/columnVolume'), volumeLabel)
            numJumps = self.pathfinder.GetAutopilotJumpCount(c.endSolarSystemID, c.startSolarSystemID)
            perjump = ''
            if numJumps:
                jumpCost = int(c.reward / numJumps)
                perjump = GetByLabel('UI/Contracts/ContractsService/ISKPerJump', costPerJump=FmtISKWithDescription(jumpCost, justDesc=True))
            if c.reward > 0:
                boldIsk = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=FmtISKWithDescription(c.reward))
                b = '<color=%s>%s</color>' % (COL_GET, boldIsk)
            else:
                b = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
            text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/Reward'), b)
            if c.reward > 0:
                text += AddBasicInfoRow('', perjump)
                if c.volume:
                    volumeCost = FmtISK(float(c.reward) / c.volume, showFractionsAlways=1)
                    perM3 = GetByLabel('UI/Contracts/ContractsService/ISKPerM3', costPerM3=volumeCost)
                    text += AddBasicInfoRow('', perM3)
            if c.collateral > 0:
                boldIsk = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=FmtISKWithDescription(c.collateral))
                b = '<color=%s>%s</color>' % (COL_PAY, boldIsk)
            else:
                b = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
            text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/Collateral'), b)
            mr = sm.GetService('contracts').GetRouteSecurityWarning(c.startSolarSystemID, c.endSolarSystemID)
            if mr:
                mr = '<t>%s' % mr
            dot = sm.GetService('contracts').GetSystemSecurityDot(c.endSolarSystemID)
            if idCheckers.IsStation(c.endStationID):
                endStationTypeID = sm.GetService('ui').GetStationStaticInfo(c.endStationID).stationTypeID
            else:
                endStationTypeID = sm.GetService('structureDirectory').GetStructureInfo(c.endStationID).typeID
            loc = GetByLabel('UI/Contracts/ContractsWindow/StationLinkWithDot', dot=dot, station=c.endStationID, info=('showinfo', endStationTypeID, c.endStationID))
            if not idCheckers.IsStation(c.endStationID):
                loc += '<br><t><color=0xffbb0000>%s</color>' % GetByLabel('UI/Contracts/ContractEntry/MightBeInaccessible')
            jumpsToEndSolarSystem = self.pathfinder.GetAutopilotJumpCount(session.solarsystemid2, c.endSolarSystemID)
            if jumpsToEndSolarSystem <= contractscommon.NUMJUMPS_UNREACHABLE:
                routeLabel = GetByLabel('UI/Contracts/ContractsService/RouteInfo', numJumps=jumpsToEndSolarSystem)
                loc += '<br><t>%s' % routeLabel
            if c.startSolarSystemID != session.solarsystemid2:
                if numJumps <= contractscommon.NUMJUMPS_UNREACHABLE:
                    routeLabel = GetByLabel('UI/Contracts/ContractsService/ShowRouteFromStart', numJumps=numJumps)
                    loc += '<br><t>%s' % routeLabel
            if mr:
                loc += '<br>%s' % mr
            text += AddBasicInfoRow(GetByLabel('UI/Common/Destination'), loc)
            infoParent = Container(name='infocontainer', parent=self.sr.main, align=uiconst.TOTOP, width=const.defaultPadding)
            info = eveLabel.EveLabelMedium(text=text, parent=infoParent, top=const.defaultPadding, idx=0, tabs=tabs, state=uiconst.UI_NORMAL, left=const.defaultPadding)
            infoParent.height = info.textheight
            Line(parent=infoParent, align=uiconst.TOTOP)
            if isIssuedByMe:
                if c.status == const.conStatusOutstanding or c.status == const.conStatusRejected:
                    self.AddButton(BDelete)
            if c.status == const.conStatusOutstanding and (not isIssuedByMePersonally or isAssignedToMePersonally):
                if not isExpired:
                    self.AddButton(BAccept)
                    if isContractMgr:
                        self.AddButton(BAcceptForCorp)
                    if canRejectContract:
                        self.AddButton(BReject)
        elif c.type == const.conTypeLoan:
            text = ''
            if c.status == const.conStatusInProgress:
                timeleft = '<font color=red>%s</font>' % GetByLabel('UI/Contracts/ContractsWindow/Expired')
                de = c.dateExpired
                if c.status == const.conStatusInProgress:
                    de = c.dateAccepted + const.DAY * c.numDays
                    overdueLabel = GetByLabel('UI/Contracts/ContractsService/Overdue', time=FmtDate(-(de - blue.os.GetWallclockTime()), 'ss'))
                    timeleft = '<color=red>%s</color>' % overdueLabel
                diff = de - blue.os.GetWallclockTime()
                if diff > 0:
                    timeleft = GetByLabel('UI/Contracts/ContractsService/TimeLeftWithoutCaption', timeLeft=ConFmtDate(diff, False), expireTime=FmtDate(de, 'ss'))
                text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/TimeLeft'), timeleft)
            elif c.status == const.conStatusOutstanding or c.status == const.conStatusRejected:
                self.AddButton(BDelete)
            if c.price > 0:
                boldISK = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=FmtISKWithDescription(c.price))
                rowInfo = '<color=%s>%s</color>' % (COL_PAY, boldISK)
            else:
                rowInfo = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
            text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsSearch/columnPrice'), rowInfo)
            if c.collateral > 0:
                boldISK = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=FmtISKWithDescription(c.collateral))
                rowInfo = '<color=%s>%s</color>' % (COL_PAY, boldISK)
            else:
                rowInfo = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
            text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/Collateral'), rowInfo)
            if c.reward > 0:
                text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractEntry/ISKBorrowed'), '<color=%s>%s</color>' % (COL_GET, FmtISKWithDescription(c.reward)))
            infoParent = Container(name='infocontainer', parent=self.sr.main, align=uiconst.TOTOP, width=const.defaultPadding)
            info = eveLabel.EveLabelMedium(text=text, parent=infoParent, top=const.defaultPadding, idx=0, tabs=tabs, state=uiconst.UI_NORMAL)
            infoParent.height = info.textheight
            Line(parent=infoParent, align=uiconst.TOTOP)
            Line(parent=infoParent, align=uiconst.TOBOTTOM)
            isResizable = self.InsertItemList(contract, GetByLabel('UI/Contracts/ContractsWindow/BorrowedItems'), True, 3, fixedSize=True)
            if isIssuedByMe:
                if c.status == const.conStatusRejected:
                    self.AddButton(BDelete)
            if c.status == const.conStatusInProgress:
                nocollateral = ''
                if not c.collateral:
                    isk = c.reward or 0
                    nocollateral = GetByLabel('UI/Contracts/ContractsService/NoCollateralISK', reward=isk)
                else:
                    nocollateral = GetByLabel('UI/Contracts/ContractsService/NoCollateral')
                contractTypeLabel = GetByLabel('UI/Contracts/ContractsService/ContractTypeNotSupported')
                notSupportedLabel = GetByLabel('UI/Contracts/ContractsService/LoanContractNotSupported')
                failLabel = GetByLabel('UI/Contracts/ContractsService/ClickFail')
                apologizeLabel = GetByLabel('UI/Contracts/ContractsService/WeApologize')
                html = '<font color=0xffff4444><h4>%s</h4></font>%s<br>%s<br><br>%s<br><br>%s' % (contractTypeLabel,
                 notSupportedLabel,
                 failLabel,
                 nocollateral,
                 apologizeLabel)
                descParent = Container(name='desc', parent=self.sr.main, align=uiconst.TOTOP, left=const.defaultPadding, top=const.defaultPadding, height=180)
                desc = eveEdit.Edit(parent=descParent, readonly=1, hideBackground=1)
                desc.SetValue('<html><body>%s</body></html>' % html)
        else:
            raise RuntimeError('Invalid contract type!')
        self.AddButton(BCancel)
        childrenList = self.sr.main.children
        height = sum([ x.height for x in childrenList if x.state != uiconst.UI_HIDDEN and x.align in (uiconst.TOBOTTOM, uiconst.TOTOP) ]) + 110
        w, h = self.minsize
        add = {False: 0,
         True: 160}[isResizable]
        self.SetMinSize([w, height + add])
        self.buttonWnd = ButtonGroup(btns=self.buttons, parent=self.sr.main, button_size_mode=ButtonSizeMode.DYNAMIC, idx=0)
        self.state = uiconst.UI_NORMAL
        self.sr.captionpush = Container(name='captionpush', parent=self.sr.main, align=uiconst.TOBOTTOM, height=12, left=0, top=-16)
        historyicon = eveIcon.MenuIcon(size=24, ignoreSize=True, align=uiconst.CENTERLEFT)
        historyicon.GetMenu = lambda : self.GetHistoryMenu()
        historyicon.hint = GetByLabel('UI/Common/History')
        self.sr.captionpush = Container(name='captionpush', parent=self.sr.main, align=uiconst.TOBOTTOM, height=12, left=0, top=-16)
        self.sr.captionpush.children.insert(1000, historyicon)
        return self

    def GetHistoryMenu(self):
        m = []
        if self.contract.contract.issuerID == session.charid:
            if self.contract.contract.forCorp:
                if not IsNPC(session.corpid):
                    lastCopiedCorpFlag = settings.char.ui.Get('contracts_lastCopiedDiv', const.flagCorpSAG1)
                    if lastCopiedCorpFlag not in (const.flagCorpDeliveries,) + const.flagCorpSAGs:
                        lastCopiedCorpFlag = const.flagCorpSAG1
                    divName = self.GetDivisionName(lastCopiedCorpFlag)
                    text = GetByLabel('UI/Contracts/ContractsWindow/CopyContractDivisionName', divisionName=divName)
                    m.append((text, sm.GetService('contracts').OpenCreateContract, (None, self.contract, lastCopiedCorpFlag)))
                    m += [(MenuLabel('UI/Contracts/ContractsWindow/CopyContractFromDivision'), ('isDynamic', self._GetCorpDivisions, ()))]
            else:
                m.append((MenuLabel('UI/Contracts/ContractsWindow/CopyContract'), sm.GetService('contracts').OpenCreateContract, (None, self.contract)))
        typeID = None
        if self.contract.items and len(self.contract.items) == 1:
            typeID = self.contract.items[0].itemTypeID
        m += [(MenuLabel('UI/Contracts/ContractEntry/FindRelated'), ('isDynamic', sm.GetService('contracts').GetRelatedMenu, (self.contract.contract, typeID)))]
        m += [None]
        m += [(MenuLabel('UI/Contracts/ContractsWindow/PreviouslyViewedContracts'), ('isDynamic', self._GetLatestContractsForHistory, ()))]
        return m

    def GetDivisionName(self, corpFlag):
        if corpFlag == const.flagCorpDeliveries:
            return GetByLabel('UI/Contracts/ContractsWindow/Deliveries')
        division = const.corpDivisionsByFlag[corpFlag]
        divName = sm.GetService('corp').GetDivisionNames()[division + 1]
        return divName

    def _GetCorpDivisions(self):
        m = []
        for eachFlagID in const.flagCorpSAGs:
            text = self.GetDivisionName(eachFlagID)
            m.append((text, self._OpenCreateContractForCorp, (self.contract, eachFlagID)))

        if session.corprole & (const.corpRoleAccountant | const.corpRoleJuniorAccountant | const.corpRoleTrader):
            m.append((GetByLabel('UI/Contracts/ContractsWindow/Deliveries'), self._OpenCreateContractForCorp, (self.contract, const.flagCorpDeliveries)))
        return m

    def _OpenCreateContractForCorp(self, contract, corpFlagID):
        settings.char.ui.Set('contracts_lastCopiedDiv', corpFlagID)
        sm.GetService('contracts').OpenCreateContract(None, contract, corpFlagID)

    def _GetLatestContractsForHistory(self):
        m = []
        for i in range(len(self.history)):
            h = self.history[-(i + 1)]
            m.append((h.title, self.SelectHistory, (h.contractID, h.solarSystemID)))

        return m

    def SelectHistory(self, contractID, solarSystemID):
        sm.GetService('contracts').ShowContract(contractID)

    def AddButton(self, which):
        caption = function = None
        if which == BCancel:
            caption = GetByLabel('UI/Common/Close')
            function = self.Cancel
        elif which == BAccept:
            caption = GetByLabel('UI/Contracts/ContractsWindow/Accept')
            function = self.Accept
        elif which == BAcceptForCorp:
            caption = GetByLabel('UI/Contracts/ContractsWindow/AcceptForCorp')
            function = self.AcceptForCorp
        elif which == BReject:
            caption = GetByLabel('UI/Contracts/ContractsWindow/Reject')
            function = self.Reject
        elif which == BComplete:
            caption = GetByLabel('UI/Contracts/ContractsWindow/Complete')
            function = self.Complete
        elif which == BDelete:
            caption = GetByLabel('UI/Contracts/ContractsWindow/Delete')
            function = self.Delete
        elif which == BSucceed:
            caption = GetByLabel('UI/Contracts/ContractsWindow/Succeed')
            function = self.Succeed
        elif which == BFail:
            caption = GetByLabel('UI/Contracts/ContractsWindow/Fail')
            function = self.Fail
        elif which == BGetItems:
            caption = GetByLabel('UI/Contracts/ContractEntry/GetItems')
            function = self.GetItems
        elif which == BGetMoney:
            caption = GetByLabel('UI/Contracts/ContractEntry/GetMoney')
            function = self.GetMoney
        elif which == BPlaceBid:
            caption = GetByLabel('UI/Contracts/ContractEntry/PlaceBid')
            function = self.PlaceBid
        button = (caption,
         function,
         (),
         84)
        self.buttons.append(button)

    def Cancel(self):
        self.Close()

    def TryHideLoad(self):
        try:
            self.HideLoad()
        except:
            pass

    def Accept(self):
        try:
            self.ShowLoad()
            if sm.GetService('contracts').AcceptContract(self.contractID, False):
                if not self or self.destroyed:
                    return
                self.Init()
        finally:
            self.TryHideLoad()

    def AcceptForCorp(self):
        try:
            self.ShowLoad()
            if sm.GetService('contracts').AcceptContract(self.contractID, True):
                self.Init()
        finally:
            self.TryHideLoad()

    def Reject(self):
        try:
            self.ShowLoad()
            if sm.GetService('contracts').RejectContract(self.contractID):
                self.Init()
        finally:
            self.TryHideLoad()

    def Complete(self):
        try:
            self.ShowLoad()
            if sm.GetService('contracts').CompleteContract(self.contractID):
                self.Init()
        finally:
            self.TryHideLoad()

    def Delete(self):
        try:
            self.ShowLoad()
            if sm.GetService('contracts').DeleteContract(self.contractID):
                self.Close()
        finally:
            try:
                self.TryHideLoad()
            except:
                pass

    def Succeed(self):
        try:
            self.ShowLoad()
            if sm.GetService('contracts').CompleteContract(self.contractID):
                self.Init()
        finally:
            self.TryHideLoad()

    def Fail(self):
        try:
            self.ShowLoad()
            if sm.GetService('contracts').FailContract(self.contractID):
                self.Init()
        finally:
            self.TryHideLoad()

    def GetItems(self):
        try:
            self.ShowLoad()
            sm.GetService('contracts').FinishAuction(self.contractID, False)
            self.Init()
        finally:
            self.TryHideLoad()

    def GetMoney(self):
        try:
            self.ShowLoad()
            sm.GetService('contracts').FinishAuction(self.contractID, True)
            self.Init()
        finally:
            self.TryHideLoad()

    def PlaceBid(self):
        try:
            self.ShowLoad()
            if sm.GetService('contracts').PlaceBid(self.contractID):
                if not self.destroyed:
                    self.Init()
        finally:
            self.TryHideLoad()

    def InsertItemList(self, contract, title, inCrate, numRows, hint = None, fixedSize = False, forceList = False):
        shouldHideBlueprintInfo = contract.contract.status in [const.conStatusFinished, const.conStatusFinishedContractor]
        items = [ e for e in contract.items if e.inCrate == inCrate ]
        if len(items) == 0:
            if len(contract.items) > 1:
                return True
            else:
                return False
        else:
            titleParent = Container(name='title', parent=self.sr.main, align=uiconst.TOTOP, width=const.defaultPadding)
            boldTitle = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=title)
            title = eveLabel.EveLabelLarge(text=boldTitle, parent=titleParent, top=6, idx=0, state=uiconst.UI_NORMAL, left=6)
            titleParent.height = title.textheight + 6
            if len(items) == 1 and not forceList:
                item = items[0]
                typeID = item.itemTypeID
                itemID = item.itemID
                groupName = evetypes.GetGroupName(item.itemTypeID)
                isCorpse = evetypes.GetGroupID(item.itemTypeID) == const.groupBiomass
                categoryID = evetypes.GetCategoryID(item.itemTypeID)
                categoryName = CategoryName(categoryID)
                details = ''
                if categoryID == const.categoryBlueprint:
                    if item.copy == 1:
                        if shouldHideBlueprintInfo:
                            details = GetByLabel('UI/Contracts/ContractsService/BlueprintCopy')
                        else:
                            details = GetByLabel('UI/VirtualGoodsStore/BlueprintCopy', runs=item.licensedProductionRunsRemaining or 0, materialLevel=item.materialLevel or 0, productivityLevel=item.productivityLevel or 0)
                    elif shouldHideBlueprintInfo:
                        details = GetByLabel('UI/Contracts/ContractsService/BlueprintOriginal')
                    else:
                        details = GetByLabel('UI/VirtualGoodsStore/OriginalBlueprint', materialLevel=item.materialLevel or 0, productivityLevel=item.productivityLevel or 0)
                descParent = Container(name='desc', parent=self.sr.main, align=uiconst.TOTOP, left=const.defaultPadding, top=const.defaultPadding, height=80)
                leftParent = Container(name='leftParent', parent=descParent, align=uiconst.TOLEFT, width=72)
                infoParent = Container(name='infoParent', parent=descParent, align=uiconst.TOALL, padding=(8,
                 2,
                 const.defaultPadding,
                 0))
                if getattr(item, 'copy', False):
                    isCopy = True
                else:
                    isCopy = False
                icon = ItemIcon(parent=leftParent, typeID=typeID, itemID=itemID, isCopy=isCopy, width=64, height=64, align=uiconst.TOPRIGHT)
                if eveCfg.IsPreviewable(typeID):
                    setattr(icon, 'typeID', typeID)
                    icon.cursor = uiconst.UICURSOR_MAGNIFIER
                    icon.OnClick = (self.OnPreviewClick, icon)
                captionText = GetByLabel('UI/Contracts/ContractsService/NameXQuantity', typeID=item.itemTypeID, quantity=FmtAmt(max(1, item.quantity)))
                self.info_caption = eveLabel.EveCaptionSmall(parent=infoParent, text=captionText, padRight=16)
                top = self.info_caption.textheight
                self.corpseNameLabel = None
                if isCorpse:
                    corpseName = GetCorpseName(itemID)
                    if corpseName:
                        self.corpseNameLabel = eveLabel.EveLabelMedium(parent=infoParent, top=top, text=corpseName)
                        top += self.corpseNameLabel.textheight
                self.infolink = InfoIcon(itemID=itemID, typeID=typeID, left=0, top=const.defaultPadding, parent=infoParent, idx=0)
                self.infolink.left = self.info_caption.textwidth + 8
                categoryAndGroupText = GetByLabel('UI/Contracts/ContractEntry/CategoryAndGroup', categoryName=categoryName, groupName=groupName)
                self.categoryAndGroup = eveLabel.EveLabelMedium(parent=infoParent, top=top, text=categoryAndGroupText)
                top += self.categoryAndGroup.textheight
                if GetItemDamageText(item):
                    damageAndTextilsText = '<color=red>%s</color> %s' % (GetItemDamageText(item), details)
                else:
                    damageAndTextilsText = details
                self.damageAndTextils = eveLabel.EveLabelMedium(parent=infoParent, top=top, text=damageAndTextilsText)
                return False
            if fixedSize:
                self.sr.scroll = eveScroll.Scroll(parent=self.sr.main, align=uiconst.TOTOP, padding=(const.defaultPadding,
                 const.defaultPadding,
                 const.defaultPadding,
                 const.defaultPadding), height=100)
            else:
                self.sr.scroll = eveScroll.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
                 const.defaultPadding,
                 const.defaultPadding,
                 const.defaultPadding))
            self.sr.scroll.sr.id = 'contractDetailScroll'
            self.sr.data = {'items': []}
            parents = []
            children = []
            for item in items:
                if not item.parentID:
                    parents.append(item)
                else:
                    children.append(item)

            items = []
            for parent in parents:
                items.append(parent)
                for child in children:
                    if child.parentID == parent.itemID:
                        items.append(child)

            for child in children:
                for item in items:
                    if child.itemID == item.itemID:
                        break
                else:
                    items.append(child)

            scrolllist = []
            itemsByParentID = defaultdict(set)
            for eachItem in items:
                itemsByParentID[eachItem.parentID].add(eachItem)

            for item in items:
                if item.inCrate != inCrate:
                    continue
                typeName = evetypes.GetName(item.itemTypeID)
                groupName = evetypes.GetGroupName(item.itemTypeID)
                categoryName = evetypes.GetCategoryName(item.itemTypeID)
                categoryID = evetypes.GetCategoryID(item.itemTypeID)
                details = ''
                isBlueprint = False
                isCopy = False
                if categoryID == const.categoryBlueprint:
                    isBlueprint = True
                    if item.copy == 1:
                        isCopy = True
                        if shouldHideBlueprintInfo:
                            details = GetByLabel('UI/Contracts/ContractsService/BlueprintCopy')
                        else:
                            details = GetByLabel('UI/VirtualGoodsStore/BlueprintCopy', runs=item.licensedProductionRunsRemaining or 0, materialLevel=item.materialLevel or 0, productivityLevel=item.productivityLevel or 0)
                    elif shouldHideBlueprintInfo:
                        details = GetByLabel('UI/Contracts/ContractsService/BlueprintOriginal')
                    else:
                        details = GetByLabel('UI/VirtualGoodsStore/OriginalBlueprint', materialLevel=item.materialLevel or 0, productivityLevel=item.productivityLevel or 0)
                elif item.flagID:
                    details = GetShipFlagLocationName(item.flagID)
                chld = ''
                sublevel = 0
                if item.parentID > 0:
                    chld = ' '
                    sublevel = 1
                mrdmg = GetItemDamageText(item)
                quantity = max(1, item.quantity) if item.quantity is not None else None
                quantityLabel = localization.formatters.FormatNumeric(quantity, useGrouping=True)
                if forceList:
                    label = '%s%s<t>%s<t>%s' % (chld,
                     typeName,
                     quantityLabel,
                     groupName)
                    hdr = [GetByLabel('UI/Contracts/ContractsWindow/Name'), GetByLabel('UI/Inventory/ItemQuantityShort'), GetByLabel('UI/Common/Type')]
                else:
                    label = '%s%s<t>%s<t>%s<t>%s<t>%s%s' % (chld,
                     typeName,
                     quantityLabel,
                     groupName,
                     categoryName,
                     details,
                     mrdmg)
                    hdr = [GetByLabel('UI/Contracts/ContractsWindow/Name'),
                     GetByLabel('UI/Inventory/ItemQuantityShort'),
                     GetByLabel('UI/Common/Type'),
                     GetByLabel('UI/Common/Category'),
                     GetByLabel('UI/Common/Details')]
                scrolllist.append(GetFromClass(Item, {'itemID': item.itemID,
                 'typeID': item.itemTypeID,
                 'label': label,
                 'getIcon': 1,
                 'isBlueprint': isBlueprint,
                 'isCopy': isCopy,
                 'GetMenu': GetContractItemMenu,
                 'sublevel': sublevel,
                 'childrenItems': itemsByParentID.get(item.itemID, set()),
                 'sort_%s' % GetByLabel('UI/Inventory/ItemQuantityShort'): quantity,
                 'LoadTooltipPanelFunc': self.LoadItemTooltipPanel}))

            self.sr.scroll.Load(None, scrolllist, headers=hdr)
            if len(scrolllist) >= 1:
                hint = None
            elif hint is None:
                hint = GetByLabel('UI/Contracts/ContractsWindow/NoItemsFound')
            self.sr.scroll.ShowHint(hint)
            return not fixedSize

    def LoadItemTooltipPanel(self, tooltipPanel, itemID, typeID):
        if evetypes.GetGroupID(typeID) == const.groupBiomass:
            corpseName = GetCorpseName(itemID)
            if corpseName:
                tooltipPanel.LoadGeneric1ColumnTemplate()
                tooltipPanel.AddTextBodyLabel(text=corpseName)

    def OnPreviewClick(self, wnd, *args):
        sm.GetService('preview').PreviewType(getattr(wnd, 'typeID'))

    def UpdateTexts(self):
        if hasattr(self, 'info_caption'):
            self.infolink.left = self.info_caption.textwidth + 8
            top = self.info_caption.textheight
            if self.corpseNameLabel:
                top += self.corpseNameLabel.textheight
            self.categoryAndGroup.top = top
            top += self.categoryAndGroup.textheight
            self.damageAndTextils.top = top

    def _OnResize(self, *args):
        self.UpdateTexts()

    def LoadTabs(self):
        pass

    def Load(self, key):
        pass

    def Confirm(self, *etc):
        pass

    def GetError(self, checkNumber = 1):
        return ''

    def Error(self, error):
        if error:
            eve.Message('CustomInfo', {'info': error})

    def HistoryAdd(self, id, solarSystemID, title):
        self.HistoryRemove(id)
        kv = utillib.KeyVal()
        kv.contractID = id
        kv.solarSystemID = solarSystemID
        kv.title = title
        self.history.append(kv)
        if len(self.history) > HISTORY_LENGTH:
            del self.history[0]
        settings.user.ui.Set('contracts_history', self.history)

    def HistoryRemove(self, id):
        for i in range(len(self.history)):
            if self.history[i].contractID == id:
                del self.history[i]
                return


def AddBasicInfoRow(key, val):
    boldKey = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=key)
    return '%(key)s<t>%(val)s<br>' % {'key': boldKey,
     'val': val}


def GetBasicInfoText(c):
    isContractMgr = session.corprole & const.corpRoleContractManager == const.corpRoleContractManager
    text = ''
    desc = c.title
    if desc == '':
        desc = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
    else:
        desc = GetByLabel('UI/Contracts/ContractsWindow/ContractDescription', description=desc)
    text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/InfoByIssuer'), '<color=0xff999999>%s</color>' % desc)
    text += AddBasicInfoRow(GetByLabel('UI/Common/Type'), contractscommon.GetContractTypeText(c.type))
    if c.forCorp:
        issuerID = c.issuerCorpID
    else:
        issuerID = c.issuerID
    try:
        issuer = cfg.eveowners.Get(issuerID)
        issuerTypeID = issuer.typeID
        issuerName = issuer.ownerName
    except:
        issuerTypeID = cfg.eveowners.Get(session.charid).typeID
        issuerName = GetByLabel('UI/Contracts/ContractsWindow/UnknownSystem')
        log.LogException()

    issuedByURL = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=issuerName, info=('showinfo', issuerTypeID, issuerID))
    issuedByLabel = GetByLabel('UI/Contracts/ContractsWindow/IssuedBy')
    text += AddBasicInfoRow(issuedByLabel, issuedByURL)
    isPrivate = not not c.availability
    if isPrivate:
        assignee = cfg.eveowners.Get(c.assigneeID)
        a = GetByLabel('UI/Contracts/ContractsWindow/PrivateWithLink', showInfoName=assignee.name, info=('showinfo', assignee.typeID, c.assigneeID))
    else:
        if c.startRegionID == session.regionid:
            reg = GetByLabel('UI/Contracts/ContractsWindow/CurrentRegion')
        else:
            reg = GetByLabel('UI/Contracts/ContractEntry/OtherRegion')
        a = GetByLabel('UI/Contracts/ContractsService/RegionInfo', regionHeader=GetByLabel('UI/Common/LocationTypes/Region'), region=c.startRegionID, currentOrOther=reg)
    text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/Availability'), a)
    if c.acceptorID > 0 and (c.status != const.conStatusInProgress or c.issuerID == session.charid or c.issuerCorpID == session.corpid and c.forCorp or c.acceptorID == session.charid or c.acceptorID == session.corpid):
        acceptor = cfg.eveowners.Get(c.acceptorID)
        more = ''
        if c.acceptorID == session.corpid and isContractMgr and c.acceptorWalletKey is not None:
            more = GetByLabel('UI/Contracts/ContractsService/WalletDivisionAccountName', accountName=sm.GetService('corp').GetCorpAccountName(c.acceptorWalletKey))
        acceptorURL = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLinkWithMore', showInfoName=acceptor.ownerName, info=('showinfo', acceptor.typeID, c.acceptorID), more=more)
        contractorLabel = GetByLabel('UI/Contracts/ContractsWindow/Contractor')
        text += AddBasicInfoRow(contractorLabel, acceptorURL)
    st = contractscommon.GetContractStatusText(c.status, c.type)
    if c.status == const.conStatusFailed:
        textToBold = '<color=red>%s</color>' % st
        st = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=textToBold)
    boldStatus = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=GetByLabel('UI/Contracts/ContractsWindow/Status'))
    text += '%(statusKey)s<t>%(status)s<br>' % {'statusKey': boldStatus,
     'status': st}
    if c.startStationID == 0:
        loc = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
    else:
        if idCheckers.IsStation(c.startStationID):
            startStationTypeID = sm.GetService('ui').GetStationStaticInfo(c.startStationID).stationTypeID
        else:
            startStationTypeID = sm.GetService('structureDirectory').GetStructureInfo(c.startStationID).typeID
        dot = sm.GetService('contracts').GetSystemSecurityDot(c.startSolarSystemID)
        loc = GetByLabel('UI/Contracts/ContractsWindow/StationLinkWithDot', dot=dot, station=c.startStationID, info=('showinfo', startStationTypeID, c.startStationID))
        if c.startStationID == session.stationid:
            loc += '<br><t>%s' % GetByLabel('UI/Generic/CurrentStation')
        elif c.startSolarSystemID == session.solarsystemid:
            loc += '<br><t>%s' % GetByLabel('UI/Generic/CurrentSystem')
            if not idCheckers.IsStation(c.startStationID):
                loc += ' - <color=0xffbb0000>%s</color>' % GetByLabel('UI/Contracts/ContractEntry/MightBeInaccessible')
        else:
            if not idCheckers.IsStation(c.startStationID):
                loc += '<br><t><color=0xffbb0000>%s</color>' % GetByLabel('UI/Contracts/ContractEntry/MightBeInaccessible')
            jumpsToStartSystem = sm.GetService('clientPathfinderService').GetAutopilotJumpCount(session.solarsystemid2, c.startSolarSystemID)
            mr = sm.GetService('contracts').GetRouteSecurityWarning(session.solarsystemid2, c.startSolarSystemID)
            if jumpsToStartSystem <= contractscommon.NUMJUMPS_UNREACHABLE:
                loc += '<br><t>'
                loc += GetByLabel('UI/Common/NumJumpsAway', numJumps=int(jumpsToStartSystem))
            if mr:
                loc += '<br><t>%s' % mr
    text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/Location'), loc)
    if c.type != const.conTypeAuction or c.status != const.conStatusOutstanding or session.charid == c.issuerID:
        text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/DateIssued'), FmtDate(c.dateIssued, 'ss'))
    if c.status == const.conStatusInProgress:
        cb = c.dateAccepted + const.DAY * c.numDays
        if cb < blue.os.GetWallclockTime() + const.HOUR:
            if cb - blue.os.GetWallclockTime() < 0:
                timeLeftLabel = GetByLabel('UI/Contracts/ContractEntry/Overdue')
            else:
                timeLeftLabel = GetByLabel('UI/Contracts/ContractsService/TimeLeftWithoutLabelVerbose', time=FmtDate(cb, 'ls'), timeLeft=FmtDate(cb - blue.os.GetWallclockTime(), 'ls'))
            cb = '<color=red>%s</color>' % timeLeftLabel
        else:
            cb = FmtDate(cb, 'ls')
        text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/CompleteBefore'), cb)
    elif c.status != const.conStatusOutstanding:
        text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/DateCompleted'), FmtDate(c.dateCompleted, 'ls'))
    elif c.type != const.conTypeAuction:
        expirationDateLabel = GetByLabel('UI/Contracts/ContractsService/ExpirationDate', expiredOn=FmtDate(c.dateExpired, 'ls'), timeSinceExpired=ConFmtDate(c.dateExpired - blue.os.GetWallclockTime(), False))
        text += AddBasicInfoRow(GetByLabel('UI/Contracts/ContractsWindow/ExpirationDate'), expirationDateLabel)
    return text


def GetItemDamageText(item):
    dmg = 0
    if item.damage:
        for attribute in dogma_data.get_type_attributes(item.itemTypeID):
            if attribute.attributeID == const.attributeHp and attribute.value:
                dmg = item.damage / attribute.value
                dmg = int(dmg * 100)
                break

    txt = ''
    if dmg > 0:
        txt = ' <color=0xffff4444>%s</color>' % GetByLabel('UI/Contracts/ContractsService/PercentDamaged', percent=dmg)
    return txt


def GetContractItemMenu(entry, *args):
    node = entry.sr.node
    typeID = entry.typeID
    itemID = entry.itemID
    m = []
    if evetypes.GetCategoryID(typeID) == const.categoryShip:
        m += [(MenuLabel('UI/Fitting/FittingWindow/SimulateShipFitting'), SimulateShipFromContract, (typeID, node.childrenItems))]
    m += GetMenuService().GetMenuFromItemIDTypeID(itemID, entry.typeID, includeMarketDetails=True)
    return m


def SimulateShipFromContract(shipTypeID, fittedItems):
    fittedItems = {Bundle(typeID=x.itemTypeID, itemID=x.itemID, flagID=x.flagID, categoryID=evetypes.GetCategoryID(x.itemTypeID), groupID=evetypes.GetGroupID(x.itemTypeID), stacksize=x.quantity) for x in fittedItems}
    fitData, _ = sm.GetService('fittingSvc').GetFittingDictFromItems(fittedItems, putModuleAmmoInCargo=False)
    fitting = utillib.KeyVal(shipTypeID=shipTypeID, fitData=fitData)
    sm.GetService('ghostFittingSvc').SimulateFitting(fitting)
