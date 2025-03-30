#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\contracts\contractsWnd.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.control.window import Window
from carbonui.control.tabGroup import GetTabData
from carbonui.window.header.tab_navigation import TabNavigationWindowHeader
from eve.client.script.ui.shared.neocom.contracts.contractPanels import StartPagePanel, MyContractsPanel
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
from eve.common.lib import appConst
from eve.client.script.ui.shared.neocom.contracts.contractsearch import ContractSearchPanel
from localization import GetByLabel

class ContractsWindow(Window):
    __guid__ = 'form.ContractsWindow'
    __notifyevents__ = ['OnDeleteContract', 'OnAddIgnore']
    default_width = 630
    default_height = 500
    default_windowID = 'contracts'
    default_captionLabelPath = 'Tooltips/Neocom/Contracts'
    default_descriptionLabelPath = 'Tooltips/Neocom/Contracts_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/contracts.png'

    def ApplyAttributes(self, attributes):
        super(ContractsWindow, self).ApplyAttributes(attributes)
        lookup = attributes.lookup
        idx = attributes.idx
        self.scope = uiconst.SCOPE_INGAME
        self.SetMinSize([700, 560])
        self.pages = {0: None}
        self.currPage = 0
        self.previousPageContractID = None
        self.currentPageContractID = None
        self.nextPageContractID = None
        self.parsingIssuers = False
        self.parsingType = False
        self.issuersByName = {}
        self.fetching = 0
        self.LoadTabs(lookup, idx)
        if lookup:
            setattr(self.myContractsParent, 'lookup', lookup)
            self.LookupOwner(lookup)
        else:
            self.SelectTab(idx)

    def MouseEnterHighlightOn(self, wnd, *args):
        wnd.SetRGB(1.0, 1.0, 0.0)

    def MouseExitHighlightOff(self, wnd, *args):
        wnd.SetRGB(1.0, 1.0, 1.0)

    def LookupOwner(self, ownerName):
        if self.IsMinimized():
            self.Maximize()
        setattr(self.myContractsParent, 'lookup', ownerName)
        settings.user.ui.Set('mycontracts_filter_status', appConst.conStatusFinished)
        self.tabGroup.SelectByIdx(1)
        self.myContractsParent.ShowOwner(ownerName)

    def ShowMyContractsPanel(self, status, forCorp = False):
        if self.IsMinimized():
            self.Maximize()
        self.tabGroup.SelectByIdx(1)
        if forCorp:
            self.myContractsParent.ShowRequireAttentionMyCorp(status)
        else:
            self.myContractsParent.ShowRequireAttention(status)

    def Prepare_Header_(self):
        self.header = TabNavigationWindowHeader()

    def LoadTabs(self, lookup = None, idx = None):
        self.startPageParent = StartPagePanel(name='startPageParent', parent=self.sr.main, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, idx=1)
        self.myContractsParent = MyContractsPanel(name='myContractsParent', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_HIDDEN, idx=1)
        self.contractSearchParent = Container(name='contractSearchParent', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_HIDDEN, idx=1)
        self.contractSearchContent = ContractSearchPanel(parent=self.contractSearchParent, parentContentPadding=self.content_padding)
        self.privateContractsParent = Container(name='privateContractsParent', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_HIDDEN, idx=1)
        self.tabGroup = self.header.tab_group
        startPageLabel = GetByLabel(self.default_captionLabelPath)
        tabList = (GetTabData(label=startPageLabel, panel=self.startPageParent, code=self, tabID='startPage'), GetTabData(label=GetByLabel('UI/Contracts/ContractsWindow/MyContracts'), panel=self.myContractsParent, code=self, tabID='myContracts'), GetTabData(label=GetByLabel('UI/Contracts/ContractsSearch/ContractSearch'), panel=self.contractSearchParent, code=self, tabID='contractSearch', uniqueName=pConst.UNIQUE_NAME_AVAILABLE_CONTRACTS_TAB))
        self.tabGroup.Startup(tabList, 'contractsTabs', autoselecttab=0)

    def SelectTab(self, idx):
        if idx:
            self.tabGroup.SelectByIdx(idx)
        else:
            h = getattr(sm.StartService('contracts'), 'hasContractWindowBeenOpened', False)
            if not h:
                self.tabGroup.SelectByIdx(0)
                setattr(sm.StartService('contracts'), 'hasContractWindowBeenOpened', True)
            else:
                self.tabGroup.AutoSelect()

    def Load(self, key):
        doInit = self.TabNotInitiatedCheck(key)
        if key == 'myContracts':
            if doInit:
                self.myContractsParent.Init()
        elif key == 'startPage':
            self.startPageParent.Init()
        elif key == 'contractSearch':
            self.contractSearchContent.Load(key)
            self.contractSearchContent.SetInitialFocus()

    def TabNotInitiatedCheck(self, key):
        doInit = not getattr(self, 'init_%s' % key, False)
        setattr(self, 'init_%s' % key, True)
        return doInit

    def Confirm(self, *etc):
        if self.tabGroup.GetSelectedArgs() == 'availableContracts':
            self.OnReturn_AvailableContracts()

    def GetError(self, checkNumber = 1):
        return ''

    def Error(self, error):
        if error:
            eve.Message('CustomInfo', {'info': error})

    def OnDeleteContract(self, contractID, *args):

        def DeleteContractInList(list, contractID):
            nodes = list.GetNodes()
            for n in nodes:
                if n.contractID == contractID:
                    list.RemoveEntries([n])
                    return

        list = self.sr.main.FindChild('mycontractlist')
        if list:
            DeleteContractInList(list, contractID)

    def OnAddIgnore(self, ignoreID, *args):
        if self.Get('contractlist'):
            list = self.contractlist
        else:
            cont = self.myContractsParent
            list = None
            for child in cont.children:
                if hasattr(child, 'name') and child.name == 'mycontractlist':
                    list = child
                    break
