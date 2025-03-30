#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_home.py
import sys
import blue
import log
import evetypes
import localization
from carbon.common.script.sys.row import Row
from carbon.common.script.util.timerstuff import AutoTimer
import carbonui
from carbonui import ButtonVariant, Density, uiconst, Align
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from carbonui.util.sortUtil import SortListOfTuples
import eveicon
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.label_text import LabelTextSides, LabelTextSidesMoreInfo, LabelTextTop, LabelMultilineTextTop
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveIcon import CorpIcon, OwnerIcon
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.infoIcon import MoreInfoIcon, InfoIcon
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.client.script.ui.shared.neocom.corporation.corp_dlg_editcorpdetails import EditCorpDetails, CreateCorp
from eve.client.script.ui.shared.neocom.wallet.walletUtil import FmtWalletCurrency
from eve.client.script.ui.util.uix import HybridWnd
from eve.common.lib import appConst as const
from eve.common.script.sys.idCheckers import IsNPC
from eveexceptions import UserError
from eveservices.menu import GetMenuService
from evewar.warPermitUtil import GetLabelPathForAllowWar
from globalConfig.getFunctions import IsContentComplianceControlSystemActive
from localization import GetByLabel, formatters
from menu import MenuLabel
from menucheckers import SessionChecker
ICON_SIZE = 128

