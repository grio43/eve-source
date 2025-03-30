#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\corp\corpBillsAutoPaySettingsPanel.py
import logging
from billtypes.data import get_bill_type_name, get_bill_type_name_id
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.util.various_unsorted import SortListOfTuples
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.checkbox import CheckboxEntry
from eve.client.script.ui.control.entries.combo import ComboEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.neocom.wallet.walletUtil import GetAccessibleCorpWalletDivisionIDs
from localization import GetByLabel
from localization import GetByMessageID
logger = logging.getLogger(__name__)

class CorpBillsAutoPaySettings(Container):
    default_name = 'CorpBillsAutoPaySettings'

    def ApplyAttributes(self, attributes):
        super(CorpBillsAutoPaySettings, self).ApplyAttributes(attributes)
        self.isInitialized = False
        self.automaticPaymentSettings = None
        self.scroll = Scroll(parent=self, align=uiconst.TOALL)
        self.scroll.HideBackground()
        ButtonGroup(btns=[(GetByLabel('UI/Commands/Apply'),
          self.SubmitAutomaticPaymentSettings,
          (),
          84)], parent=self, align=uiconst.TOBOTTOM, idx=0)

    def OnTabSelect(self):
        if not self.isInitialized:
            self.automaticPaymentSettings = sm.RemoteSvc('billMgr').GetAutomaticPaySettings()
            self.isInitialized = True
        self.PopulateScroll()

    def PopulateScroll(self):
        bill_checked_settings = self.GetBillCheckedSettings()
        scrolllist = []
        for billTypeID, checked, ownerID in bill_checked_settings:
            entry = self.GetBillCheckedScrollEntry(billTypeID, checked, ownerID)
            scrolllist.append(entry)

        entry = self.GetWalletDivisionComboEntry(entry)
        scrolllist.append(entry)
        self.scroll.Load(contentList=scrolllist, noContentHint=GetByLabel('UI/Wallet/WalletWindow/HintNoTransactionsFound'))

    def GetWalletDivisionComboEntry(self, entry):
        choices = SortListOfTuples([ (acctID, (sm.GetService('corp').GetCorpAccountName(acctID), acctID)) for acctID in GetAccessibleCorpWalletDivisionIDs() ])
        entry = GetFromClass(ComboEntry, {'options': choices,
         'label': GetByLabel('UI/Wallet/WalletWindow/ColHeaderDivision'),
         'cfgName': 'divisionID',
         'setValue': self.automaticPaymentSettings.get(session.corpid, {}).get('divisionID', 1000),
         'OnChange': self.OnAutomaticPaymentDivisionChanged,
         'name': 'divisionID'})
        return entry

    def GetBillCheckedSettings(self):
        bill_checked_settings = []
        for ownerID in self.automaticPaymentSettings:
            for billTypeID, checked in self.automaticPaymentSettings[ownerID].iteritems():
                if billTypeID == 'divisionID':
                    continue
                bill_checked_settings.append((billTypeID, checked, ownerID))

        bill_checked_settings = sorted(bill_checked_settings)
        return bill_checked_settings

    def GetBillCheckedScrollEntry(self, billTypeID, checked, ownerID):
        return GetFromClass(CheckboxEntry, {'label': GetByMessageID(get_bill_type_name_id(billTypeID)),
         'checked': checked,
         'OnChange': self.OnAutomaticPaymentChanged,
         'cfgname': get_bill_type_name(billTypeID),
         'retval': (billTypeID, ownerID)})

    def SubmitAutomaticPaymentSettings(self, *args):
        sm.RemoteSvc('billMgr').SendAutomaticPaySettings(self.automaticPaymentSettings)

    def OnAutomaticPaymentChanged(self, checkbox, node, *args):
        billTypeID, ownerID = node.retval
        if ownerID not in self.automaticPaymentSettings:
            logger.error('Changing automatic payment settings for an unknown owner', ownerID, billTypeID)
            return
        self.automaticPaymentSettings[ownerID][billTypeID] = bool(checkbox.checked)

    def OnAutomaticPaymentDivisionChanged(self, combo, header, value, *args):
        if session.corpid not in self.automaticPaymentSettings:
            self.automaticPaymentSettings[session.corpid] = {}
        self.automaticPaymentSettings[session.corpid]['divisionID'] = value
