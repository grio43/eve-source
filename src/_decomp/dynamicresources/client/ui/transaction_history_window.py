#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ui\transaction_history_window.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from dynamicresources.client.ui.transaction_history_window_controller import TransactionHistoryWindowController
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from carbonui.control.tabGroup import TabGroup
from localization import GetByLabel

class TransactionHistoryWindow(Window):
    MAIN_BANK = 1
    RESERVE_BANK = 2
    default_width = 500
    default_height = 300
    default_windowID = 'dynamicresources.ess.TransactionHistoryWindow'
    default_caption = GetByLabel('UI/ESS/TransactionHistoryWindowCaption')
    default_tab = RESERVE_BANK
    __notifyevents__ = ['OnESSDataUpdate_Local']

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        tab = attributes.get('tab', self.default_tab)
        self.controller = TransactionHistoryWindowController()
        self.ConstructLayout(tab=tab)

    def ConstructLayout(self, tab = None):
        self.tabGroup = TabGroup(parent=self.sr.main, align=uiconst.TOTOP)
        mainBankHistoryPanel = Container(name='mainBankHistoryPanel', parent=self.sr.main)
        reserveBankHistoryPanel = Container(name='reserveBankHistoryPanel', parent=self.sr.main)
        self.ConstructMainBankPanel(mainBankHistoryPanel)
        self.ConstructReserveBankPanel(reserveBankHistoryPanel)
        self.tabGroup.AddTab(GetByLabel('UI/ESS/TransactionHistoryMainBankTab'), mainBankHistoryPanel, self.sr.main, tabID=self.MAIN_BANK)
        self.tabGroup.AddTab(GetByLabel('UI/ESS/TransactionHistoryReserveBankTab'), reserveBankHistoryPanel, self.sr.main, tabID=self.RESERVE_BANK)
        if tab:
            self.ShowTab(tab)
        else:
            self.tabGroup.AutoSelect()

    def OnESSDataUpdate_Local(self):
        currentTab = self.tabGroup.GetSelectedID()
        self.sr.main.Flush()
        self.ConstructLayout(tab=currentTab)

    def ConstructMainBankPanel(self, mainBankPanel):
        entries = self.controller.GetMainBankAccessHistoryListItems()
        scroll = TransactionHistoryScroll(parent=mainBankPanel, align=uiconst.TOALL, padding=1)
        nameHeading = GetByLabel('UI/ESS/TransactionHistoryNameTableHeading')
        amountHeading = GetByLabel('UI/ESS/TransactionHistoryAmountTableHeading')
        scroll.Load(contentList=entries, headers=('', nameHeading, amountHeading), noContentHint=GetByLabel('UI/ESS/TransactionHistoryNoData'))

    def ConstructReserveBankPanel(self, reserveBankPanel):
        entries = self.controller.GetReserveBankAccessHistoryListItems()
        scroll = TransactionHistoryScroll(parent=reserveBankPanel, align=uiconst.TOALL, padding=1)
        nameHeading = GetByLabel('UI/ESS/TransactionHistoryNameTableHeading')
        dateHeading = GetByLabel('UI/ESS/TransactionHistoryDateTableHeading')
        amountHeading = GetByLabel('UI/ESS/TransactionHistoryAmountTableHeading')
        scroll.Load(contentList=entries, headers=('',
         nameHeading,
         dateHeading,
         amountHeading), noContentHint=GetByLabel('UI/ESS/TransactionHistoryNoData'))

    def ShowTab(self, tab):
        self.tabGroup.ShowPanelByID(tab)

    @classmethod
    def OpenToTab(cls, tab):
        if TransactionHistoryWindow.IsOpen():
            w = TransactionHistoryWindow.GetIfOpen()
            w.Maximize()
            w.ShowTab(tab)
        else:
            TransactionHistoryWindow.Open(tab=tab)

    @classmethod
    def OpenToMainBank(cls):
        cls.OpenToTab(cls.MAIN_BANK)

    @classmethod
    def OpenToReserveBank(cls):
        cls.OpenToTab(cls.RESERVE_BANK)


class TransactionHistoryScroll(Scroll):
    default_id = 'MainBankTransactionHistoryScroll'
    default_columnWidth = {'': 32}