class CorpUIHome(Container):
    is_initializing = False
    is_loaded = False
    is_opening_dividend_form = False

    def ApplyAttributes(self, attributes):
        super(CorpUIHome, self).ApplyAttributes(attributes)
        self.details_scroll = None

    def Load(self, panelID = None, *args):
        if not self.is_loaded:
            self.is_loaded = True
            self.ConstructDetailsLayout()
            corpUISignals.on_corporation_changed.connect(self.on_corporation_changed)
        self.PopulateDetailsScroll()
        self.UpdateOfficeJumpCounts()

    def on_corporation_changed(self, corp_id):
        self.reconstruct_top_cont()

    def ConstructDetailsLayout(self):
        btnGroup = ButtonGroup(parent=self)
        canEditCorp = not IsNPC(session.corpid) and SessionChecker(session, None).IsCorpDirector()
        if canEditCorp:
            btn = btnGroup.AddButton(GetByLabel('UI/Corporations/CorpUIHome/EditDetails'), self.EditDetails)
            if IsContentComplianceControlSystemActive(sm.GetService('machoNet')):
                btn.Disable()
        if sm.GetService('corp').UserIsCEO():
            btnGroup.AddButton(GetByLabel('UI/Corporations/CorpUIHome/Dividends'), self.PayoutDividendForm)
            btn = btnGroup.AddButton(GetByLabel('UI/Corporations/CorpUIHome/Divisions'), self.DivisionsForm)
            if IsContentComplianceControlSystemActive(sm.GetService('machoNet')):
                btn.Disable()
        else:
            btnGroup.AddButton(GetByLabel('UI/Corporations/CorpUIHome/CreateNewCorp'), self.CreateCorpForm)
            if not IsNPC(session.corpid):
                corpSvc = sm.StartService('corp')
                canLeave, error, errorDetails = corpSvc.CanLeaveCurrentCorporation()
                if not canLeave and error == 'CrpCantQuitNotInStasis':
                    btnGroup.AddButton(GetByLabel('UI/Corporations/CorpUIHome/PrepareQuitCorporation'), self.RemoveAllRoles)
                else:
                    btnGroup.AddButton(GetByLabel('UI/Corporations/CorpUIHome/QuitCorp'), self.ResignFromCorp)
                if corpSvc.UserBlocksRoles():
                    btnGroup.AddButton(GetByLabel('UI/Corporations/Common/AllowCorpRoles'), self.AllowRoles)
        self.top_cont = ContainerAutoSize(name='top_cont', parent=self, align=Align.TOTOP)
        self.reconstruct_top_cont()
        self.details_scroll = Scroll(name='detailsScroll', parent=self, padTop=16)

    def reconstruct_top_cont(self):
        self.top_cont.Flush()
        if IsNPC(session.corpid):
            OwnerIcon(ownerID=session.corpid, parent=self.top_cont, align=uiconst.CENTERLEFT, pos=(0,
             0,
             ICON_SIZE,
             ICON_SIZE))
        else:
            CorpIcon(corpID=session.corpid, parent=self.top_cont, align=uiconst.CENTERLEFT, pos=(0,
             0,
             ICON_SIZE,
             ICON_SIZE))
        caption = carbonui.TextHeadline(text=cfg.eveowners.Get(session.corpid).ownerName, parent=self.top_cont, align=uiconst.CENTERLEFT, left=ICON_SIZE + 8)
        InfoIcon(typeID=const.typeCorporation, itemID=session.corpid, parent=self.top_cont, left=caption.left + caption.width + 6, top=2, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT)

    def EditDetails(self, *args):
        if not SessionChecker(session, None).IsCorpDirector():
            eve.Message('OnlyCEOOrEquivCanEditCorp')
            return
        EditCorpDetails.Open()

    def PayoutDividendForm(self, *args):
        if self.is_opening_dividend_form:
            return
        self.is_opening_dividend_form = True
        try:
            if not sm.GetService('corp').UserIsCEO():
                eve.Message('OnlyCEOCanPayoutDividends')
                return
            maxAmount = sm.RemoteSvc('account').GetCashBalance(1, 1000)
            if maxAmount < 1:
                eve.Message('CorpHasNoMoneyToPayoutDividends')
                return
            format = [{'type': 'push',
              'frame': 0},
             {'type': 'text',
              'text': GetByLabel('UI/Corporations/CorpUIHome/HintSelectDividend'),
              'frame': 0},
             {'type': 'push',
              'frame': 0},
             {'type': 'push',
              'frame': 0}]
            payShareholders = 0
            payMembers = 1
            format.append({'type': 'text',
             'text': GetByLabel('UI/Corporations/CorpUIHome/PayDividendTo'),
             'frame': 0})
            format.append({'type': 'checkbox',
             'required': 1,
             'group': 'OdividendType',
             'height': 16,
             'setvalue': 1,
             'key': payShareholders,
             'label': '',
             'text': GetByLabel('UI/Corporations/CorpUIHome/Shareholders'),
             'frame': 0})
            format.append({'type': 'checkbox',
             'required': 1,
             'group': 'OdividendType',
             'height': 16,
             'setvalue': 0,
             'key': payMembers,
             'label': '',
             'text': GetByLabel('UI/Corporations/CorpUIHome/Members'),
             'frame': 0})
            format.append({'type': 'push',
             'frame': 0})
            format.append({'type': 'push',
             'frame': 0})
            format.append({'type': 'text',
             'text': GetByLabel('UI/Corporations/CorpUIHome/EnterTotalAmount'),
             'frame': 0})
            format.append({'type': 'text',
             'text': GetByLabel('UI/Corporations/CorpUIHome/AmountWillBeDivided'),
             'frame': 0})
            format.append({'type': 'edit',
             'key': 'payoutAmount',
             'setvalue': 1,
             'label': GetByLabel('UI/Corporations/CorpUIHome/Amount'),
             'frame': 0,
             'floatonly': [1, maxAmount]})
            format.append({'type': 'push',
             'frame': 0})
            format.append({'type': 'bbline'})
            retval = HybridWnd(format=format, caption=GetByLabel('UI/Corporations/CorpUIHome/PayDividend'), windowID='payDividend', modal=1, minW=340, minH=256, ignoreCurrent=0)
            if retval is not None:
                payShareholders = [1, 0][retval['OdividendType']]
                payoutAmount = retval['payoutAmount']
                sm.GetService('corp').PayoutDividend(payShareholders, payoutAmount)
        finally:
            self.is_opening_dividend_form = False

    def DivisionsForm(self, *args):
        if not sm.GetService('corp').UserIsCEO():
            eve.Message('CorpAccessOnlyCEOEditDivisionNames')
            return
        divisions = sm.GetService('corp').GetDivisionNames()
        format = [{'type': 'push',
          'frame': 0}, {'type': 'text',
          'frame': 0,
          'text': GetByLabel('UI/Corporations/CorpUIHome/AssignNames')}, {'type': 'push',
          'frame': 0}]
        labelWidth = 160
        for i in range(1, 8):
            key = 'division%s' % i
            format.append({'type': 'edit',
             'setvalue': divisions[i],
             'label': GetByLabel('UI/Corporations/CorpUIHome/DivisionName', index=i),
             'key': key,
             'frame': 0,
             'labelwidth': labelWidth,
             'maxlength': 50})

        format.append({'type': 'edit',
         'readonly': True,
         'label': GetByLabel('UI/Corporations/CorpUIHome/WalletDivisionName', index=1),
         'setvalue': GetByLabel('UI/Corporations/Common/CorporateDivisionMasterWallet'),
         'frame': 0,
         'labelwidth': labelWidth,
         'key': 'division8'})
        for i in range(9, 15):
            key = 'division%s' % i
            format.append({'type': 'edit',
             'setvalue': divisions[i],
             'label': GetByLabel('UI/Corporations/CorpUIHome/WalletDivisionName', index=i - 7),
             'key': key,
             'frame': 0,
             'labelwidth': labelWidth,
             'maxlength': 50})

        format.append({'type': 'push',
         'frame': 0})
        format.append({'type': 'errorcheck',
         'errorcheck': self.ApplyDivisionNames})
        wnd = HybridWnd(format=format, caption=GetByLabel('UI/Corporations/CorpUIHome/DivisionNamesCaption'), windowID='divisionName', modal=0, minW=450, ignoreCurrent=0)
        if wnd:
            wnd.Maximize()

    def ApplyDivisionNames(self, retval):

        def KeyToInt(k):
            return int(k[len('division'):])

        new = dict([ (KeyToInt(k), v) for k, v in retval.iteritems() ])
        allNames = sm.GetService('corp').GetDivisionNames()
        current = {key:allNames[key] for key in range(1, 15)}
        currentNamesForNewKeys = dict([ (k, current[k]) for k in new.iterkeys() ])
        if new != currentNamesForNewKeys:
            try:
                sm.GetService('corp').UpdateDivisionNames(*[ new.get(k, current[k]) for k in range(1, len(current) + 1) ])
            except UserError as e:
                msg = cfg.GetMessage(e.msg, e.dict)
                if msg.type == 'notify' and e.msg.find('CorpDiv') > -1:
                    sys.exc_clear()
                    return msg.text
                raise

        return ''

    def CreateCorpForm(self, *args):
        wnd = CreateCorp.GetIfOpen()
        if wnd is not None:
            wnd.Maximize()
        else:
            sm.GetService('sessionMgr').PerformSessionChange('corp.addcorp', self.ShowCreateCorpForm)

    @staticmethod
    def ShowCreateCorpForm(*args):
        if not session.stationid:
            eve.Message('CanOnlyCreateCorpInStation')
            session.ResetSessionChangeTimer('Failed criteria for creating a corporation')
            return
        if not sm.GetService('corp').MemberCanCreateCorporation():
            cost = sm.GetService('corp').GetCostForCreatingACorporation()
            eve.Message('PlayerCantCreateCorporation', {'cost': cost})
            session.ResetSessionChangeTimer('Failed criteria for creating a corporation')
            return
        if sm.GetService('corp').UserIsCEO():
            eve.Message('CEOCannotCreateCorporation')
            session.ResetSessionChangeTimer('Failed criteria for creating a corporation')
            return
        CreateCorp.Open()

    def PopulateDetailsScroll(self):
        if not self.details_scroll:
            return
        try:
            scrolllist = []
            existingNodes = self.details_scroll.GetNodes()
            self.ShowMyCorporationsDetails(scrolllist)
            if not len(existingNodes) and not len([ n for n in existingNodes if n['id'] == ('corporation', 'offices') ]):
                self.ShowMyCorporationsOffices(scrolllist)
            if len(scrolllist):
                self.details_scroll.Load(contentList=scrolllist)
        except:
            log.LogException()
            sys.exc_clear()

    def ShowMyCorporationsDetails(self, scrolllist):
        scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetSubContentDetails,
         'label': GetByLabel('UI/Common/Details'),
         'groupItems': None,
         'id': ('corporation', 'details'),
         'tabs': [],
         'state': 'locked',
         'showicon': 'hide'}))
        uicore.registry.SetListGroupOpenState(('corporation', 'details'), 1)

    def GetSubContentDetails(self, nodedata, *args):
        scrolllist = []
        corpinfo = sm.GetService('corp').GetCorporation()
        founderdone = 0
        if evetypes.GetGroupID(cfg.eveowners.Get(corpinfo.ceoID).typeID) == const.groupCharacter:
            if corpinfo.creatorID == corpinfo.ceoID:
                ceoLabel = 'UI/Corporations/CorpUIHome/CeoAndFounder'
                founderdone = 1
            else:
                ceoLabel = 'UI/Corporations/Common/CEO'
            scrolllist.append(self.GetListEntry(ceoLabel, GetByLabel('UI/Corporations/CorpUIHome/PlayerNamePlaceholder', player=corpinfo.ceoID), typeID=const.typeCharacter, itemID=corpinfo.ceoID))
        if not founderdone and evetypes.GetGroupID(cfg.eveowners.Get(corpinfo.creatorID).typeID) == const.groupCharacter:
            scrolllist.append(self.GetListEntry('UI/Corporations/Common/Founder', GetByLabel('UI/Corporations/CorpUIHome/PlayerNamePlaceholder', player=corpinfo.creatorID), typeID=const.typeCharacter, itemID=corpinfo.creatorID))
        if corpinfo.stationID:
            uiService = sm.GetService('ui')
            stationID = corpinfo.stationID
            station = uiService.GetStationStaticInfo(stationID)
            stationTypeID = station.stationTypeID
            stationName = uiService.GetStationName(stationID)
            row = Row(['stationID', 'typeID'], [stationID, stationTypeID])
            scrolllist.append(self.GetListEntry(label='UI/Corporations/CorpUIHome/Headquarters', text=stationName, typeID=stationTypeID, itemID=stationID, station=row))
        scrolllist.append(self.GetListEntry('UI/Corporations/CorpUIHome/TickerName', GetByLabel('UI/Corporations/CorpUIHome/TickerNamePlaceholder', ticker=corpinfo.tickerName)))
        scrolllist.append(self.GetListEntry('UI/Corporations/CorpUIHome/Shares', formatters.FormatNumeric(value=corpinfo.shares)))
        if not IsNPC(session.corpid):
            scrolllist.append(self.GetListEntry('UI/Corporations/CorpUIHome/MemberCount', formatters.FormatNumeric(value=corpinfo.memberCount)))
        isk_tax_label = GetByLabel('UI/Corporations/CorpUIHome/ISKTaxRate')
        isk_tax_text = GetByLabel('UI/Corporations/CorpUIHome/TaxRatePlaceholder', tax=corpinfo.taxRate * 100)
        isk_tax_min_isk_text = FmtWalletCurrency(amt=const.minCorporationTaxAmount, currency=const.creditsISK)
        isk_tax_more_info_hint = GetByLabel('UI/Corporations/BaseCorporationUI/ISKTaxRateDescription', min_isk_amount=isk_tax_min_isk_text)
        scrolllist.append(GetFromClass(LabelTextSidesMoreInfo, {'line': 1,
         'label': isk_tax_label,
         'text': isk_tax_text,
         'moreInfoHint': isk_tax_more_info_hint}))
        lp_tax_label = GetByLabel('UI/Corporations/CorpUIHome/LPTaxRate')
        lp_tax_text = GetByLabel('UI/Corporations/CorpUIHome/TaxRatePlaceholder', tax=corpinfo.loyaltyPointTaxRate * 100)
        lp_tax_more_info_hint = GetByLabel('UI/Corporations/BaseCorporationUI/LPTaxRateDescription')
        scrolllist.append(GetFromClass(LabelTextSidesMoreInfo, {'line': 1,
         'label': lp_tax_label,
         'text': lp_tax_text,
         'moreInfoHint': lp_tax_more_info_hint}))
        if corpinfo.url:
            linkTag = '<url=%s>' % corpinfo.url
            scrolllist.append(self.GetListEntry('UI/Corporations/CorpUIHome/URL', GetByLabel('UI/Corporations/CorpUIHome/URLPlaceholder', linkTag=linkTag, url=corpinfo.url)))
        enabledDisabledText = GetByLabel('UI/Corporations/CorpUIHome/Enabled')
        if not corpinfo.isRecruiting:
            enabledDisabledText = GetByLabel('UI/Corporations/CorpUIHome/Disabled')
        scrolllist.append(self.GetListEntry('UI/Corporations/CorpUIHome/MembershipApplication', enabledDisabledText))
        allowedFactionIDs = sm.GetService('fwEnlistmentSvc').GetCorpAllowedEnlistmentFactions(session.corpid)
        factionNames = sorted([ cfg.eveowners.Get(factionId).name for factionId in allowedFactionIDs ])
        rightTextLabels = [ (x, None) for x in factionNames ] or [(GetByLabel('UI/Corporations/CorpUIHome/NoFwFactionsPermitted'), None)]
        label = GetByLabel('UI/Corporations/CorpUIHome/PermittedFwFactions')
        scrolllist.append(GetFromClass(LabelMultilineTextTop, {'label': label,
         'rightTextLabels': rightTextLabels}))
        label = GetByLabel('UI/WarPermit/WarPermitStatus')
        allowWar = corpinfo.allowWar
        statusText = GetByLabel(GetLabelPathForAllowWar(allowWar))
        moreInfoHint = GetByLabel('UI/WarPermit/WarPermitExplanation')
        scrolllist.append(GetFromClass(LabelTextSidesMoreInfo, {'line': 1,
         'label': label,
         'text': statusText,
         'moreInfoHint': moreInfoHint}))
        myListEntry = GetFromClass(FriendlyFireEntry, {'line': 1,
         'label': GetByLabel('UI/Corporations/CorpUIHome/FriendlyFire'),
         'moreInfoHint': GetByLabel('UI/Corporations/FriendlyFire/Description'),
         'buttonHint': GetByLabel('UI/Corporations/ToggleSetting'),
         'text': 'text'})
        scrolllist.append(myListEntry)
        if not IsNPC(session.corpid):
            labelPath = 'UI/Corporations/CorpUIHome/AcceptsTransferredStructures'
            doesAccept = sm.GetService('corp').GetCorpRegistry().DoesMyCorpAcceptStructures()
            if doesAccept:
                text = GetByLabel('UI/Corporations/CorpUIHome/AcceptsTransferredStructuresYes')
            else:
                text = GetByLabel('UI/Corporations/CorpUIHome/AcceptsTransferredStructuresNo')
            if SessionChecker(session, None).IsCorpDirector():
                myListEntry = GetFromClass(AcceptStructureEntry, {'line': 1,
                 'label': GetByLabel(labelPath),
                 'moreInfoHint': GetByLabel('UI/Corporations/CorpUIHome/AcceptTransferredStructureExplanation'),
                 'buttonHint': GetByLabel('UI/Corporations/ToggleSetting'),
                 'text': text,
                 'doesAccept': doesAccept})
            else:
                myListEntry = self.GetListEntry(labelPath, text)
            scrolllist.append(myListEntry)
            labelPath = 'UI/Corporations/CorpUIHome/CorpMailRestrictionsCorpMail'
            isRestricted = sm.GetService('corp').GetCorpRegistry().DoesCorpRestrictCorpMails()
            if isRestricted:
                text = GetByLabel('UI/Corporations/CorpUIHome/CorpMailRestrictionsCommOfficersOnly')
            else:
                text = GetByLabel('UI/Corporations/CorpUIHome/CorpMailRestrictionsUnrestricted')
            if SessionChecker(session, None).IsCorpDirector():
                myListEntry = GetFromClass(RestrictCorpMailsEntry, {'line': 1,
                 'label': GetByLabel(labelPath),
                 'moreInfoHint': GetByLabel('UI/Corporations/CorpUIHome/CorpMailRestrictionsHint'),
                 'text': text,
                 'isRestricted': isRestricted})
            else:
                myListEntry = self.GetListEntry(labelPath, text)
            scrolllist.append(myListEntry)
        return scrolllist

    def GetListEntry(self, label, text, typeID = None, itemID = None, station = None):
        entry = GetFromClass(LabelTextSides, {'line': 1,
         'label': GetByLabel(label),
         'text': text,
         'typeID': typeID,
         'itemID': itemID,
         'station': station})
        return entry

    def ShowMyCorporationsOffices(self, scrolllist):
        scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetSubContentMyCorporationsOffices,
         'label': GetByLabel('UI/Corporations/Common/Offices'),
         'groupItems': None,
         'id': ('corporation', 'offices'),
         'tabs': [],
         'state': 'locked',
         'showicon': 'hide'}))
        uicore.registry.SetListGroupOpenState(('corporation', 'offices'), 0)

    def GetSubContentMyCorporationsOffices(self, nodedata, *args):
        subcontent = []
        for office in sm.GetService('officeManager').GetMyCorporationsOffices():
            jumps = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(office.solarsystemID)
            locationName = cfg.evelocations.Get(office.stationID).locationName
            subcontent.append((locationName.lower(), GetFromClass(CorpOfficeEntry, {'label': GetByLabel('UI/Corporations/CorpUIHome/StationAndJumps', station=office.stationID, jumpCount=jumps, jumps=jumps),
              'office': office,
              'GetMenu': self.GetMenuForCorpOffice,
              'typeID': office.stationTypeID,
              'itemID': office.stationID,
              'sublevel': 1})))

        if not len(subcontent):
            subcontent.append(GetFromClass(Generic, {'label': GetByLabel('UI/Corporations/CorpUIHome/CorpHasNoOffices')}))
        else:
            subcontent = SortListOfTuples(subcontent)
        return subcontent

    def UpdateOfficeJumpCounts(self):
        if not self.details_scroll:
            return
        for node in self.details_scroll.GetNodes():
            if node.decoClass == CorpOfficeEntry:
                office = node.office
                jumps = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(office.solarsystemID)
                label = GetByLabel('UI/Corporations/CorpUIHome/StationAndJumps', station=office.stationID, jumpCount=jumps, jumps=jumps)
                node.label = label
                if node.panel:
                    node.panel.Load(node)

    def GetMenuForCorpOffice(self, entry):
        office = entry.sr.node.office
        ret = GetMenuService().CelestialMenu(office.stationID, typeID=office.stationTypeID)
        if SessionChecker(session, None).IsCorpDirector():
            ret.append([MenuLabel('UI/Station/Hangar/UnrentOffice'), self.UnrentOffice, [office.stationID]])
        return ret

    def UnrentOffice(self, stationID):
        officeName = cfg.evelocations.Get(stationID).name
        if eve.Message('crpUnrentOffice', {'officeName': officeName}, uiconst.YESNO) != uiconst.ID_YES:
            return
        sm.GetService('officeManager').UnrentRemoteOffice(stationID)

    def RemoveAllRoles(self, *args):
        corpSvc = sm.StartService('corp')
        canLeave, error, errorDetails = corpSvc.CanLeaveCurrentCorporation()
        if not canLeave:
            if error == 'CrpCantQuitNotInStasis':
                if eve.Message('ConfirmRemoveAllRolesDetailed', errorDetails, uiconst.OKCANCEL) != uiconst.ID_OK:
                    return
                corpSvc.RemoveAllRoles(silent=True)
            else:
                raise UserError(error, errorDetails)

    def ResignFromCorp(self, *args):
        corpSvc = sm.StartService('corp')
        canLeave, error, errorDetails = corpSvc.CanLeaveCurrentCorporation()
        if canLeave:
            corpSvc.KickOut(session.charid)
        else:
            raise UserError(error, errorDetails)

    def AllowRoles(self, *args):
        if eve.Message('ConfirmAllowRoles', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return
        sm.StartService('corp').UpdateMember(session.charid, None, None, None, None, None, None, None, None, None, None, None, None, None, 0)
        eve.Message('NotifyRolesAllowed', {})


class LabelSidesWithIconButton(LabelTextSidesMoreInfo):
    __guid__ = 'listentry.LabelSidesWithIconButton'
    _shouldDisplayButton = True

    def Startup(self, *args):
        LabelTextSidesMoreInfo.Startup(self, args)
        self._button = ButtonIcon(parent=self, state=uiconst.UI_NORMAL, align=uiconst.CENTERRIGHT, height=16, width=16, left=26, texturePath=eveicon.edit, func=self.OnButtonClick, display=False)

    def Load(self, node):
        LabelTextSidesMoreInfo.Load(self, node)
        self.UpdateButton()

    def UpdateButton(self):
        self._button.hint = self.sr.node.Get('buttonHint', '')
        self._button.SetTexturePath(self.sr.node.Get('buttonIcon', eveicon.edit))

    def OnButtonClick(self, *args):
        func = self.sr.node.Get('func', None)
        if func:
            func()

    def OnMouseEnter(self, *args):
        LabelTextSidesMoreInfo.OnMouseEnter(self, *args)
        if self._shouldDisplayButton:
            self._button.state = uiconst.UI_NORMAL
            self.sr.text.left = 46

    def OnMouseExit(self, *args):
        LabelTextSidesMoreInfo.OnMouseExit(self, *args)
        self._button.state = uiconst.UI_HIDDEN
        if self._shouldDisplayButton:
            self.sr.text.left = 26


class FriendlyFireEntry(LabelSidesWithIconButton):
    __guid__ = 'listentry.FriendlyFireEntry'

    def Startup(self, *args):
        LabelSidesWithIconButton.Startup(self, args)
        self.isFFEnabled = False

    def Load(self, node):
        LabelTextSidesMoreInfo.Load(self, node)
        self.SetCorpFFStatus()

    def SetCorpFFStatus(self, myCorpAggressionSettings = None):
        if myCorpAggressionSettings is None:
            myCorpAggressionSettings = sm.GetService('crimewatchSvc').GetCorpAggressionSettings()
        now = blue.os.GetWallclockTime()
        self.isFFEnabled = myCorpAggressionSettings.IsFriendlyFireLegalAtTime(now)
        canEditCorp = not IsNPC(session.corpid) and SessionChecker(session, None).IsCorpDirector()
        if not canEditCorp:
            self._shouldDisplayButton = False
        else:
            changeAtTime = myCorpAggressionSettings.GetNextPendingChangeTime(now)
            self._shouldDisplayButton = not changeAtTime
        self.sr.text.SetText(sm.GetService('corp').GetCorpFriendlyFireStatus(myCorpAggressionSettings))

    def OnButtonClick(self, *args):
        if self.isFFEnabled:
            confirmMsgText = 'ConfirmChangeFriendlyFireToIllegal'
        else:
            confirmMsgText = 'ConfirmChangeFriendlyFireToLegal'
        if eve.Message(confirmMsgText, {}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return
        newAggressionSettings = sm.GetService('corp').GetCorpRegistry().RegisterNewAggressionSettings(not self.isFFEnabled)
        self.SetCorpFFStatus(newAggressionSettings)


class AcceptStructureEntry(LabelSidesWithIconButton):
    __guid__ = 'AcceptStructureEntry'

    def Load(self, node):
        LabelSidesWithIconButton.Load(self, node)
        self.UpdateStatusText()

    def UpdateStatusText(self):
        node = self.sr.node
        if node.doesAccept:
            text = GetByLabel('UI/Corporations/CorpUIHome/AcceptsTransferredStructuresYes')
        else:
            text = GetByLabel('UI/Corporations/CorpUIHome/AcceptsTransferredStructuresNo')
        self.sr.text.SetText(text)

    def OnButtonClick(self, *args):
        doesAccept = self.sr.node.doesAccept
        newSettingAccept = not doesAccept
        if newSettingAccept:
            confirmMsgText = 'ConfirmChangeAcceptStructuresYes'
        else:
            confirmMsgText = 'ConfirmChangeAcceptStructuresNo'
        if eve.Message(confirmMsgText, {}, uiconst.YESNO) != uiconst.ID_YES:
            return
        corpRegistry = sm.GetService('corp').GetCorpRegistry()
        try:
            corpRegistry.RegisterNewAcceptStructureSettings(newSettingAccept)
            self.sr.node.doesAccept = newSettingAccept
        except StandardError:
            self.sr.node.doesAccept = corpRegistry.DoesMyCorpAcceptStructures()
            log.LogException()

        self.UpdateStatusText()


class RestrictCorpMailsEntry(LabelSidesWithIconButton):
    __guid__ = 'RestrictCorpMailsEntry'

    def Load(self, node):
        LabelSidesWithIconButton.Load(self, node)
        self.UpdateStatusText()

    def UpdateStatusText(self):
        node = self.sr.node
        if node.isRestricted:
            text = GetByLabel('UI/Corporations/CorpUIHome/CorpMailRestrictionsCommOfficersOnly')
        else:
            text = GetByLabel('UI/Corporations/CorpUIHome/CorpMailRestrictionsUnrestricted')
        self.sr.text.SetText(text)

    def UpdateButton(self):
        if self.sr.node.isRestricted:
            text = GetByLabel('UI/Corporations/CorpUIHome/CorpMailRestrictionsRemoveRestrictions')
        else:
            text = GetByLabel('UI/Corporations/CorpUIHome/CorpMailRestrictionsAddRestrictions')
        self._button.hint = text

    def OnButtonClick(self, *args):
        isRestricted = self.sr.node.isRestricted
        newSettingIsRestricted = not isRestricted
        corpRegistry = sm.GetService('corp').GetCorpRegistry()
        try:
            corpRegistry.RegisterNewCorpMailRestrictionSettings(newSettingIsRestricted)
            self.sr.node.isRestricted = newSettingIsRestricted
        except StandardError:
            self.sr.node.isRestricted = corpRegistry.DoesCorpRestrictCorpMails()
            log.LogException()

        self.UpdateButton()
        self.UpdateStatusText()


class CorpOfficeEntry(Generic):

    def Startup(self, *args):
        self.unrentButton = None
        Generic.Startup(self, *args)

    def Load(self, node):
        Generic.Load(self, node)
        self.unrentButton = ButtonIcon(texturePath='res:/UI/Texture/Icons/73_16_210.png', pos=(0, 0, 16, 16), align=uiconst.CENTERRIGHT, parent=self, hint=localization.GetByLabel('UI/Station/Hangar/UnrentOffice'), idx=0, func=self.UnrentOffice)
        self.unrentButton.display = False

    def UnrentOffice(self):
        officeName = cfg.evelocations.Get(self.itemID).name
        if eve.Message('crpUnrentOffice', {'officeName': officeName}, uiconst.YESNO) != uiconst.ID_YES:
            return
        sm.GetService('officeManager').UnrentRemoteOffice(self.itemID)

    def OnMouseEnter(self, *args):
        Generic.OnMouseEnter(self, *args)
        if not self.unrentButton:
            return
        if self.IsDirector():
            self.mouseovertimer = AutoTimer(1, self.UpdateMouseOver)
            self.unrentButton.display = True

    def UpdateMouseOver(self):
        mo = uicore.uilib.mouseOver
        if mo in (self, self.unrentButton):
            return
        self.mouseovertimer = None
        self.unrentButton.display = False

    def IsDirector(self):
        return session.corprole & const.corpRoleDirector == const.corpRoleDirector
