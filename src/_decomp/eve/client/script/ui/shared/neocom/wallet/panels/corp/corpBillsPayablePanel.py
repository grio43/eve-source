#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\corp\corpBillsPayablePanel.py
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_WORLDMOD
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpBillsUtil import DoCfgPrimingForBills, GetTextForBill
from eve.common.lib import appConst
from eve.common.script.sys.idCheckers import IsCorporation, IsAlliance
from localization import GetByLabel
from utillib import KeyVal
import blue
headers = (GetByLabel('UI/Wallet/WalletWindow/ColHeaderBillType'),
 GetByLabel('UI/Wallet/WalletWindow/ColHeaderAmount'),
 GetByLabel('UI/Common/Date'),
 GetByLabel('UI/Wallet/WalletWindow/ColHeaderOwedBy'),
 GetByLabel('UI/Wallet/WalletWindow/ColHeaderCreditor'),
 GetByLabel('UI/Wallet/WalletWindow/ColHeaderInterest'),
 GetByLabel('UI/Wallet/WalletWindow/ColHeaderItemOrderID'))

class CorpBillsPayablePanel(Container):
    default_name = 'CorpBillsPayablePanel'
    __notifyevents__ = ['OnCorpWalletBillsChanged']

    def ApplyAttributes(self, attributes):
        super(CorpBillsPayablePanel, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.payBillsButtonGroup = ButtonGroup(btns=[(GetByLabel('UI/Wallet/WalletWindow/PayBill'),
          self.PayBillClick,
          (),
          84)], parent=self, state=uiconst.UI_HIDDEN)
        self.scroll = Scroll(parent=self, id='CorpBillsPayablePanel')

    def OnTabSelect(self):
        self.PopulateScroll()

    def PopulateScroll(self):
        ambSettings = sm.RemoteSvc('billMgr').GetAutomaticPaySettings()
        bills = self.GetBills()
        scrolllist = []
        for bill in bills:
            if bill.debtorID in ambSettings and ambSettings[bill.debtorID].get(bill.billTypeID, False) == True:
                continue
            entry = self.GetScrollEntry(bill)
            scrolllist.append(entry)

        self.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=GetByLabel('UI/Wallet/WalletWindow/HintNoTransactionsFound'))

    def GetScrollEntry(self, bill):
        data = KeyVal()
        label = GetTextForBill(bill, data)
        data.bill = bill
        data.groupID = bill.billID
        data.label = label
        data.billPaid = None
        data.GetMenu = self.OnPayBillMenu
        return GetFromClass(Generic, data)

    def GetBills(self):
        bills = []
        self.CheckShowBillsButtons()
        if session.allianceid is not None:
            res = self.GetBillsPayable(session.allianceid)
            if res:
                bills.extend(res)
        res = self.GetBillsPayable(session.corpid)
        if res:
            bills.extend(res)
        DoCfgPrimingForBills(bills)
        return bills

    def CheckShowBillsButtons(self):
        if appConst.corpRoleAccountant & session.corprole == appConst.corpRoleAccountant:
            self.payBillsButtonGroup.state = uiconst.UI_PICKCHILDREN

    def GetBillsPayable(self, ownerID):
        if IsCorporation(ownerID):
            return sm.RemoteSvc('billMgr').GetCorporationBills()
        if IsAlliance(ownerID):
            return sm.GetService('alliance').GetBills()

    def PayBillClick(self):
        sel = self.scroll.GetSelected()
        bills = [ (each.groupID, each.bill) for each in sel ]
        for each in bills:
            sm.GetService('wallet').PayBill(each[1])

    def OnPayBillMenu(self, entry):
        m = []
        if session.role & (ROLE_GML | ROLE_WORLDMOD):
            billID = entry.sr.node.bill.billID
            m += [('GM: billID: ' + str(billID), blue.pyos.SetClipboardData, (str(billID),))]
        if appConst.corpRoleAccountant & session.corprole == appConst.corpRoleAccountant:
            entry.DoSelectNode()
            sel = self.scroll.GetSelected()
            if len(sel) > 1:
                text = GetByLabel('UI/Wallet/WalletWindow/MenuPayBills', numBills=len(sel))
            else:
                text = GetByLabel('UI/Wallet/WalletWindow/MenuPayBill')
            m += [(text, self.PayBillClick)]
        return m

    def OnCorpWalletBillsChanged(self):
        self.PopulateScroll()
