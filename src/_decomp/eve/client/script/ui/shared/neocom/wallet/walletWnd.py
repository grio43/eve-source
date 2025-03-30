#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\walletWnd.py
import logging
import uthread
from carbonui import uiconst
from carbonui.control.window import Window
from carbonui.window.header.tab_navigation import TabNavigationWindowHeader
from eve.client.script.ui.shared.neocom.wallet import walletConst
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpWalletPanel import CorpWalletPanel
from eve.client.script.ui.shared.neocom.wallet.panels.personal.personalWalletPanel import PersonalWalletPanel
from eve.client.script.ui.shared.neocom.wallet.panels.settings import SettingsWalletPanel
from eve.client.script.ui.shared.neocom.wallet.walletUtil import HaveAccessToCorpWallet, HaveAccessToCorpEMWallet, HaveAccessToCorpLPWallet
from eve.common.lib import appConst
from localization import GetByLabel
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
logger = logging.getLogger(__name__)

class WalletWindow(Window):
    default_width = 750
    default_height = 600
    default_minSize = (650, 410)
    default_windowID = 'walletWindow'
    default_captionLabelPath = 'UI/Wallet/WalletWindow/Wallet'
    default_iconNum = 'res:/ui/Texture/WindowIcons/wallet.png'
    __notifyevents__ = ['DoSessionChanging']

    def ApplyAttributes(self, attributes):
        super(WalletWindow, self).ApplyAttributes(attributes)
        self.tabID = attributes.get('tabID', None)
        self.sub_tab_id = attributes.get('subTabID', None)
        self.personalWallet = None
        self.corpWallet = None
        self.settingsPanel = None
        self.tabGroup = self.header.tab_group
        self.ConstructLayout()
        sm.GetService('neocom').BlinkOff('wallet')
        sm.RegisterNotify(self)

    def ReconstructTabs(self):
        self.tabGroup.Flush()
        self.tabGroup.AddTab(label=GetByLabel('UI/Wallet/WalletWindow/MyWallet'), panel=self.personalWallet, code=self.personalWallet, tabID=walletConst.PANEL_PERSONAL, uniqueName=pConst.UNIQUE_NAME_MY_WALLET_TAB)
        if HaveAccessToCorpWallet() or HaveAccessToCorpEMWallet() or HaveAccessToCorpLPWallet():
            self.tabGroup.AddTab(label=GetByLabel('UI/Wallet/WalletWindow/CorporationWallet'), panel=self.corpWallet, code=self.corpWallet, tabID=walletConst.PANEL_CORP)
        self.tabGroup.AddTab(label=GetByLabel('UI/Common/Settings'), panel=self.settingsPanel, code=self.settingsPanel, tabID=walletConst.PANEL_SETTINGS)
        if self.tabID:
            self.tabGroup.SelectByID(self.tabID)
            if self.sub_tab_id:
                self.tabGroup.GetSelectedPanel().SelectTab(self.sub_tab_id)
        else:
            self.tabGroup.AutoSelect()

    def Prepare_Header_(self):
        self.header = TabNavigationWindowHeader()

    def Close(self, setClosed = False, *args, **kwds):
        try:
            self.SaveLastOpenedTabID()
        except Exception as e:
            logger.exception(e)

        super(WalletWindow, self).Close(setClosed, *args, **kwds)

    def SaveLastOpenedTabID(self):
        if not self.tabGroup:
            return
        settings.char.ui.Set('walletWindowTab', self.tabGroup.GetSelectedID())

    def GetLastOpenedTabID(self):
        return settings.char.ui.Get('walletWindowTab', None)

    def ConstructLayout(self):
        if HaveAccessToCorpWallet() or HaveAccessToCorpEMWallet() or HaveAccessToCorpLPWallet():
            self.ConstructPersonalAndCorpWallets()
        else:
            self.ConstructPersonalWallet()

    def ConstructPersonalWallet(self):
        self.personalWallet = PersonalWalletPanel(parent=self.GetMainArea(), state=uiconst.UI_NORMAL)
        self.settingsPanel = SettingsWalletPanel(parent=self.GetMainArea(), padTop=16)
        self.ReconstructTabs()

    def ConstructPersonalAndCorpWallets(self):
        self.personalWallet = PersonalWalletPanel(parent=self.GetMainArea())
        self.corpWallet = CorpWalletPanel(parent=self.GetMainArea())
        self.settingsPanel = SettingsWalletPanel(parent=self.GetMainArea())
        self.ReconstructTabs()

    def ReconstructLayout(self):
        self.GetMainArea().Flush()
        self.ConstructLayout()

    def SelectTab(self, tab_id, sub_tab_id = None):
        self.tabGroup.SelectByID(tab_id)
        if sub_tab_id:
            panel = self.tabGroup.GetSelectedPanel()
            panel.SelectTab(sub_tab_id)

    @classmethod
    def OpenCorpWallet(cls):
        cls._OpenWalletOnTab(walletConst.PANEL_CORP)

    @classmethod
    def OpenMyWallet(cls):
        cls._OpenWalletOnTab(walletConst.PANEL_PERSONAL)

    @classmethod
    def OpenMyPLEXWallet(cls):
        cls._OpenWalletOnTab(walletConst.PANEL_PERSONAL, walletConst.PANEL_PLEX)

    @classmethod
    def _OpenWalletOnTab(cls, tab_id, sub_tab_id = None):
        wnd = cls.GetIfOpen()
        if wnd:
            wnd.SelectTab(tab_id, sub_tab_id)
        else:
            cls.Open(tabID=tab_id, subTabID=sub_tab_id)

    @classmethod
    def OpenWalletOnPayableCorpBills(cls):
        cls.CloseIfOpen()
        settings.user.tabgroups.Set(walletConst.PANEL_CORPISK, 0)
        settings.user.tabgroups.Delete('%s_names' % walletConst.PANEL_CORPISK)
        settings.user.tabgroups.Set('corpbills', 0)
        settings.user.tabgroups.Delete('corpbills_names')
        cls.OpenCorpWallet()

    def DoSessionChanging(self, isremote, session, change):
        if 'charid' in change and change['charid'][1] is None:
            return
        corpAccountKeyChanged = 'corpAccountKey' in change
        corpChanged = 'corpid' in change
        allianceChanged = 'allianceid' in change
        if 'corprole' in change:
            old, new = change['corprole']
            rolesToCheck = appConst.corpRoleAccountant | appConst.corpRoleJuniorAccountant | appConst.corpRoleBrandManager
            for i in walletConst.corpWalletRoles:
                rolesToCheck = rolesToCheck | i

            old = old & rolesToCheck
            new = new & rolesToCheck
            rolesChanged = old != new
        else:
            rolesChanged = False
        if corpChanged or rolesChanged or allianceChanged or corpAccountKeyChanged:
            uthread.new(self.ReconstructLayout)

    def BlinkPanelByIDs(self, panelIDs):
        if self.tabGroup:
            for panelID in panelIDs:
                self.tabGroup.BlinkPanelByID(panelID)

        if self.personalWallet:
            self.personalWallet.BlinkPanelByIDs(panelIDs)
        if self.corpWallet:
            self.personalWallet.BlinkPanelByIDs(panelIDs)

    @classmethod
    def BlinkPersonalWallet(cls, panelID = None):
        wnd = cls.GetIfOpen()
        if wnd:
            wnd.BlinkPanelByIDs([walletConst.PANEL_PERSONALISK, panelID])

    @classmethod
    def BlinkCorpWallet(cls, panelID = None):
        wnd = cls.GetIfOpen()
        if wnd:
            wnd.BlinkPanelByIDs([walletConst.PANEL_CORPISK, panelID])
